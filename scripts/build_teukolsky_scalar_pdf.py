"""Build docs/teukolsky_scalar_kerr.pdf from the markdown derivation.

The derivation contains Chinese text, Unicode symbols, and long Teukolsky
formula blocks. XeLaTeX gives a much more reliable scientific PDF than drawing
text line-by-line through matplotlib.
"""
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "teukolsky_scalar_kerr.md"
PDF_PATH = ROOT / "docs" / "teukolsky_scalar_kerr.pdf"
BUILD_DIR = ROOT / "docs" / "_pdfbuild"


LATEX_SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _escape(text):
    return "".join(LATEX_SPECIALS.get(ch, ch) for ch in text)


def _inline(text):
    parts = text.split("`")
    rendered = []
    for idx, part in enumerate(parts):
        if idx % 2:
            rendered.append(r"\texttt{" + _escape(part) + "}")
        else:
            rendered.append(_escape(part))
    return "".join(rendered)


def _markdown_to_latex(markdown):
    lines = []
    in_code = False
    title_emitted = False

    for raw in markdown.splitlines():
        stripped = raw.strip()

        if stripped.startswith("```"):
            if in_code:
                lines.append(r"\end{Verbatim}")
                lines.append("")
                in_code = False
            else:
                lines.append(r"\begin{Verbatim}[fontsize=\small,breaklines=true,breakanywhere=true]")
                in_code = True
            continue

        if in_code:
            lines.append(raw)
            continue

        if not stripped:
            lines.append("")
            continue

        if stripped.startswith("# "):
            title = _inline(stripped[2:].strip())
            if not title_emitted:
                lines.extend([
                    r"\begin{center}",
                    r"{\LARGE\bfseries " + title + r"}",
                    r"\end{center}",
                    r"\vspace{0.5em}",
                ])
                title_emitted = True
            else:
                lines.append(r"\section*{" + title + r"}")
            continue

        if stripped.startswith("## "):
            lines.append(r"\section*{" + _inline(stripped[3:].strip()) + r"}")
            continue

        if stripped.startswith("### "):
            lines.append(r"\subsection*{" + _inline(stripped[4:].strip()) + r"}")
            continue

        numbered = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if numbered:
            lines.append(
                r"\noindent\textbf{"
                + _escape(numbered.group(1) + ".")
                + r"} "
                + _inline(numbered.group(2))
                + r"\par"
            )
            continue

        if stripped.startswith("- "):
            lines.append(r"\noindent$\bullet$ " + _inline(stripped[2:].strip()) + r"\par")
            continue

        lines.append(_inline(raw) + r"\par")

    return "\n".join(lines)


def _document(body):
    return rf"""
\documentclass[UTF8,fontset=windows,11pt]{{ctexart}}
\usepackage[a4paper,margin=2.2cm]{{geometry}}
\usepackage{{amsmath,amssymb}}
\usepackage{{fvextra}}
\usepackage{{enumitem}}
\usepackage[hidelinks]{{hyperref}}
\setmainfont{{Times New Roman}}
\setsansfont{{Arial}}
\setmonofont{{Consolas}}
\setCJKmainfont{{Microsoft YaHei}}
\setCJKsansfont{{Microsoft YaHei}}
\setCJKmonofont{{Microsoft YaHei}}
\DefineVerbatimEnvironment{{Verbatim}}{{Verbatim}}{{breaklines,breakanywhere,fontsize=\small}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.55em}}
\linespread{{1.08}}
\sloppy
\begin{{document}}
{body}
\end{{document}}
"""


def main():
    xelatex = shutil.which("xelatex")
    if not xelatex:
        raise RuntimeError("xelatex was not found on PATH; install TeX Live or add xelatex to PATH.")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    tex_path = BUILD_DIR / "teukolsky_scalar_kerr.tex"
    body = _markdown_to_latex(MD_PATH.read_text(encoding="utf-8"))
    tex_path.write_text(_document(body), encoding="utf-8")

    for _ in range(2):
        proc = subprocess.run(
            [
                xelatex,
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name,
            ],
            cwd=BUILD_DIR,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            log = BUILD_DIR / "teukolsky_scalar_kerr.log"
            detail = log.read_text(encoding="utf-8", errors="replace")[-4000:] if log.exists() else proc.stdout
            raise RuntimeError(detail)

    built_pdf = BUILD_DIR / "teukolsky_scalar_kerr.pdf"
    shutil.copy2(built_pdf, PDF_PATH)
    print(PDF_PATH)


if __name__ == "__main__":
    main()
