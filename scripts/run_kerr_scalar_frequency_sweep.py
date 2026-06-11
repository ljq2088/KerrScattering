"""Frequency sweeps for publication-style Kerr s=0 scattering curves."""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral
from src.teukolsky_scalar import KerrParams


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_frequency_sweep.csv")

ORDERS = [96, 128, 160, 192, 224]
SELF_TOL = 1e-7
FLUX_TOL = 1e-8
R_ABS_TOL = 1e-10

CASES = [
    {
        "label": "schwarzschild_l0",
        "a": 0.0,
        "l": 0,
        "m": 0,
        "omegas": [0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.5, 0.8, 1.0],
    },
    {
        "label": "kerr_a05_l2m2",
        "a": 0.5,
        "l": 2,
        "m": 2,
        "omegas": [
            0.01, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.24,
            0.26, 0.275, 0.3, 0.4, 0.6, 0.8, 1.0,
        ],
    },
    {
        "label": "kerr_a09_l2m2",
        "a": 0.9,
        "l": 2,
        "m": 2,
        "omegas": [
            0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4,
            0.5, 0.58, 0.62, 0.65, 0.75, 0.9, 1.1,
        ],
    },
]


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def rel_abs(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def adaptive_solve(l, m, omega, a):
    previous = None
    best = None
    for N in ORDERS:
        result = solve_scalar_in_mode_spectral(
            l,
            m,
            omega,
            a=a,
            N_outer=N,
            N_inner=N,
        )
        if previous is None:
            self_inc = float("inf")
            self_ref = float("inf")
            self_R = float("inf")
            self_T = float("inf")
        else:
            self_inc = rel_abs(abs(result.B_inc), abs(previous.B_inc))
            self_ref = rel_abs(abs(result.B_ref), abs(previous.B_ref))
            self_R = abs(result.reflection - previous.reflection)
            self_T = abs(result.transmission - previous.transmission)

        ref_score = min(self_ref, self_R)
        score = max(self_inc, ref_score, result.flux_balance_error)
        current = {
            "result": result,
            "self_rel_abs_B_inc": self_inc,
            "self_rel_abs_B_ref": self_ref,
            "self_abs_R": self_R,
            "self_abs_T": self_T,
            "score": score,
        }
        ref_ok = self_ref <= SELF_TOL or self_R <= R_ABS_TOL
        if best is None or score < best["score"]:
            best = current
        if (
            previous is not None
            and self_inc <= SELF_TOL
            and ref_ok
            and result.flux_balance_error <= FLUX_TOL
        ):
            return current
        previous = result
    return best


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fields = [
        "label", "l", "m", "a", "omega", "omega_h", "m_omega_h",
        "p_horizon", "superradiant", "N", "r_match", "mapping",
        "B_inc", "B_ref", "abs_B_inc", "abs_B_ref",
        "reflection_amplitude", "R", "T", "amplification",
        "flux_balance_error", "self_rel_abs_B_inc", "self_rel_abs_B_ref",
        "self_abs_R", "self_abs_T", "score", "passed",
        "cond_outer_down", "cond_outer_up", "cond_inner",
    ]

    rows = []
    for case in CASES:
        params = KerrParams(M=1.0, a=case["a"])
        for omega in case["omegas"]:
            solved = adaptive_solve(case["l"], case["m"], omega, case["a"])
            result = solved["result"]
            passed = (
                solved["self_rel_abs_B_inc"] <= SELF_TOL
                and (
                    solved["self_rel_abs_B_ref"] <= SELF_TOL
                    or solved["self_abs_R"] <= R_ABS_TOL
                )
                and result.flux_balance_error <= FLUX_TOL
            )
            rows.append({
                "label": case["label"],
                "l": case["l"],
                "m": case["m"],
                "a": f"{case['a']:.16e}",
                "omega": f"{omega:.16e}",
                "omega_h": f"{params.omega_h:.16e}",
                "m_omega_h": f"{case['m'] * params.omega_h:.16e}",
                "p_horizon": f"{result.p_horizon:.16e}",
                "superradiant": "true" if result.p_horizon < 0 else "false",
                "N": result.N_outer,
                "r_match": f"{result.r_match:.16e}",
                "mapping": result.mapping,
                "B_inc": fmt_complex(result.B_inc),
                "B_ref": fmt_complex(result.B_ref),
                "abs_B_inc": f"{abs(result.B_inc):.16e}",
                "abs_B_ref": f"{abs(result.B_ref):.16e}",
                "reflection_amplitude": fmt_complex(result.reflection_amplitude),
                "R": f"{result.reflection:.16e}",
                "T": f"{result.transmission:.16e}",
                "amplification": f"{result.reflection - 1.0:.16e}",
                "flux_balance_error": f"{result.flux_balance_error:.16e}",
                "self_rel_abs_B_inc": f"{solved['self_rel_abs_B_inc']:.16e}",
                "self_rel_abs_B_ref": f"{solved['self_rel_abs_B_ref']:.16e}",
                "self_abs_R": f"{solved['self_abs_R']:.16e}",
                "self_abs_T": f"{solved['self_abs_T']:.16e}",
                "score": f"{solved['score']:.16e}",
                "passed": "true" if passed else "false",
                "cond_outer_down": f"{result.outer_down_condition:.16e}",
                "cond_outer_up": f"{result.outer_up_condition:.16e}",
                "cond_inner": f"{result.inner_condition:.16e}",
            })

    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr s=0 frequency sweep")
    for row in rows:
        print(
            f"  {row['label']} omega={row['omega']}: R={row['R']} "
            f"T={row['T']} score={row['score']} passed={row['passed']}"
        )
    print(f"  saved = {OUT}")


if __name__ == "__main__":
    main()
