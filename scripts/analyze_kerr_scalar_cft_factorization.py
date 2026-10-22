"""Audit the factorization behind the near-extremal Kerr/CFT interpretation.

At fixed nonzero ``y = p/kappa`` the exact normalization identity is

    M^(2n-2) chi_H^(n) = I_H^n K_n,
    I_H = M^2 / |B_inc|^2.

This script fits the response, the linear fixed-incident horizon intensity,
and the residual nonlinear kernel separately.  It is deliberately restricted
to accepted higher-power rows for which ``B_inc`` was recorded directly.
"""

from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_kerr_scalar_modal_powerlaws import conformal_data


RESULTS = ROOT / "results"
RAW_HIGH = (
    RESULTS / "kerr_scalar_power_near_extremal_N176.csv",
    RESULTS / "kerr_scalar_power_near_extremal_extreme_N256.csv",
    RESULTS / "kerr_scalar_power_near_extremal_additional_N176.csv",
    RESULTS / "kerr_scalar_power_near_extremal_additional_extreme_N256.csv",
    RESULTS / "kerr_scalar_power_near_extremal_dense22_N288.csv",
    RESULTS / "kerr_scalar_power_near_extremal_dense33_N288.csv",
    RESULTS / "kerr_scalar_power_near_extremal_ultra_principal_N320.csv",
)
ACCEPTED_INPUT = RESULTS / "kerr_scalar_power_near_extremal_fixed_y_values.csv"
THRESHOLD_INPUT = RESULTS / "kerr_scalar_power_near_extremal_threshold_values.csv"
SAMPLES_OUT = RESULTS / "kerr_scalar_cft_factorization_samples.csv"
FITS_OUT = RESULTS / "kerr_scalar_cft_factorization_fits.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write to {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def key(row: dict[str, str]) -> tuple[int, float, int, int, float]:
    return (
        int(row["nonlinearity_order"]),
        round(float(row["a"]), 12),
        int(row["l"]),
        int(row["m"]),
        round(float(row["detuning_over_kappa"]), 12),
    )


def power_fit(kappa: np.ndarray, quantity: np.ndarray) -> tuple[float, float]:
    slope, intercept = np.polyfit(np.log(kappa), np.log(quantity), 1)
    residual = np.log(quantity) - (intercept + slope * np.log(kappa))
    total = np.log(quantity) - np.mean(np.log(quantity))
    denominator = float(np.dot(total, total))
    r_squared = 1.0 - float(np.dot(residual, residual)) / denominator if denominator else 1.0
    return -float(slope), r_squared


def collect_samples() -> list[dict[str, object]]:
    raw: dict[tuple[int, float, int, int, float], dict[str, str]] = {}
    for path in RAW_HIGH:
        for row in read_csv(path):
            raw[key(row)] = row

    output = []
    for accepted in read_csv(ACCEPTED_INPUT):
        if accepted["accepted"] != "true":
            continue
        sample = raw.get(key(accepted))
        if sample is None:
            continue
        n, a, l, m, y = key(accepted)
        b_inc = float(sample["B_inc_abs"])
        response = float(accepted["horizon_response"])
        intensity = 1.0 / b_inc**2
        kernel = response / intensity**n
        angular_k, h_real, h_imag, conformal_class = conformal_data(l, m)
        analytic_intensity_alpha = 1.0 if conformal_class == "principal_complex_h" else 2.0 - 2.0 * h_real
        output.append(
            {
                "regime": "fixed_nonzero_y",
                "nonlinearity_order": n,
                "a": f"{a:.16e}",
                "l": l,
                "m": m,
                "surface_gravity": accepted["surface_gravity"],
                "detuning_over_kappa": f"{y:.16e}",
                "B_inc_abs": f"{b_inc:.16e}",
                "fixed_incident_horizon_intensity": f"{intensity:.16e}",
                "horizon_response": f"{response:.16e}",
                "scaled_nonlinear_kernel": f"{kernel:.16e}",
                "extremal_angular_K": f"{angular_k:.16e}",
                "conformal_weight_real": f"{h_real:.16e}",
                "conformal_weight_imag_abs": f"{h_imag:.16e}",
                "conformal_class": conformal_class,
                "analytic_intensity_alpha": f"{analytic_intensity_alpha:.16e}",
            }
        )

    for accepted in read_csv(THRESHOLD_INPUT):
        if accepted["accepted"] != "true":
            continue
        n = int(accepted["nonlinearity_order"])
        a = round(float(accepted["a"]), 12)
        l = int(accepted["l"])
        m = int(accepted["m"])
        intensity_by_y = {}
        for y in (-0.05, -0.025, 0.025, 0.05):
            sample = raw.get((n, a, l, m, round(y, 12)))
            if sample is None:
                break
            intensity_by_y[y] = 1.0 / float(sample["B_inc_abs"]) ** 2
        if len(intensity_by_y) != 4:
            continue
        inner = 0.5 * (intensity_by_y[-0.025] + intensity_by_y[0.025])
        outer = 0.5 * (intensity_by_y[-0.05] + intensity_by_y[0.05])
        intensity = (4.0 * inner - outer) / 3.0
        response = float(accepted["horizon_response"])
        kernel = response / intensity**n
        angular_k, h_real, h_imag, conformal_class = conformal_data(l, m)
        analytic_intensity_alpha = 1.0 if conformal_class == "principal_complex_h" else 2.0 - 2.0 * h_real
        output.append(
            {
                "regime": "iterated_threshold",
                "nonlinearity_order": n,
                "a": f"{a:.16e}",
                "l": l,
                "m": m,
                "surface_gravity": accepted["surface_gravity"],
                "detuning_over_kappa": "0.0000000000000000e+00",
                "B_inc_abs": "",
                "fixed_incident_horizon_intensity": f"{intensity:.16e}",
                "horizon_response": f"{response:.16e}",
                "scaled_nonlinear_kernel": f"{kernel:.16e}",
                "extremal_angular_K": f"{angular_k:.16e}",
                "conformal_weight_real": f"{h_real:.16e}",
                "conformal_weight_imag_abs": f"{h_imag:.16e}",
                "conformal_class": conformal_class,
                "analytic_intensity_alpha": f"{analytic_intensity_alpha:.16e}",
            }
        )
    return output


