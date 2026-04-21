from fin_agents.rag.ingest import _collection


def retrieve(query: str, ticker: str | None = None, k: int = 5) -> list[dict]:
    col = _collection()
    where = {"ticker": ticker.upper()} if ticker else None
    res = col.query(query_texts=[query], n_results=k, where=where)
    return [
        {"text": t, "meta": m, "score": d}
        for t, m, d in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        )
    ]
