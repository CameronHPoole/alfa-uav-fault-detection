import argparse
from pathlib import Path
import matplotlib.pyplot as plt

from alfa_workbench.loader import SequenceLoader
from alfa_workbench.residuals import compute_gnc_residuals

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sequence_dir", type=str)
    args = parser.parse_args()

    seq_dir = Path(args.sequence_dir)
    loader = SequenceLoader(seq_dir, seq_dir.name)
    
    print("Loading telemetry...")
    df = loader.load_telemetry()
    t_fault = loader.get_ground_truth_fault_time("aileron")
    
    print("Computing features...")
    # Using the adaptive CUSUM settings
    df = compute_gnc_residuals(df, window=25, cusum_drift=10.0, trim_samples=250)

    # Filter out the first 20 seconds (takeoff) to match our evaluator
    plot_df = df[df["flight_time_s"] > 20.0].copy()

    # Create a 2-panel plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Top Panel: What the plane is actually doing
    ax1.plot(plot_df["flight_time_s"], plot_df["roll_cmd"], label="Commanded Roll", alpha=0.7)
    ax1.plot(plot_df["flight_time_s"], plot_df["roll_meas"], label="Measured Roll", alpha=0.7)
    if t_fault:
        ax1.axvline(t_fault, color='red', linestyle='--', label=f"Fault Injected ({t_fault:.1f}s)")
    ax1.set_ylabel("Roll Angle")
    ax1.set_title(f"Flight Dynamics: {seq_dir.name}")
    ax1.legend()
    ax1.grid(True)

    # Bottom Panel: What our algorithms see
    ax2.plot(plot_df["flight_time_s"], plot_df["roll_err_rms"], label="Rolling RMS (Old)", color='orange')
    ax2.plot(plot_df["flight_time_s"], plot_df["roll_err_cusum"], label="Adaptive CUSUM (New)", color='purple')
    if t_fault:
        ax2.axvline(t_fault, color='red', linestyle='--')
    
    # Draw our current threshold attempt
    ax2.axhline(150.0, color='black', linestyle=':', label="Current Threshold (150.0)")
    
    ax2.set_ylabel("Error Magnitude")
    ax2.set_xlabel("Flight Time (seconds)")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()