"""Loader module for ALFA UAV telemetry data."""
from pathlib import Path
import pandas as pd


class SequenceLoader:
    """Loads and merges telemetry data from ALFA CSV files."""

    def __init__(self, sequence_dir: str | Path, prefix: str):
        self.sequence_dir = Path(sequence_dir)
        self.prefix = prefix

    def _read_csv(self, suffix: str) -> pd.DataFrame:
        path = self.sequence_dir / f"{self.prefix}_{suffix}"
        if not path.exists():
            return pd.DataFrame()

        df = pd.read_csv(path)
        # ALFA timestamps are in nanoseconds under the '%time' column
        if "%time" in df.columns:
            df["timestamp_s"] = df["%time"] * 1e-9

        return df.sort_values("timestamp_s").reset_index(drop=True)

    def load_telemetry(self) -> pd.DataFrame:
        """Loads the high-rate IMU and merges the lower-rate roll data causally."""
        imu_df = self._read_csv("mavros-imu-data.csv")
        if imu_df.empty:
            raise FileNotFoundError(f"Missing IMU data for {self.prefix}")

        # Create our synchronized time base
        t0 = imu_df["timestamp_s"].iloc[0]
        base_df = pd.DataFrame(
            {
                "timestamp_s": imu_df["timestamp_s"],
                "flight_time_s": imu_df["timestamp_s"] - t0,
            }
        )

        # Bring in the Roll tracking data
        roll_df = self._read_csv("mavros-nav_info-roll.csv")
        if not roll_df.empty:
            roll_df = roll_df[
                ["timestamp_s", "field.commanded", "field.measured"]
            ].rename(
                columns={"field.commanded": "roll_cmd", "field.measured": "roll_meas"}
            )
            # merge_asof 'backward' direction ensures we don't look into the future
            base_df = pd.merge_asof(
                base_df, roll_df, on="timestamp_s", direction="backward"
            )

        return base_df