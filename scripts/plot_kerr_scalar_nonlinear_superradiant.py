"""Plot the bounded non-axisymmetric scalar superradiance check."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "kerr_scalar_nonlinear_m2_superradiant.csv"
OUTPUT = ROOT / "figures" / "kerr_scalar_nonlinear_superradiant_m2.png"


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = read_rows()
    omega = [float(row["omega"]) for row in rows]
    t0 = [float(row["T0"]) for row in rows]
    t1 = [float(row["T1"]) for row in rows]
    residual = [float(row["abs_nonlinear_balance"]) for row in rows]
    accepted = [value <= 1.0e-8 for value in residual]
    threshold = float(rows[0]["m_omega_h"])

    plt.rcParams.update({"font.size": 9, "axes.labelsize": 10})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharex=True)
    for ax, values, label, color in zip(
        axes,
        (t0, t1),
        (r"$T^{(0)}$", r"$T^{(1)}$"),
        ("#1f77b4", "#d95f02"),
    ):
        for is_ok, marker, alpha in ((True, "o", 1.0), (False, "x", 0.75)):
            indices = [i for i, flag in enumerate(accepted) if flag == is_ok]
            if indices:
                ax.plot(
                    [omega[i] for i in indices],
                    [values[i] for i in indices],
                    marker=marker,
                    linestyle="-" if is_ok else "none",
                    color=color,
                    alpha=alpha,
                    label=label if is_ok else "balance rejected",
                )
        ax.axvline(threshold, color="0.35", linestyle="--", linewidth=0.9)
        ax.axhline(0.0, color="0.5", linewidth=0.7)
        ax.set_yscale("symlog", linthresh=1.0e-7)
        ax.set_xlabel(r"$M\omega$")
        ax.set_ylabel(label)
        ax.grid(True, which="both", alpha=0.18)
    axes[0].text(
        threshold + 0.004,
        0.82,
        r"$m\Omega_H$",
        transform=axes[0].get_xaxis_transform(),
        rotation=90,
        va="bottom",
        ha="left",
        color="0.25",
    )
    axes[0].legend(frameon=False, loc="upper left")
    axes[1].legend(frameon=False, loc="upper left")
    fig.suptitle(r"Non-axisymmetric scalar Kerr flux check: $a=0.5,\;\ell=m=2$")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(f"saved = {OUTPUT}")


if __name__ == "__main__":
    main()
