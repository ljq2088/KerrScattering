"""Regenerate the axisymmetric PRD sweeps at the refined resolution."""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_kerr_scalar_nonlinear_diagnostics import (
    current_rss_mb,
    fmt_complex,
    require_memory_room,
)
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = Path(__file__).resolve().parents[1]
SWEEPS = {
    0: [0.02, 0.04, 0.06, 0.075, 0.09, 0.11, 0.14, 0.18, 0.24, 0.32, 0.45, 0.60],
    1: [0.04, 0.08, 0.12, 0.18, 0.22, 0.25, 0.28, 0.32, 0.38, 0.45, 0.55, 0.70, 0.85],
    2: [0.08, 0.14, 0.20, 0.28, 0.35, 0.42, 0.46, 0.50, 0.55, 0.62, 0.72, 0.85, 1.00],
}

FIELDS = [
    "label", "l", "m", "a", "omega", "omega_h", "m_omega_h",
    "p_horizon", "superradiant", "N", "r_match", "quad_order",
    "tail_epsrel", "B_inc", "B_ref", "A_ref_1_unit_horizon",
    "A_hor_1_unit_horizon", "A_ref_1_fixed_incident",
    "A_hor_1_fixed_incident", "T0", "R0", "linear_balance", "T1", "R1",
    "nonlinear_balance", "abs_nonlinear_balance", "wronskian_relative_error",
    "elapsed_s", "rss_mb_before", "rss_mb_after", "status",
]


def main() -> None:
    for ell, omegas in SWEEPS.items():
        output = ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_hires_l{ell}.csv"
        rows = []
        for omega in omegas:
            rss_before = require_memory_room(1500.0, f"before ell={ell} omega={omega}")
            start = time.perf_counter()
            print(
                f"Running axisymmetric ell={ell} omega={omega:g} N=240 q=192 "
                f"RSS={rss_before:.1f} MB" if rss_before is not None else
                f"Running axisymmetric ell={ell} omega={omega:g} N=240 q=192"
            )
            result = compute_kerr_scalar_green_diagnostics(
                ell, 0, omega, a=0.5, l_target=ell,
                N_outer=240, N_inner=240, r_match=40.0,
                quad_order=192, tail_epsrel=1e-11,
                radial_weight_model="kerr-covariant-sigma-dr",
            )
            elapsed = time.perf_counter() - start
            rss_after = current_rss_mb()
            b_inc = result.B_inc
            b_ref = result.B_ref
            horizon_factor = result.p_horizon * (result.r_plus**2 + result.a**2) / omega
            norm4 = abs(b_inc) ** 4
            t0 = horizon_factor / abs(b_inc) ** 2
            r0 = abs(b_ref / b_inc) ** 2
            t1 = 2.0 * horizon_factor * result.A_hor_1.real / norm4
            r1 = 2.0 * (b_ref.conjugate() * result.A_ref_1).real / norm4
            rows.append({
                "label": f"kerr_a0.5_l{ell}m0_hires", "l": ell, "m": 0,
                "a": "5.0000000000000000e-01", "omega": f"{omega:.16e}",
                "omega_h": f"{result.omega_h:.16e}",
                "m_omega_h": f"{0.0:.16e}",
                "p_horizon": f"{result.p_horizon:.16e}",
                "superradiant": "false", "N": result.N_outer,
                "r_match": f"{result.r_match:.16e}", "quad_order": result.quad_order,
                "tail_epsrel": f"{result.tail_epsrel:.16e}",
                "B_inc": fmt_complex(b_inc), "B_ref": fmt_complex(b_ref),
                "A_ref_1_unit_horizon": fmt_complex(result.A_ref_1),
                "A_hor_1_unit_horizon": fmt_complex(result.A_hor_1),
                "A_ref_1_fixed_incident": fmt_complex(result.A_ref_1 / (norm4 ** 0.5 * b_inc)),
                "A_hor_1_fixed_incident": fmt_complex(result.A_hor_1 / (norm4 ** 0.5 * b_inc)),
                "T0": f"{t0:.16e}", "R0": f"{r0:.16e}",
                "linear_balance": f"{t0 + r0:.16e}",
                "T1": f"{t1:.16e}", "R1": f"{r1:.16e}",
                "nonlinear_balance": f"{t1 + r1:.16e}",
                "abs_nonlinear_balance": f"{abs(t1 + r1):.16e}",
                "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                "elapsed_s": f"{elapsed:.6e}",
                "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
                "status": result.status,
            })
            print(
                f"  T1={t1:.6e} balance={t1 + r1:.3e} "
                f"RSS_after={rss_after:.1f} MB" if rss_after is not None else ""
            )
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
