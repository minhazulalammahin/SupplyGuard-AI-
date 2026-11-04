"""Reusable UI components for SupplyGuard AI Streamlit Dashboard.

Includes:
- Decision Hero Banners
- KPI Cards
- Procurement Summary Cards
- Supplier Evaluation Data Tables (Zero Indent, Clean Semantic Classes)
- 7-Point Compliance Checklist
- Anti-Hallucination Document Evidence Cards
- Policy Findings List
"""
import html
import re
from typing import List, Dict, Any, Optional
import streamlit as st
from src.models.schemas import RuleFinding, ExtractedQuotation


def fmt_money(val: Optional[Any]) -> str:
    """Format monetary value safely as 'BDT X,XXX.XX' without raising formatting errors."""
    if val is None:
        return "BDT 0.00"
    try:
        f_val = float(val)
        return f"BDT {f_val:,.2f}"
    except (ValueError, TypeError):
        return f"BDT {val}"


def fmt_qty(val: Optional[Any], unit: Optional[str] = "") -> str:
    """Format quantity safely as 'X,XXX unit'."""
    if val is None:
        return "N/A"
    try:
        f_val = float(val)
        u_str = f" {unit}" if unit else ""
        if f_val.is_integer():
            return f"{int(f_val):,}{u_str}"
        return f"{f_val:,.2f}{u_str}"
    except (ValueError, TypeError):
        return f"{val} {unit}".strip()


