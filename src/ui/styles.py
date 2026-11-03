"""Enterprise UI Theme and Custom CSS for SupplyGuard AI.

Inspired by Linear, Stripe, and Vercel:
- Dark navy/charcoal palette (#0b0f19, #111827, #1f2937)
- Cyber blue and cyan accents (#38bdf8, #60a5fa, #2563eb)
- Glassmorphism containers, subtle borders, soft glows
- Crisp typography and modern micro-interactions
"""

ENTERPRISE_CSS = """
<style>
/* -------------------------------------------------------------
   1. GLOBAL RESET & TYPOGRAPHY
------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f3f4f6;
    background-color: #0b0f19;
}

/* Base Streamlit App Background */
.stApp {
    background-color: #0b0f19;
    background-image: 
        radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.08) 0px, transparent 50%);
}

/* -------------------------------------------------------------
   2. SIDEBAR STYLING
------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background-color: #0e1320 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0.75rem 1.25rem 0.75rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 1.5rem;
}

.sidebar-brand-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
}

.sidebar-brand-text {
    display: flex;
    flex-direction: column;
}

.sidebar-brand-title {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #ffffff;
    line-height: 1.2;
}

.sidebar-brand-badge {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #38bdf8;
}

/* Navigation Radio Override */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 6px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    margin: 0;
    transition: all 0.2s ease;
    cursor: pointer;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(56, 189, 248, 0.08);
    border-color: rgba(56, 189, 248, 0.25);
    transform: translateX(3px);
}

/* Footer Status Card */
.sidebar-status-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 0.85rem;
    margin-top: 1.5rem;
    font-size: 0.75rem;
}

.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 8px #10b981;
    margin-right: 6px;
}

/* -------------------------------------------------------------
   3. ENTERPRISE CARDS & CONTAINERS
------------------------------------------------------------- */
.sg-card {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.sg-card:hover {
    border-color: rgba(56, 189, 248, 0.25);
    box-shadow: 0 6px 24px -2px rgba(2, 132, 199, 0.15);
}

.sg-card-title {
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #e5e7eb;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* -------------------------------------------------------------
   4. METRIC / KPI TILES
------------------------------------------------------------- */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

@media (max-width: 900px) {
    .kpi-container {
        grid-template-columns: repeat(2, 1fr);
    }
}

.kpi-card {
    background: linear-gradient(180deg, #131b2e 0%, #0f172a 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.15rem 1.25rem;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0284c7, #38bdf8);
    opacity: 0.8;
}

.kpi-card.kpi-approved::before { background: linear-gradient(90deg, #059669, #10b981); }
.kpi-card.kpi-review::before   { background: linear-gradient(90deg, #d97706, #f59e0b); }
.kpi-card.kpi-rejected::before { background: linear-gradient(90deg, #dc2626, #ef4444); }

.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
    margin-bottom: 0.35rem;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}

.kpi-subtitle {
    font-size: 0.75rem;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* -------------------------------------------------------------
   5. DECISION HERO BANNER
------------------------------------------------------------- */
.decision-hero {
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    position: relative;
    overflow: hidden;
}

.decision-hero-approve {
    background: linear-gradient(135deg, rgba(6, 78, 59, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(16, 185, 129, 0.45);
}

.decision-hero-reject {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(239, 68, 68, 0.45);
}

.decision-hero-review {
    background: linear-gradient(135deg, rgba(120, 53, 15, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(245, 158, 11, 0.45);
}

.decision-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.4rem 1rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.pill-approve {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.pill-reject {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.pill-review {
    background: rgba(245, 158, 11, 0.2);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

.decision-title {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #ffffff;
    margin: 0 0 0.35rem 0;
}

.decision-desc {
    font-size: 0.9rem;
    color: #cbd5e1;
    margin: 0;
    max-width: 800px;
    line-height: 1.45;
}

/* -------------------------------------------------------------
   6. STATUS BADGES & PILLS
------------------------------------------------------------- */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.badge-pass {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-fail {
    background: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-review {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-neutral {
    background: rgba(148, 163, 184, 0.12);
    color: #cbd5e1;
    border: 1px solid rgba(148, 163, 184, 0.25);
}

/* -------------------------------------------------------------
   7. EVIDENCE CITATION TILES
------------------------------------------------------------- */
.evidence-card {
    background: #0f172a;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 3px solid #38bdf8;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem;
}

.evidence-field-name {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #38bdf8;
    margin-bottom: 0.25rem;
    display: flex;
    justify-content: space-between;
}

.evidence-quote {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #e2e8f0;
    background: rgba(0, 0, 0, 0.3);
    padding: 0.4rem 0.6rem;
    border-radius: 4px;
    margin-top: 0.35rem;
    border: 1px solid rgba(255, 255, 255, 0.05);
    line-height: 1.4;
}

/* -------------------------------------------------------------
   8. STREAMLIT COMPONENT OVERRIDES
------------------------------------------------------------- */
/* Primary Buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    padding: 0.55rem 1.25rem !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Buttons */
.stButton > button {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #334155 !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Selectboxes & Inputs */
div[data-baseweb="select"] > div,
input, textarea {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    color: #f3f4f6 !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0b0f19;
}
::-webkit-scrollbar-thumb {
    background: #1f293d;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #38bdf8;
}

/* -------------------------------------------------------------
   9. CLEAN ENTERPRISE DATA TABLE
------------------------------------------------------------- */
.sg-table-container {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    overflow-x: auto;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
}

.sg-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.85rem;
}

.sg-table th {
    padding: 0.75rem 0.65rem;
    font-size: 0.72rem;
    text-transform: uppercase;
    color: #64748b;
    letter-spacing: 0.05em;
    font-weight: 600;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sg-table td {
    padding: 0.85rem 0.65rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    vertical-align: middle;
}

.sg-table tr:last-child td {
    border-bottom: none;
}

.sg-table tr:hover td {
    background: rgba(255, 255, 255, 0.02);
}

/* -------------------------------------------------------------
   10. PROCUREMENT AUDIT SPECIFIC CARDS
------------------------------------------------------------- */
.procure-section-card {
    background: #111827;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}

.procure-section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.01em;
}

.procure-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.procure-field {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 0.75rem 1rem;
}

.procure-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94a3b8;
    margin-bottom: 0.25rem;
    font-weight: 600;
}

.procure-value {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f8fafc;
}

.procure-subtext {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.2rem;
}

/* Compliance 7-point checklist */
.compliance-checklist-card {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.65rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background 0.15s ease;
}

.compliance-checklist-card:hover {
    background: rgba(15, 23, 42, 0.9);
    border-color: rgba(56, 189, 248, 0.2);
}

.compliance-check-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #f1f5f9;
}

.compliance-check-desc {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-top: 0.2rem;
    line-height: 1.35;
}

/* Headers */
h1, h2, h3, h4 {
    letter-spacing: -0.025em;
    font-weight: 700;
}

h1 { font-size: 1.85rem !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.45rem !important; }
h3 { font-size: 1.15rem !important; }

/* Dividers */
hr {
    border-color: rgba(255, 255, 255, 0.08) !important;
    margin: 1.5rem 0 !important;
}
</style>
"""

