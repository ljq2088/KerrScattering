"""Validate the reproducible literature seed list and metadata catalog."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "docs" / "literature" / "seed_arxiv_ids.txt"
CATALOG = ROOT / "results" / "literature" / "arxiv_catalog.json"
CARDS = ROOT / "docs" / "literature" / "paper_cards.md"
GRAPH = ROOT / "docs" / "literature" / "research_knowledge_graph.md"


def seed_ids() -> list[str]:
    ids = []
    for raw in SEEDS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            fields = line.split("|", maxsplit=3)
            if len(fields) != 4:
                raise AssertionError(f"malformed seed line: {raw}")
            ids.append(fields[0].split("v", 1)[0])
    return ids


def main() -> int:
    ids = seed_ids()
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate arXiv identifiers in seed list")
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    catalog_ids = [item["arxiv_id"].split("v", 1)[0] for item in records]
    if catalog_ids != ids:
        raise AssertionError("catalog order or identifiers do not match seed list")
    unresolved = [item["arxiv_id"] for item in records if item.get("metadata") is None]
    if unresolved:
        raise AssertionError(f"unresolved metadata: {', '.join(unresolved)}")
    if payload.get("count") != len(ids):
        raise AssertionError("catalog count does not match seed list")
    cards = CARDS.read_text(encoding="utf-8")
    graph = GRAPH.read_text(encoding="utf-8")
    required_cards = {
        "gr-qc/0202090": "Kerr geodesic frequencies",
        "0906.1420": "Analytic Kerr geodesics",
        "0904.3810": "Teukolsky waveforms",
        "1103.0287": "Scalar self-force",
        "1711.09607": "Gravitational self-force",
        "2209.05450": "Generic-Kerr regularization",
        "1409.4419": "Frequency-domain self-force workflow",
        "2504.09640": "Recent second-order self-force",
        "2403.20311": "Kerr metric reconstruction",
        "2604.06053": "EMRI tests of Kerr symmetry",
        "2410.17310": "Relativistic EMRI waveforms",
        "2507.06923": "Post-adiabatic EMRI waveforms",
        "2606.04998": "Numerical-relativity methods for self-force",
        "gr-qc/9712056": "Mino--Sasaki--Tanaka radiation reaction",
        "gr-qc/0202086": "Detweiler--Whiting singular/regular split",
        "gr-qc/9912010": "Barack--Ori mode-sum regularization",
        "1807.01699": "Post-Newtonian gravity as an effective field theory",
    }
    for arxiv_id, label in required_cards.items():
        if arxiv_id not in cards or label not in cards:
            raise AssertionError(f"missing deep-reading card: {label} ({arxiv_id})")
    for token in ("geodesic orbit", "source harmonics", "regularization", "phase"):
        if token not in graph:
            raise AssertionError(f"knowledge graph is missing required concept: {token}")
    print(f"literature catalog check passed ({len(ids)} resolved records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