def clean_reason(reason: str) -> str:
    """Strip internal technical rule IDs and prefixes to produce clean procurement English."""
    if not reason:
        return "No specific issues detected."
    cleaned = re.sub(r'^(REJECTED|NEEDS A PERSON TO CHECK|APPROVE)\s+under\s+[A-Za-z0-9_]+:\s*', '', reason, flags=re.IGNORECASE)
    cleaned = re.sub(r'^APPROVED:\s*', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def render_header(title: str, subtitle: str, badge_text: Optional[str] = None):
    """Render a modern SaaS page header with title, subtitle, and optional pill badge."""
    badge_html = f'<span class="sidebar-brand-badge" style="background: rgba(56, 189, 248, 0.12); padding: 4px 10px; border-radius: 9999px; border: 1px solid rgba(56, 189, 248, 0.25);">{badge_text}</span>' if badge_text else ''
    html_str = f"""<div style="margin-bottom: 1.5rem;">
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
<h1 style="margin: 0;">{title}</h1>
{badge_html}
</div>
<p style="margin: 0; color: var(--text-muted); font-size: 0.95rem; font-weight: 400;">{subtitle}</p>
</div>"""
    st.markdown(html_str, unsafe_allow_html=True)


def render_kpi_card(title: str, value: str, subtitle: str, status: str = "default") -> str:
    """Render a single KPI card with custom top-gradient border."""
    status_class = f"kpi-{status}" if status != "default" else ""
    return f"""<div class="kpi-card {status_class}">
<div class="kpi-label">{title}</div>
<div class="kpi-value">{value}</div>
<div class="kpi-subtitle">{subtitle}</div>
</div>"""


def render_decision_hero(decision: str, reason: str, pack_id: Optional[str] = None):
    """Render a large enterprise SaaS hero banner for the audit decision in plain English."""
    pack_label = f'<span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">Document: {pack_id}</span>' if pack_id else ''
    human_reason = clean_reason(reason)
    
    if decision == "APPROVE":
        hero_class = "decision-hero-approve"
        pill_class = "pill-approve"
        icon = "✓"
        badge_text = "APPROVED • FULLY COMPLIANT"
        headline = "Quotation Approved for Purchase Order"
        if not human_reason or "No specific" in human_reason:
            human_reason = "Quotation meets all pricing thresholds, payment requirements, delivery deadlines, and tax regulations. Ready for purchase order issuance."
    elif decision == "REJECT":
        hero_class = "decision-hero-reject"
        pill_class = "pill-reject"
        icon = "✕"
        badge_text = "REJECTED • POLICY VIOLATION"
        headline = "Quotation Rejected by Procurement Policy"
    else:
        hero_class = "decision-hero-review"
        pill_class = "pill-review"
        icon = "!"
        badge_text = "NEEDS A PERSON TO CHECK • EXCEPTION DETECTED"
        headline = "Requires Procurement Officer Review"

    html_str = f"""<div class="decision-hero {hero_class}">
<div>
<div class="decision-pill {pill_class}">
<span>{icon}</span> {badge_text}
</div>
<div class="decision-title">{headline}</div>
<div class="decision-desc">{human_reason}</div>
</div>
<div>
{pack_label}
</div>
</div>"""
    st.markdown(html_str, unsafe_allow_html=True)


def render_supplier_table(data_rows: List[Dict[str, Any]], is_batch: bool = False):
    """Render the clean supplier evaluation table.
    
    Required Columns:
    - Supplier Pack
    - Supplier Name
    - Product
    - Quoted Price
    - Price Variance
    - Decision
    - Main Reason
    - Details
    
    CRITICAL: Generates unindented HTML so markdown parser never treats rows as code blocks.
    Uses semantic classes so colors automatically adapt to Dark/Light themes.
    """
    if not data_rows:
        st.info("No supplier packs match the selected criteria.")
        return

    table_rows = []
    for row in data_rows:
        dec = row.get("decision", "APPROVE")
        if dec == "APPROVE":
            badge = '<span class="badge badge-pass">✓ APPROVED</span>'
        elif dec == "REJECT":
            badge = '<span class="badge badge-fail">✕ REJECTED</span>'
        else:
            badge = '<span class="badge badge-review">! NEEDS REVIEW</span>'

        v_pct = float(row.get("price_variance_pct", 0.0))
        if v_pct <= 0:
            v_color = "#10b981"
        elif v_pct > 3.0:
            v_color = "#ef4444"
        else:
            v_color = "#f59e0b"
        variance_str = f'<span style="color: {v_color}; font-weight: 600;">{v_pct:+.2f}%</span>'

        quoted_str = fmt_money(row.get("quoted_price", 0.0))
        item_label = f"Item {row.get('item_code', 'N/A')}: {row.get('item_desc', 'General Item')}"
        reason_text = clean_reason(row.get("reason", ""))
        
        # Details summary column
        adv = row.get("advance_pct", 0.0)
        days = row.get("delivery_days", None)
        deliv_str = f"{days}d" if days else "N/A"
        details_str = f'<span class="sg-col-details">Adv: {adv:.0f}% | Deliv: {deliv_str}</span>'

        # Build table row string with ZERO leading spaces on any line
        row_html = (
            '<tr>'
            f'<td class="sg-col-pack">{html.escape(str(row.get("pack_id", "")))}</td>'
            f'<td class="sg-col-supplier">{html.escape(str(row.get("supplier_name", "")))}</td>'
            f'<td class="sg-col-product">{html.escape(item_label)}</td>'
            f'<td class="sg-col-price">{quoted_str}</td>'
            f'<td>{variance_str}</td>'
            f'<td>{badge}</td>'
            f'<td class="sg-col-reason">{html.escape(reason_text[:65])}{"..." if len(reason_text) > 65 else ""}</td>'
            f'<td>{details_str}</td>'
            '</tr>'
        )
        table_rows.append(row_html)

    full_table_html = (
        '<div class="sg-table-container">'
        '<table class="sg-table">'
        '<thead>'
        '<tr>'
        '<th>Supplier Pack</th>'
        '<th>Supplier Name</th>'
        '<th>Product</th>'
        '<th>Quoted Price</th>'
        '<th>Price Variance</th>'
        '<th>Decision</th>'
        '<th>Main Reason</th>'
        '<th>Details</th>'
        '</tr>'
        '</thead>'
        '<tbody>'
        + "".join(table_rows) +
        '</tbody>'
        '</table>'
        '</div>'
    )
    st.markdown(full_table_html, unsafe_allow_html=True)


def render_compliance_checklist(findings: List[RuleFinding]):
    """Render the simplified 7-point corporate compliance checklist for procurement officers:
    
    1. Pricing: Passed / Failed / Needs Review
    2. Payment: Passed / Failed / Needs Review
    3. Delivery: Passed / Failed / Needs Review
    4. VAT: Passed / Failed / Needs Review
    5. Supplier TIN/BIN: Passed / Failed / Needs Review
    6. Late Delivery Penalty: Passed / Failed / Needs Review
    7. Arithmetic: Passed / Failed / Needs Review
    """
    categories = [
        {
            "id": "pricing",
            "title": "Pricing & Ceiling Threshold",
            "rule_prefix": ("R1", "H1", "H0"),
            "default_desc": "Quoted unit price is within the purchase request allowable price ceiling."
        },
        {
            "id": "payment",
            "title": "Payment Terms & Advance Limit",
            "rule_prefix": ("R2", "H3"),
            "default_desc": "Advance payment is 20% or less, and payment terms are specified within 30 to 60 days after delivery."
        },
        {
            "id": "delivery",
            "title": "Delivery Timeline",
            "rule_prefix": ("R5", "H4"),
            "default_desc": "Delivery is promised within 30 calendar days of purchase order (maximum allowable 45 days)."
        },
        {
            "id": "vat",
            "title": "VAT 15% Separation",
            "rule_prefix": ("H5",),
            "default_desc": "VAT is explicitly itemized as a separate 15% line item on the quotation."
        },
        {
            "id": "tin_bin",
            "title": "Supplier Tax ID (TIN & BIN)",
            "rule_prefix": ("R4",),
            "default_desc": "Supplier has provided valid Taxpayer Identification (TIN) and Business Identification (BIN) numbers."
        },
        {
            "id": "penalty",
            "title": "Late Delivery Penalty Clause",
            "rule_prefix": ("R3",),
            "default_desc": "Contract contains mandatory late-delivery penalty of at least 0.5% per week of delay."
        },
        {
            "id": "arithmetic",
            "title": "Arithmetic & Calculation Consistency",
            "rule_prefix": ("H6",),
            "default_desc": "Line item subtotals, VAT amounts, and total payable calculate correctly without rounding discrepancies."
        }
    ]

    cards_html = []
    for cat in categories:
        matched = [f for f in findings if any(f.rule_id.startswith(p) for p in cat["rule_prefix"])]
        
        status = "Passed"
        b_class = "badge-pass"
        b_icon = "✓ Passed"
        desc = cat["default_desc"]

        if matched:
            rejections = [f for f in matched if f.category == "REJECT"]
            reviews = [f for f in matched if f.category == "NEEDS_A_PERSON_TO_CHECK"]
            
            if rejections:
                status = "Failed"
                b_class = "badge-fail"
                b_icon = "✕ Failed"
                desc = rejections[0].description
            elif reviews:
                status = "Needs Review"
                b_class = "badge-review"
                b_icon = "! Needs Review"
                desc = reviews[0].description

        item_html = (
            '<div class="compliance-checklist-card">'
            '<div>'
            f'<div class="compliance-check-name">{html.escape(cat["title"])}</div>'
            f'<div class="compliance-check-desc">{html.escape(desc)}</div>'
            '</div>'
            '<div>'
            f'<span class="badge {b_class}">{b_icon}</span>'
            '</div>'
            '</div>'
        )
        cards_html.append(item_html)

    full_checklist_html = (
        '<div style="margin-bottom: 1rem;">'
        + "".join(cards_html) +
        '</div>'
    )
    st.markdown(full_checklist_html, unsafe_allow_html=True)


def render_evidence_table(quotation: ExtractedQuotation, filename: str):
    """Render document evidence in a clean, expandable format for procurement officers.
    
    Shows:
    - What the supplier document says (Field)
    - Exact supporting quotation
    - PDF filename
    - Page number
    - Evidence verification status
    """
    if not quotation or not quotation.evidence_quotes:
        st.info("No supporting evidence quotations recorded for this document.")
        return

    field_friendly_names = {
        "unit_price": "Quoted Unit Price",
        "quantity": "Quoted Quantity & Measurement Unit",
        "advance_payment": "Advance Payment Terms",
        "delivery_timeline": "Promised Delivery Schedule",
        "payment_terms": "Credit & Payment Period",
        "late_penalty": "Late-Delivery Delay Penalty Clause",
        "tin_bin": "Supplier TIN & BIN Tax Registration",
        "vat_itemization": "VAT 15% Separate Itemization",
        "validity_period": "Quotation Validity Window",
        "item_code": "PR Item Specification & Description",
        "total_amount": "Grand Total Payable Amount",
        "subtotal": "Subtotal Pre-Tax Amount"
    }

    cards_html = []
    for eq in quotation.evidence_quotes:
        f_name = field_friendly_names.get(eq.field_name, eq.field_name.replace("_", " ").title())
        
        if not eq.is_present:
            badge = '<span class="badge badge-fail">✕ CLAUSE MISSING IN PDF</span>'
            quote_text = "Clause or required detail is completely absent from the supplier document."
        elif eq.is_verified:
            badge = '<span class="badge badge-pass">✓ VERIFIED CITATION</span>'
            quote_text = eq.quote or "Document text verified."
        else:
            badge = '<span class="badge badge-review">! UNVERIFIED QUOTE</span>'
            quote_text = eq.quote or "Unverified citation."

        item_html = (
            '<div class="evidence-card">'
            '<div class="evidence-field-name">'
            f'<span>{html.escape(f_name)}</span>'
            '<div>'
            f'<span style="color: var(--text-muted); font-size: 0.72rem; margin-right: 8px;">Source: {html.escape(filename)} (Page {eq.page_number})</span>'
            f'{badge}'
            '</div>'
            '</div>'
            f'<div class="evidence-quote">"{html.escape(quote_text)}"</div>'
            '</div>'
        )
        cards_html.append(item_html)

    full_evidence_html = (
        '<div style="margin-bottom: 1rem;">'
        + "".join(cards_html) +
        '</div>'
    )
    st.markdown(full_evidence_html, unsafe_allow_html=True)


def render_findings_list(findings: List[RuleFinding], category: str):
    """Render findings grouped into clean cards with human-friendly plain English."""
    if not findings:
        st.markdown(
            '<div style="color: var(--text-muted); font-size: 0.85rem; font-style: italic; padding: 0.5rem 0;">No findings in this category.</div>',
            unsafe_allow_html=True
        )
        return

    badge_map = {
        "REJECT": ("badge-fail", "POLICY VIOLATION"),
        "NEEDS_A_PERSON_TO_CHECK": ("badge-review", "HUMAN REVIEW"),
        "APPROVE": ("badge-pass", "COMPLIANT")
    }
    b_class, b_label = badge_map.get(category, ("badge-neutral", category))

    cards_html = []
    for f in findings:
        obs_html = f'<div style="font-size: 0.78rem; color: var(--text-muted);"><strong style="color: var(--text-secondary);">Observed:</strong> <code>{html.escape(f.observed_value)}</code></div>' if f.observed_value else ''
        exp_html = f'<div style="font-size: 0.78rem; color: var(--text-muted);"><strong style="color: var(--text-secondary);">Requirement:</strong> <code>{html.escape(f.expected_value)}</code></div>' if f.expected_value else ''

        card_html = (
            '<div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 0.65rem;">'
            '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">'
            f'<div style="font-weight: 600; font-size: 0.88rem; color: var(--text-primary);"><span class="badge {b_class}" style="margin-right: 6px;">{b_label}</span>{html.escape(f.rule_name)}</div>'
            '</div>'
            f'<div style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 0.45rem;">{html.escape(f.description)}</div>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 0.45rem;">'
            f'{obs_html}{exp_html}'
            '</div>'
            '<div style="font-size: 0.73rem; color: var(--accent-cyan); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Supporting Text from PDF:</div>'
            f'<div class="evidence-quote">"{html.escape(f.evidence_text)}"</div>'
            '</div>'
        )
        cards_html.append(card_html)

    st.markdown("".join(cards_html), unsafe_allow_html=True)
