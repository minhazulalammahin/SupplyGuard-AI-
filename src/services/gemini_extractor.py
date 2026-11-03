"""Gemini 2.5 Flash structured document information extraction service."""
import json
import logging
import re
import time
from decimal import Decimal
from typing import Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

from src.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRIES, is_gemini_available
from src.models.schemas import ExtractedQuotation, EvidenceQuote

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert document information extraction engine for SupplyGuard AI.
Your task is to extract structured quotation details from supplier PDF text.

CRITICAL EXTRACTION RULES:
1. Extract numerical and financial values precisely without rounding or modifying them.
2. For EVERY field, provide the exact verbatim text snippet from the document as supporting evidence in `evidence_quotes`.
3. NEVER invent or hallucinate missing information.
4. If a field or clause is missing from the document (e.g. no late delivery penalty clause, or no TIN/BIN), leave the field as null and set `is_present=false` in the corresponding evidence quote.
5. If payment terms specify a range (e.g. '30 to 90 days'), extract payment_min_days=30 and payment_max_days=90.
6. For delivery terms, convert weeks to days (e.g. '4 weeks' = 28 days).
7. If unit price includes VAT or total includes taxes without separate VAT line item, set `vat_is_separate_at_15=false`. If VAT is explicitly shown as a 15% line item, set `vat_is_separate_at_15=true`.
"""


def extract_with_gemini(
    document_text: str,
    api_key: Optional[str] = None,
    model_name: Optional[str] = None
) -> ExtractedQuotation:
    """Extract structured quotation data using Gemini 2.5 Flash API with Pydantic validation."""
    key = api_key or GEMINI_API_KEY
    if not key:
        raise ValueError("Gemini API key is required for online extraction.")

    model = model_name or GEMINI_MODEL
    client = genai.Client(api_key=key)

    prompt = f"Extract all quotation information from the following supplier document text:\n\n{document_text}"

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ExtractedQuotation,
                    temperature=0.0
                )
            )

            if not response.text:
                raise ValueError("Empty response received from Gemini API.")

            # Validate directly through Pydantic
            raw_data = json.loads(response.text)
            extracted = ExtractedQuotation.model_validate(raw_data)
            return extracted

        except (APIError, Exception) as e:
            last_error = e
            logger.warning(f"Gemini API extraction attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)

    raise RuntimeError(f"Gemini API extraction failed after {MAX_RETRIES} attempts: {last_error}")


def extract_deterministic_fallback(document_text: str, filename: str = "") -> ExtractedQuotation:
    """Deterministic extractor for offline testing or when Gemini API key is not configured.
    
    Parses document text using robust regex patterns, ensuring exact citation quotes,
    correct Decimal precision, and accurate missing-clause detection.
    """
    lines = [line.strip() for line in document_text.splitlines() if line.strip()]
    evidence_quotes = []

    # Supplier name: usually first line
    supplier_name = lines[0] if lines else "Unknown Supplier"
    evidence_quotes.append(EvidenceQuote(field_name="supplier_name", quote=supplier_name, page_number=1))

    # Quotation No
    quote_no = None
    m_q = re.search(r'QT-\d{4}-\d+', document_text)
    if m_q:
        quote_no = m_q.group(0)
        evidence_quotes.append(EvidenceQuote(field_name="quotation_number", quote=quote_no, page_number=1))

    # Date
    quote_date = None
    m_d = re.search(r'\b(202\d-\d{2}-\d{2})\b', document_text)
    if m_d:
        quote_date = m_d.group(1)
        evidence_quotes.append(EvidenceQuote(field_name="quotation_date", quote=quote_date, page_number=1))

    # Reference
    pr_ref = None
    m_ref = re.search(r'PR-\d{4}-\d+', document_text)
    if m_ref:
        pr_ref = m_ref.group(0)
        evidence_quotes.append(EvidenceQuote(field_name="pr_reference", quote=pr_ref, page_number=1))

    # TIN / BIN
    tin = None
    bin_no = None
    tin_bin_raw = None
    m_tin = re.search(r'TIN:\s*(\d+)', document_text)
    m_bin = re.search(r'BIN:\s*([\d-]+)', document_text)
    m_tin_bin_line = re.search(r'(Supplier TIN:.*?BIN:.*?)(?:\n|$)', document_text)
    m_reg_req = re.search(r'Supplier registration details available on request', document_text)

    if m_tin_bin_line:
        tin_bin_raw = m_tin_bin_line.group(1).strip()
        tin = m_tin.group(1) if m_tin else None
        bin_no = m_bin.group(1) if m_bin else None
        evidence_quotes.append(EvidenceQuote(field_name="tin", quote=tin_bin_raw, page_number=1, is_present=True))
        evidence_quotes.append(EvidenceQuote(field_name="bin", quote=tin_bin_raw, page_number=1, is_present=True))
    elif m_reg_req:
        tin_bin_raw = m_reg_req.group(0).strip()
        evidence_quotes.append(EvidenceQuote(field_name="tin", quote=tin_bin_raw, page_number=1, is_present=False))
        evidence_quotes.append(EvidenceQuote(field_name="bin", quote=tin_bin_raw, page_number=1, is_present=False))
    else:
        evidence_quotes.append(EvidenceQuote(field_name="tin", quote=None, page_number=1, is_present=False))
        evidence_quotes.append(EvidenceQuote(field_name="bin", quote=None, page_number=1, is_present=False))

    # Item details
    item_code = None
    item_desc = None
    qty = None
    unit = None
    unit_price = None
    line_amount = None

    for code in ['A', 'B', 'C', 'D', 'E']:
        # Match pattern e.g. A \n Cotton twill fabric... or single line
        pattern = rf'\b{code}\b\s*\n\s*([^\n]+)\s*\n\s*([\d,]+)\s*\n\s*([a-zA-Z]+)\s*\n\s*([\d,.]+)\s*\n\s*([\d,.]+)'
        m_item = re.search(pattern, document_text)
        if m_item:
            item_code = code
            item_desc = m_item.group(1).strip()
            qty = Decimal(m_item.group(2).replace(',', ''))
            unit = m_item.group(3).strip()
            unit_price = Decimal(m_item.group(4).replace(',', ''))
            line_amount = Decimal(m_item.group(5).replace(',', ''))
            evidence_quotes.append(EvidenceQuote(field_name="item_code", quote=f"{code}", page_number=1))
            evidence_quotes.append(EvidenceQuote(field_name="unit_price", quote=f"{m_item.group(4)}", page_number=1))
            evidence_quotes.append(EvidenceQuote(field_name="quantity", quote=f"{m_item.group(2)}", page_number=1))
            evidence_quotes.append(EvidenceQuote(field_name="line_amount", quote=f"{m_item.group(5)}", page_number=1))
            break

    # Subtotal, VAT, Total
    subtotal = None
    vat_rate_pct = None
    vat_amount = None
    vat_is_separate = False
    total_amount = None

    m_sub = re.search(r'Subtotal\s*\n\s*([\d,.]+)', document_text)
    if m_sub:
        subtotal = Decimal(m_sub.group(1).replace(',', ''))
        evidence_quotes.append(EvidenceQuote(field_name="subtotal", quote=f"Subtotal {m_sub.group(1)}", page_number=1))

    m_vat = re.search(r'VAT\s*(\d+)%\s*\n\s*([\d,.]+)', document_text)
    if m_vat:
        vat_rate_pct = Decimal(m_vat.group(1))
        vat_amount = Decimal(m_vat.group(2).replace(',', ''))
        vat_is_separate = True
        evidence_quotes.append(EvidenceQuote(field_name="vat_amount", quote=f"VAT {m_vat.group(1)}% {m_vat.group(2)}", page_number=1))
    else:
        # Check if VAT included in price or taxes included
        m_vat_inc = re.search(r'Total\s*\(all taxes included\)\s*\n\s*([\d,.]+)', document_text)
        if m_vat_inc:
            vat_is_separate = False
            evidence_quotes.append(EvidenceQuote(field_name="vat_amount", quote="Total (all taxes included)", page_number=1, is_present=False))

    m_tot = re.search(r'(Total(?:\s*\([^\)]+\))?)\s*\n\s*([\d,.]+)', document_text)
    if m_tot:
        total_amount = Decimal(m_tot.group(2).replace(',', ''))
        evidence_quotes.append(EvidenceQuote(field_name="total_amount", quote=f"{m_tot.group(1)} {m_tot.group(2)}", page_number=1))

    # Terms and Conditions
    # 1. Payment
    payment_terms_raw = None
    advance_payment_pct = Decimal("0.0")
    payment_min_days = None
    payment_max_days = None
    payment_ref = "delivery"

    m_pay = re.search(r'(1\.\s*Payment\..*?)(?=\n\s*\d+\.|\n\s*For\s+|\Z)', document_text, re.DOTALL)
    if m_pay:
        payment_terms_raw = " ".join(m_pay.group(1).split())
        evidence_quotes.append(EvidenceQuote(field_name="advance_payment_pct", quote=payment_terms_raw, page_number=1))
        
        # Advance %
        m_adv = re.search(r'(\d+)%\s*advance', payment_terms_raw, re.IGNORECASE)
        if m_adv:
            advance_payment_pct = Decimal(m_adv.group(1))
        elif "no advance" in payment_terms_raw.lower():
            advance_payment_pct = Decimal("0.0")

        # Payment days range
        m_range = re.search(r'within\s*(\d+)\s*to\s*(\d+)\s*days', payment_terms_raw, re.IGNORECASE)
        if m_range:
            payment_min_days = int(m_range.group(1))
            payment_max_days = int(m_range.group(2))
        else:
            m_single_days = re.search(r'within\s*(\d+)\s*days', payment_terms_raw, re.IGNORECASE)
            if m_single_days:
                payment_min_days = int(m_single_days.group(1))
                payment_max_days = int(m_single_days.group(1))

    # 2. Delivery
    delivery_terms_raw = None
    delivery_promised_days = None
    m_del = re.search(r'(\d+\.\s*Delivery\..*?)(?=\n\s*\d+\.|\n\s*For\s+|\Z)', document_text, re.DOTALL)
    if m_del:
        delivery_terms_raw = " ".join(m_del.group(1).split())
        evidence_quotes.append(EvidenceQuote(field_name="delivery_promised_days", quote=delivery_terms_raw, page_number=1))
        
        # Days or weeks
        m_days = re.search(r'within\s*(\d+)\s*days', delivery_terms_raw, re.IGNORECASE)
        m_weeks = re.search(r'within\s*(\d+)\s*weeks', delivery_terms_raw, re.IGNORECASE)
        if m_days:
            delivery_promised_days = int(m_days.group(1))
        elif m_weeks:
            delivery_promised_days = int(m_weeks.group(1)) * 7

    # 3. Delay / Penalty
    penalty_terms_raw = None
    has_penalty = False
    late_penalty_pct = None

    m_pen = re.search(r'(\d+\.\s*Delay\..*?)(?=\n\s*\d+\.|\n\s*For\s+|\Z)', document_text, re.DOTALL)
    if m_pen:
        penalty_terms_raw = " ".join(m_pen.group(1).split())
        has_penalty = True
        evidence_quotes.append(EvidenceQuote(field_name="late_delivery_penalty_pct_per_week", quote=penalty_terms_raw, page_number=1, is_present=True))
        
        m_rate = re.search(r'([\d.]+)%', penalty_terms_raw)
        if m_rate:
            late_penalty_pct = Decimal(m_rate.group(1))
    else:
        has_penalty = False
        evidence_quotes.append(EvidenceQuote(field_name="late_delivery_penalty_pct_per_week", quote=None, page_number=1, is_present=False))

    # 4. Validity
    validity_terms_raw = None
    validity_days = None
    m_val = re.search(r'(\d+\.\s*Validity\..*?)(?=\n\s*\d+\.|\n\s*For\s+|\Z)', document_text, re.DOTALL)
    if m_val:
        validity_terms_raw = " ".join(m_val.group(1).split())
        evidence_quotes.append(EvidenceQuote(field_name="validity_days", quote=validity_terms_raw, page_number=1))
        m_val_days = re.search(r'valid for\s*(\d+)\s*days', validity_terms_raw, re.IGNORECASE)
        if m_val_days:
            validity_days = int(m_val_days.group(1))

    return ExtractedQuotation(
        supplier_name=supplier_name,
        quotation_number=quote_no,
        quotation_date=quote_date,
        pr_reference=pr_ref,
        item_code=item_code,
        item_description=item_desc,
        quantity=qty,
        unit=unit,
        unit_price=unit_price,
        line_amount=line_amount,
        subtotal=subtotal,
        vat_rate_pct=vat_rate_pct,
        vat_amount=vat_amount,
        vat_is_separate_at_15=vat_is_separate,
        total_amount=total_amount,
        tin=tin,
        bin=bin_no,
        advance_payment_pct=advance_payment_pct,
        payment_min_days=payment_min_days,
        payment_max_days=payment_max_days,
        payment_reference_point=payment_ref,
        delivery_promised_days=delivery_promised_days,
        has_late_delivery_penalty_clause=has_penalty,
        late_delivery_penalty_pct_per_week=late_penalty_pct,
        validity_days=validity_days,
        payment_terms_raw=payment_terms_raw,
        delivery_terms_raw=delivery_terms_raw,
        penalty_terms_raw=penalty_terms_raw,
        validity_terms_raw=validity_terms_raw,
        tin_bin_raw=tin_bin_raw,
        evidence_quotes=evidence_quotes
    )


def extract_supplier_quotation(
    document_text: str,
    use_ai: bool = True,
    filename: str = ""
) -> ExtractedQuotation:
    """Primary extraction entry point.
    
    If use_ai is True and Gemini API is configured, uses Gemini 2.5 Flash.
    Otherwise gracefully falls back to deterministic extraction.
    """
    if use_ai and is_gemini_available():
        try:
            return extract_with_gemini(document_text)
        except Exception as e:
            logger.warning(f"AI extraction failed, falling back to deterministic extractor: {e}")
            return extract_deterministic_fallback(document_text, filename=filename)
    else:
        return extract_deterministic_fallback(document_text, filename=filename)
