"""Enterprise UI Theme and Custom CSS for SupplyGuard AI.

Supports dynamic Dark Mode and Light Mode with seamless switching:
- Dark Mode: Premium deep navy/charcoal palette (#0b0f19, #111827) with cyan/blue accents
- Light Mode: Clean crisp white/light-slate palette (#f8fafc, #ffffff) with professional blue accents
"""


def get_enterprise_css(theme: str = "dark") -> str:
    """Generate theme-aware CSS stylesheet with CSS custom properties."""
    is_dark = theme.lower() != "light"

    if is_dark:
        # DARK MODE PALETTE
        css_vars = """
        --bg-main: #0b0f19;
        --bg-radial-1: rgba(30, 58, 138, 0.16);
        --bg-radial-2: rgba(14, 165, 233, 0.08);
        
        --sidebar-bg: #0e1320;
        --sidebar-border: rgba(255, 255, 255, 0.07);
        --sidebar-nav-bg: rgba(255, 255, 255, 0.02);
        --sidebar-nav-border: rgba(255, 255, 255, 0.04);
        --sidebar-nav-hover: rgba(56, 189, 248, 0.08);
        --sidebar-nav-hover-border: rgba(56, 189, 248, 0.25);
        --sidebar-card-bg: rgba(15, 23, 42, 0.8);
        --sidebar-card-border: rgba(255, 255, 255, 0.07);

        --bg-card: #111827;
        --bg-card-subtle: #0f172a;
        --bg-field: rgba(15, 23, 42, 0.7);
        --border-color: rgba(255, 255, 255, 0.08);
        --border-subtle: rgba(255, 255, 255, 0.05);
        --border-hover: rgba(56, 189, 248, 0.25);
        --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);

        --text-primary: #ffffff;
        --text-body: #f3f4f6;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --accent-cyan: #38bdf8;
        --accent-blue: #2563eb;

        --quote-bg: rgba(0, 0, 0, 0.35);
        --quote-text: #e2e8f0;
        --quote-border: rgba(255, 255, 255, 0.06);

        --table-bg: #111827;
        --table-header-color: #64748b;
        --table-border: rgba(255, 255, 255, 0.06);
        --table-hover: rgba(255, 255, 255, 0.02);

        --input-bg: #111827;
        --input-border: rgba(255, 255, 255, 0.12);
        --input-text: #f3f4f6;

        --kpi-bg: linear-gradient(180deg, #131b2e 0%, #0f172a 100%);
        --kpi-border: rgba(255, 255, 255, 0.08);
        --kpi-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);

        --badge-pass-text: #34d399;
        --badge-pass-bg: rgba(16, 185, 129, 0.15);
        --badge-pass-border: rgba(16, 185, 129, 0.3);

        --badge-fail-text: #f87171;
        --badge-fail-bg: rgba(239, 68, 68, 0.15);
        --badge-fail-border: rgba(239, 68, 68, 0.3);

        --badge-review-text: #fbbf24;
        --badge-review-bg: rgba(245, 158, 11, 0.15);
        --badge-review-border: rgba(245, 158, 11, 0.3);

        --badge-neutral-text: #cbd5e1;
        --badge-neutral-bg: rgba(148, 163, 184, 0.12);
        --badge-neutral-border: rgba(148, 163, 184, 0.25);

        --hero-approve-bg: linear-gradient(135deg, rgba(6, 78, 59, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%);
        --hero-approve-border: rgba(16, 185, 129, 0.45);

        --hero-reject-bg: linear-gradient(135deg, rgba(127, 29, 29, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%);
        --hero-reject-border: rgba(239, 68, 68, 0.45);

        --hero-review-bg: linear-gradient(135deg, rgba(120, 53, 15, 0.45) 0%, rgba(15, 23, 42, 0.9) 100%);
        --hero-review-border: rgba(245, 158, 11, 0.45);

        --bar-track-bg: #1e293b;
        --btn-secondary-bg: #1e293b;
        --btn-secondary-text: #e2e8f0;
        --btn-secondary-border: rgba(255, 255, 255, 0.1);
        --scrollbar-thumb: #1f293d;
        --callout-bg: rgba(15, 23, 42, 0.7);
        """
    else:
        # LIGHT MODE PALETTE
        css_vars = """
        --bg-main: #f8fafc;
        --bg-radial-1: rgba(224, 242, 254, 0.65);
        --bg-radial-2: rgba(219, 234, 254, 0.55);
        
        --sidebar-bg: #ffffff;
        --sidebar-border: rgba(0, 0, 0, 0.08);
        --sidebar-nav-bg: #f8fafc;
        --sidebar-nav-border: rgba(0, 0, 0, 0.06);
        --sidebar-nav-hover: rgba(2, 132, 199, 0.08);
        --sidebar-nav-hover-border: rgba(2, 132, 199, 0.25);
        --sidebar-card-bg: #f1f5f9;
        --sidebar-card-border: rgba(0, 0, 0, 0.08);

        --bg-card: #ffffff;
        --bg-card-subtle: #f8fafc;
        --bg-field: #f1f5f9;
        --border-color: rgba(0, 0, 0, 0.08);
        --border-subtle: rgba(0, 0, 0, 0.05);
        --border-hover: rgba(2, 132, 199, 0.35);
        --card-shadow: 0 4px 18px rgba(0, 0, 0, 0.04);

        --text-primary: #0f172a;
        --text-body: #1e293b;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --accent-cyan: #0284c7;
        --accent-blue: #1d4ed8;

        --quote-bg: #f8fafc;
        --quote-text: #0f172a;
        --quote-border: rgba(0, 0, 0, 0.08);

        --table-bg: #ffffff;
        --table-header-color: #475569;
        --table-border: rgba(0, 0, 0, 0.06);
        --table-hover: rgba(0, 0, 0, 0.02);

        --input-bg: #ffffff;
        --input-border: rgba(0, 0, 0, 0.16);
        --input-text: #0f172a;

        --kpi-bg: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        --kpi-border: rgba(0, 0, 0, 0.08);
        --kpi-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);

        --badge-pass-text: #065f46;
        --badge-pass-bg: rgba(16, 185, 129, 0.16);
        --badge-pass-border: rgba(16, 185, 129, 0.4);

        --badge-fail-text: #991b1b;
        --badge-fail-bg: rgba(239, 68, 68, 0.16);
        --badge-fail-border: rgba(239, 68, 68, 0.4);

        --badge-review-text: #92400e;
        --badge-review-bg: rgba(245, 158, 11, 0.16);
        --badge-review-border: rgba(245, 158, 11, 0.4);

        --badge-neutral-text: #334155;
        --badge-neutral-bg: rgba(148, 163, 184, 0.18);
        --badge-neutral-border: rgba(148, 163, 184, 0.35);

        --hero-approve-bg: linear-gradient(135deg, rgba(209, 250, 229, 0.75) 0%, #ffffff 100%);
        --hero-approve-border: rgba(16, 185, 129, 0.5);

        --hero-reject-bg: linear-gradient(135deg, rgba(254, 226, 226, 0.75) 0%, #ffffff 100%);
        --hero-reject-border: rgba(239, 68, 68, 0.5);

        --hero-review-bg: linear-gradient(135deg, rgba(254, 243, 199, 0.75) 0%, #ffffff 100%);
        --hero-review-border: rgba(245, 158, 11, 0.5);

        --bar-track-bg: #e2e8f0;
        --btn-secondary-bg: #f1f5f9;
        --btn-secondary-text: #0f172a;
        --btn-secondary-border: rgba(0, 0, 0, 0.12);
        --scrollbar-thumb: #cbd5e1;
        --callout-bg: #f1f5f9;
        """

    return f"""
<style>
/* -------------------------------------------------------------
   1. GLOBAL RESET & CSS VARIABLES
------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root, .stApp {{
{css_vars}
}}

html, body, [class*="css"], [data-testid="stMarkdownContainer"] p {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: var(--text-body) !important;
}}

/* Base Streamlit App Background */
.stApp {{
    background-color: var(--bg-main) !important;
    background-image: 
        radial-gradient(at 0% 0%, var(--bg-radial-1) 0px, transparent 50%),
        radial-gradient(at 100% 100%, var(--bg-radial-2) 0px, transparent 50%) !important;
    transition: background-color 0.25s ease;
}}

/* Global Headings */
h1, h2, h3, h4, h5, h6 {{
    letter-spacing: -0.025em;
    font-weight: 700;
    color: var(--text-primary) !important;
}}

h1 {{ font-size: 1.85rem !important; margin-bottom: 0.25rem !important; }}
h2 {{ font-size: 1.45rem !important; }}
h3 {{ font-size: 1.15rem !important; }}

/* -------------------------------------------------------------
   2. SIDEBAR STYLING
------------------------------------------------------------- */
[data-testid="stSidebar"] {{
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--sidebar-border) !important;
    transition: background-color 0.25s ease;
}}

[data-testid="stSidebar"] .block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}}

.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0.75rem 1.25rem 0.75rem;
    border-bottom: 1px solid var(--sidebar-border);
    margin-bottom: 1rem;
}}

.sidebar-brand-icon {{
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);
}}

.sidebar-brand-text {{
    display: flex;
    flex-direction: column;
}}

.sidebar-brand-title {{
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-primary) !important;
    line-height: 1.2;
}}

.sidebar-brand-badge {{
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent-cyan) !important;
}}

/* Theme Toggle Button & Card */
.theme-toggle-box {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    background: var(--sidebar-card-bg);
    border: 1px solid var(--sidebar-card-border);
    border-radius: 10px;
    margin-bottom: 1rem;
}}

.theme-toggle-status {{
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* Navigation Radio Override */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {{
    gap: 6px;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    background: var(--sidebar-nav-bg);
    border: 1px solid var(--sidebar-nav-border);
    border-radius: 8px;
    padding: 0.6rem 0.85rem;
    margin: 0;
    transition: all 0.2s ease;
    cursor: pointer;
    color: var(--text-primary) !important;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background: var(--sidebar-nav-hover);
    border-color: var(--sidebar-nav-hover-border);
    transform: translateX(3px);
}}

/* Footer Status Card */
.sidebar-status-card {{
    background: var(--sidebar-card-bg) !important;
    border: 1px solid var(--sidebar-card-border) !important;
    border-radius: 10px;
    padding: 0.85rem;
    margin-top: 1.5rem;
    font-size: 0.75rem;
    color: var(--text-secondary) !important;
}}

.status-indicator {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 8px #10b981;
    margin-right: 6px;
}}

/* -------------------------------------------------------------
   3. ENTERPRISE CARDS & CONTAINERS
------------------------------------------------------------- */
.sg-card {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--card-shadow);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}

.sg-card:hover {{
    border-color: var(--border-hover) !important;
}}

.sg-card-title {{
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--text-primary) !important;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* -------------------------------------------------------------
   4. METRIC / KPI TILES
------------------------------------------------------------- */
.kpi-container {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}}

@media (max-width: 900px) {{
    .kpi-container {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

.kpi-card {{
    background: var(--kpi-bg) !important;
    border: 1px solid var(--kpi-border) !important;
    border-radius: 12px;
    padding: 1.15rem 1.25rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--kpi-shadow);
}}

.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0284c7, #38bdf8);
    opacity: 0.8;
}}

.kpi-card.kpi-approved::before {{ background: linear-gradient(90deg, #059669, #10b981); }}
.kpi-card.kpi-review::before   {{ background: linear-gradient(90deg, #d97706, #f59e0b); }}
.kpi-card.kpi-rejected::before {{ background: linear-gradient(90deg, #dc2626, #ef4444); }}

.kpi-label {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted) !important;
    margin-bottom: 0.35rem;
}}

.kpi-value {{
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 0.25rem;
}}

.kpi-subtitle {{
    font-size: 0.75rem;
    color: var(--text-muted) !important;
    display: flex;
    align-items: center;
    gap: 4px;
}}

/* -------------------------------------------------------------
   5. DECISION HERO BANNER
------------------------------------------------------------- */
.decision-hero {{
    border-radius: 14px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--card-shadow);
    position: relative;
    overflow: hidden;
}}

.decision-hero-approve {{
    background: var(--hero-approve-bg) !important;
    border: 1px solid var(--hero-approve-border) !important;
}}

.decision-hero-reject {{
    background: var(--hero-reject-bg) !important;
    border: 1px solid var(--hero-reject-border) !important;
}}

.decision-hero-review {{
    background: var(--hero-review-bg) !important;
    border: 1px solid var(--hero-review-border) !important;
}}

.decision-pill {{
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
}}

.pill-approve {{
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.4);
}}

.pill-reject {{
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
}}

.pill-review {{
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.4);
}}

.decision-title {{
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--text-primary) !important;
    margin: 0 0 0.35rem 0;
}}

.decision-desc {{
    font-size: 0.9rem;
    color: var(--text-secondary) !important;
    margin: 0;
    max-width: 800px;
    line-height: 1.45;
}}

/* -------------------------------------------------------------
   6. STATUS BADGES & PILLS
------------------------------------------------------------- */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}}

.badge-pass {{
    background: var(--badge-pass-bg) !important;
    color: var(--badge-pass-text) !important;
    border: 1px solid var(--badge-pass-border) !important;
}}

.badge-fail {{
    background: var(--badge-fail-bg) !important;
    color: var(--badge-fail-text) !important;
    border: 1px solid var(--badge-fail-border) !important;
}}

.badge-review {{
    background: var(--badge-review-bg) !important;
    color: var(--badge-review-text) !important;
    border: 1px solid var(--badge-review-border) !important;
}}

.badge-neutral {{
    background: var(--badge-neutral-bg) !important;
    color: var(--badge-neutral-text) !important;
    border: 1px solid var(--badge-neutral-border) !important;
}}

/* -------------------------------------------------------------
   7. EVIDENCE CITATION TILES
------------------------------------------------------------- */
.evidence-card {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-left: 3px solid var(--accent-cyan) !important;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.75rem;
}}

.evidence-field-name {{
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--accent-cyan) !important;
    margin-bottom: 0.25rem;
    display: flex;
    justify-content: space-between;
}}

.evidence-quote {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: var(--quote-text) !important;
    background: var(--quote-bg) !important;
    padding: 0.4rem 0.6rem;
    border-radius: 4px;
    margin-top: 0.35rem;
    border: 1px solid var(--quote-border) !important;
    line-height: 1.4;
}}

/* -------------------------------------------------------------
   8. CLEAN ENTERPRISE DATA TABLE
------------------------------------------------------------- */
.sg-table-container {{
    background: var(--table-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    overflow-x: auto;
    margin-bottom: 1.5rem;
    box-shadow: var(--card-shadow);
}}

.sg-table {{
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.85rem;
}}

.sg-table th {{
    padding: 0.75rem 0.65rem;
    font-size: 0.72rem;
    text-transform: uppercase;
    color: var(--table-header-color) !important;
    letter-spacing: 0.05em;
    font-weight: 600;
    border-bottom: 1px solid var(--table-border) !important;
}}

.sg-table td {{
    padding: 0.85rem 0.65rem;
    border-bottom: 1px solid var(--table-border) !important;
    vertical-align: middle;
    color: var(--text-body);
}}

.sg-table tr:last-child td {{
    border-bottom: none !important;
}}

.sg-table tr:hover td {{
    background: var(--table-hover) !important;
}}

/* Semantic table columns */
.sg-col-pack {{ font-weight: 600; color: var(--accent-cyan) !important; }}
.sg-col-supplier {{ font-weight: 500; color: var(--text-primary) !important; }}
.sg-col-product {{ color: var(--text-secondary) !important; }}
.sg-col-price {{ font-family: monospace; color: var(--text-primary) !important; font-weight: 600; }}
.sg-col-reason {{ color: var(--text-muted) !important; font-size: 0.78rem; max-width: 280px; }}
.sg-col-details {{ color: var(--text-muted) !important; font-size: 0.76rem; }}

/* -------------------------------------------------------------
   9. PROCUREMENT AUDIT CARDS
------------------------------------------------------------- */
.procure-section-card {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--card-shadow);
}}

.procure-section-title {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent-cyan) !important;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.01em;
}}

.procure-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}}

.procure-field {{
    background: var(--bg-field) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px;
    padding: 0.75rem 1rem;
}}

.procure-label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted) !important;
    margin-bottom: 0.25rem;
    font-weight: 600;
}}

.procure-value {{
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary) !important;
}}

.procure-subtext {{
    font-size: 0.75rem;
    color: var(--text-muted) !important;
    margin-top: 0.2rem;
}}

/* 7-Point Compliance Checklist */
.compliance-checklist-card {{
    background: var(--bg-field) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px;
    padding: 0.85rem 1.15rem;
    margin-bottom: 0.65rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background 0.15s ease;
}}

.compliance-checklist-card:hover {{
    border-color: var(--border-hover) !important;
}}

.compliance-check-name {{
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary) !important;
}}

.compliance-check-desc {{
    font-size: 0.78rem;
    color: var(--text-muted) !important;
    margin-top: 0.2rem;
    line-height: 1.35;
}}

/* Callout and Risk Item Classes */
.sg-callout-box {{
    background: var(--callout-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-top: 1rem;
}}

.risk-item-fail {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0.75rem;
    background: var(--badge-fail-bg) !important;
    border-radius: 6px;
    border-left: 3px solid #ef4444;
    font-size: 0.82rem;
    color: var(--text-primary) !important;
}}

.risk-item-review {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0.75rem;
    background: var(--badge-review-bg) !important;
    border-radius: 6px;
    border-left: 3px solid #f59e0b;
    font-size: 0.82rem;
    color: var(--text-primary) !important;
}}

.rule-card-reject {{
    background: var(--badge-fail-bg) !important;
    border-radius: 6px;
    padding: 0.75rem;
    border-left: 3px solid #ef4444;
    font-size: 0.82rem;
    color: var(--text-secondary) !important;
    margin-bottom: 0.5rem;
}}

.rule-card-review {{
    background: var(--badge-review-bg) !important;
    border-radius: 6px;
    padding: 0.75rem;
    border-left: 3px solid #f59e0b;
    font-size: 0.82rem;
    color: var(--text-secondary) !important;
    margin-bottom: 0.5rem;
}}

.workflow-step-card {{
    background: var(--bg-field) !important;
    padding: 0.75rem;
    border-radius: 6px;
    border: 1px solid var(--border-subtle) !important;
}}

/* -------------------------------------------------------------
   10. STREAMLIT COMPONENT OVERRIDES
------------------------------------------------------------- */
/* Primary Buttons */
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    padding: 0.55rem 1.25rem !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    transition: all 0.2s ease !important;
}}

.stButton > button[kind="primary"]:hover {{
    background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6) !important;
    transform: translateY(-1px) !important;
}}

/* Secondary Buttons */
.stButton > button {{
    background: var(--btn-secondary-bg) !important;
    color: var(--btn-secondary-text) !important;
    border: 1px solid var(--btn-secondary-border) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}}

/* Selectboxes & Inputs */
div[data-baseweb="select"] > div,
input, textarea {{
    background-color: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 8px !important;
    color: var(--input-text) !important;
}}

/* Streamlit Expanders */
[data-testid="stExpander"] {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}}

[data-testid="stExpander"] summary {{
    color: var(--text-primary) !important;
}}

/* Custom Scrollbars */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: var(--bg-main);
}}
::-webkit-scrollbar-thumb {{
    background: var(--scrollbar-thumb);
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--accent-cyan);
}}

/* Dividers */
hr {{
    border-color: var(--border-color) !important;
    margin: 1.5rem 0 !important;
}}
</style>
"""


# Default backward compatibility export
ENTERPRISE_CSS = get_enterprise_css("dark")