def fit_samples(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    groups = sorted(
        {
            (
                str(row["regime"]),
                int(row["nonlinearity_order"]),
                int(row["l"]),
                int(row["m"]),
                float(row["detuning_over_kappa"]),
            )
            for row in samples
        }
    )
    for regime, n, l, m, y in groups:
        group = [
            row
            for row in samples
            if str(row["regime"]) == regime
            and int(row["nonlinearity_order"]) == n
            and int(row["l"]) == l
            and int(row["m"]) == m
            and np.isclose(float(row["detuning_over_kappa"]), y)
        ]
        group.sort(key=lambda row: float(row["surface_gravity"]))
        windows = [("all", len(group))]
        windows.extend(
            (f"nearest{count}", count)
            for count in (7, 6, 5, 4, 3)
            if len(group) >= count
        )
        for window, count in windows:
            if len(group) < count or count < 3:
                continue
            subset = group[:count]
            kappa = np.array([float(row["surface_gravity"]) for row in subset])
            response = np.array([float(row["horizon_response"]) for row in subset])
            intensity = np.array(
                [float(row["fixed_incident_horizon_intensity"]) for row in subset]
            )
            kernel = np.array([float(row["scaled_nonlinear_kernel"]) for row in subset])
            alpha_response, r2_response = power_fit(kappa, response)
            alpha_intensity, r2_intensity = power_fit(kappa, intensity)
            alpha_kernel, r2_kernel = power_fit(kappa, kernel)
            closure = alpha_response - n * alpha_intensity - alpha_kernel
            first = subset[0]
            output.append(
                {
                    "regime": regime,
                    "nonlinearity_order": n,
                    "l": l,
                    "m": m,
                    "detuning_over_kappa": f"{y:.16e}",
                    "fit_window": window,
                    "spin_count": len(subset),
                    "spin_min": f"{min(float(row['a']) for row in subset):.16e}",
                    "spin_max": f"{max(float(row['a']) for row in subset):.16e}",
                    "kappa_min": f"{min(kappa):.16e}",
                    "kappa_max": f"{max(kappa):.16e}",
                    "alpha_response": f"{alpha_response:.16e}",
                    "r_squared_response": f"{r2_response:.16e}",
                    "alpha_intensity": f"{alpha_intensity:.16e}",
                    "r_squared_intensity": f"{r2_intensity:.16e}",
                    "alpha_kernel": f"{alpha_kernel:.16e}",
                    "r_squared_kernel": f"{r2_kernel:.16e}",
                    "exponent_closure_error": f"{closure:.16e}",
                    "analytic_intensity_alpha": first["analytic_intensity_alpha"],
                    "conformal_weight_real": first["conformal_weight_real"],
                    "conformal_weight_imag_abs": first["conformal_weight_imag_abs"],
                    "conformal_class": first["conformal_class"],
                }
            )
    return output


def main() -> None:
    samples = collect_samples()
    fits = fit_samples(samples)
    write_csv(SAMPLES_OUT, samples)
    write_csv(FITS_OUT, fits)
    print(f"accepted factorization samples = {len(samples)}")
    for row in fits:
        if row["fit_window"] == "nearest7" and (
            row["regime"] == "iterated_threshold"
            or np.isclose(float(row["detuning_over_kappa"]), 0.5)
        ):
            print(
                f"{row['regime']} n={row['nonlinearity_order']} "
                f"mode=({row['l']},{row['m']}) "
                f"alpha_chi={float(row['alpha_response']):.6f} "
                f"alpha_I={float(row['alpha_intensity']):.6f} "
                f"alpha_K={float(row['alpha_kernel']):.6f} "
                f"class={row['conformal_class']}"
            )
    print(f"saved = {SAMPLES_OUT}")
    print(f"saved = {FITS_OUT}")


if __name__ == "__main__":
    main()
