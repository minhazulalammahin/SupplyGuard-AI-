"""LangGraph fixed 8-node step-by-step workflow definition for SupplyGuard AI."""
from langgraph.graph import StateGraph, START, END
from src.models.state import SupplyGuardState
from src.workflow.nodes import (
    node_document_loading,
    node_text_extraction,
    node_structured_information_extraction,
    node_extraction_validation,
    node_purchase_request_comparison,
    node_contract_rule_validation,
    node_final_decision,
    node_report_generation,
)


def create_supply_guard_graph():
    """Build and compile the fixed 8-node verification workflow."""
    builder = StateGraph(SupplyGuardState)

    # 1. Register the 8 explicit nodes
    builder.add_node("document_loading", node_document_loading)
    builder.add_node("text_extraction", node_text_extraction)
    builder.add_node("structured_information_extraction", node_structured_information_extraction)
    builder.add_node("extraction_validation", node_extraction_validation)
    builder.add_node("purchase_request_comparison", node_purchase_request_comparison)
    builder.add_node("contract_rule_validation", node_contract_rule_validation)
    builder.add_node("final_decision", node_final_decision)
    builder.add_node("report_generation", node_report_generation)

    # 2. Connect in fixed sequential order
    builder.add_edge(START, "document_loading")
    builder.add_edge("document_loading", "text_extraction")
    builder.add_edge("text_extraction", "structured_information_extraction")
    builder.add_edge("structured_information_extraction", "extraction_validation")
    builder.add_edge("extraction_validation", "purchase_request_comparison")
    builder.add_edge("purchase_request_comparison", "contract_rule_validation")
    builder.add_edge("contract_rule_validation", "final_decision")
    builder.add_edge("final_decision", "report_generation")
    builder.add_edge("report_generation", END)

    return builder.compile()


def run_verification(pdf_path: str) -> SupplyGuardState:
    """Execute the full 8-node verification workflow on a single PDF document."""
    graph = create_supply_guard_graph()
    initial_state = SupplyGuardState(pdf_path=str(pdf_path))
    final_output = graph.invoke(initial_state)
    return SupplyGuardState.model_validate(final_output)
