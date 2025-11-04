"""
Feedback Generator Module - FR-003 Implementation
Generates structured feedback for incomplete sections

Requirements:
- FR-003: Highlight incomplete sections
- NFR-005: Meaningful error messages
- STP: RPRS-F-003
"""

from typing import Dict, List
from src.parser.section_detector import SectionDetector, SectionType


class FeedbackGenerator:
    """
    Generates feedback for resume analysis

    Methods:
        generate_incomplete_section_feedback: Create feedback for incomplete sections
        generate_comprehensive_feedback: Complete feedback with strengths/improvements
    """

    def __init__(self):
        self.section_detector = SectionDetector()

    def check_section_completeness(self, sections: Dict[str, str]) -> Dict[str, Dict]:
        """
        Check completeness of each section

        Args:
            sections: Dictionary of section name -> content

        Returns:
            Dictionary with completeness status for each section
            Example:
            {
                "education": {
                    "is_complete": False,
                    "reason": "Education section has insufficient details",
                    "content_length": 5
                }
            }

        Requirements: FR-003 (SRS)
        Test Cases: TC-INCOMP-001 to TC-INCOMP-005
        """
        completeness_status = {}

        for section_name, content in sections.items():
            try:
                section_type = SectionType(section_name.lower())
            except ValueError:
                # Skip non-standard sections
                continue

            is_complete = self.section_detector.is_section_complete(
                content, section_type, min_words=10
            )

            # Analyze why section is incomplete
            word_count = len([word for word in content.split() if len(word) > 2])

            if not is_complete:
                reason = self._determine_incompleteness_reason(
                    section_name, content, word_count
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
        self, section_name: str, content: str, word_count: int
    ) -> str:
        """
        Determine why a section is incomplete

        Args:
            section_name: Name of the section
            content: Section content
            word_count: Number of meaningful words

        Returns:
            Human-readable reason string

        Requirements: NFR-004 (Meaningful error messages)
        """
        # Empty or near-empty section
        if word_count == 0:
            return f"{section_name.capitalize()} section is empty"

        if word_count < 5:
            return f"{section_name.capitalize()} section has insufficient details"

        # Only has header, no real content
        if word_count < 10:
            return (
                f"{section_name.capitalize()} section needs more information. "
                f"Currently only {word_count} words."
            )


        return f"{section_name.capitalize()} section incomplete"

    def generate_incomplete_section_feedback(
        self, sections: Dict[str, str]
    ) -> List[Dict]:
        """
        Generate feedback messages for incomplete sections

        Args:
            sections: Dictionary of section name -> content

        Returns:
            List of feedback dictionaries
            Example:
            [
                {
                    "section": "education",
                    "status": "incomplete",
                    "message": "Education section has insufficient details",
                    "suggestion": "Add degree, institution, and graduation date"
                }
            ]

        Requirements: FR-003, NFR-005
        Test Cases: TC-INCOMP-001, TC-INCOMP-002
        """
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
        """
        Get actionable suggestion for improving a section

        Args:
            section_name: Name of the incomplete section

        Returns:
            Specific suggestion for the section

        Requirements: NFR-005 (Meaningful feedback)
        """
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

    def generate_comprehensive_feedback(
        self, sections: Dict[str, str], validation: Dict
    ) -> Dict:
        """
        Generate complete feedback including strengths and improvements

        Args:
            sections: Parsed resume sections
            validation: Validation results from SectionDetector

        Returns:
            Comprehensive feedback dictionary
            {
                "strengths": [...],
                "incomplete_sections": [...],
                "missing_sections": [...],
                "suggestions": [...],
                "overall_score": int
            }

        Requirements: FR-003, NFR-005, NFR-009 (Balanced feedback)
        Test Cases: TC-FEED-001 to TC-FEED-008
        """
        incomplete_feedback = self.generate_incomplete_section_feedback(sections)

        # Calculate scores
        total_sections = 4  # Required: education, skills, experience, projects
        complete_count = sum(
            1
            for section in sections.values()
            if self.section_detector.is_section_complete(
                section,
                SectionType.EDUCATION,  # Type doesn't matter for counting
                min_words=10,
            )
        )

        # Deduct points for incomplete sections
        completeness_penalty = len(incomplete_feedback) * 5
        overall_score = max(
            0, int(validation.get("completeness_score", 0)) - completeness_penalty
        )

        # Generate strengths (balanced feedback per NFR-009)
        strengths = self._generate_strengths(validation, complete_count, total_sections)

        # Generate improvement suggestions
        suggestions = self._generate_suggestions(incomplete_feedback, validation)

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
            "overall_score": overall_score,
            "completeness_percentage": validation.get("completeness_score", 0),
        }

    def _generate_strengths(
        self, validation: Dict, complete_count: int, total_sections: int
    ) -> List[str]:
        """
        Generate positive feedback (NFR-009: Balanced tone)

        Args:
            validation: Validation results
            complete_count: Number of complete sections
            total_sections: Total required sections

        Returns:
            List of strength statements
        """
        strengths = []

        if validation.get("has_all_required", False):
            strengths.append("All required sections are present")

        if complete_count >= 3:
            msg = (
                f"{complete_count} out of {total_sections} sections "
                "have sufficient detail"
            )
            strengths.append(msg)


        if len(validation.get("present_sections", [])) > 0:
            strengths.append("Resume has clear structure and organization")

        if not strengths:
            strengths.append("Resume submission received successfully")

        return strengths

    def _generate_suggestions(
        self, incomplete_feedback: List[Dict], validation: Dict
    ) -> List[str]:
        """
        Generate actionable improvement suggestions

        Args:
            incomplete_feedback: List of incomplete section feedback
            validation: Validation results

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Suggestions for incomplete sections
        for item in incomplete_feedback:
            suggestions.append(
                f"Complete {item['section']} section: {item['suggestion']}"
            )

        # Suggestions for missing sections
        for section in validation.get("missing_sections", []):
            suggestions.append(
                f"Add {section} section: {self._get_section_suggestion(section)}"
            )

        # General suggestions
        if len(suggestions) == 0:
            suggestions.append(
                "Consider adding quantifiable achievements to strengthen " "your resume"
            )

        return suggestions[:5]  # Limit to top 5 suggestions
