import hashlib
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb import PersistentClient
from chromadb.utils import embedding_functions

from fin_agents.data.filings import latest_filing

# Anchored to project root (src/fin_agents/rag/ -> up 3 levels)
CHROMA_PATH = str(Path(__file__).parent.parent.parent.parent / "chroma_db")
COLLECTION_NAME = "filings"
# Best free model for Apple Silicon: large context (8192 tokens), top MTEB scores, runs on MPS
EMBED_MODEL = "BAAI/bge-m3"

_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)


def _collection():
    client = PersistentClient(path=CHROMA_PATH)
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    return client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embed_fn)


def _chunk_id(ticker: str, filing_date: str, chunk_index: int) -> str:
    key = f"{ticker.upper()}_{filing_date}_{chunk_index}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def ingest_ticker(ticker: str) -> int:
    """Fetch, chunk, and upsert the latest 10-K/10-Q for one ticker. Returns chunk count."""
    filing = latest_filing(ticker)
    chunks = _splitter.split_text(filing.text)
    col = _collection()

    ids = [_chunk_id(ticker, filing.filing_date, i) for i in range(len(chunks))]
    metadatas = [
        {
            "ticker": filing.ticker,
            "filing_type": filing.filing_type,
            "filing_date": filing.filing_date,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    col.upsert(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def ingest_tickers(tickers: list[str]) -> dict[str, int]:
    """Ingest a list of tickers. Returns {ticker: chunk_count}."""
    return {t: ingest_ticker(t) for t in tickers}
