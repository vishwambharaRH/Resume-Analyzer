"""
Unit tests for the comprehensive resume scoring system (FR-008).
(Implements DRA-63)
"""

import pytest
from src.feedback.feedback_generator import FeedbackGenerator


# Helper function to manually run the score calculation from the test
def calculate_score(generator, base, grammar, verb, jd_match):
    """Helper to call the new score logic"""
    validation = {"completeness_score": base, "keyword_match_score": jd_match}
    # NEW: Pass arguments in the correct order: (base, validation, grammar, verb)
    return generator._calculate_final_score(base, validation, grammar, verb)


@pytest.fixture(scope="module")
def generator():
    return FeedbackGenerator()


# --- DRA-63: Unit test for scoring rules ---


def test_scoring_perfect_fit(generator):
    """
    Scenario: Perfect Quality (100) AND Perfect Fit (100).
    New Weights: (100*0.6) + (100*0.3) + (100*0.1) = 100
    Final: (100 + 100) / 2 = 100
    """
    final_score = calculate_score(
        generator, base=100, grammar=1.0, verb=100, jd_match=100
    )
    assert final_score == 100


def test_scoring_high_quality_low_fit(generator):
    """
    Scenario: High Quality but Zero JD Match (0).
    Inputs: base=90, grammar=1.0, verb=100, jd_match=0
    New Weights: (90*0.6) + (100*0.3) + (100*0.1) = 54 + 30 + 10 = 94
    Final: jd_match is 0, so final_score = quality_score = 94
    """
    final_score = calculate_score(generator, base=90, grammar=1.0, verb=100, jd_match=0)
    # UPDATED ASSERTION
    assert final_score == 94


def test_scoring_poor_quality_high_fit(generator):
    """
    Scenario: Poor Quality but Perfect JD Match (100).
    Inputs: base=40, grammar=0.0, verb=0, jd_match=100
    New Weights: (40*0.6) + (0*0.3) + (0*0.1) = 24
    Final: (24 + 100) / 2 = 62
    """
    final_score = calculate_score(generator, base=40, grammar=0.0, verb=0, jd_match=100)
    # UPDATED ASSERTION
    assert final_score == 62


def test_scoring_mixed_result(generator):
    """
    Scenario: Base=80, Grammar=0.5, Verbs=75, JD Match=50.
    Inputs: base=80, grammar=0.5 (scaled=50), verb=75, jd_match=50
    New Weights: (80*0.6) + (75*0.3) + (50*0.1) = 48 + 22.5 + 5 = 75.5
    Final: (75.5 + 50) / 2 = 62.75 -> round(63)
    """
    final_score = calculate_score(generator, base=80, grammar=0.5, verb=75, jd_match=50)
    # UPDATED ASSERTION
    assert final_score == 63
