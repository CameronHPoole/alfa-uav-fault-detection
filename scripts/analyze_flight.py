import argparse
from pathlib import Path

from alfa_workbench.loader import SequenceLoader
from alfa_workbench.residuals import compute_gnc_residials
from alfa_workbench.detector import fault_detector

def main() -> None:
    parser = argparse.ArgumentParser(description="Run FDI on an ALFA sequence.")
    parser.add_argument("sequence_dir", type=str, help="Path to the ALFA sequence directory")
    args = parser.parse_args()

    seq_dir = Path(args.sequence_dir)
    prefix = seq_dir.name # ALFA folder name is the prefix of all the files

    print(f"---- Analyzing flight: {prefix}")

    # 1. Data ingest
    loader = SequenceLoader(seq_dir, prefix)
    df = loader.load_telemetry()
    t_fault = loader.get_ground_truth_fault_time("aileron") # Naive to only aileron faults

    # 2. Compute features
    df = compute_gnc_residials(df, window=25, cusum_drift=4.0)

    # 3. Evaluate requirements
    static_threshold = 150.0
    result = fault_detector(
        df,
        threshold_deg=static_threshold,
        t_fault=t_fault,
        feature_col="roll_err_cusum"
    )

    # 4. Print analysis
    print(f"\nGround Truth Fault Time: {t_fault:.2f} seconds" if t_fault else "Nominal Flight")
    print(f"Threshold: {static_threshold} degrees (Rolling RMS)")
    print("---- V&V ----")

    if result["tp"]:
        print("PASS: Valid Detection")
        print(f"Detection Latency: {result["latency_s"]} seconds")
    elif result["fp"]:
        print("FAIL: False Positive")
    elif result["fn"]:
        print("FAIL: False Negative")
    else:
        print("PASS: True Negative / Nominal Flight")

if __name__ == "__main__":
    main()