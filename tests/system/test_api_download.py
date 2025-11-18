"""
System tests for the full API download workflow (FastAPI).
"""

import io
import pdfplumber
import pytest
from fastapi.testclient import TestClient
from src.main import app  # Import the main FastAPI app


# --- Test Utility ---
def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        text = "".join(page.extract_text() for page in pdf.pages)
    return " ".join(text.split())


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


# pylint: disable=redefined-outer-name
def test_download_report_end_to_end_workflow(client):
    """
    Tests the full user workflow: API -> PDF Generation -> Download.
    """
    # 1. Simulate a user hitting the API endpoint
    response = client.get("/api/v1/download/123")  # Use a mock job ID

    # 2. Check that the response is a downloadable PDF file
    assert response.status_code == 200

    # --- THIS IS THE FIXED LINE ---
    assert response.headers["content-type"] == "application/pdf"
    # -----------------------------

    assert "Analysis_Report_123.pdf" in response.headers["content-disposition"]

    # 3. Read the PDF content from the API response
    pdf_text = extract_text_from_pdf_bytes(response.content)

    # 4. Verify BOTH content and anonymization are correct
    # NEW, CORRECT ASSERTION
    # THE CORRECT ASSERTION
    assert "**Quality Score:** 34/100" in pdf_text
    assert "a*****j@example.com" in pdf_text
    assert "alex.j@example.com" not in pdf_text
