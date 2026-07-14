"""Plot the internal Kerr-to-Schwarzschild spin-limit audit."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "results" / "kerr_scalar_spin_limit.csv"
DEFAULT_OUTPUT = ROOT / "figures" / "kerr_scalar_spin_limit.png"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def load(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("spin-limit CSV is empty")
    a = np.array([float(row["a"]) for row in rows])
    t1 = np.array([float(row["T1"]) for row in rows])
    r1 = np.array([float(row["R1"]) for row in rows])
    linear = np.array([abs(float(row["linear_balance"])) for row in rows])
    nonlinear = np.array([float(row["abs_nonlinear_balance"]) for row in rows])
    return a, t1, r1, linear, nonlinear


def main(argv=None):
    args = parse_args(argv)
    a, t1, r1, linear, nonlinear = load(args.input)
    order = np.argsort(a)
    a, t1, r1, linear, nonlinear = [x[order] for x in (a, t1, r1, linear, nonlinear)]
    t10 = t1[0]
    r10 = r1[0]

    plt.rcParams.update({"font.size": 10, "axes.linewidth": 0.8})
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.2, 3.5), constrained_layout=False)
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.78, wspace=0.20)

    ax0.plot(a, t1, "o-", lw=1.5, ms=4.5, label=r"$T^{(1)}$")
    ax0.plot(a, -r1, "s--", lw=1.3, ms=4.0, label=r"$-R^{(1)}$")
    ax0.set_xlabel(r"spin $a/M$")
    ax0.set_ylabel(r"first-order flux coefficient")
    ax0.set_title("Flux coefficients")
    ax0.grid(True, alpha=0.25)
    ax0.legend(frameon=False)

    ax1.plot(a, 100.0 * (t1 / t10 - 1.0), "o-", lw=1.5, ms=4.5,
             label=r"$T^{(1)}/T^{(1)}_{a=0}-1$")
    ax1.plot(a, 100.0 * (-r1 / (-r10) - 1.0), "s--", lw=1.3, ms=4.0,
             label=r"$[-R^{(1)}]/[-R^{(1)}_{a=0}]-1$")
    ax1.set_xlabel(r"spin $a/M$")
    ax1.set_ylabel("relative change (%)")
    ax1.set_title("Continuity from Schwarzschild")
    ax1.grid(True, alpha=0.25)
    ax1.legend(frameon=False, fontsize=8)

    fig.suptitle(r"Internal spin-limit audit: $(\ell,m,M\omega)=(2,0,0.52)$", y=0.96)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {args.output}")
    print(f"max linear balance residual = {linear.max():.3e}")
    print(f"max first-order balance residual = {nonlinear.max():.3e}")


if __name__ == "__main__":
    main()
