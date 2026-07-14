"""Measure the stability of the finite-window high-frequency tail fits."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_nonlinear_tail_window_sensitivity.csv"
INPUTS = {
    0: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l0.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l0.csv",
    ],
    1: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l1.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l1.csv",
    ],
    2: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l2.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l2.csv",
    ],
}

# The first window is the one used in the manuscript. The other windows shift
# one edge while retaining at least three points, so the test probes selection
# sensitivity without changing the numerical input data.
WINDOWS = {
    0: [("base", 0.18, 0.60), ("start_plus", 0.22, 0.60), ("end_minus", 0.18, 0.52), ("both", 0.26, 0.60)],
    1: [("base", 0.38, 0.85), ("start_plus", 0.42, 0.85), ("end_minus", 0.38, 0.77), ("both", 0.46, 0.85)],
    2: [("base", 0.62, 1.00), ("start_plus", 0.66, 1.00), ("end_minus", 0.62, 0.92), ("both", 0.70, 1.00)],
}

M = 1.0
A = 0.5
R_PLUS = M + math.sqrt(M * M - A * A)
R_MINUS = M - math.sqrt(M * M - A * A)
T_H = (R_PLUS - R_MINUS) / (4.0 * math.pi * (R_PLUS * R_PLUS + A * A))


def load(ell: int) -> tuple[np.ndarray, np.ndarray]:
    rows: dict[float, dict[str, str]] = {}
    for path in INPUTS[ell]:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                omega = round(float(row["omega"]), 14)
                old = rows.get(omega)
                if old is None or abs(float(row["nonlinear_balance"])) < abs(float(old["nonlinear_balance"])):
                    rows[omega] = row
    omega = np.array(sorted(rows), dtype=float)
    values = np.array([float(rows[x]["T1"]) for x in omega], dtype=float)
    return omega, values


def fit(omega: np.ndarray, values: np.ndarray, lo: float, hi: float) -> tuple[int, float, float]:
    mask = (omega >= lo) & (omega <= hi) & (values > 0.0)
    if int(mask.sum()) < 3:
        raise RuntimeError(f"tail window [{lo}, {hi}] has fewer than three positive points")
    slope, intercept = np.polyfit(omega[mask], np.log(values[mask]), 1)
    if slope >= 0.0:
        raise RuntimeError(f"tail window [{lo}, {hi}] has non-decaying slope {slope}")
    model = intercept + slope * omega[mask]
    rms_log = float(np.sqrt(np.mean((np.log(values[mask]) - model) ** 2)))
    return int(mask.sum()), float(math.pi * (-1.0 / slope)), rms_log


def main() -> None:
    output_rows: list[dict[str, object]] = []
    for ell, windows in WINDOWS.items():
        omega, values = load(ell)
        fits = []
        for name, lo, hi in windows:
            n, pi_t, rms = fit(omega, values, lo, hi)
            fits.append((name, lo, hi, n, pi_t, rms))
            output_rows.append(
                {
                    "l": ell,
                    "window": name,
                    "omega_min": lo,
                    "omega_max": hi,
                    "points": n,
                    "pi_Tfit": pi_t,
                    "tail_rms_log": rms,
                    "abs_Tfit_over_TH_minus_1": abs((pi_t / math.pi) / T_H - 1.0),
                }
            )
        pi_values = np.array([item[4] for item in fits])
        print(
            f"l={ell} base_piT={fits[0][4]:.8f} "
            f"range=[{pi_values.min():.8f}, {pi_values.max():.8f}] "
            f"max_abs_delta_TH={max(row['abs_Tfit_over_TH_minus_1'] for row in output_rows if row['l'] == ell):.4%}"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "l", "window", "omega_min", "omega_max", "points", "pi_Tfit",
        "tail_rms_log", "abs_Tfit_over_TH_minus_1",
    ]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in output_rows:
            writer.writerow({
                key: f"{value:.12e}" if isinstance(value, float) else value
                for key, value in row.items()
            })
    print(OUTPUT)


if __name__ == "__main__":
    main()
