"""Plot axisymmetric accuracy diagnostics for the Kerr s=0 nonlinear paper."""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COEFF = os.path.join(ROOT, "results", "kerr_scalar_axisymmetric_spectral_coefficients.csv")
RESIDUAL = os.path.join(ROOT, "results", "kerr_scalar_axisymmetric_spectral_residuals.csv")
AXISYM_INPUTS = {
    0: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv",
        "results/tmp_kerr_axisymmetric_refine_l0.csv",
    ],
    1: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv",
        "results/tmp_kerr_axisymmetric_refine_l1.csv",
    ],
    2: [
        "results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv",
        "results/tmp_kerr_axisymmetric_refine_l2.csv",
    ],
}
OUT_FIG = os.path.join(ROOT, "figures", "kerr_scalar_axisymmetric_accuracy.png")


STYLE = {
    ("down", "outer"): {"label": r"$u_{\rm down}$ outer", "color": "#0072bd"},
    ("up", "outer"): {"label": r"$u_{\rm up}$ outer", "color": "#d95319"},
    ("in", "inner"): {"label": r"$u_{\rm in}$ inner", "color": "#77ac30"},
}


def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def best_axisym_rows(paths):
    best = {}
    for rel in paths:
        with open(os.path.join(ROOT, rel), newline="") as f:
            for row in csv.DictReader(f):
                omega = round(float(row["omega"]), 14)
                score = abs(float(row["nonlinear_balance"]))
                old = best.get(omega)
                if old is None or score < abs(float(old["nonlinear_balance"])):
                    best[omega] = row
    return [best[key] for key in sorted(best)]


def main():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 9,
            "mathtext.fontset": "dejavuserif",
            "axes.linewidth": 0.8,
        }
    )

    coeff_rows = read_rows(COEFF)
    residual_rows = read_rows(RESIDUAL)

    fig, axes = plt.subplots(1, 3, figsize=(8.6, 2.7), constrained_layout=True)

    ax = axes[0]
    for key, style in STYLE.items():
        branch, subdomain = key
        rows = [r for r in coeff_rows if r["branch"] == branch and r["subdomain"] == subdomain]
        k = np.array([int(r["k"]) for r in rows])
        y = np.array([float(r["normalized_abs_coeff"]) for r in rows])
        ax.semilogy(k, np.maximum(y, 1e-18), lw=1.1, color=style["color"], label=style["label"])
    ax.axhline(1e-12, color="0.55", ls="--", lw=0.8)
    ax.set_xlabel("Chebyshev index")
    ax.set_ylabel("normalized coefficient")
    ax.text(0.04, 0.08, "(a)", transform=ax.transAxes)
    ax.tick_params(direction="in", top=True, right=True)
    ax.legend(frameon=False, fontsize=7, loc="upper right")

    ax = axes[1]
    for key, style in STYLE.items():
        branch, subdomain = key
        rows = [
            r for r in residual_rows
            if r["branch"] == branch and r["subdomain"] == subdomain
            and r["radial_relative_residual"]
        ]
        node = np.array([int(r["node_index"]) for r in rows])
        rel = np.array([float(r["radial_relative_residual"]) for r in rows])
        x = node / max(float(node.max()), 1.0)
        order = np.argsort(x)
        ax.semilogy(x[order], np.maximum(np.abs(rel[order]), 1e-18),
                    lw=1.1, color=style["color"], label=style["label"])
    ax.set_xlabel("collocation fraction")
    ax.set_ylabel(r"relative $R$-equation residual")
    ax.text(0.04, 0.08, "(b)", transform=ax.transAxes)
    ax.tick_params(direction="in", top=True, right=True)

    ax = axes[2]
    colors = {0: "#0072bd", 1: "#d95319", 2: "#edb120"}
    for ell, paths in AXISYM_INPUTS.items():
        rows = best_axisym_rows(paths)
        omega = np.array([float(r["omega"]) for r in rows])
        balance = np.array([abs(float(r["nonlinear_balance"])) for r in rows])
        ax.semilogy(omega, np.maximum(balance, 1e-18), "o-", ms=3, lw=1.1,
                    color=colors[ell], label=rf"$\ell={ell}$")
    ax.axhline(1e-8, color="0.55", ls="--", lw=0.8)
    ax.set_xlabel(r"$M\omega$")
    ax.set_ylabel(r"$|T^{(1)}+R^{(1)}|$")
    ax.text(0.04, 0.08, "(c)", transform=ax.transAxes)
    ax.tick_params(direction="in", top=True, right=True)
    ax.legend(frameon=False, fontsize=7, loc="best")

    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    fig.savefig(OUT_FIG, dpi=240)
    plt.close(fig)
    print(OUT_FIG)


if __name__ == "__main__":
    main()
