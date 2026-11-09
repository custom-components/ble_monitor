"""Tests for the minimum Home Assistant version guard."""
import json
from pathlib import Path

import pytest
from ble_monitor import MIN_HA_VERSION, _require_min_ha_version


def test_older_home_assistant_is_refused_with_both_versions():
    """An older Home Assistant gets one actionable error, not a missing API."""
    with pytest.raises(ImportError) as error:
        _require_min_ha_version("2026.1.3")
    assert MIN_HA_VERSION in str(error.value)
    assert "2026.1.3" in str(error.value)


@pytest.mark.parametrize("version", [MIN_HA_VERSION, "2026.8.1", "2026.10.0b0", "2027.1.0"])
def test_supported_home_assistant_is_accepted(version):
    """The minimum version and anything newer load normally."""
    _require_min_ha_version(version)


def test_minimum_matches_hacs_json():
    """The guard and hacs.json must name the same minimum."""
    hacs_json = Path(__file__).parents[3] / "hacs.json"
    assert json.loads(hacs_json.read_text())["homeassistant"] == MIN_HA_VERSION
