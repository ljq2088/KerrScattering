"""Scan the nonlinear scalar Kerr response across superradiant thresholds.

The primary observable is

    chi_H = T1 / T0 = 2 Re(A_hor_1) / |B_inc|^2,

evaluated from the horizon amplitude on the right-hand side.  This remains
regular at omega = m Omega_H, where T0 and T1 separately vanish.  The direct
infinity-side balance T1 + R1 is retained as an independent display gate.
Rows are written after every solve so a long sequential scan can be resumed.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    current_rss_mb,
    fmt_complex,
    require_memory_room,
)
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
)
from src.teukolsky_scalar import KerrParams


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "kerr_scalar_superradiant_response_scan.csv"

FIELDS = [
    "label", "l", "m", "a", "omega_fraction", "omega", "omega_h",
    "m_omega_h", "p_horizon", "superradiant", "N", "r_match",
    "quad_order", "tail_epsrel", "B_inc", "B_ref",
    "A_ref_1_unit_horizon", "A_hor_1_unit_horizon", "T0", "R0",
    "linear_balance", "T1", "R1", "nonlinear_balance",
    "abs_nonlinear_balance", "horizon_response", "T1_over_T0",
    "horizon_identity_error", "wronskian_relative_error", "elapsed_s",
    "linear_solver", "rss_mb_before", "rss_mb_after", "status",
]


def comma_floats(text: str) -> list[float]:
    values = [float(item) for item in text.split(",") if item.strip()]
    if not values:
        raise argparse.ArgumentTypeError("at least one value is required")
    return values


def comma_modes(text: str) -> list[tuple[int, int]]:
    modes = []
    for item in text.split(","):
        if not item.strip():
            continue
        l_text, separator, m_text = item.partition(":")
        if not separator:
            raise argparse.ArgumentTypeError("modes must use l:m notation")
        mode = (int(l_text), int(m_text))
        if mode[0] < abs(mode[1]) or mode[1] <= 0:
            raise argparse.ArgumentTypeError("require l >= |m| and m > 0")
        modes.append(mode)
    if not modes:
        raise argparse.ArgumentTypeError("at least one mode is required")
    return modes


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--spins", type=comma_floats, default=[0.3, 0.5, 0.7, 0.9])
    parser.add_argument("--modes", type=comma_modes, default=[(1, 1), (2, 2), (3, 3)])
    parser.add_argument(
        "--omega-fractions",
        type=comma_floats,
        default=[0.60, 0.80, 0.90, 0.97, 1.03, 1.10, 1.25, 1.50],
        help="frequencies omega/(m Omega_H); do not include the exact threshold",
    )
    parser.add_argument("--N", type=int, default=288)
    parser.add_argument("--quad-order", type=int, default=256)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument(
        "--linear-solver",
        choices=["direct", "equilibrated"],
        default="equilibrated",
    )
    parser.add_argument(
        "--r-match",
        type=float,
        default=0.0,
        help="fixed matching radius; 0 uses the solver's frequency-dependent default",
    )
    parser.add_argument("--max-rss-mb", type=float, default=1800.0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args(argv)


def row_key(row: dict[str, str]) -> tuple[float, int, int, float]:
    return (
        round(float(row["a"]), 14),
        int(row["l"]),
        int(row["m"]),
        round(float(row["omega_fraction"]), 14),
    )


def write_rows(output: Path, rows: list[dict[str, object]]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)


def main(argv=None) -> None:
    args = parse_args(argv)
    output = args.output.resolve()
    rows: list[dict[str, object]] = []
    completed: set[tuple[float, int, int, float]] = set()
    if args.resume and output.exists():
        with output.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        completed = {row_key(row) for row in rows}
        print(f"Resuming with {len(completed)} completed rows")

    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is not None:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    for a in args.spins:
        params = KerrParams(M=1.0, a=a)
        for l, m in args.modes:
            threshold = m * params.omega_h
            for fraction in args.omega_fractions:
                key = (round(a, 14), l, m, round(fraction, 14))
                if key in completed:
                    continue
                if fraction == 1.0:
                    raise ValueError("omit omega_fraction=1, where T0=T1=0 exactly")

                omega = fraction * threshold
                context = f"a={a:g} l={l} m={m} x={fraction:g}"
                rss_before = require_memory_room(args.max_rss_mb, f"before {context}")
                print(
                    f"Running {context} omega={omega:.12g} N={args.N} "
                    f"q={args.quad_order} RSS={rss_before:.1f} MB"
                    if rss_before is not None
                    else f"Running {context} omega={omega:.12g}"
                )
                start = time.perf_counter()
                result = compute_kerr_scalar_green_diagnostics(
                    l,
                    m,
                    omega,
                    a=a,
                    l_target=l,
                    N_outer=args.N,
                    N_inner=args.N,
                    r_match=None if args.r_match == 0.0 else args.r_match,
                    quad_order=args.quad_order,
                    tail_epsrel=args.tail_epsrel,
                    radial_weight_model="kerr-covariant-sigma-dr",
                    linear_solver=args.linear_solver,
                )
                flux = fixed_incident_flux_coefficients(result)
                elapsed_s = time.perf_counter() - start
                rss_after = current_rss_mb()
                ratio = flux.T1 / flux.T0
                identity_error = abs(ratio - flux.horizon_response) / max(
                    abs(flux.horizon_response), 1e-300
                )
                row: dict[str, object] = {
                    "label": f"kerr_a{a:g}_l{l}m{m}",
                    "l": l,
                    "m": m,
                    "a": f"{a:.16e}",
                    "omega_fraction": f"{fraction:.16e}",
                    "omega": f"{omega:.16e}",
                    "omega_h": f"{result.omega_h:.16e}",
                    "m_omega_h": f"{threshold:.16e}",
                    "p_horizon": f"{result.p_horizon:.16e}",
                    "superradiant": "true" if result.p_horizon < 0.0 else "false",
                    "N": result.N_outer,
                    "r_match": f"{result.r_match:.16e}",
                    "quad_order": result.quad_order,
                    "tail_epsrel": f"{result.tail_epsrel:.16e}",
                    "B_inc": fmt_complex(result.B_inc),
                    "B_ref": fmt_complex(result.B_ref),
                    "A_ref_1_unit_horizon": fmt_complex(result.A_ref_1),
                    "A_hor_1_unit_horizon": fmt_complex(result.A_hor_1),
                    "T0": f"{flux.T0:.16e}",
                    "R0": f"{flux.R0:.16e}",
                    "linear_balance": f"{flux.linear_balance:.16e}",
                    "T1": f"{flux.T1:.16e}",
                    "R1": f"{flux.R1:.16e}",
                    "nonlinear_balance": f"{flux.nonlinear_balance:.16e}",
                    "abs_nonlinear_balance": f"{abs(flux.nonlinear_balance):.16e}",
                    "horizon_response": f"{flux.horizon_response:.16e}",
                    "T1_over_T0": f"{ratio:.16e}",
                    "horizon_identity_error": f"{identity_error:.16e}",
                    "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                    "elapsed_s": f"{elapsed_s:.6e}",
                    "linear_solver": result.linear_solver,
                    "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                    "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
                    "status": result.status,
                }
                rows.append(row)
                completed.add(key)
                write_rows(output, rows)
                print(
                    f"  chi_H={flux.horizon_response:.9e} "
                    f"T1={flux.T1:.9e} balance={flux.nonlinear_balance:.3e} "
                    f"Werr={result.wronskian_relative_error:.3e}"
                )
                require_memory_room(args.max_rss_mb, f"after {context}")

    print(f"saved = {output}")


if __name__ == "__main__":
    main()
