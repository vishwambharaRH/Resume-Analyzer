"""
Common helper utilities for testing.
"""

import io
import pdfplumber


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Helper function to read and return all text from PDF bytes."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages)
    # Clean up whitespace for reliable assertions
    return " ".join(text.split())
