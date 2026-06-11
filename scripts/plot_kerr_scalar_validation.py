"""Create validation plots for the Kerr s=0 spectral solver."""

import csv
import os
import sys

import matplotlib.pyplot as plt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY = os.path.join(ROOT, "results", "kerr_scalar_adaptive_summary.csv")
CONVERGENCE = os.path.join(ROOT, "results", "kerr_scalar_spectral_convergence.csv")
FIGDIR = os.path.join(ROOT, "figures")


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def case_label(row):
    return f"l={row['l']},m={row['m']},a={float(row['a']):.1g},w={float(row['omega']):.2g}"


def plot_floor(values, floor=1e-16):
    return [max(float(value), floor) for value in values]


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    summary = read_csv(SUMMARY)

    labels = [case_label(row) for row in summary]
    inc_err = plot_floor(row["rel_abs_B_inc"] for row in summary)
    ref_err = plot_floor(row["rel_abs_B_ref"] for row in summary)
    flux = plot_floor(row["flux_balance_error"] for row in summary)
    x = list(range(len(summary)))

    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.semilogy(x, inc_err, "o-", label=r"$|B_{\rm inc}|$")
    ax.semilogy(x, ref_err, "s-", label=r"$|B_{\rm ref}|$")
    ax.semilogy(x, flux, "^-", label="flux balance")
    ax.axhline(1e-7, color="0.35", ls="--", lw=1, label=r"$10^{-7}$ amplitude gate")
    ax.axhline(1e-8, color="0.6", ls=":", lw=1, label=r"$10^{-8}$ flux gate")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("relative / residual error")
    ax.set_title("Kerr scalar spectral solver vs GSN benchmarks")
    ax.grid(True, which="both", ls=":", lw=0.5)
    ax.legend(ncol=2)
    fig.tight_layout()
    error_out = os.path.join(FIGDIR, "kerr_scalar_adaptive_errors.png")
    fig.savefig(error_out, dpi=180)
    plt.close(fig)

    if os.path.exists(CONVERGENCE):
        conv = read_csv(CONVERGENCE)
        labels_seen = []
        fig, ax = plt.subplots(figsize=(8.5, 5.2))
        for label in sorted({row["label"] for row in conv}):
            rows = [row for row in conv if row["label"] == label]
            rows.sort(key=lambda row: int(row["N"]))
            ax.semilogy(
                [int(row["N"]) for row in rows],
                plot_floor(row["flux_balance_error"] for row in rows),
                "o-",
                label=label,
            )
            labels_seen.append(label)
        ax.set_xlabel("Chebyshev order N")
        ax.set_ylabel("flux-balance residual")
        ax.set_title("Representative spectral convergence")
        ax.grid(True, which="both", ls=":", lw=0.5)
        ax.legend()
        fig.tight_layout()
        convergence_out = os.path.join(FIGDIR, "kerr_scalar_convergence.png")
        fig.savefig(convergence_out, dpi=180)
        plt.close(fig)
        print(convergence_out)

    print(error_out)


if __name__ == "__main__":
    main()
