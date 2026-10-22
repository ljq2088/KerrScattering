"""Run bounded convergence checks at representative high-frequency points."""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_kerr_scalar_nonlinear_diagnostics import current_rss_mb
from scripts.run_prd_axisymmetric_production_convergence import rel, row_from_result
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_axisymmetric_tail_convergence.csv"
CASES = (
    {"label": "axisym_l0_tail", "l": 0, "m": 0, "a": 0.5, "omega": 0.52, "r_match": 40.0},
    {"label": "axisym_l1_tail", "l": 1, "m": 0, "a": 0.5, "omega": 0.77, "r_match": 40.0},
    {"label": "axisym_l2_tail", "l": 2, "m": 0, "a": 0.5, "omega": 0.92, "r_match": 40.0},
)
CONFIGS = (
    ("reference", 240, 2048),
    ("q1792", 240, 1792),
    ("q1536", 240, 1536),
    ("N_lower", 224, 2048),
)
MAX_RSS_MB = 1500.0


def main() -> None:
    rows = []
    for case in CASES:
        by_config = {}
        case_rows = []
        for config, n, q in CONFIGS:
            rss_before = current_rss_mb()
            if rss_before is not None and rss_before > MAX_RSS_MB:
                raise MemoryError(
                    f"RSS {rss_before:.1f} MB exceeds {MAX_RSS_MB:.1f} MB"
                )
            start = time.perf_counter()
            print(f"Running {case['label']} {config}: N={n} q={q}")
            result = compute_kerr_scalar_green_diagnostics(
                case["l"],
                case["m"],
                case["omega"],
                a=case["a"],
                N_outer=n,
                N_inner=n,
                r_match=case["r_match"],
                quad_order=q,
                tail_epsrel=1e-11,
                radial_weight_model="kerr-covariant-sigma-dr",
            )
            elapsed = time.perf_counter() - start
            rss_after = current_rss_mb()
            row = row_from_result(
                case, config, n, q, result, elapsed, rss_before, rss_after
            )
            by_config[config] = row
            case_rows.append(row)
            print(
                f"  T1={row['T1']} balance={row['nonlinear_balance']} "
                f"RSS={row['rss_after_mb'] or 'NA'} MB"
            )

        reference = by_config["reference"]
        for row in case_rows:
            row["rel_A_ref_to_reference"] = (
                f"{rel(complex(row['A_ref_1']), complex(reference['A_ref_1'])):.16e}"
            )
            row["rel_A_hor_to_reference"] = (
                f"{rel(complex(row['A_hor_1']), complex(reference['A_hor_1'])):.16e}"
            )
            row["rel_T1_to_reference"] = (
                f"{rel(float(row['T1']), float(reference['T1'])):.16e}"
            )
            row["rel_R1_to_reference"] = (
                f"{rel(float(row['R1']), float(reference['R1'])):.16e}"
            )
        rows.extend(case_rows)

    fields = [
        "label", "l", "m", "a", "omega", "config", "N", "quad_order",
        "r_match", "B_inc", "B_ref", "A_ref_1", "A_hor_1", "T0", "R0",
        "linear_balance", "T1", "R1", "nonlinear_balance",
        "wronskian_relative_error", "rel_A_ref_to_reference",
        "rel_A_hor_to_reference", "rel_T1_to_reference",
        "rel_R1_to_reference", "rss_before_mb", "rss_after_mb", "elapsed_s",
        "status",
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
