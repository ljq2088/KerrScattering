"""Run prototype Kerr s=0 nonlinear Green-function radial diagnostics."""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_diagnostics.csv")

CASES = [
    {"label": "schwarzschild_l0", "l": 0, "m": 0, "a": 0.0, "omega": 0.1},
    {"label": "kerr_a05_l2m2_sub", "l": 2, "m": 2, "a": 0.5, "omega": 0.24},
    {"label": "kerr_a05_l2m2_super", "l": 2, "m": 2, "a": 0.5, "omega": 0.3},
    {"label": "kerr_a09_l2m2_peak", "l": 2, "m": 2, "a": 0.9, "omega": 0.58},
]
QUAD_ORDERS = [64, 96, 128, 192]


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    for case in CASES:
        previous = None
        for quad_order in QUAD_ORDERS:
            result = compute_kerr_scalar_green_diagnostics(
                case["l"],
                case["m"],
                case["omega"],
                a=case["a"],
                N_outer=128,
                N_inner=128,
                quad_order=quad_order,
            )
            if previous is None:
                rel_A_ref = float("inf")
                rel_A_hor = float("inf")
            else:
                rel_A_ref = rel(result.A_ref_1, previous.A_ref_1)
                rel_A_hor = rel(result.A_hor_1, previous.A_hor_1)
            rows.append({
                "label": case["label"],
                "l": case["l"],
                "m": case["m"],
                "a": f"{case['a']:.16e}",
                "omega": f"{case['omega']:.16e}",
                "quad_order": quad_order,
                "N_outer": result.N_outer,
                "N_inner": result.N_inner,
                "mapping": result.mapping,
                "radial_weight_model": result.radial_weight_model,
                "angular_coupling": fmt_complex(result.angular_coupling),
                "wronskian": fmt_complex(result.wronskian),
                "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                "source_projection_ref": fmt_complex(result.source_projection_ref),
                "source_projection_hor": fmt_complex(result.source_projection_hor),
                "A_ref_1": fmt_complex(result.A_ref_1),
                "A_hor_1": fmt_complex(result.A_hor_1),
                "rel_A_ref_from_previous": f"{rel_A_ref:.16e}",
                "rel_A_hor_from_previous": f"{rel_A_hor:.16e}",
                "status": result.status,
            })
            previous = result

    fields = [
        "label", "l", "m", "a", "omega", "quad_order", "N_outer",
        "N_inner", "mapping", "radial_weight_model", "angular_coupling",
        "wronskian", "wronskian_relative_error", "source_projection_ref",
        "source_projection_hor", "A_ref_1", "A_hor_1",
        "rel_A_ref_from_previous", "rel_A_hor_from_previous", "status",
    ]
    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr scalar nonlinear radial diagnostics")
    for row in rows:
        print(
            f"  {row['label']} q={row['quad_order']}: "
            f"Werr={row['wronskian_relative_error']} "
            f"dAref={row['rel_A_ref_from_previous']} "
            f"dAhor={row['rel_A_hor_from_previous']}"
        )
    print(f"  saved = {OUT}")


if __name__ == "__main__":
    main()
