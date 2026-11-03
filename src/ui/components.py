"""Reusable UI components for SupplyGuard AI Streamlit Dashboard."""
import streamlit as st
from src.models.schemas import VerificationResult, RuleFinding


def render_decision_badge(decision: str):
    """Render a prominent, colored status banner for the audit decision."""
    if decision == "APPROVE":
        st.success("### APPROVED\n**All compliance rules, commercial terms, pricing ceilings, and arithmetic verified.**", icon="✅")
    elif decision == "REJECT":
        st.error("### REJECTED\n**Critical policy violations detected. This quotation must be rejected.**", icon="❌")
    else:
        st.warning("### NEEDS A PERSON TO CHECK\n**Ambiguities, marginal variances, or non-standard terms require human procurement review.**", icon="⚠️")


def render_findings_table(findings: list[RuleFinding]):
    """Render a structured table of audit findings with supporting text."""
    if not findings:
        st.info("No findings in this category.")
        return

    for idx, f in enumerate(findings, 1):
        icon = "🔴" if f.category == "REJECT" else ("🟡" if f.category == "NEEDS_A_PERSON_TO_CHECK" else "🟢")
        with st.expander(f"{icon} [{f.rule_id}] {f.rule_name}", expanded=(f.category != "APPROVE")):
            st.markdown(f"**Explanation:** {f.description}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Observed Value:** `{f.observed_value or 'N/A'}`")
            with col2:
                st.markdown(f"**Expected / Baseline:** `{f.expected_value or 'N/A'}`")
            st.info(f"**Exact Document Citation:**\n> \"{f.evidence_text}\"")

