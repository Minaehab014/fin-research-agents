from langgraph.graph import StateGraph, START, END
from fin_agents.agents.state import ResearchState
from fin_agents.agents.orchestrator import run_orchestrator
from fin_agents.agents.fundamentals_agent import run_fundamentals
from fin_agents.agents.news_agent import run_news
from fin_agents.agents.rag_agent import run_rag
from fin_agents.agents.synthesis_agent import run_synthesis


def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("orchestrator", run_orchestrator)
    builder.add_node("fundamentals", run_fundamentals)
    builder.add_node("news", run_news)
    builder.add_node("rag", run_rag)
    builder.add_node("synthesis", run_synthesis)

    # Entry
    builder.add_edge(START, "orchestrator")

    # Fan-out: orchestrator → 3 specialists in parallel
    builder.add_edge("orchestrator", "fundamentals")
    builder.add_edge("orchestrator", "news")
    builder.add_edge("orchestrator", "rag")

    # Fan-in: all 3 → synthesis (barrier — synthesis waits for all three)
    builder.add_edge("fundamentals", "synthesis")
    builder.add_edge("news", "synthesis")
    builder.add_edge("rag", "synthesis")

    builder.add_edge("synthesis", END)

    return builder.compile()
