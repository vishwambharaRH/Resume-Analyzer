"""
Integration Test — Action Verb Suggestions (DRA-76)
"""

from src.feedback.feedback_generator import FeedbackGenerator


def test_action_verb_feedback_integration():
    sections = {
        "experience": "I did backend development and worked on APIs.",
        "projects": "I helped build a chatbot system.",
    }
    validation = {"completeness_score": 90, "has_all_required": True}
    generator = FeedbackGenerator()

    feedback = generator.generate_comprehensive_feedback_with_grammar(
        sections=sections, validation=validation, include_grammar=False
    )

    assert "action_verbs" in feedback
    assert feedback["action_verbs"]["total_weak_verbs"] > 0
    assert any("Replace weak verb" in s for s in feedback["suggestions"])
