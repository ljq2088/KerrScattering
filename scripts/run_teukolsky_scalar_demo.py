"""Demo run for scalar (s=0) Teukolsky in modes on Kerr."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.teukolsky_scalar import solve_scalar_in_mode


def main():
    result = solve_scalar_in_mode(l=0, m=0, omega=0.1, M=1.0, a=0.5, r_out=400.0)

    os.makedirs("results", exist_ok=True)
    out = "results/teukolsky_scalar_demo.csv"
    with open(out, "w", newline="") as f:
        fields = [
            "M", "a", "l", "m", "omega", "lambda", "r_plus", "omega_h",
            "p_horizon", "r_out", "Z_in", "Z_out", "reflection_amplitude", "status",
        ]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        row = dict(result)
        for key in ["Z_in", "Z_out", "reflection_amplitude"]:
            val = row[key]
            row[key] = f"{val.real:.15e}+{val.imag:.15e}j"
        writer.writerow(row)

    print("Scalar Teukolsky demo")
    print(f"  lambda = {result['lambda']:.12e}")
    print(f"  Z_in   = {result['Z_in'].real:.12e} + {result['Z_in'].imag:.12e}j")
    print(f"  Z_out  = {result['Z_out'].real:.12e} + {result['Z_out'].imag:.12e}j")
    print(f"  saved  = {out}")


if __name__ == "__main__":
    main()
