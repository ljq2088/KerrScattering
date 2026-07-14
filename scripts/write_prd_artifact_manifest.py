"""Write the frozen artifact manifest for the active PRD manuscript.

Run this after intentionally regenerating one of the figures or CSV files used
by ``docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex``.  The normal build path
checks this manifest and fails if an input artifact drifts unexpectedly.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from check_prd_artifacts import (
    ALL_ARTIFACTS,
    CSV_SCHEMAS,
    FIGURES,
    MANIFEST,
    ROOT,
    png_size,
    relative_path,
    sha256_file,
)


def csv_row_count(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _row in reader)


def artifact_entry(path: Path) -> dict[str, object]:
    entry: dict[str, object] = {
        "path": relative_path(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if path in FIGURES:
        width, height = png_size(path)
        entry["kind"] = "figure"
        entry["width_px"] = width
        entry["height_px"] = height
    elif path in CSV_SCHEMAS:
        entry["kind"] = "csv"
        entry["rows"] = csv_row_count(path)
        entry["required_columns"] = CSV_SCHEMAS[path]
    else:
        entry["kind"] = "unknown"
    return entry


def main() -> None:
    data = {
        "description": (
            "Frozen input artifacts used by "
            "docs/prd/kerr_scalar_nonlinear_GF_baseframe.tex"
        ),
        "root": ROOT.name,
        "artifacts": [artifact_entry(path) for path in ALL_ARTIFACTS],
    }
    MANIFEST.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
