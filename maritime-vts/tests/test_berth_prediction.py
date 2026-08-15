from datetime import datetime, timedelta

from app.services.berth_prediction import next_available_slot, predict_berth_availability

NOW = datetime(2026, 8, 14, 12, 0, 0)


def test_empty_berth_with_no_schedule_is_available_now():
    slots = predict_berth_availability("T2-B2", NOW, current_occupant_departure=None, scheduled_events=[])
    assert slots[0].available_from == NOW
    assert slots[0].available_until is None
    assert slots[0].confidence == "low"


def test_occupied_berth_available_after_departure():
    departure = NOW + timedelta(hours=10)
    slots = predict_berth_availability("T1-B2", NOW, current_occupant_departure=departure, scheduled_events=[])
    assert slots[0].available_from == departure
    assert slots[0].confidence == "high"


def test_scheduled_arrival_creates_bounded_window():
    departure = NOW + timedelta(hours=5)
    next_arrival = NOW + timedelta(hours=20)
    events = [{"mmsi": "X", "eta": next_arrival, "etd": next_arrival + timedelta(hours=15)}]
    slots = predict_berth_availability("T1-B1", NOW, current_occupant_departure=departure, scheduled_events=events)

    bounded = [s for s in slots if s.available_until is not None]
    assert len(bounded) == 1
    assert bounded[0].available_from == departure
    assert bounded[0].available_until == next_arrival


def test_next_available_slot_respects_minimum_duration():
    departure = NOW + timedelta(hours=2)
    short_gap_arrival = NOW + timedelta(hours=4)
    long_gap_departure_of_that_ship = short_gap_arrival + timedelta(hours=3)
    later_free = long_gap_departure_of_that_ship

    events = [{"mmsi": "X", "eta": short_gap_arrival, "etd": long_gap_departure_of_that_ship}]
    slots = predict_berth_availability("T1-B1", NOW, current_occupant_departure=departure, scheduled_events=events)

    result = next_available_slot(slots, min_duration_hours=10)
    # The 2-hour gap before the next ship isn't long enough; should skip to the open-ended slot after.
    assert result is not None
    assert result.available_until is None
