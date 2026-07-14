"""Check the active manuscript against the repository's PRD structure gates."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex"
PDF = ROOT / "docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf"


def section_names(tex: str) -> set[str]:
    return set(re.findall(r"\\section\*?\{([^{}]+)\}", tex))


def labels(tex: str, prefix: str) -> set[str]:
    return set(re.findall(rf"\\label\{{({prefix}:[^}}]+)\}}", tex))


def refs(tex: str, prefix: str) -> set[str]:
    return set(re.findall(rf"\\ref\{{({prefix}:[^}}]+)\}}", tex))


def main() -> int:
    tex = TEX.read_text(encoding="utf-8")
    if not PDF.is_file():
        raise AssertionError("active PRD PDF is missing")

    documentclass = re.search(r"\\documentclass\[([^]]+)\]\{revtex4-2\}", tex)
    if documentclass is None:
        raise AssertionError("active manuscript must use REVTeX 4.2")
    options = {item.strip() for item in documentclass.group(1).split(",")}
    required_options = {"aps", "prd", "twocolumn"}
    if not required_options.issubset(options):
        raise AssertionError(f"missing PRD document-class options: {sorted(required_options - options)}")

    for command in ("title", "author", "affiliation", "keywords"):
        if not re.search(rf"\\{command}\{{", tex):
            raise AssertionError(f"missing manuscript command: \\{command}")
    if tex.count(r"\maketitle") != 1:
        raise AssertionError("the manuscript must contain exactly one \\maketitle")

    abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.DOTALL)
    if abstract_match is None:
        raise AssertionError("abstract is missing")
    if r"\cite" in abstract_match.group(1):
        raise AssertionError("the abstract must not contain citation commands")

    required_sections = {
        "Introduction",
        "Nonlinear scattering problem in Kerr spacetime",
        "Methods",
        "Results",
        "Discussion and outlook",
        "Data and code availability",
    }
    missing_sections = required_sections - section_names(tex)
    if missing_sections:
        raise AssertionError(f"missing PRD sections: {sorted(missing_sections)}")

    for prefix in ("fig", "tab"):
        declared = labels(tex, prefix)
        referenced = refs(tex, prefix)
        missing = referenced - declared
        if missing:
            raise AssertionError(f"unresolved {prefix} references: {sorted(missing)}")

    forbidden = ("s=-2", "spin-minus2", "GeneralizedSasakiNakamura", "Mathematica", "benchmark")
    leaked = [token for token in forbidden if token.lower() in tex.lower()]
    if leaked:
        raise AssertionError(f"off-scope manuscript tokens: {leaked}")

    if "https://github.com/ljq2088/KerrScattering" not in tex:
        raise AssertionError("data/code availability statement must identify the repository")
    if "\\section{Flux normalizations}" not in tex:
        raise AssertionError("flux normalization derivation must remain in the manuscript")

    print("PRD style and structure audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
