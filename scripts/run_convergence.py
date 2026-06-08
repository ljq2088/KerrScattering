"""N-convergence test.

Runs N = 32, 48, 64, 80 at omega = 0.1 and compares results.
Uses N=80 as reference.
"""
import sys
import os
import csv
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.gf_adaptive_match import compute

warnings.filterwarnings("ignore")


def main():
    N_vals = [32, 48, 64, 80]
    omega = 0.1
    M = 1.0
    l = 0
    Cl = 1.0

    os.makedirs("results", exist_ok=True)
    os.makedirs("figures", exist_ok=True)

    results = {}
    for N in N_vals:
        print(f"\n--- N = {N} ---")
        try:
            result = compute(M=M, l=l, omega=omega, N=N, Cl=Cl)
            results[N] = result
            print(f"  T={result['T']:.8e}, R={result['R']:.8e}, T1={result['T1']:.6e}, R1={result['R1']:.6e}")
        except Exception as e:
            print(f"  FAILED: {e}")
            results[N] = None

    # Save CSV
    csv_path = "results/convergence_N.csv"
    fields = ["N", "T", "R", "T1", "R1", "matching_error", "W_error"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for N in N_vals:
            if results[N] is not None:
                r = results[N]
                writer.writerow({k: r[k] for k in fields})
    print(f"\nSaved convergence data to {csv_path}")

    # Reference (N=80) comparison
    if results[80] is not None:
        ref = results[80]
        print("\n=== Convergence relative to N=80 ===")
        for N in [32, 48, 64]:
            if results[N] is None:
                continue
            r = results[N]
            dT = abs(r["T"] - ref["T"]) / abs(ref["T"])
            dR = abs(r["R"] - ref["R"]) / abs(ref["R"])
            dT1 = abs(r["T1"] - ref["T1"]) / max(abs(ref["T1"]), 1e-30)
            dR1 = abs(r["R1"] - ref["R1"]) / max(abs(ref["R1"]), 1e-30)
            print(f"  N={N}: dT/T={dT:.2e}, dR/R={dR:.2e}, dT1/T1={dT1:.2e}, dR1/R1={dR1:.2e}")

    # Plot convergence
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    N_list = [n for n in N_vals if results[n] is not None]
    T_vals = [results[n]["T"] for n in N_list]
    R_vals = [results[n]["R"] for n in N_list]
    T1_vals = [results[n]["T1"] for n in N_list]
    R1_vals = [results[n]["R1"] for n in N_list]

    axes[0, 0].semilogy(N_list, [abs(t - T_vals[-1]) / abs(T_vals[-1]) for t in T_vals], "o-")
    axes[0, 0].set_xlabel("N")
    axes[0, 0].set_ylabel("Relative error in T")
    axes[0, 0].set_title("T convergence")
    axes[0, 0].grid(True)

    axes[0, 1].semilogy(N_list, [abs(r - R_vals[-1]) / abs(R_vals[-1]) for r in R_vals], "o-")
    axes[0, 1].set_xlabel("N")
    axes[0, 1].set_ylabel("Relative error in R")
    axes[0, 1].set_title("R convergence")
    axes[0, 1].grid(True)

    axes[1, 0].semilogy(N_list, [abs(t - T1_vals[-1]) / max(abs(T1_vals[-1]), 1e-30) for t in T1_vals], "o-")
    axes[1, 0].set_xlabel("N")
    axes[1, 0].set_ylabel("Relative error in T1")
    axes[1, 0].set_title("T1 convergence")
    axes[1, 0].grid(True)

    axes[1, 1].semilogy(N_list, [abs(r - R1_vals[-1]) / max(abs(R1_vals[-1]), 1e-30) for r in R1_vals], "o-")
    axes[1, 1].set_xlabel("N")
    axes[1, 1].set_ylabel("Relative error in R1")
    axes[1, 1].set_title("R1 convergence")
    axes[1, 1].grid(True)

    plt.tight_layout()
    fig_path = "figures/convergence_N.png"
    plt.savefig(fig_path, dpi=150)
    print(f"\nSaved convergence plot to {fig_path}")


if __name__ == "__main__":
    main()
