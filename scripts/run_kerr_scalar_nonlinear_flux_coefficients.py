"""Compute fixed-incident nonlinear flux coefficients for Kerr s=0 self channels."""

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    CASES,
    current_rss_mb,
    fmt_complex,
    require_memory_room,
)
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_flux_coefficients.csv")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", default=OUT)
    parser.add_argument("--case-label", action="append", default=[])
    parser.add_argument("--N-outer", type=int, default=256)
    parser.add_argument("--N-inner", type=int, default=256)
    parser.add_argument("--quad-order", type=int, default=192)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--max-rss-mb", type=float, default=0.0)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    cases = CASES
    if args.case_label:
        labels = set(args.case_label)
        cases = [case for case in CASES if case["label"] in labels]
        missing = labels - {case["label"] for case in cases}
        if missing:
            raise ValueError(f"Unknown case label(s): {', '.join(sorted(missing))}")

    output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is not None:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    rows = []
    for case in cases:
        rss_before = require_memory_room(args.max_rss_mb, f"before {case['label']}")
        start = time.perf_counter()
        print(
            f"Running fixed-incident coefficients for {case['label']} "
            f"N={args.N_outer} q={args.quad_order}"
        )
        result = compute_kerr_scalar_green_diagnostics(
            case["l"],
            case["m"],
            case["omega"],
            a=case["a"],
            l_target=case["l"],
            N_outer=args.N_outer,
            N_inner=args.N_inner,
            r_match=case.get("r_match"),
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
        A_ref_fixed_incident = result.A_ref_1 / (abs(b_inc) ** 2 * b_inc)
        A_hor_fixed_incident = result.A_hor_1 / (abs(b_inc) ** 2 * b_inc)
        R1 = 2.0 * (b_ref.conjugate() * result.A_ref_1).real / norm4
        T1 = 2.0 * horizon_factor * result.A_hor_1.real / norm4

        rows.append({
            "label": case["label"],
            "l": case["l"],
            "m": case["m"],
            "a": f"{case['a']:.16e}",
            "omega": f"{case['omega']:.16e}",
            "omega_h": f"{result.omega_h:.16e}",
            "p_horizon": f"{result.p_horizon:.16e}",
            "N_outer": result.N_outer,
            "N_inner": result.N_inner,
            "r_match": f"{result.r_match:.16e}",
            "quad_order": result.quad_order,
            "tail_epsrel": f"{result.tail_epsrel:.16e}",
            "B_inc": fmt_complex(result.B_inc),
            "B_ref": fmt_complex(result.B_ref),
            "A_ref_1_unit_horizon": fmt_complex(result.A_ref_1),
            "A_hor_1_unit_horizon": fmt_complex(result.A_hor_1),
            "A_ref_1_fixed_incident": fmt_complex(A_ref_fixed_incident),
            "A_hor_1_fixed_incident": fmt_complex(A_hor_fixed_incident),
            "T0": f"{T0:.16e}",
            "R0": f"{R0:.16e}",
            "linear_balance": f"{T0 + R0:.16e}",
            "T1": f"{T1:.16e}",
            "R1": f"{R1:.16e}",
            "nonlinear_balance": f"{T1 + R1:.16e}",
            "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
            "elapsed_s": f"{elapsed_s:.6e}",
            "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
            "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
            "status": result.status,
        })

    fields = [
        "label", "l", "m", "a", "omega", "omega_h", "p_horizon",
        "N_outer", "N_inner", "r_match", "quad_order", "tail_epsrel",
        "B_inc", "B_ref", "A_ref_1_unit_horizon", "A_hor_1_unit_horizon",
        "A_ref_1_fixed_incident", "A_hor_1_fixed_incident",
        "T0", "R0", "linear_balance", "T1", "R1", "nonlinear_balance",
        "wronskian_relative_error", "elapsed_s", "rss_mb_before",
        "rss_mb_after", "status",
    ]
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr scalar fixed-incident nonlinear flux coefficients")
    for row in rows:
        print(
            f"  {row['label']}: T0={row['T0']} R0={row['R0']} "
            f"T1={row['T1']} R1={row['R1']} "
            f"balance1={row['nonlinear_balance']}"
        )
    print(f"  saved = {output}")


if __name__ == "__main__":
    main()
