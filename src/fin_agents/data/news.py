import os, requests
from pydantic import BaseModel
from datetime import datetime

class NewsItem(BaseModel):
    title: str
    url: str
    published_at: datetime
    source: str
    description: str | None
    sentiment: str | None = None  # written by news_agent LLM: positive/negative/neutral

def get_news(query: str, limit: int = 5) -> list[NewsItem]:
    r = requests.get(
    "https://newsapi.org/v2/everything",
    params={"q": query, "sortBy": "publishedAt",
    "pageSize": limit, "language": "en"},
    headers={"X-Api-Key": os.environ["NEWSAPI_KEY"]},
    timeout=15,
    )
    r.raise_for_status()
    items = []
    for a in r.json().get("articles", []):
        items.append(NewsItem(
        title=a["title"], url=a["url"],
        published_at=a["publishedAt"],
        source=a["source"]["name"],
        description=a.get("description"),
        ))
    return items