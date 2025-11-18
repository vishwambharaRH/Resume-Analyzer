"""
Integration tests for report privacy and anonymization.
"""

# NEW, FIXED IMPORTS
from src.feedback.feedback_generator import generate_pdf_report
from src.mock_data import MOCK_ANALYSIS_REPORT
from tests.helpers import extract_text_from_pdf_bytes


# --- DRA-97: Integration test for PDF -> Anonymization ---
def test_pdf_anonymization_is_enforced():
    """
    Verifies the security requirement (FR-005/RPRS-F-002) is met:
    PII must be masked in the final PDF (Integration/Security Test).
    """
    pdf_output = generate_pdf_report(MOCK_ANALYSIS_REPORT)
    pdf_text = extract_text_from_pdf_bytes(pdf_output)

    # 1. Define the PII that MUST NOT appear
    original_email = MOCK_ANALYSIS_REPORT["email"]
    original_phone = MOCK_ANALYSIS_REPORT["phone"]

    # 2. Define the anonymized text that MUST appear
    anonymized_email = "[Email Anonymized]"
    anonymized_name = "[Candidate Name Anonymized]"

    # Assertion 1: The original PII is NOT present
    assert original_email not in pdf_text
    assert original_phone not in pdf_text

    # Assertion 2: The anonymized replacement IS present
    assert "a*****j@example.com" in pdf_text
    assert anonymized_name in pdf_text
