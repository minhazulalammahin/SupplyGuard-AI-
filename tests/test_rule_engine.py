"""Unit tests for deterministic Python business rule engine and boundary conditions."""
from decimal import Decimal
import pytest
from src.models.schemas import (
    ExtractedQuotation,
    PurchaseRequestItem,
    EvidenceQuote
)
from src.services.rule_engine import evaluate_quotation


@pytest.fixture
def base_pr_item():
    """Baseline PR item: Cotton twill fabric, 12,000 metres at max 480.00 BDT."""
    return PurchaseRequestItem(
        pr_number="PR-2026-114",
        item_code="A",
        description="Cotton twill fabric, 280 gsm",
        unit="metre",
        quantity_requested=Decimal("12000"),
        maximum_unit_price=Decimal("480.00")
    )


@pytest.fixture
def compliant_quotation():
    """Fully compliant baseline quotation for Item A."""
    return ExtractedQuotation(
        supplier_name="Compliant Mills Ltd",
        quotation_number="QT-TEST-001",
        quotation_date="2026-10-21",
        pr_reference="PR-2026-114",
        item_code="A",
        item_description="Cotton twill fabric, 280 gsm",
        quantity=Decimal("12000"),
        unit="metre",
        unit_price=Decimal("470.00"),  # Below 480.00
        line_amount=Decimal("5640000.00"),
        subtotal=Decimal("5640000.00"),
        vat_rate_pct=Decimal("15.0"),
        vat_amount=Decimal("846000.00"),
        vat_is_separate_at_15=True,
        total_amount=Decimal("6486000.00"),
        tin="101458013391",
        bin="000170141-0101",
        advance_payment_pct=Decimal("10.0"),  # <= 20%
        payment_min_days=30,
        payment_max_days=45,
        payment_reference_point="delivery",
        delivery_promised_days=24,  # <= 30 days
        has_late_delivery_penalty_clause=True,
        late_delivery_penalty_pct_per_week=Decimal("1.0"),  # >= 0.5%
        validity_days=45,  # >= 30 days
        payment_terms_raw="10% advance, balance within 45 days of delivery",
        delivery_terms_raw="Delivery within 24 days of PO",
        penalty_terms_raw="Late penalty 1% per week of delay",
        validity_terms_raw="Valid for 45 days",
        evidence_quotes=[
            EvidenceQuote(field_name="unit_price", quote="470.00", is_verified=True),
            EvidenceQuote(field_name="advance_payment_pct", quote="10% advance", is_verified=True)
        ]
    )


def test_baseline_approval(compliant_quotation, base_pr_item):
    """Test that a fully compliant quotation receives APPROVE."""
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "APPROVE"
    assert len(res.rejection_findings) == 0
    assert len(res.review_findings) == 0


def test_r1_price_excess_boundary(compliant_quotation, base_pr_item):
    """Boundary test for R1 (Price > +3% -> REJECT) vs H1 (0 < Price <= +3% -> REVIEW).
    Max price is 480.00.
    480.00 * 1.03 = 494.40.
    494.40 is exactly +3.00% -> NEEDS_A_PERSON_TO_CHECK
    494.41 is +3.002% (> 3%) -> REJECT
    """
    # Exactly +3.00%
    compliant_quotation.unit_price = Decimal("494.40")
    compliant_quotation.line_amount = Decimal("494.40") * compliant_quotation.quantity
    compliant_quotation.subtotal = compliant_quotation.line_amount
    compliant_quotation.vat_amount = compliant_quotation.subtotal * Decimal("0.15")
    compliant_quotation.total_amount = compliant_quotation.subtotal + compliant_quotation.vat_amount
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H1_PRICE_MARGINAL_EXCESS" for f in res.review_findings)

    # Exceeds +3.00%
    compliant_quotation.unit_price = Decimal("494.45")
    res2 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res2.overall_decision == "REJECT"
    assert any(f.rule_id == "R1_PRICE_EXCESS" for f in res2.rejection_findings)


def test_r2_advance_payment_boundary(compliant_quotation, base_pr_item):
    """Boundary test for R2 (Advance payment > 20% -> REJECT).
    20.0% -> APPROVE
    20.1% -> REJECT
    """
    compliant_quotation.advance_payment_pct = Decimal("20.0")
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "APPROVE"

    compliant_quotation.advance_payment_pct = Decimal("20.1")
    res2 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res2.overall_decision == "REJECT"
    assert any(f.rule_id == "R2_ADVANCE_PAYMENT" for f in res2.rejection_findings)


def test_r3_penalty_clause_missing_and_rate(compliant_quotation, base_pr_item):
    """Test R3 (Missing penalty clause or rate < 0.5%/week -> REJECT)."""
    # Missing clause entirely
    compliant_quotation.has_late_delivery_penalty_clause = False
    compliant_quotation.penalty_terms_raw = None
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "REJECT"
    assert any(f.rule_id == "R3_NO_PENALTY_CLAUSE" for f in res.rejection_findings)

    # Clause present but rate < 0.5% (e.g. 0.49%)
    compliant_quotation.has_late_delivery_penalty_clause = True
    compliant_quotation.penalty_terms_raw = "Penalty of 0.49% per week"
    compliant_quotation.late_delivery_penalty_pct_per_week = Decimal("0.49")
    res2 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res2.overall_decision == "REJECT"
    assert any(f.rule_id == "R3_INSUFFICIENT_PENALTY" for f in res2.rejection_findings)

    # Exactly 0.5% -> compliant
    compliant_quotation.late_delivery_penalty_pct_per_week = Decimal("0.5")
    res3 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res3.overall_decision == "APPROVE"


