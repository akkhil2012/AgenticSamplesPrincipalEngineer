"""Real MCP server: initialization, tools/list and tools/call over stdio."""

from catalog import ROOT, quote_cost, search_quotes
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(ROOT / ".env")
mcp = FastMCP("Supplier quote workspace")
mcp.tool()(search_quotes)
mcp.tool()(quote_cost)

if __name__ == "__main__":
    mcp.run(transport="stdio")
