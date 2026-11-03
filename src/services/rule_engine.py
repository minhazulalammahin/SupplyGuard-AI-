"""Deterministic Python Business Rule Engine for SupplyGuard AI."""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Tuple
from src.models.schemas import (
    ExtractedQuotation,
    PurchaseRequestItem,
    RuleFinding,
    VerificationResult,
)


def evaluate_quotation(
    quotation: ExtractedQuotation,
    pr_item: PurchaseRequestItem,
    filename: str = "",
    unverified_evidence: Optional[List[str]] = None
) -> VerificationResult:
    """Evaluate a supplier quotation deterministically against company rules and PR specifications.
    
    Decision priority:
        REJECT > NEEDS_A_PERSON_TO_CHECK > APPROVE
    """
    rejections: List[RuleFinding] = []
    reviews: List[RuleFinding] = []
    compliances: List[RuleFinding] = []
    unverified_list = unverified_evidence or []

    # -------------------------------------------------------------
    # 0. Evidence verification / Missing data safety check
    # -------------------------------------------------------------
    if unverified_list:
        reviews.append(
            RuleFinding(
                rule_id="H0_UNVERIFIED_EVIDENCE",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Unverifiable Evidence Citation",
                description=f"Evidence text could not be verified in the document: {', '.join(unverified_list)}",
                evidence_text="[EVIDENCE VERIFICATION FAILED]",
                observed_value=str(len(unverified_list)),
                expected_value="0 unverified fields",
                is_violation=True
            )
        )

    # -------------------------------------------------------------
    # REJECTION RULE 1 & HUMAN REVIEW RULE 1: Unit Price
    # -------------------------------------------------------------
    if quotation.unit_price is None:
        reviews.append(
            RuleFinding(
                rule_id="H0_MISSING_PRICE",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Missing Quoted Price",
                description="Quoted unit price is missing from document.",
                evidence_text="[MISSING IN DOCUMENT]",
                is_violation=True
            )
        )
    else:
        max_price = pr_item.maximum_unit_price
        quoted_price = quotation.unit_price
        diff_pct = ((quoted_price - max_price) / max_price) * Decimal("100.0")
        diff_pct_rounded = diff_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        price_evidence = next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "unit_price"), f"{quoted_price}") or f"{quoted_price}"

        if diff_pct > Decimal("3.0"):
            rejections.append(
                RuleFinding(
                    rule_id="R1_PRICE_EXCESS",
                    category="REJECT",
                    rule_name="Unit Price > 3% Above Maximum",
                    description=f"Quoted unit price BDT {quoted_price} is {diff_pct_rounded}% above maximum allowable BDT {max_price} (exceeds +3% limit).",
                    evidence_text=f"Unit price (BDT): {price_evidence}",
                    observed_value=f"{quoted_price} BDT (+{diff_pct_rounded}%)",
                    expected_value=f"<= {max_price} BDT (+3% max = {max_price * Decimal('1.03'):.2f} BDT)",
                    is_violation=True
                )
            )
        elif diff_pct > Decimal("0.0"):
            reviews.append(
                RuleFinding(
                    rule_id="H1_PRICE_MARGINAL_EXCESS",
                    category="NEEDS_A_PERSON_TO_CHECK",
                    rule_name="Unit Price Above Maximum by <= 3%",
                    description=f"Quoted unit price BDT {quoted_price} is {diff_pct_rounded}% above baseline maximum BDT {max_price} (within acceptable +3% human-review margin).",
                    evidence_text=f"Unit price (BDT): {price_evidence}",
                    observed_value=f"{quoted_price} BDT (+{diff_pct_rounded}%)",
                    expected_value=f"<= {max_price} BDT",
                    is_violation=True
                )
            )
        else:
            compliances.append(
                RuleFinding(
                    rule_id="C1_PRICE_COMPLIANT",
                    category="APPROVE",
                    rule_name="Unit Price Compliant",
                    description=f"Quoted unit price BDT {quoted_price} complies with ceiling BDT {max_price}.",
                    evidence_text=f"Unit price (BDT): {price_evidence}",
                    observed_value=f"{quoted_price} BDT",
                    expected_value=f"<= {max_price} BDT",
                    is_violation=False
                )
            )

    # -------------------------------------------------------------
    # REJECTION RULE 2: Advance Payment (> 20%)
    # -------------------------------------------------------------
    adv_pct = quotation.advance_payment_pct if quotation.advance_payment_pct is not None else Decimal("0.0")
    pay_evidence = quotation.payment_terms_raw or next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "advance_payment_pct"), "") or ""

    if adv_pct > Decimal("20.0"):
        rejections.append(
            RuleFinding(
                rule_id="R2_ADVANCE_PAYMENT",
                category="REJECT",
                rule_name="Advance Payment Exceeds 20%",
                description=f"Supplier demands {adv_pct}% advance payment, which exceeds the company maximum limit of 20%.",
                evidence_text=pay_evidence,
                observed_value=f"{adv_pct}% advance",
                expected_value="<= 20% advance",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C2_ADVANCE_COMPLIANT",
                category="APPROVE",
                rule_name="Advance Payment Compliant",
                description=f"Advance payment {adv_pct}% is within permissible ceiling (<= 20%).",
                evidence_text=pay_evidence,
                observed_value=f"{adv_pct}% advance",
                expected_value="<= 20%",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # REJECTION RULE 3: Late Delivery Penalty Clause Missing or < 0.5%
    # -------------------------------------------------------------
    pen_evidence = quotation.penalty_terms_raw or next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "late_delivery_penalty_pct_per_week"), None)

    if not quotation.has_late_delivery_penalty_clause or pen_evidence is None or quotation.late_delivery_penalty_pct_per_week is None:
        rejections.append(
            RuleFinding(
                rule_id="R3_NO_PENALTY_CLAUSE",
                category="REJECT",
                rule_name="Missing Late-Delivery Penalty Clause",
                description="Contract contains no late-delivery penalty clause.",
                evidence_text="[CLAUSE ABSENT FROM TERMS AND CONDITIONS]",
                observed_value="None",
                expected_value="Penalty clause of at least 0.5% per week of delay",
                is_violation=True
            )
        )
    elif quotation.late_delivery_penalty_pct_per_week < Decimal("0.5"):
        rejections.append(
            RuleFinding(
                rule_id="R3_INSUFFICIENT_PENALTY",
                category="REJECT",
                rule_name="Insufficient Late-Delivery Penalty Rate",
                description=f"Late delivery penalty rate is {quotation.late_delivery_penalty_pct_per_week}%/week, which is below the mandatory 0.5%/week minimum.",
                evidence_text=pen_evidence,
                observed_value=f"{quotation.late_delivery_penalty_pct_per_week}%/week",
                expected_value=">= 0.5% per week",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C3_PENALTY_COMPLIANT",
                category="APPROVE",
                rule_name="Late-Delivery Penalty Compliant",
                description=f"Late delivery penalty of {quotation.late_delivery_penalty_pct_per_week}% per week meets policy requirements.",
                evidence_text=pen_evidence,
                observed_value=f"{quotation.late_delivery_penalty_pct_per_week}%/week",
                expected_value=">= 0.5%/week",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # REJECTION RULE 4: Missing TIN or BIN
    # -------------------------------------------------------------
    tin_bin_evidence = quotation.tin_bin_raw or next((eq.quote for eq in quotation.evidence_quotes if eq.field_name in ("tin", "bin")), None)

    if not quotation.tin or not quotation.bin:
        rejections.append(
            RuleFinding(
                rule_id="R4_MISSING_TIN_BIN",
                category="REJECT",
                rule_name="Supplier TIN or BIN Missing",
                description="Supplier failed to state mandatory TIN or BIN registration details on quotation.",
                evidence_text=tin_bin_evidence or "[REGISTRATION DETAILS MISSING]",
                observed_value=f"TIN: {quotation.tin or 'MISSING'}, BIN: {quotation.bin or 'MISSING'}",
                expected_value="Both valid TIN and BIN must be stated",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C4_TIN_BIN_COMPLIANT",
                category="APPROVE",
                rule_name="Tax Registration Compliant",
                description=f"Valid TIN ({quotation.tin}) and BIN ({quotation.bin}) present.",
                evidence_text=tin_bin_evidence or f"TIN: {quotation.tin} BIN: {quotation.bin}",
                observed_value=f"TIN: {quotation.tin}, BIN: {quotation.bin}",
                expected_value="Valid TIN and BIN",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # REJECTION RULE 5 & HUMAN REVIEW RULE 4: Delivery Window
    # -------------------------------------------------------------
    del_days = quotation.delivery_promised_days
    del_evidence = quotation.delivery_terms_raw or next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "delivery_promised_days"), "") or ""

    if del_days is None:
        reviews.append(
            RuleFinding(
                rule_id="H0_MISSING_DELIVERY",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Missing Delivery Schedule",
                description="Promised delivery schedule is missing or unparseable.",
                evidence_text=del_evidence or "[MISSING IN DOCUMENT]",
                is_violation=True
            )
        )
    elif del_days > 45:
        rejections.append(
            RuleFinding(
                rule_id="R5_LATE_DELIVERY",
                category="REJECT",
                rule_name="Delivery Promised Later than 45 Days",
                description=f"Promised delivery period is {del_days} days after PO, which exceeds the mandatory 45-day cutoff.",
                evidence_text=del_evidence,
                observed_value=f"{del_days} days",
                expected_value="<= 45 days after PO",
                is_violation=True
            )
        )
    elif 31 <= del_days <= 45:
        reviews.append(
            RuleFinding(
                rule_id="H4_DELIVERY_WINDOW",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Delivery Promised in 31 to 45 Days",
                description=f"Promised delivery is {del_days} days (falls in the 31-45 days window requiring operational check).",
                evidence_text=del_evidence,
                observed_value=f"{del_days} days",
                expected_value="<= 30 days for automatic approval",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C5_DELIVERY_COMPLIANT",
                category="APPROVE",
                rule_name="Delivery Schedule Compliant",
                description=f"Promised delivery in {del_days} days satisfies rapid fulfillment criteria (<= 30 days).",
                evidence_text=del_evidence,
                observed_value=f"{del_days} days",
                expected_value="<= 30 days",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # HUMAN REVIEW RULE 2: Quantity Variance (> 5%)
    # -------------------------------------------------------------
    if quotation.quantity is None:
        reviews.append(
            RuleFinding(
                rule_id="H0_MISSING_QUANTITY",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Missing Quoted Quantity",
                description="Quoted quantity is missing from document.",
                evidence_text="[MISSING IN DOCUMENT]",
                is_violation=True
            )
        )
    else:
        req_qty = pr_item.quantity_requested
        quoted_qty = quotation.quantity
        qty_diff = abs(quoted_qty - req_qty)
        qty_diff_pct = (qty_diff / req_qty) * Decimal("100.0")
        qty_diff_pct_rounded = qty_diff_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        qty_evidence = next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "quantity"), f"{quoted_qty}") or f"{quoted_qty}"

        if qty_diff_pct > Decimal("5.0"):
            reviews.append(
                RuleFinding(
                    rule_id="H2_QUANTITY_VARIANCE",
                    category="NEEDS_A_PERSON_TO_CHECK",
                    rule_name="Quantity Differs by > 5%",
                    description=f"Quoted quantity of {quoted_qty:,} {pr_item.unit} differs from requested {req_qty:,} {pr_item.unit} by {qty_diff_pct_rounded}% (exceeds allowable +/- 5% variance).",
                    evidence_text=f"Qty: {qty_evidence}",
                    observed_value=f"{quoted_qty:,} {pr_item.unit} (diff: {qty_diff_pct_rounded}%)",
                    expected_value=f"{req_qty:,} {pr_item.unit} (+/- 5% window: {req_qty * Decimal('0.95'):,} to {req_qty * Decimal('1.05'):,})",
                    is_violation=True
                )
            )
        else:
            compliances.append(
                RuleFinding(
                    rule_id="C6_QUANTITY_COMPLIANT",
                    category="APPROVE",
                    rule_name="Quantity Compliant",
                    description=f"Quoted quantity {quoted_qty:,} matches requested {req_qty:,} within 5% tolerance.",
                    evidence_text=f"Qty: {qty_evidence}",
                    observed_value=f"{quoted_qty:,}",
                    expected_value=f"{req_qty:,}",
                    is_violation=False
                )
            )

    # -------------------------------------------------------------
    # HUMAN REVIEW RULE 3: Payment Terms (Unclear or Outside 30-60 Days)
    # -------------------------------------------------------------
    min_days = quotation.payment_min_days
    max_days = quotation.payment_max_days

    if min_days is None or max_days is None:
        reviews.append(
            RuleFinding(
                rule_id="H3_PAYMENT_TERMS_UNCLEAR",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Unclear Payment Term Schedule",
                description="Payment duration or timeline is unspecified or ambiguous.",
                evidence_text=pay_evidence or "[PAYMENT CLAUSE UNCLEAR]",
                observed_value="Unclear payment schedule",
                expected_value="30 to 60 days after delivery",
                is_violation=True
            )
        )
    elif min_days < 30 or max_days > 60:
        reviews.append(
            RuleFinding(
                rule_id="H3_PAYMENT_TERMS_OUTSIDE_WINDOW",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Payment Terms Outside 30–60 Days",
                description=f"Payment terms ({min_days} to {max_days} days) extend outside standard 30 to 60 days after delivery window.",
                evidence_text=pay_evidence,
                observed_value=f"{min_days} to {max_days} days",
                expected_value="Between 30 and 60 days after delivery",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C7_PAYMENT_TERMS_COMPLIANT",
                category="APPROVE",
                rule_name="Payment Terms Compliant",
                description=f"Payment terms of {min_days} to {max_days} days are within standard 30–60 days window.",
                evidence_text=pay_evidence,
                observed_value=f"{min_days} to {max_days} days",
                expected_value="30 to 60 days",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # HUMAN REVIEW RULE 5: VAT Shown Separately at 15%
    # -------------------------------------------------------------
    vat_evidence = quotation.tax_terms_raw or next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "vat_amount"), "") or ""

    if not quotation.vat_is_separate_at_15 or quotation.vat_rate_pct != Decimal("15.0") or quotation.vat_amount is None:
        reviews.append(
            RuleFinding(
                rule_id="H5_VAT_NOT_SEPARATED",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="VAT Not Shown Separately at 15%",
                description="VAT is not itemized as a separate 15% line item in the quotation.",
                evidence_text=vat_evidence or "[NO SEPARATE 15% VAT LINE]",
                observed_value=f"VAT separate: {quotation.vat_is_separate_at_15}, rate: {quotation.vat_rate_pct}%",
                expected_value="Explicit separate line item for VAT at 15%",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C8_VAT_COMPLIANT",
                category="APPROVE",
                rule_name="VAT Itemization Compliant",
                description=f"VAT is properly itemized separately at 15% (BDT {quotation.vat_amount:,}).",
                evidence_text=vat_evidence,
                observed_value=f"VAT 15% = BDT {quotation.vat_amount:,}",
                expected_value="Itemized 15% VAT",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # HUMAN REVIEW RULE 6: Numbers Do Not Add Up (Math Error)
    # -------------------------------------------------------------
    math_errors = []
    
    if quotation.quantity and quotation.unit_price and quotation.line_amount:
        expected_line = (quotation.quantity * quotation.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if abs(expected_line - quotation.line_amount) > Decimal("0.05"):
            math_errors.append(
                f"Line total mismatch: {quotation.quantity:,} * {quotation.unit_price} = BDT {expected_line:,}, but document states BDT {quotation.line_amount:,}"
            )

    if quotation.subtotal and quotation.vat_amount and quotation.vat_is_separate_at_15:
        expected_vat = (quotation.subtotal * Decimal("0.15")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if abs(expected_vat - quotation.vat_amount) > Decimal("0.05"):
            math_errors.append(
                f"VAT calculation mismatch: 15% of subtotal BDT {quotation.subtotal:,} is BDT {expected_vat:,}, but document states BDT {quotation.vat_amount:,}"
            )

    if quotation.subtotal and quotation.vat_amount and quotation.total_amount:
        expected_total = (quotation.subtotal + quotation.vat_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if abs(expected_total - quotation.total_amount) > Decimal("0.05"):
            math_errors.append(
                f"Grand total mismatch: Subtotal + VAT is BDT {expected_total:,}, but document states BDT {quotation.total_amount:,}"
            )

    if math_errors:
        reviews.append(
            RuleFinding(
                rule_id="H6_ARITHMETIC_ERROR",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Numbers Do Not Add Up",
                description="; ".join(math_errors),
                evidence_text=f"Line amount: {quotation.line_amount}, Subtotal: {quotation.subtotal}, VAT: {quotation.vat_amount}, Total: {quotation.total_amount}",
                observed_value="Arithmetic inconsistency detected",
                expected_value="Exact mathematical consistency",
                is_violation=True
            )
        )
    else:
        compliances.append(
            RuleFinding(
                rule_id="C9_ARITHMETIC_COMPLIANT",
                category="APPROVE",
                rule_name="Arithmetic Consistency Verified",
                description="All line totals, subtotals, VAT, and grand totals calculate correctly.",
                evidence_text=f"Total: BDT {quotation.total_amount:,}" if quotation.total_amount else "Verified",
                observed_value="Exact match",
                expected_value="Exact match",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # HUMAN REVIEW RULE 7: Quotation Validity (< 30 Days)
    # -------------------------------------------------------------
    val_evidence = quotation.validity_terms_raw or next((eq.quote for eq in quotation.evidence_quotes if eq.field_name == "validity_days"), "") or ""

    if quotation.validity_days is not None and quotation.validity_days < 30:
        reviews.append(
            RuleFinding(
                rule_id="H7_SHORT_VALIDITY",
                category="NEEDS_A_PERSON_TO_CHECK",
                rule_name="Quotation Validity < 30 Days",
                description=f"Quotation validity is {quotation.validity_days} days (less than standard 30-day minimum).",
                evidence_text=val_evidence,
                observed_value=f"{quotation.validity_days} days",
                expected_value=">= 30 days validity",
                is_violation=True
            )
        )
    elif quotation.validity_days is not None:
        compliances.append(
            RuleFinding(
                rule_id="C10_VALIDITY_COMPLIANT",
                category="APPROVE",
                rule_name="Quotation Validity Compliant",
                description=f"Quotation is valid for {quotation.validity_days} days (>= 30 days).",
                evidence_text=val_evidence,
                observed_value=f"{quotation.validity_days} days",
                expected_value=">= 30 days",
                is_violation=False
            )
        )

    # -------------------------------------------------------------
    # DECISION PRIORITY RESOLUTION
    # REJECT > NEEDS_A_PERSON_TO_CHECK > APPROVE
    # -------------------------------------------------------------
    if rejections:
        overall_decision = "REJECT"
        primary_finding = rejections[0]
        decision_reason = f"REJECTED under {primary_finding.rule_id}: {primary_finding.description}"
    elif reviews:
        overall_decision = "NEEDS_A_PERSON_TO_CHECK"
        primary_finding = reviews[0]
        decision_reason = f"NEEDS A PERSON TO CHECK under {primary_finding.rule_id}: {primary_finding.description}"
    else:
        overall_decision = "APPROVE"
        decision_reason = "APPROVED: All pricing, commercial terms, delivery schedules, tax, and arithmetic rules are fully compliant."

    all_findings = rejections + reviews + compliances

    audit_summary = (
        f"DECISION: {overall_decision}\n"
        f"Primary Reason: {decision_reason}\n"
        f"Total Rejections: {len(rejections)} | Reviews: {len(reviews)} | Compliances: {len(compliances)}"
    )

    return VerificationResult(
        filename=filename,
        pr_item=pr_item,
        quotation=quotation,
        overall_decision=overall_decision,
        decision_reason=decision_reason,
        findings=all_findings,
        rejection_findings=rejections,
        review_findings=reviews,
        compliance_findings=compliances,
        unverified_evidence=unverified_list,
        audit_summary=audit_summary
    )
