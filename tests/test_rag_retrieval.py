"""
Retrieval quality evaluation — Apple 10-K (FY2024).

Grading: a question is a HIT if at least one of the top-5 chunks contains
the expected keyword(s). Target: >= 7/10 hits (70%).

Run via pytest:
    pytest tests/test_rag_retrieval.py -v -s

Run directly (ingests AAPL then evaluates):
    python tests/test_rag_retrieval.py
    python tests/test_rag_retrieval.py --ingest   # force re-ingest first
"""
import sys
import pytest
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# 10 hand-crafted question / keyword pairs  (Apple FY2024 10-K)
# Each "keywords" entry is a list of strings; a chunk is a hit if it
# contains ANY of them (case-insensitive).
# ---------------------------------------------------------------------------
QA_PAIRS = [
    {
        "question": "What was Apple's total net revenue for fiscal year 2024?",
        "keywords": ["391", "net sales", "total net sales"],
    },
    {
        "question": "What is Apple's primary business and main products?",
        "keywords": ["iphone", "mac", "ipad", "wearables", "services"],
    },
    {
        "question": "How much did Apple spend on research and development in 2024?",
        "keywords": ["research and development", "r&d"],
    },
    {
        "question": "What was Apple's net income in fiscal 2024?",
        "keywords": ["net income", "93", "earnings"],
    },
    {
        "question": "What are the main risk factors Apple disclosed?",
        "keywords": ["risk factor", "competition", "supply chain", "economic conditions"],
    },
    {
        "question": "How does Apple generate revenue from its Services segment?",
        "keywords": ["app store", "apple music", "icloud", "advertising", "licensing"],
    },
    {
        "question": "What is Apple's strategy for share repurchases and dividends?",
        "keywords": ["repurchase", "buyback", "dividend"],
    },
    {
        "question": "Which geographic regions does Apple report revenue for?",
        "keywords": ["americas", "europe", "greater china", "japan", "rest of asia"],
    },
    {
        "question": "What manufacturing and supply chain risks does Apple face?",
        "keywords": ["supplier", "manufacturer", "taiwan", "china", "concentration"],
    },
    {
        "question": "What was Apple's total cash and marketable securities position?",
        "keywords": ["cash and cash equivalents", "marketable securities", "liquidity"],
    },
]

TICKER = "AAPL"
K = 5
PASS_THRESHOLD = 0.70


def _chunks_contain(chunks: list[dict], keywords: list[str]) -> bool:
    combined = " ".join(c["text"] for c in chunks).lower()
    return any(kw.lower() in combined for kw in keywords)


# ---------------------------------------------------------------------------
# Parametrized test — one test case per Q&A pair
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("qa", QA_PAIRS, ids=[f"q{i+1}" for i in range(len(QA_PAIRS))])
def test_retrieval_hit(qa):
    from fin_agents.rag.retriever import retrieve

    chunks = retrieve(qa["question"], ticker=TICKER, k=K)

    hit = _chunks_contain(chunks, qa["keywords"])

    print(f"\n  Q: {qa['question']}")
    print(f"  keywords: {qa['keywords']}")
    print(f"  hit: {hit}")
    if not hit:
        print("  top chunk preview:")
        for c in chunks:
            print(f"    [{c['score']:.4f}] {c['text'][:120]!r}")

    assert hit, (
        f"None of {qa['keywords']} found in top-{K} chunks for: {qa['question']!r}"
    )


# ---------------------------------------------------------------------------
# Summary test — overall hit rate must meet threshold
# ---------------------------------------------------------------------------
def test_overall_hit_rate():
    from fin_agents.rag.retriever import retrieve

    hits = 0
    for qa in QA_PAIRS:
        chunks = retrieve(qa["question"], ticker=TICKER, k=K)
        if _chunks_contain(chunks, qa["keywords"]):
            hits += 1

    rate = hits / len(QA_PAIRS)
    print(f"\n  Hit rate: {hits}/{len(QA_PAIRS)} = {rate:.0%}")
    assert rate >= PASS_THRESHOLD, (
        f"Retrieval hit rate {rate:.0%} is below the {PASS_THRESHOLD:.0%} target"
    )


# ---------------------------------------------------------------------------
# Direct-run entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    load_dotenv()
    from fin_agents.rag.ingest import ingest_ticker
    from fin_agents.rag.retriever import retrieve

    if "--ingest" in sys.argv:
        print(f"Ingesting {TICKER}...")
        n = ingest_ticker(TICKER)
        print(f"  {n} chunks stored.\n")

    hits = 0
    for i, qa in enumerate(QA_PAIRS, 1):
        chunks = retrieve(qa["question"], ticker=TICKER, k=K)
        hit = _chunks_contain(chunks, qa["keywords"])
        if hit:
            hits += 1
        status = "PASS" if hit else "FAIL"
        print(f"  [{status}] q{i}: {qa['question']}")
        if not hit:
            print(f"         keywords: {qa['keywords']}")
            print(f"         top chunk: {chunks[0]['text'][:120]!r}")

    rate = hits / len(QA_PAIRS)
    print(f"\n  Hit rate: {hits}/{len(QA_PAIRS)} = {rate:.0%}  "
          f"({'PASS' if rate >= PASS_THRESHOLD else 'FAIL'} — threshold {PASS_THRESHOLD:.0%})")
