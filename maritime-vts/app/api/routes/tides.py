from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from app.services.tidal_calculations import find_safe_tidal_windows, tide_height_m

router = APIRouter(prefix="/tides", tags=["tides"])

# Harmonic epoch reference; in production this comes from the station's
# published harmonic constituent table (see tidal_calculations.py docstring).
EPOCH = datetime(2026, 1, 1, 0, 0, 0)


@router.get("/height")
def current_height(at: datetime | None = None):
    at = at or datetime.utcnow()
    return {"timestamp": at.isoformat(), "tide_height_m": tide_height_m(at, EPOCH)}


@router.get("/window")
def tidal_window(
    charted_depth_m: float = Query(..., description="Charted depth of the channel/berth"),
    vessel_draft_m: float = Query(..., description="Vessel's current draft"),
    min_required_ukc_m: float = Query(1.0, description="Minimum required under-keel clearance"),
    search_hours: int = Query(72, le=168),
):
    now = datetime.utcnow()
    windows = find_safe_tidal_windows(
        epoch=EPOCH,
        search_start=now,
        search_hours=search_hours,
        charted_depth_m=charted_depth_m,
        vessel_draft_m=vessel_draft_m,
        min_required_ukc_m=min_required_ukc_m,
    )
    return [
        {
            "start": w.start.isoformat(),
            "end": w.end.isoformat(),
            "min_clearance_m": w.min_clearance_m,
        }
        for w in windows
    ]
