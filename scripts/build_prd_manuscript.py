"""Build the active PRD manuscript with submission-prep checks.

The script is intentionally small and conservative:

1. verify required figure/CSV artifacts exist, have expected schemas, and
   match the frozen artifact manifest;
2. verify manuscript display numbers against tracked CSV files;
3. run pdflatex twice in the manuscript directory;
4. fail on unresolved references, citation warnings, overfull boxes, or TeX
   errors in the final log;
5. copy the generated PDF to the repository root for convenient inspection;
6. remove auxiliary LaTeX files unless requested otherwise.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX_DIR = ROOT / "docs" / "prd"
TEX_NAME = "kerr_scalar_nonlinear_GF_baseframe.tex"
PDF_NAME = "kerr_scalar_nonlinear_GF_baseframe.pdf"
LOG_NAME = "kerr_scalar_nonlinear_GF_baseframe.log"
AUX_NAMES = [
    "kerr_scalar_nonlinear_GF_baseframe.aux",
    "kerr_scalar_nonlinear_GF_baseframe.log",
    "kerr_scalar_nonlinear_GF_baseframe.out",
    "kerr_scalar_nonlinear_GF_baseframeNotes.bib",
]


FAIL_PATTERNS = [
    re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    for pattern in [
        r"undefined references",
        r"undefined citations",
        r"citation `[^']+' .* undefined",
        r"reference `[^']+' .* undefined",
        r"package natbib warning",
        r"latex warning",
        r"overfull \\hbox",
        r"fatal error",
        r"! latex error",
        r"^!",
    ]
]


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def run_pdflatex() -> None:
    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        TEX_NAME,
    ]
    # REVTeX can place a newly added table on a later page after the second
    # pass.  A third pass makes the label state deterministic before the log
    # is audited for unresolved references.
    for _ in range(3):
        run(command, cwd=TEX_DIR)


def check_latex_log() -> None:
    log_path = TEX_DIR / LOG_NAME
    text = log_path.read_text(encoding="utf-8", errors="replace")
    failures: list[str] = []
    for pattern in FAIL_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            excerpt = text[match.start(): text.find("\n", match.start())]
            failures.append(f"line {line}: {excerpt}")
            break
    if failures:
        joined = "\n".join(failures)
        raise RuntimeError(f"LaTeX log contains submission-blocking warnings:\n{joined}")


def copy_pdf() -> None:
    source = TEX_DIR / PDF_NAME
    target = ROOT / PDF_NAME
    if not source.exists():
        raise FileNotFoundError(source)
    shutil.copy2(source, target)
    print(f"Copied {source} -> {target}")


def clean_aux() -> None:
    for name in AUX_NAMES:
        path = TEX_DIR / name
        if path.exists():
            path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep-aux",
        action="store_true",
        help="Keep LaTeX auxiliary files after a successful build.",
    )
    args = parser.parse_args()

    run([sys.executable, str(ROOT / "scripts" / "check_prd_artifacts.py")])
    run([sys.executable, str(ROOT / "scripts" / "check_prd_manuscript_numbers.py")])
    run([sys.executable, str(ROOT / "scripts" / "check_prd_citations.py")])
    run_pdflatex()
    check_latex_log()
    copy_pdf()
    if not args.keep_aux:
        clean_aux()
    print("PRD manuscript build passed.")


if __name__ == "__main__":
    main()
