from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.database import store
from app.services.emergency_diversion import build_diversion_plan

router = APIRouter(prefix="/emergencies", tags=["emergencies"])

# Fictional candidate anchorages/alternate ports for the sample port.
CANDIDATE_ANCHORAGES = [
    {"name": "Outer Anchorage Alpha", "lat": 40.980, "lon": -71.360, "charted_depth_m": 20.0},
    {"name": "Sheltered Cove Anchorage", "lat": 41.070, "lon": -71.410, "charted_depth_m": 14.0},
    {"name": "Neighboring Port of Millbrook", "lat": 40.850, "lon": -71.500, "charted_depth_m": 18.5},
    {"name": "Shoal Anchorage Bravo", "lat": 41.005, "lon": -71.290, "charted_depth_m": 9.0},
]


class DivertRequest(BaseModel):
    mmsi: str
    severity: str  # low, medium, high, critical
    lat: float
    lon: float


@router.post("/divert")
def divert(request: DivertRequest):
    vessel = store.vessels.get(request.mmsi)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    plan = build_diversion_plan(
        mmsi=request.mmsi,
        severity=request.severity,
        vessel_lat=request.lat,
        vessel_lon=request.lon,
        vessel_draft_m=vessel["draft_m"],
        candidate_anchorages=CANDIDATE_ANCHORAGES,
    )
    return {
        "mmsi": plan.mmsi,
        "severity": plan.severity,
        "notify": plan.notify,
        "options": [o.__dict__ for o in plan.options],
    }
