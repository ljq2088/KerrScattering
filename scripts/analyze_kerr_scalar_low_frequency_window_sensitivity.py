"""Measure low-frequency log-log slope sensitivity to the number of points."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_low_frequency_axisymmetric_window_sensitivity.csv"


def load(ell: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_hires_l{ell}.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = sorted(csv.DictReader(handle), key=lambda row: float(row["omega"]))
    omega = np.array([float(row["omega"]) for row in rows], dtype=float)
    t0 = np.array([abs(float(row["T0"])) for row in rows], dtype=float)
    t1 = np.array([abs(float(row["T1"])) for row in rows], dtype=float)
    return omega, t0, t1


def fit(omega: np.ndarray, values: np.ndarray, npoints: int) -> tuple[float, float]:
    x = omega[:npoints]
    y = values[:npoints]
    slope, intercept = np.polyfit(np.log(x), np.log(y), 1)
    residual = np.log(y) - (slope * np.log(x) + intercept)
    rms = float(np.sqrt(np.mean(residual * residual)))
    return float(slope), rms


def main() -> None:
    rows: list[dict[str, object]] = []
    for ell in (0, 1, 2):
        omega, t0, t1 = load(ell)
        for npoints in (3, 4, 5):
            slope0, rms0 = fit(omega, t0, npoints)
            slope1, rms1 = fit(omega, t1, npoints)
            rows.append(
                {
                    "l": ell,
                    "points": npoints,
                    "T0_slope": slope0,
                    "T1_slope": slope1,
                    "T0_rms_log": rms0,
                    "T1_rms_log": rms1,
                }
            )
        subset = [row for row in rows if row["l"] == ell]
        baseline = next(row for row in subset if row["points"] == 4)
        print(
            f"l={ell} baseline T0={baseline['T0_slope']:.6f} "
            f"T1={baseline['T1_slope']:.6f}; "
            f"T0 range=[{min(row['T0_slope'] for row in subset):.6f}, {max(row['T0_slope'] for row in subset):.6f}] "
            f"T1 range=[{min(row['T1_slope'] for row in subset):.6f}, {max(row['T1_slope'] for row in subset):.6f}]"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = ["l", "points", "T0_slope", "T1_slope", "T0_rms_log", "T1_rms_log"]
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: f"{value:.12e}" if isinstance(value, float) else value
                for key, value in row.items()
            })
    print(OUTPUT)


if __name__ == "__main__":
    main()
