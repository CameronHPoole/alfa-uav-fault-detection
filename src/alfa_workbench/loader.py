from pathlib import Path
import pandas as pd


class SequenceLoader:
    """A class for loading flight sequences.

    This class performs two primary pre-processing steps.
    
    1. Standardize timestamps: from nanoseconds -> seconds from t_0
    2. Handling asynchronous clocks: use IMU as master clock, then merge_asofdirection="backward")

    Attributes:
        None | TBD
    """
    def __init__(self, sequence_dir: str | Path, prefix: str):
        self.sequence_dir = Path(sequence_dir)
        self.prefix = prefix
        self.t_0 = None     # source of truth for a flights start time

    def _read_csv(self, suffix: str) -> pd.DataFrame:
        path = self.sequence_dir / f"{self.prefix}_{suffix}"
        if not path.exists():
            path = self.sequence_dir / suffix
        if not path.exists():
            matches = list(self.sequence_dir.glob(f"*{suffix}"))
            if not matches:
                print(f"COULD NOT FILE FILE ENDING IN {suffix} in {self.sequence_dir}")
                return pd.DataFrame()
            path = matches[0]
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

        if self.t_0 is None:
            self.t_0 = imu_df["timestamp_s"].iloc[0]

        # Create our synchronized time base
        base_df = pd.DataFrame(
            {
                "timestamp_s": imu_df["timestamp_s"],
                "flight_time_s": imu_df["timestamp_s"] - self.t_0,
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
                base_df, roll_df, on="timestamp_s", direction="backward")

        return base_df

    def get_ground_truth_fault_time(self, fault_type: str = "aileron") -> float | None:
        """
        Returns the timestamp of ground truth faults

        Args:
            type (str, optional): String defining the fault to be analyzed. Defaults to "aileron".

        Returns:
            float | None: timestamp in seconds | None if no ground truth fault in file or no file found
        """

        # get file and load df with _read_csv w/ fault type
        fault_df = self._read_csv(f"failure_status-{fault_type}.csv")

        if fault_df.empty or "field.data" not in fault_df.columns:
            return None
        
        fault_active = fault_df[fault_df["field.data"] > 0]
        if fault_active.empty:
            return None

        # get timpstamp (convert from nanoseconds * 1e-9)
        fault_time_s = fault_active["timestamp_s"].iloc[0]

        # time safety check
        if fault_time_s < 1e6:
            return float(fault_time_s)

        if self.t_0 is None:
                    self.load_telemetry()

        # return diff of timestamp and t_0
        return round(float(fault_time_s - self.t_0), 3)
