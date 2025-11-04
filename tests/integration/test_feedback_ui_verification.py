"""
Integration Tests for Feedback UI Verification - DRA-49
Test Cases: TC-FEED-001 to TC-FEED-008

Requirements:
- FR-003: Integration of incomplete section feedback
- STP: RPRS-F-003
- RTM: Feedback → UI flow
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestFeedbackUIIntegration:
    """Integration tests for feedback display"""

    def test_api_returns_incomplete_section_feedback(self):
        """
        TC-FEED-001: Verify API returns incomplete section feedback

        Expected: Feedback includes incomplete sections with messages
        """
        response = client.get("/api/v1/results/test-job-123")

        assert response.status_code == 200
        data = response.json()

        assert "feedback" in data
        assert "incomplete_sections" in data["feedback"]

    def test_incomplete_sections_have_messages(self):
        """
        TC-FEED-002: Verify incomplete sections have clear messages

        Expected: Each incomplete section has message and suggestion
        Requirements: NFR-004 (Meaningful error messages)
        """
        response = client.get("/api/v1/results/test-job-123")
        data = response.json()

        incomplete = data["feedback"]["incomplete_sections"]

        for item in incomplete:
            assert "section" in item
            assert "message" in item
            assert "suggestion" in item
            assert len(item["message"]) > 10  # Meaningful message

    def test_feedback_includes_strengths(self):
        """
        TC-FEED-003: Verify feedback includes positive elements

        Expected: Strengths section present
        Requirements: NFR-009 (Balanced feedback)
        """
        response = client.get("/api/v1/results/test-job-123")
        data = response.json()

        assert "strengths" in data["feedback"]
        assert len(data["feedback"]["strengths"]) > 0

    def test_feedback_includes_suggestions(self):
        """
        TC-FEED-004: Verify actionable suggestions provided

        Expected: Suggestions for improvement
        """
        response = client.get("/api/v1/results/test-job-123")
        data = response.json()

        assert "suggestions" in data["feedback"]
        assert len(data["feedback"]["suggestions"]) > 0

    def test_overall_score_calculated(self):
        """
        TC-FEED-005: Verify overall score is calculated

        Expected: Score reflects completeness and quality
        """
        response = client.get("/api/v1/results/test-job-123")
        data = response.json()

        assert "overall_score" in data["feedback"]
        assert 0 <= data["feedback"]["overall_score"] <= 100

    def test_missing_and_incomplete_sections_distinguished(self):
        """
        TC-FEED-006: Verify missing vs incomplete sections are separate

        Expected: Different fields for missing vs incomplete
        """
        response = client.get("/api/v1/results/test-job-123")
        data = response.json()

        assert "missing_sections" in data["feedback"]
        assert "incomplete_sections" in data["feedback"]
        # These should be different lists
        assert isinstance(data["feedback"]["missing_sections"], list)
        assert isinstance(data["feedback"]["incomplete_sections"], list)

    def test_invalid_job_id_returns_404(self):
        """
        Test error handling for invalid job ID
        """
        response = client.get("/api/v1/results/")

        assert response.status_code == 404
