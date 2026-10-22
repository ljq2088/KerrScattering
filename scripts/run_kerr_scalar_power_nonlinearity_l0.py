"""Scan scalar-monopole response for |Phi|^(2n) Phi interactions."""

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
    require_memory_room,
)
from scripts.run_kerr_scalar_superradiant_response_scan import comma_floats
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
    scalar_monopole_low_frequency_coefficient,
)
from src.teukolsky_scalar import KerrParams


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "kerr_scalar_power_nonlinearity_l0.csv"

FIELDS = [
    "nonlinearity_order",
    "a",
    "surface_gravity",
    "frequency_mode",
    "frequency_coordinate",
    "omega_over_kappa",
    "omega",
    "N",
    "quad_order",
    "r_match",
    "angular_coupling",
    "angular_coupling_cos2",
    "T0",
    "T1",
    "R1",
    "linear_balance",
    "nonlinear_balance",
    "relative_nonlinear_balance",
    "horizon_response",
    "response_over_frequency_power",
    "analytic_low_frequency_coefficient",
    "relative_error_to_analytic_coefficient",
    "wronskian_relative_error",
    "elapsed_s",
    "rss_mb_before",
    "rss_mb_after",
    "status",
]


def comma_positive_ints(text: str) -> list[int]:
    values = [int(item) for item in text.split(",") if item.strip()]
    if not values or any(value < 1 for value in values):
        raise argparse.ArgumentTypeError("orders must be positive integers")
    return values


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--spins", type=comma_floats, default=[0.0, 0.5, 0.9])
    parser.add_argument("--orders", type=comma_positive_ints, default=[1, 2, 3])
    parser.add_argument(
        "--frequencies",
        type=comma_floats,
        default=[0.005, 0.01, 0.02, 0.03, 0.05],
        help="omega for fixed mode or omega/kappa for kappa mode",
    )
    parser.add_argument(
        "--frequency-mode",
        choices=("fixed", "kappa"),
        default="fixed",
    )
    parser.add_argument("--N", type=int, default=144)
    parser.add_argument("--quad-order", type=int, default=144)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--r-match", type=float, default=0.0)
    parser.add_argument("--max-rss-mb", type=float, default=1000.0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args(argv)


def surface_gravity(params: KerrParams) -> float:
    return (params.rp - params.rm) / (
        2.0 * (params.rp**2 + params.a**2)
    )


def row_key(row: dict[str, str]) -> tuple[int, float, float]:
    return (
        int(row["nonlinearity_order"]),
        round(float(row["a"]), 14),
        round(float(row["frequency_coordinate"]), 14),
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
    completed: set[tuple[int, float, float]] = set()
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
        kappa = surface_gravity(params)
        for n in args.orders:
            analytic = scalar_monopole_low_frequency_coefficient(n)
            power = 2 * n - 2
            for coordinate in args.frequencies:
                key = (n, round(a, 14), round(coordinate, 14))
                if key in completed:
                    continue
                omega = (
                    coordinate
                    if args.frequency_mode == "fixed"
                    else coordinate * kappa
                )
                if omega <= 0.0:
                    raise ValueError("All sampled frequencies must be positive.")
                context = (
                    f"n={n} a={a:g} {args.frequency_mode}={coordinate:g} "
                    f"omega={omega:.12g}"
                )
                rss_before = require_memory_room(
                    args.max_rss_mb, f"before {context}"
                )
                print(
                    f"Running {context} N={args.N} q={args.quad_order}"
                )
                start = time.perf_counter()
                result = compute_kerr_scalar_green_diagnostics(
                    0,
                    0,
                    omega,
                    a=a,
                    l_target=0,
                    N_outer=args.N,
                    N_inner=args.N,
                    r_match=None if args.r_match == 0.0 else args.r_match,
                    quad_order=args.quad_order,
                    tail_epsrel=args.tail_epsrel,
                    radial_weight_model="kerr-covariant-sigma-dr",
                    linear_solver="equilibrated",
                    nonlinearity_order=n,
                )
                flux = fixed_incident_flux_coefficients(result)
                elapsed = time.perf_counter() - start
                rss_after = current_rss_mb()
                scaled = flux.horizon_response / omega**power
                relative_balance = abs(flux.nonlinear_balance) / max(
                    abs(flux.T1), abs(flux.R1), 1.0e-300
                )
                row: dict[str, object] = {
                    "nonlinearity_order": n,
                    "a": f"{a:.16e}",
                    "surface_gravity": f"{kappa:.16e}",
                    "frequency_mode": args.frequency_mode,
                    "frequency_coordinate": f"{coordinate:.16e}",
                    "omega_over_kappa": f"{omega / kappa:.16e}",
                    "omega": f"{omega:.16e}",
                    "N": result.N_outer,
                    "quad_order": result.quad_order,
                    "r_match": f"{result.r_match:.16e}",
                    "angular_coupling": f"{result.angular_coupling:.16e}",
                    "angular_coupling_cos2": (
                        f"{result.angular_coupling_cos2:.16e}"
                    ),
                    "T0": f"{flux.T0:.16e}",
                    "T1": f"{flux.T1:.16e}",
                    "R1": f"{flux.R1:.16e}",
                    "linear_balance": f"{flux.linear_balance:.16e}",
                    "nonlinear_balance": f"{flux.nonlinear_balance:.16e}",
                    "relative_nonlinear_balance": f"{relative_balance:.16e}",
                    "horizon_response": f"{flux.horizon_response:.16e}",
                    "response_over_frequency_power": f"{scaled:.16e}",
                    "analytic_low_frequency_coefficient": f"{analytic:.16e}",
                    "relative_error_to_analytic_coefficient": (
                        f"{abs(scaled - analytic) / analytic:.16e}"
                    ),
                    "wronskian_relative_error": (
                        f"{result.wronskian_relative_error:.16e}"
                    ),
                    "elapsed_s": f"{elapsed:.6e}",
                    "rss_mb_before": (
                        "" if rss_before is None else f"{rss_before:.6e}"
                    ),
                    "rss_mb_after": (
                        "" if rss_after is None else f"{rss_after:.6e}"
                    ),
                    "status": result.status,
                }
                rows.append(row)
                completed.add(key)
                write_rows(output, rows)
                print(
                    f"  chi={flux.horizon_response:.9e} "
                    f"chi/omega^{power}={scaled:.9e} "
                    f"rel_analytic={abs(scaled - analytic) / analytic:.3e} "
                    f"rel_balance={relative_balance:.3e}"
                )
                require_memory_room(args.max_rss_mb, f"after {context}")

    print(f"saved = {output}")


if __name__ == "__main__":
    main()
