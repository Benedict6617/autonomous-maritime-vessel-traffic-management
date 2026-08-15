from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.db.database import store
from app.models.manifest import CrewManifest
from app.services.customs_integration import check_manifest_compliance

router = APIRouter(prefix="/manifests", tags=["manifests"])


@router.get("")
def list_manifests():
    return list(store.manifests.values())


@router.get("/{mmsi}")
def get_manifest_compliance(mmsi: str):
    raw = store.manifests.get(mmsi)
    if not raw:
        raise HTTPException(status_code=404, detail="Manifest not found")

    settings = get_settings()
    manifest = CrewManifest(**raw)
    result = check_manifest_compliance(manifest, settings.customs_advance_notice_hours)
    return result.__dict__
