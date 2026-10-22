"""Scan scalar Kerr response in the near-horizon detuning p/kappa.

The near-extremal variables are

    y = (omega - m Omega_H) / kappa,
    Xi = kappa chi_H,

where kappa is the Kerr surface gravity and chi_H = T1/T0 is evaluated
directly from the horizon amplitude.  Rows are checkpointed after every solve
so the memory-bounded scan can be resumed.
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
    require_memory_room,
)
from scripts.run_kerr_scalar_superradiant_response_scan import (
    comma_floats,
)
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
)
from src.teukolsky_scalar import KerrParams


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "kerr_scalar_near_extremal_scaling.csv"

FIELDS = [
    "a", "l", "m", "surface_gravity", "detuning_over_kappa",
    "omega_fraction", "omega", "m_omega_h", "p_horizon", "N",
    "quad_order", "r_match", "T0", "T1", "R1", "linear_balance",
    "nonlinear_balance", "horizon_response", "scaled_horizon_response",
    "wronskian_relative_error", "elapsed_s", "rss_mb_before",
    "rss_mb_after", "status",
]


def comma_scalar_modes(text: str) -> list[tuple[int, int]]:
    modes = []
    for item in text.split(","):
        if not item.strip():
            continue
        l_text, separator, m_text = item.partition(":")
        if not separator:
            raise argparse.ArgumentTypeError("modes must use l:m notation")
        mode = (int(l_text), int(m_text))
        if mode[0] < abs(mode[1]) or mode[1] < 0:
            raise argparse.ArgumentTypeError("require l >= |m| and m >= 0")
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
    parser.add_argument("--spins", type=comma_floats, default=[0.95, 0.98, 0.99])
    parser.add_argument(
        "--modes", type=comma_scalar_modes, default=[(1, 1), (2, 2), (3, 3)]
    )
    parser.add_argument(
        "--detunings",
        type=comma_floats,
        default=[-1.0, -0.5, -0.2, -0.05, 0.05, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5],
        help="values of (omega - m Omega_H) / kappa",
    )
    parser.add_argument("--N", type=int, default=144)
    parser.add_argument("--quad-order", type=int, default=144)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--r-match", type=float, default=0.0)
    parser.add_argument("--max-rss-mb", type=float, default=1200.0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args(argv)


def surface_gravity(params: KerrParams) -> float:
    return (params.rp - params.rm) / (
        2.0 * (params.rp**2 + params.a**2)
    )


def row_key(row: dict[str, str]) -> tuple[float, int, int, float]:
    return (
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
        kappa = surface_gravity(params)
        for l, m in args.modes:
            threshold = m * params.omega_h
            for detuning in args.detunings:
                if detuning == 0.0:
                    raise ValueError(
                        "omit exact p=0; use symmetric nonzero detunings to select "
                        "the ingoing threshold limit"
                    )
                key = (round(a, 14), l, m, round(detuning, 14))
                if key in completed:
                    continue
                omega = threshold + detuning * kappa
                if omega <= 0.0:
                    raise ValueError(
                        f"Nonpositive omega for a={a}, l={l}, m={m}, y={detuning}"
                    )
                fraction = omega / threshold if threshold != 0.0 else float("nan")
                fraction_label = f"{fraction:.12g}" if threshold != 0.0 else "n/a"
                context = f"a={a:g} l={l} m={m} y={detuning:g}"
                rss_before = require_memory_room(args.max_rss_mb, f"before {context}")
                print(
                    f"Running {context} x={fraction_label} omega={omega:.12g} "
                    f"N={args.N} q={args.quad_order}"
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
                )
                flux = fixed_incident_flux_coefficients(result)
                elapsed = time.perf_counter() - start
                rss_after = current_rss_mb()
                row: dict[str, object] = {
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
                }
                rows.append(row)
                completed.add(key)
                write_rows(output, rows)
                print(
                    f"  kappa*chi_H={kappa * flux.horizon_response:.9e} "
                    f"chi_H={flux.horizon_response:.9e} "
                    f"balance={flux.nonlinear_balance:.3e}"
                )
                require_memory_room(args.max_rss_mb, f"after {context}")

    print(f"saved = {output}")


if __name__ == "__main__":
    main()
