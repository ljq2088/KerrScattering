"""Plot scalar-monopole response for higher odd-power interactions."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIXED = RESULTS / "kerr_scalar_power_nonlinearity_l0_fixed_N176.csv"
KAPPA = RESULTS / "kerr_scalar_power_nonlinearity_l0_kappa_N176.csv"
OUTPUT = ROOT / "figures" / "kerr_scalar_power_nonlinearity_l0.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"No rows in {path}")
    return rows


def select(rows, *, n=None, a=None, coordinate=None):
    output = []
    for row in rows:
        if n is not None and int(row["nonlinearity_order"]) != n:
            continue
        if a is not None and not np.isclose(float(row["a"]), a):
            continue
        if coordinate is not None and not np.isclose(
            float(row["frequency_coordinate"]), coordinate
        ):
            continue
        output.append(row)
    return output


def main() -> None:
    fixed = read_csv(FIXED)
    kappa = read_csv(KAPPA)
    colors = {2: "#0072b2", 3: "#d55e00"}
    markers = {2: "o", 3: "s"}

    plt.rcParams.update({
        "font.size": 8,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
    })
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.55))
    fig.subplots_adjust(left=0.075, right=0.99, bottom=0.19, top=0.86, wspace=0.34)

    for n in (2, 3):
        rows = sorted(select(fixed, n=n, a=0.5), key=lambda row: float(row["omega"]))
        omega = np.array([float(row["omega"]) for row in rows])
        response = np.array([float(row["horizon_response"]) for row in rows])
        coefficient = float(rows[0]["analytic_low_frequency_coefficient"])
        power = 2 * n - 2
        axes[0].plot(
            omega, response, marker=markers[n], color=colors[n], lw=1.0, ms=3.2,
            label=rf"$n={n}$",
        )
        axes[0].plot(
            omega, coefficient * omega**power, color=colors[n], ls=":", lw=1.0,
        )
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel(r"$M\omega$")
    axes[0].set_ylabel(r"$M^{2n-2}\chi_{H,00}^{(n)}$")
    axes[0].set_title(r"Low-frequency hierarchy, $a/M=0.5$")
    axes[0].legend(frameon=False, fontsize=7)

    spin_colors = {
        0.0: "#000000",
        0.5: "#0072b2",
        0.9: "#009e73",
        0.99: "#e69f00",
        0.999: "#cc79a7",
    }
    for n, linestyle in ((2, "-"), (3, "--")):
        for a in (0.0, 0.5, 0.9, 0.99, 0.999):
            rows = sorted(select(fixed, n=n, a=a), key=lambda row: float(row["omega"]))
            omega = [float(row["omega"]) for row in rows]
            ratio = [
                float(row["response_over_frequency_power"])
                / float(row["analytic_low_frequency_coefficient"])
                for row in rows
            ]
            axes[1].plot(
                omega, ratio, color=spin_colors[a], ls=linestyle, lw=0.9,
                marker=markers[n], ms=2.3, markevery=[0, len(rows) - 1],
            )
    axes[1].axhline(1.0, color="0.35", ls=":", lw=0.8)
    axes[1].set_xscale("log")
    axes[1].set_xlabel(r"$M\omega$")
    axes[1].set_ylabel(r"$\chi_{H,00}^{(n)}/(c_n\omega^{2n-2})$")
    axes[1].set_title("Spin-independent infrared limit")
    axes[1].text(0.00056, 1.029, r"$n=2$ solid", color=colors[2], fontsize=6.8)
    axes[1].text(0.00056, 1.018, r"$n=3$ dashed", color=colors[3], fontsize=6.8)

    y = 0.025
    for n in (2, 3):
        rows = sorted(
            select(kappa, n=n, coordinate=y),
            key=lambda row: float(row["surface_gravity"]),
        )
        surface_gravity = np.array([float(row["surface_gravity"]) for row in rows])
        response = np.array([float(row["horizon_response"]) for row in rows])
        coefficient = float(rows[0]["analytic_low_frequency_coefficient"])
        power = 2 * n - 2
        axes[2].plot(
            surface_gravity, response, marker=markers[n], color=colors[n],
            lw=1.0, ms=3.2, label=rf"$n={n}$",
        )
        axes[2].plot(
            surface_gravity, coefficient * (y * surface_gravity) ** power,
            color=colors[n], ls=":", lw=1.0,
        )
    axes[2].set_xscale("log")
    axes[2].set_yscale("log")
    axes[2].set_xticks([0.02, 0.04, 0.08])
    axes[2].set_xticklabels(["0.02", "0.04", "0.08"])
    axes[2].xaxis.set_minor_formatter(NullFormatter())
    axes[2].set_xlabel(r"$M\kappa$")
    axes[2].set_ylabel(r"$M^{2n-2}\chi_{H,00}^{(n)}$")
    axes[2].set_title(r"Fixed $\omega/\kappa=0.025$")
    axes[2].legend(frameon=False, fontsize=7)

    for label, ax in zip(("(a)", "(b)", "(c)"), axes):
        ax.text(0.02, 0.97, label, transform=ax.transAxes, ha="left", va="top")
        ax.tick_params(direction="in", which="both", top=True, right=True)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=300)
    plt.close(fig)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
