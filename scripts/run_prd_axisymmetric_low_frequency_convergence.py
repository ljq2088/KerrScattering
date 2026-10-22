"""Audit the lowest accepted Kerr scalar points displayed by the PRD paper."""

from __future__ import annotations

import csv
import gc
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_kerr_scalar_nonlinear_diagnostics import current_rss_mb
from src.kerr_scalar_nonlinear import (
    compute_kerr_scalar_green_diagnostics,
    fixed_incident_flux_coefficients,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_axisymmetric_low_frequency_convergence.csv"

CASES = (
    {"label": "axisym_l0_low", "l": 0, "m": 0, "a": 0.5, "omega": 0.02},
    {"label": "axisym_l1_low", "l": 1, "m": 0, "a": 0.5, "omega": 0.12},
    {"label": "axisym_l2_low", "l": 2, "m": 0, "a": 0.5, "omega": 0.28},
)

# The reference is the largest simultaneous radial/quadrature setting.  The
# remaining rows vary one numerical choice at a time wherever possible.
CONFIGS = (
    {"name": "reference", "N": 256, "q": 256, "r_match": 40.0},
    {"name": "active", "N": 240, "q": 192, "r_match": 40.0},
    {"name": "N_low", "N": 224, "q": 256, "r_match": 40.0},
    {"name": "q_low", "N": 256, "q": 192, "r_match": 40.0},
    {"name": "rmatch_low", "N": 256, "q": 256, "r_match": 32.0},
    {"name": "rmatch_high", "N": 256, "q": 256, "r_match": 48.0},
)


def relative(value: float, reference: float) -> float:
    return abs(value - reference) / max(abs(reference), 1e-300)


def solve_row(case: dict[str, float | int | str], config: dict[str, float | int | str]):
    rss_before = current_rss_mb()
    start = time.perf_counter()
    result = compute_kerr_scalar_green_diagnostics(
        int(case["l"]),
        int(case["m"]),
        float(case["omega"]),
        a=float(case["a"]),
        N_outer=int(config["N"]),
        N_inner=int(config["N"]),
        r_match=float(config["r_match"]),
        quad_order=int(config["q"]),
        tail_epsrel=1e-11,
        radial_weight_model="kerr-covariant-sigma-dr",
    )
    flux = fixed_incident_flux_coefficients(result)
    elapsed = time.perf_counter() - start
    rss_after = current_rss_mb()
    return {
        "label": case["label"],
        "l": int(case["l"]),
        "m": int(case["m"]),
        "a": f"{float(case['a']):.16e}",
        "omega": f"{float(case['omega']):.16e}",
        "config": config["name"],
        "N": int(config["N"]),
        "quad_order": int(config["q"]),
        "r_match": f"{float(config['r_match']):.16e}",
        "mapping": result.mapping,
        "T0": f"{flux.T0:.16e}",
        "R0": f"{flux.R0:.16e}",
        "linear_balance": f"{flux.linear_balance:.16e}",
        "T1": f"{flux.T1:.16e}",
        "R1": f"{flux.R1:.16e}",
        "nonlinear_balance": f"{flux.nonlinear_balance:.16e}",
        "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
        "rss_before_mb": "" if rss_before is None else f"{rss_before:.6e}",
        "rss_after_mb": "" if rss_after is None else f"{rss_after:.6e}",
        "elapsed_s": f"{elapsed:.6e}",
        "status": result.status,
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for case in CASES:
        case_rows = []
        for config in CONFIGS:
            rss = current_rss_mb()
            suffix = "" if rss is None else f" RSS={rss:.1f} MB"
            print(
                f"Running {case['label']} {config['name']}: "
                f"N={config['N']} q={config['q']} r_m={config['r_match']}{suffix}",
                flush=True,
            )
            row = solve_row(case, config)
            case_rows.append(row)
            print(
                f"  T1={row['T1']} balance={row['nonlinear_balance']} "
                f"Werr={row['wronskian_relative_error']} "
                f"RSS={row['rss_after_mb'] or 'NA'} MB",
                flush=True,
            )
            gc.collect()

        reference = case_rows[0]
        for row in case_rows:
            row["rel_T1_to_reference"] = (
                f"{relative(float(row['T1']), float(reference['T1'])):.16e}"
            )
            row["rel_R1_to_reference"] = (
                f"{relative(float(row['R1']), float(reference['R1'])):.16e}"
            )
        rows.extend(case_rows)

    fields = [
        "label", "l", "m", "a", "omega", "config", "N", "quad_order",
        "r_match", "mapping", "T0", "R0", "linear_balance", "T1", "R1",
        "nonlinear_balance", "wronskian_relative_error",
        "rel_T1_to_reference", "rel_R1_to_reference", "rss_before_mb",
        "rss_after_mb", "elapsed_s", "status",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
