"""Build the compact convergence table used by the PRD manuscript.

The source scans are kept in the larger diagnostic CSV files.  This script
reduces them to one row per stress-test case and records the largest relative
change in the Green-function amplitudes for spectral order, matching radius,
and quadrature-order variations.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "results" / "kerr_scalar_nonlinear_control_scan.csv"
DIAGNOSTICS = ROOT / "results" / "kerr_scalar_nonlinear_diagnostics.csv"
OUTPUT = ROOT / "results" / "kerr_scalar_nonlinear_convergence_summary.csv"

CASES = (
    "kerr_a05_l2m2_sub",
    "kerr_a05_l2m2_super",
    "kerr_a09_l2m2_peak",
)


def complex_value(row: dict[str, str], key: str) -> complex:
    return complex(row[key])


def rel_change(row: dict[str, str], ref: dict[str, str], key: str) -> float:
    return abs(complex_value(row, key) - complex_value(ref, key)) / abs(complex_value(ref, key))


def max_pair(rows: list[dict[str, str]], ref: dict[str, str]) -> tuple[float, float]:
    return (
        max(rel_change(row, ref, "A_ref_1") for row in rows),
        max(rel_change(row, ref, "A_hor_1") for row in rows),
    )


def build_rows() -> list[dict[str, str]]:
    with CONTROL.open(newline="", encoding="utf-8") as handle:
        control = list(csv.DictReader(handle))
    with DIAGNOSTICS.open(newline="", encoding="utf-8") as handle:
        diagnostics = list(csv.DictReader(handle))

    output: list[dict[str, str]] = []
    for label in CASES:
        crows = [row for row in control if row["label"] == label]
        base_n = next(row for row in crows if row["scan"] == "N_scan" and row["N_outer"] == "256")
        n_rows = [row for row in crows if row["scan"] == "N_scan" and row["N_outer"] != "256"]
        r_rows = [row for row in crows if row["scan"] == "r_match_scan" and row["r_match"] != base_n["r_match"]]
        n_ref = dict(base_n)
        r_ref = dict(base_n)
        n_ref.update({"A_ref_1": base_n["A_ref_1"], "A_hor_1": base_n["A_hor_1"]})
        r_ref.update({"A_ref_1": base_n["A_ref_1"], "A_hor_1": base_n["A_hor_1"]})
        n_ref_change = max_pair(n_rows, n_ref)
        r_ref_change = max_pair(r_rows, r_ref)

        qrows = [row for row in diagnostics if row["label"] == label]
        q_ref = max(qrows, key=lambda row: int(row["quad_order"]))
        q_rows = [row for row in qrows if row["quad_order"] != q_ref["quad_order"]]
        q_ref_change = max_pair(q_rows, q_ref)

        output.append(
            {
                "case": label,
                "N_reference": base_n["N_outer"],
                "N_test_max_relative_A_ref": f"{n_ref_change[0]:.12e}",
                "N_test_max_relative_A_H": f"{n_ref_change[1]:.12e}",
                "r_match_reference": base_n["r_match"],
                "r_match_test_max_relative_A_ref": f"{r_ref_change[0]:.12e}",
                "r_match_test_max_relative_A_H": f"{r_ref_change[1]:.12e}",
                "quad_reference": q_ref["quad_order"],
                "quad_test_max_relative_A_ref": f"{q_ref_change[0]:.12e}",
                "quad_test_max_relative_A_H": f"{q_ref_change[1]:.12e}",
                "max_Wronskian_relative_error": f"{max(float(row['wronskian_relative_error']) for row in crows + qrows):.12e}",
            }
        )
    return output


def main() -> None:
    rows = build_rows()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        fields = list(rows[0])
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
