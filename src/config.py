"""Configuration and environment variables for SupplyGuard AI."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data" / "sample")))
PURCHASE_REQUEST_PATH = DATA_DIR / "purchase-request.csv"
COMPANY_RULES_PATH = DATA_DIR / "company-rules.md"

def get_gemini_api_key() -> str:
    """Retrieve Gemini API key from environment variable or Streamlit secrets."""
    # 1. Environment variable
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key and key != "your_gemini_api_key_here":
        return key

    # 2. Streamlit secrets (if running in Streamlit runtime)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            sec_key = st.secrets["GEMINI_API_KEY"].strip()
            if sec_key and sec_key != "your_gemini_api_key_here":
                return sec_key
    except Exception:
        pass

    return ""

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

def is_gemini_available() -> bool:
    """Check if a valid Gemini API key is configured."""
    return bool(get_gemini_api_key())
