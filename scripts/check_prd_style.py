"""Check the active manuscript against the repository's PRD structure gates."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex"
PDF = ROOT / "docs/prd/kerr_scalar_nonlinear_GF_baseframe.pdf"
METADATA = ROOT / "docs/prd/submission_metadata.template.json"
COVER_LETTER = ROOT / "docs/prd/cover_letter.template.md"


def section_names(tex: str) -> set[str]:
    return set(re.findall(r"\\section\*?\{([^{}]+)\}", tex))


def labels(tex: str, prefix: str) -> set[str]:
    return set(re.findall(rf"\\label\{{({prefix}:[^}}]+)\}}", tex))


def refs(tex: str, prefix: str) -> set[str]:
    return set(re.findall(rf"\\(?:eq)?ref\{{({prefix}:[^}}]+)\}}", tex))


def prose_word_count(tex: str) -> int:
    text = re.sub(r"%.*", " ", tex)
    text = re.sub(r"\$.*?\$", " ", text, flags=re.DOTALL)
    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^]]*\])?", " ", text)
    text = re.sub(r"[{}~]", " ", text)
    return len(re.findall(r"\b[A-Za-z0-9][A-Za-z0-9'-]*\b", text))


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

    title_match = re.search(r"\\title\{([^{}]+)\}", tex)
    if title_match is None:
        raise AssertionError("manuscript title could not be parsed")
    title = title_match.group(1)
    metadata_title = json.loads(METADATA.read_text(encoding="utf-8"))["submission"]["title"]
    if metadata_title != title:
        raise AssertionError("submission metadata title does not match manuscript title")
    if f"> {title}" not in COVER_LETTER.read_text(encoding="utf-8"):
        raise AssertionError("cover-letter title does not match manuscript title")

    abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.DOTALL)
    if abstract_match is None:
        raise AssertionError("abstract is missing")
    if r"\cite" in abstract_match.group(1):
        raise AssertionError("the abstract must not contain citation commands")
    abstract_words = prose_word_count(abstract_match.group(1))
    if not 150 <= abstract_words <= 500:
        raise AssertionError(
            f"abstract must contain 150--500 prose words; found {abstract_words}"
        )

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

    all_labels = re.findall(r"\\label\{([^}]+)\}", tex)
    duplicate_labels = sorted(
        label for label in set(all_labels) if all_labels.count(label) > 1
    )
    if duplicate_labels:
        raise AssertionError(f"duplicate manuscript labels: {duplicate_labels}")

    for prefix in ("fig", "tab", "eq", "sec", "app"):
        declared = labels(tex, prefix)
        referenced = refs(tex, prefix)
        missing = referenced - declared
        if missing:
            raise AssertionError(f"unresolved {prefix} references: {sorted(missing)}")

    forbidden = ("s=-2", "spin-minus2", "GeneralizedSasakiNakamura", "Mathematica", "benchmark")
    leaked = [token for token in forbidden if token.lower() in tex.lower()]
    if leaked:
        raise AssertionError(f"off-scope manuscript tokens: {leaked}")

    data_match = re.search(
        r"\\section\*\{Data and code availability\}(.*?)(?:\\appendix|\\section)",
        tex,
        re.DOTALL,
    )
    if data_match is None:
        raise AssertionError("data/code availability statement could not be parsed")
    data_statement = data_match.group(1).lower()
    required_data_terms = {
        "review package": "identify the frozen review-stage reproduction package",
        "reasonable request": "state how editors and referees can access nonpublic data",
        "persistent identifier": "state the versioned archival-release plan",
    }
    missing_data_terms = [
        detail for term, detail in required_data_terms.items() if term not in data_statement
    ]
    if missing_data_terms:
        raise AssertionError(
            "incomplete data/code availability statement: " + "; ".join(missing_data_terms)
        )
    if "\\section{Flux normalizations}" not in tex:
        raise AssertionError("flux normalization derivation must remain in the manuscript")

    required_physics_patterns = {
        r"interaction is \$U\(1\)\$ invariant": (
            "state why the complex-scalar cubic source closes at fixed frequency"
        ),
        r"positive quartic": (
            "state the sign conversion between epsilon and a conventional quartic potential"
        ),
        r"\\label\{eq:amplitude_scaling\}": (
            "retain the incident-amplitude scaling of the nonlinear flux response"
        ),
        r"\\label\{eq:first_order_balance\}": (
            "retain the first-order flux-balance identity"
        ),
        r"\\label\{eq:radial_residual\}": (
            "retain the field-dependent off-grid residual definition"
        ),
        r"real scalar with a \$\\Phi\^3\$ source": (
            "distinguish the single-frequency complex field from real-scalar harmonics"
        ),
        r"\\label\{eq:windowed-spectral-hierarchy\}": (
            "retain the finite-bandwidth hierarchy and its one-power softening"
        ),
        r"\\label\{eq:peak-factorization-condition\}": (
            "retain the qualified interpretation of operator-dependent peak migration"
        ),
    }
    missing_physics = [
        detail
        for pattern, detail in required_physics_patterns.items()
        if re.search(pattern, tex, re.DOTALL) is None
    ]
    if missing_physics:
        raise AssertionError(
            "incomplete physics-scope safeguards: " + "; ".join(missing_physics)
        )

    print("PRD style and structure audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
