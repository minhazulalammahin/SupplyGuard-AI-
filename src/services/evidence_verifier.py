"""Evidence verification and anti-hallucination validation service."""
import re
from typing import List, Tuple
from src.models.schemas import ExtractedQuotation


def normalize_text_for_comparison(text: str) -> str:
    """Normalize whitespace and punctuation for robust substring matching across line breaks."""
    if not text:
        return ""
    # Replace non-breaking spaces, excessive whitespace, and standard newlines with single space
    cleaned = re.sub(r'\s+', ' ', text)
    # Remove surrounding quotes and strip
    return cleaned.strip().strip('"\'')


def snippet_exists_in_text(snippet: str, full_document_text: str) -> bool:
    """Verify whether an evidence snippet exists verbatim or near-verbatim in the document text."""
    if not snippet or not full_document_text:
        return False
        
    norm_snippet = normalize_text_for_comparison(snippet)
    norm_doc = normalize_text_for_comparison(full_document_text)
    
    if not norm_snippet:
        return False
        
    # Check direct substring
    if norm_snippet.lower() in norm_doc.lower():
        return True
        
    # If snippet has multiple sentences or words, check if a 4-word window exists
    words = norm_snippet.split()
    if len(words) >= 4:
        sub_phrase = " ".join(words[:4]).lower()
        if sub_phrase in norm_doc.lower():
            return True
            
    return False


def verify_quotation_evidence(
    quotation: ExtractedQuotation,
    full_document_text: str,
    pdf_filename: str = ""
) -> Tuple[ExtractedQuotation, List[str]]:
    """Verify all evidence quotes in an ExtractedQuotation against the raw document text.
    
    Args:
        quotation: The extracted quotation model.
        full_document_text: Full raw text extracted from PDF.
        pdf_filename: Optional PDF filename for logging context.
        
    Returns:
        Tuple of (updated_quotation, list_of_unverified_fields)
    """
    unverified: List[str] = []
    
    for eq in quotation.evidence_quotes:
        if not eq.is_present:
            # Genuinely absent clauses/fields are verified as absent
            eq.is_verified = True
            continue
            
        if not eq.quote or eq.quote.strip() == "":
            eq.is_verified = False
            unverified.append(f"{eq.field_name}: Empty quote provided")
            continue
            
        # Check against full document text
        if snippet_exists_in_text(eq.quote, full_document_text):
            eq.is_verified = True
        else:
            eq.is_verified = False
            unverified.append(f"{eq.field_name}: Quote '{eq.quote}' not found in document")
            
    return quotation, unverified

