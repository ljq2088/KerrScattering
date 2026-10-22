"""Check citation keys and audited recent metadata in the active PRD manuscript."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "docs" / "prd" / "kerr_scalar_nonlinear_GF_baseframe.tex"


def main() -> int:
    text = TEX.read_text(encoding="utf-8")
    cited: set[str] = set()
    for match in re.finditer(r"\\cite\w*\{([^}]*)\}", text, flags=re.DOTALL):
        cited.update(key.strip() for key in match.group(1).split(",") if key.strip())

    defined = re.findall(r"\\bibitem\{([^}]+)\}", text)
    defined_set = set(defined)
    duplicate_keys = sorted(key for key in defined_set if defined.count(key) > 1)
    missing = sorted(cited - defined_set)

    if duplicate_keys:
        raise AssertionError(f"duplicate bibliography keys: {', '.join(duplicate_keys)}")
    if missing:
        raise AssertionError(f"cited keys without bibitems: {', '.join(missing)}")

    unused = sorted(defined_set - cited)

    blocks = {
        match.group(1): match.group(2)
        for match in re.finditer(
            r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})",
            text,
            flags=re.DOTALL,
        )
    }
    audited_metadata = {
        "Wei2025": (
            r"Phys. Rev. D \textbf{112}, 064048 (2025)",
            "doi:10.1103/42fh-sw5h",
            "arXiv:2504.09640",
        ),
        "ZhangEffectiveSource2025": (
            r"Phys. Rev. D \textbf{112}, 104069 (2025)",
            "doi:10.1103/z9jr-qxc7",
            "arXiv:2505.19732",
        ),
        "UptonWardell2026": (
            r"Phys. Rev. D \textbf{113}, 064013 (2026)",
            "doi:10.1103/f9j2-k64r",
            "arXiv:2508.00087",
        ),
        "Berens2024": (
            r"Class. Quantum Grav. \textbf{41}, 195004 (2024)",
            "doi:10.1088/1361-6382/ad6c9c",
            "arXiv:2403.20311",
        ),
        "Lo2023": (
            r"Phys. Rev. D \textbf{110}, 124070 (2024)",
            "arXiv:2306.16469",
        ),
        "Cardoso2026": ("arXiv:2603.04501",),
        "XieHuang2025": (
            r"Phys. Rev. D \textbf{112}, 055028 (2025)",
            "doi:10.1103/xmhn-cpv4",
            "arXiv:2503.10347",
        ),
        "Iuliano2025": (
            r"Phys. Rev. D \textbf{111}, 124038 (2025)",
            "doi:10.1103/PhysRevD.111.124038",
            "arXiv:2412.02821",
        ),
    }
    metadata_failures: list[str] = []
    for key, fragments in audited_metadata.items():
        block = blocks.get(key, "")
        missing_fragments = [fragment for fragment in fragments if fragment not in block]
        if missing_fragments:
            metadata_failures.append(f"{key}: {', '.join(missing_fragments)}")
    if metadata_failures:
        raise AssertionError(
            "audited bibliography metadata missing or stale: "
            + "; ".join(metadata_failures)
        )

    print(
        f"PRD citation integrity passed ({len(cited)} cited keys, "
        f"{len(defined_set)} bibliography entries; "
        f"{len(audited_metadata)} recent records audited)"
    )
    if unused:
        print(f"unused bibliography entries: {', '.join(unused)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
