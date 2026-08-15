"""Harbor pilot model."""
from enum import Enum

from pydantic import BaseModel


class PilotLicenseClass(str, Enum):
    """Maximum vessel size class the pilot is licensed to handle."""
    CLASS_A = "class_a"  # up to 150m LOA
    CLASS_B = "class_b"  # up to 250m LOA
    CLASS_C = "class_c"  # unrestricted (LNG/ULCV endorsed)


class Pilot(BaseModel):
    pilot_id: str
    name: str
    license_class: PilotLicenseClass
    on_duty: bool
    rest_hours_remaining: float
    current_assignment_mmsi: str | None = None
