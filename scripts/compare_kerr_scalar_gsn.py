"""Compare the Kerr s=0 spectral solver with GSN Teukolsky amplitudes.

The complex amplitudes depend on the additive constant used in the tortoise
coordinate and on package-specific phase conventions. The amplitude magnitudes
and flux balance are the convention-invariant benchmark quantities.
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral
from src.teukolsky_scalar import teukolsky_lambda_s0


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GSN_IN = os.path.join(ROOT, "results", "kerr_scalar_gsn_benchmark.csv")
OUT = os.path.join(ROOT, "results", "kerr_scalar_spectral_vs_gsn.csv")


def parse_complex(text):
    return complex(text.replace("im", "j"))


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def rel_abs(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def main():
    if not os.path.exists(GSN_IN):
        raise FileNotFoundError(
            f"{GSN_IN} not found. Run scripts/run_kerr_scalar_gsn_benchmark.jl first."
        )

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fields = [
        "s", "l", "m", "a", "omega", "N", "r_match", "mapping",
        "kappa_outer", "kappa_inner",
        "lambda_gsn", "lambda_local", "lambda_abs_error",
        "B_inc_spectral", "B_ref_spectral",
        "B_inc_gsn", "B_ref_gsn",
        "rel_abs_B_inc", "rel_abs_B_ref",
        "rel_complex_B_inc", "rel_complex_B_ref",
        "phase_factor_B_inc", "phase_factor_B_ref",
        "T_spectral", "R_spectral", "flux_balance_error",
        "cond_outer_down", "cond_outer_up", "cond_inner", "status",
    ]

    rows = []
    with open(GSN_IN, newline="") as f:
        for row in csv.DictReader(f):
            if row["status"] != "ok":
                continue
            s = int(row["s"])
            if s != 0:
                continue
            l = int(row["l"])
            m = int(row["m"])
            a = float(row["a"])
            omega = float(row["omega"])
            lam_gsn = float(row["lambda"])
            g_inc = parse_complex(row["incidence_amplitude"])
            g_ref = parse_complex(row["reflection_amplitude"])

            result = solve_scalar_in_mode_spectral(
                l,
                m,
                omega,
                a=a,
                N_outer=128,
                N_inner=128,
                radial_lambda=lam_gsn,
            )
            lam_local = teukolsky_lambda_s0(l, m, a, omega)

            rows.append({
                "s": s,
                "l": l,
                "m": m,
                "a": f"{a:.16e}",
                "omega": f"{omega:.16e}",
                "N": result.N_outer,
                "r_match": f"{result.r_match:.16e}",
                "mapping": result.mapping,
                "kappa_outer": f"{result.kappa_outer:.16e}",
                "kappa_inner": f"{result.kappa_inner:.16e}",
                "lambda_gsn": f"{lam_gsn:.16e}",
                "lambda_local": f"{lam_local:.16e}",
                "lambda_abs_error": f"{abs(lam_local - lam_gsn):.16e}",
                "B_inc_spectral": fmt_complex(result.B_inc),
                "B_ref_spectral": fmt_complex(result.B_ref),
                "B_inc_gsn": fmt_complex(g_inc),
                "B_ref_gsn": fmt_complex(g_ref),
                "rel_abs_B_inc": f"{rel_abs(abs(result.B_inc), abs(g_inc)):.16e}",
                "rel_abs_B_ref": f"{rel_abs(abs(result.B_ref), abs(g_ref)):.16e}",
                "rel_complex_B_inc": f"{rel_abs(result.B_inc, g_inc):.16e}",
                "rel_complex_B_ref": f"{rel_abs(result.B_ref, g_ref):.16e}",
                "phase_factor_B_inc": fmt_complex(result.B_inc / g_inc),
                "phase_factor_B_ref": fmt_complex(result.B_ref / g_ref),
                "T_spectral": f"{result.transmission:.16e}",
                "R_spectral": f"{result.reflection:.16e}",
                "flux_balance_error": f"{result.flux_balance_error:.16e}",
                "cond_outer_down": f"{result.outer_down_condition:.16e}",
                "cond_outer_up": f"{result.outer_up_condition:.16e}",
                "cond_inner": f"{result.inner_condition:.16e}",
                "status": result.status,
            })

    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr s=0 spectral vs GSN")
    for row in rows:
        print(
            f"  l={row['l']} m={row['m']} omega={row['omega']}: "
            f"rel_abs_Binc={row['rel_abs_B_inc']} "
            f"rel_abs_Bref={row['rel_abs_B_ref']} "
            f"flux={row['flux_balance_error']} "
            f"r_match={row['r_match']} mapping={row['mapping']}"
        )
    print(f"  saved = {OUT}")


if __name__ == "__main__":
    main()
