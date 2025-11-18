"""
Feedback Generator Module (Merged)

[CRITICAL SCORING FIX 2]:
1.  Penalties in `generate_comprehensive_feedback` are now
    much stricter and based on ALL suggestions.
2.  All scoring weights are adjusted to 60% (Completeness),
    30% (Verbs), and 10% (Grammar).
"""

import os
import io
import logging
from typing import Dict, List, Any
from xhtml2pdf import pisa
from jinja2 import Template

from src.parser.section_detector import SectionDetector, SectionType
from src.core.masking import mask_email, mask_phone
from src.core.grammar_integration import enhance_feedback_with_grammar
from src.core.action_verbs import ActionVerbEngine

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """
    Generates resume feedback for completeness, structure, grammar, and style.
    """

    def __init__(self):
        self.section_detector = SectionDetector()
        logger.info("Initialized FeedbackGenerator")

    # ----------------------------------------------------------------------
    # --- 🔴 MODIFIED FUNCTION (WEIGHTS) 🔴 ---
    # ----------------------------------------------------------------------
    def _calculate_final_score(
        self,
        penalized_completeness: int,
        validation: Dict,
        grammar_score: float,
        verb_score: int,
    ) -> int:
        """
        Calculates the final weighted score, integrating Quality and JD Match.
        """
        base_completeness = penalized_completeness
        jd_match_score = validation.get("keyword_match_score", 0)
        grammar_score_scaled = int(grammar_score * 100)

        base_completeness = min(100, max(0, base_completeness))
        grammar_score_scaled = min(100, max(0, grammar_score_scaled))
        verb_score = min(100, max(0, verb_score))
        jd_match_score = min(100, max(0, jd_match_score))

        # 1. Calculate Quality Score
        # --- NEW WEIGHTS ---
        # Completeness: 60%
        # Action Verbs: 30%
        # Grammar: 10%
        quality_score = (
            (base_completeness * 0.60)
            + (verb_score * 0.30)
            + (grammar_score_scaled * 0.10)
        )

        if jd_match_score < 1:
            final_score = quality_score
        else:
            final_score = (quality_score + jd_match_score) / 2

        return max(0, min(100, int(round(final_score, 0))))

    # ----------------------------------------------------------------------
    # SECTION COMPLETENESS LOGIC (Unchanged)
    # ----------------------------------------------------------------------

    def check_section_completeness(self, sections: Dict[str, str]) -> Dict[str, Dict]:
        completeness_status = {}
        for section_name, content in sections.items():
            try:
                section_type = SectionType(section_name.lower())
            except ValueError:
                continue

            min_words_for_complete = 10

            is_complete = self.section_detector.is_section_complete(
                content, section_type, min_words=min_words_for_complete
            )
            words = [word for word in content.split() if len(word) > 2]
            word_count = len(words)

            if not is_complete:
                reason = self._determine_incompleteness_reason(
                    section_name, content, word_count, min_words_for_complete
                )
            else:
                reason = None

            completeness_status[section_name] = {
                "is_complete": is_complete,
                "reason": reason,
                "content_length": word_count,
                "status": "complete" if is_complete else "incomplete",
            }
        return completeness_status

    def _determine_incompleteness_reason(
        self, section_name: str, content: str, word_count: int, min_words: int
    ) -> str:
        if word_count == 0:
            return f"{section_name.capitalize()} section is empty"
        if word_count < min_words:
            return (
                f"{section_name.capitalize()} section has insufficient details. "
                f"Currently {word_count} words, aim for at least {min_words}."
            )
        return f"{section_name.capitalize()} section incomplete"

    def generate_incomplete_section_feedback(
        self, sections: Dict[str, str]
    ) -> List[Dict]:
        completeness = self.check_section_completeness(sections)
        feedback_list = []
        for section_name, status in completeness.items():
            if not status["is_complete"]:
                feedback_item = {
                    "section": section_name,
                    "status": "incomplete",
                    "message": status["reason"],
                    "suggestion": self._get_section_suggestion(section_name),
                    "word_count": status["content_length"],
                }
                feedback_list.append(feedback_item)
        return feedback_list

    def _get_section_suggestion(self, section_name: str) -> str:
        suggestions = {
            "education": (
                "Add degree/qualification, institution name, graduation date, "
                "and GPA if relevant"
            ),
            "skills": (
                "List technical skills, tools, programming languages, "
                "and relevant certifications"
            ),
            "experience": (
                "Include job title, company name, dates, "
                "and 2-3 key achievements or responsibilities"
            ),
            "projects": (
                "Describe project name, technologies used, your role, "
                "and measurable outcomes"
            ),
        }
        return suggestions.get(
            section_name.lower(),
            f"Add more detailed information to {section_name} section",
        )

    # ----------------------------------------------------------------------
    # --- 🔴 MODIFIED FUNCTION (PENALTIES) 🔴 ---
    # ----------------------------------------------------------------------
    def generate_comprehensive_feedback(
        self, sections: Dict[str, str], validation: Dict
    ) -> Dict:
        incomplete_feedback = self.generate_incomplete_section_feedback(sections)
        strengths = self._generate_strengths(validation)
        suggestions = self._generate_suggestions(incomplete_feedback, validation)

        # --- NEW PENALTY LOGIC ---
        # We base the penalty on the *total number of suggestions*,
        # which correctly includes BOTH missing and incomplete sections.

        num_issues = len(suggestions)
        penalty_per_issue = 15  # Much stricter penalty

        completeness_penalty = num_issues * penalty_per_issue

        raw_completeness_score = int(validation.get("completeness_score", 0))

        # For the weak resume:
        # raw_score = 50 (for finding "education" and "skills")
        # num_issues = 4 (missing 2, incomplete 2)
        # penalty = 4 * 15 = 60
        # penalized_score = max(0, 50 - 60) = 0.
        # This is correct.
        penalized_completeness_score = max(
            0, raw_completeness_score - completeness_penalty
        )

        return {
            "strengths": strengths,
            "incomplete_sections": [
                {
                    "section": item["section"],
                    "message": item["message"],
                    "suggestion": item["suggestion"],
                }
                for item in incomplete_feedback
            ],
            "missing_sections": validation.get("missing_sections", []),
            "suggestions": suggestions,
            "overall_score": penalized_completeness_score,
            "completeness_percentage": raw_completeness_score,
        }

    def _generate_strengths(self, validation: Dict) -> List[str]:
        strengths = []
        if validation.get("has_all_required", False):
            strengths.append("All required sections are present")
        else:
            present_sections = validation.get("present_sections", [])
            if len(present_sections) > 0:
                strengths.append(
                    f"Found {len(present_sections)} sections: {', '.join(present_sections)}"
                )

        if not strengths:
            strengths.append("Resume submitted. Analysis in progress.")
        return strengths

    def _generate_suggestions(
        self, incomplete_feedback: List[Dict], validation: Dict
    ) -> List[str]:
        suggestions = []
        for item in incomplete_feedback:
            suggestions.append(
                f"Complete {item['section']} section: {item['suggestion']}"
            )
        for section in validation.get("missing_sections", []):
            suggestions.append(
                f"Add {section} section: {self._get_section_suggestion(section)}"
            )
        if not suggestions and validation.get("has_all_required", False):
            # Only add this if the resume is *already* good
            msg = "Consider adding quantifiable achievements to strengthen your resume"
            suggestions.append(msg)
        return suggestions[:5]

    # ----------------------------------------------------------------------
    # --- 🔴 MODIFIED ORCHESTRATOR (USES NEW WEIGHTS) 🔴 ---
    # ----------------------------------------------------------------------
    def generate_comprehensive_feedback_with_grammar(
        self,
        sections: Dict[str, str],
        validation: Dict,
        include_grammar: bool = True,
    ) -> Dict:
        logger.info("Generating comprehensive feedback with grammar + verb analysis")

        # 1. This dictionary has our keys: 'strengths', 'incomplete_sections', etc.
        base_feedback = self.generate_comprehensive_feedback(sections, validation)
        penalized_completeness_score = base_feedback.get("overall_score", 0)

        if include_grammar:
            try:
                # This external function *only* returns grammar data
                enhanced_feedback = enhance_feedback_with_grammar(
                    sections=sections,
                    base_feedback=base_feedback,
                )

                # --- 🐞 BUG FIX AREA START 🐞 ---

                # We get the new data from the other functions
                grammar_data = enhanced_feedback.get("grammar", {})
                verb_data = self._analyze_action_verbs(sections)

                # And we ADD IT to base_feedback, not enhanced_feedback
                base_feedback["grammar"] = grammar_data
                base_feedback["action_verbs"] = verb_data

                # Add grammar suggestions (if any)
                if grammar_data.get("total_errors", 0) > 0:
                    grammar_suggestion = f"Review {grammar_data['total_errors']} grammar/spelling issues in your resume."
                    # Add to base_feedback
                    base_feedback.setdefault("suggestions", []).insert(
                        0, grammar_suggestion
                    )

                # Add verb suggestions (if any)
                if verb_data.get("total_weak_verbs", 0) > 0:
                    # Add to base_feedback
                    base_feedback.setdefault("suggestions", []).extend(
                        verb_data["suggestions"]
                    )

                # --- FINAL SCORING LOGIC ---
                grammar_score = grammar_data.get("score", 0)
                verb_score = verb_data.get("overall_score", 0)

                final_overall_score = self._calculate_final_score(
                    penalized_completeness=penalized_completeness_score,
                    validation=validation,
                    grammar_score=grammar_score,
                    verb_score=verb_score,
                )

                # Add the final score to base_feedback
                base_feedback["overall_score"] = final_overall_score

                # --- 🐞 BUG FIX AREA END 🐞 ---

                logger.info(
                    f"Grammar + Verb analysis complete. Final Score: {final_overall_score}"
                )

                # Return the CORRECT, merged dictionary
                return base_feedback

            except Exception as e:
                # This block was already correctly modifying base_feedback
                logger.error(
                    f"Grammar analysis failed: {str(e)}. Calculating score without grammar."
                )
                base_feedback["grammar"] = {
                    "error": str(e),
                    "score": 0,
                    "message": "Grammar analysis unavailable",
                }

                grammar_score = 0
                verb_data = self._analyze_action_verbs(sections)
                base_feedback["action_verbs"] = verb_data
                verb_score = verb_data.get("overall_score", 0)

                final_overall_score = self._calculate_final_score(
                    penalized_completeness=penalized_completeness_score,
                    validation=validation,
                    grammar_score=grammar_score,
                    verb_score=verb_score,
                )

                base_feedback["overall_score"] = final_overall_score

                logger.info(
                    f"Grammar failed. Final Score (no grammar): {final_overall_score}"
                )
                return base_feedback

        else:
            # Grammar is disabled. Run scoring without it.
            logger.info(
                "Grammar analysis skipped, running action verb analysis and scoring"
            )

            grammar_score = 0
            verb_data = self._analyze_action_verbs(sections)
            base_feedback["action_verbs"] = verb_data
            verb_score = verb_data.get("overall_score", 0)

            # --- THIS IS THE FIX ---
            # Add verb suggestions even when grammar is off
            if verb_data.get("total_weak_verbs", 0) > 0:
                base_feedback.setdefault("suggestions", []).extend(
                    verb_data["suggestions"]
                )
            # --- End of fix ---

            final_overall_score = self._calculate_final_score(
                penalized_completeness=penalized_completeness_score,
                validation=validation,
                grammar_score=grammar_score,
                verb_score=verb_score,
            )

            base_feedback["overall_score"] = final_overall_score

            return base_feedback

    # ----------------------------------------------------------------------
    # --- 🔴 MODIFIED HELPER FUNCTION (FIX FOR 0 VERBS) 🔴 ---
    # ----------------------------------------------------------------------
    def _analyze_action_verbs(self, sections: dict) -> dict:
        """Analyze experience/project sections for weak verbs."""
        engine = ActionVerbEngine()
        all_suggestions = []
        section_scores = {}
        total_weak = 0
        total_verbs = 0
        for name, text in sections.items():
            if name.lower() in ["experience", "projects"]:
                result = engine.suggest(text)
                section_scores[name] = result["score"]
                total_weak += result["weak_verbs"]
                total_verbs += result["total_verbs"]
                for w, s in zip(result["found"], result["suggestions"]):
                    all_suggestions.append(
                        f"Replace weak verb '{w}' with stronger '{s}' in {name} section."
                    )

        # --- 🔴 BUG FIX 🔴 ---
        # If total_verbs is 0, the score must be 0, not 100.
        if total_verbs == 0:
            overall_score = 0
        else:
            overall_score = engine._calculate_action_verb_score(total_weak, total_verbs)
        # --- 🔴 END OF FIX 🔴 ---

        return {
            "overall_score": overall_score,
            "section_scores": section_scores,
            "total_weak_verbs": total_weak,
            "suggestions": all_suggestions,
        }


