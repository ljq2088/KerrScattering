"""Classify modal near-extremal power laws at threshold and fixed p/kappa.

The exact-threshold value is not obtained from a degenerate p=0 radial solve.
For every spin and mode, responses at y=p/kappa=+/-0.025 and +/-0.05 are
symmetrized and Richardson extrapolated to y=0.  Fixed-y fits use the raw
nonzero-y rows independently.  Low- and high-resolution files are paired
before either type of fit is admitted.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.teukolsky_scalar import scalar_spheroidal_eigenvalue


RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

INPUT_PAIRS = (
    (
        RESULTS / "kerr_scalar_modal_powerlaw_N144.csv",
        RESULTS / "kerr_scalar_modal_powerlaw_N176.csv",
    ),
    (
        RESULTS / "kerr_scalar_modal_powerlaw_extreme_N144.csv",
        RESULTS / "kerr_scalar_modal_powerlaw_extreme_N176.csv",
    ),
    (
        RESULTS / "kerr_scalar_modal_powerlaw_subdominant_refine_N224.csv",
        RESULTS / "kerr_scalar_modal_powerlaw_subdominant_refine_N256.csv",
    ),
)
THRESHOLD_VALUES_OUT = RESULTS / "kerr_scalar_modal_powerlaw_threshold_values.csv"
FIXED_Y_VALUES_OUT = RESULTS / "kerr_scalar_modal_powerlaw_fixed_y_values.csv"
FITS_OUT = RESULTS / "kerr_scalar_modal_powerlaw_fits.csv"
MODEL_COMPARISON_OUT = RESULTS / "kerr_scalar_modal_powerlaw_model_comparison.csv"
FIGURE_OUT = FIGURES / "kerr_scalar_modal_powerlaw_classification.png"

THRESHOLD_Y = (0.025, 0.05)
FIXED_Y = (-0.5, 0.5, 1.0)
RESPONSE_GATE = 5.0e-4
LINEAR_GATE = 2.0e-8
WRONSKIAN_GATE = 1.0e-12


@dataclass(frozen=True)
class PairedValue:
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


def row_key(row: dict[str, str]) -> tuple[float, int, int, float]:
    return (
        round(float(row["a"]), 12),
        int(row["l"]),
        int(row["m"]),
        round(float(row["detuning_over_kappa"]), 12),
    )


def pair_rows(low_path: Path, high_path: Path) -> dict[tuple[float, int, int, float], PairedValue]:
    low = {row_key(row): row for row in read_csv(low_path)}
    high = {row_key(row): row for row in read_csv(high_path)}
    output = {}
    for key in sorted(low.keys() & high.keys()):
        a, l, m, y = key
        response_low = float(low[key]["horizon_response"])
        response = float(high[key]["horizon_response"])
        change = relative_change(response_low, response)
        linear = max(abs(float(low[key]["linear_balance"])), abs(float(high[key]["linear_balance"])))
        nonlinear = max(
            abs(float(low[key]["nonlinear_balance"])),
            abs(float(high[key]["nonlinear_balance"])),
        )
        wronskian = max(
            float(low[key]["wronskian_relative_error"]),
            float(high[key]["wronskian_relative_error"]),
        )
        output[key] = PairedValue(
            a=a,
            l=l,
            m=m,
            kappa=float(high[key]["surface_gravity"]),
            y=y,
            response=response,
            response_low=response_low,
            resolution_change=change,
            linear_balance=linear,
            nonlinear_balance=nonlinear,
            wronskian_error=wronskian,
            accepted=(
                change <= RESPONSE_GATE
                and linear <= LINEAR_GATE
                and wronskian <= WRONSKIAN_GATE
            ),
        )
    return output


def load_all_pairs() -> dict[tuple[float, int, int, float], PairedValue]:
    output = {}
    for low_path, high_path in INPUT_PAIRS:
        if not low_path.exists() or not high_path.exists():
            raise FileNotFoundError(f"Missing paired inputs: {low_path}, {high_path}")
        # Later, higher-resolution pairs intentionally replace duplicate rows.
        output.update(pair_rows(low_path, high_path))
    return output


def conformal_data(l: int, m: int) -> tuple[float, float, float, str]:
    angular_a = scalar_spheroidal_eigenvalue(l, m, m / 2.0, lmax_extra=32)
    angular_k = angular_a + m**2 / 4.0
    discriminant = 0.25 + angular_k - 2.0 * m**2
    if discriminant < 0.0:
        return angular_k, 0.5, float(np.sqrt(-discriminant)), "principal_complex_h"
    return angular_k, 0.5 + float(np.sqrt(discriminant)), 0.0, "supplementary_real_h"


def threshold_extrapolation(
    values: dict[tuple[float, int, int, float], PairedValue],
) -> list[dict[str, object]]:
    mode_spins = sorted({key[:3] for key in values})
    output = []
    for a, l, m in mode_spins:
        samples = {
            y: values.get((a, l, m, round(y, 12)))
            for y in (-0.05, -0.025, 0.025, 0.05)
        }
        if any(value is None for value in samples.values()):
            continue
        typed_samples = {y: value for y, value in samples.items() if value is not None}

        def extrapolate(field: str) -> tuple[float, float, float]:
            inner = 0.5 * (
                getattr(typed_samples[-0.025], field)
                + getattr(typed_samples[0.025], field)
            )
            outer = 0.5 * (
                getattr(typed_samples[-0.05], field)
                + getattr(typed_samples[0.05], field)
            )
            return (4.0 * inner - outer) / 3.0, inner, outer

        response, inner, outer = extrapolate("response")
        response_low, _, _ = extrapolate("response_low")
        max_sample_change = max(value.resolution_change for value in typed_samples.values())
        extrapolated_change = relative_change(response_low, response)
        accepted = (
            all(value.accepted for value in typed_samples.values())
            and response > 0.0
            and extrapolated_change <= RESPONSE_GATE
        )
        output.append({
            "a": f"{a:.16e}",
            "l": l,
            "m": m,
            "surface_gravity": f"{typed_samples[0.025].kappa:.16e}",
            "regime": "threshold_p_equals_0_limit",
            "detuning_over_kappa": "0.0000000000000000e+00",
            "sample_detunings": "-0.05,-0.025,0.025,0.05",
            "horizon_response": f"{response:.16e}",
            "scaled_horizon_response": f"{typed_samples[0.025].kappa * response:.16e}",
            "horizon_response_N144": f"{response_low:.16e}",
            "resolution_relative_change": f"{extrapolated_change:.16e}",
            "max_sample_resolution_change": f"{max_sample_change:.16e}",
            "richardson_relative_correction": f"{relative_change(inner, response):.16e}",
            "even_inner_response": f"{inner:.16e}",
            "even_outer_response": f"{outer:.16e}",
            "max_linear_balance": f"{max(value.linear_balance for value in typed_samples.values()):.16e}",
            "max_nonlinear_balance": f"{max(value.nonlinear_balance for value in typed_samples.values()):.16e}",
            "max_wronskian_relative_error": f"{max(value.wronskian_error for value in typed_samples.values()):.16e}",
            "accepted": "true" if accepted else "false",
        })
    return output


def fixed_y_values(
    values: dict[tuple[float, int, int, float], PairedValue],
) -> list[dict[str, object]]:
    output = []
    for key, value in sorted(values.items()):
        if not any(np.isclose(value.y, target) for target in FIXED_Y):
            continue
        output.append({
            "a": f"{value.a:.16e}",
            "l": value.l,
            "m": value.m,
            "surface_gravity": f"{value.kappa:.16e}",
            "regime": "fixed_nonzero_y",
            "detuning_over_kappa": f"{value.y:.16e}",
            "horizon_response": f"{value.response:.16e}",
            "scaled_horizon_response": f"{value.kappa * value.response:.16e}",
            "horizon_response_N144": f"{value.response_low:.16e}",
            "resolution_relative_change": f"{value.resolution_change:.16e}",
            "max_linear_balance": f"{value.linear_balance:.16e}",
            "max_nonlinear_balance": f"{value.nonlinear_balance:.16e}",
            "max_wronskian_relative_error": f"{value.wronskian_error:.16e}",
            "accepted": "true" if value.accepted and value.response > 0.0 else "false",
        })
    return output


def power_fit(kappa: np.ndarray, response: np.ndarray) -> dict[str, float]:
    x = np.log(kappa)
    z = np.log(response)
    slope, intercept = np.polyfit(x, z, 1)
    prediction = intercept + slope * x
    residual = z - prediction
    total = np.sum((z - np.mean(z)) ** 2)
    return {
        "amplitude": float(np.exp(intercept)),
        "alpha": float(-slope),
        "r_squared": float(1.0 - np.sum(residual**2) / total) if total > 0.0 else 1.0,
        "rms_log_residual": float(np.sqrt(np.mean(residual**2))),
        "rss": float(np.sum((response - np.exp(prediction)) ** 2)),
    }


def finite_limit_fit(kappa: np.ndarray, response: np.ndarray) -> dict[str, float]:
    scale = max(float(np.max(response)), 1.0e-12)

    def residual(parameters: np.ndarray) -> np.ndarray:
        c0, c1, beta = parameters
        return (c0 + c1 * kappa**beta - response) / scale

    initial = np.array([1.05 * response[-1], response[0] - response[-1], 0.5])
    fit = least_squares(
        residual,
        initial,
        bounds=([0.0, -1000.0 * scale, 0.05], [1000.0 * scale, 1000.0 * scale, 5.0]),
        max_nfev=100000,
        xtol=1.0e-14,
        ftol=1.0e-14,
        gtol=1.0e-14,
    )
    c0, c1, beta = fit.x
    prediction = c0 + c1 * kappa**beta
    return {
        "c0": float(c0),
        "c1": float(c1),
        "beta": float(beta),
        "rss": float(np.sum((response - prediction) ** 2)),
    }


def information_criteria(rss: float, count: int, parameters: int) -> tuple[float, float]:
    rss_floor = max(rss, np.finfo(float).tiny)
    aic = count * np.log(rss_floor / count) + 2.0 * parameters
    correction = (
        2.0 * parameters * (parameters + 1.0) / (count - parameters - 1.0)
        if count > parameters + 1
        else float("inf")
    )
    return float(aic), float(aic + correction)


def classify(window_fits: dict[str, dict[str, float]]) -> str:
    nearest3 = window_fits["nearest3"]
    nearest4 = window_fits["nearest4"]
    alpha = nearest3["alpha"]
    stable = abs(alpha - nearest4["alpha"]) <= 0.10
    if 0.80 <= alpha <= 1.20 and stable and nearest3["r_squared"] >= 0.995:
        return "inverse_kappa"
    if alpha <= 0.15 and alpha <= nearest4["alpha"] + 0.02:
        return "bounded_candidate"
    if (
        alpha <= 0.25
        and stable
        and nearest3["r_squared"] >= 0.98
        and alpha <= nearest4["alpha"] + 0.02
    ):
        return "bounded_candidate"
    return "crossover_or_fractional"


def fit_rows(thresholds: list[dict[str, object]], fixed: list[dict[str, object]]):
    datasets: dict[tuple[str, int, int, float], list[dict[str, object]]] = {}
    for row in thresholds + fixed:
        if row["accepted"] != "true":
            continue
        key = (
            str(row["regime"]),
            int(row["l"]),
            int(row["m"]),
            round(float(row["detuning_over_kappa"]), 12),
        )
        datasets.setdefault(key, []).append(row)

    output = []
    model_rows = []
    for key, rows in sorted(datasets.items()):
        regime, l, m, y = key
        angular_k, h_real, h_imag, conformal_class = conformal_data(l, m)
        rows = sorted(rows, key=lambda row: float(row["surface_gravity"]), reverse=True)
        if len(rows) < 4:
            continue
        windows = {
            "all": rows,
            "nearest4": rows[-4:],
            "nearest3": rows[-3:],
        }
        window_fits = {}
        for name, subset in windows.items():
            kappa = np.array([float(row["surface_gravity"]) for row in subset])
            response = np.array([float(row["horizon_response"]) for row in subset])
            result = power_fit(kappa, response)
            window_fits[name] = result
            output.append({
                "regime": regime,
                "l": l,
                "m": m,
                "detuning_over_kappa": f"{y:.16e}",
                "fit_window": name,
                "spin_count": len(subset),
                "spin_min": f"{min(float(row['a']) for row in subset):.16e}",
                "spin_max": f"{max(float(row['a']) for row in subset):.16e}",
                "kappa_min": f"{min(kappa):.16e}",
                "kappa_max": f"{max(kappa):.16e}",
                "amplitude": f"{result['amplitude']:.16e}",
                "alpha": f"{result['alpha']:.16e}",
                "r_squared": f"{result['r_squared']:.16e}",
                "rms_log_residual": f"{result['rms_log_residual']:.16e}",
                "max_resolution_relative_change": f"{max(float(row['resolution_relative_change']) for row in subset):.16e}",
                "extremal_angular_K": f"{angular_k:.16e}",
                "conformal_weight_real": f"{h_real:.16e}",
                "conformal_weight_imag_abs": f"{h_imag:.16e}",
                "conformal_class": conformal_class,
                "classification": "pending",
            })
        classification = classify(window_fits)
        for row in output[-3:]:
            row["classification"] = classification

        kappa = np.array([float(row["surface_gravity"]) for row in rows])
        response = np.array([float(row["horizon_response"]) for row in rows])
        pure = power_fit(kappa, response)
        finite = finite_limit_fit(kappa, response)
        pure_aic, pure_aicc = information_criteria(pure["rss"], len(rows), 2)
        finite_aic, finite_aicc = information_criteria(finite["rss"], len(rows), 3)
        model_rows.append({
            "regime": regime,
            "l": l,
            "m": m,
            "detuning_over_kappa": f"{y:.16e}",
            "spin_count": len(rows),
            "pure_power_alpha": f"{pure['alpha']:.16e}",
            "pure_power_amplitude": f"{pure['amplitude']:.16e}",
            "pure_power_rss": f"{pure['rss']:.16e}",
            "pure_power_aicc": f"{pure_aicc:.16e}",
            "finite_limit_c0": f"{finite['c0']:.16e}",
            "finite_limit_c1": f"{finite['c1']:.16e}",
            "finite_limit_beta": f"{finite['beta']:.16e}",
            "finite_limit_rss": f"{finite['rss']:.16e}",
            "finite_limit_aicc": f"{finite_aicc:.16e}",
            "delta_aicc_finite_minus_power": f"{finite_aicc - pure_aicc:.16e}",
            "extremal_angular_K": f"{angular_k:.16e}",
            "conformal_weight_real": f"{h_real:.16e}",
            "conformal_weight_imag_abs": f"{h_imag:.16e}",
            "conformal_class": conformal_class,
            "classification": classification,
        })
    return output, model_rows


def local_exponents(rows: list[dict[str, object]]) -> tuple[np.ndarray, np.ndarray]:
    rows = sorted(rows, key=lambda row: float(row["surface_gravity"]), reverse=True)
    kappa = np.array([float(row["surface_gravity"]) for row in rows])
    response = np.array([float(row["horizon_response"]) for row in rows])
    centers = np.sqrt(kappa[:-1] * kappa[1:])
    alpha = -np.diff(np.log(response)) / np.diff(np.log(kappa))
    return centers, alpha


def plot(thresholds: list[dict[str, object]], fits: list[dict[str, object]]) -> None:
    accepted = [row for row in thresholds if row["accepted"] == "true"]
    modes = sorted({(int(row["l"]), int(row["m"])) for row in accepted})
    colors = {
        (1, 1): "#0072B2",
        (2, 2): "#D55E00",
        (3, 3): "#009E73",
        (4, 4): "#CC79A7",
        (5, 5): "#8C564B",
        (2, 1): "#E69F00",
        (3, 2): "#6F6F6F",
    }
    markers = {(1, 1): "o", (2, 2): "s", (3, 3): "^", (4, 4): "D", (5, 5): "v", (2, 1): "P", (3, 2): "X"}
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.75))

    for mode in modes:
        subset = [row for row in accepted if (int(row["l"]), int(row["m"])) == mode]
        subset = sorted(subset, key=lambda row: float(row["surface_gravity"]), reverse=True)
        label = rf"$({mode[0]},{mode[1]})$"
        axes[0].plot(
            [float(row["surface_gravity"]) for row in subset],
            [float(row["horizon_response"]) for row in subset],
            color=colors[mode], marker=markers[mode], markersize=3.0,
            linewidth=0.9, label=label,
        )
        centers, alpha = local_exponents(subset)
        axes[1].plot(
            centers, alpha, color=colors[mode], marker=markers[mode],
            markersize=3.0, linewidth=0.9,
        )

    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].invert_xaxis()
    axes[0].set_xlabel(r"$M\kappa$")
    axes[0].set_ylabel(r"$\chi_H^\star$")
    axes[0].set_title(r"Threshold: $p\to0$")
    axes[0].legend(frameon=False, fontsize=5.8, ncol=2)

    axes[1].axhline(1.0, color="0.4", linestyle=":", linewidth=0.8)
    axes[1].axhline(0.0, color="0.4", linestyle=":", linewidth=0.8)
    axes[1].set_xscale("log")
    axes[1].invert_xaxis()
    axes[1].set_xlabel(r"pair center $M\kappa$")
    axes[1].set_ylabel(r"local $\alpha_{\rm eff}$")
    axes[1].set_title("Window drift")

    nearest = [row for row in fits if row["fit_window"] == "nearest3"]
    positions = np.arange(len(modes), dtype=float)
    offsets = {-0.5: -0.24, 0.0: -0.08, 0.5: 0.08, 1.0: 0.24}
    y_colors = {-0.5: "#0072B2", 0.0: "#000000", 0.5: "#D55E00", 1.0: "#009E73"}
    for y in (-0.5, 0.0, 0.5, 1.0):
        values = []
        for l, m in modes:
            candidates = [
                row for row in nearest
                if int(row["l"]) == l and int(row["m"]) == m
                and np.isclose(float(row["detuning_over_kappa"]), y)
            ]
            values.append(float(candidates[0]["alpha"]) if candidates else np.nan)
        axes[2].scatter(
            positions + offsets[y], values, s=18, color=y_colors[y],
            marker="o" if y == 0.0 else "s", label=rf"$y={y:g}$", zorder=3,
        )
    axes[2].axhline(1.0, color="0.4", linestyle=":", linewidth=0.8)
    axes[2].axhline(0.0, color="0.4", linestyle=":", linewidth=0.8)
    axes[2].set_xticks(positions)
    axes[2].set_xticklabels([rf"${l}{m}$" for l, m in modes])
    axes[2].set_xlabel(r"mode $(\ell m)$")
    axes[2].set_ylabel(r"nearest-three effective $\alpha$")
    axes[2].set_title("Finite-window slopes")
    axes[2].legend(frameon=False, fontsize=5.8, ncol=2)

    for ax in axes:
        ax.grid(True, which="both", alpha=0.18)
        ax.xaxis.set_minor_formatter(NullFormatter())
    fig.tight_layout()
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    paired = load_all_pairs()
    thresholds = threshold_extrapolation(paired)
    fixed = fixed_y_values(paired)
    fits, model_comparison = fit_rows(thresholds, fixed)
    write_csv(THRESHOLD_VALUES_OUT, thresholds)
    write_csv(FIXED_Y_VALUES_OUT, fixed)
    write_csv(FITS_OUT, fits)
    write_csv(MODEL_COMPARISON_OUT, model_comparison)
    plot(thresholds, fits)
    print(f"paired samples = {len(paired)}")
    print(f"accepted threshold limits = {sum(row['accepted'] == 'true' for row in thresholds)}")
    print(f"accepted fixed-y samples = {sum(row['accepted'] == 'true' for row in fixed)}")
    for row in fits:
        if row["fit_window"] == "nearest3":
            print(
                f"mode=({row['l']},{row['m']}) y={float(row['detuning_over_kappa']):g} "
                f"alpha={float(row['alpha']):.6f} R2={float(row['r_squared']):.6f} "
                f"class={row['classification']}"
            )
    print(f"saved = {FIGURE_OUT}")


if __name__ == "__main__":
    main()
