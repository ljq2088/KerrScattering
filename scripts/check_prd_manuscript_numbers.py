"""Check PRD manuscript display numbers against tracked Kerr scalar CSV data.

This is a lightweight submission-prep guard: it verifies that the rounded
numbers printed in the active REVTeX draft still agree with the numerical data
files used to generate the figures and tables.
"""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.tex"
FIT_CSV = ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_fit_table.csv"
TAIL_WINDOW_CSV = ROOT / "results" / "kerr_scalar_nonlinear_tail_window_sensitivity.csv"
TAIL_MODEL_CSV = ROOT / "results" / "kerr_scalar_nonlinear_tail_model_comparison.csv"
PEAK_WINDOW_CSV = ROOT / "results" / "kerr_scalar_nonlinear_peak_window_sensitivity.csv"
LOW_ACCEPTANCE_CSV = ROOT / "results" / "kerr_scalar_low_frequency_axisymmetric_acceptance.csv"
LOW_CONVERGENCE_CSV = ROOT / "results" / "kerr_scalar_axisymmetric_low_frequency_convergence.csv"
PRODUCTION_CSV = ROOT / "results" / "kerr_scalar_axisymmetric_production_convergence.csv"
TAIL_CONVERGENCE_CSV = ROOT / "results" / "kerr_scalar_axisymmetric_tail_convergence.csv"
CHANNEL_CSV = ROOT / "results" / "kerr_scalar_nonlinear_channels.csv"
SUPERRADIANT_CSV = ROOT / "results" / "kerr_scalar_superradiant_threshold_limits.csv"
NEAR_EXTREMAL_CSV = ROOT / "results" / "kerr_scalar_near_extremal_threshold_summary.csv"
MODAL_POWER_FITS_CSV = ROOT / "results" / "kerr_scalar_modal_powerlaw_fits.csv"
POWER_MODAL_FITS_CSV = ROOT / "results" / "kerr_scalar_power_near_extremal_fits.csv"
CFT_FACTORIZATION_FITS_CSV = ROOT / "results" / "kerr_scalar_cft_factorization_fits.csv"
POWER_BANDWIDTH_CSV = ROOT / "results" / "kerr_scalar_power_bandwidth_summary.csv"
POWER_BANDWIDTH_FITS_CSV = ROOT / "results" / "kerr_scalar_power_bandwidth_fits.csv"
POWER_PEAK_MIGRATION_CSV = ROOT / "results" / "kerr_scalar_power_peak_migration_summary.csv"
L0_ZERO_CSV = ROOT / "results" / "kerr_scalar_l0_zero_frequency_summary.csv"
AXISYMMETRIC_IR_LOW_CSV = (
    ROOT / "results" / "kerr_scalar_axisymmetric_infrared_N144.csv"
)
AXISYMMETRIC_IR_HIGH_CSV = (
    ROOT / "results" / "kerr_scalar_axisymmetric_infrared_N176.csv"
)
AXISYMMETRIC_IR_FITS_CSV = (
    ROOT / "results" / "kerr_scalar_axisymmetric_infrared_fits.csv"
)
POWER_FIXED_CSV = ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_fixed_summary.csv"
POWER_KAPPA_CSV = ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_kappa_summary.csv"
POWER_SPECTRAL_COEFF_CSV = ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_spectral_coefficients.csv"
POWER_SPECTRAL_RESIDUAL_CSV = ROOT / "results" / "kerr_scalar_power_nonlinearity_l0_spectral_residuals.csv"
SPIN_LIMIT_CSV = ROOT / "results" / "kerr_scalar_spin_limit.csv"
SPECTRAL_RESIDUAL_CSV = ROOT / "results" / "kerr_scalar_axisymmetric_spectral_residuals.csv"
ANGULAR_CSV = ROOT / "results" / "kerr_scalar_angular_convergence.csv"
SWEEP_CSVS = {
    0: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l0.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l0.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_dense_l0.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_tail_q2048_l0.csv",
    ],
    1: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l1.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l1.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_dense_l1.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_tail_q2048_l1.csv",
    ],
    2: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l2.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l2.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_dense_l2.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_tail_q2048_l2.csv",
    ],
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def decimal_tolerance(display: str, *, multiplier: float = 0.75) -> float:
    if "." not in display:
        return multiplier
    decimals = len(display.split(".", 1)[1])
    return multiplier * 10.0 ** (-decimals)


def assert_close(label: str, shown: float, actual: float, tol: float) -> None:
    if not math.isfinite(actual):
        raise AssertionError(f"{label}: non-finite actual value {actual!r}")
    if abs(shown - actual) > tol:
        raise AssertionError(
            f"{label}: manuscript has {shown}, data give {actual} "
            f"(tolerance {tol})"
        )


def assert_decimal(label: str, shown_text: str, actual: float) -> None:
    assert_close(label, float(shown_text), actual, decimal_tolerance(shown_text))


def parse_tex_scientific(mantissa: str, exponent: str) -> float:
    return float(mantissa) * 10.0 ** int(exponent)


def check_table_i(tex: str) -> None:
    rows = {
        int(row["l"]): row for row in read_csv_rows(FIT_CSV)
    }
    pattern = re.compile(
        r"^(?P<l>[012])\s*&\s*"
        r"(?P<omega>[0-9.]+)\s*&\s*"
        r"(?P<gamma>[0-9.]+)\s*&\s*"
        r"(?P<qnm_r>[0-9.]+)\s*&\s*"
        r"(?P<qnm_i>[0-9.]+)\s*&\s*"
        r"(?P<pi_t>[0-9.]+)\s*&\s*"
        r"(?P<dt>[0-9.]+)\\%\\\\",
        re.MULTILINE,
    )
    found = {}
    for match in pattern.finditer(tex):
        ell = int(match.group("l"))
        if ell not in rows:
            continue
        found[ell] = match.groupdict()

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all Table I rows in manuscript")

    for ell, groups in found.items():
        row = rows[ell]
        assert_decimal(f"Table I l={ell} omega_peak", groups["omega"], float(row["omega_peak"]))
        assert_decimal(f"Table I l={ell} gamma", groups["gamma"], float(row["gamma"]))
        assert_decimal(f"Table I l={ell} qnm_real", groups["qnm_r"], float(row["qnm_real"]))
        assert_decimal(f"Table I l={ell} qnm_imag_abs", groups["qnm_i"], float(row["qnm_imag_abs"]))
        assert_decimal(f"Table I l={ell} pi_Tfit", groups["pi_t"], float(row["pi_Tfit"]))
        assert_decimal(
            f"Table I l={ell} Delta T percent",
            groups["dt"],
            100.0 * float(row["Tfit_over_TH_minus_1_abs"]),
        )


def best_sweep_rows(ell: int) -> list[dict[str, str]]:
    best: dict[float, dict[str, str]] = {}
    for path in SWEEP_CSVS[ell]:
        for row in read_csv_rows(path):
            omega = float(row["omega"])
            rank = (
                int(float(row.get("N", 0))),
                int(float(row.get("quad_order", 0))),
                -abs(float(row["nonlinear_balance"])),
            )
            old = best.get(omega)
            old_rank = None if old is None else (
                int(float(old.get("N", 0))),
                int(float(old.get("quad_order", 0))),
                -abs(float(old["nonlinear_balance"])),
            )
            if old is None or rank > old_rank:
                best[omega] = row
    return [best[omega] for omega in sorted(best)]


