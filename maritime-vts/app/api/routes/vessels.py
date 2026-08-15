from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException

from app.db.database import store
from app.services import ais_ingestion, collision_avoidance, radar_processing

router = APIRouter(prefix="/vessels", tags=["vessels"])


@router.get("")
def list_vessels():
    return list(store.vessels.values())


@router.get("/{mmsi}")
def get_vessel(mmsi: str):
    vessel = store.vessels.get(mmsi)
    if not vessel:
        raise HTTPException(status_code=404, detail="Vessel not found")
    return vessel


@router.get("/track/current")
def current_tracks():
    """Fused AIS + (simulated) radar picture of vessels currently in the sector."""
    tracks = ais_ingestion.ingest_feed(store.ais_feed)
    # Deduplicate to most recent report per MMSI
    latest: dict[str, object] = {}
    for t in tracks:
        if t.mmsi not in latest or t.timestamp > latest[t.mmsi].timestamp:
            latest[t.mmsi] = t
    return [t.model_dump() for t in latest.values()]


@router.get("/{mmsi}/collision-risk")
def collision_risk(mmsi: str):
    tracks = ais_ingestion.ingest_feed(store.ais_feed)
    latest: dict[str, object] = {}
    for t in tracks:
        if t.mmsi not in latest or t.timestamp > latest[t.mmsi].timestamp:
            latest[t.mmsi] = t

    if mmsi not in latest:
        raise HTTPException(status_code=404, detail="No current track for vessel")

    all_risks = collision_avoidance.screen_traffic(list(latest.values()))
    relevant = [r for r in all_risks if mmsi in (r.mmsi_a, r.mmsi_b)]
    return [r.__dict__ for r in relevant]
