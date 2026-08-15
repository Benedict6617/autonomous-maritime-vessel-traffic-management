"""Tugboat assignment for vessel movements.

Required bollard pull is estimated from vessel size (a standard rule-of-thumb
approach used by many small/medium ports that don't run full ship-handling
simulations for every call); larger vessels may require two tugs.
"""
from dataclasses import dataclass

from app.models.tugboat import Tugboat, TugStatus

# Rough bollard-pull-per-meter-LOA guidance used by several regional pilotage
# authorities for routine (non-heavy-weather) berthing assistance.
BOLLARD_PULL_PER_METER_LOA = 0.35
TWO_TUG_LOA_THRESHOLD_M = 200.0


@dataclass
class TugAssignmentResult:
    tug_ids: list[str]
    total_bollard_pull_tons: float
    required_bollard_pull_tons: float
    sufficient: bool
    reason: str


def estimate_required_bollard_pull_tons(vessel_loa_m: float) -> float:
    return round(vessel_loa_m * BOLLARD_PULL_PER_METER_LOA, 1)


def assign_tugs(vessel_loa_m: float, tugboats: list[Tugboat]) -> TugAssignmentResult:
    required = estimate_required_bollard_pull_tons(vessel_loa_m)
    tugs_needed = 2 if vessel_loa_m >= TWO_TUG_LOA_THRESHOLD_M else 1

    available = [t for t in tugboats if t.status == TugStatus.AVAILABLE]
    available.sort(key=lambda t: -t.bollard_pull_tons)  # strongest first

    selected: list[Tugboat] = []
    total_pull = 0.0
    for tug in available:
        if len(selected) >= tugs_needed and total_pull >= required:
            break
        selected.append(tug)
        total_pull += tug.bollard_pull_tons

    sufficient = total_pull >= required and len(selected) >= tugs_needed
    reason = (
        f"Assigned {len(selected)} tug(s) totaling {total_pull}t against a "
        f"{required}t requirement."
        if sufficient
        else f"Only {total_pull}t available from {len(selected)} tug(s); "
        f"{required}t required. Consider delaying the movement or requesting mutual aid."
    )

    return TugAssignmentResult(
        tug_ids=[t.tug_id for t in selected],
        total_bollard_pull_tons=round(total_pull, 1),
        required_bollard_pull_tons=required,
        sufficient=sufficient,
        reason=reason,
    )
