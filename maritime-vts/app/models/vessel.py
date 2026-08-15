"""Vessel and live track data models."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VesselType(str, Enum):
    CONTAINER = "container"
    BULK_CARRIER = "bulk_carrier"
    TANKER = "tanker"
    LNG_CARRIER = "lng_carrier"
    RORO = "roro"
    GENERAL_CARGO = "general_cargo"
    PASSENGER = "passenger"


class NavStatus(str, Enum):
    UNDERWAY_USING_ENGINE = "underway_using_engine"
    AT_ANCHOR = "at_anchor"
    MOORED = "moored"
    RESTRICTED_MANEUVERABILITY = "restricted_maneuverability"
    AGROUND = "aground"
    NOT_UNDER_COMMAND = "not_under_command"


class Vessel(BaseModel):
    mmsi: str = Field(..., description="Maritime Mobile Service Identity")
    imo_number: str
    name: str
    call_sign: str
    flag: str
    vessel_type: VesselType
    loa_m: float = Field(..., description="Length overall, meters")
    beam_m: float
    draft_m: float
    gross_tonnage: int
    destination_berth: Optional[str] = None
    eta: Optional[datetime] = None
    agent: Optional[str] = None


class VesselTrack(BaseModel):
    """A single fused position report for a vessel (AIS and/or radar derived)."""
    mmsi: str
    source: str = Field(..., description="Origin of the report: 'ais', 'radar', or 'fused'")
    lat: float
    lon: float
    sog_kt: float = Field(..., description="Speed over ground, knots")
    cog_deg: float = Field(..., description="Course over ground, degrees")
    heading_deg: Optional[float] = None
    nav_status: NavStatus = NavStatus.UNDERWAY_USING_ENGINE
    timestamp: datetime
