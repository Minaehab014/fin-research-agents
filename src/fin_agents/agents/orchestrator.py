from rich.console import Console
from langchain_core.messages import HumanMessage
from fin_agents.agents.state import ResearchState
from fin_agents.config import groq_llm

console = Console()
_llm = groq_llm()

_PROMPT = """\
Extract the stock ticker symbol from the query below.
If a company name is given (e.g. "Apple", "Nvidia"), convert it to its correct ticker.
Return ONLY the uppercase ticker symbol — nothing else. Examples: AAPL, NVDA, TSLA.

Query: {query}"""


async def run_orchestrator(state: ResearchState) -> dict:
    query = state["query"]
    console.print(f"[bold cyan]⟳ orchestrator[/bold cyan]  query={query!r}")

    response = await _llm.ainvoke([HumanMessage(content=_PROMPT.format(query=query))])
    ticker = response.content.strip().upper()

    console.print(f"[cyan]✓ orchestrator[/cyan]  ticker={ticker}")
    return {"query": query, "ticker": ticker}
