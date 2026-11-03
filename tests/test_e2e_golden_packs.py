"""End-to-End Regression Test Suite for all 10 sample supplier packs."""
from pathlib import Path
import pytest
from src.workflow.graph import run_verification

GOLDEN_EXPECTATIONS = [
    (
        "supplier-pack-01.pdf",
        "APPROVE",
        "Padma Textile Mills Ltd",
        "A",
        [],
        []
    ),
    (
        "supplier-pack-02.pdf",
        "APPROVE",
        "Jamuna Trims and Accessories",
        "B",
        [],
        []
    ),
    (
        "supplier-pack-03.pdf",
        "REJECT",
        "Karnaphuli Yarn Traders",
        "C",
        ["R1_PRICE_EXCESS"],
        []
    ),
    (
        "supplier-pack-04.pdf",
        "NEEDS_A_PERSON_TO_CHECK",
        "Surma Packaging Industries",
        "D",
        [],
        ["H1_PRICE_MARGINAL_EXCESS"]
    ),
    (
        "supplier-pack-05.pdf",
        "REJECT",
        "Meghna Carton Works",
        "E",
        ["R2_ADVANCE_PAYMENT"],
        []
    ),
    (
        "supplier-pack-06.pdf",
        "REJECT",
        "Teesta Fabrics Ltd",
        "A",
        ["R3_NO_PENALTY_CLAUSE"],
        []
    ),
    (
        "supplier-pack-07.pdf",
        "NEEDS_A_PERSON_TO_CHECK",
        "Rupsha Zipper Factory",
        "B",
        [],
        ["H2_QUANTITY_VARIANCE"]
    ),
    (
        "supplier-pack-08.pdf",
        "REJECT",
        "Bhairab Thread and Co",
        "C",
        ["R4_MISSING_TIN_BIN"],
        []
    ),
    (
        "supplier-pack-09.pdf",
        "NEEDS_A_PERSON_TO_CHECK",
        "Dhaleshwari Poly Pack",
        "D",
        [],
        ["H3_PAYMENT_TERMS_OUTSIDE_WINDOW", "H6_ARITHMETIC_ERROR"]
    ),
    (
        "supplier-pack-10.pdf",
        "REJECT",
        "Kushiyara Box Industries",
        "E",
        ["R5_LATE_DELIVERY"],
        ["H5_VAT_NOT_SEPARATED"]
    ),
]


@pytest.mark.parametrize(
    "filename,expected_decision,expected_supplier,expected_item,expected_reject_rules,expected_review_rules",
    GOLDEN_EXPECTATIONS
)
def test_golden_pack_evaluation(
    filename,
    expected_decision,
    expected_supplier,
    expected_item,
    expected_reject_rules,
    expected_review_rules
):
    """Verify that every supplier pack is audited with 100% agreement against ground-truth rules."""
    pdf_path = Path("data/sample") / filename
    assert pdf_path.exists(), f"File {pdf_path} not found"

    state = run_verification(str(pdf_path))
    res = state.verification_result

    # 1. Decision check
    assert res.overall_decision == expected_decision, (
        f"Decision mismatch for {filename}: expected {expected_decision}, got {res.overall_decision}. "
        f"Reason: {res.decision_reason}"
    )

    # 2. Supplier and Item check
    assert expected_supplier.lower() in res.quotation.supplier_name.lower()
    assert res.pr_item.item_code == expected_item

    # 3. Rule findings check
    actual_reject_ids = [f.rule_id for f in res.rejection_findings]
    actual_review_ids = [f.rule_id for f in res.review_findings]

    for exp_r in expected_reject_rules:
        assert exp_r in actual_reject_ids, f"Expected rejection rule {exp_r} in {actual_reject_ids} for {filename}"

    for exp_h in expected_review_rules:
        assert exp_h in actual_review_ids, f"Expected review rule {exp_h} in {actual_review_ids} for {filename}"

    # 4. Zero unverified citations check
    assert len(res.unverified_evidence) == 0, f"Unverified evidence found for {filename}: {res.unverified_evidence}"
