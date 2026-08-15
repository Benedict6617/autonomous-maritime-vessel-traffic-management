"""Berth, terminal, and anchorage models."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CraneType(str, Enum):
    GANTRY = "gantry"
    MOBILE_HARBOR_CRANE = "mobile_harbor_crane"
    NONE = "none"


class Berth(BaseModel):
    berth_id: str
    terminal: str
    max_loa_m: float
    max_draft_m: float
    crane_type: CraneType
    current_occupant_mmsi: Optional[str] = None
    occupied_until: Optional[datetime] = None


class AnchorageSlot(BaseModel):
    """A vessel waiting for a berth assignment."""
    mmsi: str
    requested_at: datetime
    priority_score: float
    reason: str
    estimated_wait_hours: Optional[float] = None
