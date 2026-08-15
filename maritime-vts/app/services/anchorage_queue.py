"""Anchorage queue management — priority-scored waiting list for vessels
without an assigned berth.
"""
from dataclasses import dataclass, field
from datetime import datetime

# Weighting reflects common harbor-master priority policy: safety/emergency
# first, then perishable/time-sensitive cargo, then vessel size (larger
# vessels have fewer alternate anchorage options), then simple FIFO by
# request time.
CARGO_PRIORITY_WEIGHT = {
    "hazardous": 40,
    "perishable": 30,
    "passenger": 25,
    "container": 10,
    "bulk": 5,
    "general": 0,
}


@dataclass(order=True)
class QueuedVessel:
    sort_index: float = field(init=False, repr=False)
    mmsi: str
    requested_at: datetime
    loa_m: float
    cargo_category: str
    is_emergency: bool = False

    def __post_init__(self):
        self.sort_index = -self._priority_score()

    def _priority_score(self) -> float:
        score = 0.0
        if self.is_emergency:
            score += 1000
        score += CARGO_PRIORITY_WEIGHT.get(self.cargo_category, 0)
        score += min(self.loa_m / 10.0, 20)  # larger vessels weighted slightly higher
        # Age in queue: +1 point per hour waiting, to prevent starvation.
        wait_hours = (datetime.utcnow() - self.requested_at).total_seconds() / 3600.0
        score += wait_hours
        return score


class AnchorageQueue:
    def __init__(self):
        self._vessels: list[QueuedVessel] = []

    def add(self, vessel: QueuedVessel) -> None:
        self._vessels.append(vessel)

    def remove(self, mmsi: str) -> None:
        self._vessels = [v for v in self._vessels if v.mmsi != mmsi]

    def ordered(self) -> list[QueuedVessel]:
        """Vessels ordered by descending priority score (next-to-berth first)."""
        return sorted(self._vessels, key=lambda v: v.sort_index)

    def position_of(self, mmsi: str) -> int | None:
        for idx, v in enumerate(self.ordered()):
            if v.mmsi == mmsi:
                return idx + 1
        return None
