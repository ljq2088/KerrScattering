"""Plot Kerr s=0 nonlinear target-channel and flux-coefficient results."""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNELS = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_channels.csv")
FLUX = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_flux_coefficients.csv")
OUT = os.path.join(ROOT, "figures", "kerr_scalar_nonlinear_results.png")


def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    channel_rows = read_rows(CHANNELS)
    flux_rows = read_rows(FLUX)
    active = [row for row in channel_rows if row["status"] == "ok"]

    l_targets = np.array([int(row["l_target"]) for row in active])
    aref = np.array([float(row["abs_A_ref_1"]) for row in active])
    ahor = np.array([float(row["abs_A_hor_1"]) for row in active])

    labels = [row["label"].replace("kerr_", "").replace("schwarzschild_", "schw_")
              for row in flux_rows]
    T1 = np.array([float(row["T1"]) for row in flux_rows])
    R1 = np.array([float(row["R1"]) for row in flux_rows])

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.8))

    ax = axes[0]
    width = 0.35
    x = np.arange(len(l_targets))
    ax.bar(x - width / 2, aref, width, label=r"$|A_{\rm ref}^{(1)}|$")
    ax.bar(x + width / 2, ahor, width, label=r"$|A_H^{(1)}|$")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([rf"${ell}$" for ell in l_targets])
    ax.set_xlabel(r"target channel $\ell'$")
    ax.set_ylabel("unit-horizon Green amplitude")
    ax.set_title(r"$a=0.5,\ \ell=m=2,\ M\omega=0.30$")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, which="both", axis="y", alpha=0.25)

    ax = axes[1]
    x = np.arange(len(labels))
    ax.bar(x - width / 2, T1, width, label=r"$T^{(1)}$")
    ax.bar(x + width / 2, R1, width, label=r"$R^{(1)}$")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_yscale("symlog", linthresh=1e-7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("fixed-incident flux coefficient")
    ax.set_title("self-channel nonlinear balance")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=220)
    print(OUT)


if __name__ == "__main__":
    main()
