# SupplyGuard AI: Supplier Document Verification System

**SupplyGuard AI** is an AI-powered procurement document verification and audit system developed for the BIAI recruitment challenge (Aamar Garments Ltd scenario). It verifies supplier quotation documents against internal Purchase Requests (PRs) and company purchasing rules, combining **Gemini 2.5 Flash** for document information extraction with a **deterministic Python business rule engine** orchestrated via **LangGraph**.

---

## 🏛️ System Architecture

```
[Supplier PDF Document]
          │
          ▼ (PyMuPDF - Page-preserving Text Extraction)
[Raw Document Text & Citations]
          │
          ▼ (Gemini 2.5 Flash / Deterministic Fallback)
[Structured ExtractedQuotation (Pydantic with Decimal)]
          │
          ▼ (Anti-Hallucination Evidence Verifier)
[Evidence Verification Check (Substring & Absence Audit)]
          │
          ▼ (Purchase Request Baseline Loader via Pandas)
[PR-2026-114 Baseline Item Benchmark]
          │
          ▼ (Deterministic Python Business Rule Engine)
[Decision Evaluation: REJECT > HUMAN REVIEW > APPROVE]
          │
          ▼
[Streamlit Interactive Audit Dashboard & Human Sign-Off]
```

### Key Engineering Principles
1. **Decoupled AI & Deterministic Business Logic**:
   - The LLM (**Gemini 2.5 Flash**) is strictly used as an Information Extraction (IE) engine to parse unstructured PDF text into structured Pydantic models.
   - Company business rules, price thresholds, quantity deviations, arithmetic checks, and decision priority are **100% deterministic Python functions** using `Decimal` arithmetic.
2. **Strict Decision Priority**:
   $$\text{REJECT} \succ \text{NEEDS A PERSON TO CHECK} \succ \text{APPROVE}$$
   Uncertain extraction, missing critical fields, or unverifiable evidence never produce an automatic approval.
3. **Anti-Hallucination & Citation Grounding**:
   - Every extracted field records its exact verbatim citation from the PDF document.
   - An evidence verification layer cross-checks all snippets against the raw PyMuPDF text.
   - For absent clauses (such as a missing penalty clause in Pack 06 or missing TIN/BIN in Pack 08), the system records the absence as an explicit finding rather than inventing text.
4. **Data Privacy**:
   - Explicit advisory regarding Gemini API Free Tier (where prompt data may be used for model improvement) vs Paid Tier (confidential enterprise terms).

---

## 📊 Summary of Evaluation Results (All 10 Sample Packs)

| Pack ID | Supplier Name | PR Item | Quoted Price (BDT) | PR Max (BDT) | Decision | Rule Code | Primary Audit Finding |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **01** | Padma Textile Mills Ltd | A | 472.00 | 480.00 | **APPROVE** | Compliant | Fully compliant pricing, terms, 10% advance, 24-day delivery, 1% penalty. |
| **02** | Jamuna Trims and Accessories | B | 36.00 | 38.00 | **APPROVE** | Compliant | Fully compliant pricing, 0% advance, 21-day delivery, 0.75% penalty. |
| **03** | Karnaphuli Yarn Traders | C | 229.00 | 210.00 | **REJECT** | `R1_PRICE_EXCESS` | Quoted price (+9.05%) exceeds +3% allowable ceiling. |
| **04** | Surma Packaging Industries | D | 6.65 | 6.50 | **NEEDS REVIEW** | `H1_PRICE_MARGINAL_EXCESS` | Quoted price (+2.31%) exceeds max by $\le 3\%$. |
| **05** | Meghna Carton Works | E | 92.00 | 95.00 | **REJECT** | `R2_ADVANCE_PAYMENT` | Advance payment of 40% exceeds mandatory 20% limit. |
| **06** | Teesta Fabrics Ltd | A | 465.00 | 480.00 | **REJECT** | `R3_NO_PENALTY_CLAUSE` | Contract completely omits late-delivery penalty clause. |
| **07** | Rupsha Zipper Factory | B | 35.00 | 38.00 | **NEEDS REVIEW** | `H2_QUANTITY_VARIANCE` | Quoted quantity (16,500) differs from PR (20,000) by 17.50% (> 5%). |
| **08** | Bhairab Thread and Co | C | 205.00 | 210.00 | **REJECT** | `R4_MISSING_TIN_BIN` | TIN and BIN missing from quotation ("available on request"). |
| **09** | Dhaleshwari Poly Pack | D | 6.40 | 6.50 | **NEEDS REVIEW** | `H6_ARITHMETIC_ERROR`<br>`H3_PAYMENT_TERMS` | Math error ($50,000 \times 6.40 = 320,000 \ne 322,000$) & payment terms outside 30–60 days. |
| **10** | Kushiyara Box Industries | E | 94.00 | 95.00 | **REJECT** | `R5_LATE_DELIVERY` | Promised delivery in 60 days exceeds 45-day cutoff (Secondary: VAT not separated). |

