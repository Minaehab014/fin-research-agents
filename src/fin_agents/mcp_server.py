"""
MCP server — exposes the research pipeline as tools for Claude Desktop
or any other MCP client.

Add to Claude Desktop config (~/.claude/claude_desktop_config.json):
{
  "mcpServers": {
    "fin-research": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "fin_agents.mcp_server"],
      "env": {
        "GROQ_API_KEY": "...",
        "GOOGLE_API_KEY": "...",
        "NEWSAPI_KEY": "...",
        "SEC_USER_AGENT": "..."
      }
    }
  }
}

Run standalone for testing:
    python -m fin_agents.mcp_server
"""
import asyncio
from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP
from fin_agents.agents.graph import build_graph
from fin_agents.rag.ingest import ingest_ticker, delete_ticker

mcp = FastMCP(
    name="fin-research",
    instructions=(
        "Financial research assistant. Use research_company to get a full "
        "analyst-style report on any publicly traded company. "
        "Use ingest_company to pre-load SEC filing data for better filings insights."
    ),
)

_graph = None


def _get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


@mcp.tool
async def research_company(query: str) -> str:
    """Run a full multi-agent research report for any company or stock query.

    Args:
        query: Natural language question e.g. 'Analyze Nvidia's AI outlook'
               or 'Is Tesla a good buy right now?'

    Returns:
        A structured markdown research brief covering financials, news,
        SEC filing insights, risks, and analyst takeaway.
    """
    graph = _get_graph()
    state = await graph.ainvoke({
        "query": query,
        "ticker": "",
        "fundamentals": None,
        "news": None,
        "news_summary": None,
        "rag_chunks": None,
        "final_report": None,
    })
    return state.get("final_report", "No report generated.")


@mcp.tool
async def ingest_company(ticker: str, refresh: bool = False) -> str:
    """Ingest the latest SEC 10-K/10-Q filing for a company into the vector store.

    Only needed once per ticker. Use refresh=True after a new quarterly filing
    to replace stale data.

    Args:
        ticker: Stock ticker symbol e.g. 'NVDA', 'AAPL', 'TSLA'
        refresh: If True, deletes existing chunks before re-ingesting.

    Returns:
        Confirmation message with chunk count.
    """
    ticker = ticker.upper()
    if refresh:
        deleted = delete_ticker(ticker)
        if deleted:
            note = f"Cleared {deleted} old chunks. "
        else:
            note = ""
    else:
        note = ""

    n = ingest_ticker(ticker)
    return f"{note}Ingested {n} chunks for {ticker}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
