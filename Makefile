.PHONY: install dev test lint format clean ingest analyze mcp

# ── Setup ─────────────────────────────────────────────────────────────────────

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

# ── Quality ───────────────────────────────────────────────────────────────────

lint:
	ruff check src tests

format:
	ruff format src tests

test:
	pytest tests/ -v

# ── CLI shortcuts ─────────────────────────────────────────────────────────────

# Usage: make ingest TICKER=AAPL
ingest:
	fin-research ingest $(TICKER)

# Usage: make analyze TICKER=AAPL
analyze:
	fin-research analyze $(TICKER)

# Start the MCP server
mcp:
	fin-research-mcp

# ── Housekeeping ──────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
