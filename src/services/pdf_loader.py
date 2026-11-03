"""PDF Extraction service using PyMuPDF (pymupdf)."""
from pathlib import Path
from typing import Dict, Tuple
import pymupdf


def extract_pdf_document(pdf_path: str | Path) -> Tuple[Dict[int, str], str]:
    """Extract text from a PDF file preserving page numbers and formatting.
    
    Args:
        pdf_path: Path to the PDF file.
        
    Returns:
        Tuple of (page_texts_dict, full_document_text)
        page_texts_dict keys are 1-indexed page numbers.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found at: {path}")
    
    doc = pymupdf.open(str(path))
    page_texts: Dict[int, str] = {}
    full_text_chunks = []
    
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            page_num = page_index + 1
            text = page.get_text("text")
            page_texts[page_num] = text
            full_text_chunks.append(text)
    finally:
        doc.close()
        
    full_text = "\n".join(full_text_chunks)
    return page_texts, full_text
