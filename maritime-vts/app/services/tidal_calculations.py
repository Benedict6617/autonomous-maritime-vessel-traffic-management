"""Tidal height prediction and under-keel clearance / tidal window calculation.

Uses a simplified harmonic tide model: tide height is modeled as the sum of
a handful of dominant harmonic constituents (M2 principal lunar semi-diurnal,
S2 principal solar semi-diurnal, K1 and O1 diurnal). Real port authorities
publish station-specific constituent amplitude/phase tables (e.g. from
NOAA CO-OPS); this module accepts those as configuration so it can be
calibrated to any station without code changes.
"""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta

# Default constituents approximate a moderate mixed semi-diurnal tide.
# amplitude_m, period_hours, phase_deg — replace with station-calibrated
# values from a NOAA/national hydrographic office harmonic table for real use.
DEFAULT_CONSTITUENTS = [
    {"name": "M2", "amplitude_m": 1.10, "period_hours": 12.4206, "phase_deg": 45},
    {"name": "S2", "amplitude_m": 0.35, "period_hours": 12.0000, "phase_deg": 60},
    {"name": "K1", "amplitude_m": 0.22, "period_hours": 23.9345, "phase_deg": 120},
    {"name": "O1", "amplitude_m": 0.15, "period_hours": 25.8193, "phase_deg": 100},
]

MEAN_SEA_LEVEL_M = 2.4  # station datum offset, meters above chart datum


@dataclass
class TidalWindow:
    start: datetime
    end: datetime
    min_clearance_m: float


def tide_height_m(at: datetime, epoch: datetime, constituents: list[dict] | None = None) -> float:
    """Predicted tide height (meters above chart datum) at a given time."""
    constituents = constituents or DEFAULT_CONSTITUENTS
    hours_elapsed = (at - epoch).total_seconds() / 3600.0

    height = MEAN_SEA_LEVEL_M
    for c in constituents:
        omega = 2 * math.pi / c["period_hours"]
        phase = math.radians(c["phase_deg"])
        height += c["amplitude_m"] * math.cos(omega * hours_elapsed - phase)
    return round(height, 3)


def under_keel_clearance_m(
    at: datetime,
    epoch: datetime,
    charted_depth_m: float,
    vessel_draft_m: float,
    squat_allowance_m: float = 0.3,
) -> float:
    """UKC = (charted depth + tide height) - (draft + squat allowance).

    squat_allowance_m accounts for vessel squat effect at speed in shallow
    water; default is a conservative placeholder — real UKC policy should
    use a squat formula calibrated to the channel and vessel class.
    """
    tide = tide_height_m(at, epoch)
    return round((charted_depth_m + tide) - (vessel_draft_m + squat_allowance_m), 3)


def find_safe_tidal_windows(
    epoch: datetime,
    search_start: datetime,
    search_hours: int,
    charted_depth_m: float,
    vessel_draft_m: float,
    min_required_ukc_m: float,
    step_minutes: int = 15,
) -> list[TidalWindow]:
    """Scan forward from search_start to find contiguous windows where UKC
    meets or exceeds the minimum required clearance — i.e. safe transit
    windows for a vessel of the given draft.
    """
    windows: list[TidalWindow] = []
    current_start: datetime | None = None
    min_seen = float("inf")

    steps = int((search_hours * 60) / step_minutes) + 1
    for i in range(steps):
        t = search_start + timedelta(minutes=i * step_minutes)
        ukc = under_keel_clearance_m(t, epoch, charted_depth_m, vessel_draft_m)
        safe = ukc >= min_required_ukc_m

        if safe and current_start is None:
            current_start = t
            min_seen = ukc
        elif safe:
            min_seen = min(min_seen, ukc)
        elif not safe and current_start is not None:
            windows.append(TidalWindow(start=current_start, end=t, min_clearance_m=round(min_seen, 3)))
            current_start = None
            min_seen = float("inf")

    if current_start is not None:
        windows.append(
            TidalWindow(
                start=current_start,
                end=search_start + timedelta(hours=search_hours),
                min_clearance_m=round(min_seen, 3),
            )
        )

    return windows
