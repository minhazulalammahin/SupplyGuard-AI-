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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

def is_gemini_available() -> bool:
    """Check if Gemini API key is configured."""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY.strip() and GEMINI_API_KEY != "your_gemini_api_key_here")
