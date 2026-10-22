"""Validate and plot near-extremal scalar Kerr nonlinear response scaling."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

THRESHOLD_PAIRS = [
    (
        RESULTS / "kerr_scalar_newphysics_threshold_N144.csv",
        RESULTS / "kerr_scalar_newphysics_threshold_N176.csv",
    ),
    (
        RESULTS / "kerr_scalar_newphysics_extreme_threshold_N144.csv",
        RESULTS / "kerr_scalar_newphysics_extreme_threshold_N176.csv",
    ),
    (
        RESULTS / "kerr_scalar_newphysics_highl_threshold_N144.csv",
        RESULTS / "kerr_scalar_newphysics_highl_threshold_N176.csv",
    ),
]
SCALING_PAIR = (
    RESULTS / "kerr_scalar_near_extremal_scaling_N144.csv",
    RESULTS / "kerr_scalar_near_extremal_scaling_N176.csv",
)
SUBDOMINANT_PAIR = (
    RESULTS / "kerr_scalar_newphysics_subdominant_threshold_N144.csv",
    RESULTS / "kerr_scalar_newphysics_subdominant_threshold_N176.csv",
)
PEAK_PAIR = (
    RESULTS / "kerr_scalar_near_extremal_peakdense_N144.csv",
    RESULTS / "kerr_scalar_near_extremal_peakdense_N176.csv",
)

THRESHOLD_OUT = RESULTS / "kerr_scalar_near_extremal_threshold_summary.csv"
SCALING_OUT = RESULTS / "kerr_scalar_near_extremal_scaling_convergence.csv"
COLLAPSE_OUT = RESULTS / "kerr_scalar_near_extremal_collapse_summary.csv"
SUBDOMINANT_OUT = RESULTS / "kerr_scalar_near_extremal_subdominant_summary.csv"
PEAK_OUT = RESULTS / "kerr_scalar_near_extremal_peak_summary.csv"
CROSSING_OUT = RESULTS / "kerr_scalar_near_extremal_mode_crossings.csv"
FIGURE_OUT = FIGURES / "kerr_scalar_near_extremal_scaling.png"

RESPONSE_GATE = 1.0e-5
SCALING_GATE = 5.0e-4


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


def kappa_from_spin(a: float) -> float:
    root = np.sqrt(1.0 - a**2)
    return float(root / (2.0 * (1.0 + root)))


def relative_change(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def threshold_values(rows: list[dict[str, str]]) -> dict[tuple[float, int, int], dict[str, float]]:
    grouped: dict[tuple[float, int, int], dict[float, dict[str, str]]] = {}
    for row in rows:
        key = (round(float(row["a"]), 12), int(row["l"]), int(row["m"]))
        grouped.setdefault(key, {})[round(float(row["omega_fraction"]), 12)] = row

    output = {}
    for key, samples in grouped.items():
        def value(x: float, field: str) -> float:
            return float(samples[round(x, 12)][field])

        small = 0.5 * (
            value(0.999, "horizon_response")
            + value(1.001, "horizon_response")
        )
        large = 0.5 * (
            value(0.99, "horizon_response")
            + value(1.01, "horizon_response")
        )
        response = (100.0 * small - large) / 99.0
        output[key] = {
            "response": response,
            "richardson_relative_correction": relative_change(small, response),
            "max_linear_balance": max(
                abs(float(row["linear_balance"])) for row in samples.values()
            ),
            "max_wronskian_error": max(
                float(row["wronskian_relative_error"]) for row in samples.values()
            ),
            "max_nonlinear_balance": max(
                abs(float(row["nonlinear_balance"])) for row in samples.values()
            ),
        }
    return output


def threshold_summary() -> list[dict[str, object]]:
    output = []
    for low_path, high_path in THRESHOLD_PAIRS:
        low = threshold_values(read_csv(low_path))
        high = threshold_values(read_csv(high_path))
        for key in sorted(low.keys() & high.keys()):
            a, l, m = key
            response = high[key]["response"]
            change = relative_change(low[key]["response"], response)
            output.append({
                "a": f"{a:.16e}",
                "l": l,
                "m": m,
                "surface_gravity": f"{kappa_from_spin(a):.16e}",
                "horizon_response_threshold": f"{response:.16e}",
                "scaled_threshold_response": f"{kappa_from_spin(a) * response:.16e}",
                "horizon_response_N144": f"{low[key]['response']:.16e}",
                "resolution_relative_change": f"{change:.16e}",
                "richardson_relative_correction": (
                    f"{high[key]['richardson_relative_correction']:.16e}"
                ),
                "max_linear_balance": f"{high[key]['max_linear_balance']:.16e}",
                "max_nonlinear_balance": f"{high[key]['max_nonlinear_balance']:.16e}",
                "max_wronskian_relative_error": f"{high[key]['max_wronskian_error']:.16e}",
                "accepted": "true" if change <= RESPONSE_GATE else "false",
                "low_resolution": low_path.name,
                "high_resolution": high_path.name,
            })
    return sorted(output, key=lambda row: (float(row["a"]), int(row["l"])))


def keyed_scaling(rows: list[dict[str, str]]):
    return {
        (
            round(float(row["a"]), 12),
            int(row["l"]),
            int(row["m"]),
            round(float(row["detuning_over_kappa"]), 12),
        ): row
        for row in rows
    }


def scaling_summary(paths=SCALING_PAIR) -> list[dict[str, object]]:
    low = keyed_scaling(read_csv(paths[0]))
    high = keyed_scaling(read_csv(paths[1]))
    output = []
    for key in sorted(low.keys() & high.keys()):
        a, l, m, detuning = key
        response_low = float(low[key]["scaled_horizon_response"])
        response_high = float(high[key]["scaled_horizon_response"])
        change = relative_change(response_low, response_high)
        linear_error = max(
            abs(float(low[key]["linear_balance"])),
            abs(float(high[key]["linear_balance"])),
        )
        wronskian_error = max(
            float(low[key]["wronskian_relative_error"]),
            float(high[key]["wronskian_relative_error"]),
        )
        accepted = (
            change <= SCALING_GATE
            and linear_error <= 2.0e-8
            and wronskian_error <= 1.0e-12
        )
        output.append({
            "a": f"{a:.16e}",
            "l": l,
            "m": m,
            "surface_gravity": high[key]["surface_gravity"],
            "detuning_over_kappa": f"{detuning:.16e}",
            "omega_fraction": high[key]["omega_fraction"],
            "horizon_response": high[key]["horizon_response"],
            "scaled_horizon_response": f"{response_high:.16e}",
            "scaled_horizon_response_N144": f"{response_low:.16e}",
            "resolution_relative_change": f"{change:.16e}",
            "max_linear_balance": f"{linear_error:.16e}",
            "max_nonlinear_balance": (
                f"{max(abs(float(low[key]['nonlinear_balance'])), abs(float(high[key]['nonlinear_balance']))):.16e}"
            ),
            "max_wronskian_relative_error": f"{wronskian_error:.16e}",
            "accepted": "true" if accepted else "false",
        })
    return output


def collapse_summary(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output = []
    for l in (2, 3):
        detunings = sorted({
            float(row["detuning_over_kappa"])
            for row in rows
            if int(row["l"]) == l and row["accepted"] == "true"
        })
        for detuning in detunings:
            subset = [
                float(row["scaled_horizon_response"])
                for row in rows
                if int(row["l"]) == l
                and row["accepted"] == "true"
                and np.isclose(float(row["detuning_over_kappa"]), detuning)
            ]
            mean = float(np.mean(subset))
            output.append({
                "l": l,
                "m": l,
                "detuning_over_kappa": f"{detuning:.16e}",
                "spin_count": len(subset),
                "mean_scaled_horizon_response": f"{mean:.16e}",
                "relative_standard_deviation": (
                    f"{np.std(subset) / max(abs(mean), 1e-300):.16e}"
                ),
                "relative_range": (
                    f"{(max(subset) - min(subset)) / max(abs(mean), 1e-300):.16e}"
                ),
            })
    return output


def threshold_pair_summary(paths) -> list[dict[str, object]]:
    low = threshold_values(read_csv(paths[0]))
    high = threshold_values(read_csv(paths[1]))
    output = []
    for key in sorted(low.keys() & high.keys()):
        a, l, m = key
        response = high[key]["response"]
        output.append({
            "a": f"{a:.16e}",
            "l": l,
            "m": m,
            "surface_gravity": f"{kappa_from_spin(a):.16e}",
            "horizon_response_threshold": f"{response:.16e}",
            "scaled_threshold_response": f"{kappa_from_spin(a) * response:.16e}",
            "resolution_relative_change": (
                f"{relative_change(low[key]['response'], response):.16e}"
            ),
        })
    return output


def peak_summary() -> list[dict[str, object]]:
    rows = scaling_summary(PEAK_PAIR)
    output = []
    for a in sorted({float(row["a"]) for row in rows}):
        for l in (2, 3):
            subset = [
                row for row in rows
                if np.isclose(float(row["a"]), a)
                and int(row["l"]) == l
                and row["accepted"] == "true"
            ]
            peak = max(subset, key=lambda row: float(row["scaled_horizon_response"]))
            output.append({
                "a": peak["a"],
                "l": l,
                "m": l,
                "sampled_peak_detuning_over_kappa": peak["detuning_over_kappa"],
                "sampled_peak_scaled_horizon_response": peak["scaled_horizon_response"],
                "sampled_peak_horizon_response": peak["horizon_response"],
                "resolution_relative_change": peak["resolution_relative_change"],
                "note": "sampled maximum on Delta(p/kappa)=0.05 grid",
            })
    return output


def crossing_rows(thresholds: list[dict[str, object]]) -> list[dict[str, object]]:
    accepted = [row for row in thresholds if row["accepted"] == "true" and int(row["l"]) <= 3]
    spins = sorted({float(row["a"]) for row in accepted})
    values = {
        (float(row["a"]), int(row["l"])): float(row["horizon_response_threshold"])
        for row in accepted
    }
    output = []
    for first, second in ((1, 2), (1, 3), (2, 3)):
        previous = None
        for a in spins:
            if (a, first) not in values or (a, second) not in values:
                continue
            difference = values[(a, second)] - values[(a, first)]
            if previous is not None and previous[1] * difference < 0.0:
                output.append({
                    "first_l": first,
                    "second_l": second,
                    "lower_spin": f"{previous[0]:.16e}",
                    "upper_spin": f"{a:.16e}",
                    "lower_difference": f"{previous[1]:.16e}",
                    "upper_difference": f"{difference:.16e}",
                    "interpretation": "mode-order crossing bracket; no interpolated root claimed",
                })
            previous = (a, difference)
    return output


def plot(thresholds, scaling) -> None:
    accepted_thresholds = [row for row in thresholds if row["accepted"] == "true"]
    accepted_scaling = [
        row for row in scaling
        if row["accepted"] == "true" and float(row["detuning_over_kappa"]) <= 1.0
    ]
    colors = {1: "#2a6fbb", 2: "#d95f02", 3: "#228833", 4: "#9467bd", 5: "#8c564b"}
    spin_colors = {0.98: "#2a6fbb", 0.99: "#d95f02", 0.995: "#228833"}
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.75))

    for l in (1, 2, 3):
        subset = sorted(
            [row for row in accepted_thresholds if int(row["l"]) == l],
            key=lambda row: float(row["surface_gravity"]),
        )
        axes[0].plot(
            [float(row["surface_gravity"]) for row in subset],
            [float(row["horizon_response_threshold"]) for row in subset],
            marker="o", markersize=3.0, linewidth=1.0, color=colors[l],
            label=rf"$\ell=m={l}$",
        )
        axes[1].plot(
            [float(row["surface_gravity"]) for row in subset],
            [float(row["scaled_threshold_response"]) for row in subset],
            marker="o", markersize=3.0, linewidth=1.0, color=colors[l],
            label=rf"$\ell=m={l}$",
        )
    for l in (4, 5):
        subset = [row for row in accepted_thresholds if int(row["l"]) == l]
        axes[0].scatter(
            [float(row["surface_gravity"]) for row in subset],
            [float(row["horizon_response_threshold"]) for row in subset],
            s=16, marker="D", color=colors[l], label=rf"$\ell=m={l}$",
        )
        axes[1].scatter(
            [float(row["surface_gravity"]) for row in subset],
            [float(row["scaled_threshold_response"]) for row in subset],
            s=16, marker="D", color=colors[l], label=rf"$\ell=m={l}$",
        )

    guide_kappa = np.geomspace(0.02, 0.115, 100)
    axes[0].plot(guide_kappa, 0.0291 / guide_kappa, color="0.35", linestyle=":", linewidth=0.9, label=r"$0.0291/(M\kappa)$")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xticks([0.02, 0.05, 0.10])
    axes[0].set_xticklabels(["0.02", "0.05", "0.10"])
    axes[0].xaxis.set_minor_formatter(NullFormatter())
    axes[0].set_xlabel(r"$M\kappa$")
    axes[0].set_ylabel(r"$\chi_H^\star$")
    axes[0].set_title("Threshold enhancement")
    axes[0].legend(frameon=False, fontsize=6.2)

    axes[1].axhline(0.0291, color="0.35", linestyle=":", linewidth=0.9)
    axes[1].set_xscale("log")
    axes[1].set_xticks([0.02, 0.05, 0.10])
    axes[1].set_xticklabels(["0.02", "0.05", "0.10"])
    axes[1].xaxis.set_minor_formatter(NullFormatter())
    axes[1].set_xlabel(r"$M\kappa$")
    axes[1].set_ylabel(r"$M\kappa\,\chi_H^\star$")
    axes[1].set_title("Multipole reordering")

    for a in (0.98, 0.99, 0.995):
        for l, linestyle in ((2, "-"), (3, "--")):
            subset = sorted(
                [
                    row for row in accepted_scaling
                    if np.isclose(float(row["a"]), a) and int(row["l"]) == l
                ],
                key=lambda row: float(row["detuning_over_kappa"]),
            )
            axes[2].plot(
                [float(row["detuning_over_kappa"]) for row in subset],
                [float(row["scaled_horizon_response"]) for row in subset],
                color=spin_colors[a], linestyle=linestyle, marker="o",
                markersize=2.3, linewidth=0.9,
                label=(rf"$a={a:g}$" if l == 2 else None),
            )
    axes[2].set_xlabel(r"$p/\kappa$")
    axes[2].set_ylabel(r"$M\kappa\,\chi_H$")
    axes[2].set_title("Near-horizon collapse")
    axes[2].legend(frameon=False, fontsize=6.5)
    axes[2].text(
        0.97, 0.05,
        r"solid: $\ell=m=2$" "\n" r"dashed: $\ell=m=3$",
        transform=axes[2].transAxes, ha="right", va="bottom", fontsize=6.2,
    )

    for ax in axes:
        ax.grid(True, which="both", alpha=0.18)
    fig.tight_layout()
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_OUT, dpi=280, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    thresholds = threshold_summary()
    scaling = scaling_summary()
    collapse = collapse_summary(scaling)
    subdominant = threshold_pair_summary(SUBDOMINANT_PAIR)
    peaks = peak_summary()
    crossings = crossing_rows(thresholds)
    write_csv(THRESHOLD_OUT, thresholds)
    write_csv(SCALING_OUT, scaling)
    write_csv(COLLAPSE_OUT, collapse)
    write_csv(SUBDOMINANT_OUT, subdominant)
    write_csv(PEAK_OUT, peaks)
    write_csv(CROSSING_OUT, crossings)
    plot(thresholds, scaling)
    print(f"accepted threshold rows = {sum(row['accepted'] == 'true' for row in thresholds)}")
    print(f"accepted scaling rows = {sum(row['accepted'] == 'true' for row in scaling)}")
    print(f"saved = {FIGURE_OUT}")


if __name__ == "__main__":
    main()
