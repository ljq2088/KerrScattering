"""Adaptive Kerr s=0 spectral validation against GSN.

For each GSN benchmark case this script scans spectral order and matching
radius. It reports the best convention-invariant amplitude-magnitude errors
and the corresponding flux-balance residual.
"""

import csv
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kerr_scalar_spectral import solve_scalar_in_mode_spectral


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GSN_IN = os.path.join(ROOT, "results", "kerr_scalar_gsn_benchmark.csv")
DETAIL_OUT = os.path.join(ROOT, "results", "kerr_scalar_adaptive_scan.csv")
SUMMARY_OUT = os.path.join(ROOT, "results", "kerr_scalar_adaptive_summary.csv")

ORDERS = [64, 80, 96, 112, 128, 160, 192, 224]
REL_TOL = 1e-7
FLUX_TOL = 1e-8


def parse_complex(text):
    return complex(text.replace("im", "j"))


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def rel_abs(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def default_r_match(omega):
    w = abs(omega)
    if w >= 0.5:
        return 12.0
    if w >= 0.05:
        return 30.0
    return max(30.0, 3.0 + 1.0 / math.sqrt(w))


def r_match_candidates(omega, r_plus):
    base = default_r_match(omega)
    raw = [base, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 40.0]
    if abs(omega) < 0.05:
        raw.extend([50.0, 60.0])
    return sorted({r for r in raw if r > 1.05 * r_plus})


def score(row):
    return max(row["rel_abs_B_inc"], row["rel_abs_B_ref"], row["flux_balance_error"])


def main():
    if not os.path.exists(GSN_IN):
        raise FileNotFoundError(
            f"{GSN_IN} not found. Run scripts/run_kerr_scalar_gsn_benchmark.jl first."
        )

    details = []
    summaries = []
    with open(GSN_IN, newline="") as f:
        for bench in csv.DictReader(f):
            if bench["status"] != "ok" or int(bench["s"]) != 0:
                continue

            l = int(bench["l"])
            m = int(bench["m"])
            a = float(bench["a"])
            omega = float(bench["omega"])
            lam = float(bench["lambda"])
            g_inc = parse_complex(bench["incidence_amplitude"])
            g_ref = parse_complex(bench["reflection_amplitude"])

            best = None
            # One cheap call gets r_plus and default radius diagnostics.
            probe = solve_scalar_in_mode_spectral(
                l, m, omega, a=a, radial_lambda=lam, N_outer=32, N_inner=32
            )
            for r_match in r_match_candidates(omega, probe.r_plus):
                for N in ORDERS:
                    try:
                        result = solve_scalar_in_mode_spectral(
                            l,
                            m,
                            omega,
                            a=a,
                            radial_lambda=lam,
                            N_outer=N,
                            N_inner=N,
                            r_match=r_match,
                        )
                        rel_inc = rel_abs(abs(result.B_inc), abs(g_inc))
                        rel_ref = rel_abs(abs(result.B_ref), abs(g_ref))
                        rel_complex_inc = rel_abs(result.B_inc, g_inc)
                        rel_complex_ref = rel_abs(result.B_ref, g_ref)
                        row = {
                            "s": 0,
                            "l": l,
                            "m": m,
                            "a": a,
                            "omega": omega,
                            "lambda_gsn": lam,
                            "N": N,
                            "r_match": result.r_match,
                            "mapping": result.mapping,
                            "rel_abs_B_inc": rel_inc,
                            "rel_abs_B_ref": rel_ref,
                            "rel_complex_B_inc": rel_complex_inc,
                            "rel_complex_B_ref": rel_complex_ref,
                            "flux_balance_error": result.flux_balance_error,
                            "score": max(rel_inc, rel_ref, result.flux_balance_error),
                            "B_inc_spectral": result.B_inc,
                            "B_ref_spectral": result.B_ref,
                            "B_inc_gsn": g_inc,
                            "B_ref_gsn": g_ref,
                            "T_spectral": result.transmission,
                            "R_spectral": result.reflection,
                            "cond_outer_down": result.outer_down_condition,
                            "cond_outer_up": result.outer_up_condition,
                            "cond_inner": result.inner_condition,
                            "status": "ok",
                        }
                    except Exception as exc:
                        row = {
                            "s": 0,
                            "l": l,
                            "m": m,
                            "a": a,
                            "omega": omega,
                            "lambda_gsn": lam,
                            "N": N,
                            "r_match": r_match,
                            "mapping": "failed",
                            "rel_abs_B_inc": float("inf"),
                            "rel_abs_B_ref": float("inf"),
                            "rel_complex_B_inc": float("inf"),
                            "rel_complex_B_ref": float("inf"),
                            "flux_balance_error": float("inf"),
                            "score": float("inf"),
                            "B_inc_spectral": 0j,
                            "B_ref_spectral": 0j,
                            "B_inc_gsn": g_inc,
                            "B_ref_gsn": g_ref,
                            "T_spectral": float("nan"),
                            "R_spectral": float("nan"),
                            "cond_outer_down": float("inf"),
                            "cond_outer_up": float("inf"),
                            "cond_inner": float("inf"),
                            "status": f"failed: {exc}",
                        }
                    details.append(row)
                    if row["status"] == "ok" and (best is None or score(row) < score(best)):
                        best = row

            if best is None:
                summaries.append({
                    "s": 0, "l": l, "m": m, "a": a, "omega": omega,
                    "status": "failed", "passed": "false",
                })
            else:
                passed = (
                    best["rel_abs_B_inc"] <= REL_TOL
                    and best["rel_abs_B_ref"] <= REL_TOL
                    and best["flux_balance_error"] <= FLUX_TOL
                )
                summary = dict(best)
                summary["passed"] = "true" if passed else "false"
                summaries.append(summary)

    os.makedirs(os.path.dirname(DETAIL_OUT), exist_ok=True)
    detail_fields = [
        "s", "l", "m", "a", "omega", "lambda_gsn", "N", "r_match", "mapping",
        "rel_abs_B_inc", "rel_abs_B_ref", "rel_complex_B_inc", "rel_complex_B_ref",
        "flux_balance_error", "score", "B_inc_spectral", "B_ref_spectral",
        "B_inc_gsn", "B_ref_gsn", "T_spectral", "R_spectral",
        "cond_outer_down", "cond_outer_up", "cond_inner", "status",
    ]
    with open(DETAIL_OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=detail_fields)
        writer.writeheader()
        for row in details:
            out = dict(row)
            for key in ["B_inc_spectral", "B_ref_spectral", "B_inc_gsn", "B_ref_gsn"]:
                out[key] = fmt_complex(out[key])
            writer.writerow(out)

    summary_fields = detail_fields + ["passed"]
    with open(SUMMARY_OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields)
        writer.writeheader()
        for row in summaries:
            out = {key: row.get(key, "") for key in summary_fields}
            for key in ["B_inc_spectral", "B_ref_spectral", "B_inc_gsn", "B_ref_gsn"]:
                if key in out and out[key] != "":
                    out[key] = fmt_complex(out[key])
            writer.writerow(out)

    print("Adaptive Kerr s=0 GSN validation")
    for row in summaries:
        print(
            f"  l={row.get('l')} m={row.get('m')} a={row.get('a')} "
            f"omega={row.get('omega')}: passed={row.get('passed')} "
            f"N={row.get('N')} r_match={row.get('r_match')} "
            f"score={row.get('score')}"
        )
    print(f"  detail  = {DETAIL_OUT}")
    print(f"  summary = {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
