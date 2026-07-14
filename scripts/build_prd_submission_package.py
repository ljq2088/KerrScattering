"""Build a self-contained PRD manuscript package.

By default this script refuses to package the draft unless the submission
readiness audit passes.  Use ``--allow-draft`` for an internal review package
while final author and submission metadata are still pending.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRD_DIR = ROOT / "docs" / "prd"
FINAL_PACKAGE = PRD_DIR / "submission_package"
DRAFT_PACKAGE = PRD_DIR / "submission_package_draft"
FINAL_ZIP = PRD_DIR / "submission_package.zip"
DRAFT_ZIP = PRD_DIR / "submission_package_draft.zip"
MANIFEST = PRD_DIR / "artifact_manifest.json"
ACTIVE_TEX = PRD_DIR / "kerr_scalar_nonlinear_GF_baseframe.tex"
ACTIVE_PDF = PRD_DIR / "kerr_scalar_nonlinear_GF_baseframe.pdf"
ROOT_PDF = ROOT / "kerr_scalar_nonlinear_GF_baseframe.pdf"


STATIC_FILES = [
    PRD_DIR / "README.md",
    PRD_DIR / "PRD_SUBMISSION_CHECKLIST.md",
    PRD_DIR / "artifact_manifest.json",
    PRD_DIR / "cover_letter.template.md",
    PRD_DIR / "reproducibility_report.md",
    PRD_DIR / "environment_snapshot.txt",
    PRD_DIR / "submission_metadata.template.json",
    ACTIVE_TEX,
    ACTIVE_PDF,
    ROOT_PDF,
]

OPTIONAL_STATIC_FILES = [
    PRD_DIR / "submission_metadata.json",
    PRD_DIR / "cover_letter.md",
]

SCRIPT_FILES = [
    ROOT / "scripts" / "apply_prd_submission_metadata.py",
    ROOT / "scripts" / "build_prd_manuscript.py",
    ROOT / "scripts" / "build_prd_submission_package.py",
    ROOT / "scripts" / "check_prd_artifacts.py",
    ROOT / "scripts" / "check_prd_citations.py",
    ROOT / "scripts" / "check_prd_manuscript_numbers.py",
    ROOT / "scripts" / "check_prd_submission_ready.py",
    ROOT / "scripts" / "check_prd_style.py",
    ROOT / "scripts" / "build_prd_convergence_summary.py",
    ROOT / "scripts" / "plot_kerr_scalar_axisymmetric_accuracy.py",
    ROOT / "scripts" / "plot_kerr_scalar_low_frequency_axisymmetric.py",
    ROOT / "scripts" / "analyze_kerr_scalar_low_frequency_window_sensitivity.py",
    ROOT / "scripts" / "plot_kerr_scalar_nonlinear_axisymmetric_base_like.py",
    ROOT / "scripts" / "analyze_kerr_scalar_tail_window_sensitivity.py",
    ROOT / "scripts" / "plot_kerr_scalar_spin_limit.py",
    ROOT / "scripts" / "render_prd_cover_letter.py",
    ROOT / "scripts" / "run_kerr_scalar_spin_limit.py",
    ROOT / "scripts" / "write_prd_artifact_manifest.py",
    ROOT / "scripts" / "write_prd_reproducibility_report.py",
]


def run(command: list[str], *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    print("+", " ".join(command))
    if completed.stdout:
        print(completed.stdout)
    if completed.returncode and not allow_failure:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
        )
    return completed


def clean_directory(path: Path) -> None:
    resolved = path.resolve()
    prd_resolved = PRD_DIR.resolve()
    if resolved == prd_resolved or prd_resolved not in resolved.parents:
        raise RuntimeError(f"Refusing to remove unexpected package directory: {path}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def clean_archive(path: Path) -> None:
    if not path.exists():
        return
    resolved = path.resolve()
    prd_resolved = PRD_DIR.resolve()
    if prd_resolved not in resolved.parents:
        raise RuntimeError(f"Refusing to remove unexpected package archive: {path}")
    path.unlink()


def copy_file(source: Path, package_dir: Path) -> str:
    rel = source.relative_to(ROOT)
    target = package_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return rel.as_posix()


def package_artifacts(package_dir: Path) -> list[str]:
    copied: list[str] = []
    with MANIFEST.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    for entry in manifest["artifacts"]:
        copied.append(copy_file(ROOT / entry["path"], package_dir))
    return copied


def write_package_manifest(
    package_dir: Path,
    copied_files: list[str],
    readiness_returncode: int,
    readiness_output: str,
    *,
    draft: bool,
) -> None:
    package_manifest = {
        "draft": draft,
        "readiness_returncode": readiness_returncode,
        "readiness_output": readiness_output,
        "files": sorted(copied_files),
    }
    (package_dir / "package_manifest.json").write_text(
        json.dumps(package_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_package_readme(package_dir: Path, *, draft: bool) -> str:
    label = "DRAFT internal-review package" if draft else "FINAL submission package"
    warning = (
        "\nThis draft package still contains submission-readiness blockers. "
        "Inspect `package_manifest.json` before circulation.\n"
        if draft
        else "\nThe submission-readiness audit passed when this package was built.\n"
    )
    text = f"""# Kerr Scalar PRD {label}

