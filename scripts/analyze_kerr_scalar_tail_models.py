"""Compare exponential and power-law models for the resolved Kerr tails."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results" / "kerr_scalar_nonlinear_tail_model_comparison.csv"
INPUTS = {
    ell: [
        ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_hires_l{ell}.csv",
        ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_refine_l{ell}.csv",
        ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_dense_l{ell}.csv",
        ROOT / "results" / f"kerr_scalar_nonlinear_axisymmetric_tail_q2048_l{ell}.csv",
    ]
    for ell in (0, 1, 2)
}
WINDOWS = {
    0: (0.18, 0.60),
    1: (0.38, 0.85),
    2: (0.62, 1.00),
}

M = 1.0
A = 0.5
R_PLUS = M + math.sqrt(M * M - A * A)
R_MINUS = M - math.sqrt(M * M - A * A)
T_H = (R_PLUS - R_MINUS) / (4.0 * math.pi * (R_PLUS * R_PLUS + A * A))


def load(ell: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows: dict[float, dict[str, str]] = {}
    for path in INPUTS[ell]:
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                omega = round(float(row["omega"]), 14)
                rank = (
                    int(float(row.get("N", 0))),
                    int(float(row.get("quad_order", 0))),
                    -abs(float(row["nonlinear_balance"])),
                )
                old = rows.get(omega)
                old_rank = None if old is None else (
                    int(float(old.get("N", 0))),
                    int(float(old.get("quad_order", 0))),
                    -abs(float(old["nonlinear_balance"])),
                )
                if old is None or rank > old_rank:
                    rows[omega] = row
    lo, hi = WINDOWS[ell]
    selected = [
        row
        for omega, row in sorted(rows.items())
        if lo <= omega <= hi and float(row["T1"]) > 0.0
    ]
    return (
        np.array([float(row["omega"]) for row in selected]),
        np.array([float(row["T1"]) for row in selected]),
        np.array([abs(float(row["nonlinear_balance"])) for row in selected]),
    )


def linear_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float, np.ndarray]:
    slope, intercept = np.polyfit(x, y, 1)
    return float(slope), float(intercept), intercept + slope * x


def aicc(residual: np.ndarray, parameters: int) -> float:
    n = residual.size
    if n <= parameters + 1:
        raise ValueError("AICc requires more than k+1 samples")
    sse = max(float(np.dot(residual, residual)), np.finfo(float).tiny)
    return float(
        n * math.log(sse / n)
        + 2.0 * parameters
        + 2.0 * parameters * (parameters + 1.0) / (n - parameters - 1.0)
    )


def loo_rms(x: np.ndarray, y: np.ndarray) -> float:
    residuals = []
    for index in range(x.size):
        keep = np.arange(x.size) != index
        slope, intercept, _ = linear_fit(x[keep], y[keep])
        residuals.append(y[index] - (intercept + slope * x[index]))
    return float(np.sqrt(np.mean(np.square(residuals))))


def main() -> None:
    rows = []
    for ell in (0, 1, 2):
        omega, values, balance = load(ell)
        log_values = np.log(values)

        exp_slope, _, exp_model = linear_fit(omega, log_values)
        power_slope, _, power_model = linear_fit(np.log(omega), log_values)
        if exp_slope >= 0.0 or power_slope >= 0.0:
            raise RuntimeError(f"non-decaying fitted tail for l={ell}")

        fixed_slope = -1.0 / T_H
        fixed_intercept = float(np.mean(log_values - fixed_slope * omega))
        fixed_model = fixed_intercept + fixed_slope * omega

        exp_residual = log_values - exp_model
        power_residual = log_values - power_model
        fixed_residual = log_values - fixed_model
        row = {
            "l": ell,
            "omega_min": float(omega.min()),
            "omega_max": float(omega.max()),
            "points": int(omega.size),
            "pi_Tfit": math.pi * (-1.0 / exp_slope),
            "power_index": -power_slope,
            "exp_rms_log": float(np.sqrt(np.mean(exp_residual**2))),
            "power_rms_log": float(np.sqrt(np.mean(power_residual**2))),
            "hawking_fixed_rms_log": float(np.sqrt(np.mean(fixed_residual**2))),
            "exp_aicc": aicc(exp_residual, 2),
            "power_aicc": aicc(power_residual, 2),
            "delta_aicc_power_minus_exp": aicc(power_residual, 2)
            - aicc(exp_residual, 2),
            "exp_loo_rms_log": loo_rms(omega, log_values),
            "power_loo_rms_log": loo_rms(np.log(omega), log_values),
            "max_abs_balance": float(balance.max()),
        }
        rows.append(row)
        print(
            f"l={ell} n={row['points']} piT={row['pi_Tfit']:.8f} "
            f"rms(exp,power)=({row['exp_rms_log']:.4e},"
            f"{row['power_rms_log']:.4e}) "
            f"delta_AICc={row['delta_aicc_power_minus_exp']:.3f}"
        )

    fields = list(rows[0])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.12e}" if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )
    print(OUTPUT)


if __name__ == "__main__":
    main()
