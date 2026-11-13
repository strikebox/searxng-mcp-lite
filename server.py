"""Минимальный MCP-сервер: web_search через локальный SearXNG.

Только официальный MCP Python SDK (modelcontextprotocol, v2.x) + httpx.
"""
import argparse
import json
import os

import httpx
import uvicorn
from mcp.server import Server
from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool

SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://127.0.0.1:8080").rstrip("/")

WEB_SEARCH_TOOL = Tool(
    name="web_search",
    description=(
        "Perform a privacy-respecting web search via the local SearXNG "
        "metasearch instance."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"},
            "categories": {
                "type": "string",
                "description": (
                    "Comma-separated SearXNG categories: general, news, "
                    "science, files, images, videos, it, social_media"
                ),
            },
            "language": {"type": "string", "description": "Language code, e.g. en-US, ru-RU"},
            "pageno": {"type": "integer", "description": "Page number (1-based)"},
        },
        "required": ["query"],
    },
)


async def on_list_tools(ctx, params) -> ListToolsResult:
    return ListToolsResult(tools=[WEB_SEARCH_TOOL])


async def on_call_tool(ctx, params) -> CallToolResult:
    if params.name != "web_search":
        raise ValueError(f"Unknown tool: {params.name}")
    args = params.arguments or {}

    request_params = {
        "q": args.get("query", ""),
        "format": "json",
        "language": args.get("language", "en-US"),
        "pageno": str(args.get("pageno", 1)),
    }
    if args.get("categories"):
        request_params["categories"] = args["categories"]

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{SEARXNG_URL}/search", params=request_params)
        resp.raise_for_status()
        data = resp.json()

    results = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
            "engine": r.get("engine", ""),
        }
        for r in data.get("results", [])
    ]
    payload = {
        "query": args.get("query", ""),
        "number_of_results": len(results),
        "results": results,
    }
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
    )


def build_app():
    """Build the Streamable HTTP Starlette app."""
    server = Server(
        "searxng-web-search",
        instructions="Web search through the local SearXNG metasearch instance.",
        on_list_tools=on_list_tools,
        on_call_tool=on_call_tool,
    )
    return server.streamable_http_app(host="0.0.0.0", stateless_http=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal MCP server: web_search via a local SearXNG instance."
    )
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "0.0.0.0"))
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("MCP_PORT", "8765"))
    )
    args = parser.parse_args()
    uvicorn.run(build_app(), host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
