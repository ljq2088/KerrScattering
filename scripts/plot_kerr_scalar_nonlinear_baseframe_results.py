"""Publication-style main result figure for the Kerr nonlinear article."""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLUX = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_flux_coefficients.csv")
CHANNELS = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_channels.csv")
CONV = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_flux_convergence.csv")
OUT = os.path.join(ROOT, "figures", "kerr_scalar_nonlinear_baseframe_results.png")


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def short_label(label):
    return (
        label.replace("schwarzschild_l0", "Schw l=0")
        .replace("kerr_a05_l2m2_sub", "a=0.5, 0.24")
        .replace("kerr_a05_l2m2_super", "a=0.5, 0.30")
        .replace("kerr_a09_l2m2_peak", "a=0.9, 0.58")
    )


def main():
    flux = rows(FLUX)
    channels = [r for r in rows(CHANNELS) if r["status"] == "ok"]
    conv = rows(CONV)

    x = np.arange(len(flux))
    labels = [short_label(r["label"]) for r in flux]
    T0 = np.array([float(r["T0"]) for r in flux])
    R0 = np.array([float(r["R0"]) for r in flux])
    T1 = np.array([float(r["T1"]) for r in flux])
    R1 = np.array([float(r["R1"]) for r in flux])
    bal1 = np.abs(T1 + R1)

    ellp = np.array([int(r["l_target"]) for r in channels])
    aref = np.array([float(r["abs_A_ref_1"]) for r in channels])
    ahor = np.array([float(r["abs_A_hor_1"]) for r in channels])

    conv_last = {}
    for row in conv:
        conv_last.setdefault(row["label"], []).append(row)
    conv_labels = []
    conv_N = []
    conv_bal = []
    for label, rs in conv_last.items():
        last = sorted(rs, key=lambda r: int(r["N"]))[-1]
        conv_labels.append(short_label(label))
        conv_N.append(int(last["N"]))
        conv_bal.append(abs(float(last["nonlinear_balance"])))

    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.2))

    ax = axes[0, 0]
    width = 0.36
    ax.bar(x - width / 2, T1, width, label=r"$T^{(1)}$")
    ax.bar(x + width / 2, R1, width, label=r"$R^{(1)}$")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_yscale("symlog", linthresh=1e-8)
    ax.set_ylim(-2e-1, 2e-1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("first-order flux coefficient")
    ax.set_title("(a) nonlinear flux coefficients")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, axis="y", alpha=0.25)

    ax = axes[0, 1]
    ax.semilogy(x, bal1, "o-", color="tab:red", label=r"$|T^{(1)}+R^{(1)}|$")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("balance residual")
    ax.set_title("(b) first-order flux balance")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 0]
    w = 0.35
    xx = np.arange(len(ellp))
    ax.bar(xx - w / 2, aref, w, label=r"$|A_{\rm ref}^{(1)}|$")
    ax.bar(xx + w / 2, ahor, w, label=r"$|A_H^{(1)}|$")
    ax.set_yscale("log")
    ax.set_xticks(xx)
    ax.set_xticklabels([rf"${ell}$" for ell in ellp])
    ax.set_xlabel(r"target channel $\ell'$")
    ax.set_ylabel("unit-horizon Green amplitude")
    ax.set_title(r"(c) target-channel matrix, $a=0.5,\ M\omega=0.30$")
    ax.grid(True, which="both", axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    ax.semilogy(np.arange(len(conv_labels)), conv_bal, "s-", color="tab:green")
    ax.set_ylim(min(conv_bal) / 3.0, max(conv_bal) * 3.0)
    ax.set_xticks(np.arange(len(conv_labels)))
    ax.set_xticklabels(conv_labels, rotation=20, ha="right")
    ax.set_ylabel(r"$|T^{(1)}+R^{(1)}|$ at largest $N$")
    ax.set_title("(d) convergence check")
    for i, n in enumerate(conv_N):
        ax.annotate(f"N={n}", (i, conv_bal[i]), textcoords="offset points", xytext=(0, 6),
                    ha="center", fontsize=8, clip_on=False)
    ax.grid(True, which="both", alpha=0.25)

    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, dpi=220)
    print(OUT)


if __name__ == "__main__":
    main()
