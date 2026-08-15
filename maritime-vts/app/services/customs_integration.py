"""Crew manifest / customs & immigration advance-notice compliance.

Checks manifest submissions against the port's configured advance-notice
window (commonly 24-96 hours depending on jurisdiction and vessel type —
see docs/COMPLIANCE.md). This module performs a timing/completeness check;
it is not a filing integration with a specific national single-window
system (e.g. US CBP eNOA/D, EU PortNet) — that requires jurisdiction-specific
credentials and message formats and is intentionally left as an integration
point (see docs/ARCHITECTURE.md).
"""
from dataclasses import dataclass
from datetime import datetime

from app.models.manifest import CrewManifest


@dataclass
class ComplianceCheck:
    mmsi: str
    advance_notice_met: bool
    hours_before_eta_filed: float
    customs_cleared: bool
    immigration_cleared: bool
    issues: list[str]


def check_manifest_compliance(manifest: CrewManifest, required_advance_hours: int) -> ComplianceCheck:
    hours_before_eta = (manifest.eta - manifest.manifest_filed_at).total_seconds() / 3600.0
    advance_notice_met = hours_before_eta >= required_advance_hours

    issues = []
    if not advance_notice_met:
        issues.append(
            f"Manifest filed only {round(hours_before_eta, 1)}h before ETA; "
            f"{required_advance_hours}h required."
        )
    if not manifest.customs_cleared:
        issues.append("Customs clearance pending.")
    if not manifest.immigration_cleared:
        issues.append("Immigration clearance pending.")

    return ComplianceCheck(
        mmsi=manifest.mmsi,
        advance_notice_met=advance_notice_met,
        hours_before_eta_filed=round(hours_before_eta, 1),
        customs_cleared=manifest.customs_cleared,
        immigration_cleared=manifest.immigration_cleared,
        issues=issues,
    )
