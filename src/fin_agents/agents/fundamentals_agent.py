from rich.console import Console
from langchain_core.messages import HumanMessage
from fin_agents.agents.state import ResearchState
from fin_agents.data.fundamentals import get_fundamentals
from fin_agents.config import groq_llm

console = Console()
_llm = groq_llm()

_PROMPT = """\
You are a buy-side equity analyst. Given these metrics for {name} ({ticker}):

  Sector:      {sector}
  Market Cap:  ${market_cap:,.0f}
  P/E Ratio:   {pe_ratio}
  EPS:         {eps}
  Revenue TTM: ${revenue_ttm:,.0f}

Write a concise one-paragraph analyst commentary. Highlight valuation signals,\
 growth context, and any notable observations. Be direct — no filler."""


async def run_fundamentals(state: ResearchState) -> dict:
    ticker = state["ticker"]
    console.print(f"[bold cyan]⟳ fundamentals_agent[/bold cyan]  {ticker}")

    f = get_fundamentals(ticker)

    prompt = _PROMPT.format(
        name=f.name,
        ticker=ticker,
        sector=f.sector or "N/A",
        market_cap=f.market_cap or 0,
        pe_ratio=f.pe_ratio or "N/A",
        eps=f.eps or "N/A",
        revenue_ttm=f.revenue_ttm or 0,
    )
    response = await _llm.ainvoke([HumanMessage(content=prompt)])
    f.commentary = response.content.strip()

    console.print(f"[cyan]✓ fundamentals_agent[/cyan]  {ticker}  market_cap=${f.market_cap:,.0f}")
    return {"fundamentals": f}
