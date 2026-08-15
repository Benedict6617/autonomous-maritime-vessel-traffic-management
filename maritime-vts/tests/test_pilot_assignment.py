from app.models.pilot import Pilot, PilotLicenseClass
from app.services.pilot_assignment import assign_pilot, required_license_class


def _pilot(pilot_id, license_class, on_duty=True, rest=8.0, assignment=None):
    return Pilot(
        pilot_id=pilot_id, name=pilot_id, license_class=license_class,
        on_duty=on_duty, rest_hours_remaining=rest, current_assignment_mmsi=assignment,
    )


def test_required_license_class_scales_with_vessel_size():
    assert required_license_class(120.0) == PilotLicenseClass.CLASS_A
    assert required_license_class(200.0) == PilotLicenseClass.CLASS_B
    assert required_license_class(350.0) == PilotLicenseClass.CLASS_C


def test_assigns_eligible_rested_pilot():
    pilots = [
        _pilot("P1", PilotLicenseClass.CLASS_A),
        _pilot("P2", PilotLicenseClass.CLASS_C),
    ]
    result = assign_pilot(120.0, pilots)
    assert result.pilot_id == "P1"  # closest license match preferred over overqualified P2


def test_excludes_pilots_below_rest_threshold():
    pilots = [_pilot("P1", PilotLicenseClass.CLASS_A, rest=2.0)]
    result = assign_pilot(100.0, pilots)
    assert result.pilot_id is None


def test_excludes_already_assigned_pilots():
    pilots = [_pilot("P1", PilotLicenseClass.CLASS_C, assignment="999999999")]
    result = assign_pilot(300.0, pilots)
    assert result.pilot_id is None


def test_no_eligible_pilot_returns_reason():
    result = assign_pilot(300.0, [])
    assert result.pilot_id is None
    assert "No pilot" in result.reason
