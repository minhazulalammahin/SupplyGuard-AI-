"""LangGraph node implementations for SupplyGuard AI."""
from pathlib import Path
from typing import Any, Dict
from src.models.state import SupplyGuardState
from src.services.pdf_loader import extract_pdf_document
from src.services.pr_repository import PurchaseRequestRepository
from src.services.gemini_extractor import extract_supplier_quotation
from src.services.evidence_verifier import verify_quotation_evidence
from src.services.rule_engine import evaluate_quotation


def node_load_document(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 1: Extract text from PDF using PyMuPDF."""
    pdf_path = Path(state.pdf_path)
    page_texts, full_text = extract_pdf_document(pdf_path)
    return {
        "pdf_filename": pdf_path.name,
        "page_texts": page_texts,
        "full_text": full_text
    }


def node_load_pr_baseline(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 2: Load PR baseline items from purchase-request.csv."""
    repo = PurchaseRequestRepository()
    pr_items = repo.get_all_items()
    return {"pr_items": pr_items}


def node_extract_quotation(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 3: Extract structured quotation data using Gemini (or deterministic fallback)."""
    quotation = extract_supplier_quotation(
        document_text=state.full_text,
        use_ai=True,
        filename=state.pdf_filename
    )
    return {
        "extracted_quotation": quotation,
        "extraction_successful": quotation is not None
    }


def node_match_pr_item(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 4: Match quotation to appropriate PR item (A, B, C, D, E)."""
    quotation = state.extracted_quotation
    if not quotation or not quotation.item_code:
        # If item_code missing, fall back to checking text for item descriptions
        for code, item in state.pr_items.items():
            if item.description.lower() in state.full_text.lower():
                return {"selected_pr_item": item}
        return {"selected_pr_item": None, "error_message": "Could not identify PR item from document"}

    pr_item = state.pr_items.get(quotation.item_code.strip())
    return {"selected_pr_item": pr_item}


def node_verify_evidence(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 5: Anti-hallucination verification of all supporting citations."""
    quotation = state.extracted_quotation
    if not quotation:
        return {"unverified_evidence": ["No quotation extracted"]}
        
    verified_quote, unverified = verify_quotation_evidence(
        quotation=quotation,
        full_document_text=state.full_text,
        pdf_filename=state.pdf_filename
    )
    return {
        "extracted_quotation": verified_quote,
        "unverified_evidence": unverified
    }


def node_evaluate_rules(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 6: Deterministic business rule validation."""
    if not state.selected_pr_item:
        raise ValueError("Cannot evaluate rules without a matched PR item.")
    if not state.extracted_quotation:
        raise ValueError("Cannot evaluate rules without extracted quotation.")

    result = evaluate_quotation(
        quotation=state.extracted_quotation,
        pr_item=state.selected_pr_item,
        filename=state.pdf_filename,
        unverified_evidence=state.unverified_evidence
    )
    return {"verification_result": result}
