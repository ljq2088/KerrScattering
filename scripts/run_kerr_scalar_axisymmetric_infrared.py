"""Validate the analytic omega -> 0 flux laws for axisymmetric scalar modes."""

from __future__ import annotations

import argparse
import csv
import gc
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    current_rss_mb,
    require_memory_room,
)
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
    scalar_axisymmetric_cubic_low_frequency_horizon_coefficient,
    scalar_axisymmetric_cubic_low_frequency_integral,
    scalar_axisymmetric_cubic_low_frequency_phase_integral,
    scalar_axisymmetric_cubic_low_frequency_relative_horizon_amplitude,
    scalar_axisymmetric_cubic_low_frequency_response,
    scalar_axisymmetric_linear_low_frequency_coefficient,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "kerr_scalar_axisymmetric_infrared.csv"
CASES = {
    0: (0.00075, 0.001, 0.00125, 0.00175, 0.0025, 0.0035, 0.005),
    1: (0.0015, 0.002, 0.0025, 0.0035, 0.005, 0.007, 0.01),
    2: (0.005, 0.006, 0.007, 0.0085, 0.01, 0.014, 0.02),
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--a", type=float, default=0.5)
    parser.add_argument("--N", type=int, default=176)
    parser.add_argument("--quad-order", type=int, default=176)
    parser.add_argument("--tail-epsrel", type=float, default=1e-11)
    parser.add_argument("--max-rss-mb", type=float, default=1000.0)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    require_memory_room(args.max_rss_mb, "initial")
    rows = []
    for ell, frequencies in CASES.items():
        integral = scalar_axisymmetric_cubic_low_frequency_integral(ell)
        phase_integral = scalar_axisymmetric_cubic_low_frequency_phase_integral(
            ell
        )
        horizon_coefficient = (
            scalar_axisymmetric_cubic_low_frequency_horizon_coefficient(
                ell, args.a
            )
        )
        relative_horizon_limit = (
            scalar_axisymmetric_cubic_low_frequency_relative_horizon_amplitude(
                ell
            )
        )
        response_limit = scalar_axisymmetric_cubic_low_frequency_response(ell)
        t0_coefficient = scalar_axisymmetric_linear_low_frequency_coefficient(
            ell, args.a
        )
        t1_coefficient = t0_coefficient * response_limit
        for omega in frequencies:
            rss_before = require_memory_room(
                args.max_rss_mb, f"before l={ell} omega={omega:g}"
            )
            print(
                f"Running l={ell} m=0 a={args.a:g} omega={omega:g} "
                f"N={args.N} q={args.quad_order} "
                f"RSS={rss_before if rss_before is not None else float('nan'):.1f} MB",
                flush=True,
            )
            started = time.perf_counter()
            result = compute_kerr_scalar_green_diagnostics(
                ell,
                0,
                omega,
                a=args.a,
                l_target=ell,
                N_outer=args.N,
                N_inner=args.N,
                quad_order=args.quad_order,
                tail_epsrel=args.tail_epsrel,
                radial_weight_model="kerr-covariant-sigma-dr",
                linear_solver="equilibrated",
            )
            flux = fixed_incident_flux_coefficients(result)
            elapsed = time.perf_counter() - started
            rss_after = current_rss_mb()
            power = 2 * ell + 2
            scaled_t0 = flux.T0 / omega**power
            scaled_t1 = flux.T1 / omega**power
            scaled_horizon_amplitude = result.A_hor_1 * omega**power
            relative_horizon_amplitude = (
                result.A_hor_1 / abs(result.B_inc) ** 2
            )
            scaled_horizon_error = abs(
                scaled_horizon_amplitude - horizon_coefficient
            ) / abs(horizon_coefficient)
            relative_horizon_error = abs(
                relative_horizon_amplitude - relative_horizon_limit
            ) / abs(relative_horizon_limit)
            rows.append(
                {
                    "l": ell,
                    "m": 0,
                    "a": f"{args.a:.16e}",
                    "omega": f"{omega:.16e}",
                    "N": args.N,
                    "quad_order": args.quad_order,
                    "mapping": result.mapping,
                    "T0": f"{flux.T0:.16e}",
                    "T1": f"{flux.T1:.16e}",
                    "horizon_response": f"{flux.horizon_response:.16e}",
                    "infrared_integral": f"{integral:.16e}",
                    "phase_integral": f"{phase_integral:.16e}",
                    "analytic_response_limit": f"{response_limit:.16e}",
                    "response_relative_error": (
                        f"{abs(flux.horizon_response-response_limit)/response_limit:.16e}"
                    ),
                    "scaled_T0": f"{scaled_t0:.16e}",
                    "analytic_T0_coefficient": f"{t0_coefficient:.16e}",
                    "scaled_T0_relative_error": (
                        f"{abs(scaled_t0-t0_coefficient)/t0_coefficient:.16e}"
                    ),
                    "scaled_T1": f"{scaled_t1:.16e}",
                    "analytic_T1_coefficient": f"{t1_coefficient:.16e}",
                    "scaled_T1_relative_error": (
                        f"{abs(scaled_t1-t1_coefficient)/t1_coefficient:.16e}"
                    ),
                    "A_hor_1_real": f"{result.A_hor_1.real:.16e}",
                    "A_hor_1_imag": f"{result.A_hor_1.imag:.16e}",
                    "scaled_A_hor_1_real": (
                        f"{scaled_horizon_amplitude.real:.16e}"
                    ),
                    "scaled_A_hor_1_imag": (
                        f"{scaled_horizon_amplitude.imag:.16e}"
                    ),
                    "analytic_A_hor_1_real_coefficient": (
                        f"{horizon_coefficient.real:.16e}"
                    ),
                    "analytic_A_hor_1_imag_coefficient": (
                        f"{horizon_coefficient.imag:.16e}"
                    ),
                    "scaled_A_hor_1_complex_relative_error": (
                        f"{scaled_horizon_error:.16e}"
                    ),
                    "A_hor_1_phase_rad": (
                        f"{math.atan2(result.A_hor_1.imag, result.A_hor_1.real):.16e}"
                    ),
                    "analytic_A_hor_1_phase_rad": (
                        f"{math.atan2(horizon_coefficient.imag, horizon_coefficient.real):.16e}"
                    ),
                    "relative_horizon_amplitude_real": (
                        f"{relative_horizon_amplitude.real:.16e}"
                    ),
                    "relative_horizon_amplitude_imag": (
                        f"{relative_horizon_amplitude.imag:.16e}"
                    ),
                    "analytic_relative_horizon_amplitude_real": (
                        f"{relative_horizon_limit.real:.16e}"
                    ),
                    "analytic_relative_horizon_amplitude_imag": (
                        f"{relative_horizon_limit.imag:.16e}"
                    ),
                    "relative_horizon_amplitude_complex_relative_error": (
                        f"{relative_horizon_error:.16e}"
                    ),
                    "linear_balance": f"{flux.linear_balance:.16e}",
                    "infinity_side_nonlinear_balance": f"{flux.nonlinear_balance:.16e}",
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
            )
            print(
                f"  chi={flux.horizon_response:.12e} "
                f"rel_chi={abs(flux.horizon_response-response_limit)/response_limit:.3e} "
                f"rel_AH={scaled_horizon_error:.3e} "
                f"Werr={result.wronskian_relative_error:.3e}",
                flush=True,
            )
            del result, flux
            gc.collect()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved = {args.output.resolve()}")


if __name__ == "__main__":
    main()
