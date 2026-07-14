"""Audit the Kerr-to-Schwarzschild limit of the scalar nonlinear response.

The experiment keeps (l, m, M omega) fixed and sweeps the spin parameter.
It is an internal continuity test, not an external benchmark comparison.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    current_rss_mb,
    fmt_complex,
    require_memory_room,
)
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "results", "kerr_scalar_spin_limit.csv")
DEFAULT_SPINS = "0,0.05,0.1,0.2,0.3,0.5"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default=DEFAULT_OUT)
    parser.add_argument("--a-values", default=DEFAULT_SPINS)
    parser.add_argument("--l", type=int, default=2)
    parser.add_argument("--m", type=int, default=0)
    parser.add_argument("--omega", type=float, default=0.52)
    parser.add_argument("--N", type=int, default=240)
    parser.add_argument("--quad-order", type=int, default=192)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--r-match", type=float, default=40.0)
    parser.add_argument("--max-rss-mb", type=float, default=2000.0)
    return parser.parse_args(argv)


def parse_spins(text):
    values = [float(item) for item in text.split(",") if item.strip()]
    if not values:
        raise ValueError("At least one spin value is required.")
    if any(abs(a) >= 1.0 for a in values):
        raise ValueError("Require |a| < 1 for every spin value.")
    return values


def row_from_result(result, args, rss_before, rss_after, elapsed_s):
    b_inc = result.B_inc
    b_ref = result.B_ref
    norm4 = abs(b_inc) ** 4
    horizon_factor = (
        result.p_horizon * (result.r_plus ** 2 + result.a ** 2) / result.omega
    )
    T0 = horizon_factor / abs(b_inc) ** 2
    R0 = abs(b_ref / b_inc) ** 2
    T1 = 2.0 * horizon_factor * result.A_hor_1.real / norm4
    R1 = 2.0 * (b_ref.conjugate() * result.A_ref_1).real / norm4
    return {
        "l": args.l,
        "m": args.m,
        "a": f"{result.a:.16e}",
        "omega": f"{result.omega:.16e}",
        "N": result.N_outer,
        "r_match": f"{result.r_match:.16e}",
        "quad_order": result.quad_order,
        "tail_epsrel": f"{result.tail_epsrel:.16e}",
        "radial_lambda": f"{result.radial_lambda:.16e}",
        "angular_coupling": fmt_complex(result.angular_coupling),
        "angular_coupling_cos2": fmt_complex(result.angular_coupling_cos2),
        "B_inc": fmt_complex(b_inc),
        "B_ref": fmt_complex(b_ref),
        "T0": f"{T0:.16e}",
        "R0": f"{R0:.16e}",
        "linear_balance": f"{T0 + R0 - 1.0:.16e}",
        "T1": f"{T1:.16e}",
        "R1": f"{R1:.16e}",
        "nonlinear_balance": f"{T1 + R1:.16e}",
        "abs_nonlinear_balance": f"{abs(T1 + R1):.16e}",
        "flux_normalization_condition_number": f"{result.flux_normalization_condition_number:.16e}",
        "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
        "elapsed_s": f"{elapsed_s:.6e}",
        "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
        "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
        "status": result.status,
    }


def main(argv=None):
    args = parse_args(argv)
    spins = parse_spins(args.a_values)
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    require_memory_room(args.max_rss_mb, "initial")

    rows = []
    for a in spins:
        rss_before = require_memory_room(args.max_rss_mb, f"before a={a:g}")
        start = time.perf_counter()
        print(
            f"Running a={a:g} l={args.l} m={args.m} omega={args.omega:g} "
            f"N={args.N} q={args.quad_order} RSS={rss_before:.1f} MB"
            if rss_before is not None
            else f"Running a={a:g} l={args.l} m={args.m} omega={args.omega:g}"
        )
        result = compute_kerr_scalar_green_diagnostics(
            args.l,
            args.m,
            args.omega,
            a=a,
            l_target=args.l,
            N_outer=args.N,
            N_inner=args.N,
            r_match=args.r_match,
            quad_order=args.quad_order,
            tail_epsrel=args.tail_epsrel,
            radial_weight_model="kerr-covariant-sigma-dr",
        )
        elapsed_s = time.perf_counter() - start
        rss_after = current_rss_mb()
        row = row_from_result(result, args, rss_before, rss_after, elapsed_s)
        rows.append(row)
        print(
            f"  T1={row['T1']} R1={row['R1']} "
            f"balance={row['abs_nonlinear_balance']} RSS_after="
            f"{rss_after:.1f} MB" if rss_after is not None else ""
        )
        require_memory_room(args.max_rss_mb, f"after a={a}")

    fields = [
        "l", "m", "a", "omega", "N", "r_match", "quad_order", "tail_epsrel",
        "radial_lambda", "angular_coupling", "angular_coupling_cos2", "B_inc",
        "B_ref", "T0", "R0", "linear_balance", "T1", "R1", "nonlinear_balance",
        "abs_nonlinear_balance", "flux_normalization_condition_number",
        "wronskian_relative_error", "elapsed_s", "rss_mb_before", "rss_mb_after",
        "status",
    ]
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved = {output}")


if __name__ == "__main__":
    main()
