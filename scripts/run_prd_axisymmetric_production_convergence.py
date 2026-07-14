"""Run production-versus-refined convergence checks for the PRD data."""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_kerr_scalar_nonlinear_diagnostics import current_rss_mb
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_axisymmetric_production_convergence.csv"

CASES = (
    {"label": "axisym_l0_peak", "l": 0, "m": 0, "a": 0.5, "omega": 0.125, "r_match": 40.0},
    {"label": "axisym_l1_peak", "l": 1, "m": 0, "a": 0.5, "omega": 0.34, "r_match": 40.0},
    {"label": "axisym_l2_peak", "l": 2, "m": 0, "a": 0.5, "omega": 0.52, "r_match": 40.0},
)

CONFIGS = (
    ("reference", 240, 192),
    ("production", 224, 160),
    ("N_only", 224, 192),
    ("q_only", 240, 160),
    ("q_low", 240, 128),
)


def fmt_complex(value: complex) -> str:
    return f"{value.real:.16e}{value.imag:+.16e}j"


def rel(value: complex | float, reference: complex | float) -> float:
    return abs(value - reference) / max(abs(reference), 1e-300)


def row_from_result(case, config, n, q, result, elapsed, rss_before, rss_after):
    horizon_factor = result.p_horizon * (result.r_plus**2 + result.a**2) / result.omega
    bnorm4 = abs(result.B_inc) ** 4
    t0 = horizon_factor / abs(result.B_inc) ** 2
    r0 = abs(result.B_ref / result.B_inc) ** 2
    t1 = 2.0 * horizon_factor * result.A_hor_1.real / bnorm4
    r1 = 2.0 * (result.B_ref.conjugate() * result.A_ref_1).real / bnorm4
    return {
        "label": case["label"],
        "l": case["l"],
        "m": case["m"],
        "a": f"{case['a']:.16e}",
        "omega": f"{case['omega']:.16e}",
        "config": config,
        "N": n,
        "quad_order": q,
        "r_match": f"{case['r_match']:.16e}",
        "B_inc": fmt_complex(result.B_inc),
        "B_ref": fmt_complex(result.B_ref),
        "A_ref_1": fmt_complex(result.A_ref_1),
        "A_hor_1": fmt_complex(result.A_hor_1),
        "T0": f"{t0:.16e}",
        "R0": f"{r0:.16e}",
        "linear_balance": f"{t0 + r0 - 1.0:.16e}",
        "T1": f"{t1:.16e}",
        "R1": f"{r1:.16e}",
        "nonlinear_balance": f"{t1 + r1:.16e}",
        "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
        "rss_before_mb": "" if rss_before is None else f"{rss_before:.6e}",
        "rss_after_mb": "" if rss_after is None else f"{rss_after:.6e}",
        "elapsed_s": f"{elapsed:.6e}",
        "status": result.status,
    }


def main() -> None:
    rows = []
    for case in CASES:
        by_config = {}
        for config, n, q in CONFIGS:
            rss_before = current_rss_mb()
            start = time.perf_counter()
            print(
                f"Running {case['label']} {config}: N={n} q={q} "
                f"RSS={rss_before:.1f} MB" if rss_before is not None else
                f"Running {case['label']} {config}: N={n} q={q}"
            )
            result = compute_kerr_scalar_green_diagnostics(
                case["l"], case["m"], case["omega"], a=case["a"],
                N_outer=n, N_inner=n, r_match=case["r_match"],
                quad_order=q, tail_epsrel=1e-11,
                radial_weight_model="kerr-covariant-sigma-dr",
            )
            elapsed = time.perf_counter() - start
            rss_after = current_rss_mb()
            row = row_from_result(case, config, n, q, result, elapsed, rss_before, rss_after)
            by_config[config] = row
            rows.append(row)
            print(
                f"  balance={row['nonlinear_balance']} "
                f"Werr={row['wronskian_relative_error']} "
                f"RSS={row['rss_after_mb'] or 'NA'} MB"
            )

        reference = by_config["reference"]
        for row in rows[-len(CONFIGS):]:
            row["rel_A_ref_to_reference"] = f"{rel(complex(row['A_ref_1']), complex(reference['A_ref_1'])):.16e}"
            row["rel_A_hor_to_reference"] = f"{rel(complex(row['A_hor_1']), complex(reference['A_hor_1'])):.16e}"
            row["rel_T1_to_reference"] = f"{rel(float(row['T1']), float(reference['T1'])):.16e}"
            row["rel_R1_to_reference"] = f"{rel(float(row['R1']), float(reference['R1'])):.16e}"

    fields = [
        "label", "l", "m", "a", "omega", "config", "N", "quad_order",
        "r_match", "B_inc", "B_ref", "A_ref_1", "A_hor_1", "T0", "R0",
        "linear_balance", "T1", "R1", "nonlinear_balance",
        "wronskian_relative_error", "rel_A_ref_to_reference",
        "rel_A_hor_to_reference", "rel_T1_to_reference",
        "rel_R1_to_reference", "rss_before_mb", "rss_after_mb", "elapsed_s",
        "status",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