{warning}
Core files:

- `docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf`
- `docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex`
- `docs/prd/artifact_manifest.json`
- `docs/prd/reproducibility_report.md`
- `package_manifest.json`

Useful checks from the package root:

```powershell
python scripts\\check_prd_artifacts.py
python scripts\\check_prd_citations.py
python scripts\\check_prd_manuscript_numbers.py
python scripts\\check_prd_style.py
python scripts\\check_prd_submission_ready.py
```

The figure and CSV inputs are copied under `figures/` and `results/`.  The
included scripts are the PRD-specific build, check, plotting, metadata, and
reporting utilities used for this draft.  If `docs/prd/submission_metadata.json`
or `docs/prd/cover_letter.md` existed when the package was built, those final
submission-support files are copied as well.
"""
    target = package_dir / "PACKAGE_README.md"
    target.write_text(text, encoding="utf-8", newline="\n")
    return target.relative_to(package_dir).as_posix()


def write_archive(package_dir: Path, archive_path: Path) -> None:
    clean_archive(archive_path)
    base_name = archive_path.with_suffix("")
    shutil.make_archive(str(base_name), "zip", root_dir=package_dir)
    print(f"Wrote PRD package archive: {archive_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Create an internal-review package even when readiness has blockers.",
    )
    args = parser.parse_args()

    run([sys.executable, str(ROOT / "scripts" / "build_prd_manuscript.py")])
    run([sys.executable, str(ROOT / "scripts" / "write_prd_reproducibility_report.py")])
    readiness = run(
        [sys.executable, str(ROOT / "scripts" / "check_prd_submission_ready.py")],
        allow_failure=args.allow_draft,
    )
    if readiness.returncode and not args.allow_draft:
        raise SystemExit(readiness.returncode)

    package_dir = DRAFT_PACKAGE if args.allow_draft else FINAL_PACKAGE
    archive_path = DRAFT_ZIP if args.allow_draft else FINAL_ZIP
    clean_directory(package_dir)

    copied = [copy_file(path, package_dir) for path in STATIC_FILES]
    copied.extend(
        copy_file(path, package_dir)
        for path in OPTIONAL_STATIC_FILES
        if path.exists()
    )
    copied.extend(copy_file(path, package_dir) for path in SCRIPT_FILES)
    copied.extend(package_artifacts(package_dir))
    copied.append(write_package_readme(package_dir, draft=args.allow_draft))
    write_package_manifest(
        package_dir,
        copied,
        readiness.returncode,
        readiness.stdout.strip(),
        draft=args.allow_draft,
    )
    write_archive(package_dir, archive_path)
    print(f"Wrote PRD package: {package_dir}")


if __name__ == "__main__":
    main()
