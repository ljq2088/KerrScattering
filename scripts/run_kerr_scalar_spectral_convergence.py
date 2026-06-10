"""Convergence scan for the scalar Kerr two-domain spectral solver."""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral


def _fmt_complex(z):
    return f"{z.real:.15e}{z.imag:+.15e}j"


def main():
    case = {"l": 0, "m": 0, "omega": 0.1, "M": 1.0, "a": 0.5}
    orders = [48, 64, 80, 96, 112, 128]

    os.makedirs("results", exist_ok=True)
    out = "results/kerr_scalar_spectral_convergence.csv"
    fields = [
        "N", "B_inc", "B_ref", "abs_B_inc", "abs_B_ref",
        "T", "R", "flux_balance_error",
        "cond_outer_down", "cond_outer_up", "cond_inner",
    ]

    rows = []
    for N in orders:
        result = solve_scalar_in_mode_spectral(
            case["l"],
            case["m"],
            case["omega"],
            M=case["M"],
            a=case["a"],
            N_outer=N,
            N_inner=N,
        )
        rows.append({
            "N": N,
            "B_inc": _fmt_complex(result.B_inc),
            "B_ref": _fmt_complex(result.B_ref),
            "abs_B_inc": f"{abs(result.B_inc):.15e}",
            "abs_B_ref": f"{abs(result.B_ref):.15e}",
            "T": f"{result.transmission:.15e}",
            "R": f"{result.reflection:.15e}",
            "flux_balance_error": f"{result.flux_balance_error:.15e}",
            "cond_outer_down": f"{result.outer_down_condition:.15e}",
            "cond_outer_up": f"{result.outer_up_condition:.15e}",
            "cond_inner": f"{result.inner_condition:.15e}",
        })

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Scalar Kerr spectral convergence")
    print(
        f"  case: l={case['l']} m={case['m']} a={case['a']} "
        f"omega={case['omega']}"
    )
    for row in rows:
        print(
            f"  N={row['N']}: |Binc|={row['abs_B_inc']} "
            f"|Bref|={row['abs_B_ref']} "
            f"flux_balance_error={row['flux_balance_error']}"
        )
    print(f"  saved = {out}")


if __name__ == "__main__":
    main()
