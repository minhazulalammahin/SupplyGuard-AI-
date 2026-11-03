"""LangGraph fixed workflow definition for SupplyGuard AI."""
from langgraph.graph import StateGraph, START, END
from src.models.state import SupplyGuardState
from src.workflow.nodes import (
    node_load_document,
    node_load_pr_baseline,
    node_extract_quotation,
    node_match_pr_item,
    node_verify_evidence,
    node_evaluate_rules,
)


def create_supply_guard_graph():
    """Build and compile the fixed, deterministic step-by-step verification workflow."""
    builder = StateGraph(SupplyGuardState)

    # Register workflow nodes
    builder.add_node("load_document", node_load_document)
    builder.add_node("load_pr_baseline", node_load_pr_baseline)
    builder.add_node("extract_quotation", node_extract_quotation)
    builder.add_node("match_pr_item", node_match_pr_item)
    builder.add_node("verify_evidence", node_verify_evidence)
    builder.add_node("evaluate_rules", node_evaluate_rules)

    # Define fixed linear execution pipeline
    builder.add_edge(START, "load_document")
    builder.add_edge("load_document", "load_pr_baseline")
    builder.add_edge("load_pr_baseline", "extract_quotation")
    builder.add_edge("extract_quotation", "match_pr_item")
    builder.add_edge("match_pr_item", "verify_evidence")
    builder.add_edge("verify_evidence", "evaluate_rules")
    builder.add_edge("evaluate_rules", END)

    return builder.compile()


def run_verification(pdf_path: str) -> SupplyGuardState:
    """Execute the full verification workflow on a single PDF document."""
    graph = create_supply_guard_graph()
    initial_state = SupplyGuardState(pdf_path=str(pdf_path))
    final_output = graph.invoke(initial_state)
    return SupplyGuardState.model_validate(final_output)
