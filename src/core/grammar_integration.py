"""
Integrates grammar analysis into feedback pipeline (CI-safe and backward-compatible).
"""

from typing import Dict, Any
from src.core.grammar_engine import GrammarEngine


def enhance_feedback_with_grammar(
    sections: Dict[str, str] = None,
    base_feedback: Dict[str, Any] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Enhance feedback dictionary with grammar analysis.

    Supports both `sections` and `parsed_sections` naming for backward compatibility.
    Safely handles missing keys like `suggestions`.
    """
    sections = sections or kwargs.get("parsed_sections") or {}
    base_feedback = (
        base_feedback or kwargs.get("feedback") or kwargs.get("existing_feedback") or {}
    )

    # Defensive copy — even if feedback lacks suggestions or scores
    enhanced = {
        "overall_score": base_feedback.get("overall_score", 0),
        "suggestions": base_feedback.get("suggestions", []),
    }

    try:
        engine = GrammarEngine()
        analysis = engine.analyze_sections(sections)

        grammar_block = {
            "score": analysis.get("overall_score", 0),
            "total_errors": analysis.get("total_errors", 0),
            "section_analysis": analysis.get("section_results", {}),
            "top_errors": [],
        }

        # Flatten top 5 errors from all sections
        top = []
        for sec_name, sec_res in grammar_block["section_analysis"].items():
            for e in sec_res.get("errors", [])[:5]:
                top.append(
                    {
                        "section": sec_name,
                        "type": e.get("type", "grammar"),
                        "sentence": e.get("sentence", ""),
                        "suggestion": e.get("suggestion", ""),
                    }
                )
        grammar_block["top_errors"] = top[:5]

        # ✅ Weighted average for final score
        base_score = int(enhanced.get("overall_score", 0))
        combined_score = int(base_score * 0.7 + grammar_block["score"] * 0.3)

        enhanced.update(
            {
                "grammar": grammar_block,
                "overall_score": combined_score,
            }
        )

    except Exception as exc:
        enhanced["grammar"] = {
            "score": 0,
            "total_errors": 0,
            "error": str(exc),
            "message": "Grammar analysis unavailable",
        }

    finally:
        try:
            engine.close()
        except Exception:
            pass

    return enhanced
