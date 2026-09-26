from pathlib import Path

import pytest
from pydantic import ValidationError

from alfa_workbench.schema import DetectorThresholds, load_config


def test_load_carbon_z_config() -> None:
    config_path = Path("configs/carbon_z_limits.yaml")
    cfg = load_config(config_path)

    assert cfg.platform == "Carbon Z T-28"
    assert cfg.base_clock_hz == 50.0
    assert cfg.trim_initial_seconds == 10.0
    assert "REQ-FDI-002" in cfg.requirements
    assert cfg.detector_thresholds.roll_err_rms_deg == 8.0


def test_detector_thresholds_rejects_non_positive_values() -> None:
    with pytest.raises(ValidationError):
        DetectorThresholds(roll_err_rms_deg=-1.0)

    with pytest.raises(ValidationError):
        DetectorThresholds(airspeed_err_rms_mps=0.0)
