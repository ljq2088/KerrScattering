"""Plot spectral-coefficient, residual, and nonlinear flux convergence diagnostics."""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COEFF = os.path.join(ROOT, "results", "kerr_scalar_spectral_coefficients.csv")
RESIDUAL = os.path.join(ROOT, "results", "kerr_scalar_spectral_residuals.csv")
FLUX = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_flux_convergence.csv")
QUALITY_FIG = os.path.join(ROOT, "figures", "kerr_scalar_spectral_quality.png")
FLUX_FIG = os.path.join(ROOT, "figures", "kerr_scalar_nonlinear_flux_convergence.png")


STYLE = {
    ("down", "outer"): {"label": r"$u_{\rm down}$ outer", "color": "#1f77b4"},
    ("up", "outer"): {"label": r"$u_{\rm up}$ outer", "color": "#ff7f0e"},
    ("in", "inner"): {"label": r"$u_{\rm in}$ inner", "color": "#2ca02c"},
}


def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def short_label(label):
    return (
        label.replace("kerr_", "")
        .replace("schwarzschild_", "schw_")
        .replace("_l2m2_", "_")
    )


def plot_quality():
    coeff_rows = read_rows(COEFF)
    residual_rows = read_rows(RESIDUAL)

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.8))

    ax = axes[0]
    for key, style in STYLE.items():
        branch, subdomain = key
        rows = [
            row for row in coeff_rows
            if row["branch"] == branch and row["subdomain"] == subdomain
        ]
        k = np.array([int(row["k"]) for row in rows])
        y = np.array([float(row["normalized_abs_coeff"]) for row in rows])
        ax.semilogy(k, np.maximum(y, 1e-18), lw=1.2, color=style["color"],
                    label=style["label"])
    ax.axhline(1e-12, color="0.55", ls="--", lw=0.8)
    ax.set_xlabel("Chebyshev index")
    ax.set_ylabel("normalized coefficient")
    ax.set_title("spectral coefficient decay")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    for key, style in STYLE.items():
        branch, subdomain = key
        rows = [
            row for row in residual_rows
            if row["branch"] == branch and row["subdomain"] == subdomain
        ]
        z = np.array([float(row["z"]) for row in rows])
        rel = np.array([float(row["relative_residual"]) for row in rows])
        order = np.argsort(z)
        ax.semilogy(z[order], np.maximum(rel[order], 1e-18), lw=1.1,
                    color=style["color"], label=style["label"])
    ax.set_xlabel(r"compact coordinate $z=r_+/r$")
    ax.set_ylabel("relative ODE residual")
    ax.set_title("collocation equation residual")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    fig.tight_layout()
    os.makedirs(os.path.dirname(QUALITY_FIG), exist_ok=True)
    fig.savefig(QUALITY_FIG, dpi=220)
    print(QUALITY_FIG)


def plot_flux_convergence():
    rows = read_rows(FLUX)
    labels = list(dict.fromkeys(row["label"] for row in rows))
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.8))

    ax = axes[0]
    for label in labels:
        case_rows = [row for row in rows if row["label"] == label]
        case_rows.sort(key=lambda row: int(row["N"]))
        N = np.array([int(row["N"]) for row in case_rows])
        rel = np.array([
            max(float(row["rel_T1_to_reference"]), float(row["rel_R1_to_reference"]))
            for row in case_rows
        ])
        ax.semilogy(N, np.maximum(rel, 1e-16), marker="o", lw=1.2,
                    label=short_label(label))
    ax.set_xlabel("Chebyshev order N")
    ax.set_ylabel(r"relative change to largest $N$")
    ax.set_title(r"convergence of $T^{(1)},R^{(1)}$")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    for label in labels:
        case_rows = [row for row in rows if row["label"] == label]
        case_rows.sort(key=lambda row: int(row["N"]))
        N = np.array([int(row["N"]) for row in case_rows])
        balance = np.array([abs(float(row["nonlinear_balance"])) for row in case_rows])
        ax.semilogy(N, np.maximum(balance, 1e-18), marker="o", lw=1.2,
                    label=short_label(label))
    ax.set_xlabel("Chebyshev order N")
    ax.set_ylabel(r"$|T^{(1)}+R^{(1)}|$")
    ax.set_title("nonlinear flux balance residual")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    fig.tight_layout()
    os.makedirs(os.path.dirname(FLUX_FIG), exist_ok=True)
    fig.savefig(FLUX_FIG, dpi=220)
    print(FLUX_FIG)


def main():
    plot_quality()
    plot_flux_convergence()


if __name__ == "__main__":
    main()