---

## 🛠️ Project Setup & Installation

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/your-username/SupplyGuard-AI.git
cd SupplyGuard-AI

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables (Optional for Live Gemini AI)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*(Note: If `GEMINI_API_KEY` is not provided, SupplyGuard AI automatically operates in deterministic extraction mode, ensuring 100% full functionality and testability without an API key).*

---

## 🧪 Running Automated Tests

Run the full pytest suite covering rule engine boundary conditions, anti-hallucination verification, PDF extraction, Gemini error handling, and all 10 golden supplier packs:

```bash
pytest -v
```

Expected output:
```text
37 passed in 8.02s
```

---

## 🖥️ Launching the Streamlit Web Application

To launch the interactive dashboard:

```bash
streamlit run src/ui/app.py
```

The dashboard will open at `http://localhost:8501`, featuring:
- **Individual Pack Audit**: Interactive selector for all 10 supplier packs or custom PDF upload.
- **Key Comparison Metrics**: Price variance deltas, quantity deltas, advance percentages, and delivery schedules.
- **Audit Findings Breakdown**: Categorized by Rejections (🔴), Human Review Triggers (🟡), and Compliant Rules (🟢), citing exact verbatim document text.
- **Batch Evaluation Matrix**: One-click execution over all 10 sample supplier packs with an interactive colored status matrix.
- **Human-in-the-Loop Review**: Manual sign-off and note-logging for items requiring human procurement discretion.

---

## 📁 Repository Directory Structure

```
SupplyGuard-AI/
├── .env.example                  # Environment variable template
├── pyproject.toml                # Pytest configuration & pythonpath
├── requirements.txt              # Production and test dependencies
├── README.md                     # Documentation & setup instructions
├── data/
│   └── sample/                   # Supplied benchmark files
│       ├── company-rules.md
│       ├── purchase-request.csv
│       ├── README.md
│       └── supplier-pack-01.pdf ... supplier-pack-10.pdf
├── src/
│   ├── __init__.py
│   ├── config.py                 # Paths, environment configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py            # Pydantic models (Decimal precision, citations)
│   │   └── state.py              # LangGraph workflow state schema
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py         # PyMuPDF page-preserving extraction
│   │   ├── pr_repository.py      # Pandas PR baseline loader
│   │   ├── evidence_verifier.py  # Anti-hallucination substring verification
│   │   ├── gemini_extractor.py   # Gemini 2.5 Flash / deterministic fallback
│   │   └── rule_engine.py        # Deterministic Python rule validator
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── nodes.py              # LangGraph pipeline nodes
│   │   └── graph.py              # Compiled StateGraph definition
│   └── ui/
│       ├── __init__.py
│       ├── app.py                # Streamlit dashboard application
│       └── components.py         # UI audit badges, metrics, and cards
└── tests/
    ├── __init__.py
    ├── conftest.py               # Test configuration and fixtures
    ├── test_pdf_loader.py        # PyMuPDF extraction tests on all 10 PDFs
    ├── test_evidence_verifier.py # Anti-hallucination & quote verification tests
    ├── test_rule_engine.py       # Rule boundary condition tests (Decimal)
    ├── test_gemini_integration.py# Gemini API retries and malformed JSON tests
    └── test_e2e_golden_packs.py  # End-to-end regression on all 10 sample packs
```

