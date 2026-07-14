"""Plot the Kerr scalar nonlinear frequency sweep."""

import csv
import math
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INFILE = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_frequency_sweep_best.csv")
OUTFILE = os.path.join(ROOT, "figures", "kerr_scalar_nonlinear_frequency_sweep.png")


def read_rows():
    with open(INFILE, newline="") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda row: float(row["omega"]))
    return rows


def arr(rows, key):
    return np.array([float(row[key]) for row in rows], dtype=float)


def main():
    rows = read_rows()
    omega = arr(rows, "omega")
    t0 = arr(rows, "T0")
    r0 = arr(rows, "R0")
    t1 = arr(rows, "T1")
    r1 = arr(rows, "R1")
    residual = np.abs(arr(rows, "nonlinear_balance"))
    accepted = np.array([row["accepted_balance"].lower() == "true" for row in rows])

    a = float(rows[0]["a"])
    m = int(float(rows[0]["m"]))
    omega_h = float(rows[0]["omega_h"])
    threshold = m * omega_h

    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "font.size": 10,
            "mathtext.fontset": "dejavuserif",
            "axes.linewidth": 0.8,
        }
    )

    fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.2), constrained_layout=True)
    ax_t1, ax_abs, ax_r1, ax_res = axes.ravel()

    for ax in axes.ravel():
        ax.axvline(threshold, color="0.35", lw=0.9, ls="--", zorder=0)
        ax.grid(True, which="major", color="0.88", lw=0.7)
        ax.grid(True, which="minor", color="0.94", lw=0.5)
        ax.set_xlabel(r"$M\omega$")

    ax_t1.plot(omega, t1, color="#1f5a85", lw=1.3)
    ax_t1.scatter(omega, t1, s=28, color="#1f5a85", zorder=3)
    ax_t1.axhline(0.0, color="0.3", lw=0.8)
    ax_t1.set_yscale("symlog", linthresh=1.0e-7)
    ax_t1.set_ylabel(r"$T^{(1)}$")
    ax_t1.set_title(r"(a) nonlinear transmission")

    ax_abs.plot(omega, np.abs(t1), color="#8b2f2f", lw=1.3)
    ax_abs.scatter(omega, np.abs(t1), s=28, color="#8b2f2f", zorder=3)
    ax_abs.set_yscale("log")
    ax_abs.set_ylabel(r"$|T^{(1)}|$")
    ax_abs.set_title(r"(b) magnitude of correction")

    ax_r1.plot(omega, r1, color="0.72", lw=1.0, zorder=1)
    ax_r1.scatter(
        omega[accepted],
        r1[accepted],
        s=32,
        color="#2f6f4f",
        label=r"accepted",
        zorder=3,
    )
    ax_r1.scatter(
        omega[~accepted],
        r1[~accepted],
        s=36,
        facecolors="white",
        edgecolors="#9a3d2f",
        linewidths=1.2,
        label=r"balance limited",
        zorder=3,
    )
    ax_r1.axhline(0.0, color="0.3", lw=0.8)
    ax_r1.set_yscale("symlog", linthresh=1.0e-7)
    ax_r1.set_ylabel(r"$R^{(1)}$")
    ax_r1.set_title(r"(c) nonlinear reflection")
    ax_r1.legend(frameon=False, loc="best", fontsize=8)

    ax_res.scatter(
        omega[accepted],
        residual[accepted],
        s=32,
        color="#2f6f4f",
        label=r"accepted",
        zorder=3,
    )
    ax_res.scatter(
        omega[~accepted],
        residual[~accepted],
        s=36,
        facecolors="white",
        edgecolors="#9a3d2f",
        linewidths=1.2,
        label=r"balance limited",
        zorder=3,
    )
    ax_res.axhline(1.0e-8, color="#7a4b00", lw=1.0, ls=":", label=r"$10^{-8}$")
    ax_res.set_yscale("log")
    ax_res.set_ylabel(r"$|T^{(1)}+R^{(1)}|$")
    ax_res.set_title(r"(d) first-order flux balance")
    ax_res.legend(frameon=False, loc="best", fontsize=8)

    ymin = max(np.nanmin(np.abs(t1[np.abs(t1) > 0])) / 3.0, 1.0e-9)
    ymax = np.nanmax(np.abs(t1)) * 3.0
    ax_abs.set_ylim(ymin, ymax)
    ax_res.set_ylim(max(np.nanmin(residual) / 3.0, 1.0e-14), np.nanmax(residual) * 3.0)

    os.makedirs(os.path.dirname(OUTFILE), exist_ok=True)
    fig.savefig(OUTFILE, dpi=220)
    plt.close(fig)
    print(OUTFILE)
    print(f"threshold={threshold:.12g}")
    print(f"accepted={int(accepted.sum())}/{len(accepted)}")
    print(f"T1 range=({t1.min():.6e}, {t1.max():.6e})")


if __name__ == "__main__":
    main()
