"""Validate the analytic scalar-monopole zero-frequency response."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
BASE_PAIR = (
    RESULTS / "kerr_scalar_near_extremal_l0_N144.csv",
    RESULTS / "kerr_scalar_near_extremal_l0_N176.csv",
)
HIGH_SPIN_PAIR = (
    RESULTS / "kerr_scalar_near_extremal_l0_highspin_N224.csv",
    RESULTS / "kerr_scalar_near_extremal_l0_highspin_N256.csv",
)
OUT = RESULTS / "kerr_scalar_l0_zero_frequency_summary.csv"
ANALYTIC_RESPONSE = math.log(2.0) / math.pi


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def row_key(row: dict[str, str]) -> tuple[float, float]:
    return (
        round(float(row["a"]), 12),
        round(float(row["detuning_over_kappa"]), 12),
    )


def relative_change(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def paired_rows(paths: tuple[Path, Path]):
    low = {row_key(row): row for row in read_csv(paths[0])}
    high = {row_key(row): row for row in read_csv(paths[1])}
    return low, high


def fit_summary(
    a: float,
    detunings: tuple[float, float, float],
    paths: tuple[Path, Path],
) -> dict[str, object]:
    low, high = paired_rows(paths)
    keys = [(round(a, 12), round(y, 12)) for y in detunings]
    samples = [high[key] for key in keys]
    y = np.asarray(detunings, dtype=float)
    response = np.asarray([float(row["horizon_response"]) for row in samples])
    intercept = float(np.polyfit(y, response, 2)[-1])
    resolution_change = max(
        relative_change(
            float(low[key]["horizon_response"]),
            float(high[key]["horizon_response"]),
        )
        for key in keys
    )
    return {
        "a": f"{a:.16e}",
        "fit_detunings": ",".join(f"{value:g}" for value in detunings),
        "zero_frequency_response": f"{intercept:.16e}",
        "analytic_response_ln2_over_pi": f"{ANALYTIC_RESPONSE:.16e}",
        "relative_error_to_analytic": f"{relative_change(intercept, ANALYTIC_RESPONSE):.16e}",
        "max_resolution_relative_change": f"{resolution_change:.16e}",
        "max_linear_balance": f"{max(abs(float(row['linear_balance'])) for row in samples):.16e}",
        "max_nonlinear_balance": f"{max(abs(float(row['nonlinear_balance'])) for row in samples):.16e}",
        "max_wronskian_relative_error": f"{max(float(row['wronskian_relative_error']) for row in samples):.16e}",
        "low_resolution": paths[0].name,
        "high_resolution": paths[1].name,
    }


def main() -> None:
    rows = []
    for a in (0.0, 0.5, 0.9, 0.98, 0.99, 0.995):
        rows.append(fit_summary(a, (0.0125, 0.025, 0.05), BASE_PAIR))
    rows.append(fit_summary(0.997, (0.0125, 0.025, 0.05), HIGH_SPIN_PAIR))
    # At a/M=0.999 the two smallest frequencies are conditioning limited.
    rows.append(fit_summary(0.999, (0.05, 0.1, 0.2), BASE_PAIR))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"analytic chi_00(0) = {ANALYTIC_RESPONSE:.12f}")
    print(
        "maximum relative extrapolation error = "
        f"{max(float(row['relative_error_to_analytic']) for row in rows):.3e}"
    )
    print(f"saved = {OUT}")


if __name__ == "__main__":
    main()
