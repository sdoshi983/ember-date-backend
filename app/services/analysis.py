from langgraph.graph import StateGraph, START, END

from app.schemas import GraphState, OnboardingInput, AnalysisOutput
from app.services.agents import run_insight_agent, run_trait_agent


def build_analysis_graph() -> StateGraph:
    """
    Build the LangGraph workflow for onboarding analysis.
    
    The graph runs two agents in parallel:
    - InsightAgent: produces summary and keywords
    - TraitAgent: produces trait scores with reasoning
    
    Graph structure:
        START
          │
          ├───────────────┬───────────────┐
          │               │               │
          ▼               ▼               │
    [insight_agent]  [trait_agent]        │
          │               │               │
          └───────────────┴───────────────┘
                          │
                          ▼
                        END
    """
    graph = StateGraph(GraphState)
    
    # Add agent nodes
    graph.add_node("insight_agent", run_insight_agent)
    graph.add_node("trait_agent", run_trait_agent)
    
    # Wire up parallel execution from START
    graph.add_edge(START, "insight_agent")
    graph.add_edge(START, "trait_agent")
    
    # Both agents lead to END
    graph.add_edge("insight_agent", END)
    graph.add_edge("trait_agent", END)
    
    return graph


# Singleton compiled graph
_compiled_graph = None


def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_analysis_graph()
        _compiled_graph = graph.compile()
    return _compiled_graph


def analyze_response(input_data: OnboardingInput) -> AnalysisOutput:
    """
    Main entry point for analyzing an onboarding response.
    
    Args:
        input_data: Validated OnboardingInput with user_id, question, and answer
        
    Returns:
        AnalysisOutput with insight and traits from both agents
        
    Raises:
        ValueError: If agents encounter errors during processing
    """
    initial_state = GraphState(
        user_id=input_data.user_id,
        question=input_data.question,
        answer=input_data.answer
    )
    
    compiled = get_compiled_graph()
    final_state = compiled.invoke(initial_state)
    
    if final_state.get("errors"):
        raise ValueError(f"Agent errors: {final_state['errors']}")
    
    insight_data = final_state.get("insight")
    if insight_data is None:
        raise ValueError("InsightAgent did not produce output")
    
    return AnalysisOutput(
        user_id=input_data.user_id,
        insight=insight_data,
        traits=final_state.get("traits", [])
    )

