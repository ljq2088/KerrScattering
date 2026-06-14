"""Run control scans for Kerr s=0 nonlinear source amplitudes."""

import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_kerr_scalar_nonlinear_diagnostics import CASES, current_rss_mb
from src.kerr_scalar_nonlinear import compute_kerr_scalar_green_diagnostics


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "kerr_scalar_nonlinear_control_scan.csv")

N_VALUES = [256, 224, 288]
R_MATCH_VALUES = {
    "schwarzschild_l0": [30.0, 25.0, 35.0],
    "kerr_a05_l2m2_sub": [40.0, 35.0, 45.0],
    "kerr_a05_l2m2_super": [40.0, 35.0, 45.0],
    "kerr_a09_l2m2_peak": [16.0, 12.0, 20.0],
}


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def main():
    rows = []
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    for case in CASES:
        label = case["label"]
        base_n = 256
        base_r = float(case["r_match"])
        base = None
        configs = []
        for n in N_VALUES:
            configs.append(("N_scan", n, n, base_r))
        for r_match in R_MATCH_VALUES[label]:
            configs.append(("r_match_scan", base_n, base_n, r_match))

        seen = set()
        for scan, n_outer, n_inner, r_match in configs:
            key = (scan, n_outer, n_inner, r_match)
            if key in seen:
                continue
            seen.add(key)
            start = time.perf_counter()
            rss_before = current_rss_mb()
            result = compute_kerr_scalar_green_diagnostics(
                case["l"],
                case["m"],
                case["omega"],
                a=case["a"],
                N_outer=n_outer,
                N_inner=n_inner,
                r_match=r_match,
                quad_order=96,
                radial_weight_model="kerr-covariant-sigma-dr",
            )
            elapsed_s = time.perf_counter() - start
            rss_after = current_rss_mb()
            if n_outer == base_n and n_inner == base_n and r_match == base_r:
                base = result
            ref_rel = "" if base is None else f"{rel(result.A_ref_1, base.A_ref_1):.16e}"
            hor_rel = "" if base is None else f"{rel(result.A_hor_1, base.A_hor_1):.16e}"
            rows.append({
                "label": label,
                "scan": scan,
                "l": case["l"],
                "m": case["m"],
                "a": f"{case['a']:.16e}",
                "omega": f"{case['omega']:.16e}",
                "N_outer": n_outer,
                "N_inner": n_inner,
                "r_match": f"{r_match:.16e}",
                "quad_order": 96,
                "A_ref_1": fmt_complex(result.A_ref_1),
                "A_hor_1": fmt_complex(result.A_hor_1),
                "abs_A_ref_1": f"{abs(result.A_ref_1):.16e}",
                "abs_A_hor_1": f"{abs(result.A_hor_1):.16e}",
                "rel_A_ref_to_base": ref_rel,
                "rel_A_hor_to_base": hor_rel,
                "wronskian_relative_error": f"{result.wronskian_relative_error:.16e}",
                "elapsed_s": f"{elapsed_s:.6e}",
                "rss_mb_before": "" if rss_before is None else f"{rss_before:.6e}",
                "rss_mb_after": "" if rss_after is None else f"{rss_after:.6e}",
                "status": result.status,
            })
            print(
                f"{label} {scan} N={n_outer} r_match={r_match:g}: "
                f"dref={ref_rel or 'base-pending'} dhor={hor_rel or 'base-pending'}"
            )

    fields = [
        "label", "scan", "l", "m", "a", "omega", "N_outer", "N_inner",
        "r_match", "quad_order", "A_ref_1", "A_hor_1", "abs_A_ref_1",
        "abs_A_hor_1", "rel_A_ref_to_base", "rel_A_hor_to_base",
        "wronskian_relative_error", "elapsed_s", "rss_mb_before",
        "rss_mb_after", "status",
    ]
    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"saved = {OUT}")


if __name__ == "__main__":
    main()
