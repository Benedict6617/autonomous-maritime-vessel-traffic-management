from fastapi import APIRouter

from app.db.database import store

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/buoys")
def list_buoys():
    return store.weather_buoys
