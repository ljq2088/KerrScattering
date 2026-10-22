"""Analyze scalar-monopole |Phi|^(2n) Phi response scans."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

FIXED_PAIR = (
    RESULTS / "kerr_scalar_power_nonlinearity_l0_fixed_N144.csv",
    RESULTS / "kerr_scalar_power_nonlinearity_l0_fixed_N176.csv",
)
KAPPA_PAIR = (
    RESULTS / "kerr_scalar_power_nonlinearity_l0_kappa_N144.csv",
    RESULTS / "kerr_scalar_power_nonlinearity_l0_kappa_N176.csv",
)
FIXED_OUT = RESULTS / "kerr_scalar_power_nonlinearity_l0_fixed_summary.csv"
KAPPA_OUT = RESULTS / "kerr_scalar_power_nonlinearity_l0_kappa_summary.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"No rows in {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def key(row: dict[str, str]) -> tuple[int, float, float]:
    return (
        int(row["nonlinearity_order"]),
        round(float(row["a"]), 12),
        round(float(row["frequency_coordinate"]), 12),
    )


def keyed(rows: list[dict[str, str]]) -> dict[tuple[int, float, float], dict[str, str]]:
    return {key(row): row for row in rows}


def relative_change(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def paired_rows(paths: tuple[Path, Path]) -> list[dict[str, object]]:
    low = keyed(read_csv(paths[0]))
    high = keyed(read_csv(paths[1]))
    if low.keys() != high.keys():
        missing_low = sorted(high.keys() - low.keys())
        missing_high = sorted(low.keys() - high.keys())
        raise RuntimeError(
            f"Resolution grids differ: missing low={missing_low}, "
            f"missing high={missing_high}"
        )
    output = []
    for sample_key in sorted(high):
        high_row = high[sample_key]
        low_row = low[sample_key]
        high_response = float(high_row["horizon_response"])
        output.append({
            "n": int(high_row["nonlinearity_order"]),
            "a": float(high_row["a"]),
            "coordinate": float(high_row["frequency_coordinate"]),
            "omega": float(high_row["omega"]),
            "kappa": float(high_row["surface_gravity"]),
            "response": high_response,
            "scaled_response": float(high_row["response_over_frequency_power"]),
            "analytic": float(high_row["analytic_low_frequency_coefficient"]),
            "resolution_change": relative_change(
                float(low_row["horizon_response"]), high_response
            ),
            "linear_balance": max(
                abs(float(low_row["linear_balance"])),
                abs(float(high_row["linear_balance"])),
            ),
            "wronskian_error": max(
                float(low_row["wronskian_relative_error"]),
                float(high_row["wronskian_relative_error"]),
            ),
            "rss_mb": max(
                float(low_row["rss_mb_after"]),
                float(high_row["rss_mb_after"]),
            ),
        })
    return output


def power_fit(rows: list[dict[str, object]]) -> tuple[float, float]:
    x = np.log([float(row["omega"]) for row in rows])
    y = np.log([float(row["response"]) for row in rows])
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    r2 = 1.0 - np.sum((y - fitted) ** 2) / np.sum((y - np.mean(y)) ** 2)
    return float(slope), float(r2)


def coefficient_extrapolation(rows: list[dict[str, object]]) -> float:
    omega = np.array([float(row["omega"]) for row in rows])
    scaled = np.array([float(row["scaled_response"]) for row in rows])
    return float(np.polyval(np.polyfit(omega, scaled, 2), 0.0))


def fixed_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for n in sorted({int(row["n"]) for row in rows}):
        spins = sorted({float(row["a"]) for row in rows if int(row["n"]) == n})
        for a in spins:
            subset = sorted(
                [
                    row for row in rows
                    if int(row["n"]) == n and np.isclose(float(row["a"]), a)
                ],
                key=lambda row: float(row["omega"]),
            )
            if len(subset) < 6:
                raise RuntimeError(f"Need at least six fixed-frequency rows for n={n}, a={a}")
            fit_rows = subset[:5]
            fitted_power, power_r2 = power_fit(fit_rows)
            coefficient = coefficient_extrapolation(fit_rows)
            window_coefficients = [
                coefficient_extrapolation(subset[:count]) for count in (4, 5, 6)
            ]
            window_spread = max(
                relative_change(value, coefficient) for value in window_coefficients
            )
            analytic = float(fit_rows[0]["analytic"])
            output.append({
                "nonlinearity_order": n,
                "a": f"{a:.16e}",
                "predicted_frequency_power": 2 * n - 2,
                "fitted_frequency_power": f"{fitted_power:.16e}",
                "power_fit_r2": f"{power_r2:.16e}",
                "analytic_low_frequency_coefficient": f"{analytic:.16e}",
                "extrapolated_low_frequency_coefficient": f"{coefficient:.16e}",
                "relative_error_to_analytic_coefficient": (
                    f"{relative_change(coefficient, analytic):.16e}"
                ),
                "fit_window_relative_spread": f"{window_spread:.16e}",
                "max_resolution_relative_change": (
                    f"{max(float(row['resolution_change']) for row in subset):.16e}"
                ),
                "max_linear_balance": (
                    f"{max(float(row['linear_balance']) for row in subset):.16e}"
                ),
                "max_wronskian_relative_error": (
                    f"{max(float(row['wronskian_error']) for row in subset):.16e}"
                ),
                "max_rss_mb": f"{max(float(row['rss_mb']) for row in subset):.6e}",
                "fit_frequencies": ";".join(
                    f"{float(row['omega']):.8g}" for row in fit_rows
                ),
                "low_resolution": FIXED_PAIR[0].name,
                "high_resolution": FIXED_PAIR[1].name,
            })
    return output


def kappa_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for n in sorted({int(row["n"]) for row in rows}):
        coordinates = sorted({
            float(row["coordinate"]) for row in rows if int(row["n"]) == n
        })
        for coordinate in coordinates:
            subset = sorted(
                [
                    row for row in rows
                    if int(row["n"]) == n
                    and np.isclose(float(row["coordinate"]), coordinate)
                ],
                key=lambda row: float(row["kappa"]),
            )
            if len(subset) < 5:
                raise RuntimeError(
                    f"Need five fixed-omega/kappa rows for n={n}, y={coordinate}"
                )
            high_spin = subset[:3]
            high_spin_power, high_spin_r2 = power_fit(high_spin)
            all_spin_power, all_spin_r2 = power_fit(subset)
            endpoint = subset[0]
            analytic = float(endpoint["analytic"])
            output.append({
                "nonlinearity_order": n,
                "omega_over_kappa": f"{coordinate:.16e}",
                "predicted_kappa_power": 2 * n - 2,
                "fitted_kappa_power_high_spin": f"{high_spin_power:.16e}",
                "high_spin_fit_r2": f"{high_spin_r2:.16e}",
                "fitted_kappa_power_all_spins": f"{all_spin_power:.16e}",
                "all_spin_fit_r2": f"{all_spin_r2:.16e}",
                "smallest_surface_gravity": f"{float(endpoint['kappa']):.16e}",
                "scaled_response_at_smallest_surface_gravity": (
                    f"{float(endpoint['scaled_response']):.16e}"
                ),
                "analytic_low_frequency_coefficient": f"{analytic:.16e}",
                "endpoint_relative_error_to_analytic_coefficient": (
                    f"{relative_change(float(endpoint['scaled_response']), analytic):.16e}"
                ),
                "max_resolution_relative_change": (
                    f"{max(float(row['resolution_change']) for row in subset):.16e}"
                ),
                "max_linear_balance": (
                    f"{max(float(row['linear_balance']) for row in subset):.16e}"
                ),
                "max_wronskian_relative_error": (
                    f"{max(float(row['wronskian_error']) for row in subset):.16e}"
                ),
                "max_rss_mb": f"{max(float(row['rss_mb']) for row in subset):.6e}",
                "spin_count": len(subset),
                "low_resolution": KAPPA_PAIR[0].name,
                "high_resolution": KAPPA_PAIR[1].name,
            })
    return output


def main() -> None:
    fixed = fixed_summary(paired_rows(FIXED_PAIR))
    kappa = kappa_summary(paired_rows(KAPPA_PAIR))
    write_csv(FIXED_OUT, fixed)
    write_csv(KAPPA_OUT, kappa)
    print(f"wrote {FIXED_OUT}")
    print(f"wrote {KAPPA_OUT}")
    print(
        "fixed-frequency maxima: "
        f"analytic error={max(float(row['relative_error_to_analytic_coefficient']) for row in fixed):.3e}, "
        f"resolution change={max(float(row['max_resolution_relative_change']) for row in fixed):.3e}"
    )
    for n in sorted({int(row["nonlinearity_order"]) for row in kappa}):
        row = next(
            item for item in kappa
            if int(item["nonlinearity_order"]) == n
            and np.isclose(float(item["omega_over_kappa"]), 0.025)
        )
        print(
            f"n={n}: expected kappa power={row['predicted_kappa_power']}, "
            f"high-spin fit={float(row['fitted_kappa_power_high_spin']):.8f}"
        )


if __name__ == "__main__":
    main()
