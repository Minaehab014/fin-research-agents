import json
from rich.console import Console
from langchain_core.messages import HumanMessage
from fin_agents.agents.state import ResearchState
from fin_agents.data.news import get_news, NewsItem
from fin_agents.config import groq_llm

console = Console()
_llm = groq_llm()

_SENTIMENT_PROMPT = """\
You are a financial news analyst. For each headline below, assign a sentiment:\
 positive, negative, or neutral.

Then write a 2-3 sentence summary of the overall news theme.

Headlines:
{headlines}

Respond in this exact JSON format:
{{
  "sentiments": ["positive", "neutral", ...],
  "summary": "Overall theme in 2-3 sentences."
}}"""


async def run_news(state: ResearchState) -> dict:
    ticker = state["ticker"]
    query = state.get("query", ticker)
    console.print(f"[bold cyan]⟳ news_agent[/bold cyan]  {ticker}")

    items: list[NewsItem] = get_news(ticker, limit=5)
    if not items:
        console.print(f"[cyan]✓ news_agent[/cyan]  {ticker}  no articles found")
        return {"news": [], "news_summary": "No recent news found."}

    headlines = "\n".join(f"{i+1}. {item.title}" for i, item in enumerate(items))
    response = await _llm.ainvoke(
        [HumanMessage(content=_SENTIMENT_PROMPT.format(headlines=headlines))]
    )

    try:
        parsed = json.loads(response.content.strip())
        sentiments: list[str] = parsed.get("sentiments", [])
        summary: str = parsed.get("summary", "")
    except (json.JSONDecodeError, AttributeError):
        sentiments = ["neutral"] * len(items)
        summary = response.content.strip()

    for item, sent in zip(items, sentiments):
        item.sentiment = sent

    console.print(f"[cyan]✓ news_agent[/cyan]  {ticker}  {len(items)} articles tagged")
    return {"news": items, "news_summary": summary}
