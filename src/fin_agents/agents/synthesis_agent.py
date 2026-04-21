from rich.console import Console
from langchain_core.messages import HumanMessage
from fin_agents.agents.state import ResearchState
from fin_agents.config import groq_llm

console = Console()
_llm = groq_llm()

_PROMPT = """\
You are a senior equity research analyst. Produce a structured markdown research brief\
 based solely on the data provided below.

## Input Data

### Fundamentals
{fundamentals_block}

### Recent News
{news_block}

### SEC Filing Excerpts
{rag_block}

---

Write the brief using EXACTLY these sections (use ## headers):

## Executive Summary
## Key Financials
## Recent News
## Filings Insights
## Risks
## Analyst Takeaway

Be specific, cite numbers where available, and keep each section concise."""


def _fmt_fundamentals(state: ResearchState) -> str:
    f = state.get("fundamentals")
    if not f:
        return "No fundamentals data."
    lines = [
        f"Company: {f.name} ({f.ticker})",
        f"Sector: {f.sector}",
        f"Market Cap: ${f.market_cap:,.0f}" if f.market_cap else "Market Cap: N/A",
        f"P/E: {f.pe_ratio}  |  EPS: {f.eps}",
        f"Revenue TTM: ${f.revenue_ttm:,.0f}" if f.revenue_ttm else "Revenue TTM: N/A",
        "",
        f.commentary or "",
    ]
    return "\n".join(lines)


def _fmt_news(state: ResearchState) -> str:
    items = state.get("news") or []
    summary = state.get("news_summary") or ""
    if not items:
        return "No recent news."
    lines = [f"Overall theme: {summary}", ""]
    for item in items:
        lines.append(
            f"- [{item.sentiment or 'neutral'}] {item.title} ({item.source}, {item.published_at.date()})"
        )
    return "\n".join(lines)


def _fmt_rag(state: ResearchState) -> str:
    chunks = state.get("rag_chunks") or []
    if not chunks:
        return "No filing excerpts retrieved."
    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(f"[{i}] {c['text'][:400].strip()}")
        lines.append("")
    return "\n".join(lines)


async def run_synthesis(state: ResearchState) -> dict:
    ticker = state["ticker"]
    console.print(f"[bold yellow]⟳ synthesis_agent[/bold yellow]  {ticker}")

    prompt = _PROMPT.format(
        fundamentals_block=_fmt_fundamentals(state),
        news_block=_fmt_news(state),
        rag_block=_fmt_rag(state),
    )

    response = await _llm.ainvoke([HumanMessage(content=prompt)])
    report = response.content.strip()

    console.print(f"[yellow]✓ synthesis_agent[/yellow]  {ticker}  {len(report)} chars")
    return {"final_report": report}
