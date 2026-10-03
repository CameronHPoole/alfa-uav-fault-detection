import pandas as pd
from alfa_workbench.det_evaluator import failure_detector

def test_evaluate_successful_detection() -> None:
    # Fault happens at t=2.0s. Alarm crosses threshold (10.0) at t=2.5s.
    df = pd.DataFrame({
        "timestamp_s": [1.0, 2.0, 2.5, 3.0],
        "roll_err_rms":  [1.0, 3.0, 11.0, 15.0]
    })
    
    result = failure_detector(df, threshold_deg=8.0, t_fault=2.0)
    print("\n--- SANITY CHECK: Result Dict ---")
    print(result)
    print("---------------------------------------")
    assert result["tp"] is True
    assert result["fp"] is False
    assert result["latency_s"] == 0.5  # 2.5s - 2.0s


def test_evaluate_false_positive_gust() -> None:
    # Fault happens at t=4.0s. But a wind gust pushes RMS to 9.0 at t=1.0s.
    df = pd.DataFrame({
        "timestamp_s": [1.0, 2.0, 4.0, 5.0],
        "roll_err_rms":  [9.0, 2.0, 2.0, 15.0]
    })
    
    result = failure_detector(df, threshold_deg=8.0, t_fault=4.0)
    
    # The detector failed because it cried wolf at t=1.0s
    assert result["fp"] is True
    assert result["tp"] is False


def test_evaluate_nominal_flight() -> None:
    # No fault injected (t_fault=None). Flight stays under threshold.
    df = pd.DataFrame({
        "timestamp_s": [1.0, 2.0, 3.0],
        "roll_err_rms":  [1.0, 2.0, 1.5]
    })
    
    result = failure_detector(df, threshold_deg=8.0, t_fault=None)
    
    assert result["fp"] is False
    assert result["fn"] is False