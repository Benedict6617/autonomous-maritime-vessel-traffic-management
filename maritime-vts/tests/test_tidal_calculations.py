from datetime import datetime, timedelta

from app.services.tidal_calculations import (
    find_safe_tidal_windows,
    tide_height_m,
    under_keel_clearance_m,
)

EPOCH = datetime(2026, 1, 1)


def test_tide_height_oscillates_around_mean_sea_level():
    heights = [tide_height_m(EPOCH + timedelta(hours=h), EPOCH) for h in range(0, 25)]
    assert min(heights) < 2.4 < max(heights)


def test_under_keel_clearance_decreases_with_shallower_depth():
    t = EPOCH + timedelta(hours=3)
    deep = under_keel_clearance_m(t, EPOCH, charted_depth_m=20.0, vessel_draft_m=10.0)
    shallow = under_keel_clearance_m(t, EPOCH, charted_depth_m=12.0, vessel_draft_m=10.0)
    assert deep > shallow


def test_find_safe_tidal_windows_returns_valid_ranges():
    windows = find_safe_tidal_windows(
        epoch=EPOCH,
        search_start=EPOCH,
        search_hours=48,
        charted_depth_m=13.0,
        vessel_draft_m=12.0,
        min_required_ukc_m=1.0,
    )
    for w in windows:
        assert w.end > w.start
        assert w.min_clearance_m >= 1.0