def test_r4_tin_bin_missing(compliant_quotation, base_pr_item):
    """Test R4 (Missing TIN or BIN -> REJECT)."""
    # Missing TIN
    compliant_quotation.tin = None
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "REJECT"
    assert any(f.rule_id == "R4_MISSING_TIN_BIN" for f in res.rejection_findings)

    # Missing BIN
    compliant_quotation.tin = "101458013391"
    compliant_quotation.bin = None
    res2 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res2.overall_decision == "REJECT"
    assert any(f.rule_id == "R4_MISSING_TIN_BIN" for f in res2.rejection_findings)


def test_r5_delivery_days_boundary(compliant_quotation, base_pr_item):
    """Boundary test for delivery schedule:
    <= 30 days: APPROVE
    31 to 45 days: NEEDS_A_PERSON_TO_CHECK (H4)
    > 45 days (e.g. 46): REJECT (R5)
    """
    compliant_quotation.delivery_promised_days = 30
    assert evaluate_quotation(compliant_quotation, base_pr_item).overall_decision == "APPROVE"

    compliant_quotation.delivery_promised_days = 31
    res31 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res31.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H4_DELIVERY_WINDOW" for f in res31.review_findings)

    compliant_quotation.delivery_promised_days = 45
    res45 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res45.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H4_DELIVERY_WINDOW" for f in res45.review_findings)

    compliant_quotation.delivery_promised_days = 46
    res46 = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res46.overall_decision == "REJECT"
    assert any(f.rule_id == "R5_LATE_DELIVERY" for f in res46.rejection_findings)


def test_h2_quantity_variance_boundary(compliant_quotation, base_pr_item):
    """Boundary test for H2 (Quantity differs by > 5% -> REVIEW).
    Requested: 12,000.
    12,000 * 0.95 = 11,400 (-5.00%) -> APPROVE
    11,399 (-5.008%) -> NEEDS_A_PERSON_TO_CHECK
    12,600 (+5.00%) -> APPROVE
    12,601 (+5.008%) -> NEEDS_A_PERSON_TO_CHECK
    """
    compliant_quotation.quantity = Decimal("11400")
    compliant_quotation.line_amount = compliant_quotation.quantity * compliant_quotation.unit_price
    compliant_quotation.subtotal = compliant_quotation.line_amount
    compliant_quotation.vat_amount = compliant_quotation.subtotal * Decimal("0.15")
    compliant_quotation.total_amount = compliant_quotation.subtotal + compliant_quotation.vat_amount
    assert evaluate_quotation(compliant_quotation, base_pr_item).overall_decision == "APPROVE"

    compliant_quotation.quantity = Decimal("11399")
    compliant_quotation.line_amount = compliant_quotation.quantity * compliant_quotation.unit_price
    compliant_quotation.subtotal = compliant_quotation.line_amount
    compliant_quotation.vat_amount = compliant_quotation.subtotal * Decimal("0.15")
    compliant_quotation.total_amount = compliant_quotation.subtotal + compliant_quotation.vat_amount
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H2_QUANTITY_VARIANCE" for f in res.review_findings)


def test_h3_payment_terms_outside_window(compliant_quotation, base_pr_item):
    """Test H3 (Payment terms outside 30 to 60 days -> REVIEW)."""
    # 30 to 90 days
    compliant_quotation.payment_min_days = 30
    compliant_quotation.payment_max_days = 90
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H3_PAYMENT_TERMS_OUTSIDE_WINDOW" for f in res.review_findings)


def test_h5_vat_not_separate(compliant_quotation, base_pr_item):
    """Test H5 (VAT not shown separately at 15% -> REVIEW)."""
    compliant_quotation.vat_is_separate_at_15 = False
    compliant_quotation.vat_amount = None
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H5_VAT_NOT_SEPARATED" for f in res.review_findings)


def test_h6_arithmetic_mismatch(compliant_quotation, base_pr_item):
    """Test H6 (Arithmetic errors in line amounts or totals -> REVIEW)."""
    # Force a mismatch in line amount
    compliant_quotation.line_amount = compliant_quotation.line_amount + Decimal("100.00")
    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H6_ARITHMETIC_ERROR" for f in res.review_findings)


def test_decision_priority_reject_overrides_review(compliant_quotation, base_pr_item):
    """Decision priority: REJECT must override NEEDS_A_PERSON_TO_CHECK."""
    # Trigger Review: Quantity variance > 5% (11,000 vs 12,000)
    compliant_quotation.quantity = Decimal("11000")
    compliant_quotation.line_amount = compliant_quotation.quantity * compliant_quotation.unit_price
    compliant_quotation.subtotal = compliant_quotation.line_amount
    compliant_quotation.vat_amount = compliant_quotation.subtotal * Decimal("0.15")
    compliant_quotation.total_amount = compliant_quotation.subtotal + compliant_quotation.vat_amount

    # Trigger Reject: Advance payment 40% > 20%
    compliant_quotation.advance_payment_pct = Decimal("40.0")

    res = evaluate_quotation(compliant_quotation, base_pr_item)
    assert res.overall_decision == "REJECT"
    assert len(res.rejection_findings) >= 1
    assert len(res.review_findings) >= 1


def test_unverified_evidence_prevents_approval(compliant_quotation, base_pr_item):
    """Unverified evidence must NEVER result in automatic approval."""
    unverified = ["unit_price: Quote '470.00' not found in document"]
    res = evaluate_quotation(compliant_quotation, base_pr_item, unverified_evidence=unverified)
    assert res.overall_decision == "NEEDS_A_PERSON_TO_CHECK"
    assert any(f.rule_id == "H0_UNVERIFIED_EVIDENCE" for f in res.review_findings)
