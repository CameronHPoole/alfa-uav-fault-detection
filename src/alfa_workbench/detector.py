import pandas as pd

def fault_detector(
        df: pd.DataFrame, 
        threshold_deg: float, 
        t_fault: float | None, 
        trim_time = 10.0,
        feature_col: str = "roll_err_rms") -> dict:
    """
    Deterministic fault detector utilizing a fixed threshold

    Args:
        df (pd.DataFrame): flight dataframe
        threshold_deg (float): fixed threshold in degrees
        t_fault (float | None): ground truth time a failure occured
        trim_time = 10: Amount of time (s) to trim for transient takeoff to remove FP's

    Returns:
        Dict: {tp, fp, fn, latency_s}
    """
    # Trim transient startup time
    t_0 = df["timestamp_s"].iloc[0]
    valid_df = df[df["timestamp_s"] - t_0 >= trim_time]

    # RMS threshold
    alarms = valid_df[valid_df[feature_col] > threshold_deg]

    # save first index occurance of an alarm
    t_pred = alarms["flight_time_s"].iloc[0] if not alarms.empty else None
    num_alarms = alarms.size

    print(f"Number of alarms: {num_alarms}")

    # Case 1: No ground truth fault
    if t_fault is None:
        return {
            "tp": False,
            "fp": bool(t_pred is not None),
            "fn": False,
            "latency_s": None, 
        }
    
    # t_fault is true
    # Case 2: Ground truth fault
    if t_pred is None:
        return {
            "tp": False,
            "fp": False,
            "fn": True,
            "latency_s": None, 
        }

    # Case 3: Ground truth fault and we detected one
    latency_s = round(t_pred - t_fault, 3)
    return {
        "tp": bool(latency_s >= 0),
        "fp": bool(not latency_s >= 0),
        "fn": False,
        "latency_s": latency_s, # "latency_s": None if not latency_s >= 0 else latency_s, 
    }
