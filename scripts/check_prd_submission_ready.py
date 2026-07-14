"""Audit whether the PRD manuscript has no remaining submission placeholders.

This check is stricter than ``build_prd_manuscript.py``.  The build script
verifies a reproducible, internally consistent draft.  This script answers the
separate question "is it ready to submit without manual metadata edits?"
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.tex"
PDF = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.pdf"
ROOT_PDF = ROOT / "kerr_scalar_nonlinear_GF_baseframe.pdf"
METADATA_TEMPLATE = ROOT / "docs" / "prd" / "submission_metadata.template.json"
METADATA_FINAL = ROOT / "docs" / "prd" / "submission_metadata.json"
REPRO_REPORT = ROOT / "docs" / "prd" / "reproducibility_report.md"
SUBMISSION_CHECKLIST = ROOT / "docs" / "prd" / "PRD_SUBMISSION_CHECKLIST.md"
COVER_LETTER_TEMPLATE = ROOT / "docs" / "prd" / "cover_letter.template.md"
COVER_LETTER_DEFAULT = ROOT / "docs" / "prd" / "cover_letter.md"
PLACEHOLDER_TOKENS = [
    "First Author",
    "Second Author",
    "Example University",
    "Example Academy",
    "example.edu",
    "xxxx.xxxxx",
    "arXiv:xxxx",
]
FORBIDDEN_MANUSCRIPT_TOKENS = [
    "s=-2",
    "spin-minus2",
    "GeneralizedSasakiNakamura",
    "Mathematica",
    "benchmark",
]


@dataclass(frozen=True)
class Finding:
    label: str
    detail: str


def has_real_author_metadata(tex: str) -> list[Finding]:
    findings: list[Finding] = []
    if r"\author{KerrScattering Collaboration}" in tex:
        findings.append(
            Finding(
                "author-placeholder",
                "Replace \\author{KerrScattering Collaboration} with the final author list.",
            )
        )
    if r"\affiliation{KerrScattering Project}" in tex:
        findings.append(
            Finding(
                "affiliation-placeholder",
                "Replace \\affiliation{KerrScattering Project} with final institutional affiliations.",
            )
        )
    if r"\email{" not in tex:
        findings.append(
            Finding(
                "missing-email",
                "Add at least one corresponding-author \\email{...} entry if required by the submission.",
            )
        )
    return findings


def has_final_companion_reference(tex: str) -> list[Finding]:
    if re.search(r"Nonlinear scattering problem in black hole spacetimes,\s*unpublished manuscript", tex):
        return [
            Finding(
                "unpublished-companion-reference",
                "Replace the Schwarzschild companion citation with its final arXiv or journal reference when available.",
            )
        ]
    return []


def has_obvious_placeholders(tex: str) -> list[Finding]:
    findings = []
    for token in ["TODO", "FIXME", "PLACEHOLDER", *PLACEHOLDER_TOKENS]:
        if token in tex:
            findings.append(Finding("placeholder-token", f"Remove placeholder token {token!r}."))
    return findings


def has_forbidden_draft_content(tex: str) -> list[Finding]:
    findings = []
    lowered = tex.lower()
    for token in FORBIDDEN_MANUSCRIPT_TOKENS:
        if token.lower() in lowered:
            findings.append(
                Finding(
                    "off-scope-manuscript-token",
                    f"Remove off-scope token {token!r} from the PRD manuscript.",
                )
            )
    return findings


def has_required_submission_structure(tex: str) -> list[Finding]:
    findings: list[Finding] = []

    class_match = re.search(r"\\documentclass\[([^\]]+)\]\{revtex4-2\}", tex)
    if not class_match:
        findings.append(
            Finding(
                "missing-revtex-prd-class",
                "Use the REVTeX 4.2 document class for the PRD manuscript.",
            )
        )
    else:
        class_options = {option.strip() for option in class_match.group(1).split(",")}
        for required_option in ("aps", "prd", "twocolumn"):
            if required_option not in class_options:
                findings.append(
                    Finding(
                        "missing-revtex-prd-option",
                        f"Add the REVTeX document-class option {required_option!r}.",
                    )
                )

    if r"\section*{Data and code availability}" not in tex:
        findings.append(
            Finding(
                "missing-data-code-availability",
                "Add a Data and code availability section for the manuscript.",
            )
        )

    return findings


def has_pdf() -> list[Finding]:
    findings: list[Finding] = []
    if not PDF.exists():
        findings.append(Finding("missing-pdf", f"Build the PDF at {PDF}."))
    elif PDF.stat().st_size < 100_000:
        findings.append(
            Finding(
                "suspicious-pdf-size",
                f"PDF is unexpectedly small: {PDF.stat().st_size} bytes.",
            )
        )
    elif PDF.stat().st_mtime + 1.0 < TEX.stat().st_mtime:
        findings.append(
            Finding(
                "stale-pdf",
                "Rebuild the PDF; the TeX source is newer than the PDF.",
            )
        )

    if not ROOT_PDF.exists():
        findings.append(Finding("missing-root-pdf", f"Build the root copy at {ROOT_PDF}."))
    elif PDF.exists() and ROOT_PDF.stat().st_size != PDF.stat().st_size:
        findings.append(
            Finding(
                "root-pdf-mismatch",
                "Rebuild with scripts/build_prd_manuscript.py so the root PDF matches docs/prd.",
            )
        )
    return findings


def has_submission_metadata_template() -> list[Finding]:
    if not METADATA_TEMPLATE.exists():
        return [
            Finding(
                "missing-metadata-template",
                f"Add the metadata template at {METADATA_TEMPLATE}.",
            )
        ]
    return []


def placeholder_findings_in_json(data: dict) -> list[str]:
    text = json.dumps(data, ensure_ascii=False)
    return [token for token in PLACEHOLDER_TOKENS if token in text]


def validate_final_metadata(tex: str) -> list[Finding]:
    findings: list[Finding] = []
    if not METADATA_FINAL.exists():
        return [
            Finding(
                "missing-final-metadata",
                "Create docs/prd/submission_metadata.json from the template and fill in final submission details.",
            )
        ]

    try:
        with METADATA_FINAL.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        return [
            Finding(
                "invalid-final-metadata-json",
                f"Fix invalid JSON in {METADATA_FINAL}: {exc}.",
            )
        ]

    placeholders = placeholder_findings_in_json(data)
    for token in placeholders:
        findings.append(
            Finding(
                "final-metadata-placeholder",
                f"Remove placeholder token {token!r} from docs/prd/submission_metadata.json.",
            )
        )

    submission = data.get("submission")
    if not isinstance(submission, dict):
        findings.append(
            Finding(
                "missing-final-submission-object",
                "Add a 'submission' object to docs/prd/submission_metadata.json.",
            )
        )
        submission = {}

    title = submission.get("title")
    if title and rf"\title{{{title}}}" not in tex:
        findings.append(
            Finding(
                "metadata-title-mismatch",
                "Make submission.title match the REVTeX manuscript title.",
            )
        )

    authors = data.get("authors")
    if not isinstance(authors, list) or not authors:
        findings.append(
            Finding(
                "missing-final-authors",
                "Add a non-empty authors list to docs/prd/submission_metadata.json.",
            )
        )
        authors = []

    author_by_name = {}
    for index, author in enumerate(authors, start=1):
        if not isinstance(author, dict):
            findings.append(
                Finding(
                    "invalid-final-author",
                    f"Author entry {index} in docs/prd/submission_metadata.json is not an object.",
                )
            )
            continue
        name = author.get("name")
        if not name:
            findings.append(
                Finding(
                    "missing-final-author-name",
                    f"Author entry {index} is missing a name.",
                )
            )
        else:
            author_by_name[name] = author
        affiliations = author.get("affiliations")
        if not isinstance(affiliations, list) or not affiliations:
            findings.append(
                Finding(
                    "missing-final-author-affiliation",
                    f"Author {name or index!r} is missing at least one affiliation.",
                )
            )

    corresponding = submission.get("corresponding_author")
    if not corresponding:
        findings.append(
            Finding(
                "missing-final-corresponding-author",
                "Set submission.corresponding_author in docs/prd/submission_metadata.json.",
            )
        )
    elif corresponding not in author_by_name:
        findings.append(
            Finding(
                "final-corresponding-author-mismatch",
                "Make submission.corresponding_author match one of the final author names.",
            )
        )
    elif not author_by_name[corresponding].get("email"):
        findings.append(
            Finding(
                "missing-final-corresponding-email",
                f"Add an email for corresponding author {corresponding!r}.",
            )
        )

    reference = data.get("companion_reference")
    if reference is not None:
        if not isinstance(reference, dict):
            findings.append(
                Finding(
                    "invalid-companion-reference",
                    "companion_reference must be an object when supplied.",
                )
            )
            reference = {}
        publication = reference.get("publication_tex", "")
        if "xxxx" in publication or "unpublished manuscript" in publication.lower():
            findings.append(
                Finding(
                    "placeholder-final-companion-reference",
                    "Replace companion_reference.publication_tex with the final arXiv or journal reference.",
                )
            )

    configured_cover = submission.get("cover_letter_output")
    cover_path = Path(configured_cover) if configured_cover else COVER_LETTER_DEFAULT
    if not cover_path.is_absolute():
        cover_path = ROOT / cover_path
    if not cover_path.exists():
        findings.append(
            Finding(
                "missing-final-cover-letter",
                f"Render the final cover letter at {cover_path}.",
            )
        )
    else:
        cover_text = cover_path.read_text(encoding="utf-8", errors="replace")
        if cover_path.stat().st_mtime + 1.0 < METADATA_FINAL.stat().st_mtime:
            findings.append(
                Finding(
                    "stale-final-cover-letter",
                    "Re-render the cover letter after editing docs/prd/submission_metadata.json.",
                )
            )
        if title and title not in cover_text:
            findings.append(
                Finding(
                    "cover-letter-title-mismatch",
                    "Make the final cover letter contain the final manuscript title.",
                )
            )
        if corresponding and corresponding not in cover_text:
            findings.append(
                Finding(
                    "cover-letter-corresponding-author-mismatch",
                    "Make the final cover letter contain the corresponding author name.",
                )
            )

    return findings


def has_submission_support_files() -> list[Finding]:
    findings: list[Finding] = []
    if not REPRO_REPORT.exists():
        findings.append(
            Finding(
                "missing-reproducibility-report",
                f"Run scripts/write_prd_reproducibility_report.py to create {REPRO_REPORT}.",
            )
        )
    if not SUBMISSION_CHECKLIST.exists():
        findings.append(
            Finding(
                "missing-submission-checklist",
                f"Add the PRD submission checklist at {SUBMISSION_CHECKLIST}.",
            )
        )
    if not COVER_LETTER_TEMPLATE.exists():
        findings.append(
            Finding(
                "missing-cover-letter-template",
                f"Add the PRD cover-letter template at {COVER_LETTER_TEMPLATE}.",
            )
        )
    return findings


def main() -> int:
    tex = TEX.read_text(encoding="utf-8")
    findings: list[Finding] = []
    findings.extend(has_required_submission_structure(tex))
    findings.extend(has_real_author_metadata(tex))
    findings.extend(has_final_companion_reference(tex))
    findings.extend(has_obvious_placeholders(tex))
    findings.extend(has_forbidden_draft_content(tex))
    findings.extend(has_pdf())
    findings.extend(has_submission_metadata_template())
    findings.extend(validate_final_metadata(tex))
    findings.extend(has_submission_support_files())

    if findings:
        print("PRD submission readiness audit: NOT READY")
        for finding in findings:
            print(f"- {finding.label}: {finding.detail}")
        return 1

    print("PRD submission readiness audit: READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())
