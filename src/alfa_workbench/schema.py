"""Data schemas and V&V contracts for the ALFA FDI Workbench."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class RequirementSpec(BaseModel):
    """Defines a single verifiable system requirement for fault detection."""

    description: str
    fault_type: str
    max_detection_latency_s: float = Field(gt=0.0)
    allow_false_positives: bool = False


class DetectorThresholds(BaseModel):
    """Physical GNC residual thresholds that trigger a fault alarm."""

    roll_err_rms_deg: float = Field(default=8.0, gt=0.0)
    pitch_err_rms_deg: float = Field(default=6.0, gt=0.0)
    yaw_err_rms_deg: float = Field(default=10.0, gt=0.0)
    airspeed_err_rms_mps: float = Field(default=3.5, gt=0.0)


class WorkbenchConfig(BaseModel):
    """Top-level configuration contract loaded from YAML."""

    platform: str
    base_clock_hz: float = Field(default=50.0, gt=0.0)
    trim_initial_seconds: float = Field(default=10.0, ge=0.0)
    requirements: dict[str, RequirementSpec]
    detector_thresholds: DetectorThresholds


class SequenceEvaluationResult(BaseModel):
    """Structured V&V output for a single flight test sequence."""

    sequence_name: str
    ground_truth_fault: str
    fault_onset_time_s: float | None = None
    detected_time_s: float | None = None
    detection_latency_s: float | None = None
    false_positive: bool
    true_positive: bool
    false_negative: bool
    true_negative: bool
    passed_vv: bool


def load_config(config_path: Path | str) -> WorkbenchConfig:
    """Reads and validates a YAML workbench configuration file."""
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f)
    return WorkbenchConfig.model_validate(raw_data)
