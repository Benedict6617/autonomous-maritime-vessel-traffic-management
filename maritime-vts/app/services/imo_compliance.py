"""IMO pre-arrival compliance checklist engine.

A lightweight rule engine evaluating common IMO / port-state obligations
that a harbor master's office typically tracks before granting a berth,
including FAL Convention documentation, ballast water reporting (BWM
Convention), and MARPOL garbage/oil record book confirmation. This is a
compliance *aid*, not a substitute for flag-state or port-state control
inspection — see docs/COMPLIANCE.md for scope.
"""
from dataclasses import dataclass


@dataclass
class ComplianceItem:
    code: str
    description: str
    satisfied: bool


@dataclass
class ComplianceReport:
    mmsi: str
    items: list[ComplianceItem]
    fully_compliant: bool


def evaluate_imo_compliance(vessel_declarations: dict) -> ComplianceReport:
    """vessel_declarations: dict of booleans/flags submitted by the vessel
    agent, e.g.:
    {
        "fal_general_declaration": True,
        "fal_crew_list": True,
        "fal_passenger_list": True,
        "ballast_water_report": True,
        "garbage_record_book_current": True,
        "oil_record_book_current": True,
        "pre_arrival_notice_filed": True,
    }
    """
    checklist = [
        ("FAL-1", "IMO General Declaration submitted", "fal_general_declaration"),
        ("FAL-5", "Crew List submitted", "fal_crew_list"),
        ("FAL-6", "Passenger List submitted", "fal_passenger_list"),
        ("BWM-1", "Ballast Water Report Form submitted", "ballast_water_report"),
        ("MARPOL-V", "Garbage Record Book current", "garbage_record_book_current"),
        ("MARPOL-I", "Oil Record Book current", "oil_record_book_current"),
        ("PAN-1", "Pre-arrival notice filed within required window", "pre_arrival_notice_filed"),
    ]

    items = [
        ComplianceItem(code=code, description=desc, satisfied=bool(vessel_declarations.get(key, False)))
        for code, desc, key in checklist
    ]
    return ComplianceReport(
        mmsi=vessel_declarations.get("mmsi", "unknown"),
        items=items,
        fully_compliant=all(i.satisfied for i in items),
    )
