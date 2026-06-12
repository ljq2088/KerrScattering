"""Compute scalar spheroidal cubic source projection coefficients."""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.teukolsky_scalar import scalar_cubic_coupling


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMARY = os.path.join(ROOT, "results", "kerr_scalar_adaptive_summary.csv")
OUT = os.path.join(ROOT, "results", "kerr_scalar_cubic_couplings.csv")


def main():
    if not os.path.exists(SUMMARY):
        raise FileNotFoundError(
            f"{SUMMARY} not found. Run scripts/adaptive_kerr_scalar_gsn_validation.py first."
        )

    with open(SUMMARY, newline="") as f:
        cases = list(csv.DictReader(f))

    rows = []
    seen = set()
    for case in cases:
        l = int(case["l"])
        m = int(case["m"])
        a = float(case["a"])
        omega = float(case["omega"])
        key = (l, m, a, omega)
        if key in seen:
            continue
        seen.add(key)

        l_min = abs(m)
        l_max = l + 4
        coeffs = []
        for l_target in range(l_min, l_max + 1):
            coeff = scalar_cubic_coupling(
                l,
                m,
                a,
                omega,
                l_target=l_target,
                lmax_extra=24,
                quad_order=320,
            )
            coeffs.append((l_target, coeff))

        total_abs = sum(abs(coeff) for _, coeff in coeffs)
        for l_target, coeff in coeffs:
            rows.append({
                "l_source": l,
                "m": m,
                "a": f"{a:.16e}",
                "omega": f"{omega:.16e}",
                "l_target": l_target,
                "coefficient": f"{coeff.real:.16e}{coeff.imag:+.16e}j",
                "abs_coefficient": f"{abs(coeff):.16e}",
                "relative_abs_weight": f"{abs(coeff) / max(total_abs, 1e-300):.16e}",
            })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fields = [
        "l_source", "m", "a", "omega", "l_target", "coefficient",
        "abs_coefficient", "relative_abs_weight",
    ]
    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print("Kerr scalar cubic projector")
    print(f"  cases = {len(seen)}")
    print(f"  rows  = {len(rows)}")
    print(f"  saved = {OUT}")


if __name__ == "__main__":
    main()
