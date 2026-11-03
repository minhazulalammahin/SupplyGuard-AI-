"""Unit tests for Gemini extraction, retry logic, and malformed AI responses."""
from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError
from google.genai.errors import APIError

from src.models.schemas import ExtractedQuotation
from src.services.gemini_extractor import extract_with_gemini, extract_supplier_quotation


def test_malformed_json_response_triggers_retry(mocker):
    """Test that malformed JSON from Gemini triggers retries and eventually fails gracefully."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "{ malformed json: missing quotes and brackets"
    mock_client.models.generate_content.return_value = mock_response

    mocker.patch("google.genai.Client", return_value=mock_client)

    with pytest.raises(RuntimeError, match="Gemini API extraction failed"):
        extract_with_gemini("Sample document text", api_key="dummy_key")


def test_valid_json_parses_through_pydantic(mocker):
    """Test that valid JSON response from Gemini is correctly parsed into ExtractedQuotation."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = """{
        "supplier_name": "Test Mill",
        "quotation_number": "QT-001",
        "unit_price": 450.00,
        "quantity": 1000,
        "advance_payment_pct": 10,
        "delivery_promised_days": 20,
        "has_late_delivery_penalty_clause": true,
        "late_delivery_penalty_pct_per_week": 0.5,
        "payment_min_days": 30,
        "payment_max_days": 45,
        "vat_is_separate_at_15": true,
        "vat_rate_pct": 15,
        "vat_amount": 67500,
        "subtotal": 450000,
        "total_amount": 517500,
        "tin": "123456",
        "bin": "789101",
        "validity_days": 30,
        "evidence_quotes": [
            {"field_name": "unit_price", "quote": "450.00", "is_present": true}
        ]
    }"""
    mock_client.models.generate_content.return_value = mock_response
    mocker.patch("google.genai.Client", return_value=mock_client)

    extracted = extract_with_gemini("Sample text", api_key="dummy_key")
    assert extracted.supplier_name == "Test Mill"
    assert extracted.unit_price == pytest.approx(450.00)
    assert extracted.advance_payment_pct == pytest.approx(10.0)


def test_missing_api_key_falls_back_to_deterministic():
    """Test that when Gemini API key is missing, system falls back to deterministic extraction."""
    with patch("src.services.gemini_extractor.is_gemini_available", return_value=False):
        sample_text = """Padma Textile Mills Ltd
QUOTATION
QT-2026-901
Item A
Cotton twill fabric, 280 gsm
12,000
metre
472.00
5,664,000.00
Subtotal
5,664,000.00
VAT 15%
849,600.00
Total
6,513,600.00
Supplier TIN: 101458013391 BIN: 000170141-0101
1. Payment. 10% advance payable with the purchase order.
2. Delivery. Delivery within 24 days of PO.
3. Delay. Late delivery penalty of 1% of order value per week.
4. Validity. This quotation is valid for 45 days from the date above.
"""
        extracted = extract_supplier_quotation(sample_text, use_ai=True)
        assert extracted.supplier_name == "Padma Textile Mills Ltd"
        assert extracted.quotation_number == "QT-2026-901"
        assert extracted.unit_price == pytest.approx(472.00)
        assert extracted.advance_payment_pct == pytest.approx(10.0)

