"""Plot publication-style Kerr s=0 frequency-sweep curves."""

import csv
import os
import sys

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SWEEP = os.path.join(ROOT, "results", "kerr_scalar_frequency_sweep.csv")
FIGDIR = os.path.join(ROOT, "figures")


def read_rows():
    with open(SWEEP, newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in [
            "omega", "R", "T", "amplification", "m_omega_h",
            "score", "flux_balance_error",
        ]:
            row[key] = float(row[key])
    return rows


def label_for(label):
    return {
        "schwarzschild_l0": r"$a=0,\ell=m=0$",
        "kerr_a05_l2m2": r"$a=0.5,\ell=m=2$",
        "kerr_a09_l2m2": r"$a=0.9,\ell=m=2$",
    }.get(label, label)


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    rows = read_rows()
    labels = sorted({row["label"] for row in rows})

    fig, axes = plt.subplots(2, 1, figsize=(8.4, 7.0), sharex=True)
    for label in labels:
        subset = sorted([row for row in rows if row["label"] == label], key=lambda r: r["omega"])
        omega = [row["omega"] for row in subset]
        axes[0].plot(omega, [row["R"] for row in subset], "o-", label=label_for(label))
        axes[1].plot(omega, [row["T"] for row in subset], "o-", label=label_for(label))
        threshold = subset[0]["m_omega_h"]
        if threshold > 0:
            for ax in axes:
                ax.axvline(threshold, color="0.75", ls="--", lw=1)

    axes[0].axhline(1.0, color="0.35", ls=":", lw=1)
    axes[0].set_ylabel(r"$R=|B_{\rm ref}/B_{\rm inc}|^2$")
    axes[1].set_ylabel(r"$T$")
    axes[1].set_xlabel(r"$\omega M$")
    axes[0].set_title("Scalar Kerr scattering coefficients")
    for ax in axes:
        ax.grid(True, which="both", ls=":", lw=0.5)
        ax.legend()
    fig.tight_layout()
    out_rt = os.path.join(FIGDIR, "kerr_scalar_frequency_rt.png")
    fig.savefig(out_rt, dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for label in labels:
        subset = sorted(
            [
                row for row in rows
                if row["label"] != "schwarzschild_l0"
                and row["omega"] < row["m_omega_h"]
                and row["amplification"] > 0
            ],
            key=lambda r: (r["label"], r["omega"]),
        )
        subset = [row for row in subset if row["label"] == label]
        if not subset:
            continue
        ax.semilogy(
            [row["omega"] for row in subset],
            [row["amplification"] for row in subset],
            "o-",
            label=label_for(label),
        )
        ax.axvline(subset[0]["m_omega_h"], color="0.75", ls="--", lw=1)
    ax.set_xlabel(r"$\omega M$")
    ax.set_ylabel(r"$R-1$")
    ax.set_title("Scalar superradiant amplification")
    ax.grid(True, which="both", ls=":", lw=0.5)
    ax.legend()
    fig.tight_layout()
    out_amp = os.path.join(FIGDIR, "kerr_scalar_superradiance_amplification.png")
    fig.savefig(out_amp, dpi=180)
    plt.close(fig)

    print(out_rt)
    print(out_amp)


if __name__ == "__main__":
    main()
