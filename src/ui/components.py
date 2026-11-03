"""Reusable UI components for SupplyGuard AI Streamlit Dashboard.

Includes:
- Decision Hero Banners
- KPI Cards
- Compliance Checklists
- Evidence Citation Cards
- Findings Accordions
- Rule Category Cards
"""
from typing import List, Dict, Any, Optional
import streamlit as st
from src.models.schemas import RuleFinding, ExtractedQuotation, PurchaseRequestItem


def render_header(title: str, subtitle: str, badge_text: Optional[str] = None):
    """Render a modern SaaS page header with title, subtitle, and optional pill badge."""
    badge_html = f'<span class="sidebar-brand-badge" style="background: rgba(56, 189, 248, 0.12); padding: 4px 10px; border-radius: 9999px; border: 1px solid rgba(56, 189, 248, 0.25);">{badge_text}</span>' if badge_text else ''
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
                <h1 style="margin: 0; color: #ffffff;">{title}</h1>
                {badge_html}
            </div>
            <p style="margin: 0; color: #94a3b8; font-size: 0.95rem; font-weight: 400;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_kpi_card(title: str, value: str, subtitle: str, status: str = "default"):
    """Render a single KPI card with custom top-gradient border."""
    status_class = f"kpi-{status}" if status != "default" else ""
    return f"""
    <div class="kpi-card {status_class}">
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """


def render_decision_hero(decision: str, reason: str, pack_id: Optional[str] = None):
    """Render a large enterprise SaaS hero banner for the audit decision."""
    pack_label = f'<span style="font-size: 0.85rem; color: #94a3b8; font-weight: 500;">Document: {pack_id}</span>' if pack_id else ''
    
    if decision == "APPROVE":
        hero_class = "decision-hero-approve"
        pill_class = "pill-approve"
        icon = "✓"
        badge_text = "APPROVED • FULLY COMPLIANT"
        headline = "Quotation Approved for Purchase Order"
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
        badge_text = "NEEDS HUMAN REVIEW • EXCEPTION DETECTED"
        headline = "Requires Procurement Officer Review"

    html = f"""
    <div class="decision-hero {hero_class}">
        <div>
            <div class="decision-pill {pill_class}">
                <span>{icon}</span> {badge_text}
            </div>
            <div class="decision-title">{headline}</div>
            <div class="decision-desc">{reason}</div>
        </div>
        <div>
            {pack_label}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_findings_list(findings: List[RuleFinding], category: str):
    """Render findings grouped into clean cards with exact verbatim citations."""
    if not findings:
        st.markdown(
            '<div style="color: #64748b; font-size: 0.85rem; font-style: italic; padding: 0.5rem 0;">No findings in this category.</div>',
            unsafe_allow_html=True
        )
        return

    badge_map = {
        "REJECT": ("badge-fail", "FAIL"),
        "NEEDS_A_PERSON_TO_CHECK": ("badge-review", "REVIEW"),
        "APPROVE": ("badge-pass", "PASS")
    }
    b_class, b_label = badge_map.get(category, ("badge-neutral", category))

    for f in findings:
        obs_html = f'<div style="font-size: 0.78rem; color: #94a3b8;"><strong style="color: #cbd5e1;">Observed:</strong> <code>{f.observed_value or "N/A"}</code></div>' if f.observed_value else ''
        exp_html = f'<div style="font-size: 0.78rem; color: #94a3b8;"><strong style="color: #cbd5e1;">Expected:</strong> <code>{f.expected_value or "N/A"}</code></div>' if f.expected_value else ''

        card_html = f"""
        <div style="background: #0f172a; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 0.65rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                <div style="font-weight: 600; font-size: 0.88rem; color: #ffffff;">
                    <span class="badge {b_class}" style="margin-right: 6px;">{b_label}</span>
                    [{f.rule_id}] {f.rule_name}
                </div>
            </div>
            <div style="font-size: 0.82rem; color: #cbd5e1; line-height: 1.4; margin-bottom: 0.45rem;">
                {f.description}
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 0.45rem;">
                {obs_html}
                {exp_html}
            </div>
            <div style="font-size: 0.75rem; color: #38bdf8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Exact Supporting Text:</div>
            <div class="evidence-quote">"{f.evidence_text}"</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)


