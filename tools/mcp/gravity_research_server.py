"""Local research MCP server for arXiv, Zotero, and Mathematica.

The server is intentionally read-only except for evaluating an explicitly
provided Mathematica expression. It is a local bridge for this project, not
an official arXiv, Zotero, or Wolfram integration.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import arxiv
from mcp.server.fastmcp import FastMCP


MCP_INSTRUCTIONS = """Local research tools for the KerrScattering project.
Use arXiv and Zotero tools for read-only literature metadata and bibliography
work. Use the local literature-card tools to recover project-specific transfer
notes and learning-gate tools to plan derivations and validation, but treat the primary paper as authoritative. Use Mathematica only for
an explicitly requested finite evaluation; do not use it to edit files or
execute unrelated system commands. Return exact paths, identifiers, errors,
and timeouts. Literature claims still require a primary-source check and
should not be inferred from metadata alone."""

mcp = FastMCP("gravity-research", instructions=MCP_INSTRUCTIONS)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _seed_records() -> list[dict[str, str]]:
    path = _project_root() / "docs/literature/seed_arxiv_ids.txt"
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        arxiv_id, module, priority, reason = line.split("|", 3)
        records.append(
            {
                "arxiv_id": arxiv_id,
                "module": module,
                "priority": priority,
                "reason": reason,
            }
        )
    return records


@mcp.tool()
def list_literature_modules(priority: str | None = None) -> str:
    """List the maintained project literature modules and their priorities."""

    records = _seed_records()
    if priority:
        records = [record for record in records if record["priority"].upper() == priority.upper()]
    return _json({"ok": True, "count": len(records), "records": records})


@mcp.tool()
def get_literature_card(module: str) -> str:
    """Return a local paper card and seed metadata for one literature module."""

    module = module.strip()
    records = [record for record in _seed_records() if record["module"] == module]
    if not records:
        return _json({"ok": False, "module": module, "error": "module_not_found"})
    record = records[0]
    base_id = record["arxiv_id"].split("v", 1)[0]
    cards_text = (_project_root() / "docs/literature/paper_cards.md").read_text(encoding="utf-8")
    card = None
    for section in cards_text.split("\n## ")[1:]:
        if base_id in section:
            card = "## " + section.strip()
            break
    return _json({"ok": True, "module": module, "seed": record, "card": card})


@mcp.tool()
def get_learning_gate(module_id: str | None = None) -> str:
    """Return machine-checkable derivation and validation gates."""

    path = _project_root() / "docs/literature/learning_gates.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    modules = payload.get("modules", [])
    if module_id:
        modules = [item for item in modules if item.get("id") == module_id.strip()]
        if not modules:
            return _json({"ok": False, "module_id": module_id, "error": "gate_not_found"})
    return _json({"ok": True, "count": len(modules), "modules": modules})


@mcp.tool()
def search_arxiv(query: str, max_results: int = 10, sort_by: str = "relevance") -> str:
    """Search arXiv metadata and abstracts without downloading papers."""

    max_results = max(1, min(int(max_results), 50))
    sort_map = {
        "relevance": arxiv.SortCriterion.Relevance,
        "submitted": arxiv.SortCriterion.SubmittedDate,
        "updated": arxiv.SortCriterion.LastUpdatedDate,
    }
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=sort_map.get(sort_by.lower(), arxiv.SortCriterion.Relevance),
    )
    client = arxiv.Client(page_size=max_results, delay_seconds=3.0, num_retries=2)
    records = []
    try:
        for result in client.results(search):
            records.append(
                {
                    "arxiv_id": result.get_short_id(),
                    "title": result.title,
                    "authors": [a.name for a in result.authors],
                    "published": result.published.isoformat() if result.published else None,
                    "updated": result.updated.isoformat() if result.updated else None,
                    "summary": result.summary,
                    "pdf_url": result.pdf_url,
                    "primary_category": result.primary_category,
                    "categories": result.categories,
                }
            )
    except Exception as exc:
        return _json({"ok": False, "query": query, "error": repr(exc), "records": records})
    return _json({"ok": True, "query": query, "count": len(records), "records": records})


@mcp.tool()
def get_arxiv_paper(arxiv_id: str) -> str:
    """Fetch metadata and abstract for one arXiv identifier."""

    search = arxiv.Search(id_list=[arxiv_id.strip()], max_results=1)
    client = arxiv.Client(page_size=1, delay_seconds=3.0, num_retries=2)
    try:
        result = next(client.results(search))
    except StopIteration:
        return _json({"ok": False, "arxiv_id": arxiv_id, "error": "not found"})
    except Exception as exc:
        return _json({"ok": False, "arxiv_id": arxiv_id, "error": repr(exc)})
    return _json(
        {
            "ok": True,
            "arxiv_id": result.get_short_id(),
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "published": result.published.isoformat() if result.published else None,
            "updated": result.updated.isoformat() if result.updated else None,
            "summary": result.summary,
            "pdf_url": result.pdf_url,
            "primary_category": result.primary_category,
            "categories": result.categories,
        }
    )


def _zotero_get(path: str, params: dict[str, str] | None = None) -> tuple[int, Any]:
    base = os.environ.get("ZOTERO_LOCAL_API", "http://127.0.0.1:23119/api")
    url = base.rstrip("/") + "/" + path.lstrip("/")
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(payload)
            except json.JSONDecodeError:
                return response.status, payload
    except Exception as exc:
        return 0, {"error": repr(exc), "url": url}


@mcp.tool()
def zotero_status() -> str:
    """Check whether the local Zotero read API is reachable."""

    status, payload = _zotero_get("")
    summary = {
        "payload_type": type(payload).__name__,
        "payload_keys": sorted(payload.keys()) if isinstance(payload, dict) else None,
    }
    return _json({"ok": status == 200, "http_status": status, "summary": summary})


@mcp.tool()
def search_zotero(query: str, limit: int = 20) -> str:
    """Search the local Zotero library and return item metadata."""

    limit = max(1, min(int(limit), 100))
    status, payload = _zotero_get("users/0/items", {"q": query, "limit": str(limit)})
    if status != 200 or not isinstance(payload, list):
        return _json({"ok": False, "http_status": status, "payload": payload})
    records = []
    for item in payload:
        data = item.get("data", {}) if isinstance(item, dict) else {}
        records.append(
            {
                "key": item.get("key"),
                "item_type": data.get("itemType"),
                "title": data.get("title"),
                "creators": data.get("creators", []),
                "date": data.get("date"),
                "DOI": data.get("DOI"),
                "url": data.get("url"),
                "citation_key": data.get("citationKey"),
            }
        )
    return _json({"ok": True, "query": query, "count": len(records), "records": records})


@mcp.tool()
def export_zotero_bibtex(item_key: str | None = None) -> str:
    """Return BibTeX from the local Zotero library without writing a file."""

    path = "users/0/items"
    if item_key:
        path += "/" + urllib.parse.quote(item_key, safe="")
    status, payload = _zotero_get(path, {"format": "bibtex"})
    return _json({"ok": status == 200, "http_status": status, "item_key": item_key, "bibtex": payload})


@mcp.tool()
def evaluate_mathematica(code: str, timeout_sec: int = 60, kernel_path: str | None = None) -> str:
    """Evaluate an explicitly supplied Wolfram Language expression locally."""

    timeout_sec = max(1, min(int(timeout_sec), 300))
    configured = kernel_path or os.environ.get("WOLFRAM_SCRIPT") or r"F:\mma\wolframscript.exe"
    executable = Path(configured)
    if not executable.exists():
        return _json({"ok": False, "error": "kernel_not_found", "kernel_path": str(executable)})
    try:
        completed = subprocess.run(
            [str(executable), "-code", code],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _json(
            {
                "ok": False,
                "error": "timeout",
                "timeout_sec": timeout_sec,
                "kernel_path": str(executable),
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
            }
        )
    except Exception as exc:
        return _json({"ok": False, "error": repr(exc), "kernel_path": str(executable)})
    return _json(
        {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "kernel_path": str(executable),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    )


@mcp.tool()
def research_environment() -> str:
    """Report configured research-tool paths without executing them."""

    candidates = {
        "matlab": os.environ.get("MATLAB_EXE", r"F:\matlab\2026a\bin\matlab.exe"),
        "wolfram_script": os.environ.get("WOLFRAM_SCRIPT", r"F:\mma\wolframscript.exe"),
        "wolfram_kernel": os.environ.get("WOLFRAM_KERNEL", r"F:\mma\MathKernel.exe"),
        "zotero_api": os.environ.get("ZOTERO_LOCAL_API", "http://127.0.0.1:23119/api"),
        "wsl": os.environ.get("WSL_EXE", "wsl.exe"),
    }
    result = {}
    for name, value in candidates.items():
        if value.startswith("http://") or value.startswith("https://"):
            result[name] = {"value": value, "exists": None}
        else:
            result[name] = {"value": value, "exists": Path(value).exists()}
    return _json(result)


if __name__ == "__main__":
    mcp.run(transport="stdio")
