"""LangGraph node implementations for SupplyGuard AI.

Each node represents an isolated, testable step in the verification pipeline:
1. document_loading
2. text_extraction
3. structured_information_extraction
4. extraction_validation
5. purchase_request_comparison
6. contract_rule_validation
7. final_decision
8. report_generation
"""
from pathlib import Path
from typing import Any, Dict
from src.models.state import SupplyGuardState
from src.models.schemas import VerificationResult
from src.services.pdf_loader import extract_pdf_document
from src.services.pr_repository import PurchaseRequestRepository
from src.services.gemini_extractor import extract_supplier_quotation
from src.services.evidence_verifier import verify_quotation_evidence
from src.services.rule_engine import (
    compare_purchase_request,
    validate_contract_rules,
    resolve_decision,
)


def node_document_loading(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 1: Document Loading - Validate file presence and initialize document path."""
    path = Path(state.pdf_path)
    if not path.exists():
        return {
            "is_document_loaded": False,
            "error_message": f"Document file not found: {path}"
        }
    return {
        "pdf_filename": path.name,
        "is_document_loaded": True
    }


def node_text_extraction(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 2: Text Extraction - Extract page-by-page text preserving page numbers via PyMuPDF."""
    if not state.is_document_loaded:
        return {"error_message": "Cannot extract text: document not loaded."}

    page_texts, full_text = extract_pdf_document(state.pdf_path)
    return {
        "page_texts": page_texts,
        "full_text": full_text,
        "page_count": len(page_texts)
    }


def node_structured_information_extraction(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 3: Structured Information Extraction - Use Gemini 2.5 Flash (or deterministic fallback)."""
    if not state.full_text:
        return {
            "extraction_successful": False,
            "error_message": "Cannot extract structured information: document text is empty."
        }

    quotation = extract_supplier_quotation(
        document_text=state.full_text,
        use_ai=True,
        filename=state.pdf_filename
    )
    return {
        "extracted_quotation": quotation,
        "extraction_successful": quotation is not None
    }


def node_extraction_validation(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 4: Extraction Validation - Validate schema structure and verify all evidence citations."""
    quotation = state.extracted_quotation
    if not quotation:
        return {
            "unverified_evidence": ["Extraction failed: no quotation object available"],
            "is_extraction_valid": False
        }

    verified_quotation, unverified = verify_quotation_evidence(
        quotation=quotation,
        full_document_text=state.full_text,
        pdf_filename=state.pdf_filename
    )
    return {
        "extracted_quotation": verified_quotation,
        "unverified_evidence": unverified,
        "is_extraction_valid": len(unverified) == 0
    }


def node_purchase_request_comparison(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 5: Purchase Request Comparison - Match PR item and evaluate price/quantity variances."""
    # 1. Load PR Repository
    repo = PurchaseRequestRepository()
    pr_items = repo.get_all_items()

    quotation = state.extracted_quotation
    selected_pr_item = None

    if quotation and quotation.item_code and quotation.item_code.strip() in pr_items:
        selected_pr_item = pr_items[quotation.item_code.strip()]
    elif quotation:
        # Fallback by item description
        for item in pr_items.values():
            if item.description.lower() in state.full_text.lower():
                selected_pr_item = item
                break

    if not selected_pr_item:
        return {
            "pr_items": pr_items,
            "selected_pr_item": None,
            "error_message": "Could not identify corresponding Purchase Request item."
        }

    # Evaluate PR rules (Price ceiling & quantity tolerance)
    pr_findings = compare_purchase_request(quotation, selected_pr_item)

    return {
        "pr_items": pr_items,
        "selected_pr_item": selected_pr_item,
        "pr_comparison_findings": pr_findings
    }


def node_contract_rule_validation(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 6: Contract Rule Validation - Validate commercial clauses, registration, taxes, math."""
    quotation = state.extracted_quotation
    if not quotation:
        return {"contract_rule_findings": []}

    contract_findings = validate_contract_rules(quotation)
    return {"contract_rule_findings": contract_findings}


def node_final_decision(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 7: Final Decision - Apply priority REJECT > NEEDS_A_PERSON_TO_CHECK > APPROVE."""
    decision, reason, rejections, reviews, compliances = resolve_decision(
        pr_findings=state.pr_comparison_findings,
        contract_findings=state.contract_rule_findings,
        unverified_evidence=state.unverified_evidence
    )
    return {
        "overall_decision": decision,
        "decision_reason": reason,
        "rejection_findings": rejections,
        "review_findings": reviews,
        "compliance_findings": compliances
    }


def node_report_generation(state: SupplyGuardState) -> Dict[str, Any]:
    """Node 8: Report Generation - Assemble structured VerificationResult and markdown audit summary."""
    all_findings = state.rejection_findings + state.review_findings + state.compliance_findings

    audit_summary = (
        f"DECISION: {state.overall_decision}\n"
        f"Primary Reason: {state.decision_reason}\n"
        f"Total Rejections: {len(state.rejection_findings)} | "
        f"Reviews: {len(state.review_findings)} | "
        f"Compliances: {len(state.compliance_findings)}"
    )

    result = VerificationResult(
        filename=state.pdf_filename,
        pr_item=state.selected_pr_item,
        quotation=state.extracted_quotation,
        overall_decision=state.overall_decision or "NEEDS_A_PERSON_TO_CHECK",
        decision_reason=state.decision_reason or "Audit completed",
        findings=all_findings,
        rejection_findings=state.rejection_findings,
        review_findings=state.review_findings,
        compliance_findings=state.compliance_findings,
        unverified_evidence=state.unverified_evidence,
        audit_summary=audit_summary
    )

    # Build clean markdown report
    md_lines = [
        f"# SupplyGuard AI Verification Report: {state.pdf_filename}",
        f"**Overall Decision:** `{state.overall_decision}`",
        f"**Summary:** {state.decision_reason}",
        "",
        "## Purchase Request Item Match",
        f"- **Item Code:** {state.selected_pr_item.item_code if state.selected_pr_item else 'N/A'}",
        f"- **Description:** {state.selected_pr_item.description if state.selected_pr_item else 'N/A'}",
        f"- **Maximum Ceiling:** BDT {state.selected_pr_item.maximum_unit_price if state.selected_pr_item else 'N/A'}",
        "",
        "## Audit Findings",
    ]
    for f in all_findings:
        icon = "🔴" if f.category == "REJECT" else ("🟡" if f.category == "NEEDS_A_PERSON_TO_CHECK" else "🟢")
        md_lines.append(f"- {icon} **[{f.rule_id}] {f.rule_name}**: {f.description}")
        md_lines.append(f"  - *Evidence:* `{f.evidence_text}`")

    return {
        "verification_result": result,
        "report_markdown": "\n".join(md_lines)
    }
