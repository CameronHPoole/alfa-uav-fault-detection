from pathlib import Path
import pandas as pd
from alfa_workbench.loader import SequenceLoader


def test_load_telemetry_merges_causally(tmp_path: Path) -> None:
    # ---- Testing DF merging ----
    prefix = "flight_01"

    # 1. Fake IMU data at 0.0s, 0.1s, 0.2s
    imu_csv = tmp_path / f"{prefix}_mavros-imu-data.csv"
    imu_csv.write_text(
        "%time,field.linear_acceleration.z\n"
        "0e8,-9.8\n"
        "1e8,-9.8\n"
        "2e8,-9.8\n"
    )

    # 2. Fake Roll data that only updates at 0.0s and 0.2s
    roll_csv = tmp_path / f"{prefix}_mavros-nav_info-roll.csv"
    roll_csv.write_text(
        "%time,field.commanded,field.measured\n"
        "0e8,15.0,14.5\n"
        "2e8,20.0,19.5\n"
    )

    loader = SequenceLoader(tmp_path, prefix)
    df = loader.load_telemetry()

    print("\n--- SANITY CHECK: MERGED DATAFRAME ---")
    print(df.head())
    print("--------------------------------------")

    # The DataFrame should have exactly 3 rows (driven by the IMU)
    assert len(df) == 3

    # At t=0.1s, the roll command should hold the previous value (15.0), NOT interpolate to 17.5
    row_at_100ms = df[df["flight_time_s"] == 0.1].iloc[0]
    assert row_at_100ms["roll_cmd"] == 15.0


def test_missing_roll_degrades_gracefully(tmp_path: Path) -> None:
    # ---- Testing graceful degredation ----
    prefix = "flight_02"

    # 1. Fake IMU data only
    imu_csv = tmp_path / f"{prefix}_mavros-imu-data.csv"
    imu_csv.write_text(
        "%time,field.linear_acceleration.z\n"
        "0e8,-9.8\n"
        "1e8,-9.8\n"
    )
    
    # Notice we intentionally DO NOT create the roll_csv file

    loader = SequenceLoader(tmp_path, prefix)
    df = loader.load_telemetry()

    print("\n--- SANITY CHECK: MISSING ROLL DATA ---")
    print(df.head())
    print("---------------------------------------")

    # The DataFrame should still generate the timeline
    assert len(df) == 2
    assert "timestamp_s" in df.columns
    assert "flight_time_s" in df.columns
    
    # But it should safely omit the roll columns without crashing
    assert "roll_cmd" not in df.columns
    assert "roll_meas" not in df.columns