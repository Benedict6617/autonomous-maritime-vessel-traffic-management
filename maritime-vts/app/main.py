"""FastAPI application entrypoint for the Coastal Vessel Traffic Management System."""
from fastapi import FastAPI

from app.api.routes import (
    anchorage,
    berths,
    compliance,
    emergencies,
    manifests,
    pilots,
    tides,
    tugboats,
    vessels,
    weather,
)
from app.config import get_settings
from app.db.init_db import seed

settings = get_settings()

app = FastAPI(
    title="Coastal Vessel Traffic Management System",
    description=(
        f"Decision-support API for {settings.port_name} ({settings.port_unlocode}) — "
        "vessel tracking, collision risk, berth forecasting, pilot/tug coordination, "
        "tidal windows, emergency diversion, and regulatory compliance checks."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    seed()


@app.get("/", tags=["health"])
def root():
    return {
        "service": "Coastal Vessel Traffic Management System",
        "port": settings.port_name,
        "status": "operational",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


app.include_router(vessels.router)
app.include_router(berths.router)
app.include_router(weather.router)
app.include_router(anchorage.router)
app.include_router(pilots.router)
app.include_router(tugboats.router)
app.include_router(tides.router)
app.include_router(emergencies.router)
app.include_router(manifests.router)
app.include_router(compliance.router)
