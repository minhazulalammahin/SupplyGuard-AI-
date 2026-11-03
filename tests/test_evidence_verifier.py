"""Unit tests for evidence verification and anti-hallucination validation."""
from decimal import Decimal
from src.models.schemas import ExtractedQuotation, EvidenceQuote
from src.services.evidence_verifier import (
    snippet_exists_in_text,
    verify_quotation_evidence
)


def test_snippet_exact_and_multiline_matching():
    """Verify substring matching handles linebreaks, tabs, and spaces."""
    doc_text = """Padma Textile Mills Ltd
QUOTATION
QT-2026-901
Item A Cotton twill fabric, 280 gsm
Qty: 12,000 metre Unit price: 472.00
1. Payment. 10% advance payable with the purchase order.
Balance payable within 45 days after delivery.
"""
    # Exact match
    assert snippet_exists_in_text("QT-2026-901", doc_text)
    assert snippet_exists_in_text("10% advance", doc_text)
    
    # Across line breaks
    assert snippet_exists_in_text("10% advance payable with the purchase order. Balance payable", doc_text)
    
    # Non-existent quote
    assert not snippet_exists_in_text("50% advance non-existent", doc_text)


def test_verify_quotation_evidence_detects_hallucinations():
    """Verify that hallucinated quotes are flagged as unverified."""
    doc_text = "Supplier TIN: 101458013391 BIN: 000170141-0101\nDelivery within 24 days."
    
    q = ExtractedQuotation(
        supplier_name="Padma",
        unit_price=Decimal("472.00"),
        evidence_quotes=[
            EvidenceQuote(field_name="tin", quote="TIN: 101458013391", is_present=True),
            EvidenceQuote(field_name="delivery", quote="Delivery in 5 days immediately", is_present=True),  # Hallucinated!
            EvidenceQuote(field_name="penalty", quote=None, is_present=False)  # Genuinely absent
        ]
    )
    
    verified_q, unverified = verify_quotation_evidence(q, doc_text)
    assert verified_q.evidence_quotes[0].is_verified is True
    assert verified_q.evidence_quotes[1].is_verified is False
    assert verified_q.evidence_quotes[2].is_verified is True  # Absent clause verified as absent
    assert len(unverified) == 1
    assert "delivery" in unverified[0]
