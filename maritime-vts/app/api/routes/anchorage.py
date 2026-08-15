from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.anchorage_queue import AnchorageQueue, QueuedVessel

router = APIRouter(prefix="/anchorage", tags=["anchorage"])

# Process-lifetime queue instance. In a multi-worker deployment this would
# move to a shared store (DB/Redis) — noted in docs/ARCHITECTURE.md.
_queue = AnchorageQueue()


class AnchorageRequest(BaseModel):
    mmsi: str
    loa_m: float
    cargo_category: str
    is_emergency: bool = False


@router.post("/queue")
def add_to_queue(request: AnchorageRequest):
    vessel = QueuedVessel(
        mmsi=request.mmsi,
        requested_at=datetime.utcnow(),
        loa_m=request.loa_m,
        cargo_category=request.cargo_category,
        is_emergency=request.is_emergency,
    )
    _queue.add(vessel)
    return {"mmsi": request.mmsi, "queue_position": _queue.position_of(request.mmsi)}


@router.delete("/queue/{mmsi}")
def remove_from_queue(mmsi: str):
    _queue.remove(mmsi)
    return {"mmsi": mmsi, "removed": True}


@router.get("/queue")
def get_queue():
    return [
        {
            "mmsi": v.mmsi,
            "requested_at": v.requested_at.isoformat(),
            "cargo_category": v.cargo_category,
            "is_emergency": v.is_emergency,
            "queue_position": idx + 1,
        }
        for idx, v in enumerate(_queue.ordered())
    ]
