import pandas as pd
import numpy as np

def compute_gnc_residuals(
        df: pd.DataFrame, 
        window: int = 25, 
        cusum_drift = 5.0,
        trim_samples = 5 * 50 # 5 sec @ 50hz        
    ) -> pd.DataFrame:
    """
    Computes tracking residuals and a causal rolling RMS.
    At 50 Hz, window = 25 equals a 0.5 second smoothing window.

    Args:
        df (pd.DataFrame): _description_
        window (int, optional): _description_. Defaults to 25.

    Returns:
        pd.DataFrame: the input dataframe with two new rows appended.
                        1. ["roll_err"]: instantaneous tracking error
                        2. ["roll_err_rms"]: error -> squared -> rolling mean -> square rooted
    """

    out = df.copy()

    if "roll_cmd" in out.columns and "roll_meas" in out.columns:
        out["roll_err"] = out["roll_cmd"] - out["roll_meas"]

        # Causal Rolling RMS
        out["roll_err_rms"] = np.sqrt(
            (out["roll_err"] ** 2)
            .rolling(window=window, min_periods=1)
            .mean()
            )

        # Washout Filter (remove steady state corrections from cusum)
        steady_state_error = out["roll_err"].rolling(
            window=trim_samples,
            min_periods=1
        ).mean()

        centered_error = out["roll_err"] - steady_state_error

        # Page's CUSUM Filter
        abs_err = np.abs(centered_error.values)
        cusum = np.zeros(len(abs_err))
        
        for i in range(1, len(abs_err)):
            cusum[i] = max(0.0, cusum[i-1] + abs_err[i] - cusum_drift)
            
        out["roll_err_cusum"] = cusum

    return out
