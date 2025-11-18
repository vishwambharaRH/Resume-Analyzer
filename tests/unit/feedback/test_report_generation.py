"""
Unit tests for the report generation logic.
"""

# NEW, FIXED IMPORTS
from src.feedback.feedback_generator import generate_pdf_report
from src.mock_data import MOCK_ANALYSIS_REPORT
from tests.helpers import extract_text_from_pdf_bytes


# --- DRA-96: Unit test for PDF Content Correctness ---
def test_pdf_contains_key_report_data():
    """
    Verifies that key functional data (score, suggestions, missing sections)
    are correctly present in the final PDF output.
    """
    pdf_output = generate_pdf_report(MOCK_ANALYSIS_REPORT)
    pdf_text = extract_text_from_pdf_bytes(pdf_output)

    # Assertion 1: Check for the numerical score and match (with asterisks)
    assert "**Quality Score:** 82/100" in pdf_text
    assert "**Job Match:** 76%" in pdf_text

    # Assertion 2: Check for a key suggestion (robust check)
    assert "Suggestions for Improvement:" in pdf_text
    assert "Use stronger action verbs." in pdf_text

    # Assertion 3: Check for a missing section (robust check)
    assert "Missing Core Sections:" in pdf_text
    assert "Certifications" in pdf_text
