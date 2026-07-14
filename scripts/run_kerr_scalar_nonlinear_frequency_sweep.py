"""Run a Kerr s=0 self-channel nonlinear frequency sweep.

This supplies the Kerr analogue of the frequency-dependent nonlinear
scattering-coefficient plot in the Schwarzschild nonlinear Green-function
paper.  The sweep is sequential and records RSS before/after each point.
"""

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
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_frequency_sweep.csv")


OMEGAS_A05 = [
    0.18, 0.20, 0.22, 0.24, 0.255, 0.265,
    0.270, 0.280, 0.300, 0.350, 0.450, 0.600,
]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default=OUT)
    parser.add_argument("--a", type=float, default=0.5)
    parser.add_argument("--l", type=int, default=2)
    parser.add_argument("--m", type=int, default=2)
    parser.add_argument("--omegas", default=",".join(str(x) for x in OMEGAS_A05))
    parser.add_argument("--N", type=int, default=288)
    parser.add_argument("--quad-order", type=int, default=224)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--r-match", type=float, default=40.0)
    parser.add_argument("--max-rss-mb", type=float, default=2000.0)
    return parser.parse_args(argv)


def parse_omegas(text):
    out = [float(item) for item in text.split(",") if item.strip()]
    if not out:
        raise ValueError("At least one frequency is required.")
    return out


def main(argv=None):
    args = parse_args(argv)
    omegas = parse_omegas(args.omegas)
    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)

    rows = []
    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is not None:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    for omega in omegas:
        rss_before = require_memory_room(args.max_rss_mb, f"before omega={omega}")
        start = time.perf_counter()
        print(
            f"Running a={args.a:g} l={args.l} m={args.m} omega={omega:g} "
            f"N={args.N} q={args.quad_order} RSS={rss_before:.1f} MB"
            if rss_before is not None
            else f"Running a={args.a:g} l={args.l} m={args.m} omega={omega:g}"
        )
        result = compute_kerr_scalar_green_diagnostics(
            args.l,
            args.m,
            omega,
            a=args.a,
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

        b_inc = result.B_inc
        b_ref = result.B_ref
        norm4 = abs(b_inc) ** 4
        horizon_factor = result.p_horizon * (result.r_plus ** 2 + result.a ** 2) / result.omega
        T0 = horizon_factor / abs(b_inc) ** 2
        R0 = abs(b_ref / b_inc) ** 2
        T1 = 2.0 * horizon_factor * result.A_hor_1.real / norm4
        R1 = 2.0 * (b_ref.conjugate() * result.A_ref_1).real / norm4
        A_ref_fixed = result.A_ref_1 / (abs(b_inc) ** 2 * b_inc)
        A_hor_fixed = result.A_hor_1 / (abs(b_inc) ** 2 * b_inc)

        row = {
            "label": f"kerr_a{args.a:g}_l{args.l}m{args.m}",
            "l": args.l,
            "m": args.m,
            "a": f"{args.a:.16e}",
            "omega": f"{omega:.16e}",
            "omega_h": f"{result.omega_h:.16e}",
            "m_omega_h": f"{args.m * result.omega_h:.16e}",
            "p_horizon": f"{result.p_horizon:.16e}",
            "superradiant": "true" if result.p_horizon < 0.0 else "false",
            "N": result.N_outer,
            "r_match": f"{result.r_match:.16e}",
            "quad_order": result.quad_order,
            "tail_epsrel": f"{result.tail_epsrel:.16e}",
            "B_inc": fmt_complex(b_inc),
            "B_ref": fmt_complex(b_ref),
            "A_ref_1_unit_horizon": fmt_complex(result.A_ref_1),
            "A_hor_1_unit_horizon": fmt_complex(result.A_hor_1),
            "A_ref_1_fixed_incident": fmt_complex(A_ref_fixed),
            "A_hor_1_fixed_incident": fmt_complex(A_hor_fixed),
            "T0": f"{T0:.16e}",
            "R0": f"{R0:.16e}",
            "linear_balance": f"{T0 + R0:.16e}",
            "T1": f"{T1:.16e}",
            "R1": f"{R1:.16e}",
            "nonlinear_balance": f"{T1 + R1:.16e}",
            "abs_nonlinear_balance": f"{abs(T1 + R1):.16e}",
            "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
            "elapsed_s": f"{elapsed_s:.6e}",
            "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
            "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
            "status": result.status,
        }
        rows.append(row)
        print(
            f"  T1={row['T1']} R1={row['R1']} "
            f"balance={row['nonlinear_balance']} RSS_after="
            f"{rss_after:.1f} MB" if rss_after is not None else ""
        )
        require_memory_room(args.max_rss_mb, f"after omega={omega}")

    fields = [
        "label", "l", "m", "a", "omega", "omega_h", "m_omega_h",
        "p_horizon", "superradiant", "N", "r_match", "quad_order",
        "tail_epsrel", "B_inc", "B_ref", "A_ref_1_unit_horizon",
        "A_hor_1_unit_horizon", "A_ref_1_fixed_incident",
        "A_hor_1_fixed_incident", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
        "wronskian_relative_error", "elapsed_s", "rss_mb_before",
        "rss_mb_after", "status",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved = {output}")


if __name__ == "__main__":
    main()
