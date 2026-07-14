"""Smoke-test the local gravity research MCP server through its stdio protocol."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> int:
    root = Path(__file__).resolve().parents[1]
    params = StdioServerParameters(
        command="python",
        args=["tools/mcp/gravity_research_server.py"],
        cwd=str(root),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            names = sorted(tool.name for tool in tools)
            expected = {
                "search_arxiv",
                "get_arxiv_paper",
                "zotero_status",
                "search_zotero",
                "export_zotero_bibtex",
                "evaluate_mathematica",
                "research_environment",
            }
            missing = expected.difference(names)
            if missing:
                raise RuntimeError(f"MCP tools missing: {sorted(missing)}")
            result = await session.call_tool("research_environment", {})
            print(f"MCP tools: {', '.join(names)}")
            print(f"environment probe returned {len(result.content)} content blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
