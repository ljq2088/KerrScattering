"""Validate and summarize the nonlinear scalar Kerr superradiant response."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

COARSE_LOW = RESULTS / "kerr_scalar_superradiant_response_N288.csv"
COARSE_HIGH = RESULTS / "kerr_scalar_superradiant_response_N320.csv"
NEAR_LOW = RESULTS / "kerr_scalar_superradiant_near_threshold_N288.csv"
NEAR_HIGH = RESULTS / "kerr_scalar_superradiant_near_threshold_N320.csv"
DENSE_LOW = RESULTS / "kerr_scalar_superradiant_highspin_dense_N288.csv"
DENSE_HIGH = RESULTS / "kerr_scalar_superradiant_highspin_dense_N320.csv"

ACCEPTED_OUT = RESULTS / "kerr_scalar_superradiant_response_accepted.csv"
THRESHOLD_OUT = RESULTS / "kerr_scalar_superradiant_threshold_limits.csv"
PEAK_OUT = RESULTS / "kerr_scalar_superradiant_highspin_peaks.csv"
MATCHING_OUT = RESULTS / "kerr_scalar_superradiant_matching_convergence.csv"
FIGURE_OUT = FIGURES / "kerr_scalar_superradiant_response.png"

CHI_RELATIVE_GATE = 1.0e-5
FLUX_BALANCE_GATE = 1.0e-8


def read_rows(path: Path) -> dict[tuple[float, int, int, float], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {
        (
            round(float(row["a"]), 12),
            int(row["l"]),
            int(row["m"]),
            round(float(row["omega_fraction"]), 12),
        ): row
        for row in rows
    }


def relative_change(first: float, second: float) -> float:
    return abs(first - second) / max(abs(second), 1.0e-300)


def in_display_window(a: float, l: int, x: float) -> bool:
    if a == 0.5:
        return 0.90 <= x <= 1.50
    if a == 0.7:
        return 0.60 <= x <= 1.50
    if a == 0.9 and l == 1:
        return 0.60 <= x <= 1.60
    if a == 0.9 and l == 2:
        return 0.60 <= x <= 1.30
    return False


def validate_pair(
    low: dict[str, str], high: dict[str, str], source: str
) -> dict[str, object] | None:
    chi_low = float(low["horizon_response"])
    chi_high = float(high["horizon_response"])
    chi_change = relative_change(chi_low, chi_high)
    linear_error = max(abs(float(low["linear_balance"])), abs(float(high["linear_balance"])))
    wronskian_error = max(
        float(low["wronskian_relative_error"]),
        float(high["wronskian_relative_error"]),
    )
    if (
        chi_change > CHI_RELATIVE_GATE
        or linear_error > 1.0e-8
        or wronskian_error > 1.0e-10
        or low["status"] != "ok"
        or high["status"] != "ok"
    ):
        return None

    balance_low = abs(float(low["nonlinear_balance"]))
    balance_high = abs(float(high["nonlinear_balance"]))
    return {
        "a": f"{float(high['a']):.16e}",
        "l": int(high["l"]),
        "m": int(high["m"]),
        "omega_fraction": f"{float(high['omega_fraction']):.16e}",
        "omega": f"{float(high['omega']):.16e}",
        "m_omega_h": f"{float(high['m_omega_h']):.16e}",
        "p_horizon": f"{float(high['p_horizon']):.16e}",
        "T0": f"{float(high['T0']):.16e}",
        "T1": f"{float(high['T1']):.16e}",
        "horizon_response": f"{chi_high:.16e}",
        "horizon_response_N288": f"{chi_low:.16e}",
        "horizon_response_relative_change": f"{chi_change:.16e}",
        "max_linear_balance_error": f"{linear_error:.16e}",
        "max_wronskian_relative_error": f"{wronskian_error:.16e}",
        "nonlinear_balance_abs_N288": f"{balance_low:.16e}",
        "nonlinear_balance_abs_N320": f"{balance_high:.16e}",
        "direct_flux_accepted": (
            "true"
            if max(balance_low, balance_high) <= FLUX_BALANCE_GATE
            else "false"
        ),
        "source_grid": source,
    }


def accepted_rows() -> list[dict[str, object]]:
    pairs = [
        ("coarse", read_rows(COARSE_LOW), read_rows(COARSE_HIGH)),
        ("near-threshold", read_rows(NEAR_LOW), read_rows(NEAR_HIGH)),
        ("high-spin-dense", read_rows(DENSE_LOW), read_rows(DENSE_HIGH)),
    ]
    priority = {"coarse": 0, "near-threshold": 1, "high-spin-dense": 2}
    selected: dict[tuple[float, int, int, float], dict[str, object]] = {}
    for source, low_rows, high_rows in pairs:
        for key in sorted(low_rows.keys() & high_rows.keys()):
            a, l, _, x = key
            if not in_display_window(a, l, x):
                continue
            validated = validate_pair(low_rows[key], high_rows[key], source)
            if validated is None:
                continue
            previous = selected.get(key)
            if previous is None or priority[source] > priority[str(previous["source_grid"])]:
                selected[key] = validated
    return [selected[key] for key in sorted(selected)]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows to write to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def threshold_limit(rows: dict[tuple[float, int, int, float], dict[str, str]], key3):
    def value(x: float, field: str) -> float:
        return float(rows[(*key3, round(x, 12))][field])

    symmetric_small = 0.5 * (
        value(0.999, "horizon_response") + value(1.001, "horizon_response")
    )
    symmetric_large = 0.5 * (
        value(0.99, "horizon_response") + value(1.01, "horizon_response")
    )
    response = (100.0 * symmetric_small - symmetric_large) / 99.0
    slope_small = 0.5 * (
        value(0.999, "T1") / value(0.999, "p_horizon")
        + value(1.001, "T1") / value(1.001, "p_horizon")
    )
    slope_large = 0.5 * (
        value(0.99, "T1") / value(0.99, "p_horizon")
        + value(1.01, "T1") / value(1.01, "p_horizon")
    )
    t1_slope = (100.0 * slope_small - slope_large) / 99.0
    sign_change = value(0.999, "T1") < 0.0 < value(1.001, "T1")
    return response, t1_slope, sign_change


def threshold_rows() -> list[dict[str, object]]:
    low = read_rows(NEAR_LOW)
    high = read_rows(NEAR_HIGH)
    output = []
    for key3 in sorted({key[:3] for key in low} & {key[:3] for key in high}):
        response_low, slope_low, sign_low = threshold_limit(low, key3)
        response_high, slope_high, sign_high = threshold_limit(high, key3)
        a, l, m = key3
        output.append({
            "a": f"{a:.16e}",
            "l": l,
            "m": m,
            "horizon_response_threshold": f"{response_high:.16e}",
            "horizon_response_threshold_N288": f"{response_low:.16e}",
            "horizon_response_relative_change": (
                f"{relative_change(response_low, response_high):.16e}"
            ),
            "T1_over_p_threshold": f"{slope_high:.16e}",
            "T1_over_p_threshold_N288": f"{slope_low:.16e}",
            "T1_sign_change_verified": "true" if sign_low and sign_high else "false",
            "extrapolation": "Richardson symmetric x=1+-0.001,0.01",
        })
    return output


def peak_rows(accepted: list[dict[str, object]]) -> list[dict[str, object]]:
    dense = [
        row for row in accepted
        if row["source_grid"] == "high-spin-dense" and float(row["a"]) == 0.9
    ]
    output = []
    for l in (1, 2):
        mode_rows = [row for row in dense if int(row["l"]) == l]
        peak = max(mode_rows, key=lambda row: float(row["horizon_response"]))
        output.append({
            "a": peak["a"],
            "l": l,
            "m": l,
            "sampled_peak_omega_fraction": peak["omega_fraction"],
            "sampled_peak_omega": peak["omega"],
            "sampled_peak_horizon_response": peak["horizon_response"],
            "horizon_response_relative_change": (
                peak["horizon_response_relative_change"]
            ),
            "T1_at_sampled_peak": peak["T1"],
            "largest_valid_omega_fraction": f"{max(float(row['omega_fraction']) for row in mode_rows):.16e}",
            "note": "sampled maximum; no interpolated peak fit",
        })
    return output


def single_row(path: Path) -> dict[str, str]:
    rows = read_rows(path)
    if len(rows) != 1:
        raise RuntimeError(f"Expected one row in {path}, found {len(rows)}")
    return next(iter(rows.values()))


def matching_rows() -> list[dict[str, object]]:
    near_high = read_rows(NEAR_HIGH)
    dense_high = read_rows(DENSE_HIGH)
    cases = [
        (
            (0.5, 2, 2, 0.999),
            near_high,
            [
                RESULTS / "kerr_scalar_superradiant_match_a05_l2_r24.csv",
                RESULTS / "kerr_scalar_superradiant_match_a05_l2_r36.csv",
            ],
        ),
        (
            (0.7, 1, 1, 0.999),
            near_high,
            [
                RESULTS / "kerr_scalar_superradiant_match_a07_l1_r24.csv",
                RESULTS / "kerr_scalar_superradiant_match_a07_l1_r36.csv",
            ],
        ),
        (
            (0.9, 1, 1, 1.30),
            dense_high,
            [
                RESULTS / "kerr_scalar_superradiant_match_a09_l1_r10.csv",
                RESULTS / "kerr_scalar_superradiant_match_a09_l1_r16.csv",
            ],
        ),
        (
            (0.9, 2, 2, 1.20),
            dense_high,
            [
                RESULTS / "kerr_scalar_superradiant_match_a09_l2_r10.csv",
                RESULTS / "kerr_scalar_superradiant_match_a09_l2_r16.csv",
            ],
        ),
    ]
    output = []
    for key, baseline_rows, alternate_paths in cases:
        normalized_key = (key[0], key[1], key[2], round(key[3], 12))
        baseline = baseline_rows[normalized_key]
        all_rows = [baseline, *(single_row(path) for path in alternate_paths)]
        responses = [float(row["horizon_response"]) for row in all_rows]
        reference = float(baseline["horizon_response"])
        output.append({
            "a": f"{key[0]:.16e}",
            "l": key[1],
            "m": key[2],
            "omega_fraction": f"{key[3]:.16e}",
            "matching_radii": ",".join(f"{float(row['r_match']):g}" for row in all_rows),
            "horizon_response_reference": f"{reference:.16e}",
            "horizon_response_relative_spread": (
                f"{(max(responses) - min(responses)) / max(abs(reference), 1e-300):.16e}"
            ),
            "max_wronskian_relative_error": (
                f"{max(float(row['wronskian_relative_error']) for row in all_rows):.16e}"
            ),
        })
    return output


def plot_rows(rows: list[dict[str, object]]) -> None:
    colors = {0.5: "#1f77b4", 0.7: "#d95f02", 0.9: "#228833"}
    markers = {1: "o", 2: "s"}
    linestyles = {1: "-", 2: "--"}
    plt.rcParams.update({"font.size": 8.5, "axes.labelsize": 9.5})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.15), sharex=True)

    for a in (0.5, 0.7, 0.9):
        for l in (1, 2):
            subset = sorted(
                [row for row in rows if float(row["a"]) == a and int(row["l"]) == l],
                key=lambda row: float(row["omega_fraction"]),
            )
            if not subset:
                continue
            x = [float(row["omega_fraction"]) for row in subset]
            label = rf"$a={a:.1f},\ \ell=m={l}$"
            style = {
                "color": colors[a],
                "linestyle": linestyles[l],
                "marker": markers[l],
                "markersize": 2.8,
                "linewidth": 1.0,
            }
            axes[0].plot(x, [float(row["T1"]) for row in subset], label=label, **style)
            axes[1].plot(
                x,
                [float(row["horizon_response"]) for row in subset],
                label=label,
                **style,
            )

    for ax in axes:
        ax.axvline(1.0, color="0.35", linestyle=":", linewidth=0.9)
        ax.grid(True, which="both", alpha=0.18)
        ax.set_xlabel(r"$x=\omega/(m\Omega_H)$")
        ax.set_xlim(0.56, 1.64)
    axes[0].axhline(0.0, color="0.5", linewidth=0.7)
    axes[0].set_yscale("symlog", linthresh=1.0e-7)
    axes[0].set_ylabel(r"$T^{(1)}$")
    axes[0].set_title("Signed first-order horizon flux")
    axes[1].set_ylabel(r"$\chi_H=T^{(1)}/T^{(0)}$")
    axes[1].set_ylim(0.0, 0.41)
    axes[1].set_title("Threshold-regular relative response")
    axes[1].legend(frameon=False, fontsize=7.1, ncol=2, loc="upper left")
    fig.tight_layout()
    FIGURE_OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_OUT, dpi=260, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    accepted = accepted_rows()
    thresholds = threshold_rows()
    peaks = peak_rows(accepted)
    matching = matching_rows()
    write_csv(ACCEPTED_OUT, accepted)
    write_csv(THRESHOLD_OUT, thresholds)
    write_csv(PEAK_OUT, peaks)
    write_csv(MATCHING_OUT, matching)
    plot_rows(accepted)
    direct_count = sum(row["direct_flux_accepted"] == "true" for row in accepted)
    print(f"accepted response rows = {len(accepted)}")
    print(f"direct-flux-accepted rows = {direct_count}")
    print(f"saved = {ACCEPTED_OUT}")
    print(f"saved = {THRESHOLD_OUT}")
    print(f"saved = {PEAK_OUT}")
    print(f"saved = {MATCHING_OUT}")
    print(f"saved = {FIGURE_OUT}")


if __name__ == "__main__":
    main()
