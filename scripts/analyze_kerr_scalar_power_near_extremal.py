"""Analyze near-extremal ``|Phi|^(2n) Phi`` modal response laws.

Orders n=2 and n=3 are paired across two spectral resolutions.  Their
threshold limits use the same symmetric Richardson prescription as the cubic
study.  Accepted cubic rows are then merged so order dependence can be fitted
and plotted on one common footing.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_kerr_scalar_modal_powerlaws import conformal_data


RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

INPUT_PAIRS = (
    (
        RESULTS / "kerr_scalar_power_near_extremal_N144.csv",
        RESULTS / "kerr_scalar_power_near_extremal_N176.csv",
    ),
    (
        RESULTS / "kerr_scalar_power_near_extremal_extreme_N224.csv",
        RESULTS / "kerr_scalar_power_near_extremal_extreme_N256.csv",
    ),
    (
        RESULTS / "kerr_scalar_power_near_extremal_additional_N144.csv",
        RESULTS / "kerr_scalar_power_near_extremal_additional_N176.csv",
    ),
    (
        RESULTS / "kerr_scalar_power_near_extremal_additional_extreme_N224.csv",
        RESULTS / "kerr_scalar_power_near_extremal_additional_extreme_N256.csv",
    ),
    (
        RESULTS / "kerr_scalar_power_near_extremal_dense22_N256.csv",
        RESULTS / "kerr_scalar_power_near_extremal_dense22_N288.csv",
    ),
    (
        RESULTS / "kerr_scalar_power_near_extremal_dense33_N256.csv",
        RESULTS / "kerr_scalar_power_near_extremal_dense33_N288.csv",
    ),
    (
        RESULTS / "kerr_scalar_power_near_extremal_ultra_principal_N288.csv",
        RESULTS / "kerr_scalar_power_near_extremal_ultra_principal_N320.csv",
    ),
)
CUBIC_THRESHOLD = RESULTS / "kerr_scalar_modal_powerlaw_threshold_values.csv"
CUBIC_FIXED_Y = RESULTS / "kerr_scalar_modal_powerlaw_fixed_y_values.csv"
THRESHOLD_OUT = RESULTS / "kerr_scalar_power_near_extremal_threshold_values.csv"
FIXED_Y_OUT = RESULTS / "kerr_scalar_power_near_extremal_fixed_y_values.csv"
FITS_OUT = RESULTS / "kerr_scalar_power_near_extremal_fits.csv"
FIGURE_OUT = FIGURES / "kerr_scalar_power_near_extremal_scaling.png"

THRESHOLD_Y = (0.025, 0.05)
FIXED_Y = (-0.5, 0.5, 1.0)
RESPONSE_GATE = 5.0e-4
LINEAR_GATE = 2.0e-8
WRONSKIAN_GATE = 1.0e-12
NONLINEAR_ABSOLUTE_GATE = 1.0e-8
NONLINEAR_RELATIVE_GATE = 2.0e-8
PRIMARY_FIT_WINDOW = "nearest7"


@dataclass(frozen=True)
class PairedValue:
    n: int
    a: float
    l: int
    m: int
    kappa: float
    y: float
    response: float
    response_low: float
    resolution_change: float
    linear_balance: float
    nonlinear_balance: float
    nonlinear_relative_balance: float
    wronskian_error: float
    accepted: bool


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def relative_change(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def row_key(row: dict[str, str]) -> tuple[int, float, int, int, float]:
    return (
        int(row["nonlinearity_order"]),
        round(float(row["a"]), 12),
        int(row["l"]),
        int(row["m"]),
        round(float(row["detuning_over_kappa"]), 12),
    )


def pair_rows(low_path: Path, high_path: Path) -> dict[tuple[int, float, int, int, float], PairedValue]:
    low = {row_key(row): row for row in read_csv(low_path)}
    high = {row_key(row): row for row in read_csv(high_path)}
    output = {}
    for key in sorted(low.keys() & high.keys()):
        n, a, l, m, y = key
        low_response = float(low[key]["horizon_response"])
        response = float(high[key]["horizon_response"])
        change = relative_change(low_response, response)
        linear = max(abs(float(low[key]["linear_balance"])), abs(float(high[key]["linear_balance"])))
        nonlinear = max(
            abs(float(low[key]["nonlinear_balance"])),
            abs(float(high[key]["nonlinear_balance"])),
        )
        nonlinear_relative = max(
            abs(float(row["nonlinear_balance"]))
            / max(abs(float(row["T1"])), abs(float(row["R1"])), 1.0e-300)
            for row in (low[key], high[key])
        )
        wronskian = max(
            float(low[key]["wronskian_relative_error"]),
            float(high[key]["wronskian_relative_error"]),
        )
        output[key] = PairedValue(
            n=n,
            a=a,
            l=l,
            m=m,
            kappa=float(high[key]["surface_gravity"]),
            y=y,
            response=response,
            response_low=low_response,
            resolution_change=change,
            linear_balance=linear,
            nonlinear_balance=nonlinear,
            nonlinear_relative_balance=nonlinear_relative,
            wronskian_error=wronskian,
            accepted=(
                change <= RESPONSE_GATE
                and linear <= LINEAR_GATE
                and (
                    nonlinear <= NONLINEAR_ABSOLUTE_GATE
                    or nonlinear_relative <= NONLINEAR_RELATIVE_GATE
                )
                and wronskian <= WRONSKIAN_GATE
            ),
        )
    return output


def load_pairs() -> dict[tuple[int, float, int, int, float], PairedValue]:
    output = {}
    for low_path, high_path in INPUT_PAIRS:
        if low_path.exists() != high_path.exists():
            raise FileNotFoundError(f"Incomplete resolution pair: {low_path}, {high_path}")
        if low_path.exists():
            output.update(pair_rows(low_path, high_path))
    if not output:
        raise FileNotFoundError("No complete higher-power resolution pairs found")
    return output


def threshold_extrapolation(values: dict[tuple[int, float, int, int, float], PairedValue]):
    output = []
    for n, a, l, m in sorted({key[:4] for key in values}):
        samples = {
            y: values.get((n, a, l, m, round(y, 12)))
            for y in (-0.05, -0.025, 0.025, 0.05)
        }
        if any(value is None for value in samples.values()):
            continue
        typed = {y: value for y, value in samples.items() if value is not None}

        def extrapolate(field: str) -> tuple[float, float, float]:
            inner = 0.5 * (getattr(typed[-0.025], field) + getattr(typed[0.025], field))
            outer = 0.5 * (getattr(typed[-0.05], field) + getattr(typed[0.05], field))
            return (4.0 * inner - outer) / 3.0, inner, outer

        response, inner, outer = extrapolate("response")
        response_low, _, _ = extrapolate("response_low")
        extrapolated_change = relative_change(response_low, response)
        accepted = (
            all(value.accepted for value in typed.values())
            and response > 0.0
            and extrapolated_change <= RESPONSE_GATE
        )
        output.append({
            "nonlinearity_order": n,
            "a": f"{a:.16e}",
            "l": l,
            "m": m,
            "surface_gravity": f"{typed[0.025].kappa:.16e}",
            "regime": "threshold_p_equals_0_limit",
            "detuning_over_kappa": "0.0000000000000000e+00",
            "sample_detunings": "-0.05,-0.025,0.025,0.05",
            "horizon_response": f"{response:.16e}",
            "order_rescaled_response": f"{typed[0.025].kappa**n * response:.16e}",
            "horizon_response_low": f"{response_low:.16e}",
            "resolution_relative_change": f"{extrapolated_change:.16e}",
            "max_sample_resolution_change": f"{max(value.resolution_change for value in typed.values()):.16e}",
            "richardson_relative_correction": f"{relative_change(inner, response):.16e}",
            "even_inner_response": f"{inner:.16e}",
            "even_outer_response": f"{outer:.16e}",
            "max_linear_balance": f"{max(value.linear_balance for value in typed.values()):.16e}",
            "max_nonlinear_balance": f"{max(value.nonlinear_balance for value in typed.values()):.16e}",
            "max_nonlinear_relative_balance": f"{max(value.nonlinear_relative_balance for value in typed.values()):.16e}",
            "max_wronskian_relative_error": f"{max(value.wronskian_error for value in typed.values()):.16e}",
            "accepted": "true" if accepted else "false",
        })
    return output


def fixed_y_values(values: dict[tuple[int, float, int, int, float], PairedValue]):
    output = []
    for value in sorted(values.values(), key=lambda item: (item.n, item.a, item.l, item.m, item.y)):
        if not any(np.isclose(value.y, target) for target in FIXED_Y):
            continue
        output.append({
            "nonlinearity_order": value.n,
            "a": f"{value.a:.16e}",
            "l": value.l,
            "m": value.m,
            "surface_gravity": f"{value.kappa:.16e}",
            "regime": "fixed_nonzero_y",
            "detuning_over_kappa": f"{value.y:.16e}",
            "horizon_response": f"{value.response:.16e}",
            "order_rescaled_response": f"{value.kappa**value.n * value.response:.16e}",
            "horizon_response_low": f"{value.response_low:.16e}",
            "resolution_relative_change": f"{value.resolution_change:.16e}",
            "max_linear_balance": f"{value.linear_balance:.16e}",
            "max_nonlinear_balance": f"{value.nonlinear_balance:.16e}",
            "max_nonlinear_relative_balance": f"{value.nonlinear_relative_balance:.16e}",
            "max_wronskian_relative_error": f"{value.wronskian_error:.16e}",
            "accepted": "true" if value.accepted and value.response > 0.0 else "false",
        })
    return output


def add_cubic_rows(path: Path, regime: str) -> list[dict[str, object]]:
    rows = []
    for source in read_csv(path):
        if source["accepted"] != "true" or (int(source["l"]), int(source["m"])) not in {(1, 1), (2, 2)}:
            continue
        if regime == "fixed_nonzero_y" and not any(
            np.isclose(float(source["detuning_over_kappa"]), target) for target in FIXED_Y
        ):
            continue
        row = dict(source)
        row["nonlinearity_order"] = 1
        row["order_rescaled_response"] = f"{float(source['surface_gravity']) * float(source['horizon_response']):.16e}"
        rows.append(row)
    return rows


def power_fit(rows: list[dict[str, object]]) -> dict[str, float]:
    kappa = np.array([float(row["surface_gravity"]) for row in rows])
    response = np.array([float(row["horizon_response"]) for row in rows])
    x = np.log(kappa)
    z = np.log(response)
    slope, intercept = np.polyfit(x, z, 1)
    residual = z - (intercept + slope * x)
    total = np.sum((z - np.mean(z)) ** 2)
    degrees_of_freedom = len(rows) - 2
    slope_standard_error = 0.0
    if degrees_of_freedom > 0:
        centered_x = x - np.mean(x)
        slope_standard_error = float(
            np.sqrt(
                np.sum(residual**2)
                / degrees_of_freedom
                / np.sum(centered_x**2)
            )
        )
    t_critical = float(student_t.ppf(0.975, degrees_of_freedom))
    alpha = float(-slope)
    alpha_ci_half_width = t_critical * slope_standard_error

    loo_log_errors = []
    for omitted in range(len(rows)):
        keep = np.arange(len(rows)) != omitted
        loo_slope, loo_intercept = np.polyfit(x[keep], z[keep], 1)
        loo_log_errors.append(float(loo_intercept + loo_slope * x[omitted] - z[omitted]))
    loo_log_errors = np.asarray(loo_log_errors)
    return {
        "amplitude": float(np.exp(intercept)),
        "alpha": alpha,
        "r_squared": float(1.0 - np.sum(residual**2) / total) if total > 0.0 else 1.0,
        "rms_log_residual": float(np.sqrt(np.mean(residual**2))),
        "max_abs_log_residual": float(np.max(np.abs(residual))),
        "alpha_standard_error": slope_standard_error,
        "alpha_ci95_low": alpha - alpha_ci_half_width,
        "alpha_ci95_high": alpha + alpha_ci_half_width,
        "loo_rms_log_prediction": float(np.sqrt(np.mean(loo_log_errors**2))),
        "loo_max_relative_prediction_error": float(
            np.max(np.abs(np.exp(loo_log_errors) - 1.0))
        ),
    }


def fit_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    datasets: dict[tuple[int, str, int, int, float], list[dict[str, object]]] = {}
    for row in rows:
        if row["accepted"] != "true":
            continue
        key = (
            int(row["nonlinearity_order"]),
            str(row["regime"]),
            int(row["l"]),
            int(row["m"]),
            round(float(row["detuning_over_kappa"]), 12),
        )
        datasets.setdefault(key, []).append(row)

    output = []
    for (n, regime, l, m, y), dataset in sorted(datasets.items()):
        dataset = sorted(dataset, key=lambda row: float(row["surface_gravity"]), reverse=True)
        if len(dataset) < 4:
            continue
        _, _, _, conformal_class = conformal_data(l, m)
        windows = [("all", dataset)]
        windows.extend(
            (f"nearest{count}", dataset[-count:])
            for count in (7, 6, 5, 4, 3)
            if len(dataset) >= count
        )
        for window, subset in windows:
            fit = power_fit(subset)
            alpha_difference = fit["alpha"] - n
            if conformal_class == "principal_complex_h" and abs(alpha_difference) <= 0.2:
                classification = "order_locked_principal"
            elif fit["alpha"] < n - 0.2:
                classification = "sub_order_suppressed"
            else:
                classification = "crossover"
            output.append({
                "nonlinearity_order": n,
                "regime": regime,
                "l": l,
                "m": m,
                "detuning_over_kappa": f"{y:.16e}",
                "fit_window": window,
                "spin_count": len(subset),
                "spin_min": f"{min(float(row['a']) for row in subset):.16e}",
                "spin_max": f"{max(float(row['a']) for row in subset):.16e}",
                "kappa_min": f"{min(float(row['surface_gravity']) for row in subset):.16e}",
                "kappa_max": f"{max(float(row['surface_gravity']) for row in subset):.16e}",
                "amplitude": f"{fit['amplitude']:.16e}",
                "alpha": f"{fit['alpha']:.16e}",
                "predicted_order_locked_alpha": f"{float(n):.16e}",
                "alpha_minus_n": f"{alpha_difference:.16e}",
                "alpha_over_n": f"{fit['alpha'] / n:.16e}",
                "r_squared": f"{fit['r_squared']:.16e}",
                "rms_log_residual": f"{fit['rms_log_residual']:.16e}",
                "max_abs_log_residual": f"{fit['max_abs_log_residual']:.16e}",
                "alpha_standard_error": f"{fit['alpha_standard_error']:.16e}",
                "alpha_ci95_low": f"{fit['alpha_ci95_low']:.16e}",
                "alpha_ci95_high": f"{fit['alpha_ci95_high']:.16e}",
                "loo_rms_log_prediction": f"{fit['loo_rms_log_prediction']:.16e}",
                "loo_max_relative_prediction_error": f"{fit['loo_max_relative_prediction_error']:.16e}",
                "max_resolution_relative_change": f"{max(float(row['resolution_relative_change']) for row in subset):.16e}",
                "conformal_class": conformal_class,
                "classification": classification,
            })
    return output


def subset(rows, *, n, mode, y=0.0):
    return sorted(
        [
            row for row in rows
            if int(row["nonlinearity_order"]) == n
            and (int(row["l"]), int(row["m"])) == mode
            and np.isclose(float(row["detuning_over_kappa"]), y)
            and row["accepted"] == "true"
        ],
        key=lambda row: float(row["surface_gravity"]),
        reverse=True,
    )


def plot(all_rows: list[dict[str, object]], fits: list[dict[str, object]]) -> None:
    colors = {1: "#0072B2", 2: "#D55E00", 3: "#009E73"}
    markers = {1: "o", 2: "s", 3: "^"}
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.25))

    for n in (1, 2, 3):
        principal = subset(all_rows, n=n, mode=(2, 2))
        supplementary = subset(all_rows, n=n, mode=(1, 1))
        if principal:
            kappa = np.array([float(row["surface_gravity"]) for row in principal])
            response = np.array([float(row["horizon_response"]) for row in principal])
            axes[0, 0].plot(kappa, response, color=colors[n], marker=markers[n], markersize=3, linewidth=0.9, label=rf"$n={n}$")
            axes[0, 1].plot(kappa, kappa**n * response, color=colors[n], marker=markers[n], markersize=3, linewidth=0.9, label=rf"$n={n}$")
        if supplementary:
            axes[1, 0].plot(
                [float(row["surface_gravity"]) for row in supplementary],
                [float(row["horizon_response"]) for row in supplementary],
                color=colors[n], marker=markers[n], markersize=3, linewidth=0.9,
                label=rf"$n={n}$",
            )

    for ax in (axes[0, 0], axes[0, 1], axes[1, 0]):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.invert_xaxis()
        ax.grid(True, which="both", alpha=0.18)
        ax.set_xlabel(r"$M\kappa$")
        ax.legend(frameon=False, fontsize=7)
    axes[0, 0].set_ylabel(r"$M^{2n-2}\chi_{H,22}^{(n)}$")
    axes[0, 0].set_title(r"Principal mode, $p\to0$")
    axes[0, 1].set_ylabel(r"$(M\kappa)^nM^{2n-2}\chi_{H,22}^{(n)}$")
    axes[0, 1].set_title("Empirical order collapse")
    axes[1, 0].set_ylabel(r"$M^{2n-2}\chi_{H,11}^{(n)}$")
    axes[1, 0].set_title(r"Supplementary finite-window response")

    nearest = [row for row in fits if row["fit_window"] == PRIMARY_FIT_WINDOW]
    styles = {
        ((2, 2), 0.0): ("#D55E00", "o", r"$(2,2),\ p\to0$"),
        ((2, 2), 0.5): ("#D55E00", "s", r"$(2,2),\ y=0.5$"),
        ((1, 1), 0.0): ("#0072B2", "o", r"$(1,1),\ p\to0$"),
        ((1, 1), 0.5): ("#0072B2", "s", r"$(1,1),\ y=0.5$"),
    }
    axes[1, 1].plot([1, 3], [1, 3], color="0.35", linestyle=":", linewidth=0.9, label=r"$\alpha=n$")
    for (mode, y), (color, marker, label) in styles.items():
        selected = [
            row for row in nearest
            if (int(row["l"]), int(row["m"])) == mode
            and np.isclose(float(row["detuning_over_kappa"]), y)
        ]
        selected.sort(key=lambda row: int(row["nonlinearity_order"]))
        axes[1, 1].plot(
            [int(row["nonlinearity_order"]) for row in selected],
            [float(row["alpha"]) for row in selected],
            color=color, marker=marker, markersize=4, linewidth=0.9, label=label,
        )
    axes[1, 1].set_xlabel(r"nonlinearity order $n$")
    axes[1, 1].set_ylabel(r"seven-point effective $\alpha_n$")
    axes[1, 1].set_xticks([1, 2, 3])
    axes[1, 1].set_title("Finite-window slopes")
    axes[1, 1].grid(True, alpha=0.18)
    axes[1, 1].legend(frameon=False, fontsize=6.3, ncol=2)

    fig.tight_layout()
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    paired = load_pairs()
    thresholds = threshold_extrapolation(paired)
    fixed = fixed_y_values(paired)
    write_csv(THRESHOLD_OUT, thresholds)
    write_csv(FIXED_Y_OUT, fixed)

    all_thresholds = add_cubic_rows(CUBIC_THRESHOLD, "threshold_p_equals_0_limit") + thresholds
    all_fixed = add_cubic_rows(CUBIC_FIXED_Y, "fixed_nonzero_y") + fixed
    fits = fit_rows(all_thresholds + all_fixed)
    write_csv(FITS_OUT, fits)
    plot(all_thresholds + all_fixed, fits)

    print(f"paired higher-power samples = {len(paired)}")
    print(f"accepted threshold limits = {sum(row['accepted'] == 'true' for row in thresholds)}")
    print(f"accepted fixed-y values = {sum(row['accepted'] == 'true' for row in fixed)}")
    for row in fits:
        if row["fit_window"] == PRIMARY_FIT_WINDOW and np.isclose(float(row["detuning_over_kappa"]), 0.0):
            print(
                f"n={row['nonlinearity_order']} mode=({row['l']},{row['m']}) "
                f"alpha={float(row['alpha']):.6f} alpha-n={float(row['alpha_minus_n']):+.3e} "
                f"CI95=[{float(row['alpha_ci95_low']):.6f},"
                f"{float(row['alpha_ci95_high']):.6f}] "
                f"R2={float(row['r_squared']):.8f} "
                f"LOOmax={float(row['loo_max_relative_prediction_error']):.3e} "
                f"{row['classification']}"
            )
    print(f"saved = {FIGURE_OUT}")


if __name__ == "__main__":
    main()
