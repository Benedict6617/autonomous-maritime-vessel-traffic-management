from fastapi import APIRouter, HTTPException

from app.db.database import store
from app.models.tugboat import Tugboat
from app.services.tugboat_coordination import assign_tugs

router = APIRouter(prefix="/tugboats", tags=["tugboats"])


@router.get("")
def list_tugboats():
    return list(store.tugboats.values())


@router.get("/assign/{mmsi}")
def recommend_tugs(mmsi: str):
    vessel = store.vessels.get(mmsi)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")

    tugs = [Tugboat(**t) for t in store.tugboats.values()]
    result = assign_tugs(vessel["loa_m"], tugs)
    return result.__dict__
