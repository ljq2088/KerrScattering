"""Audit the depth and evidence structure of the gravity literature curriculum."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "docs/literature/learning_gates.json"
CARDS = ROOT / "docs/literature/paper_cards.md"
REPORT = ROOT / "docs/literature/deep_learning_report_2026-07-14.md"
PROTOCOL = ROOT / "docs/literature/advanced_learning_protocol_zh.md"
EMRI_PROTOCOL = ROOT / "docs/literature/EMRI_TRANSFER_PROTOCOL_ZH.md"

REQUIRED_FIELDS = (
    "prerequisites",
    "equations",
    "implementation_targets",
    "acceptance_tests",
)


def main() -> int:
    payload = json.loads(GATES.read_text(encoding="utf-8"))
    modules = payload.get("modules", [])
    if payload.get("version", 0) < 1 or len(modules) < 8:
        raise AssertionError("the curriculum must expose all eight research modules")

    ids = [module.get("id") for module in modules]
    if any(not module_id for module_id in ids) or len(ids) != len(set(ids)):
        raise AssertionError("learning-gate ids must be present and unique")

    for module in modules:
        for field in REQUIRED_FIELDS:
            values = module.get(field)
            if not isinstance(values, list) or not values:
                raise AssertionError(f"{module.get('id')}: missing non-empty {field}")
        if len(module["acceptance_tests"]) < 3:
            raise AssertionError(f"{module.get('id')}: too few independent acceptance tests")

    cards = CARDS.read_text(encoding="utf-8").lower().replace("-", " ")
    report = REPORT.read_text(encoding="utf-8").lower().replace("-", " ")
    protocol = PROTOCOL.read_text(encoding="utf-8").lower().replace("-", " ")
    emri_protocol = EMRI_PROTOCOL.read_text(encoding="utf-8").lower().replace("-", " ")
    required_concepts = (
        "emri",
        "self force",
        "gravitational wave",
        "kerr",
        "regularization",
        "flux",
        "phase",
    )
    for concept in required_concepts:
        if concept not in cards + report + protocol + emri_protocol:
            raise AssertionError(f"literature curriculum is missing concept: {concept}")

    if not any(module.get("id") == "emri-waveform-transfer" for module in modules):
        raise AssertionError("EMRI waveform transfer gate is missing")
    emri_concepts = {
        "mino": ("mino",),
        "wronskian": ("wronskian",),
        "phase": ("phase", "相位"),
        "self force": ("self force", "self-force", "自力"),
    }
    for concept, aliases in emri_concepts.items():
        if not any(alias in emri_protocol for alias in aliases):
            raise AssertionError(f"EMRI transfer protocol is missing concept: {concept}")
    if "omega" not in emri_protocol or "mkn" not in emri_protocol:
        raise AssertionError("EMRI transfer protocol is missing the omega_mkn mode-frequency relation")

    print(
        "literature learning-gate audit passed "
        f"({len(modules)} modules, "
        f"{sum(len(module['acceptance_tests']) for module in modules)} acceptance tests)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
