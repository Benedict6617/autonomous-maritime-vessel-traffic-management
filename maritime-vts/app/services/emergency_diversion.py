"""Emergency diversion protocol.

Given a distress or diversion event, identifies the nearest suitable
anchorage or alternate port and produces the notification list of
stakeholders that must be alerted, per typical VTS emergency procedure.
"""
from dataclasses import dataclass

from app.utils.geo import haversine_nm

SEVERITY_NOTIFY_LISTS = {
    "low": ["harbor_master", "vessel_agent"],
    "medium": ["harbor_master", "vessel_agent", "pilots_on_duty", "tugboat_operators"],
    "high": [
        "harbor_master",
        "vessel_agent",
        "pilots_on_duty",
        "tugboat_operators",
        "coast_guard",
        "port_authority_duty_officer",
    ],
    "critical": [
        "harbor_master",
        "vessel_agent",
        "pilots_on_duty",
        "tugboat_operators",
        "coast_guard",
        "port_authority_duty_officer",
        "emergency_medical_services",
        "customs_and_immigration",
    ],
}


@dataclass
class DiversionOption:
    name: str
    lat: float
    lon: float
    distance_nm: float
    suitable: bool
    reason: str


@dataclass
class DiversionPlan:
    mmsi: str
    severity: str
    notify: list[str]
    options: list[DiversionOption]


def evaluate_diversion_options(
    vessel_lat: float,
    vessel_lon: float,
    vessel_draft_m: float,
    candidate_anchorages: list[dict],
) -> list[DiversionOption]:
    """Rank candidate anchorages/alternate ports by distance, filtering out
    those with insufficient charted depth for the vessel's draft.
    """
    options = []
    for c in candidate_anchorages:
        dist = haversine_nm(vessel_lat, vessel_lon, c["lat"], c["lon"])
        suitable = c["charted_depth_m"] >= vessel_draft_m + 1.0  # 1m safety margin
        reason = (
            "Sufficient depth and within range."
            if suitable
            else f"Charted depth {c['charted_depth_m']}m insufficient for {vessel_draft_m}m draft."
        )
        options.append(
            DiversionOption(
                name=c["name"],
                lat=c["lat"],
                lon=c["lon"],
                distance_nm=round(dist, 2),
                suitable=suitable,
                reason=reason,
            )
        )
    return sorted(options, key=lambda o: (not o.suitable, o.distance_nm))


def build_diversion_plan(
    mmsi: str,
    severity: str,
    vessel_lat: float,
    vessel_lon: float,
    vessel_draft_m: float,
    candidate_anchorages: list[dict],
) -> DiversionPlan:
    options = evaluate_diversion_options(vessel_lat, vessel_lon, vessel_draft_m, candidate_anchorages)
    notify = SEVERITY_NOTIFY_LISTS.get(severity, SEVERITY_NOTIFY_LISTS["medium"])
    return DiversionPlan(mmsi=mmsi, severity=severity, notify=notify, options=options)
