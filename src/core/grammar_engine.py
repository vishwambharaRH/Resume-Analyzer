"""
Grammar Engine using LanguageTool (remote by default) with CI-safe mocking.
Implements DRA-60: Grammar and spelling analysis.
"""

import os
from typing import Dict, Any, List

_language_tool = None

# Flags for CI/CD vs local runs
USE_REAL_GRAMMAR = os.getenv("USE_REAL_GRAMMAR", "true").lower() == "true"
IS_CI = (
    os.getenv("CI", "false").lower() == "true"
    or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
)

if IS_CI:
    USE_REAL_GRAMMAR = os.getenv("USE_REAL_GRAMMAR", "false").lower() == "true"


class _MockTool:
    """Fast mock for CI runs (no API calls)."""

    def check(self, text: str):
        return []

    def close(self):
        return None


def _get_tool():
    """Lazy initializer for grammar tool (real or mock)."""
    global _language_tool
    if _language_tool is not None:
        return _language_tool

    if not USE_REAL_GRAMMAR:
        _language_tool = _MockTool()
        return _language_tool

    try:
        import language_tool_python

        remote = os.getenv("USE_REMOTE_LT", "true").lower() == "true"
        if remote:
            _language_tool = language_tool_python.LanguageTool(
                "en-US", remote_server="https://api.languagetool.org/"
            )
        else:
            _language_tool = language_tool_python.LanguageTool("en-US")

    except Exception:
        _language_tool = _MockTool()

    return _language_tool


class GrammarEngine:
    """Lightweight grammar and spelling checker."""

    def __init__(self, language: str = "en-US"):
        self.language = language
        self._tool = None

    @property
    def tool(self):
        if self._tool is None:
            self._tool = _get_tool()
        return self._tool

    def analyze_text(self, text: str, max_errors: int = 10) -> Dict[str, Any]:
        """
        Analyze text for grammar and spelling issues.
        Returns structured dictionary with scores and errors.
        """
        if text is None:
            raise ValueError("Text cannot be None")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            matches = self.tool.check(text)
        except Exception:
            matches = []

        total_errors = len(matches)
        limited = matches[:max_errors]

        errors: List[Dict[str, Any]] = []
        for m in limited:
            sentence = getattr(m, "context", None) or getattr(m, "sentence", None) or ""
            replacements = getattr(m, "replacements", []) or []
            error_type = (
                getattr(m, "ruleIssueType", None)
                or getattr(m, "issueType", None)
                or "grammar"
            )
            offset = getattr(m, "offset", None) or getattr(m, "fromPos", None)
            length = getattr(m, "errorLength", None) or getattr(m, "toPos", None) or 0
            message = getattr(m, "message", None) or ""

            errors.append(
                {
                    "sentence": sentence,
                    "suggestions": replacements,  # ✅ structured list instead of string
                    "type": error_type,
                    "offset": offset,
                    "length": length,
                    "message": message,
                }
            )

        word_count = len(text.split()) or 1
        score = self._calculate_score(total_errors, word_count)
        error_density = (total_errors / word_count) * 100

        return {
            "errors": errors,
            "total_errors": total_errors,
            "score": round(score, 2),
            "word_count": word_count,
            "error_density": round(error_density, 2),
        }

    def analyze_sections(self, sections: dict, max_errors: int = 10) -> dict:
        """
        Analyze multiple resume sections and combine results.
        """
        section_results = {}
        total_errors = 0
        weighted_scores = []

        for name, text in sections.items():
            if not isinstance(text, str) or not text.strip():
                section_results[name] = {"score": 0, "total_errors": 0, "errors": []}
                weighted_scores.append(0)
                continue

            res = self.analyze_text(text, max_errors=max_errors)
            section_results[name] = res
            total_errors += res["total_errors"]
            weighted_scores.append(res["score"])

        overall_score = (
            int(sum(weighted_scores) / len(weighted_scores)) if weighted_scores else 0
        )

        return {
            "overall_score": overall_score,
            "section_results": section_results,
            "total_errors": total_errors,
        }

    def _calculate_score(self, total_errors: int, word_count: int) -> float:
        """
        Dynamic scoring function — non-linear decay for better realism.
        """
        if word_count <= 0:
            return 0.0
        density = total_errors / word_count
        # Non-linear: smooth penalty curve
        score = 100 * (1 - min(1, density * 0.8))
        return round(score, 2)

    def close(self):
        try:
            if self._tool is not None:
                self._tool.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
