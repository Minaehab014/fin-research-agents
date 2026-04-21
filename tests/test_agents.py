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
    state = asyncio.run(_run("Analyze Apple's latest quarter"))
    print(state.get("final_report", ""))
