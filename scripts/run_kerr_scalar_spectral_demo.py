"""Compare scalar Kerr spectral matching against direct radial IVP output.

The IVP comparison uses the leading large-r form at one finite radius, so its
complex phase is a lower-quality benchmark than the amplitude magnitudes.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral
from src.teukolsky_scalar import solve_scalar_in_mode


def _fmt_complex(z):
    return f"{z.real:.15e}{z.imag:+.15e}j"


def main():
    cases = [
        {"l": 0, "m": 0, "omega": 0.1, "a": 0.5, "N": 96},
        {"l": 1, "m": 1, "omega": 0.1, "a": 0.5, "N": 112},
        {"l": 2, "m": 1, "omega": 0.3, "a": 0.5, "N": 112},
    ]

    os.makedirs("results", exist_ok=True)
    out = "results/kerr_scalar_spectral_demo.csv"
    fields = [
        "l", "m", "a", "omega", "lambda", "r_match", "N",
        "B_inc_spectral", "B_ref_spectral", "ratio_spectral",
        "B_inc_ivp", "B_ref_ivp", "ratio_ivp",
        "rel_err_ratio", "rel_err_abs_Binc", "rel_err_abs_Bref",
        "T_spectral", "R_spectral", "flux_balance_error",
        "cond_outer_down", "cond_outer_up", "cond_inner",
    ]

    rows = []
    for case in cases:
        spec = solve_scalar_in_mode_spectral(
            case["l"], case["m"], case["omega"], M=1.0, a=case["a"],
            N_outer=case["N"], N_inner=case["N"],
        )
        ivp = solve_scalar_in_mode(
            case["l"], case["m"], case["omega"], M=1.0, a=case["a"],
            r_out=max(500.0, 100.0 / case["omega"]),
            radial_lambda=spec.radial_lambda,
            rtol=1e-10,
            atol=1e-12,
        )
        ratio_ivp = ivp["reflection_amplitude"]
        ratio_spec = spec.reflection_amplitude
        rel_ratio = abs(ratio_spec - ratio_ivp) / max(abs(ratio_ivp), 1e-300)
        rel_binc = abs(abs(spec.B_inc) - abs(ivp["Z_in"])) / max(abs(ivp["Z_in"]), 1e-300)
        rel_bref = abs(abs(spec.B_ref) - abs(ivp["Z_out"])) / max(abs(ivp["Z_out"]), 1e-300)

        rows.append({
            "l": case["l"],
            "m": case["m"],
            "a": case["a"],
            "omega": case["omega"],
            "lambda": f"{spec.radial_lambda:.15e}",
            "r_match": f"{spec.r_match:.15e}",
            "N": case["N"],
            "B_inc_spectral": _fmt_complex(spec.B_inc),
            "B_ref_spectral": _fmt_complex(spec.B_ref),
            "ratio_spectral": _fmt_complex(ratio_spec),
            "B_inc_ivp": _fmt_complex(ivp["Z_in"]),
            "B_ref_ivp": _fmt_complex(ivp["Z_out"]),
            "ratio_ivp": _fmt_complex(ratio_ivp),
            "rel_err_ratio": f"{rel_ratio:.15e}",
            "rel_err_abs_Binc": f"{rel_binc:.15e}",
            "rel_err_abs_Bref": f"{rel_bref:.15e}",
            "T_spectral": f"{spec.transmission:.15e}",
            "R_spectral": f"{spec.reflection:.15e}",
            "flux_balance_error": f"{spec.flux_balance_error:.15e}",
            "cond_outer_down": f"{spec.outer_down_condition:.15e}",
            "cond_outer_up": f"{spec.outer_up_condition:.15e}",
            "cond_inner": f"{spec.inner_condition:.15e}",
        })

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Scalar Kerr spectral demo")
    for row in rows:
        print(
            f"  l={row['l']} m={row['m']} a={row['a']} omega={row['omega']}: "
            f"rel_err_abs_Binc={row['rel_err_abs_Binc']} "
            f"rel_err_abs_Bref={row['rel_err_abs_Bref']} "
            f"rel_err_ratio={row['rel_err_ratio']} "
            f"flux_balance_error={row['flux_balance_error']}"
        )
    print(f"  saved = {out}")


if __name__ == "__main__":
    main()
