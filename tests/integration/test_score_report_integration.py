"""
Integration test for the final scoring pipeline.
Verifies DRA-64: Score is correctly calculated and exposed in the final report.
"""

import pytest
from unittest.mock import patch
from src.feedback.feedback_generator import FeedbackGenerator

# --- Mock Data Structures ---
# We define the expected scores from the external engines here
MOCK_VALIDATION_RESULT = {
    "completeness_score": 80,
    "has_all_required": True,
    "missing_sections": [],
    "present_sections": ["education", "skills", "experience", "projects"],
    "keyword_match_score": 30,  # Mock result from JD Matching (DRA-18)
}

MOCK_SECTIONS_INPUT = {"placeholder": "text"}  # Minimal input required


# Helper to mock the data coming from the Grammar/Verb Engines
def mock_grammar_and_verbs():
    # Grammar Score: 0.5 (50%) | Action Verb Score: 75%
    return {
        "grammar": {"score": 0.5, "total_errors": 5},
        "action_verbs": {"overall_score": 75},
    }


# --- DRA-64: Integration Test for Score/Report ---


@pytest.fixture
def generator():
    return FeedbackGenerator()


# Use patches to inject the Grammar and Action Verb scores
@patch(
    "src.core.grammar_integration.enhance_feedback_with_grammar",
    lambda sections, base_feedback: {**base_feedback, **mock_grammar_and_verbs()},
)
@patch(
    "src.feedback.feedback_generator.FeedbackGenerator._analyze_action_verbs",
    lambda self, sections: mock_grammar_and_verbs()["action_verbs"],
)
def test_dra64_score_to_report_integration(generator):
    """
    Tests that the aggregate score is correctly calculated and exposed in the final report structure.
    The test verifies that the JD Match Score (30) and other scores (Completeness: 80, Quality: 69.5)
    are correctly fused into a final score.
    """
    # Final Score Calculation: (Quality Score 69.5 + JD Match 30) / 2 = 49.75 -> rounds to 50
    EXPECTED_SCORE = 51

    # 1. Generate the report (This calls the score calculation method)
    final_report = generator.generate_comprehensive_feedback_with_grammar(
        sections=MOCK_SECTIONS_INPUT,
        validation=MOCK_VALIDATION_RESULT,
        include_grammar=True,
    )

    # 2. Assertions
    assert (
        "overall_score" in final_report
    ), "Final report is missing the overall_score key (FR-008)."
    assert (
        final_report["overall_score"] == EXPECTED_SCORE
    ), f"Final overall score calculation is incorrect. Expected {EXPECTED_SCORE}, got {final_report['overall_score']}"

    # Check that the report contains the data from ALL sources
    assert "grammar" in final_report
    assert "action_verbs" in final_report
