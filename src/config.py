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
    """Retrieve Gemini API key from Streamlit secrets, environment variables, or local .env."""
    # 1. Streamlit secrets (primary for Streamlit Community Cloud)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for sec_name in ("GEMINI_API_KEY", "gemini_api_key"):
                if sec_name in st.secrets:
                    sec_key = str(st.secrets[sec_name]).strip()
                    if sec_key and sec_key != "your_gemini_api_key_here":
                        return sec_key
            # Check nested [general] table if present in secrets.toml
            if "general" in st.secrets and isinstance(st.secrets["general"], dict):
                for sec_name in ("GEMINI_API_KEY", "gemini_api_key"):
                    if sec_name in st.secrets["general"]:
                        sec_key = str(st.secrets["general"][sec_name]).strip()
                        if sec_key and sec_key != "your_gemini_api_key_here":
                            return sec_key
    except Exception:
        pass

    # 2. Environment variables / .env (local development and CI/CD)
    for env_name in ("GEMINI_API_KEY", "gemini_api_key"):
        key = os.getenv(env_name, "").strip()
        if key and key != "your_gemini_api_key_here":
            return key

    return ""

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

def is_gemini_available() -> bool:
    """Check if a valid Gemini API key is configured."""
    return bool(get_gemini_api_key())
