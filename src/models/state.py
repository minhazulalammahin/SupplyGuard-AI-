"""LangGraph State Definition for SupplyGuard AI."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from src.models.schemas import (
    ExtractedQuotation,
    PurchaseRequestItem,
    RuleFinding,
    VerificationResult
)


class SupplyGuardState(BaseModel):
    """Execution state passed across the 8 sequential nodes in the LangGraph workflow."""
    # 1. Document Loading
    pdf_path: str
    pdf_filename: str = ""
    is_document_loaded: bool = False

    # 2. Text Extraction (PyMuPDF)
    page_texts: Dict[int, str] = Field(default_factory=dict)
    full_text: str = ""
    page_count: int = 0

    # 3. Structured Information Extraction (Gemini 2.5 Flash)
    extracted_quotation: Optional[ExtractedQuotation] = None
    extraction_successful: bool = False

    # 4. Extraction Validation
    unverified_evidence: List[str] = Field(default_factory=list)
    is_extraction_valid: bool = False

    # 5. Purchase Request Comparison
    pr_items: Dict[str, PurchaseRequestItem] = Field(default_factory=dict)
    selected_pr_item: Optional[PurchaseRequestItem] = None
    pr_comparison_findings: List[RuleFinding] = Field(default_factory=list)

    # 6. Contract Rule Validation
    contract_rule_findings: List[RuleFinding] = Field(default_factory=list)

    # 7. Final Decision
    rejection_findings: List[RuleFinding] = Field(default_factory=list)
    review_findings: List[RuleFinding] = Field(default_factory=list)
    compliance_findings: List[RuleFinding] = Field(default_factory=list)
    overall_decision: Optional[str] = None
    decision_reason: Optional[str] = None

    # 8. Report Generation
    verification_result: Optional[VerificationResult] = None
    report_markdown: str = ""

    # Error tracking
    error_message: Optional[str] = None