def render_evidence_table(quotation: ExtractedQuotation, filename: str):
    """Render a clean enterprise evidence audit table showing verification status and page numbers."""
    if not quotation or not quotation.evidence_quotes:
        st.info("No evidence citations recorded.")
        return

    cards_html = []
    for eq in quotation.evidence_quotes:
        if not eq.is_present:
            status_badge = '<span class="badge badge-fail">NOT FOUND IN DOCUMENT</span>'
            quote_text = '[ABSENT IN DOCUMENT]'
        elif eq.is_verified:
            status_badge = '<span class="badge badge-pass">✓ VERIFIED CITATION</span>'
            quote_text = eq.quote or 'N/A'
        else:
            status_badge = '<span class="badge badge-review">⚠ UNVERIFIED QUOTE</span>'
            quote_text = eq.quote or 'N/A'

        item_html = f"""
        <div class="evidence-card">
            <div class="evidence-field-name">
                <span>{eq.field_name.replace('_', ' ')}</span>
                <div>
                    <span style="color: #64748b; font-size: 0.72rem; margin-right: 8px;">Source: {filename} (p. {eq.page_number})</span>
                    {status_badge}
                </div>
            </div>
            <div class="evidence-quote">"{quote_text}"</div>
        </div>
        """
        cards_html.append(item_html)

    st.markdown("".join(cards_html), unsafe_allow_html=True)


def render_compliance_checklist(findings: List[RuleFinding]):
    """Render a visual 2-column compliance matrix with PASS / FAIL / REVIEW badges."""
    rules_map = {
        "R1": ("Price Ceiling (+3% Max)", "Price does not exceed maximum by more than 3%"),
        "R2": ("Advance Payment (<= 20%)", "Advance payment required is 20% or less"),
        "R3": ("Late-Delivery Penalty", "Penalty clause present and rate >= 0.5% per week"),
        "R4": ("Tax Registration (TIN/BIN)", "Valid supplier TIN and BIN clearly stated"),
        "R5": ("Delivery Cutoff (<= 45 days)", "Delivery promised within 45 days of PO"),
        "H1": ("Marginal Price Tolerance", "Quoted price strictly within ceiling baseline"),
        "H2": ("Quantity Variance (<= 5%)", "Quoted quantity within +/- 5% of requested quantity"),
        "H3": ("Payment Window (30-60 days)", "Payment terms clearly specified within 30-60 days"),
        "H4": ("Rapid Delivery (<= 30 days)", "Delivery promised in 30 days or less"),
        "H5": ("15% VAT Separation", "VAT itemized separately at 15% rate"),
        "H6": ("Arithmetic Consistency", "Line amounts, VAT, and totals calculate correctly"),
        "H7": ("Quotation Validity (>= 30 days)", "Quotation validity period is at least 30 days")
    }

    results = {}
    for code, (name, desc) in rules_map.items():
        matched = [f for f in findings if f.rule_id.startswith(code)]
        if not matched:
            results[code] = ("PASS", "badge-pass", "✓ Compliant", desc)
        else:
            first = matched[0]
            if first.category == "REJECT":
                results[code] = ("FAIL", "badge-fail", "✕ Violation", first.description)
            elif first.category == "NEEDS_A_PERSON_TO_CHECK":
                results[code] = ("REVIEW", "badge-review", "! Check", first.description)
            else:
                results[code] = ("PASS", "badge-pass", "✓ Compliant", desc)

    col1, col2 = st.columns(2)
    keys = list(rules_map.keys())
    half = len(keys) // 2

    for col, chunk in [(col1, keys[:half]), (col2, keys[half:])]:
        with col:
            for k in chunk:
                status, b_class, b_text, desc = results[k]
                name = rules_map[k][0]
                item_html = f"""
                <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.65rem 0.85rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; font-size: 0.82rem; color: #e2e8f0;">{name}</div>
                        <div style="font-size: 0.72rem; color: #94a3b8; max-width: 380px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{desc}</div>
                    </div>
                    <div>
                        <span class="badge {b_class}">{b_text}</span>
                    </div>
                </div>
                """
                st.markdown(item_html, unsafe_allow_html=True)
