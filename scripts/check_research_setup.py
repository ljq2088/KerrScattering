"""Audit the project-scoped research-agent and literature setup."""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    required = [
        "AGENTS.md",
        ".codex/config.toml",
        ".agents/skills/gravity-theory-research/SKILL.md",
        "docs/agent/RESEARCH_AGENT_ARCHITECTURE.md",
        "docs/agent/RESEARCH_CAPABILITY_MATRIX.md",
        "docs/literature/gravity_literature_map.md",
        "docs/literature/deep_learning_curriculum.md",
        "docs/literature/deep_learning_curriculum_zh.md",
        "docs/literature/advanced_learning_protocol_zh.md",
        "docs/literature/learning_gates.json",
        "docs/literature/convention_ledger.md",
        "docs/literature/paper_cards.md",
        "docs/literature/seed_arxiv_ids.txt",
        "tools/mcp/gravity_research_server.py",
        "scripts/check_literature_learning_gates.py",
        "scripts/check_prd_style.py",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    if missing:
        fail(f"missing research files: {missing}")

    with (ROOT / ".codex/config.toml").open("rb") as handle:
        config = tomllib.load(handle)
    server = config["mcp_servers"]["gravity_research"]
    configured_cwd = Path(server["cwd"]).resolve()
    if configured_cwd != ROOT.resolve():
        fail(f"MCP cwd mismatch: {configured_cwd} != {ROOT.resolve()}")
    if not (ROOT / server["args"][0]).is_file():
        fail(f"MCP entry point not found: {server['args'][0]}")

    catalog_path = ROOT / "results/literature/arxiv_catalog.json"
    if not catalog_path.is_file():
        fail("arXiv catalog is missing; run build_literature_manifest.py")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    records = catalog.get("records", [])
    unresolved = [record["arxiv_id"] for record in records if not record.get("metadata")]
    if unresolved:
        fail(f"unresolved arXiv records: {unresolved}")

    seed_lines = [
        line for line in (ROOT / "docs/literature/seed_arxiv_ids.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(seed_lines) != len(records):
        fail(f"seed/catalog count mismatch: {len(seed_lines)} != {len(records)}")

    gates = json.loads((ROOT / "docs/literature/learning_gates.json").read_text(encoding="utf-8"))
    gate_ids = {item.get("id") for item in gates.get("modules", [])}
    required_gates = {
        "fixed-background-bhpt",
        "radiation-reaction",
        "singular-regular-self-force",
        "emri-source-lattice",
        "gw-waveform-phase",
        "pn-eft-gravity",
        "nonlinear-ringdown",
        "numerical-methods",
    }
    if not required_gates.issubset(gate_ids):
        fail(f"learning gates missing: {sorted(required_gates - gate_ids)}")

    gate_check = subprocess.run(
        [sys.executable, "scripts/check_literature_learning_gates.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if gate_check.returncode:
        fail(f"literature learning-gate audit failed:\n{gate_check.stdout}\n{gate_check.stderr}")

    check = subprocess.run(
        [sys.executable, "scripts/check_mcp_server.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if check.returncode:
        fail(f"MCP smoke check failed:\n{check.stdout}\n{check.stderr}")

    print("research setup audit passed")
    print(f"repository: {ROOT}")
    print(f"literature records: {len(records)}")
    print("MCP configuration, local documents, catalog, and runtime smoke check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
