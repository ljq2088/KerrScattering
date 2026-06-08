"""Compare Python R_in amplitudes against GSN/MST benchmarks.

Parameters are the user-requested mode

    s=-2, a=0.5, l=m=2, M=1.

The high-frequency row uses the phase-peeled Chebyshev construction closest to
the Schwarzschild spectral code.  The middle/low-frequency rows use the same
Teukolsky equation with high-order asymptotic matching, which is more stable
for the subdominant B_inc/B_ref extraction in the direct Teukolsky variable.
"""
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.teukolsky_rin import solve_rin_asymptotic, solve_rin_chebyshev


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "spin_minus2_rin_comparison.csv"


BENCHMARKS = {
    10.0: {
        "lambda": -26.85215496939334,
        "source": "GSN",
        "B_inc": complex(24.675049712429978, -5.00013326071889),
        "B_ref": complex(-6.457956617151793e-9, -8.144599106575082e-9),
    },
    0.1: {
        "lambda": 3.667320713846837,
        "source": "Mathematica MST",
        "B_inc": complex(-114228.20426982341, 232645.3143227442),
        "B_ref": complex(-4.272969428276756, -17.9464051131823),
    },
    1.0e-4: {
        "lambda": 3.9996666673280417,
        "source": "Mathematica MST",
        "B_inc": complex(-1.5435347274666643e20, 3.416432242244572e20),
        "B_ref": complex(10210.782613860754, -22813.76866596801),
    },
}


def fmt_complex(z):
    return f"{z.real:.16e}{z.imag:+.16e}j"


def relerr(value, reference):
    return abs(value - reference) / max(abs(reference), 1e-300)


def compute_row(omega):
    bench = BENCHMARKS[omega]
    lam = bench["lambda"]
    if omega == 10.0:
        result = solve_rin_chebyshev(omega, lam, n=192, r_match=20.0)
        note = "B_ref is close to the double-precision floor in direct Teukolsky variables."
    elif omega == 0.1:
        result = solve_rin_asymptotic(
            omega, lam, r_match=50.0, infinity_order=4, horizon_order=3
        )
        note = "High-order infinity matching; stable B_ref and percent-level B_inc."
    else:
        result = solve_rin_asymptotic(
            omega, lam, r_match=1.0e5, infinity_order=6, horizon_order=3
        )
        note = "Low-frequency MST regime; asymptotic matching is well conditioned."

    return {
        "s": -2,
        "a": 0.5,
        "l": 2,
        "m": 2,
        "omega": omega,
        "lambda": lam,
        "method": result.method,
        "r_match": result.r_match,
        "B_inc": fmt_complex(result.incidence_amplitude),
        "B_inc_benchmark": fmt_complex(bench["B_inc"]),
        "B_inc_relerr": f"{relerr(result.incidence_amplitude, bench['B_inc']):.16e}",
        "B_ref": fmt_complex(result.reflection_amplitude),
        "B_ref_benchmark": fmt_complex(bench["B_ref"]),
        "B_ref_relerr": f"{relerr(result.reflection_amplitude, bench['B_ref']):.16e}",
        "benchmark_source": bench["source"],
        "note": note,
    }


def main():
    OUT.parent.mkdir(exist_ok=True)
    rows = [compute_row(omega) for omega in [10.0, 0.1, 1.0e-4]]
    fields = list(rows[0].keys())
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved={OUT}")
    for row in rows:
        print(
            f"omega={row['omega']}: "
            f"Binc_rel={row['B_inc_relerr']}, "
            f"Bref_rel={row['B_ref_relerr']} "
            f"({row['benchmark_source']})"
        )


if __name__ == "__main__":
    main()
