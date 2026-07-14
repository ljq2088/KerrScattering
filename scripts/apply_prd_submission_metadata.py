"""Apply final author metadata and optional references to the PRD draft.

Usage:
    python scripts/apply_prd_submission_metadata.py docs/prd/submission_metadata.json

The input JSON follows ``docs/prd/submission_metadata.template.json``.  The
script edits the REVTeX front matter and, when provided, a companion bibitem.
The companion reference is optional because the active manuscript does not
cite an unpublished local companion.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.tex"


FRONT_MATTER_RE = re.compile(
    r"(\\title\{Weakly nonlinear scalar scattering from a Kerr black hole\}\n\n)"
    r".*?"
    r"(\n\\maketitle)",
    re.DOTALL,
)

COMPANION_RE = re.compile(
    r"(\\bibitem\{HeTianZhang2026\}\n)"
    r".*?"
    r"(?=\n\\bibitem\{StarobinskyChurilov\})",
    re.DOTALL,
)

PLACEHOLDER_TOKENS = [
    "First Author",
    "Second Author",
    "Example University",
    "Example Academy",
    "example.edu",
    "City, Country",
    "xxxx.xxxxx",
]


def latex_escape_text(value: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    return "".join(replacements.get(char, char) for char in value)


def metadata_placeholder_findings(data: dict) -> list[str]:
    text = json.dumps(data, ensure_ascii=False)
    return [token for token in PLACEHOLDER_TOKENS if token in text]


def load_metadata(path: Path, *, allow_placeholders: bool = False) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    submission = data.get("submission")
    if not isinstance(submission, dict):
        raise ValueError("metadata must contain a 'submission' object")

    authors = data.get("authors")
    if not isinstance(authors, list) or not authors:
        raise ValueError("metadata must contain a non-empty 'authors' list")

    author_by_name = {}
    for index, author in enumerate(authors, start=1):
        if not author.get("name"):
            raise ValueError(f"author {index} is missing 'name'")
        author_by_name[author["name"]] = author
        affiliations = author.get("affiliations")
        if not isinstance(affiliations, list) or not affiliations:
            raise ValueError(f"author {index} is missing at least one affiliation")

    corresponding = submission.get("corresponding_author")
    if not corresponding:
        raise ValueError("submission.corresponding_author is required")
    if corresponding not in author_by_name:
        raise ValueError(
            "submission.corresponding_author does not match any author name: "
            f"{corresponding!r}"
        )
    if not author_by_name[corresponding].get("email"):
        raise ValueError(f"corresponding author {corresponding!r} must have an email")

    reference = data.get("companion_reference")
    if reference is not None:
        if not isinstance(reference, dict):
            raise ValueError("companion_reference must be an object when supplied")
        for key in ("authors_tex", "title", "publication_tex"):
            if not reference.get(key):
                raise ValueError(f"companion_reference is missing required key {key!r}")

    placeholders = metadata_placeholder_findings(data)
    if placeholders and not allow_placeholders:
        joined = ", ".join(repr(token) for token in placeholders)
        raise ValueError(
            "metadata still contains template placeholders: "
            f"{joined}. Pass --allow-placeholders only for dry-run testing."
        )
    return data


def render_front_matter(data: dict) -> str:
    lines: list[str] = []
    for author in data["authors"]:
        lines.append(rf"\author{{{latex_escape_text(author['name'])}}}")
        email = author.get("email")
        if email:
            lines.append(rf"\email{{{latex_escape_text(email)}}}")
        for affiliation in author["affiliations"]:
            lines.append(rf"\affiliation{{{latex_escape_text(affiliation)}}}")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_companion_reference(data: dict) -> str | None:
    reference = data.get("companion_reference")
    if not reference:
        return None
    required = ["authors_tex", "title", "publication_tex"]
    missing = [key for key in required if not reference.get(key)]
    if missing:
        raise ValueError(
            "companion_reference is missing required keys: " + ", ".join(missing)
        )
    return (
        r"\bibitem{HeTianZhang2026}" "\n"
        f"{reference['authors_tex']},\n"
        f"{latex_escape_text(reference['title'])},\n"
        f"{reference['publication_tex']}\n"
    )


def apply_metadata(tex: str, data: dict) -> str:
    front_matter = render_front_matter(data)
    tex, count = FRONT_MATTER_RE.subn(
        lambda match: match.group(1) + front_matter + match.group(2),
        tex,
        count=1,
    )
    if count != 1:
        raise RuntimeError("could not locate manuscript front matter")

    companion = render_companion_reference(data)
    if companion is not None:
        tex, count = COMPANION_RE.subn(lambda _match: companion, tex, count=1)
        if count != 1:
            raise RuntimeError("could not locate HeTianZhang2026 bibitem")
    return tex


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata_json", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print the updated TeX without writing it.",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Allow template placeholder values. Use only for dry-run testing.",
    )
    args = parser.parse_args()

    data = load_metadata(args.metadata_json, allow_placeholders=args.allow_placeholders)
    tex = TEX.read_text(encoding="utf-8")
    updated = apply_metadata(tex, data)
    if args.dry_run:
        print(updated)
        return
    TEX.write_text(updated, encoding="utf-8", newline="\n")
    print(f"Updated {TEX}")


if __name__ == "__main__":
    main()
