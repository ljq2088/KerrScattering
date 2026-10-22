"""Scan ``|Phi|^(2n) Phi`` Kerr responses near the superradiant threshold.

The scan keeps the nonlinearity order in the checkpoint key and records the
quantities needed to separate fixed-incident normalization from the radial
Green-function response.  Exact threshold is approached symmetrically in
``y = (omega - m Omega_H) / kappa`` rather than solved at the degenerate
point ``p = 0``.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_near_extremal_scaling import (
    comma_scalar_modes,
    surface_gravity,
)
from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    current_rss_mb,
    require_memory_room,
)
from scripts.run_kerr_scalar_superradiant_response_scan import comma_floats
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
)
from src.teukolsky_scalar import KerrParams


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "kerr_scalar_power_near_extremal.csv"

FIELDS = [
    "nonlinearity_order", "a", "l", "m", "surface_gravity",
    "detuning_over_kappa", "omega_fraction", "omega", "m_omega_h",
    "p_horizon", "N", "quad_order", "r_match", "angular_coupling_real",
    "angular_coupling_imag", "angular_coupling_cos2_real",
    "angular_coupling_cos2_imag", "B_inc_abs", "A_hor_1_real",
    "A_hor_1_imag", "T0", "T1", "R1", "linear_balance",
    "nonlinear_balance", "horizon_response", "scaled_horizon_response",
    "wronskian_relative_error", "elapsed_s", "rss_mb_before",
    "rss_mb_after", "status", "inner_quadrature", "inner_log_min",
]


def comma_positive_integers(text: str) -> list[int]:
    values = []
    for item in text.split(","):
        if not item.strip():
            continue
        value = int(item)
        if value < 1:
            raise argparse.ArgumentTypeError("orders must be positive integers")
        values.append(value)
    if not values:
        raise argparse.ArgumentTypeError("at least one order is required")
    return values


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--orders", type=comma_positive_integers, default=[2, 3])
    parser.add_argument("--spins", type=comma_floats, default=[0.98, 0.99, 0.995, 0.997, 0.999])
    parser.add_argument(
        "--modes", type=comma_scalar_modes, default=[(1, 1), (2, 2)]
    )
    parser.add_argument(
        "--detunings", type=comma_floats,
        default=[-0.5, -0.05, -0.025, 0.025, 0.05, 0.5, 1.0],
        help="values of y=(omega-m Omega_H)/kappa",
    )
    parser.add_argument("--N", type=int, default=144)
    parser.add_argument("--quad-order", type=int, default=144)
    parser.add_argument("--inner-quadrature", choices=['legendre','log-horizon'], default='legendre')
    parser.add_argument("--inner-log-min", type=float, default=-30)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--r-match", type=float, default=0.0)
    parser.add_argument("--max-rss-mb", type=float, default=1200.0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args(argv)


def row_key(row: dict[str, str]) -> tuple[int, float, int, int, float]:
    return (
        int(row["nonlinearity_order"]),
        round(float(row["a"]), 14),
        int(row["l"]),
        int(row["m"]),
        round(float(row["detuning_over_kappa"]), 14),
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
    completed: set[tuple[int, float, int, int, float]] = set()
    if args.resume and output.exists():
        with output.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        completed = {row_key(row) for row in rows}
        print(f"Resuming with {len(completed)} completed rows")

    initial_rss = require_memory_room(args.max_rss_mb, "initial")
    if initial_rss is not None:
        print(f"Initial RSS = {initial_rss:.1f} MB")

    for n in args.orders:
        for a in args.spins:
            params = KerrParams(M=1.0, a=a)
            kappa = surface_gravity(params)
            for l, m in args.modes:
                threshold = m * params.omega_h
                for detuning in args.detunings:
                    if detuning == 0.0:
                        raise ValueError(
                            "omit exact p=0; use symmetric nonzero detunings"
                        )
                    key = (n, round(a, 14), l, m, round(detuning, 14))
                    if key in completed:
                        continue
                    omega = threshold + detuning * kappa
                    if omega <= 0.0:
                        raise ValueError(
                            f"Nonpositive omega for n={n}, a={a}, "
                            f"l={l}, m={m}, y={detuning}"
                        )
                    fraction = omega / threshold if threshold != 0.0 else float("nan")
                    context = f"n={n} a={a:g} l={l} m={m} y={detuning:g}"
                    rss_before = require_memory_room(args.max_rss_mb, f"before {context}")
                    print(
                        f"Running {context} omega={omega:.12g} "
                        f"N={args.N} q={args.quad_order}",
                        flush=True,
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
                        linear_solver="equilibrated",
                        nonlinearity_order=n,
                        inner_quadrature=args.inner_quadrature,
                        inner_log_min=args.inner_log_min,
                    )
                    flux = fixed_incident_flux_coefficients(result)
                    elapsed = time.perf_counter() - start
                    rss_after = current_rss_mb()
                    row: dict[str, object] = {
                        "nonlinearity_order": n,
                        "a": f"{a:.16e}",
                        "l": l,
                        "m": m,
                        "surface_gravity": f"{kappa:.16e}",
                        "detuning_over_kappa": f"{detuning:.16e}",
                        "omega_fraction": f"{fraction:.16e}",
                        "omega": f"{omega:.16e}",
                        "m_omega_h": f"{threshold:.16e}",
                        "p_horizon": f"{result.p_horizon:.16e}",
                        "N": result.N_outer,
                        "quad_order": result.quad_order,
                        "r_match": f"{result.r_match:.16e}",
                        "angular_coupling_real": f"{result.angular_coupling.real:.16e}",
                        "angular_coupling_imag": f"{result.angular_coupling.imag:.16e}",
                        "angular_coupling_cos2_real": f"{result.angular_coupling_cos2.real:.16e}",
                        "angular_coupling_cos2_imag": f"{result.angular_coupling_cos2.imag:.16e}",
                        "B_inc_abs": f"{abs(result.B_inc):.16e}",
                        "A_hor_1_real": f"{result.A_hor_1.real:.16e}",
                        "A_hor_1_imag": f"{result.A_hor_1.imag:.16e}",
                        "T0": f"{flux.T0:.16e}",
                        "T1": f"{flux.T1:.16e}",
                        "R1": f"{flux.R1:.16e}",
                        "linear_balance": f"{flux.linear_balance:.16e}",
                        "nonlinear_balance": f"{flux.nonlinear_balance:.16e}",
                        "horizon_response": f"{flux.horizon_response:.16e}",
                        "scaled_horizon_response": f"{kappa * flux.horizon_response:.16e}",
                        "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                        "elapsed_s": f"{elapsed:.6e}",
                        "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                        "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
                        "status": result.status,
                        "inner_quadrature": args.inner_quadrature,
                        "inner_log_min": args.inner_log_min,
                    }
                    rows.append(row)
                    completed.add(key)
                    write_rows(output, rows)
                    print(
                        f"  kappa*chi_H={kappa * flux.horizon_response:.9e} "
                        f"chi_H={flux.horizon_response:.9e} "
                        f"balance={flux.nonlinear_balance:.3e} "
                        f"rss={rss_after if rss_after is not None else float('nan'):.1f} MB",
                        flush=True,
                    )
                    require_memory_room(args.max_rss_mb, f"after {context}")

    print(f"saved = {output}")


if __name__ == "__main__":
    main()
