"""Refresh a small, reproducible arXiv metadata catalog for the project."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import arxiv


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SEEDS = ROOT / "docs" / "literature" / "seed_arxiv_ids.txt"
DEFAULT_OUTPUT = ROOT / "results" / "literature" / "arxiv_catalog.json"


def read_seeds(path: Path) -> list[dict[str, str]]:
    seeds = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split("|", maxsplit=3)
        if len(fields) != 4:
            raise ValueError(f"Malformed seed line: {raw}")
        arxiv_id, module, priority, reason = fields
        seeds.append(
            {
                "arxiv_id": arxiv_id.strip(),
                "module": module.strip(),
                "priority": priority.strip(),
                "reason": reason.strip(),
            }
        )
    return seeds


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    seeds = read_seeds(args.seeds)
    ids = [item["arxiv_id"] for item in seeds]
    search = arxiv.Search(id_list=ids, max_results=len(ids))
    client = arxiv.Client(page_size=len(ids), delay_seconds=3.0, num_retries=2)
    records_by_id = {}
    for result in client.results(search):
        records_by_id[result.get_short_id().split("v", 1)[0]] = {
            "arxiv_id": result.get_short_id(),
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "published": result.published.isoformat() if result.published else None,
            "updated": result.updated.isoformat() if result.updated else None,
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "primary_category": result.primary_category,
            "categories": result.categories,
        }

    records = []
    for seed in seeds:
        base_id = seed["arxiv_id"].split("v", 1)[0]
        records.append({**seed, "metadata": records_by_id.get(base_id)})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "arXiv API metadata; PDFs are not downloaded",
        "count": len(records),
        "records": records,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    found = sum(item["metadata"] is not None for item in records)
    print(f"wrote {args.output} ({found}/{len(records)} records resolved)")
    return 0 if found == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