# ----------------------------------------------------------------------
# PDF + ANONYMIZATION (Unchanged from before)
# ----------------------------------------------------------------------
def anonymize_data(report: dict) -> dict:
    """Anonymizes sensitive PII in the report."""
    anonymized_report = report.copy()
    if "email" in anonymized_report:
        anonymized_report["email"] = mask_email(anonymized_report["email"])
    if "phone" in anonymized_report:
        anonymized_report["phone"] = mask_phone(anonymized_report["phone"])
    if "name" in anonymized_report:
        anonymized_report["name"] = "[Candidate Name Anonymized]"
    return anonymized_report


def generate_pdf_report(report_json: dict) -> bytes:
    """Implements PDF export using xhtml2pdf and Jinja2."""

    # 1. FIX TEMPLATE PATH
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        template_path = os.path.join(project_root, "templates", "report_template.html")

        if not os.path.exists(template_path):
            logger.error(f"Template not found at path: {template_path}")
            raise FileNotFoundError(
                f"PDF Template not found. Looked in: {template_path}"
            )

        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    except Exception as e:
        logger.error(f"Error reading PDF template: {e}")
        raise

    # NEW ROBUST MAPPING

    # Get the nested dictionaries first, with fallbacks.
    feedback_dict = report_json.get("feedback", {})
    validation_dict = report_json.get("validation", {})

    # Now build the context.

    template_context = {
        "name": report_json.get("name", "[Candidate]"),
        "email": report_json.get("email", "candidate@example.com"),
        "phone": report_json.get("phone", "555-555-5555"),
        # --- THIS IS THE FINAL FIX ---
        # It checks for the new logic's key, the mock data key, AND the data_service key
        "score": report_json.get(
            "overall_score",
            report_json.get("score", report_json.get("overallScore", 0)),
        ),
        # FIX for Match %: Checks MOCK_ANALYSIS key and data_service key
        "match_percentage": report_json.get(
            "match_percentage", validation_dict.get("keyword_match_score", 0)
        ),
        "feedback": {
            # FIX for Missing Sections: Checks new key and MOCK_ANALYSIS key
            "missingSections": feedback_dict.get(
                "missing_sections", feedback_dict.get("missingSections", [])
            ),
            # FIX for Suggestions: Checks data_service key and MOCK_ANALYSIS key
            "suggestions": report_json.get(
                "improvements", feedback_dict.get("suggestions", [])
            ),
        },
    }

    # 3. Anonymize the new, correctly-structured context
    safe_report_context = anonymize_data(template_context)

    # 4. Render the template
    template = Template(template_content)
    html_content = template.render(report=safe_report_context)

    # 5. Generate PDF
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html_content), dest=result)

    if not pdf.err:
        return result.getvalue()

    raise Exception(f"PDF Generation Error: {pdf.err}")
