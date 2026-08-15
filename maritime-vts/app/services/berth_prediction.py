"""72-hour berth availability forecasting.

Approach: for each berth, project forward from its current occupancy
(known departure time, if any) and layer in the scheduled arrivals/
departures for that berth from the port schedule. This is a deterministic
timeline projection rather than a statistical/ML forecast — appropriate as
a first release for a small port where schedule adherence data to train a
predictive model usually doesn't exist yet. The `docs/ARCHITECTURE.md`
roadmap covers replacing this with a probabilistic ETA-based model once
historical AIS/schedule data has been collected.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

FORECAST_HOURS = 72


@dataclass
class BerthAvailabilitySlot:
    berth_id: str
    available_from: datetime
    available_until: datetime | None  # None = open-ended until next known event
    confidence: str  # "high" (occupant known), "medium" (schedule-based), "low" (default)


def predict_berth_availability(
    berth_id: str,
    now: datetime,
    current_occupant_departure: datetime | None,
    scheduled_events: list[dict],
) -> list[BerthAvailabilitySlot]:
    """Build a 72-hour timeline of free windows for a single berth.

    scheduled_events: list of {"mmsi", "eta", "etd", "berth_id"} sorted by eta,
    already filtered to this berth_id, representing the confirmed port schedule.
    """
    horizon = now + timedelta(hours=FORECAST_HOURS)
    events = sorted(
        [e for e in scheduled_events if e["eta"] < horizon],
        key=lambda e: e["eta"],
    )

    slots: list[BerthAvailabilitySlot] = []
    cursor = current_occupant_departure if current_occupant_departure else now
    confidence = "high" if current_occupant_departure else "medium"

    for event in events:
        if event["eta"] <= cursor:
            # Overlaps current occupancy / a preceding event — occupant queue backs up.
            cursor = max(cursor, event.get("etd", event["eta"] + timedelta(hours=18)))
            continue

        slots.append(
            BerthAvailabilitySlot(
                berth_id=berth_id,
                available_from=cursor,
                available_until=event["eta"],
                confidence=confidence,
            )
        )
        cursor = event.get("etd", event["eta"] + timedelta(hours=18))
        confidence = "medium"

    if cursor < horizon:
        slots.append(
            BerthAvailabilitySlot(
                berth_id=berth_id,
                available_from=cursor,
                available_until=None,
                confidence="low",
            )
        )

    return slots


def next_available_slot(slots: list[BerthAvailabilitySlot], min_duration_hours: float = 0) -> BerthAvailabilitySlot | None:
    """Return the earliest slot long enough to accommodate a call of the
    given minimum duration.
    """
    for slot in slots:
        if slot.available_until is None:
            return slot
        duration = (slot.available_until - slot.available_from).total_seconds() / 3600.0
        if duration >= min_duration_hours:
            return slot
    return None
