"""
Unit tests for Grammar Engine (DRA-60) — CI-safe.
"""

import pytest
import os
from unittest.mock import MagicMock
from src.core.grammar_engine import GrammarEngine


@pytest.fixture(autouse=True)
def mock_language_tool_in_ci(monkeypatch):
    """Automatically mock grammar backend in CI."""
    is_ci = (
        os.getenv("CI", "false").lower() == "true"
        or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
    )
    if is_ci:
        mock_tool = MagicMock()
        mock_tool.check.return_value = []
        mock_tool.close.return_value = None
        monkeypatch.setattr(
            "src.core.grammar_engine._MockTool", lambda *a, **kw: mock_tool
        )
    yield


class TestGrammarEngine:
    @pytest.fixture
    def engine(self):
        return GrammarEngine()

    @pytest.fixture(autouse=True)
    def cleanup(self, engine):
        yield
        engine.close()

    def test_engine_initialization(self, engine):
        assert engine is not None
        assert engine.language == "en-US"
        assert engine.tool is not None

    def test_analyze_perfect_text(self, engine):
        text = "I am a software engineer with five years of experience."
        result = engine.analyze_text(text)
        assert "errors" in result
        assert "score" in result
        assert isinstance(result["score"], (int, float))

    def test_analyze_empty_text(self, engine):
        with pytest.raises(ValueError, match="Text cannot be empty"):
            engine.analyze_text("")

    def test_analyze_none_text(self, engine):
        with pytest.raises(ValueError):
            engine.analyze_text(None)

    def test_score_calculation_no_errors(self, engine):
        assert engine._calculate_score(0, 100) == 100

    def test_score_calculation_low_error_rate(self, engine):
        score = engine._calculate_score(1, 100)
        assert 90 <= score <= 100

    def test_analyze_sections_empty_dict(self, engine):
        result = engine.analyze_sections({})
        assert result["overall_score"] == 0
        assert result["section_results"] == {}
        assert result["total_errors"] == 0
