"""Audit finite-bandwidth scaling and peak migration in principal modes.

The raw calculations are paired in spectral order.  This script applies the
same acceptance gates as the near-extremal response analysis, integrates the
accepted monochromatic susceptibilities over a fixed throat-frequency window,
and fits the dense peak scans locally in ``log(response)``.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

BAND_LOW = RESULTS / "kerr_scalar_power_band_N256.csv"
BAND_HIGH = RESULTS / "kerr_scalar_power_band_N288.csv"
CUBIC_BAND_LOW = RESULTS / "kerr_scalar_near_extremal_scaling_N144.csv"
CUBIC_BAND_HIGH = RESULTS / "kerr_scalar_near_extremal_scaling_N176.csv"
PEAK_LOW = RESULTS / "kerr_scalar_power_peakdense_N288.csv"
PEAK_HIGH = RESULTS / "kerr_scalar_power_peakdense_N320.csv"

BAND_OUT = RESULTS / "kerr_scalar_power_bandwidth_summary.csv"
FIT_OUT = RESULTS / "kerr_scalar_power_bandwidth_fits.csv"
PEAK_OUT = RESULTS / "kerr_scalar_power_peak_migration_summary.csv"
FIGURE_OUT = FIGURES / "kerr_scalar_power_bandwidth_hierarchy.png"

RESPONSE_GATE = 5.0e-4
LINEAR_GATE = 2.0e-8
WRONSKIAN_GATE = 1.0e-12
NONLINEAR_ABSOLUTE_GATE = 1.0e-8
NONLINEAR_RELATIVE_GATE = 2.0e-8


@dataclass(frozen=True)
class Pair:
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


def row_key(
    row: dict[str, str], default_n: int | None = None
) -> tuple[int, float, int, int, float]:
    order = row.get("nonlinearity_order")
    if order is None:
        if default_n is None:
            raise KeyError("nonlinearity_order")
        order = str(default_n)
    return (
        int(order),
        round(float(row["a"]), 12),
        int(row["l"]),
        int(row["m"]),
        round(float(row["detuning_over_kappa"]), 12),
    )


def pair_rows(
    low_path: Path, high_path: Path, default_n: int | None = None
) -> list[Pair]:
    low = {row_key(row, default_n): row for row in read_csv(low_path)}
    high = {row_key(row, default_n): row for row in read_csv(high_path)}
    if low.keys() != high.keys():
        missing_low = sorted(high.keys() - low.keys())
        missing_high = sorted(low.keys() - high.keys())
        raise RuntimeError(
            f"Resolution grids differ: missing_low={missing_low}, "
            f"missing_high={missing_high}"
        )

    output = []
    for key in sorted(high):
        low_row = low[key]
        high_row = high[key]
        response_low = float(low_row["horizon_response"])
        response = float(high_row["horizon_response"])
        response_change = abs(response_low - response) / max(abs(response), 1.0e-300)
        linear_balance = max(
            abs(float(low_row["linear_balance"])),
            abs(float(high_row["linear_balance"])),
        )
        nonlinear_balance = max(
            abs(float(low_row["nonlinear_balance"])),
            abs(float(high_row["nonlinear_balance"])),
        )
        nonlinear_relative_balance = max(
            abs(float(row["nonlinear_balance"]))
            / max(abs(float(row["T1"])), abs(float(row["R1"])), 1.0e-300)
            for row in (low_row, high_row)
        )
        wronskian_error = max(
            float(low_row["wronskian_relative_error"]),
            float(high_row["wronskian_relative_error"]),
        )
        accepted = (
            response > 0.0
            and response_change <= RESPONSE_GATE
            and linear_balance <= LINEAR_GATE
            and (
                nonlinear_balance <= NONLINEAR_ABSOLUTE_GATE
                or nonlinear_relative_balance <= NONLINEAR_RELATIVE_GATE
            )
            and wronskian_error <= WRONSKIAN_GATE
        )
        output.append(
            Pair(
                n=key[0],
                a=key[1],
                l=key[2],
                m=key[3],
                kappa=float(high_row["surface_gravity"]),
                y=key[4],
                response=response,
                response_low=response_low,
                resolution_change=response_change,
                linear_balance=linear_balance,
                nonlinear_balance=nonlinear_balance,
                nonlinear_relative_balance=nonlinear_relative_balance,
                wronskian_error=wronskian_error,
                accepted=accepted,
            )
        )
    return output


def band_summaries(pairs: list[Pair]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = []
    groups: dict[tuple[int, float, int, int], list[Pair]] = {}
    for pair in pairs:
        groups.setdefault((pair.n, pair.a, pair.l, pair.m), []).append(pair)

    for (n, a, l, m), group in sorted(groups.items()):
        group = sorted(group, key=lambda item: item.y)
        if not all(item.accepted for item in group):
            rejected = [item.y for item in group if not item.accepted]
            raise RuntimeError(f"Rejected band rows for n={n}, a={a}, mode={(l, m)}: {rejected}")
        y = np.array([item.y for item in group])
        response = np.array([item.response for item in group])
        response_low = np.array([item.response_low for item in group])
        kappa = group[0].kappa
        spectral_weight = float(kappa * np.trapezoid(response, y))
        spectral_weight_low = float(kappa * np.trapezoid(response_low, y))
        rescaled_weight = float(kappa ** (n - 1) * spectral_weight)
        rescaled_weight_low = float(kappa ** (n - 1) * spectral_weight_low)
        profile = kappa**n * response
        peak_index = int(np.argmax(profile))
        rows.append(
            {
                "nonlinearity_order": n,
                "a": f"{a:.16e}",
                "l": l,
                "m": m,
                "surface_gravity": f"{kappa:.16e}",
                "y_min": f"{y[0]:.16e}",
                "y_max": f"{y[-1]:.16e}",
                "node_count": len(y),
                "windowed_spectral_weight": f"{spectral_weight:.16e}",
                "windowed_spectral_weight_low": f"{spectral_weight_low:.16e}",
                "rescaled_windowed_weight": f"{rescaled_weight:.16e}",
                "rescaled_windowed_weight_low": f"{rescaled_weight_low:.16e}",
                "integral_resolution_relative_change": f"{abs(rescaled_weight - rescaled_weight_low) / abs(rescaled_weight):.16e}",
                "max_point_resolution_relative_change": f"{max(item.resolution_change for item in group):.16e}",
                "max_linear_balance": f"{max(item.linear_balance for item in group):.16e}",
                "max_nonlinear_balance": f"{max(item.nonlinear_balance for item in group):.16e}",
                "max_nonlinear_relative_balance": f"{max(item.nonlinear_relative_balance for item in group):.16e}",
                "max_wronskian_relative_error": f"{max(item.wronskian_error for item in group):.16e}",
                "sampled_peak_y": f"{y[peak_index]:.16e}",
                "sampled_peak_rescaled_response": f"{profile[peak_index]:.16e}",
                "accepted": "true",
            }
        )

    fits = []
    for n, l, m in sorted({(int(row["nonlinearity_order"]), int(row["l"]), int(row["m"])) for row in rows}):
        subset = [
            row for row in rows
            if int(row["nonlinearity_order"]) == n
            and int(row["l"]) == l
            and int(row["m"]) == m
        ]
        subset.sort(key=lambda row: float(row["surface_gravity"]), reverse=True)
        x = np.log([float(row["surface_gravity"]) for row in subset])
        z = np.log([float(row["windowed_spectral_weight"]) for row in subset])
        slope, intercept = np.polyfit(x, z, 1)
        predicted = intercept + slope * x
        total = np.sum((z - np.mean(z)) ** 2)
        rescaled = np.array([float(row["rescaled_windowed_weight"]) for row in subset])
        inner = subset[-2:]
        inner_alpha = -(
            np.log(float(inner[-1]["windowed_spectral_weight"]))
            - np.log(float(inner[-2]["windowed_spectral_weight"]))
        ) / (
            np.log(float(inner[-1]["surface_gravity"]))
            - np.log(float(inner[-2]["surface_gravity"]))
        )
        fits.append(
            {
                "nonlinearity_order": n,
                "l": l,
                "m": m,
                "spin_count": len(subset),
                "spin_min": f"{min(float(row['a']) for row in subset):.16e}",
                "spin_max": f"{max(float(row['a']) for row in subset):.16e}",
                "spectral_weight_alpha": f"{-slope:.16e}",
                "predicted_alpha": f"{float(n - 1):.16e}",
                "alpha_minus_prediction": f"{-slope - (n - 1):.16e}",
                "innermost_pair_alpha": f"{inner_alpha:.16e}",
                "r_squared": f"{1.0 - np.sum((z - predicted) ** 2) / total:.16e}",
                "rescaled_weight_mean": f"{np.mean(rescaled):.16e}",
                "rescaled_weight_relative_std": f"{np.std(rescaled) / np.mean(rescaled):.16e}",
                "rescaled_weight_relative_range": f"{np.ptp(rescaled) / np.mean(rescaled):.16e}",
                "max_integral_resolution_relative_change": f"{max(float(row['integral_resolution_relative_change']) for row in subset):.16e}",
                "max_point_resolution_relative_change": f"{max(float(row['max_point_resolution_relative_change']) for row in subset):.16e}",
                "max_nonlinear_relative_balance": f"{max(float(row['max_nonlinear_relative_balance']) for row in subset):.16e}",
            }
        )
    return rows, fits


def peak_summaries(pairs: list[Pair]) -> list[dict[str, object]]:
    rows = []
    groups: dict[tuple[int, int, int], list[Pair]] = {}
    for pair in pairs:
        groups.setdefault((pair.n, pair.l, pair.m), []).append(pair)
    for (n, l, m), group in sorted(groups.items()):
        group = sorted(group, key=lambda item: item.y)
        if not all(item.accepted for item in group):
            rejected = [item.y for item in group if not item.accepted]
            raise RuntimeError(f"Rejected peak rows for n={n}, mode={(l, m)}: {rejected}")
        y = np.array([item.y for item in group])
        response = np.array([item.response for item in group])
        kappa = group[0].kappa
        profile = kappa**n * response
        sampled_peak = int(np.argmax(profile))
        start = max(0, sampled_peak - 2)
        stop = min(len(y), sampled_peak + 3)
        if stop - start < 5:
            raise RuntimeError(f"Peak fit touches scan boundary for n={n}, mode={(l, m)}")
        quadratic, linear, constant = np.polyfit(y[start:stop], np.log(profile[start:stop]), 2)
        if quadratic >= 0.0:
            raise RuntimeError(f"Peak curvature is nonnegative for n={n}, mode={(l, m)}")
        peak_y = -linear / (2.0 * quadratic)
        peak_value = np.exp(constant + linear * peak_y + quadratic * peak_y**2)
        local_sigma = np.sqrt(-1.0 / (2.0 * quadratic))
        rows.append(
            {
                "nonlinearity_order": n,
                "a": f"{group[0].a:.16e}",
                "l": l,
                "m": m,
                "surface_gravity": f"{kappa:.16e}",
                "scan_y_min": f"{y[0]:.16e}",
                "scan_y_max": f"{y[-1]:.16e}",
                "scan_spacing": f"{float(np.min(np.diff(y))):.16e}",
                "sampled_peak_y": f"{y[sampled_peak]:.16e}",
                "log_quadratic_peak_y": f"{peak_y:.16e}",
                "log_quadratic_peak_response": f"{peak_value:.16e}",
                "local_log_gaussian_sigma": f"{local_sigma:.16e}",
                "fit_point_count": stop - start,
                "max_point_resolution_relative_change": f"{max(item.resolution_change for item in group):.16e}",
                "max_linear_balance": f"{max(item.linear_balance for item in group):.16e}",
                "max_nonlinear_balance": f"{max(item.nonlinear_balance for item in group):.16e}",
                "max_nonlinear_relative_balance": f"{max(item.nonlinear_relative_balance for item in group):.16e}",
                "max_wronskian_relative_error": f"{max(item.wronskian_error for item in group):.16e}",
                "accepted": "true",
            }
        )
    return rows


def plot(band_pairs: list[Pair], band_rows: list[dict[str, object]], peak_pairs: list[Pair], peak_rows: list[dict[str, object]]) -> None:
    colors = {1: "#0072B2", 2: "#D55E00", 3: "#009E73"}
    markers = {(2, 2): "o", (3, 3): "s"}
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.25))

    for mode, ax in [((2, 2), axes[0, 0]), ((3, 3), axes[0, 1])]:
        for n in (1, 2, 3):
            group = sorted(
                [pair for pair in peak_pairs if pair.n == n and (pair.l, pair.m) == mode],
                key=lambda item: item.y,
            )
            y = np.array([item.y for item in group])
            profile = np.array([item.kappa**n * item.response for item in group])
            ax.plot(y, profile / np.max(profile), color=colors[n], marker="o", markersize=2.6, linewidth=0.9, label=rf"$n={n}$")
        ax.set_title(rf"Principal mode $({mode[0]},{mode[1]})$")
        ax.set_xlabel(r"$y=p/\kappa$")
        ax.set_ylabel("peak-normalized response")
        ax.grid(True, alpha=0.18)
        ax.legend(frameon=False, fontsize=7)

    for n in (1, 2, 3):
        for mode in ((2, 2), (3, 3)):
            subset = [
                row for row in band_rows
                if int(row["nonlinearity_order"]) == n
                and (int(row["l"]), int(row["m"])) == mode
            ]
            subset.sort(key=lambda row: float(row["surface_gravity"]), reverse=True)
            rescaled_weight = np.array(
                [float(row["rescaled_windowed_weight"]) for row in subset]
            )
            axes[1, 0].plot(
                [float(row["surface_gravity"]) for row in subset],
                rescaled_weight / rescaled_weight[-1],
                color=colors[n], marker=markers[mode], markersize=3.5, linewidth=0.9,
                label=rf"$n={n},\ ({mode[0]},{mode[1]})$",
            )
    axes[1, 0].set_xscale("log")
    axes[1, 0].invert_xaxis()
    axes[1, 0].set_xlabel(r"$M\kappa$")
    axes[1, 0].set_ylabel("rescaled weight / innermost value")
    axes[1, 0].set_title("Windowed spectral-weight collapse")
    axes[1, 0].grid(True, which="both", alpha=0.18)
    axes[1, 0].legend(frameon=False, fontsize=6.4, ncol=2)

    for mode in ((2, 2), (3, 3)):
        subset = [row for row in peak_rows if (int(row["l"]), int(row["m"])) == mode]
        subset.sort(key=lambda row: int(row["nonlinearity_order"]))
        axes[1, 1].plot(
            [int(row["nonlinearity_order"]) for row in subset],
            [float(row["log_quadratic_peak_y"]) for row in subset],
            color="#7A3E00" if mode == (2, 2) else "#6A3D9A",
            marker=markers[mode], markersize=4, linewidth=0.9,
            label=rf"$y_{{\rm pk}},\ ({mode[0]},{mode[1]})$",
        )
        axes[1, 1].plot(
            [int(row["nonlinearity_order"]) for row in subset],
            [float(row["local_log_gaussian_sigma"]) for row in subset],
            color="#7A3E00" if mode == (2, 2) else "#6A3D9A",
            marker=markers[mode], markersize=4, linewidth=0.9, linestyle="--",
            label=rf"$\sigma_y,\ ({mode[0]},{mode[1]})$",
        )
    axes[1, 1].set_xlabel(r"nonlinearity order $n$")
    axes[1, 1].set_ylabel(r"local peak parameter")
    axes[1, 1].set_xticks([1, 2, 3])
    axes[1, 1].set_title("Peak migration and narrowing")
    axes[1, 1].grid(True, alpha=0.18)
    axes[1, 1].legend(frameon=False, fontsize=6.2, ncol=2)

    fig.tight_layout()
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    cubic_band_pairs = pair_rows(CUBIC_BAND_LOW, CUBIC_BAND_HIGH, default_n=1)
    higher_band_pairs = pair_rows(BAND_LOW, BAND_HIGH)
    band_pairs = cubic_band_pairs + higher_band_pairs
    peak_pairs = pair_rows(PEAK_LOW, PEAK_HIGH)
    band_rows, fit_rows = band_summaries(band_pairs)
    peak_rows = peak_summaries(peak_pairs)
    write_csv(BAND_OUT, band_rows)
    write_csv(FIT_OUT, fit_rows)
    write_csv(PEAK_OUT, peak_rows)
    plot(band_pairs, band_rows, peak_pairs, peak_rows)

    print(
        f"accepted band rows = {sum(pair.accepted for pair in band_pairs)}/"
        f"{len(band_pairs)}"
    )
    print(f"accepted peak rows = {sum(pair.accepted for pair in peak_pairs)}/{len(peak_pairs)}")
    for row in fit_rows:
        print(
            f"n={row['nonlinearity_order']} mode=({row['l']},{row['m']}) "
            f"alpha_W={float(row['spectral_weight_alpha']):.6f} "
            f"inner={float(row['innermost_pair_alpha']):.6f} "
            f"predicted={float(row['predicted_alpha']):.0f}"
        )
    for row in peak_rows:
        print(
            f"n={row['nonlinearity_order']} mode=({row['l']},{row['m']}) "
            f"y_peak={float(row['log_quadratic_peak_y']):.5f} "
            f"sigma={float(row['local_log_gaussian_sigma']):.5f}"
        )
    print(f"saved = {FIGURE_OUT}")


if __name__ == "__main__":
    main()
