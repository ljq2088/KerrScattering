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
SLOPE_CSV = ROOT / "results" / "kerr_scalar_low_frequency_axisymmetric_slopes.csv"
PRODUCTION_CSV = ROOT / "results" / "kerr_scalar_axisymmetric_production_convergence.csv"
CHANNEL_CSV = ROOT / "results" / "kerr_scalar_nonlinear_channels.csv"
SUPERRADIANT_CSV = ROOT / "results" / "kerr_scalar_nonlinear_m2_superradiant.csv"
SPIN_LIMIT_CSV = ROOT / "results" / "kerr_scalar_spin_limit.csv"
SWEEP_CSVS = {
    0: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l0.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l0.csv",
    ],
    1: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l1.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l1.csv",
    ],
    2: [
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l2.csv",
        ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l2.csv",
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
            residual = abs(float(row["nonlinear_balance"]))
            old = best.get(omega)
            if old is None or residual < abs(float(old["nonlinear_balance"])):
                best[omega] = row
    return [best[omega] for omega in sorted(best)]


def check_table_ii(tex: str) -> None:
    tail_rows = {int(row["l"]): row for row in read_csv_rows(FIT_CSV)}
    pattern = re.compile(
        r"^(?P<l>[012])\s*&\s*"
        r"(?P<points>\d+)\s*&\s*"
        r"\$(?P<d0_m>[0-9.]+)\\times10\^\{(?P<d0_e>-?\d+)\}\$\s*&\s*"
        r"(?P<acc>\d+)/(?P<total>\d+)\s*&\s*"
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
        max_delta0 = max(abs(float(row["linear_balance"]) - 1.0) for row in rows)
        max_delta1_acc = max(abs(float(row["nonlinear_balance"])) for row in accepted)
        tail_rms = float(tail_rows[ell]["tail_rms_log"])

        if int(groups["points"]) != len(rows):
            raise AssertionError(f"Table II l={ell}: point count mismatch")
        if int(groups["acc"]) != len(accepted) or int(groups["total"]) != len(rows):
            raise AssertionError(f"Table II l={ell}: accepted count mismatch")

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


def check_low_frequency_slopes(tex: str) -> None:
    slopes = {int(row["l"]): row for row in read_csv_rows(SLOPE_CSV)}
    nonlinear_match = re.search(
        r"\\alpha_0\\simeq(?P<a0>[0-9.]+),\\quad\s*"
        r"\\alpha_1\\simeq(?P<a1>[0-9.]+),\\quad\s*"
        r"\\alpha_2\\simeq(?P<a2>[0-9.]+)",
        tex,
    )
    if nonlinear_match is None:
        raise AssertionError("Could not find nonlinear low-frequency slopes")
    for ell in [0, 1, 2]:
        assert_decimal(
            f"low-frequency T1 slope l={ell}",
            nonlinear_match.group(f"a{ell}"),
            float(slopes[ell]["T1_slope"]),
        )

    linear_match = re.search(
        r"The corresponding linear slopes are approximately\s*"
        r"\$(?P<s0>[0-9.]+)\$, \$(?P<s1>[0-9.]+)\$, and \$(?P<s2>[0-9.]+)\$",
        tex,
    )
    if linear_match is None:
        raise AssertionError("Could not find linear low-frequency slopes")
    for ell in [0, 1, 2]:
        assert_decimal(
            f"low-frequency T0 slope l={ell}",
            linear_match.group(f"s{ell}"),
            float(slopes[ell]["T0_slope"]),
        )


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


def check_production_convergence(tex: str) -> None:
    rows = read_csv_rows(PRODUCTION_CSV)
    grouped = {}
    for row in rows:
        grouped[(row["label"], row["config"])] = row

    flat = re.sub(r"\s+", " ", tex)
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
        round(float(row["omega"]), 8): row
        for row in read_csv_rows(SUPERRADIANT_CSV)
        if abs(float(row["abs_nonlinear_balance"])) <= 1.0e-8
    }
    table_match = re.search(
        r"\\label\{tab:superradiant\}(?P<body>.*?)\\end\{table\*\}",
        tex,
        re.DOTALL,
    )
    if table_match is None:
        raise AssertionError("Could not find superradiant table")

    found: dict[float, list[float]] = {}
    for line in table_match.group("body").splitlines():
        line = line.strip()
        if not re.match(r"^0\.[0-9]+\s*&", line):
            continue
        parts = [part.strip() for part in line.rstrip("\\").split("&")]
        if len(parts) != 5:
            raise AssertionError(f"Malformed superradiant row: {line}")
        omega = float(parts[0])
        found[round(omega, 8)] = [parse_tex_value(part) for part in parts[1:]]

    if sorted(found) != sorted(rows):
        raise AssertionError("Superradiant table rows do not match accepted CSV rows")

    for omega, shown_values in found.items():
        row = rows[omega]
        actual_values = [
            float(row["p_horizon"]),
            float(row["T0"]),
            float(row["T1"]),
            abs(float(row["nonlinear_balance"])),
        ]
        for index, (shown, actual) in enumerate(zip(shown_values, actual_values)):
            tolerance = max(0.15 * abs(shown), 1.0e-15)
            assert_close(f"superradiant table omega={omega} column={index}", shown, actual, tolerance)


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

def main() -> None:
    tex = TEX.read_text(encoding="utf-8")
    check_table_i(tex)
    check_table_ii(tex)
    check_low_frequency_slopes(tex)
    check_peak_fit_quality(tex)
    check_tail_window_table(tex)
    check_production_convergence(tex)
    check_target_channels(tex)
    check_superradiant_table(tex)
    check_spin_limit_table(tex)
    print("PRD manuscript numeric checks passed.")


if __name__ == "__main__":
    main()
