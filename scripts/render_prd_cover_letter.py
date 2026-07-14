"""Render the PRD cover letter from submission metadata.

Usage:
    python scripts/render_prd_cover_letter.py docs/prd/submission_metadata.json

The script reads the same metadata file used by
``apply_prd_submission_metadata.py`` and writes to
``submission.cover_letter_output`` when that field is present, otherwise to
``docs/prd/cover_letter.md``.  It rejects template placeholder values unless
``--allow-placeholders`` is passed for dry-run testing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "prd" / "cover_letter.md"

PLACEHOLDER_TOKENS = [
    "First Author",
    "Second Author",
    "Example University",
    "Example Academy",
    "example.edu",
    "City, Country",
    "xxxx.xxxxx",
]


def placeholder_findings(data: dict) -> list[str]:
    text = json.dumps(data, ensure_ascii=False)
    return [token for token in PLACEHOLDER_TOKENS if token in text]


def load_metadata(path: Path, *, allow_placeholders: bool) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    authors = data.get("authors")
    if not isinstance(authors, list) or not authors:
        raise ValueError("metadata must contain a non-empty 'authors' list")

    submission = data.get("submission")
    if not isinstance(submission, dict):
        raise ValueError("metadata must contain a 'submission' object")

    placeholders = placeholder_findings(data)
    if placeholders and not allow_placeholders:
        joined = ", ".join(repr(token) for token in placeholders)
        raise ValueError(
            "metadata still contains template placeholders: "
            f"{joined}. Pass --allow-placeholders only for dry-run testing."
        )
    return data


def corresponding_author(data: dict) -> dict:
    requested = data["submission"].get("corresponding_author")
    if not requested:
        raise ValueError("submission.corresponding_author is required")
    for author in data["authors"]:
        if author.get("name") == requested:
            if not author.get("email"):
                raise ValueError(
                    f"corresponding author {requested!r} must have an email"
                )
            return author
    raise ValueError(
        "submission.corresponding_author does not match any author name: "
        f"{requested!r}"
    )


def first_affiliation(author: dict) -> str:
    affiliations = author.get("affiliations")
    if not isinstance(affiliations, list) or not affiliations:
        raise ValueError(f"author {author.get('name')!r} has no affiliation")
    return affiliations[0]


def render_cover_letter(data: dict) -> str:
    submission = data["submission"]
    corr = corresponding_author(data)
    title = submission.get("title") or "Nonlinear scalar scattering problem in Kerr spacetime"
    journal = submission.get("journal") or "Physical Review D"
    manuscript_type = submission.get("manuscript_type") or "Regular Article"

    return f"""Dear Editors of {journal},

We submit the manuscript

> {title}

for consideration as a {manuscript_type} in {journal}.

The manuscript formulates and computes a weakly nonlinear scattering problem
for a self-interacting complex scalar field on Kerr spacetime. It extends the
flux-based nonlinear Green-function construction used in the Schwarzschild
case to the scalar Teukolsky equation with spin weight s=0. The Kerr extension
keeps the physical definition of transmission and reflection coefficients
fixed while incorporating the co-rotating horizon frequency, scalar spheroidal
harmonics, and the Sigma-weighted nonlinear source.

The numerical results focus on the axisymmetric Kerr sample a=0.5, m=0, and
l=0,1,2. The data show Breit-Wigner-type peaks in the first-order nonlinear
transmission coefficients, peak locations close to the real parts of the
corresponding scalar Kerr quasinormal modes, and high-frequency exponential
tails with finite-window effective temperatures close to the Kerr Hawking
temperature. The numerical accuracy is assessed internally by Chebyshev
coefficient tails, direct residuals of the radial Teukolsky equation, and the
linear and first-order flux balance laws.

The work should be of interest to readers studying black-hole scattering, Kerr
perturbation theory, nonlinear response functions, and frequency-domain
methods for black-hole physics.

The manuscript includes a Data and code availability statement. The numerical
CSV data, plotting scripts, frozen artifact manifest, and local reproducibility
report are included in the accompanying project package.

This manuscript is original, has not been published elsewhere, and is not under
consideration by another journal.

Sincerely,

{corr["name"]}
{first_affiliation(corr)}
{corr["email"]}
"""


def cover_letter_output(data: dict, override: Path | None) -> Path:
    if override is not None:
        output = override
    else:
        configured = data["submission"].get("cover_letter_output")
        output = Path(configured) if configured else DEFAULT_OUTPUT
    if not output.is_absolute():
        output = ROOT / output
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata_json", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output cover-letter path. Defaults to submission.cover_letter_output "
            "or docs/prd/cover_letter.md."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate metadata and print the cover letter without writing it.",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Allow template placeholder values. Use only for dry-run testing.",
    )
    args = parser.parse_args()

    data = load_metadata(args.metadata_json, allow_placeholders=args.allow_placeholders)
    text = render_cover_letter(data)
    if args.dry_run:
        print(text)
        return

    output = cover_letter_output(data, args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
