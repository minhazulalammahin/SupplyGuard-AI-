"""Unit tests for PyMuPDF PDF extraction across all 10 sample packs."""
from pathlib import Path
import pytest
from src.services.pdf_loader import extract_pdf_document


@pytest.mark.parametrize("pack_idx", range(1, 11))
def test_all_10_sample_pdfs_extractable(pack_idx):
    """Test that all 10 supplier packs are readable and yield page text via PyMuPDF."""
    pdf_path = Path(f"data/sample/supplier-pack-{pack_idx:02d}.pdf")
    assert pdf_path.exists(), f"Sample file {pdf_path} does not exist"

    page_texts, full_text = extract_pdf_document(pdf_path)
    assert len(page_texts) >= 1
    assert 1 in page_texts
    assert len(page_texts[1]) > 200
    assert "QUOTATION" in full_text
    assert "PR-2026-114" in full_text

