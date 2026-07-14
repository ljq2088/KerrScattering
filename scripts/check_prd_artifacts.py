"""Check that PRD manuscript input artifacts exist and have expected schemas."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "prd" / "artifact_manifest.json"

FIGURES = [
    ROOT / "figures" / "kerr_scalar_low_frequency_axisymmetric.png",
    ROOT / "figures" / "kerr_scalar_nonlinear_axisymmetric_fig2.png",
    ROOT / "figures" / "kerr_scalar_axisymmetric_accuracy.png",
    ROOT / "figures" / "kerr_scalar_nonlinear_superradiant_m2.png",
]

CSV_SCHEMAS = {
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l0.csv": [
        "omega", "B_inc", "B_ref", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l1.csv": [
        "omega", "B_inc", "B_ref", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_hires_l2.csv": [
        "omega", "B_inc", "B_ref", "T0", "R0", "linear_balance",
        "T1", "R1", "nonlinear_balance", "abs_nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l0.csv": [
        "omega", "T1", "R1", "linear_balance", "nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l1.csv": [
        "omega", "T1", "R1", "linear_balance", "nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_refine_l2.csv": [
        "omega", "T1", "R1", "linear_balance", "nonlinear_balance",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_axisymmetric_fit_table.csv": [
        "l", "omega_peak", "gamma", "qnm_real", "qnm_imag_abs",
        "peak_rms_over_peak", "peak_r2", "peak_fit_points", "pi_Tfit",
        "Tfit_over_TH_minus_1_abs", "tail_rms_log",
    ],
    ROOT / "results" / "kerr_scalar_low_frequency_axisymmetric_slopes.csv": [
        "l", "T0_slope", "T1_slope",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_spectral_coefficients.csv": [
        "branch", "subdomain", "k", "abs_coeff", "normalized_abs_coeff",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_spectral_residuals.csv": [
        "branch", "subdomain", "node_index", "relative_residual",
        "radial_relative_residual", "term_scale",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_spectral_quality_summary.csv": [
        "case", "branch", "subdomain", "coeff_tail_ratio",
        "max_radial_relative_residual",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_convergence_summary.csv": [
        "case", "N_reference", "N_test_max_relative_A_ref",
        "N_test_max_relative_A_H", "r_match_reference",
        "r_match_test_max_relative_A_ref", "r_match_test_max_relative_A_H",
        "quad_reference", "quad_test_max_relative_A_ref",
        "quad_test_max_relative_A_H", "max_Wronskian_relative_error",
    ],
    ROOT / "results" / "kerr_scalar_axisymmetric_production_convergence.csv": [
        "label", "config", "N", "quad_order", "A_ref_1", "A_hor_1",
        "T1", "R1", "nonlinear_balance", "rel_A_ref_to_reference",
        "rel_A_hor_to_reference", "rel_T1_to_reference",
        "rel_R1_to_reference", "rss_after_mb",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_channels.csv": [
        "l_source", "l_target", "m", "a", "omega", "angular_coupling",
        "angular_coupling_cos2", "abs_A_ref_1", "abs_A_hor_1",
        "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_channel_convergence.csv": [
        "l_source", "l_target", "N_outer", "quad_order",
        "rel_A_ref_to_reference", "rel_A_hor_to_reference",
        "wronskian_relative_error", "status",
    ],
    ROOT / "results" / "kerr_scalar_nonlinear_m2_superradiant.csv": [
        "l", "m", "omega", "p_horizon", "superradiant", "T0", "T1",
        "R1", "nonlinear_balance", "abs_nonlinear_balance",
        "wronskian_relative_error", "status",
    ],
}

ALL_ARTIFACTS = [*FIGURES, *CSV_SCHEMAS.keys()]


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a valid PNG file")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def check_figures() -> None:
    for path in FIGURES:
        if not path.exists():
            raise AssertionError(f"Missing figure: {path}")
        if path.stat().st_size < 10_000:
            raise AssertionError(f"Figure is suspiciously small: {path}")
        width, height = png_size(path)
        if width < 600 or height < 300:
            raise AssertionError(
                f"Figure resolution is suspiciously low: {path} ({width}x{height})"
            )


def check_csv(path: Path, required_columns: list[str]) -> None:
    if not path.exists():
        raise AssertionError(f"Missing CSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AssertionError(f"CSV has no header: {path}")
        missing = [column for column in required_columns if column not in reader.fieldnames]
        if missing:
            raise AssertionError(f"{path} is missing columns: {', '.join(missing)}")
        row_count = sum(1 for _row in reader)
    if row_count == 0:
        raise AssertionError(f"CSV has no data rows: {path}")


def check_csvs() -> None:
    for path, columns in CSV_SCHEMAS.items():
        check_csv(path, columns)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def check_manifest() -> None:
    if not MANIFEST.exists():
        raise AssertionError(
            f"Missing artifact manifest: {MANIFEST}. "
            "Run scripts/write_prd_artifact_manifest.py after regenerating PRD inputs."
        )
    with MANIFEST.open(encoding="utf-8") as handle:
        data = json.load(handle)
    entries = data.get("artifacts")
    if not isinstance(entries, list):
        raise AssertionError(f"{MANIFEST} does not contain an 'artifacts' list")

    by_path = {entry.get("path"): entry for entry in entries}
    expected = {relative_path(path) for path in ALL_ARTIFACTS}
    actual = set(by_path)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        raise AssertionError(f"{MANIFEST} is missing artifacts: {', '.join(missing)}")
    if extra:
        raise AssertionError(f"{MANIFEST} contains unused artifacts: {', '.join(extra)}")

    for path in ALL_ARTIFACTS:
        rel = relative_path(path)
        entry = by_path[rel]
        size = path.stat().st_size
        digest = sha256_file(path)
        if entry.get("size_bytes") != size:
            raise AssertionError(
                f"{rel} size differs from manifest: {size} != {entry.get('size_bytes')}"
            )
        if entry.get("sha256") != digest:
            raise AssertionError(f"{rel} sha256 differs from manifest")


def main() -> None:
    check_figures()
    check_csvs()
    check_manifest()
    print("PRD artifact checks passed.")


if __name__ == "__main__":
    main()
