import asyncio
from dotenv import load_dotenv

load_dotenv()

import typer
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer(help="Financial Research Multi-Agent CLI")
console = Console()


@app.command()
def analyze(
    query: str = typer.Argument(..., help='Research query e.g. "Is Tesla a good buy?"'),
    no_rag: bool = typer.Option(False, "--no-rag", help="Skip RAG (faster, no filing data)"),
):
    """Run the full multi-agent research pipeline for a query."""
    from fin_agents.agents.graph import build_graph

    initial = {
        "query": query,
        "ticker": "",
        "fundamentals": None,
        "news": None,
        "news_summary": None,
        "rag_chunks": None,
        "final_report": None,
    }

    graph = build_graph()

    with console.status("[bold cyan]Running research agents...[/bold cyan]"):
        state = asyncio.run(graph.ainvoke(initial))

    report = state.get("final_report", "")
    if report:
        console.print(Markdown(report))
    else:
        console.print("[red]No report generated.[/red]")


@app.command()
def ingest(
    tickers: list[str] = typer.Argument(..., help="Ticker symbols to ingest e.g. AAPL TSLA NVDA"),
    refresh: bool = typer.Option(False, "--refresh", help="Delete existing chunks and re-ingest (use after a new filing)"),
):
    """Ingest SEC filings for one or more tickers into the RAG vector store."""
    from fin_agents.rag.ingest import ingest_ticker

    for ticker in tickers:
        label = "Re-ingesting" if refresh else "Ingesting"
        with console.status(f"[cyan]{label} {ticker.upper()}...[/cyan]"):
            try:
                n = ingest_ticker(ticker, refresh=refresh)
                console.print(f"[green]✓[/green] {ticker.upper()}  {n} chunks stored")
            except Exception as e:
                console.print(f"[red]✗[/red] {ticker.upper()}  {e}")


def main():
    app()
