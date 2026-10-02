import pandas as pd
import numpy as np

from alfa_workbench.residuals import compute_gnc_residials

def test_compute_gnc_residuals_smoothing() -> None:
    """
    Test the ability of compute_gnc_residuals to smooth instantaneous spikes in tracking error
    """

    df = pd.DataFrame({
        "timestamp_s":  [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        "roll_cmd":     [5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        "roll_meas":    [5.0, 5.0, 1.5, 5.0, 5.0, 5.0],
    })

    result = compute_gnc_residials(df, window=3)

    print("\n--- SANITY CHECK: GNC RESIDUALS ---")
    print(result[["timestamp_s", "roll_err", "roll_err_rms"]])
    print("-----------------------------------")

    assert 3.5 == result[result["timestamp_s"] == 0.2].iloc[0]["roll_err"]

    assert np.isclose(
        result[result["timestamp_s"] == 0.2].iloc[0]["roll_err_rms"],
        np.sqrt((0**2 + 0**2 + 3.5**2) / 3)
    )