"""Crew manifest / customs & immigration model."""
from datetime import datetime

from pydantic import BaseModel


class CrewManifest(BaseModel):
    mmsi: str
    vessel_name: str
    crew_count: int
    nationalities: list[str]
    manifest_filed_at: datetime
    eta: datetime
    customs_cleared: bool = False
    immigration_cleared: bool = False


class Emergency(BaseModel):
    mmsi: str
    event_type: str  # e.g. "engine_failure", "fire", "medical", "grounding_risk"
    lat: float
    lon: float
    reported_at: datetime
    severity: str  # "low", "medium", "high", "critical"
