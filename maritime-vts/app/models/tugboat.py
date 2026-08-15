"""Tugboat model."""
from enum import Enum

from pydantic import BaseModel


class TugStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    MAINTENANCE = "maintenance"


class Tugboat(BaseModel):
    tug_id: str
    name: str
    bollard_pull_tons: float
    status: TugStatus
    home_berth: str
    assigned_mmsi: str | None = None
