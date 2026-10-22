"""Audit higher-power spheroidal source projections at the hardest spin."""

from __future__ import annotations

import csv
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.teukolsky_scalar import KerrParams, scalar_power_coupling


OUT = ROOT / "results" / "kerr_scalar_power_angular_convergence.csv"


def relative_change(first: complex, second: complex) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def main() -> None:
    a = 0.9999
    params = KerrParams(M=1.0, a=a)
    rows = []
    for n in (2, 3):
        for l, m in ((1, 1), (2, 1), (2, 2), (3, 3)):
            omega = m * params.omega_h
            for cos_power in (0, 2):
                active = scalar_power_coupling(
                    l, m, a, omega, n, l_target=l,
                    lmax_extra=16, quad_order=256, cos_power=cos_power,
                )
                reference = scalar_power_coupling(
                    l, m, a, omega, n, l_target=l,
                    lmax_extra=24, quad_order=512, cos_power=cos_power,
                )
                rows.append({
                    "nonlinearity_order": n,
                    "a": f"{a:.16e}",
                    "l": l,
                    "m": m,
                    "omega": f"{omega:.16e}",
                    "cos_power": cos_power,
                    "active_lmax_extra": 16,
                    "active_quad_order": 256,
                    "reference_lmax_extra": 24,
                    "reference_quad_order": 512,
                    "active_real": f"{active.real:.16e}",
                    "active_imag": f"{active.imag:.16e}",
                    "reference_real": f"{reference.real:.16e}",
                    "reference_imag": f"{reference.imag:.16e}",
                    "relative_change": f"{relative_change(active, reference):.16e}",
                })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"rows = {len(rows)}")
    print(f"maximum relative change = {max(float(row['relative_change']) for row in rows):.6e}")
    print(f"saved = {OUT}")


if __name__ == "__main__":
    main()
