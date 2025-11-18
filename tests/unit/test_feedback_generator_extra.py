import pytest
from src.feedback.feedback_generator import FeedbackGenerator
from src.core.grammar_integration import enhance_feedback_with_grammar


def test_generate_comprehensive_feedback_empty_sections():
    """Should handle empty or missing sections gracefully."""
    gen = FeedbackGenerator()

    sections = {"education": "", "experience": "", "projects": "", "skills": ""}
    validation = {
        "completeness_score": 0,
        "missing_sections": [],
        "has_all_required": False,
        "present_sections": [],
    }

    feedback = gen.generate_comprehensive_feedback(sections, validation)

    assert isinstance(feedback, dict)
    assert feedback["overall_score"] == 0
    assert len(feedback["incomplete_sections"]) == 4
    assert len(feedback["suggestions"]) > 0


def test_feedback_generator_strengths_logic():
    """Covers the strengths generation branch."""
    gen = FeedbackGenerator()

    sections = {
        "education": "Completed BTech in CSE",
        "experience": "Worked at ABC",
    }
    validation = {
        "has_all_required": True,
        "completeness_score": 80,
        "present_sections": ["education", "experience", "projects", "skills"],
        "missing_sections": [],
    }

    feedback = gen.generate_comprehensive_feedback(sections, validation)

    assert "strengths" in feedback
    assert any("All required sections" in s for s in feedback["strengths"])


def test_generate_comprehensive_feedback_with_grammar_disabled(monkeypatch):
    """Covers grammar-skipped branch."""
    gen = FeedbackGenerator()

    sections = {"projects": "I did a project"}
    validation = {"completeness_score": 50, "has_all_required": False}

    # Mock action verb analysis so grammar is skipped but verbs run
    monkeypatch.setattr(
        "src.feedback.feedback_generator.FeedbackGenerator._analyze_action_verbs",
        lambda self, sec: {"total_weak_verbs": 1, "suggestions": ["Replace X"]},
    )

    result = gen.generate_comprehensive_feedback_with_grammar(
        sections, validation, include_grammar=False
    )

    assert "action_verbs" in result
    assert result["action_verbs"]["total_weak_verbs"] == 1
