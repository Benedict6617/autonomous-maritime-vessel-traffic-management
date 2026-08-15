from fastapi import APIRouter, HTTPException

from app.db.database import store
from app.models.pilot import Pilot
from app.services.pilot_assignment import assign_pilot

router = APIRouter(prefix="/pilots", tags=["pilots"])


@router.get("")
def list_pilots():
    return list(store.pilots.values())


@router.get("/assign/{mmsi}")
def recommend_pilot(mmsi: str):
    vessel = store.vessels.get(mmsi)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    pilots = [Pilot(**p) for p in store.pilots.values()]
    result = assign_pilot(vessel["loa_m"], pilots)
    return result.__dict__
