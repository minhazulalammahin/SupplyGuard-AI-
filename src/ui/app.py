"""Streamlit Web Application for SupplyGuard AI."""
import os
import tempfile
from pathlib import Path
import pandas as pd
import streamlit as st

from src.config import DATA_DIR, is_gemini_available, GEMINI_MODEL
from src.workflow.graph import run_verification
from src.ui.components import render_decision_badge, render_findings_table

# Page Configuration
st.set_page_config(
    page_title="SupplyGuard AI | Document Verification System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("SupplyGuard AI")
    st.caption("AI-Powered Supplier Verification System")
    st.markdown("---")
    
    st.markdown("### System Status")
    ai_status = is_gemini_available()
    if ai_status:
        st.success(f"**Gemini API:** Connected\n\nModel: `{GEMINI_MODEL}`", icon="🟢")
    else:
        st.info("**Deterministic Rule Mode:** Active\n\n(Set `GEMINI_API_KEY` for live AI extraction)", icon="ℹ️")

    st.markdown("---")
    st.markdown("### ⚠️ Data Privacy Advisory")
    st.caption(
        "• **Gemini Free Tier:** May use prompts & completions to improve Google products; human reviewers may inspect data.\n"
        "• **Gemini Paid Tier:** Prompt data is **not** used to train models and remains confidential.\n"
        "• Always use a paid key for confidential procurement documents."
    )
    st.markdown("---")
    st.caption("Built for BIAI Recruitment Challenge • Aamar Garments Ltd")


# Main Dashboard
st.title("🛡️ SupplyGuard AI: Document Verification System")
st.markdown("Automated compliance verification of supplier quotation packs against PR benchmarks and company purchasing rules.")

tabs = st.tabs([
    "📄 Individual Pack Audit",
    "📊 Batch Evaluation Matrix (All 10 Packs)",
    "📈 Evaluation Report",
    "📋 Company Rules Reference"
])

# Tab 1: Individual Pack Audit
with tabs[0]:
    col_mode, col_file = st.columns([1, 2])
    with col_mode:
        source_mode = st.radio("Select Document Source:", ["Sample Supplier Packs (01-10)", "Upload Custom PDF"], horizontal=True)

    target_pdf_path = None
    if source_mode == "Sample Supplier Packs (01-10)":
        with col_file:
            sample_files = sorted(list(DATA_DIR.glob("supplier-pack-*.pdf")))
            sample_names = [f.name for f in sample_files]
            selected_pack = st.selectbox("Choose a Supplier Pack:", sample_names, index=0)
            if selected_pack:
                target_pdf_path = DATA_DIR / selected_pack
    else:
        with col_file:
            uploaded_file = st.file_uploader("Upload Supplier PDF Quotation:", type=["pdf"])
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    target_pdf_path = Path(tmp.name)

    if target_pdf_path and target_pdf_path.exists():
        if st.button("🚀 Run Verification Pipeline", type="primary"):
            with st.spinner("Processing document through LangGraph workflow..."):
                state = run_verification(str(target_pdf_path))
                st.session_state["last_result"] = state.verification_result
                st.session_state["last_state"] = state

    if "last_result" in st.session_state and st.session_state["last_result"]:
        res = st.session_state["last_result"]
        q = res.quotation
        pr = res.pr_item
        
        st.markdown("---")
        # Decision Banner
        render_decision_badge(res.overall_decision)
        st.markdown(f"**Audit Summary:** {res.decision_reason}")

        # Metrics row
        st.markdown("### 📊 Key Comparison Metrics")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Supplier", q.supplier_name if q else "Unknown")
        with m2:
            st.metric("Item Code", f"{q.item_code if q else 'N/A'} ({pr.description[:15]}...)" if pr else "N/A")
        with m3:
            price_delta = None
            if q and pr and q.unit_price and pr.maximum_unit_price:
                diff = ((q.unit_price - pr.maximum_unit_price) / pr.maximum_unit_price) * 100
                price_delta = f"{diff:+.2f}%"
            st.metric("Unit Price", f"BDT {q.unit_price}" if q else "N/A", delta=price_delta, delta_color="inverse")
        with m4:
            qty_delta = None
            if q and pr and q.quantity and pr.quantity_requested:
                q_diff = ((q.quantity - pr.quantity_requested) / pr.quantity_requested) * 100
                qty_delta = f"{q_diff:+.1f}%"
            st.metric("Quantity", f"{q.quantity:,}" if q else "N/A", delta=qty_delta)
        with m5:
            st.metric("Advance Required", f"{q.advance_payment_pct}%" if q else "N/A", delta="<= 20% limit")

        # Detail tabs
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🔎 Rule Violations & Findings", "📑 Extracted Data & Citations", "📄 Raw Document Text"])

        with sub_tab1:
            st.markdown(f"#### 🔴 Rejection Findings ({len(res.rejection_findings)})")
            render_findings_table(res.rejection_findings)

            st.markdown(f"#### 🟡 Human Review Triggers ({len(res.review_findings)})")
            render_findings_table(res.review_findings)

            st.markdown(f"#### 🟢 Compliant Rules ({len(res.compliance_findings)})")
            render_findings_table(res.compliance_findings)

        with sub_tab2:
            st.markdown("#### Structured Quotation Data")
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown("**Commercial Details:**")
                st.json({
                    "Quotation No": q.quotation_number if q else None,
                    "Date": q.quotation_date if q else None,
                    "PR Reference": q.pr_reference if q else None,
                    "Unit Price (BDT)": str(q.unit_price) if q else None,
                    "Quantity": str(q.quantity) if q else None,
                    "Subtotal (BDT)": str(q.subtotal) if q else None,
                    "VAT Rate": f"{q.vat_rate_pct}%" if q and q.vat_rate_pct else "Not Itemized",
                    "VAT Amount (BDT)": str(q.vat_amount) if q else None,
                    "Total Amount (BDT)": str(q.total_amount) if q else None,
                })
            with c_right:
                st.markdown("**Terms & Compliance:**")
                st.json({
                    "TIN": q.tin if q else None,
                    "BIN": q.bin if q else None,
                    "Advance Payment": f"{q.advance_payment_pct}%" if q else None,
                    "Payment Window": f"{q.payment_min_days} to {q.payment_max_days} days" if q and q.payment_min_days else "Unclear",
                    "Delivery Days": f"{q.delivery_promised_days} days" if q else None,
                    "Penalty Clause Present": q.has_late_delivery_penalty_clause if q else False,
                    "Penalty Rate": f"{q.late_delivery_penalty_pct_per_week}%/week" if q and q.late_delivery_penalty_pct_per_week else "None",
                    "Validity Days": f"{q.validity_days} days" if q else None,
                })

            st.markdown("#### 📜 Evidence Verification")
            quotes_data = []
            for eq in (q.evidence_quotes if q else []):
                quotes_data.append({
                    "Field": eq.field_name,
                    "Verified in PDF": "✅ Verified" if eq.is_verified else ("⚠️ Missing" if not eq.is_present else "❌ Unverified"),
                    "Exact Quote": eq.quote or "[ABSENT IN DOCUMENT]"
                })
            st.dataframe(pd.DataFrame(quotes_data), use_container_width=True)

        with sub_tab3:
            st.markdown("#### Raw Document Text (Extracted via PyMuPDF)")
            st.code(st.session_state["last_state"].full_text)

        # Human-In-The-Loop Section
        if res.overall_decision == "NEEDS_A_PERSON_TO_CHECK":
            st.markdown("---")
            st.markdown("### ✍️ Human Procurement Reviewer Sign-off")
            hitl_notes = st.text_area("Reviewer Assessment & Justification:", placeholder="Enter reason for approval or rejection override...")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ Approve with Policy Exception", type="primary"):
                    st.success(f"Quotation approved by Procurement Officer. Notes: {hitl_notes}")
            with col_b2:
                if st.button("❌ Reject Following Review"):
                    st.error(f"Quotation rejected by Procurement Officer. Notes: {hitl_notes}")

# Tab 2: Batch Matrix
with tabs[1]:
    st.markdown("### 📊 Automated Evaluation Matrix: All 10 Supplier Packs")
    st.caption("Executes the LangGraph verification workflow across all sample supplier packs to confirm system integrity.")

    if st.button("▶️ Run Batch Evaluation on All 10 Packs"):
        results_list = []
        progress_bar = st.progress(0)
        sample_files = sorted(list(DATA_DIR.glob("supplier-pack-*.pdf")))
        
        for idx, pdf in enumerate(sample_files):
            state = run_verification(str(pdf))
            r = state.verification_result
            results_list.append({
                "Pack ID": pdf.name,
                "Supplier": r.quotation.supplier_name if r.quotation else "N/A",
                "Item": r.pr_item.item_code if r.pr_item else "N/A",
                "Quoted Price": float(r.quotation.unit_price) if r.quotation and r.quotation.unit_price else None,
                "Max Price": float(r.pr_item.maximum_unit_price) if r.pr_item else None,
                "Decision": r.overall_decision,
                "Primary Finding": r.decision_reason
            })
            progress_bar.progress((idx + 1) / len(sample_files))

        df_batch = pd.DataFrame(results_list)
        st.dataframe(
            df_batch.style.map(
                lambda val: "background-color: #d4edda; color: #155724; font-weight: bold;" if val == "APPROVE"
                else ("background-color: #f8d7da; color: #721c24; font-weight: bold;" if val == "REJECT"
                else ("background-color: #fff3cd; color: #856404; font-weight: bold;" if val == "NEEDS_A_PERSON_TO_CHECK" else "")),
                subset=["Decision"]
            ),
            use_container_width=True
        )

# Tab 3: Evaluation Report
with tabs[2]:
    st.markdown("### 📈 Independent Verification & Accuracy Report")
    eval_file = Path(__file__).resolve().parent.parent.parent / "EVALUATION_REPORT.md"
    if eval_file.exists():
        st.markdown(eval_file.read_text())
    else:
        st.info("Evaluation report available in project root: EVALUATION_REPORT.md")

# Tab 4: Company Rules Reference
with tabs[3]:
    st.markdown("### 📜 Aamar Garments Ltd: Supplier Document Rules")
    rules_file = DATA_DIR / "company-rules.md"
    if rules_file.exists():
        st.markdown(rules_file.read_text())
    else:
        st.warning("company-rules.md not found.")