def check_table_ii(tex: str) -> None:
    tail_rows = {int(row["l"]): row for row in read_csv_rows(FIT_CSV)}
    pattern = re.compile(
        r"^(?P<l>[012])\s*&\s*"
        r"(?P<points>\d+)\s*&\s*"
        r"(?P<omega_min>[0-9.]+)\s*&\s*"
        r"\$(?P<d0_m>[0-9.]+)\\times10\^\{(?P<d0_e>-?\d+)\}\$\s*&\s*"
        r"\$(?P<d1_m>[0-9.]+)\\times10\^\{(?P<d1_e>-?\d+)\}\$\s*&\s*"
        r"\$(?P<tail_m>[0-9.]+)\\times10\^\{(?P<tail_e>-?\d+)\}\$\\\\",
        re.MULTILINE,
    )
    found = {}
    for match in pattern.finditer(tex):
        ell = int(match.group("l"))
        found[ell] = match.groupdict()

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all Table II rows in manuscript")

    for ell, groups in found.items():
        rows = best_sweep_rows(ell)
        accepted = [
            row for row in rows
            if abs(float(row["nonlinear_balance"])) <= 1.0e-8
        ]
        max_delta0 = max(abs(float(row["linear_balance"]) - 1.0) for row in accepted)
        max_delta1_acc = max(abs(float(row["nonlinear_balance"])) for row in accepted)
        tail_rms = float(tail_rows[ell]["tail_rms_log"])

        if int(groups["points"]) != len(accepted):
            raise AssertionError(f"Table II l={ell}: retained point count mismatch")
        assert_decimal(
            f"Table II l={ell} minimum omega",
            groups["omega_min"],
            min(float(row["omega"]) for row in accepted),
        )

        shown_d0 = parse_tex_scientific(groups["d0_m"], groups["d0_e"])
        shown_d1 = parse_tex_scientific(groups["d1_m"], groups["d1_e"])
        shown_tail = parse_tex_scientific(groups["tail_m"], groups["tail_e"])

        assert_close(
            f"Table II l={ell} max delta0",
            shown_d0,
            max_delta0,
            1.0e-1 * 10.0 ** int(groups["d0_e"]),
        )
        assert_close(
            f"Table II l={ell} max accepted delta1",
            shown_d1,
            max_delta1_acc,
            1.0e-1 * 10.0 ** int(groups["d1_e"]),
        )
        assert_close(
            f"Table II l={ell} tail RMS",
            shown_tail,
            tail_rms,
            1.0e-1 * 10.0 ** int(groups["tail_e"]),
        )


