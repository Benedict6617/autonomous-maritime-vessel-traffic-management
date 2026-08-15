"""Harbor pilot assignment.

Matches an available, rested, appropriately-licensed pilot to an inbound
vessel. Rest-hour logic is a simplified analogue of STCW/pilotage-authority
rest requirements (this is NOT a certified fatigue-management system —
see docs/COMPLIANCE.md).
"""
from dataclasses import dataclass

from app.models.pilot import Pilot, PilotLicenseClass

MIN_REST_HOURS_FOR_ASSIGNMENT = 6.0

LOA_LICENSE_THRESHOLDS = [
    (150.0, PilotLicenseClass.CLASS_A),
    (250.0, PilotLicenseClass.CLASS_B),
    (float("inf"), PilotLicenseClass.CLASS_C),
]


@dataclass
class PilotAssignmentResult:
    pilot_id: str | None
    pilot_name: str | None
    reason: str


def required_license_class(vessel_loa_m: float) -> PilotLicenseClass:
    for threshold, license_class in LOA_LICENSE_THRESHOLDS:
        if vessel_loa_m <= threshold:
            return license_class
    return PilotLicenseClass.CLASS_C


_LICENSE_RANK = {
    PilotLicenseClass.CLASS_A: 1,
    PilotLicenseClass.CLASS_B: 2,
    PilotLicenseClass.CLASS_C: 3,
}


def assign_pilot(vessel_loa_m: float, pilots: list[Pilot]) -> PilotAssignmentResult:
    """Pick the best available pilot for a vessel of the given LOA.

    Selection order: must be on duty, rested, and licensed for a vessel of
    this size or larger; among eligible pilots, prefer the closest license
    match (don't "waste" a Class C pilot on a small coaster if a Class A/B
    pilot is available) and then the most rest hours remaining.
    """
    required = required_license_class(vessel_loa_m)
    required_rank = _LICENSE_RANK[required]

    eligible = [
        p
        for p in pilots
        if p.on_duty
        and p.current_assignment_mmsi is None
        and p.rest_hours_remaining >= MIN_REST_HOURS_FOR_ASSIGNMENT
        and _LICENSE_RANK[p.license_class] >= required_rank
    ]

    if not eligible:
        return PilotAssignmentResult(
            pilot_id=None,
            pilot_name=None,
            reason=f"No pilot on duty is both rested and licensed for {required.value} vessels.",
        )

    eligible.sort(key=lambda p: (_LICENSE_RANK[p.license_class], -p.rest_hours_remaining))
    best = eligible[0]
    return PilotAssignmentResult(
        pilot_id=best.pilot_id,
        pilot_name=best.name,
        reason=f"Licensed {best.license_class.value}, {best.rest_hours_remaining}h rest remaining.",
    )
