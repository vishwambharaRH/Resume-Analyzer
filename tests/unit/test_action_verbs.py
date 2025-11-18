"""
Unit tests for ActionVerbEngine
Validates detection of weak verbs, suggestions, and scoring.
"""

import pytest
from src.core.action_verbs import ActionVerbEngine


@pytest.fixture(scope="module")
def engine():
    """Provide a reusable ActionVerbEngine instance."""
    return ActionVerbEngine()


def test_detects_weak_verbs(engine):
    """Should detect weak verbs and suggest improvements."""
    text = "I did backend work and helped build a project."
    result = engine.suggest(text)

    assert isinstance(result, dict)
    assert "found" in result
    assert "suggestions" in result
    assert len(result["found"]) > 0
    assert "did" in [v.lower() for v in result["found"]]
    assert any(s for s in result["suggestions"] if isinstance(s, str))
    assert result["total_weak_verbs"] == len(result["found"])


def test_strong_verbs_no_suggestions(engine):
    """Should return empty if no weak verbs exist."""
    text = "Developed APIs and optimized machine learning models."
    result = engine.suggest(text)

    assert result["weak_verbs"] == 0
    assert result["total_verbs"] > 0
    assert result["score"] == 100.0
    assert result["found"] == []
    assert result["suggestions"] == []


def test_case_insensitivity(engine):
    """Should detect weak verbs regardless of case."""
    text = "Helped coordinate team and BUILT tools for deployment."
    result = engine.suggest(text)

    lower_found = [v.lower() for v in result["found"]]
    assert "helped" in lower_found or "built" in lower_found
    assert result["weak_verbs"] >= 1
    assert result["score"] < 100.0


def test_score_calculation(engine):
    """Score should decrease as number of weak verbs increases."""
    text_weak = "I did work and helped build systems."
    text_strong = "I engineered APIs and designed scalable systems."

    weak_score = engine.suggest(text_weak)["score"]
    strong_score = engine.suggest(text_strong)["score"]

    assert strong_score > weak_score
    assert 0 <= weak_score <= 100
    assert 0 <= strong_score <= 100


def test_empty_text_returns_full_score(engine):
    """Empty text should safely return a perfect score."""
    result = engine.suggest("")
    assert result["score"] == 100.0
    assert result["weak_verbs"] == 0
