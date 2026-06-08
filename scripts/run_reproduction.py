"""One-click reproduction of the Schwarzschild Green-function spectral method.

Runs the default-parameter computation and saves results.
"""
import sys
import os
import csv
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.gf_adaptive_match import compute


def main():
    # Default parameters from GF_adaptive_match.m
    M = 1.0
    l = 0
    omega = 1e-3
    N = 128
    Cl = 1.0

    print(f"Running reproduction with omega={omega}, N={N}, l={l}, M={M}")
    result = compute(M=M, l=l, omega=omega, N=N, Cl=Cl)

    # Ensure output directories
    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)

    # Save as CSV
    csv_path = "results/single_case_result.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(result.keys())
        row = []
        for v in result.values():
            if isinstance(v, complex):
                row.append(f"{v.real:.15e}+{v.imag:.15e}j")
            else:
                row.append(str(v))
        writer.writerow(row)
    print(f"Saved CSV to {csv_path}")

    # Save as NPY (NumPy binary, equivalent to .mat)
    npy_path = "results/single_case_result.npy"
    # Convert complex values to separate real/imag for storage
    result_serializable = {}
    for k, v in result.items():
        if isinstance(v, complex):
            result_serializable[k] = {"real": v.real, "imag": v.imag}
        elif isinstance(v, np.integer):
            result_serializable[k] = int(v)
        elif isinstance(v, np.floating):
            result_serializable[k] = float(v)
        else:
            result_serializable[k] = v
    np.save(npy_path, result_serializable, allow_pickle=True)
    print(f"Saved NPY to {npy_path}")

    # Print key results
    print("\n=== Key Results ===")
    for key in ["omega", "zp", "C_id", "C_iu", "T", "R", "W", "A1out", "A1in", "T1", "R1",
                "matching_error", "W_error", "status"]:
        val = result[key]
        if isinstance(val, complex):
            print(f"  {key}: {val.real:.10e} + {val.imag:.10e}j")
        elif isinstance(val, float):
            print(f"  {key}: {val:.10e}")
        else:
            print(f"  {key}: {val}")

    # Sanity checks
    assert result["T"] >= 0 and result["R"] >= 0, "T, R must be non-negative"
    assert np.isfinite(result["C_id"]), "C_id must be finite"
    assert result["matching_error"] < 1e-6, f"Matching error {result['matching_error']} exceeds 1e-6"
    print("\nAll sanity checks passed.")


if __name__ == "__main__":
    main()
