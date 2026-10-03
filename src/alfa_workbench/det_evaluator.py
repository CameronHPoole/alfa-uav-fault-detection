import pandas as pd

def failure_detector(df: pd.DataFrame, threshold_deg: float, t_fault: float | None) -> dict:
    """
    Deterministic fault detector utilizing a fixed threshold

    Args:
        df (pd.DataFrame): flight dataframe
        threshold_deg (float): fixed threshold in degrees
        t_fault (float | None): ground truth time a failure occured

    Returns:
        Dict: {tp, fp, fn, latency_s}
    """
    # RMS threshold
    alarms = df[df["roll_err_rms"] > threshold_deg]

    # save first index occurance of an alarm
    t_pred = alarms["timestamp_s"].iloc[0] if not alarms.empty else None
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
        "latency_s": None if not latency_s >= 0 else latency_s, 
    }
