"""
End-to-end agent graph test.

Run:
    pytest tests/test_agents.py -v -s
    python tests/test_agents.py
"""
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def _run(query: str) -> dict:
    from fin_agents.agents.graph import build_graph
    graph = build_graph()
    initial = {
        "query": query,
        "ticker": "",
        "fundamentals": None,
        "news": None,
        "news_summary": None,
        "rag_chunks": None,
        "final_report": None,
    }
    return await graph.ainvoke(initial)


def test_end_to_end_report():
    state = asyncio.run(_run("Analyze Apple's latest quarter"))

    print(f"\n  ticker:         {state['ticker']}")
    print(f"  fundamentals:   {state['fundamentals'].name if state['fundamentals'] else 'None'}")
    print(f"  news items:     {len(state['news'] or [])}")
    print(f"  rag chunks:     {len(state['rag_chunks'] or [])}")
    print(f"  report length:  {len(state.get('final_report') or '')} chars")
    print("\n--- REPORT ---")
    print(state.get("final_report", ""))

    assert state["ticker"] == "AAPL"
    assert state["fundamentals"] is not None
    assert state["fundamentals"].commentary
    assert len(state["news"] or []) > 0
    assert len(state["rag_chunks"] or []) > 0
    assert state["final_report"]
    assert "## Executive Summary" in state["final_report"]


if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    load_dotenv()

    # python tests/test_agents.py --ingest TSLA NVDA   → ingest tickers (one-time per ticker)
    # python tests/test_agents.py "query"              → run analysis
    if len(sys.argv) > 1 and sys.argv[1] == "--ingest":
        from fin_agents.rag.ingest import ingest_ticker
        tickers = sys.argv[2:]
        if not tickers:
            print("Usage: python tests/test_agents.py --ingest TICKER [TICKER ...]")
        for t in tickers:
            print(f"Ingesting {t}...")
            n = ingest_ticker(t)
            print(f"  {n} chunks stored for {t}")
    else:
        query = sys.argv[1] if len(sys.argv) > 1 else "Is Tesla a good buy right now"
        state = asyncio.run(_run(query))
        print(state.get("final_report", ""))
