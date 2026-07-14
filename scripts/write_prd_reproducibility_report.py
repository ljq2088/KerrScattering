"""Write a PRD reproducibility report for the active Kerr manuscript."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "prd" / "reproducibility_report.md"
MANIFEST = ROOT / "docs" / "prd" / "artifact_manifest.json"
TEX = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.tex"
PDF = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.pdf"
ROOT_PDF = ROOT / "kerr_scalar_nonlinear_GF_baseframe.pdf"
DEFAULT_SOURCE_DATE_EPOCH = "1704067200"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def run_check(command: list[str]) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def status_label(returncode: int, *, expected_failure: bool = False) -> str:
    if returncode == 0:
        return "PASS"
    if expected_failure:
        return "EXPECTED BLOCKERS"
    return "FAIL"


def artifact_table(entries: list[dict[str, object]]) -> list[str]:
    lines = [
        "| Path | Kind | Rows/size | Bytes | SHA-256 |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for entry in entries:
        detail = ""
        if entry.get("kind") == "figure":
            detail = f"{entry['width_px']}x{entry['height_px']} px"
        elif entry.get("kind") == "csv":
            detail = f"{entry['rows']} rows"
        lines.append(
            "| {path} | {kind} | {detail} | {size} | `{digest}` |".format(
                path=entry["path"],
                kind=entry["kind"],
                detail=detail,
                size=entry["size_bytes"],
                digest=str(entry["sha256"])[:16],
            )
        )
    return lines


def file_summary_table(paths: list[Path]) -> list[str]:
    lines = [
        "| File | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
    ]
    for path in paths:
        lines.append(
            f"| {rel(path)} | {path.stat().st_size} | `{sha256_file(path)}` |"
        )
    return lines


def fenced(text: str) -> str:
    if not text:
        return "```text\n<no output>\n```"
    return "```text\n" + text + "\n```"


def main() -> None:
    source_date_epoch = int(
        os.environ.get("SOURCE_DATE_EPOCH", DEFAULT_SOURCE_DATE_EPOCH)
    )
    build_timestamp = datetime.fromtimestamp(
        source_date_epoch, tz=timezone.utc
    ).isoformat(timespec="seconds")
    with MANIFEST.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    checks = [
        (
            "Artifact manifest/schema check",
            [sys.executable, str(ROOT / "scripts" / "check_prd_artifacts.py")],
            False,
        ),
        (
            "Manuscript numeric consistency check",
            [sys.executable, str(ROOT / "scripts" / "check_prd_manuscript_numbers.py")],
            False,
        ),
        (
            "Citation integrity check",
            [sys.executable, str(ROOT / "scripts" / "check_prd_citations.py")],
            False,
        ),
        (
            "Submission readiness audit",
            [sys.executable, str(ROOT / "scripts" / "check_prd_submission_ready.py")],
            True,
        ),
    ]
    check_results = [
        (name, *run_check(command), expected_failure)
        for name, command, expected_failure in checks
    ]

    lines: list[str] = [
        "# Kerr Scalar PRD Reproducibility Report",
        "",
        f"Generated from build epoch: `{build_timestamp}`",
        f"Build `SOURCE_DATE_EPOCH`: `{source_date_epoch}`",
        "",
        "This report records the local artifacts used by the active PRD-style "
        "draft `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`.",
        "",
        "## Manuscript Files",
        "",
        *file_summary_table([TEX, PDF, ROOT_PDF, MANIFEST]),
        "",
        "## Frozen Figure And CSV Inputs",
        "",
        *artifact_table(manifest["artifacts"]),
        "",
        "## Checks",
        "",
    ]

    for name, returncode, output, expected_failure in check_results:
        lines.extend(
            [
                f"### {name}",
                "",
                f"Status: **{status_label(returncode, expected_failure=expected_failure)}**",
                "",
                fenced(output),
                "",
            ]
        )

    lines.extend(
        [
            "## Rebuild Commands",
            "",
            "```powershell",
            "python scripts\\write_prd_artifact_manifest.py",
            "python scripts\\build_prd_manuscript.py",
            "python scripts\\check_prd_citations.py",
            "python scripts\\check_prd_submission_ready.py",
            "```",
            "",
            "The readiness audit is expected to report blockers until the final "
            "author metadata, submission metadata, and cover letter are "
            "available.",
            "",
        ]
    )

    REPORT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
