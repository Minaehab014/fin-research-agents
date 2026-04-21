from typing import TypedDict
from fin_agents.data.fundamentals import Fundamentals
from fin_agents.data.news import NewsItem


class ResearchState(TypedDict):
    query: str
    ticker: str
    fundamentals: Fundamentals | None
    news: list[NewsItem] | None
    news_summary: str | None   # 2-3 sentence theme written by news_agent
    rag_chunks: list[dict] | None
    final_report: str | None
