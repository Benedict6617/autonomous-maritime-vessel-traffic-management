"""Collision risk assessment using CPA/TCPA (Closest Point of Approach /
Time to Closest Point of Approach) — the standard technique used in real
VTS and ARPA radar systems to flag converging traffic.
"""
import math
from dataclasses import dataclass

from app.models.vessel import VesselTrack

NM_TO_M = 1852.0


@dataclass
class CollisionRisk:
    mmsi_a: str
    mmsi_b: str
    cpa_nm: float
    tcpa_min: float
    risk_level: str  # "none", "low", "medium", "high"


def _velocity_components(sog_kt: float, cog_deg: float) -> tuple[float, float]:
    """Decompose speed/course into north/east velocity components (kt)."""
    rad = math.radians(cog_deg)
    v_north = sog_kt * math.cos(rad)
    v_east = sog_kt * math.sin(rad)
    return v_north, v_east


def _relative_position_nm(a: VesselTrack, b: VesselTrack) -> tuple[float, float]:
    """Approximate flat-earth north/east offset of b relative to a, in nm.

    Valid for the short ranges (a few nm) typical of coastal VTS collision
    screening; a full geodesic isn't necessary at this scale.
    """
    d_lat_nm = (b.lat - a.lat) * 60.0
    mean_lat_rad = math.radians((a.lat + b.lat) / 2)
    d_lon_nm = (b.lon - a.lon) * 60.0 * math.cos(mean_lat_rad)
    return d_lat_nm, d_lon_nm


def compute_cpa_tcpa(a: VesselTrack, b: VesselTrack) -> CollisionRisk:
    """Compute CPA (nm) and TCPA (minutes) between two vessel tracks."""
    north0, east0 = _relative_position_nm(a, b)  # relative position of b wrt a

    van, vae = _velocity_components(a.sog_kt, a.cog_deg)
    vbn, vbe = _velocity_components(b.sog_kt, b.cog_deg)
    rel_vn, rel_ve = vbn - van, vbe - vae  # relative velocity of b wrt a, kt

    rel_speed_sq = rel_vn**2 + rel_ve**2

    if rel_speed_sq < 1e-6:
        # No relative motion: CPA is the current range, never changes.
        cpa = math.hypot(north0, east0)
        tcpa = 0.0 if cpa == 0 else float("inf")
    else:
        # Time (hours) at which relative distance is minimized.
        t_hours = -(north0 * rel_vn + east0 * rel_ve) / rel_speed_sq
        t_hours = max(t_hours, 0.0)  # CPA in the past isn't operationally relevant
        cpa_north = north0 + rel_vn * t_hours
        cpa_east = east0 + rel_ve * t_hours
        cpa = math.hypot(cpa_north, cpa_east)
        tcpa = t_hours * 60.0

    risk_level = _classify_risk(cpa, tcpa)
    return CollisionRisk(mmsi_a=a.mmsi, mmsi_b=b.mmsi, cpa_nm=round(cpa, 3), tcpa_min=round(tcpa, 1), risk_level=risk_level)


def _classify_risk(cpa_nm: float, tcpa_min: float) -> str:
    """Simplified risk banding based on IMO/COLREGS-informed thresholds
    commonly used in ARPA/VTS operator guidance (not a substitute for
    officer judgment or a certified ARPA system).
    """
    if tcpa_min < 0 or tcpa_min == float("inf"):
        return "none"
    if cpa_nm < 0.5 and tcpa_min <= 12:
        return "high"
    if cpa_nm < 1.0 and tcpa_min <= 20:
        return "medium"
    if cpa_nm < 2.0 and tcpa_min <= 30:
        return "low"
    return "none"


def screen_traffic(tracks: list[VesselTrack]) -> list[CollisionRisk]:
    """Pairwise CPA/TCPA screening across all active tracks.

    O(n^2) — appropriate for the traffic density of a single coastal VTS
    sector (tens of vessels), not a basin-wide/global feed.
    """
    risks: list[CollisionRisk] = []
    for i in range(len(tracks)):
        for j in range(i + 1, len(tracks)):
            risk = compute_cpa_tcpa(tracks[i], tracks[j])
            if risk.risk_level != "none":
                risks.append(risk)
    return sorted(risks, key=lambda r: (r.risk_level != "high", r.tcpa_min))
