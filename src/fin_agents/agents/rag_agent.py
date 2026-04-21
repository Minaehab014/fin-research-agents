import hashlib
from rich.console import Console
from langchain_core.messages import HumanMessage
from fin_agents.agents.state import ResearchState
from fin_agents.rag.retriever import retrieve
from fin_agents.rag.ingest import ingest_ticker, _collection
from fin_agents.config import groq_llm

console = Console()
_llm = groq_llm()

_SUBQUERY_PROMPT = """\
You are a financial research assistant preparing queries to search SEC filing chunks.

Original question: {query}
Company ticker: {ticker}

Generate exactly 3 specific sub-queries that together cover the original question.
Return ONLY a JSON array of 3 strings — no explanation.
Example: ["What were revenue and gross margin trends?", "What risks were disclosed?", "What is the capital allocation strategy?"]"""


async def run_rag(state: ResearchState) -> dict:
    ticker = state["ticker"]
    query = state["query"]
    console.print(f"[bold cyan]⟳ rag_agent[/bold cyan]  {ticker}")

    # Auto-ingest if this ticker has no chunks yet
    col = _collection()
    existing = col.get(where={"ticker": ticker.upper()}, limit=1)
    if not existing["ids"]:
        console.print(f"[cyan]  rag_agent[/cyan]  {ticker} not in DB — ingesting now...")
        n = ingest_ticker(ticker)
        console.print(f"[cyan]  rag_agent[/cyan]  {ticker} ingested {n} chunks")

    # Generate sub-queries
    response = await _llm.ainvoke(
        [HumanMessage(content=_SUBQUERY_PROMPT.format(query=query, ticker=ticker))]
    )
    try:
        import json
        sub_queries: list[str] = json.loads(response.content.strip())
    except Exception:
        sub_queries = [query]

    # Retrieve chunks for each sub-query and deduplicate by content hash
    seen: set[str] = set()
    all_chunks: list[dict] = []
    for sq in sub_queries:
        for chunk in retrieve(sq, ticker=ticker, k=5):
            key = hashlib.md5(chunk["text"].encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                chunk["sub_query"] = sq
                all_chunks.append(chunk)

    console.print(
        f"[cyan]✓ rag_agent[/cyan]  {ticker}  "
        f"{len(sub_queries)} sub-queries → {len(all_chunks)} unique chunks"
    )
    return {"rag_chunks": all_chunks}