def check_low_frequency_acceptance(tex: str) -> None:
    rows = {int(row["l"]): row for row in read_csv_rows(LOW_ACCEPTANCE_CSV)}
    table_match = re.search(
        r"\\label\{tab:low-acceptance\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find the low-frequency acceptance table")

    found: dict[int, list[object]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[012]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 6:
            raise AssertionError(f"Malformed low-frequency acceptance row: {line}")
        window = re.fullmatch(r"\$\[([0-9.]+),([0-9.]+)\]\$", parts[1])
        if window is None:
            raise AssertionError(f"Malformed low-frequency window: {line}")
        found[int(parts[0])] = [
            float(window.group(1)),
            float(window.group(2)),
            int(parts[2]),
            parse_tex_value(parts[3]),
            parse_tex_value(parts[4]),
            parse_tex_value(parts[5]),
        ]

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all low-frequency acceptance rows")
    for ell, shown in found.items():
        row = rows[ell]
        expected = [
            float(row["lowest_accepted_omega"]),
            float(row["highest_displayed_omega"]),
            int(row["displayed_points"]),
            float(row["T0_at_lowest"]),
            float(row["T1_at_lowest"]),
            float(row["abs_balance_at_lowest"]),
        ]
        for index, (displayed, actual) in enumerate(zip(shown, expected)):
            if index == 2:
                if displayed != actual:
                    raise AssertionError(
                        f"low-frequency acceptance l={ell} point count mismatch"
                    )
                continue
            tolerance = max(0.06 * abs(displayed), 5.0e-15)
            assert_close(
                f"low-frequency acceptance l={ell} column={index}",
                float(displayed),
                float(actual),
                tolerance,
            )


def check_low_frequency_convergence(tex: str) -> None:
    rows = read_csv_rows(LOW_CONVERGENCE_CSV)
    grouped: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(int(row["l"]), []).append(row)

    table_match = re.search(
        r"\\label\{tab:low-convergence\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find the low-frequency convergence table")

    found: dict[int, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[012]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 6:
            raise AssertionError(f"Malformed low-frequency convergence row: {line}")
        found[int(parts[0])] = [parse_tex_value(part) for part in parts[1:]]

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all low-frequency convergence rows")

    global_max = 0.0
    for ell, shown in found.items():
        case_rows = grouped[ell]
        reference = next(row for row in case_rows if row["config"] == "reference")
        variants = [row for row in case_rows if row["config"] != "reference"]
        expected = [
            float(reference["omega"]),
            float(reference["T1"]),
            max(float(row["rel_T1_to_reference"]) for row in variants),
            max(float(row["rel_R1_to_reference"]) for row in variants),
            max(abs(float(row["nonlinear_balance"])) for row in case_rows),
        ]
        global_max = max(global_max, expected[2])
        for index, (displayed, actual) in enumerate(zip(shown, expected)):
            tolerance = max(0.06 * abs(displayed), 5.0e-14)
            assert_close(
                f"low-frequency convergence l={ell} column={index}",
                displayed,
                actual,
                tolerance,
            )

    claim = re.search(
        r"largest relative change in \$T\^\{\(1\)\}\$ is "
        r"\$(?P<m>[0-9.]+)\\times10\^\{(?P<e>-?\d+)\}\$",
        tex,
    )
    if claim is None:
        raise AssertionError("Could not find the low-frequency convergence claim")
    shown_max = parse_tex_scientific(claim.group("m"), claim.group("e"))
    assert_close("low-frequency convergence maximum", shown_max, global_max, 0.06 * shown_max)


def check_peak_fit_quality(tex: str) -> None:
    rows = {int(row["l"]): row for row in read_csv_rows(FIT_CSV)}
    match = re.search(
        r"relative RMS residuals of these peak fits .*? are\s*"
        r"\$(?P<r0>[0-9.]+)\\%\$,\s*"
        r"\$(?P<r1>[0-9.]+)\\%\$, and\s*"
        r"\$(?P<r2>[0-9.]+)\\%\$",
        tex,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError("Could not find Lorentzian peak-fit quality statement")
    for ell in [0, 1, 2]:
        assert_decimal(
            f"Lorentzian peak relative RMS l={ell}",
            match.group(f"r{ell}"),
            100.0 * float(rows[ell]["peak_rms_over_peak"]),
        )

    r2_match = re.search(
        r"coefficient of determination of the three fits is\s*"
        r"\$R\^2=([0-9.]+)\$,\s*\$([0-9.]+)\$, and\s*\$([0-9.]+)\$",
        tex,
        flags=re.DOTALL,
    )
    if r2_match is None:
        raise AssertionError("Could not find Lorentzian peak-fit R^2 statement")
    for ell, group in enumerate((1, 2, 3)):
        assert_decimal(
            f"Lorentzian peak R^2 l={ell}",
            r2_match.group(group),
            float(rows[ell]["peak_r2"]),
        )


def check_peak_window_sensitivity(tex: str) -> None:
    rows = read_csv_rows(PEAK_WINDOW_CSV)
    match = re.search(
        r"fitted centers vary by at most\s*"
        r"\$([0-9.]+)\\times10\^{-([0-9]+)}\$,\s*"
        r"\$([0-9.]+)\\times10\^{-([0-9]+)}\$, and\s*"
        r"\$([0-9.]+)\\times10\^{-([0-9]+)}\$.*?"
        r"half-widths vary by\s*"
        r"\$([0-9.]+)\\times10\^{-([0-9]+)}\$,\s*"
        r"\$([0-9.]+)\\times10\^{-([0-9]+)}\$, and\s*"
        r"\$([0-9.]+)\\times10\^{-([0-9]+)}\$",
        tex,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError("Could not find peak-window sensitivity statement")
    grouped: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(int(row["l"]), []).append(row)
    centers = []
    widths = []
    for ell in [0, 1, 2]:
        subset = grouped[ell]
        centers.append(max(float(row["omega_peak"]) for row in subset) - min(float(row["omega_peak"]) for row in subset))
        widths.append(max(float(row["gamma"]) for row in subset) - min(float(row["gamma"]) for row in subset))
    for index, actual in enumerate(centers):
        shown = float(match.group(1 + 2 * index)) * 10.0 ** -int(match.group(2 + 2 * index))
        assert_close(f"peak center sensitivity l={index}", shown, actual, 0.15 * shown)
    for index, actual in enumerate(widths):
        offset = 7 + 2 * index
        shown = float(match.group(offset)) * 10.0 ** -int(match.group(offset + 1))
        assert_close(f"peak width sensitivity l={index}", shown, actual, 0.15 * shown)


def check_tail_window_table(tex: str) -> None:
    rows = read_csv_rows(TAIL_WINDOW_CSV)
    table_match = re.search(
        r"\\label\{tab:tail-window\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find the tail-window sensitivity table")

    grouped: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(int(row["l"]), []).append(row)

    found: dict[int, list[float | tuple[float, float]]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[012]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 6:
            raise AssertionError(f"Malformed tail-window row: {line}")
        ell = int(parts[0])
        base_window = re.fullmatch(r"\$\[([0-9.]+),([0-9.]+)\]\$", parts[1])
        range_window = re.fullmatch(r"\$\[([0-9.]+),([0-9.]+)\]\$", parts[3])
        if base_window is None or range_window is None:
            raise AssertionError(f"Malformed tail-window range: {line}")
        found[ell] = [
            (float(base_window.group(1)), float(base_window.group(2))),
            float(parts[2]),
            (float(range_window.group(1)), float(range_window.group(2))),
            parse_tex_value(parts[4]),
            float(parts[5].rstrip("\\%")),
        ]

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all tail-window sensitivity rows")

    for ell, shown in found.items():
        actual = grouped[ell]
        base = next(row for row in actual if row["window"] == "base")
        pi_values = [float(row["pi_Tfit"]) for row in actual]
        rms_values = [float(row["tail_rms_log"]) for row in actual]
        delta_values = [float(row["abs_Tfit_over_TH_minus_1"]) for row in actual]
        assert_close(f"tail-window l={ell} baseline min", shown[0][0], float(base["omega_min"]), 1e-12)
        assert_close(f"tail-window l={ell} baseline max", shown[0][1], float(base["omega_max"]), 1e-12)
        assert_decimal(f"tail-window l={ell} baseline piT", f"{shown[1]:.4f}", float(base["pi_Tfit"]))
        assert_decimal(f"tail-window l={ell} range min", f"{shown[2][0]:.4f}", min(pi_values))
        assert_decimal(f"tail-window l={ell} range max", f"{shown[2][1]:.4f}", max(pi_values))
        assert_close(f"tail-window l={ell} max RMS", shown[3], max(rms_values), 0.15 * 10.0 ** int(f"{shown[3]:.0e}".split("e")[-1]))
        assert_decimal(f"tail-window l={ell} max Hawking offset", f"{shown[4]:.2f}", 100.0 * max(delta_values))


def check_tail_model_table(tex: str) -> None:
    rows = {int(row["l"]): row for row in read_csv_rows(TAIL_MODEL_CSV)}
    table_match = re.search(
        r"\\label\{tab:tail-models\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find the tail-model comparison table")

    found = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[012]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 7:
            raise AssertionError(f"Malformed tail-model row: {line}")
        found[int(parts[0])] = [int(parts[1]), *[parse_tex_value(part) for part in parts[2:]]]

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all tail-model rows")

    for ell, shown in found.items():
        row = rows[ell]
        if shown[0] != int(row["points"]):
            raise AssertionError(f"tail-model l={ell}: point count mismatch")
        tail_rows = [
            item
            for item in read_csv_rows(SWEEP_CSVS[ell][-1])
            if float(row["omega_min"]) <= float(item["omega"])
            <= float(row["omega_max"])
            and float(item["T1"]) > 0.0
            and abs(float(item["nonlinear_balance"])) <= 1.0e-8
        ]
        if len(tail_rows) != int(row["points"]):
            raise AssertionError(
                f"tail-model l={ell}: q=2048 source-point count mismatch"
            )
        if any(
            int(float(item["N"])) != 240
            or int(float(item["quad_order"])) != 2048
            for item in tail_rows
        ):
            raise AssertionError(
                f"tail-model l={ell}: tail-fit source is not uniformly "
                "N=240, q=2048"
            )
        expected = [
            float(row["exp_rms_log"]),
            float(row["power_rms_log"]),
            float(row["delta_aicc_power_minus_exp"]),
            float(row["exp_loo_rms_log"]),
            float(row["power_loo_rms_log"]),
        ]
        for index, (displayed, actual) in enumerate(zip(shown[1:], expected)):
            tolerance = max(0.15 * abs(displayed), 5.0e-3 if index == 2 else 1.0e-5)
            assert_close(f"tail-model l={ell} column={index}", displayed, actual, tolerance)


def check_production_convergence(tex: str) -> None:
    rows = read_csv_rows(PRODUCTION_CSV)
    grouped = {}
    for row in rows:
        grouped[(row["label"], row["config"])] = row

    table_match = re.search(
        r"\\label\{tab:production-convergence\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find the production-convergence table")
    flat = re.sub(r"\s+", " ", table_match.group("body"))
    def scientific(name: str) -> str:
        return rf"\$(?P<{name}_m>[0-9.]+)\\times10\^\{{(?P<{name}_e>-?\d+)\}}\$"

    pattern = re.compile(
        r"\$\\ell=(?P<ell>[012]),\\ M\\omega=(?P<omega>[0-9.]+)\$\s*&\s*"
        + scientific("a")
        + r"\s*&\s*"
        + scientific("h")
        + r"\s*&\s*"
        + scientific("t")
        + r"\s*&\s*"
        + scientific("r")
        + r"\s*&\s*"
        + scientific("b")
        + r"\\",
    )
    matches = list(pattern.finditer(flat))
    if len(matches) != 3:
        raise AssertionError("Could not find all Table IV production rows")

    for match in matches:
        ell = int(match.group("ell"))
        label = f"axisym_l{ell}_peak"
        ref = grouped[(label, "reference")]
        prod = grouped[(label, "production")]
        expected = {
            "a": abs(complex(prod["A_ref_1"]) - complex(ref["A_ref_1"])) / abs(complex(ref["A_ref_1"])),
            "h": abs(complex(prod["A_hor_1"]) - complex(ref["A_hor_1"])) / abs(complex(ref["A_hor_1"])),
            "t": abs(float(prod["T1"]) - float(ref["T1"])) / abs(float(ref["T1"])),
            "r": abs(float(prod["R1"]) - float(ref["R1"])) / abs(float(ref["R1"])),
            "b": abs(float(ref["nonlinear_balance"])),
        }
        for key in ("a", "h", "t", "r", "b"):
            shown = float(match.group(f"{key}_m")) * 10.0 ** int(match.group(f"{key}_e"))
            assert_close(f"Table IV l={ell} {key}", shown, expected[key], 0.15 * 10.0 ** int(match.group(f"{key}_e")))


def check_tail_convergence(tex: str) -> None:
    rows = {
        (row["label"], row["config"]): row
        for row in read_csv_rows(TAIL_CONVERGENCE_CSV)
    }
    table_match = re.search(
        r"\\label\{tab:tail-convergence\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find the tail-convergence table")

    found = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not line.startswith("$\\ell="):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 6:
            raise AssertionError(f"Malformed tail-convergence row: {line}")
        case = re.fullmatch(r"\$\\ell=([012]),\\ M\\omega=([0-9.]+)\$", parts[0])
        if case is None:
            raise AssertionError(f"Malformed tail-convergence case: {parts[0]}")
        ell = int(case.group(1))
        found[ell] = (float(case.group(2)), [parse_tex_value(part) for part in parts[1:]])

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Could not find all tail-convergence rows")

    for ell, (omega, shown) in found.items():
        label = f"axisym_l{ell}_tail"
        reference = rows[(label, "reference")]
        q_test = rows[(label, "q1792")]
        n_test = rows[(label, "N_lower")]
        assert_close(f"tail-convergence l={ell} omega", omega, float(reference["omega"]), 1.0e-12)
        expected = [
            float(q_test["rel_T1_to_reference"]),
            float(n_test["rel_T1_to_reference"]),
            float(q_test["rel_A_ref_to_reference"]),
            float(q_test["rel_A_hor_to_reference"]),
            abs(float(reference["nonlinear_balance"])),
        ]
        for index, (displayed, actual) in enumerate(zip(shown, expected)):
            assert_close(
                f"tail-convergence l={ell} column={index}",
                displayed,
                actual,
                max(0.15 * abs(displayed), 1.0e-15),
            )


def parse_tex_value(text: str) -> float:
    value = text.strip().strip("$").replace("\\,", "")
    if value == "0":
        return 0.0
    if re.fullmatch(r"[-+]?[0-9.]+", value):
        return float(value)
    match = re.fullmatch(r"([-+]?[0-9.]+)\\times10\^\{(-?\d+)\}", value)
    if match is None:
        raise AssertionError(f"unrecognised table number: {text!r}")
    return float(match.group(1)) * 10.0 ** int(match.group(2))


def check_target_channels(tex: str) -> None:
    rows = {
        int(row["l_target"]): row
        for row in read_csv_rows(CHANNEL_CSV)
        if int(row["l_source"]) == 2
    }
    table_match = re.search(
        r"\\label\{tab:channels\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find target-channel table")

    found = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[2-6]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 5:
            raise AssertionError(f"Malformed target-channel row: {line}")
        ell = int(parts[0])
        found[ell] = [parse_tex_value(part) for part in parts[1:]]

    if sorted(found) != [2, 3, 4, 5, 6]:
        raise AssertionError("Could not find all target-channel table rows")

    for ell, shown_values in found.items():
        row = rows[ell]
        actual_values = [
            abs(complex(row["angular_coupling"])),
            abs(complex(row["angular_coupling_cos2"])),
            float(row["abs_A_ref_1"]),
            float(row["abs_A_hor_1"]),
        ]
        for index, (shown, actual) in enumerate(zip(shown_values, actual_values)):
            tolerance = 1.0e-12 if shown == 0.0 else max(0.15 * abs(shown), 1.0e-15)
            assert_close(f"target table l'={ell} column={index}", shown, actual, tolerance)


def check_superradiant_table(tex: str) -> None:
    rows = {
        (round(float(row["a"]), 8), int(row["l"])): row
        for row in read_csv_rows(SUPERRADIANT_CSV)
    }
    table_match = re.search(
        r"\\label\{tab:superradiant\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find superradiant table")

    found: dict[tuple[float, int], list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^0\.[579]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 5:
            raise AssertionError(f"Malformed superradiant row: {line}")
        key = (round(float(parts[0]), 8), int(parts[1]))
        found[key] = [parse_tex_value(part) for part in parts[2:]]

    if sorted(found) != sorted(rows):
        raise AssertionError("Superradiant table rows do not match accepted CSV rows")

    for key, shown_values in found.items():
        row = rows[key]
        actual_values = [
            float(row["horizon_response_threshold"]),
            float(row["T1_over_p_threshold"]),
            float(row["horizon_response_relative_change"]),
        ]
        for index, (shown, actual) in enumerate(zip(shown_values, actual_values)):
            tolerance = 7.5e-7 if index == 0 else max(0.15 * abs(shown), 1.0e-15)
            assert_close(f"superradiant table key={key} column={index}", shown, actual, tolerance)


def check_near_extremal_table(tex: str) -> None:
    rows = [
        row for row in read_csv_rows(MODAL_POWER_FITS_CSV)
        if row["fit_window"] == "nearest3"
    ]
    by_key = {
        (
            int(row["l"]),
            int(row["m"]),
            round(float(row["detuning_over_kappa"]), 8),
        ): row
        for row in rows
    }
    table_match = re.search(
        r"\\label\{tab:near-extremal-threshold\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find near-extremal threshold table")

    found: dict[tuple[int, int], list[str]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        mode_match = re.match(r"^\$\((\d+),(\d+)\)\$\s*&", line)
        if mode_match is None:
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 7:
            raise AssertionError(f"Malformed near-extremal row: {line}")
        found[(int(mode_match.group(1)), int(mode_match.group(2)))] = parts[1:]

    expected_modes = sorted({(key[0], key[1]) for key in by_key})
    if sorted(found) != expected_modes:
        raise AssertionError("Near-extremal modal rows do not match the tracked CSV")
    for mode, shown_parts in found.items():
        h_text = shown_parts[0].strip("$")
        reference = by_key[(mode[0], mode[1], 0.0)]
        h_real = float(reference["conformal_weight_real"])
        h_imag = float(reference["conformal_weight_imag_abs"])
        if "i" in h_text:
            match = re.fullmatch(r"([0-9.]+)\+([0-9.]+)i", h_text)
            if match is None:
                raise AssertionError(f"Malformed conformal weight: {h_text}")
            assert_close(f"conformal h real mode={mode}", float(match.group(1)), h_real, 7.5e-4)
            assert_close(f"conformal h imag mode={mode}", float(match.group(2)), h_imag, 7.5e-4)
        else:
            assert_close(
                f"conformal h mode={mode}", float(h_text), h_real, 7.5e-4
            )
        for index, y in enumerate((-0.5, 0.0, 0.5, 1.0), start=1):
            shown = parse_tex_value(shown_parts[index])
            actual = float(by_key[(mode[0], mode[1], y)]["alpha"])
            assert_close(
                f"modal exponent mode={mode} y={y}", shown, actual, 7.5e-4
            )

    all_22 = next(
        row for row in read_csv_rows(MODAL_POWER_FITS_CSV)
        if row["fit_window"] == "all"
        and row["regime"] == "threshold_p_equals_0_limit"
        and int(row["l"]) == 2
        and int(row["m"]) == 2
    )
    for display, field, tolerance in (
        ("0.02872", "amplitude", 7.5e-6),
        ("1.0037", "alpha", 7.5e-5),
        ("0.99975", "r_squared", 7.5e-6),
    ):
        if display not in tex:
            raise AssertionError(f"Near-extremal summary value {display} is absent")
        assert_close(
            f"near-extremal summary {display}",
            float(display),
            float(all_22[field]),
            tolerance,
        )

    audit_22 = next(
        row for row in read_csv_rows(POWER_MODAL_FITS_CSV)
        if row["fit_window"] == "nearest7"
        and row["regime"] == "threshold_p_equals_0_limit"
        and int(row["nonlinearity_order"]) == 1
        and int(row["l"]) == 2
        and int(row["m"]) == 2
    )
    for display, field, tolerance, scale in (
        ("0.9855", "alpha_ci95_low", 7.5e-5, 1.0),
        ("1.0219", "alpha_ci95_high", 7.5e-5, 1.0),
        ("5.02", "loo_max_relative_prediction_error", 7.5e-3, 100.0),
        ("1.26", "max_resolution_relative_change", 0.01, 1.0e5),
    ):
        if display not in tex:
            raise AssertionError(f"Near-extremal fit-audit value {display} is absent")
        assert_close(
            f"near-extremal fit audit {field}",
            float(display),
            scale * float(audit_22[field]),
            tolerance,
        )


def check_power_modal_table(tex: str) -> None:
    rows = []
    for row in read_csv_rows(POWER_MODAL_FITS_CSV):
        mode = (int(row["l"]), int(row["m"]))
        expected_window = "nearest5" if mode == (2, 1) else "nearest7"
        if (
            row["fit_window"] == expected_window
            and int(row["nonlinearity_order"]) in {2, 3}
            and any(
                math.isclose(float(row["detuning_over_kappa"]), y, abs_tol=1e-12)
                for y in (0.0, 0.5)
            )
        ):
            rows.append(row)
    by_key = {
        (
            int(row["nonlinearity_order"]),
            int(row["l"]),
            int(row["m"]),
            round(float(row["detuning_over_kappa"]), 8),
        ): row
        for row in rows
    }
    table_match = re.search(
        r"\\label\{tab:power-modal\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find higher-power modal table")

    found: dict[tuple[int, int, int], tuple[float, float]] = {}
    current_mode: tuple[int, int] | None = None
    for line in table_match.group("body").splitlines():
        line = line.strip()
        mode_match = re.match(r"^\$\((\d+),(\d+)\)\$\s*&", line)
        if mode_match is not None:
            current_mode = (int(mode_match.group(1)), int(mode_match.group(2)))
        if current_mode is None or not line.endswith(r"\\"):
            continue
        parts = [part.strip() for part in line[:-2].split("&")]
        if len(parts) != 6 or parts[2] not in {"2", "3"}:
            continue
        n = int(parts[2])
        found[(n, *current_mode)] = (
            parse_tex_value(parts[3]),
            parse_tex_value(parts[4]),
        )

    expected_keys = {
        (n, l, m)
        for n in (2, 3)
        for l, m in ((1, 1), (2, 1), (2, 2), (3, 3))
    }
    if set(found) != expected_keys:
        raise AssertionError("Higher-power modal table rows do not match CSV modes")
    for key, shown in found.items():
        n, l, m = key
        expected = (
            float(by_key[(n, l, m, 0.0)]["alpha"]),
            float(by_key[(n, l, m, 0.5)]["alpha"]),
        )
        for index, (displayed, actual) in enumerate(zip(shown, expected)):
            assert_close(
                f"higher-power modal exponent key={key} column={index}",
                displayed,
                actual,
                7.5e-4,
            )


def check_cft_factorization_table(tex: str) -> None:
    rows = []
    for row in read_csv_rows(CFT_FACTORIZATION_FITS_CSV):
        mode = (int(row["l"]), int(row["m"]))
        expected_window = "nearest5" if mode == (2, 1) else "nearest7"
        if (
            row["regime"] == "fixed_nonzero_y"
            and row["fit_window"] == expected_window
            and math.isclose(float(row["detuning_over_kappa"]), 0.5, abs_tol=1e-12)
            and int(row["nonlinearity_order"]) in {2, 3}
        ):
            rows.append(row)
    by_key = {
        (int(row["nonlinearity_order"]), int(row["l"]), int(row["m"])): row
        for row in rows
    }
    table_match = re.search(
        r"\\label\{tab:cft-factorization\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find Kerr/CFT factorization table")

    found: dict[tuple[int, int], list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        mode_match = re.match(r"^\$\((\d+),(\d+)\)\$\s*&", line)
        if mode_match is None or not line.endswith(r"\\"):
            continue
        parts = [part.strip() for part in line[:-2].split("&")]
        if len(parts) != 7:
            raise AssertionError(f"Malformed Kerr/CFT factorization row: {line}")
        analytic_text = parts[1].split()[0]
        found[(int(mode_match.group(1)), int(mode_match.group(2)))] = [
            parse_tex_value(analytic_text),
            *[parse_tex_value(part) for part in parts[2:]],
        ]

    expected_modes = {(1, 1), (2, 1), (2, 2), (3, 3)}
    if set(found) != expected_modes:
        raise AssertionError("Kerr/CFT factorization table modes do not match CSV")
    for l, m in sorted(expected_modes):
        row2 = by_key[(2, l, m)]
        row3 = by_key[(3, l, m)]
        actual = [
            float(row2["analytic_intensity_alpha"]),
            float(row2["alpha_intensity"]),
            float(row2["alpha_kernel"]),
            float(row2["alpha_response"]),
            float(row3["alpha_kernel"]),
            float(row3["alpha_response"]),
        ]
        for index, (displayed, expected) in enumerate(zip(found[(l, m)], actual)):
            assert_close(
                f"Kerr/CFT factorization mode={(l, m)} column={index}",
                displayed,
                expected,
                7.5e-4,
            )


def check_power_fit_quality_table(tex: str) -> None:
    rows = [
        row for row in read_csv_rows(POWER_MODAL_FITS_CSV)
        if row["fit_window"] == "nearest7"
        and int(row["nonlinearity_order"]) in {2, 3}
        and (int(row["l"]), int(row["m"])) in {(2, 2), (3, 3)}
        and any(
            math.isclose(float(row["detuning_over_kappa"]), y, abs_tol=1e-12)
            for y in (0.0, 0.5)
        )
    ]
    by_key = {
        (
            int(row["l"]),
            int(row["m"]),
            int(row["nonlinearity_order"]),
            round(float(row["detuning_over_kappa"]), 8),
        ): row
        for row in rows
    }
    table_match = re.search(
        r"\\label\{tab:power-fit-quality\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find principal fit-quality table")

    found = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        mode_match = re.match(r"^\$\((\d+),(\d+)\)\$\s*&", line)
        if mode_match is None or not line.endswith(r"\\"):
            continue
        parts = [part.strip() for part in line[:-2].split("&")]
        if len(parts) != 7 or parts[1] not in {"2", "3"}:
            continue
        y = 0.0 if "p\\to0" in parts[2] else 0.5
        interval = re.fullmatch(
            r"([0-9.]+)\s*\[([0-9.]+),([0-9.]+)\]", parts[3]
        )
        if interval is None:
            raise AssertionError(f"Malformed fit interval: {parts[3]}")
        loo = float(parts[5].replace(r"\%", "")) / 100.0
        key = (
            int(mode_match.group(1)),
            int(mode_match.group(2)),
            int(parts[1]),
            y,
        )
        found[key] = [
            float(interval.group(1)),
            float(interval.group(2)),
            float(interval.group(3)),
            parse_tex_value(parts[4]),
            loo,
            parse_tex_value(parts[6]),
        ]

    if set(found) != set(by_key):
        raise AssertionError("Principal fit-quality table rows do not match CSV")
    for key, displayed in found.items():
        row = by_key[key]
        expected = [
            float(row["alpha"]),
            float(row["alpha_ci95_low"]),
            float(row["alpha_ci95_high"]),
            float(row["r_squared"]),
            float(row["loo_max_relative_prediction_error"]),
            float(row["max_resolution_relative_change"]),
        ]
        tolerances = [7.5e-5, 7.5e-5, 7.5e-5, 7.5e-9, 7.5e-5, 0.15 * displayed[-1]]
        for index, (shown, actual, tolerance) in enumerate(
            zip(displayed, expected, tolerances)
        ):
            assert_close(
                f"principal fit-quality key={key} column={index}",
                shown,
                actual,
                tolerance,
            )


def check_power_window_drift_summary(tex: str) -> None:
    rows = [
        row for row in read_csv_rows(POWER_MODAL_FITS_CSV)
        if int(row["nonlinearity_order"]) in {2, 3}
        and (int(row["l"]), int(row["m"])) in {(2, 2), (3, 3)}
        and row["fit_window"] in {"nearest7", "nearest3"}
        and (
            row["regime"] == "threshold_p_equals_0_limit"
            or (
                row["regime"] == "fixed_nonzero_y"
                and math.isclose(float(row["detuning_over_kappa"]), 0.5, abs_tol=1e-12)
            )
        )
    ]
    by_key = {
        (
            int(row["nonlinearity_order"]),
            int(row["l"]),
            row["regime"],
            row["fit_window"],
        ): float(row["alpha"])
        for row in rows
    }
    match = re.search(
        r"changes the principal \$n=2\$ slopes from\s*"
        r"\$(?P<a>[0-9.]+)\$ to \$(?P<b>[0-9.]+)\$ for \$\(2,2\)\$ and from "
        r"\$(?P<c>[0-9.]+)\$ to \$(?P<d>[0-9.]+)\$ for \$\(3,3\)\$ at\s*"
        r"threshold\.\s*For \$n=3\$ the corresponding nearest-three values are "
        r"\$(?P<e>[0-9.]+)\$ and\s*\$(?P<f>[0-9.]+)\$\.\s*At fixed \$y=0\.5\$, "
        r"all four nearest-three slopes lie between\s*\$(?P<g>[0-9.]+)\$ and "
        r"\$(?P<h>[0-9.]+)\$ or between \$(?P<i>[0-9.]+)\$ and "
        r"\$(?P<j>[0-9.]+)\$",
        tex,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Could not parse nested-window slope audit")

    fixed_n2 = [
        by_key[(2, l, "fixed_nonzero_y", "nearest3")] for l in (2, 3)
    ]
    fixed_n3 = [
        by_key[(3, l, "fixed_nonzero_y", "nearest3")] for l in (2, 3)
    ]
    expected = [
        by_key[(2, 2, "threshold_p_equals_0_limit", "nearest7")],
        by_key[(2, 2, "threshold_p_equals_0_limit", "nearest3")],
        by_key[(2, 3, "threshold_p_equals_0_limit", "nearest7")],
        by_key[(2, 3, "threshold_p_equals_0_limit", "nearest3")],
        by_key[(3, 2, "threshold_p_equals_0_limit", "nearest3")],
        by_key[(3, 3, "threshold_p_equals_0_limit", "nearest3")],
        min(fixed_n2),
        max(fixed_n2),
        min(fixed_n3),
        max(fixed_n3),
    ]
    for key, actual in zip("abcdefghij", expected):
        assert_close(
            f"nested-window slope {key}",
            float(match.group(key)),
            actual,
            7.5e-5,
        )


def check_spin_limit_table(tex: str) -> None:
    rows = {round(float(row["a"]), 8): row for row in read_csv_rows(SPIN_LIMIT_CSV)}
    table_match = re.search(
        r"\\label\{tab:spin-limit\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find spin-limit table")

    found: dict[float, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^0\.[0-9]+\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 6:
            raise AssertionError(f"Malformed spin-limit row: {line}")
        a = float(parts[0])
        found[round(a, 8)] = [parse_tex_value(part) for part in parts[1:]]

    if sorted(found) != sorted(rows):
        raise AssertionError("Spin-limit table rows do not match the tracked CSV")

    for a, shown_values in found.items():
        row = rows[a]
        actual_values = [
            float(row["T1"]),
            float(row["R1"]),
            abs(float(row["linear_balance"])),
            abs(float(row["nonlinear_balance"])),
            float(row["wronskian_relative_error"]),
        ]
        for index, (shown, actual) in enumerate(zip(shown_values, actual_values)):
            tolerance = max(0.15 * abs(shown), 1.0e-15)
            assert_close(f"spin-limit table a={a} column={index}", shown, actual, tolerance)


def check_l0_zero_frequency_table(tex: str) -> None:
    rows = {
        round(float(row["a"]), 8): row for row in read_csv_rows(L0_ZERO_CSV)
    }
    table_match = re.search(
        r"\\label\{tab:l0-zero-frequency\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find scalar-monopole zero-frequency table")

    found: dict[float, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^0\.[0-9]+\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 4:
            raise AssertionError(f"Malformed scalar-monopole row: {line}")
        found[round(float(parts[0]), 8)] = [
            parse_tex_value(part) for part in parts[1:]
        ]

    if sorted(found) != sorted(rows):
        raise AssertionError("Scalar-monopole table spins do not match tracked CSV")

    for a, shown_values in found.items():
        row = rows[a]
        actual_values = [
            float(row["zero_frequency_response"]),
            float(row["relative_error_to_analytic"]),
            float(row["max_resolution_relative_change"]),
        ]
        for index, (shown, actual) in enumerate(zip(shown_values, actual_values)):
            tolerance = max(0.06 * abs(shown), 5.0e-9)
            assert_close(
                f"scalar-monopole table a={a} column={index}",
                shown,
                actual,
                tolerance,
            )

    analytic = math.log(2.0) / math.pi
    match = re.search(
        r"\\frac\{\\ln 2\}\{\\pi\}\s*=\s*(?P<value>[0-9.]+)", tex
    )
    if match is None:
        raise AssertionError("Could not find analytic scalar-monopole value")
    assert_close(
        "analytic scalar-monopole response",
        float(match.group("value")),
        analytic,
        7.5e-13,
    )


def check_axisymmetric_infrared_table(tex: str) -> None:
    low_rows = {
        (int(row["l"]), float(row["omega"])): row
        for row in read_csv_rows(AXISYMMETRIC_IR_LOW_CSV)
    }
    high_by_l: dict[int, list[dict[str, str]]] = {}
    for row in read_csv_rows(AXISYMMETRIC_IR_HIGH_CSV):
        high_by_l.setdefault(int(row["l"]), []).append(row)
    table_match = re.search(
        r"\\label\{tab:axisymmetric-infrared\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find axisymmetric infrared table")

    found: dict[int, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[012]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 7:
            raise AssertionError(f"Malformed axisymmetric infrared row: {line}")
        found[int(parts[0])] = [parse_tex_value(part) for part in parts[1:]]

    if sorted(found) != [0, 1, 2]:
        raise AssertionError("Axisymmetric infrared table is missing a multipole")
    for ell, shown in found.items():
        rows = high_by_l[ell]
        high = min(rows, key=lambda row: float(row["omega"]))
        key = (ell, float(high["omega"]))
        low = low_rows[key]
        delta_response = abs(
            float(high["horizon_response"])
            - float(low["horizon_response"])
        ) / abs(float(high["horizon_response"]))
        expected = [
            float(high["infrared_integral"]),
            float(high["analytic_response_limit"]),
            float(high["analytic_T0_coefficient"]),
            float(high["analytic_T1_coefficient"]),
            float(high["omega"]),
            delta_response,
        ]
        for index, (displayed, actual) in enumerate(zip(shown, expected)):
            tolerance = max(0.06 * abs(displayed), 7.5e-13)
            assert_close(
                f"axisymmetric infrared l={ell} column={index}",
                displayed,
                actual,
                tolerance,
            )


def check_axisymmetric_complex_response(tex: str) -> None:
    low_rows = {
        (int(row["l"]), float(row["omega"])): row
        for row in read_csv_rows(AXISYMMETRIC_IR_LOW_CSV)
    }
    high_by_l: dict[int, list[dict[str, str]]] = {}
    for row in read_csv_rows(AXISYMMETRIC_IR_HIGH_CSV):
        high_by_l.setdefault(int(row["l"]), []).append(row)
    high_rows = [
        min(high_by_l[ell], key=lambda row: float(row["omega"]))
        for ell in (0, 1, 2)
    ]

    patterns = {
        "phase_integral": (
            r"\\mathcal J_\\ell=\(([^)]+)\)",
            [float(row["phase_integral"]) for row in high_rows],
            7.5e-13,
        ),
        "phase_deg": (
            r"limiting\s+phases\s+\$?\(([^)]+)\)",
            [
                math.degrees(float(row["analytic_A_hor_1_phase_rad"]))
                for row in high_rows
            ],
            7.5e-5,
        ),
        "complex_error_percent": (
            r"complex relative responses agree.*?to\s+\$?\(([^)]+)\)\\%",
            [
                100.0
                * float(row["relative_horizon_amplitude_complex_relative_error"])
                for row in high_rows
            ],
            7.5e-4,
        ),
    }
    for label, (pattern, expected, tolerance) in patterns.items():
        match = re.search(pattern, tex, flags=re.DOTALL)
        if match is None:
            raise AssertionError(f"Could not find axisymmetric {label} triplet")
        shown = [
            parse_tex_value(value.strip().replace(r"^\circ", ""))
            for value in match.group(1).split(",")
        ]
        if len(shown) != 3:
            raise AssertionError(f"Malformed axisymmetric {label} triplet")
        for ell, (displayed, actual) in enumerate(zip(shown, expected)):
            assert_close(
                f"axisymmetric {label} l={ell}",
                displayed,
                actual,
                tolerance,
            )

    delta_match = re.search(
        r"simultaneous-resolution changes are\s+\$?\(([^)]+)\)",
        tex,
        flags=re.DOTALL,
    )
    if delta_match is None:
        raise AssertionError("Could not find complex-response resolution triplet")
    shown_delta = [
        parse_tex_value(value.strip())
        for value in delta_match.group(1).split(",")
    ]
    for ell, (displayed, high) in enumerate(zip(shown_delta, high_rows)):
        low = low_rows[(ell, float(high["omega"]))]
        high_value = complex(
            float(high["relative_horizon_amplitude_real"]),
            float(high["relative_horizon_amplitude_imag"]),
        )
        low_value = complex(
            float(low["relative_horizon_amplitude_real"]),
            float(low["relative_horizon_amplitude_imag"]),
        )
        actual = abs(high_value - low_value) / abs(high_value)
        assert_close(
            f"axisymmetric complex response resolution l={ell}",
            displayed,
            actual,
            max(0.08 * actual, 7.5e-8),
        )


def check_axisymmetric_infrared_fits(tex: str) -> None:
    rows = {
        (int(row["l"]), row["quantity"], int(row["points"])): row
        for row in read_csv_rows(AXISYMMETRIC_IR_FITS_CSV)
    }
    patterns = {
        ("T0", 7): r"For \$T\^\{\(0\)\}\$ the fitted powers are "
        r"\$([0-9.]+)\$, \$([0-9.]+)\$, and \$([0-9.]+)\$",
        ("T1", 7): r"for\s*\$T\^\{\(1\)\}\$ they are "
        r"\$([0-9.]+)\$, \$([0-9.]+)\$, and \$([0-9.]+)\$",
        ("T0", 5): r"sets to \$\(([0-9.]+),([0-9.]+),([0-9.]+)\)\$ and",
        ("T1", 5): (
            r"and \$\(([0-9.]+),([0-9.]+),([0-9.]+)\)\$,\s*respectively"
        ),
    }
    for (quantity, points), pattern in patterns.items():
        match = re.search(pattern, tex, flags=re.DOTALL)
        if match is None:
            raise AssertionError(
                f"Could not find {points}-point infrared {quantity} powers"
            )
        for ell, shown in enumerate(match.groups()):
            assert_decimal(
                f"infrared fit {quantity} l={ell} points={points}",
                shown,
                float(rows[(ell, quantity, points)]["power"]),
            )

    stated_r2 = re.search(r"Every fit has\s*\$R\^2>([0-9.]+)\$", tex)
    if stated_r2 is None:
        raise AssertionError("Could not find infrared fit R^2 bound")
    actual_min = min(float(row["R2"]) for row in rows.values())
    if actual_min <= float(stated_r2.group(1)):
        raise AssertionError(
            f"infrared R^2 bound {stated_r2.group(1)} exceeds data {actual_min}"
        )


def check_offgrid_radial_residuals(tex: str) -> None:
    rows = read_csv_rows(SPECTRAL_RESIDUAL_CSV)
    values = [
        float(row["radial_relative_residual"])
        for row in rows
        if row["radial_relative_residual"]
    ]
    if not values:
        raise AssertionError("No off-grid radial residual values found")
    if any(row.get("sample_kind") != "chebyshev-gauss-offgrid" for row in rows):
        raise AssertionError("Spectral residual CSV contains non-off-grid samples")

    ordered = sorted(values)
    index = 0.95 * (len(ordered) - 1)
    lower = int(math.floor(index))
    upper = int(math.ceil(index))
    weight = index - lower
    percentile95 = ordered[lower] * (1.0 - weight) + ordered[upper] * weight
    midpoint = len(ordered) // 2
    median = (
        ordered[midpoint]
        if len(ordered) % 2
        else 0.5 * (ordered[midpoint - 1] + ordered[midpoint])
    )
    expected = [max(values), percentile95, median]
    match = re.search(
        r"Across the (?P<count>\d+) off-grid validation points,.*?"
        r"maximum, 95th-percentile, and median values\s*"
        r"\$(?P<m0>[0-9.]+)\\times10\^\{(?P<e0>-?\d+)\}\$,\s*"
        r"\$(?P<m1>[0-9.]+)\\times10\^\{(?P<e1>-?\d+)\}\$, and\s*"
        r"\$(?P<m2>[0-9.]+)\\times10\^\{(?P<e2>-?\d+)\}\$",
        tex,
        flags=re.DOTALL,
    )
    if match is None:
        raise AssertionError("Could not find off-grid radial-residual statement")
    if int(match.group("count")) != len(values):
        raise AssertionError("Off-grid radial-residual sample count mismatch")
    for i, actual in enumerate(expected):
        shown = parse_tex_scientific(match.group(f"m{i}"), match.group(f"e{i}"))
        assert_close(
            f"off-grid radial residual statistic {i}",
            shown,
            actual,
            0.15 * shown,
        )


def check_power_nonlinearity_table(tex: str) -> None:
    fixed_rows = read_csv_rows(POWER_FIXED_CSV)
    kappa_rows = read_csv_rows(POWER_KAPPA_CSV)
    table_match = re.search(
        r"\\label\{tab:power-l0\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find higher-power monopole table")

    found: dict[int, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^[23]\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 7:
            raise AssertionError(f"Malformed higher-power row: {line}")
        slope_match = re.fullmatch(r"([0-9.]+)--([0-9.]+)", parts[3])
        if slope_match is None:
            raise AssertionError(f"Malformed fixed-frequency slope range: {parts[3]}")
        found[int(parts[0])] = [
            parse_tex_value(parts[1]),
            parse_tex_value(parts[2]),
            float(slope_match.group(1)),
            float(slope_match.group(2)),
            parse_tex_value(parts[4]),
            parse_tex_value(parts[5]),
            parse_tex_value(parts[6]),
        ]

    if sorted(found) != [2, 3]:
        raise AssertionError("Higher-power table must contain n=2 and n=3")
    for n, shown in found.items():
        fixed = [row for row in fixed_rows if int(row["nonlinearity_order"]) == n]
        kappa = next(
            row for row in kappa_rows
            if int(row["nonlinearity_order"]) == n
            and math.isclose(float(row["omega_over_kappa"]), 0.025)
        )
        slopes = [float(row["fitted_frequency_power"]) for row in fixed]
        expected = [
            float(fixed[0]["analytic_low_frequency_coefficient"]),
            float(fixed[0]["predicted_frequency_power"]),
            min(slopes),
            max(slopes),
            float(kappa["fitted_kappa_power_high_spin"]),
            max(float(row["relative_error_to_analytic_coefficient"]) for row in fixed),
            max(
                max(float(row["max_resolution_relative_change"]) for row in fixed),
                max(
                    float(row["max_resolution_relative_change"])
                    for row in kappa_rows
                    if int(row["nonlinearity_order"]) == n
                ),
            ),
        ]
        tolerances = [7.5e-11, 0.0, 7.5e-6, 7.5e-6, 7.5e-6,
                      0.08 * shown[5], 0.08 * shown[6]]
        for index, (displayed, actual, tolerance) in enumerate(
            zip(shown, expected, tolerances)
        ):
            assert_close(
                f"higher-power table n={n} column={index}",
                displayed,
                actual,
                tolerance,
            )

    coefficient_rows = read_csv_rows(POWER_SPECTRAL_COEFF_CSV)
    residual_rows = read_csv_rows(POWER_SPECTRAL_RESIDUAL_CSV)
    tail = max(float(row["normalized_abs_coeff"]) for row in coefficient_rows[-16:])
    # The manuscript quotes the maximum over the final 16 coefficients of
    # each branch, not merely the final 16 rows of the concatenated file.
    branches = {(row["branch"], row["subdomain"]) for row in coefficient_rows}
    tail = 0.0
    for branch in branches:
        subset = [
            row for row in coefficient_rows
            if (row["branch"], row["subdomain"]) == branch
        ]
        tail = max(tail, max(float(row["normalized_abs_coeff"]) for row in subset[-16:]))
    values = sorted(
        float(row["radial_relative_residual"])
        for row in residual_rows
        if row["radial_relative_residual"]
    )
    percentile95_index = 0.95 * (len(values) - 1)
    lower = math.floor(percentile95_index)
    upper = math.ceil(percentile95_index)
    weight = percentile95_index - lower
    percentile95 = values[lower] * (1.0 - weight) + values[upper] * weight
    median = 0.5 * (values[len(values) // 2 - 1] + values[len(values) // 2])
    match = re.search(
        r"last 16 normalized.*?at most \$(?P<t>[0-9.]+)\\times10\^\{(?P<te>-?\d+)\}\$\."
        r".*?Across (?P<count>\d+) independent.*?has median\s*"
        r"\$(?P<m>[0-9.]+)\\times10\^\{(?P<me>-?\d+)\}\$, 95th percentile\s*"
        r"\$(?P<p>[0-9.]+)\\times10\^\{(?P<pe>-?\d+)\}\$, and a localized\s*"
        r"maximum \$(?P<x>[0-9.]+)\\times10\^\{(?P<xe>-?\d+)\}\$",
        tex,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("Could not find higher-power spectral-quality statement")
    if int(match.group("count")) != len(values):
        raise AssertionError("Higher-power off-grid residual count mismatch")
    shown_quality = [
        parse_tex_scientific(match.group("t"), match.group("te")),
        parse_tex_scientific(match.group("m"), match.group("me")),
        parse_tex_scientific(match.group("p"), match.group("pe")),
        parse_tex_scientific(match.group("x"), match.group("xe")),
    ]
    expected_quality = [tail, median, percentile95, max(values)]
    for index, (displayed, actual) in enumerate(zip(shown_quality, expected_quality)):
        assert_close(
            f"higher-power spectral-quality statistic {index}",
            displayed,
            actual,
            0.15 * displayed,
        )


def check_angular_convergence(tex: str) -> None:
    rows = read_csv_rows(ANGULAR_CSV)
    table_match = re.search(
        r"\\label\{tab:angular-convergence\}(?P<body>.*?)\\end\{table\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find angular-convergence table")

    config_lookup = {
        "active": "active",
        "basis": "basis_lower",
        "quadrature": "quadrature_lower",
    }
    found: dict[str, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        config_name = line.split(maxsplit=1)[0] if line else ""
        if config_name not in config_lookup:
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 4:
            raise AssertionError(f"Malformed angular-convergence row: {line}")
        found[config_lookup[config_name]] = [
            parse_tex_value(part) for part in parts[1:]
        ]

    if sorted(found) != sorted(config_lookup.values()):
        raise AssertionError("Angular-convergence table rows do not match CSV")
    for config, shown in found.items():
        subset = [row for row in rows if row["config"] == config]
        expected = [
            max(float(row["max_rel_lambda_to_reference"]) for row in subset),
            max(float(row["rel_C0_to_reference"]) for row in subset),
            max(float(row["rel_C2_to_reference"]) for row in subset),
        ]
        for index, (displayed, actual) in enumerate(zip(shown, expected)):
            tolerance = 1.0e-18 if displayed == 0.0 else 0.15 * abs(displayed)
            assert_close(
                f"angular-convergence {config} column={index}",
                displayed,
                actual,
                tolerance,
            )


def check_bandwidth_hierarchy(tex: str) -> None:
    fit_rows = read_csv_rows(POWER_BANDWIDTH_FITS_CSV)
    fit_lookup = {
        (int(row["nonlinearity_order"]), int(row["l"]), int(row["m"])): row
        for row in fit_rows
    }
    exponent_match = re.search(
        r"n=1 & (?P<n122>[0-9.]+) & (?P<r122>[0-9.]+) & "
        r"(?P<n133>[0-9.]+) & (?P<r133>[0-9.]+)\\\\\s*"
        r"n=2 & (?P<n222>[0-9.]+) & (?P<r222>[0-9.]+) & "
        r"(?P<n233>[0-9.]+) & (?P<r233>[0-9.]+)\\\\\s*"
        r"n=3 & (?P<n322>[0-9.]+) & (?P<r322>[0-9.]+) & "
        r"(?P<n333>[0-9.]+) & (?P<r333>[0-9.]+)",
        tex,
    )
    if exponent_match is None:
        raise AssertionError("Could not find bandwidth effective-exponent array")
    for group, key in [
        ("n122", (1, 2, 2)),
        ("n133", (1, 3, 3)),
        ("n222", (2, 2, 2)),
        ("n233", (2, 3, 3)),
        ("n322", (3, 2, 2)),
        ("n333", (3, 3, 3)),
    ]:
        shown = float(exponent_match.group(group))
        actual = float(fit_lookup[key]["spectral_weight_alpha"])
        assert_close(f"bandwidth exponent {key}", shown, actual, 7.5e-5)
        shown_r2 = float(exponent_match.group(f"r{group[1:]}"))
        actual_r2 = float(fit_lookup[key]["r_squared"])
        assert_close(f"bandwidth R-squared {key}", shown_r2, actual_r2, 7.5e-6)

    inner_match = re.search(
        r"innermost-pair exponents for \$n=1,2,3\$ are\s*"
        r"\$\((?P<n122>[0-9.]+),(?P<n222>[0-9.]+),(?P<n322>[0-9.]+)\)\$ "
        r"for \$\(2,2\)\$ and \$\((?P<n133>[0-9.]+),(?P<n233>[0-9.]+),"
        r"(?P<n333>[0-9.]+)\)\$ for\s*\$\(3,3\)\$",
        tex,
    )
    if inner_match is None:
        raise AssertionError("Could not find innermost bandwidth exponents")
    for group, key in [
        ("n122", (1, 2, 2)),
        ("n133", (1, 3, 3)),
        ("n222", (2, 2, 2)),
        ("n233", (2, 3, 3)),
        ("n322", (3, 2, 2)),
        ("n333", (3, 3, 3)),
    ]:
        assert_close(
            f"innermost bandwidth exponent {key}",
            float(inner_match.group(group)),
            float(fit_lookup[key]["innermost_pair_alpha"]),
            7.5e-5,
        )

    band_rows = read_csv_rows(POWER_BANDWIDTH_CSV)
    expected_band_diagnostics = [
        max(float(row["max_point_resolution_relative_change"]) for row in band_rows),
        max(float(row["integral_resolution_relative_change"]) for row in band_rows),
        max(float(row["max_nonlinear_relative_balance"]) for row in band_rows),
    ]
    diagnostics_match = re.search(
        r"largest pointwise resolution change is\s*"
        r"\$(?P<p>[0-9.]+)\\times10\^\{(?P<pe>-?\d+)\}\$, "
        r"the largest integral change is \$(?P<i>[0-9.]+)\\times10\^\{(?P<ie>-?\d+)\}\$,\s*"
        r"and the largest flux-relative first-order balance residual is\s*"
        r"\$(?P<b>[0-9.]+)\\times10\^\{(?P<be>-?\d+)\}\$",
        tex,
    )
    if diagnostics_match is None:
        raise AssertionError("Could not find bandwidth diagnostics")
    shown_band_diagnostics = [
        parse_tex_scientific(diagnostics_match.group("p"), diagnostics_match.group("pe")),
        parse_tex_scientific(diagnostics_match.group("i"), diagnostics_match.group("ie")),
        parse_tex_scientific(diagnostics_match.group("b"), diagnostics_match.group("be")),
    ]
    for index, (shown, actual) in enumerate(zip(shown_band_diagnostics, expected_band_diagnostics)):
        assert_close(f"bandwidth diagnostic {index}", shown, actual, 0.01 * actual)

    peak_rows = read_csv_rows(POWER_PEAK_MIGRATION_CSV)
    peak_lookup = {
        (int(row["nonlinearity_order"]), int(row["l"]), int(row["m"])): row
        for row in peak_rows
    }
    peak_match = re.search(
        r"y_\{\\rm pk\} & (?P<y122>[0-9.]+) & (?P<y222>[0-9.]+) & (?P<y322>[0-9.]+) "
        r"& (?P<y133>[0-9.]+) & (?P<y233>[0-9.]+) & (?P<y333>[0-9.]+)\\\\\s*"
        r"\\sigma_y & (?P<s122>[0-9.]+) & (?P<s222>[0-9.]+) & (?P<s322>[0-9.]+) "
        r"& (?P<s133>[0-9.]+) & (?P<s233>[0-9.]+) & (?P<s333>[0-9.]+)",
        tex,
    )
    if peak_match is None:
        raise AssertionError("Could not find peak-migration array")
    peak_groups = [
        ("y122", "log_quadratic_peak_y", (1, 2, 2)),
        ("y222", "log_quadratic_peak_y", (2, 2, 2)),
        ("y322", "log_quadratic_peak_y", (3, 2, 2)),
        ("y133", "log_quadratic_peak_y", (1, 3, 3)),
        ("y233", "log_quadratic_peak_y", (2, 3, 3)),
        ("y333", "log_quadratic_peak_y", (3, 3, 3)),
        ("s122", "local_log_gaussian_sigma", (1, 2, 2)),
        ("s222", "local_log_gaussian_sigma", (2, 2, 2)),
        ("s322", "local_log_gaussian_sigma", (3, 2, 2)),
        ("s133", "local_log_gaussian_sigma", (1, 3, 3)),
        ("s233", "local_log_gaussian_sigma", (2, 3, 3)),
        ("s333", "local_log_gaussian_sigma", (3, 3, 3)),
    ]
    for group, column, key in peak_groups:
        assert_close(
            f"peak migration {group}",
            float(peak_match.group(group)),
            float(peak_lookup[key][column]),
            7.5e-4,
        )

    expected_peak_diagnostics = [
        max(float(row["max_point_resolution_relative_change"]) for row in peak_rows),
        max(float(row["max_nonlinear_relative_balance"]) for row in peak_rows),
    ]
    peak_diagnostics_match = re.search(
        r"All 60 dense-scan rows pass; the largest paired-response change is\s*"
        r"\$(?P<p>[0-9.]+)\\times10\^\{(?P<pe>-?\d+)\}\$ and the largest "
        r"flux-relative balance residual is\s*"
        r"\$(?P<b>[0-9.]+)\\times10\^\{(?P<be>-?\d+)\}\$",
        tex,
    )
    if peak_diagnostics_match is None:
        raise AssertionError("Could not find peak-migration diagnostics")
    shown_peak_diagnostics = [
        parse_tex_scientific(peak_diagnostics_match.group("p"), peak_diagnostics_match.group("pe")),
        parse_tex_scientific(peak_diagnostics_match.group("b"), peak_diagnostics_match.group("be")),
    ]
    for index, (shown, actual) in enumerate(zip(shown_peak_diagnostics, expected_peak_diagnostics)):
        assert_close(f"peak diagnostic {index}", shown, actual, 0.01 * actual)

def main() -> None:
    tex = TEX.read_text(encoding="utf-8")
    check_table_i(tex)
    check_table_ii(tex)
    check_low_frequency_acceptance(tex)
    check_low_frequency_convergence(tex)
    check_peak_fit_quality(tex)
    check_peak_window_sensitivity(tex)
    check_tail_window_table(tex)
    check_tail_model_table(tex)
    check_production_convergence(tex)
    check_tail_convergence(tex)
    check_target_channels(tex)
    check_superradiant_table(tex)
    check_near_extremal_table(tex)
    check_power_modal_table(tex)
    check_power_fit_quality_table(tex)
    check_power_window_drift_summary(tex)
    check_cft_factorization_table(tex)
    check_l0_zero_frequency_table(tex)
    check_axisymmetric_infrared_table(tex)
    check_axisymmetric_complex_response(tex)
    check_axisymmetric_infrared_fits(tex)
    check_power_nonlinearity_table(tex)
    check_spin_limit_table(tex)
    check_offgrid_radial_residuals(tex)
    check_angular_convergence(tex)
    check_bandwidth_hierarchy(tex)
    print("PRD manuscript numeric checks passed.")


if __name__ == "__main__":
    main()
