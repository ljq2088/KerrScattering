"""Check citation keys in the active PRD manuscript."""

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
    print(
        f"PRD citation integrity passed ({len(cited)} cited keys, "
        f"{len(defined_set)} bibliography entries)"
    )
    if unused:
        print(f"unused bibliography entries: {', '.join(unused)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
