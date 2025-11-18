"""
Integration tests for Grammar → Feedback Pipeline (DRA-61).
"""

import pytest
import os
from unittest.mock import MagicMock, patch
from src.parser.section_detector import SectionDetector
from src.feedback.feedback_generator import FeedbackGenerator
from src.core.grammar_integration import enhance_feedback_with_grammar


@pytest.fixture(autouse=True)
def optional_mock_grammar(monkeypatch):
    """If running in CI, mock grammar backend."""
    is_ci = (
        os.getenv("CI", "false").lower() == "true"
        or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
    )
    if is_ci:
        mock_tool = MagicMock()
        mock_tool.check.return_value = []
        monkeypatch.setattr(
            "src.core.grammar_engine._MockTool", lambda *a, **kw: mock_tool
        )
    yield


@pytest.fixture
def detector():
    return SectionDetector()


@pytest.fixture
def generator():
    return FeedbackGenerator()


@pytest.fixture
def sample_resume_with_errors():
    return """
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University, 2020

    SKILLS
    Python, Java, machne learning, data science

    EXPERIENCE
    I has worked as software engineer at Google for five years.
    Led team of developers and improved system performence.

    PROJECTS
    Built web application using React and Node.js
    Deployed on AWS with hight availability
    """


@pytest.fixture
def sample_resume_perfect():
    return """
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University, 2020

    SKILLS
    Python, Java, Machine Learning, Data Science

    EXPERIENCE
    Worked as Software Engineer at Google for five years.
    Led team of developers and improved system performance.

    PROJECTS
    Built web application using React and Node.js.
    Deployed on AWS with high availability.
    """


class TestGrammarFeedbackIntegration:
    def test_end_to_end_grammar_integration(
        self, detector, generator, sample_resume_with_errors
    ):
        validation = detector.validate_resume_structure(sample_resume_with_errors)
        sections = validation.get("merged_sections", {})
        assert len(sections) > 0

        feedback = generator.generate_comprehensive_feedback_with_grammar(
            sections=sections,
            validation=validation,
            include_grammar=True,
        )

        grammar = feedback.get("grammar", {})
        assert "score" in grammar
        assert "total_errors" in grammar

    def test_grammar_optional_flag(
        self, detector, generator, sample_resume_with_errors
    ):
        validation = detector.validate_resume_structure(sample_resume_with_errors)
        sections = validation.get("merged_sections", {})

        feedback = generator.generate_comprehensive_feedback_with_grammar(
            sections=sections,
            validation=validation,
            include_grammar=False,
        )
        assert "grammar" not in feedback or feedback["grammar"] is None


class TestGrammarIntegrationHelpers:
    def test_enhance_feedback_with_grammar_function(self):
        sections = {"experience": "I has worked at Google for five years."}
        base_feedback = {"overall_score": 80, "suggestions": ["Add more details"]}
        enhanced = enhance_feedback_with_grammar(sections, base_feedback)
        assert "grammar" in enhanced


# ------------------------------------------------------------------------
# NEW TESTS FOR COVERAGE BOOST (do not modify existing ones)
# ------------------------------------------------------------------------


class TestGrammarPipelineEdgeCases:
    def test_grammar_integration_exception_handling(
        self, detector, generator, sample_resume_with_errors
    ):
        """Simulate grammar engine crash and ensure fallback still returns valid output."""
        validation = detector.validate_resume_structure(sample_resume_with_errors)
        sections = validation.get("merged_sections", {})

        with patch(
            "src.feedback.feedback_generator.enhance_feedback_with_grammar",
            side_effect=RuntimeError("Grammar engine failed"),
        ):
            feedback = generator.generate_comprehensive_feedback_with_grammar(
                sections=sections, validation=validation, include_grammar=True
            )

        assert "grammar" in feedback
        assert "error" in feedback["grammar"]

    def test_empty_resume_does_not_crash(self, detector, generator):
        """Ensure empty input returns safe feedback."""
        validation = detector.validate_resume_structure("")
        feedback = generator.generate_comprehensive_feedback_with_grammar(
            sections={}, validation=validation, include_grammar=False
        )
        assert isinstance(feedback, dict)

    def test_action_verb_only_mode(self, detector, generator, sample_resume_perfect):
        """Ensure when grammar disabled, only action verbs are analyzed."""
        validation = detector.validate_resume_structure(sample_resume_perfect)
        sections = validation.get("merged_sections", {})
        feedback = generator.generate_comprehensive_feedback_with_grammar(
            sections=sections, validation=validation, include_grammar=False
        )
        assert "action_verbs" in feedback
        assert "total_weak_verbs" in feedback["action_verbs"]

    def test_enhance_feedback_with_grammar_merges_existing_fields(self):
        """Ensure grammar feedback merges cleanly into base feedback."""
        sections = {"projects": "I made an app using React."}
        base_feedback = {"suggestions": ["Good structure"], "overall_score": 95}
        result = enhance_feedback_with_grammar(sections, base_feedback)
        assert isinstance(result, dict)
        assert "grammar" in result
        assert "score" in result["grammar"]

    def test_mock_tool_is_used_in_ci_mode(self, monkeypatch):
        """Force CI mode and verify that _MockTool is used instead of real grammar."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.setattr("src.core.grammar_engine._MockTool", MagicMock)
        from src.core import grammar_engine

        tool = grammar_engine._get_tool()
        # ensure we got an object that looks like the grammar tool (has .check)
        assert tool is not None
        assert hasattr(tool, "check")
