"""Pydantic models and schemas for SupplyGuard AI."""
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EvidenceQuote(BaseModel):
    """Exact citation quote from the document supporting an extracted field."""
    field_name: str = Field(description="Name of the extracted field, e.g. 'unit_price', 'advance_payment'")
    quote: Optional[str] = Field(default=None, description="Verbatim text copied from the PDF document")
    page_number: int = Field(default=1, description="1-indexed page number where quote was found")
    is_present: bool = Field(default=True, description="False if this field or clause is missing from the document")
    is_verified: bool = Field(default=False, description="True if quote has been verified against raw PDF text")


class ExtractedQuotation(BaseModel):
    """Structured quotation extracted from a supplier document with strict Decimal values."""
    # Metadata
    supplier_name: Optional[str] = Field(default=None, description="Supplier company name")
    quotation_number: Optional[str] = Field(default=None, description="Quotation number / identifier")
    quotation_date: Optional[str] = Field(default=None, description="Quotation date (YYYY-MM-DD)")
    pr_reference: Optional[str] = Field(default=None, description="Purchase request reference number")

    # Item details
    item_code: Optional[str] = Field(default=None, description="Item code corresponding to PR (A, B, C, D, E)")
    item_description: Optional[str] = Field(default=None, description="Description of the item quoted")
    quantity: Optional[Decimal] = Field(default=None, description="Quantity quoted")
    unit: Optional[str] = Field(default=None, description="Unit of measurement, e.g. metre, piece, cone")
    unit_price: Optional[Decimal] = Field(default=None, description="Quoted unit price in BDT")
    line_amount: Optional[Decimal] = Field(default=None, description="Item line total amount in BDT")

    # Tax and totals
    subtotal: Optional[Decimal] = Field(default=None, description="Subtotal before taxes in BDT")
    vat_rate_pct: Optional[Decimal] = Field(default=None, description="Explicit VAT percentage rate (e.g. 15.0)")
    vat_amount: Optional[Decimal] = Field(default=None, description="Explicit VAT amount in BDT")
    vat_is_separate_at_15: bool = Field(default=False, description="Whether VAT is explicitly itemized as separate 15% line item")
    total_amount: Optional[Decimal] = Field(default=None, description="Total amount payable including VAT in BDT")

    # Registration details
    tin: Optional[str] = Field(default=None, description="Supplier Taxpayer Identification Number")
    bin: Optional[str] = Field(default=None, description="Supplier Business Identification Number")

    # Terms & Conditions (Normalized)
    advance_payment_pct: Optional[Decimal] = Field(default=Decimal("0.0"), description="Required advance payment percentage (0-100)")
    payment_min_days: Optional[int] = Field(default=None, description="Minimum days for payment after delivery/acceptance")
    payment_max_days: Optional[int] = Field(default=None, description="Maximum days for payment after delivery/acceptance")
    payment_reference_point: Optional[str] = Field(default=None, description="Reference event: 'delivery', 'PO', etc.")
    delivery_promised_days: Optional[int] = Field(default=None, description="Delivery promised in calendar days from PO")
    has_late_delivery_penalty_clause: bool = Field(default=True, description="False if late delivery penalty clause is missing")
    late_delivery_penalty_pct_per_week: Optional[Decimal] = Field(default=None, description="Late delivery penalty percentage per week of delay")
    validity_days: Optional[int] = Field(default=None, description="Quotation validity in calendar days")

    # Raw Textual Terms (preserved verbatim)
    payment_terms_raw: Optional[str] = Field(default=None, description="Verbatim text of payment clause")
    delivery_terms_raw: Optional[str] = Field(default=None, description="Verbatim text of delivery clause")
    penalty_terms_raw: Optional[str] = Field(default=None, description="Verbatim text of delay/penalty clause if present")
    validity_terms_raw: Optional[str] = Field(default=None, description="Verbatim text of quotation validity clause")
    tax_terms_raw: Optional[str] = Field(default=None, description="Verbatim text of VAT/Tax line items")
    tin_bin_raw: Optional[str] = Field(default=None, description="Verbatim text of TIN/BIN section")

    # Supporting Citations
    evidence_quotes: List[EvidenceQuote] = Field(default_factory=list, description="Exact quotes for verification")


class PurchaseRequestItem(BaseModel):
    """PR item specifications loaded from purchase-request.csv."""
    pr_number: str
    item_code: str
    description: str
    unit: str
    quantity_requested: Decimal
    maximum_unit_price: Decimal


class RuleFinding(BaseModel):
    """Individual rule evaluation audit finding."""
    rule_id: str = Field(description="Unique rule code, e.g. R1, R2, H1, H6")
    category: str = Field(description="'REJECT', 'NEEDS_A_PERSON_TO_CHECK', or 'APPROVE'")
    rule_name: str = Field(description="Human readable name of the rule")
    description: str = Field(description="Specific finding explanation")
    evidence_text: str = Field(description="Verbatim supporting text or [MISSING IN DOCUMENT]")
    observed_value: Optional[str] = Field(default=None, description="Observed value from supplier document")
    expected_value: Optional[str] = Field(default=None, description="Allowed boundary or baseline from PR/rules")
    is_violation: bool = Field(default=True, description="True if rule was violated or triggered review")


class VerificationResult(BaseModel):
    """Complete audit record for a supplier pack."""
    filename: str
    pr_item: Optional[PurchaseRequestItem] = None
    quotation: Optional[ExtractedQuotation] = None
    overall_decision: str = Field(description="'REJECT', 'NEEDS_A_PERSON_TO_CHECK', or 'APPROVE'")
    decision_reason: str = Field(default="", description="Summary of primary reason for decision")
    findings: List[RuleFinding] = Field(default_factory=list)
    rejection_findings: List[RuleFinding] = Field(default_factory=list)
    review_findings: List[RuleFinding] = Field(default_factory=list)
    compliance_findings: List[RuleFinding] = Field(default_factory=list)
    unverified_evidence: List[str] = Field(default_factory=list)
    audit_summary: str = Field(default="")

