"""Multi-frequency parameter sweep.

Runs omega = 0.01, 0.03, 0.1, 0.3, 1.0 and saves results.
"""
import sys
import os
import csv
import warnings
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.gf_adaptive_match import compute

warnings.filterwarnings("ignore")


def main():
    omegas = [0.01, 0.03, 0.1, 0.3, 1.0]
    M = 1.0
    l = 0
    N = 128
    Cl = 1.0

    os.makedirs("results", exist_ok=True)

    results = []
    for omega in omegas:
        print(f"\n--- omega = {omega} ---")
        try:
            result = compute(M=M, l=l, omega=omega, N=N, Cl=Cl)
            result["status"] = "ok"
            print(f"  T={result['T']:.6e}, R={result['R']:.6e}, T1={result['T1']:.6e}, R1={result['R1']:.6e}")
        except Exception as e:
            result = {
                "omega": omega, "N": N, "zp": np.nan,
                "T": np.nan, "R": np.nan, "T1": np.nan, "R1": np.nan,
                "matching_error": np.nan, "W_error": np.nan,
                "status": f"failed: {str(e)}"
            }
            print(f"  FAILED: {e}")
        results.append(result)

    # Save CSV
    csv_path = "results/frequency_sweep.csv"
    fields = ["omega", "N", "zp", "T", "R", "T1", "R1", "matching_error", "W_error", "status"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            row = {k: r.get(k, np.nan) for k in fields}
            for k in row:
                if isinstance(row[k], complex):
                    row[k] = f"{row[k].real}+{row[k].imag}j"
            writer.writerow(row)
    print(f"\nSaved frequency sweep to {csv_path}")


if __name__ == "__main__":
    main()
