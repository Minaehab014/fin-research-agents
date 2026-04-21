"""Integration tests for the data layer — hits real endpoints, no mocks."""
import sys
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# fundamentals
# ---------------------------------------------------------------------------

def test_get_fundamentals_shape():
    from fin_agents.data.fundamentals import get_fundamentals, Fundamentals

    result = get_fundamentals("AAPL")

    print(f"\n  ticker:     {result.ticker}")
    print(f"  name:       {result.name}")
    print(f"  sector:     {result.sector}")
    print(f"  market_cap: ${result.market_cap:,.0f}")
    print(f"  pe_ratio:   {result.pe_ratio}")
    print(f"  eps:        {result.eps}")
    print(f"  revenue:    ${result.revenue_ttm:,.0f}")

    assert isinstance(result, Fundamentals)
    assert result.ticker == "AAPL"
    assert result.name
    assert result.market_cap is not None and result.market_cap > 0
    assert result.pe_ratio is not None
    assert result.eps is not None


# ---------------------------------------------------------------------------
# news
# ---------------------------------------------------------------------------

def test_get_news_shape():
    from fin_agents.data.news import get_news, NewsItem

    results = get_news("Apple AAPL", limit=3)

    print()
    for i, item in enumerate(results, 1):
        print(f"  [{i}] {item.title}")
        print(f"      source: {item.source}  |  published: {item.published_at.date()}")
        print(f"      url: {item.url}")

    assert isinstance(results, list)
    assert len(results) > 0
    for item in results:
        assert isinstance(item, NewsItem)
        assert item.title
        assert item.url.startswith("http")
        assert item.source


# ---------------------------------------------------------------------------
# filings
# ---------------------------------------------------------------------------

def test_ticker_to_cik():
    from fin_agents.data.filings import ticker_to_cik

    cik = ticker_to_cik("AAPL")

    print(f"\n  AAPL CIK: {cik}")

    assert isinstance(cik, str)
    assert len(cik) == 10
    assert cik == "0000320193"


def test_latest_filing_shape():
    from fin_agents.data.filings import latest_filing, Filing

    result = latest_filing("AAPL")

    print(f"\n  ticker:       {result.ticker}")
    print(f"  filing_type:  {result.filing_type}")
    print(f"  filing_date:  {result.filing_date}")
    print(f"  text length:  {len(result.text):,} chars")
    print(f"  text preview: {result.text[:120]!r}")

    assert isinstance(result, Filing)
    assert result.ticker == "AAPL"
    assert result.filing_type in ("10-K", "10-Q")
    assert result.filing_date  # e.g. "2024-11-01"
    assert len(result.text) > 1000


# ---------------------------------------------------------------------------
# Direct-run entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

    tests = [
        ("fundamentals", test_get_fundamentals_shape),
        ("news",         test_get_news_shape),
        ("ticker_to_cik", test_ticker_to_cik),
        ("latest_filing", test_latest_filing_shape),
    ]

    passed = failed = 0
    for name, fn in tests:
        try:
            print(f"\n--- {name} ---")
            fn()
            print(f"  PASS")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
