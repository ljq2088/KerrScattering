"""Plot low-frequency Kerr scalar scattering diagnostics."""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FIG = os.path.join(ROOT, "figures", "kerr_scalar_low_frequency_axisymmetric.png")
OUT_TABLE = os.path.join(ROOT, "results", "kerr_scalar_low_frequency_axisymmetric_slopes.csv")
INPUTS = {
    0: ["results/kerr_scalar_nonlinear_axisymmetric_hires_l0.csv"],
    1: ["results/kerr_scalar_nonlinear_axisymmetric_hires_l1.csv"],
    2: ["results/kerr_scalar_nonlinear_axisymmetric_hires_l2.csv"],
}


def read_rows(paths):
    rows = []
    for rel in paths:
        with open(os.path.join(ROOT, rel), newline="") as f:
            rows.extend(csv.DictReader(f))
    rows.sort(key=lambda row: float(row["omega"]))
    omega = np.array([float(row["omega"]) for row in rows])
    t0 = np.array([float(row["T0"]) for row in rows])
    t1 = np.array([float(row["T1"]) for row in rows])
    return omega, t0, t1


def low_fit(omega, values, npts=4):
    x = omega[:npts]
    y = np.abs(values[:npts])
    mask = y > 0.0
    coeff = np.polyfit(np.log(x[mask]), np.log(y[mask]), 1)
    slope = float(coeff[0])
    amp = float(np.exp(coeff[1]))
    return slope, amp


def main():
    data = {ell: read_rows(paths) for ell, paths in INPUTS.items()}
    slopes = []
    for ell, (omega, t0, t1) in data.items():
        s0, a0 = low_fit(omega, t0, npts=4)
        s1, a1 = low_fit(omega, t1, npts=4)
        slopes.append({"l": ell, "T0_slope": s0, "T1_slope": s1, "T0_amp": a0, "T1_amp": a1})

    os.makedirs(os.path.dirname(OUT_TABLE), exist_ok=True)
    with open(OUT_TABLE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["l", "T0_slope", "T1_slope", "T0_amp", "T1_amp"])
        writer.writeheader()
        for row in slopes:
            writer.writerow({k: (f"{v:.12e}" if isinstance(v, float) else v) for k, v in row.items()})

    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 10,
            "mathtext.fontset": "dejavuserif",
            "axes.linewidth": 0.8,
        }
    )
    colors = {0: "#0072bd", 1: "#d95319", 2: "#edb120"}
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.25), constrained_layout=True)
    for ax in axes:
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(r"$M\omega$")
        ax.tick_params(direction="in", top=True, right=True)
    axes[0].set_ylabel(r"$T_\ell^{(0)}$")
    axes[1].set_ylabel(r"$T_\ell^{(1)}$")

    for ell, (omega, t0, t1) in data.items():
        take = omega <= {0: 0.14, 1: 0.22, 2: 0.35}[ell]
        axes[0].plot(omega[take], t0[take], "o-", color=colors[ell], ms=3, lw=1.2, label=rf"$\ell={ell}$")
        axes[1].plot(omega[take], t1[take], "o-", color=colors[ell], ms=3, lw=1.2, label=rf"$\ell={ell}$")

    axes[0].legend(frameon=True, fontsize=9, loc="best")
    axes[1].legend(frameon=True, fontsize=9, loc="best")

    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    fig.savefig(OUT_FIG, dpi=240)
    plt.close(fig)

    print(OUT_FIG)
    print(OUT_TABLE)
    for row in slopes:
        print(f"l={row['l']} T0~w^{row['T0_slope']:.3f} T1~w^{row['T1_slope']:.3f}")


if __name__ == "__main__":
    main()
