"""Weather buoy telemetry model."""
from datetime import datetime

from pydantic import BaseModel


class WeatherBuoyReading(BaseModel):
    buoy_id: str
    lat: float
    lon: float
    wind_speed_kt: float
    wind_dir_deg: float
    wave_height_m: float
    wave_period_s: float
    visibility_nm: float
    air_temp_c: float
    water_temp_c: float
    timestamp: datetime
