from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.db.database import store
from app.services import berth_prediction

router = APIRouter(prefix="/berths", tags=["berths"])


@router.get("")
def list_berths():
    return list(store.berths.values())


@router.get("/{berth_id}")
def get_berth(berth_id: str):
    berth = store.berths.get(berth_id)
    if not berth:
        raise HTTPException(status_code=404, detail="Berth not found")
    return berth


@router.get("/forecast")
def berth_forecast():
    """72-hour berth availability forecast across all berths."""
    now = datetime.utcnow()
    forecast = {}
    for berth_id, berth in store.berths.items():
        occupant_departure = (
            datetime.fromisoformat(berth["occupied_until"]) if berth.get("occupied_until") else None
        )
        events = [
            {
                "mmsi": e["mmsi"],
                "eta": datetime.fromisoformat(e["eta"]),
                "etd": datetime.fromisoformat(e["etd"]),
            }
            for e in store.port_schedule
            if e["berth_id"] == berth_id
        ]
        slots = berth_prediction.predict_berth_availability(berth_id, now, occupant_departure, events)
        forecast[berth_id] = [
            {
                "available_from": s.available_from.isoformat(),
                "available_until": s.available_until.isoformat() if s.available_until else None,
                "confidence": s.confidence,
            }
            for s in slots
        ]
    return forecast
