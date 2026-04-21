import yfinance as yf
from pydantic import BaseModel


class Fundamentals(BaseModel):
    ticker: str
    name: str
    sector: str | None
    market_cap: float | None
    pe_ratio: float | None
    eps: float | None
    revenue_ttm: float | None
    summary: str | None


def get_fundamentals(ticker: str) -> Fundamentals:
    t = yf.Ticker(ticker)
    info = t.info
    return Fundamentals(
    ticker=ticker.upper(),
    name=info.get("longName", ticker),
    sector=info.get("sector"),
    market_cap=info.get("marketCap"),
    pe_ratio=info.get("trailingPE"),
    eps=info.get("trailingEps"),
    revenue_ttm=info.get("totalRevenue"),
    summary=info.get("longBusinessSummary"),
    )