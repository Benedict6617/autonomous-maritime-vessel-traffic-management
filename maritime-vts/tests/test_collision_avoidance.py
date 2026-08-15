from datetime import datetime

from app.models.vessel import VesselTrack
from app.services.collision_avoidance import compute_cpa_tcpa, screen_traffic

NOW = datetime(2026, 8, 14, 12, 0, 0)


def _track(mmsi, lat, lon, sog, cog):
    return VesselTrack(
        mmsi=mmsi, source="ais", lat=lat, lon=lon, sog_kt=sog, cog_deg=cog,
        heading_deg=cog, nav_status="underway_using_engine", timestamp=NOW,
    )


def test_head_on_converging_vessels_flagged_high_risk():
    a = _track("A", 41.000, -71.300, 12.0, 90)   # heading east
    b = _track("B", 41.000, -71.250, 12.0, 270)  # heading west, same latitude, closing
    risk = compute_cpa_tcpa(a, b)
    assert risk.cpa_nm < 0.5
    assert risk.risk_level in ("high", "medium")


def test_diverging_vessels_are_not_flagged():
    a = _track("A", 41.000, -71.300, 12.0, 90)    # heading east
    b = _track("B", 41.000, -71.250, 12.0, 90)    # also heading east, same speed -> no closure
    risk = compute_cpa_tcpa(a, b)
    assert risk.risk_level == "none"


def test_screen_traffic_returns_only_flagged_pairs_sorted_by_urgency():
    a = _track("A", 41.000, -71.300, 12.0, 90)
    b = _track("B", 41.000, -71.250, 12.0, 270)
    c = _track("C", 42.500, -70.000, 5.0, 0)  # far away, irrelevant
    risks = screen_traffic([a, b, c])
    assert all(r.risk_level != "none" for r in risks)
    assert {"A", "B"} <= {risks[0].mmsi_a, risks[0].mmsi_b}
