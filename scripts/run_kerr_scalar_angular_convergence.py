"""Audit spheroidal-basis and angular-quadrature convergence for the PRD draft."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.teukolsky_scalar import (
    scalar_cubic_coupling,
    scalar_cubic_coupling_cos2,
    teukolsky_lambda_s0,
)


OUTPUT = ROOT / "results" / "kerr_scalar_angular_convergence.csv"

CASES = [
    {
        "case": "axisym_l2_tail",
        "l_source": 2,
        "l_target": 2,
        "m": 0,
        "a": 0.5,
        "omega": 1.0,
    },
    {
        "case": "m2_target_l6",
        "l_source": 2,
        "l_target": 6,
        "m": 2,
        "a": 0.5,
        "omega": 0.30,
    },
]

CONFIGS = [
    ("reference", 24, 512),
    ("active", 16, 256),
    ("basis_lower", 12, 512),
    ("quadrature_lower", 24, 128),
]

FIELDS = [
    "case",
    "l_source",
    "l_target",
    "m",
    "a",
    "omega",
    "config",
    "lmax_extra",
    "angular_quad_order",
    "lambda_source",
    "lambda_target",
    "C0",
    "C2",
    "rel_lambda_source_to_reference",
    "rel_lambda_target_to_reference",
    "max_rel_lambda_to_reference",
    "rel_C0_to_reference",
    "rel_C2_to_reference",
]


def relative_change(value: complex, reference: complex) -> float:
    return float(abs(value - reference) / max(abs(reference), 1.0e-300))


def evaluate(case: dict[str, float | int | str], lmax_extra: int, quad_order: int):
    l_source = int(case["l_source"])
    l_target = int(case["l_target"])
    m = int(case["m"])
    a = float(case["a"])
    omega = float(case["omega"])
    return {
        "lambda_source": teukolsky_lambda_s0(
            l_source, m, a, omega, lmax_extra=lmax_extra
        ),
        "lambda_target": teukolsky_lambda_s0(
            l_target, m, a, omega, lmax_extra=lmax_extra
        ),
        "C0": scalar_cubic_coupling(
            l_source,
            m,
            a,
            omega,
            l_target=l_target,
            lmax_extra=lmax_extra,
            quad_order=quad_order,
        ),
        "C2": scalar_cubic_coupling_cos2(
            l_source,
            m,
            a,
            omega,
            l_target=l_target,
            lmax_extra=lmax_extra,
            quad_order=quad_order,
        ),
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for case in CASES:
        evaluated = {
            label: evaluate(case, lmax_extra, quad_order)
            for label, lmax_extra, quad_order in CONFIGS
        }
        reference = evaluated["reference"]
        for label, lmax_extra, quad_order in CONFIGS:
            values = evaluated[label]
            rel_lambda_source = relative_change(
                values["lambda_source"], reference["lambda_source"]
            )
            rel_lambda_target = relative_change(
                values["lambda_target"], reference["lambda_target"]
            )
            row = {
                **case,
                "config": label,
                "lmax_extra": lmax_extra,
                "angular_quad_order": quad_order,
                "lambda_source": f"{values['lambda_source']:.16e}",
                "lambda_target": f"{values['lambda_target']:.16e}",
                "C0": f"{complex(values['C0']).real:.16e}{complex(values['C0']).imag:+.16e}j",
                "C2": f"{complex(values['C2']).real:.16e}{complex(values['C2']).imag:+.16e}j",
                "rel_lambda_source_to_reference": f"{rel_lambda_source:.16e}",
                "rel_lambda_target_to_reference": f"{rel_lambda_target:.16e}",
                "max_rel_lambda_to_reference": f"{max(rel_lambda_source, rel_lambda_target):.16e}",
                "rel_C0_to_reference": f"{relative_change(values['C0'], reference['C0']):.16e}",
                "rel_C2_to_reference": f"{relative_change(values['C2'], reference['C2']):.16e}",
            }
            rows.append(row)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
