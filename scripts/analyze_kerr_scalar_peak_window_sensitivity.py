"""Measure the Kerr nonlinear peak-fit sensitivity to the selection threshold."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import curve_fit


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_nonlinear_peak_window_sensitivity.csv"
THRESHOLDS = (0.15, 0.20, 0.25, 0.30)


def lorentzian(w: np.ndarray, amplitude: float, center: float, gamma: float, offset: float) -> np.ndarray:
    return offset + amplitude * gamma**2 / ((w - center) ** 2 + gamma**2)


def read_best_rows(ell: int) -> tuple[np.ndarray, np.ndarray]:
    best: dict[float, dict[str, str]] = {}
    paths = (
        ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_hires_l{ell}.csv",
        ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_refine_l{ell}.csv",
    )
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                omega = round(float(row["omega"]), 14)
                if omega not in best or abs(float(row["nonlinear_balance"])) < abs(
                    float(best[omega]["nonlinear_balance"])
                ):
                    best[omega] = row
    rows = [best[omega] for omega in sorted(best)]
    return (
        np.array([float(row["omega"]) for row in rows]),
        np.array([float(row["T1"]) for row in rows]),
    )


def fit_threshold(omega: np.ndarray, t1: np.ndarray, threshold: float) -> dict[str, float | int]:
    dense = np.linspace(omega.min(), omega.max(), 4000)
    interpolant = PchipInterpolator(omega, t1)
    peak_value = float(np.max(interpolant(dense)))
    mask = t1 > threshold * peak_value
    x = omega[mask]
    y = t1[mask]
    if len(x) < 5:
        raise RuntimeError(f"threshold {threshold} retains only {len(x)} points")
    peak_location = float(dense[np.argmax(interpolant(dense))])
    p0 = [peak_value, peak_location, 0.08, 0.0]
    bounds = ([0.0, omega.min(), 1.0e-4, -np.inf], [np.inf, omega.max(), 1.0, np.inf])
    parameters, _ = curve_fit(
        lorentzian, x, y, p0=p0, bounds=bounds, maxfev=20_000
    )
    prediction = lorentzian(x, *parameters)
    rms = float(np.sqrt(np.mean((y - prediction) ** 2)) / peak_value)
    denominator = float(np.sum((y - np.mean(y)) ** 2))
    r2 = float(
        1.0 - np.sum((y - prediction) ** 2) / denominator
        if denominator > 0.0
        else np.nan
    )
    return {
        "l": 0,
        "threshold": threshold,
        "points": len(x),
        "omega_peak": float(parameters[1]),
        "gamma": float(abs(parameters[2])),
        "peak_rms_over_peak": rms,
        "peak_r2": r2,
    }


def main() -> None:
    rows: list[dict[str, float | int]] = []
    for ell in (0, 1, 2):
        omega, t1 = read_best_rows(ell)
        for threshold in THRESHOLDS:
            result = fit_threshold(omega, t1, threshold)
            result["l"] = ell
            rows.append(result)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "l",
            "threshold",
            "points",
            "omega_peak",
            "gamma",
            "peak_rms_over_peak",
            "peak_r2",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.12e}" if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )
    print(OUTPUT)
    for ell in (0, 1, 2):
        subset = [row for row in rows if row["l"] == ell]
        center_span = max(float(row["omega_peak"]) for row in subset) - min(
            float(row["omega_peak"]) for row in subset
        )
        width_span = max(float(row["gamma"]) for row in subset) - min(
            float(row["gamma"]) for row in subset
        )
        print(f"l={ell} center_span={center_span:.12e} gamma_span={width_span:.12e}")


if __name__ == "__main__":
    main()
