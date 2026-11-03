"""LangGraph State Definition for SupplyGuard AI."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from src.models.schemas import ExtractedQuotation, PurchaseRequestItem, VerificationResult


class SupplyGuardState(BaseModel):
    """Execution state passed between nodes in the LangGraph workflow."""
    pdf_path: str
    pdf_filename: str = ""
    page_texts: Dict[int, str] = Field(default_factory=dict)
    full_text: str = ""
    
    # Baseline PR data
    pr_items: Dict[str, PurchaseRequestItem] = Field(default_factory=dict)
    selected_pr_item: Optional[PurchaseRequestItem] = None
    
    # Extraction & Evidence Verification
    extracted_quotation: Optional[ExtractedQuotation] = None
    unverified_evidence: List[str] = Field(default_factory=list)
    extraction_successful: bool = False
    
    # Audit & Rule Evaluation
    verification_result: Optional[VerificationResult] = None
    
    # Error tracking
    error_message: Optional[str] = None
