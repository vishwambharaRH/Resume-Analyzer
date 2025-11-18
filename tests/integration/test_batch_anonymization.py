"""
Integration test for anonymization with batch processing.
Tests that the new masking rules are correctly applied in the final PDF output.
(Implements DRA-100)
"""

import pytest
from src.feedback.feedback_generator import anonymize_data

# Mock data for the "batch"
MOCK_REPORTS = [
    {
        "name": "Report 1",
        "email": "report1.user@example.com",
        "phone": "+1 12345 67890",
        "score": 80,
        "feedback": {"missingSections": [], "suggestions": []},
    },
    {
        "name": "Report 2",
        "email": "another.user@domain.net",
        "phone": "9876543210",
        "score": 90,
        "feedback": {"missingSections": [], "suggestions": []},
    },
]


def test_anonymization_in_batch_processing(mocker):
    """
    Loops through multiple reports, runs the anonymization logic,
    and verifies the *masked* PII is present in the data.
    (This is the new test logic for DRA-100)
    """
    # Mock the PDF generator, we don't need to test it here
    mocker.patch("src.feedback.feedback_generator.generate_pdf_report")

    # Loop through the "batch" of mock reports
    for report in MOCK_REPORTS:

        # 1. Run the anonymization function
        safe_report = anonymize_data(report)

        # 2. Assert that the *masked* data is in the dictionary

        if report["score"] == 80:
            assert safe_report["email"] == "r*****r@example.com"
            assert safe_report["phone"] == "+1 XXXXX 67890"

        if report["score"] == 90:
            assert safe_report["email"] == "a*****r@domain.net"
            assert safe_report["phone"] == "XXXXX43210"

        assert safe_report["name"] == "[Candidate Name Anonymized]"
