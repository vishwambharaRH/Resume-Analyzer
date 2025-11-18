import pytest
from unittest.mock import MagicMock, patch
from src.core.grammar_integration import enhance_feedback_with_grammar


# ----------------------------------------------------------------------
# Helper: Fake GrammarEngine analysis response
# ----------------------------------------------------------------------
def fake_analysis():
    return {
        "overall_score": 80,
        "total_errors": 3,
        "section_results": {
            "experience": {
                "errors": [
                    {
                        "type": "grammar",
                        "sentence": "I has experience",
                        "suggestion": "have",
                    },
                    {
                        "type": "spelling",
                        "sentence": "I am lernng",
                        "suggestion": "learning",
                    },
                ]
            },
            "projects": {
                "errors": [
                    {
                        "type": "grammar",
                        "sentence": "We build system",
                        "suggestion": "built",
                    },
                ]
            },
        },
    }


# ----------------------------------------------------------------------
# 1. Normal flow – ensure grammar block is added
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_integration_adds_grammar_block(mock_engine_cls):
    mock_engine = MagicMock()
    mock_engine.analyze_sections.return_value = fake_analysis()
    mock_engine_cls.return_value = mock_engine

    sections = {"experience": "I has experience"}
    base_feedback = {"overall_score": 90, "suggestions": ["Improve structure"]}

    result = enhance_feedback_with_grammar(
        sections=sections, base_feedback=base_feedback
    )

    assert "grammar" in result
    assert result["grammar"]["total_errors"] == 3
    assert len(result["grammar"]["top_errors"]) > 0
    assert result["overall_score"] != 90  # weighted merge applied


# ----------------------------------------------------------------------
# 2. Ensure backward-compatibility fields work (parsed_sections + feedback)
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_integration_accepts_legacy_kwargs(mock_engine_cls):
    mock_engine = MagicMock()
    mock_engine.analyze_sections.return_value = fake_analysis()
    mock_engine_cls.return_value = mock_engine

    result = enhance_feedback_with_grammar(
        parsed_sections={"projects": "We build system"},
        feedback={"overall_score": 50},
    )

    assert "grammar" in result
    assert result["grammar"]["total_errors"] == 3


# ----------------------------------------------------------------------
# 3. Missing base feedback fields should not crash
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_missing_base_feedback_safe(mock_engine_cls):
    mock_engine = MagicMock()
    mock_engine.analyze_sections.return_value = fake_analysis()
    mock_engine_cls.return_value = mock_engine

    result = enhance_feedback_with_grammar(sections={"exp": "Hello"}, base_feedback={})

    assert "grammar" in result
    assert result["overall_score"] >= 0
    assert isinstance(result["suggestions"], list)


# ----------------------------------------------------------------------
# 4. When GrammarEngine raises an exception → graceful fallback
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_integration_handles_engine_exception(mock_engine_cls):
    mock_engine = MagicMock()
    mock_engine.analyze_sections.side_effect = RuntimeError("Engine fail")
    mock_engine_cls.return_value = mock_engine

    result = enhance_feedback_with_grammar(sections={"exp": "Hello"})

    assert result["grammar"]["score"] == 0
    assert result["grammar"]["total_errors"] == 0
    assert "Engine fail" in result["grammar"]["error"]


# ----------------------------------------------------------------------
# 5. GrammarEngine.close() is always attempted (finally block)
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_engine_close_is_called(mock_engine_cls):
    mock_engine = MagicMock()
    mock_engine.analyze_sections.return_value = fake_analysis()
    mock_engine_cls.return_value = mock_engine

    enhance_feedback_with_grammar(sections={"a": "b"})
    assert mock_engine.close.called


# ----------------------------------------------------------------------
# 6. Ensure top errors flattening only picks 5 max
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_top_errors_limit(mock_engine_cls):
    mock_engine = MagicMock()
    # Create 10 fake errors
    big_analysis = {
        "overall_score": 70,
        "total_errors": 10,
        "section_results": {
            "experience": {
                "errors": [
                    {"type": "grammar", "sentence": f"s{i}", "suggestion": "fix"}
                    for i in range(10)
                ]
            }
        },
    }
    mock_engine.analyze_sections.return_value = big_analysis
    mock_engine_cls.return_value = mock_engine

    result = enhance_feedback_with_grammar(sections={"experience": "abc"})

    assert len(result["grammar"]["top_errors"]) == 5


# ----------------------------------------------------------------------
# 7. Weighted score merge is correct
# ----------------------------------------------------------------------
@patch("src.core.grammar_integration.GrammarEngine")
def test_score_merge_logic(mock_engine_cls):
    mock_engine = MagicMock()
    mock_engine.analyze_sections.return_value = {
        "overall_score": 100,
        "total_errors": 0,
        "section_results": {},
    }
    mock_engine_cls.return_value = mock_engine

    base_feedback = {"overall_score": 50}
    result = enhance_feedback_with_grammar(
        sections={"exp": "x"}, base_feedback=base_feedback
    )

    # base=50, grammar=100 -> 50*0.7 + 100*0.3 = 65
    assert result["overall_score"] == 65
