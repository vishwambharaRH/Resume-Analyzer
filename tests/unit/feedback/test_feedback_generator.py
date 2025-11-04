"""
Unit Tests for Feedback Generator - DRA-48
Test Cases: TC-INCOMP-001 to TC-INCOMP-005, TC-FEED-001 to TC-FEED-008

Requirements:
- FR-003: Highlight incomplete sections
- STP: RPRS-F-003
- RTM: Feedback generation coverage
"""

import pytest
from src.feedback.feedback_generator import FeedbackGenerator


class TestIncompleteSectionDetection:
    """Unit tests for incomplete section detection"""

    @pytest.fixture
    def feedback_gen(self):
        """Initialize feedback generator"""
        return FeedbackGenerator()

    @pytest.fixture
    def complete_sections(self):
        """Sections with sufficient content"""
        return {
            "education": (
                "Bachelor of Science in Computer Science\n"
                "Stanford University, California\n"
                "Graduated: May 2020\n"
                "GPA: 3.8/4.0\n"
                "Relevant Coursework: Data Structures, Algorithms, Machine Learning"
            ),
            "skills": (
                "Python, JavaScript, React, FastAPI, Docker, Kubernetes, "
                "AWS, PostgreSQL, MongoDB, Git, CI/CD, Machine Learning"
            ),
            "experience": (
                "Software Engineer\n"
                "Google Inc., Mountain View, CA\n"
                "June 2020 - Present\n"
                "- Developed scalable REST APIs serving 1M+ users\n"
                "- Led team of 5 engineers on cloud migration\n"
                "- Reduced API latency by 40% through optimization"
            ),
            "projects": (
                "AI-Powered Resume Analyzer\n"
                "Built full-stack application using React and FastAPI\n"
                "Implemented NLP-based skill extraction using spaCy\n"
                "Deployed on AWS with 99.9% uptime"
            ),
        }

    @pytest.fixture
    def incomplete_sections(self):
        """Sections with insufficient content"""
        return {
            "education": "BS Computer Science",  # Too short
            "skills": "Python Java",  # Too few skills
            "experience": "Software Engineer",  # No details
            "projects": "",  # Empty
        }

    def test_detect_complete_sections(self, feedback_gen, complete_sections):
        """
        TC-INCOMP-001: Verify complete sections are not flagged

        Expected: All sections marked as complete
        """
        completeness = feedback_gen.check_section_completeness(complete_sections)

        assert completeness["education"]["is_complete"] is True
        assert completeness["skills"]["is_complete"] is True
        assert completeness["experience"]["is_complete"] is True
        assert completeness["projects"]["is_complete"] is True

    def test_detect_incomplete_education(self, feedback_gen):
        """
        TC-INCOMP-002: Detect incomplete education section

        Expected: Flagged as incomplete with specific reason
        """
        sections = {"education": "BS Computer Science"}

        completeness = feedback_gen.check_section_completeness(sections)

        assert completeness["education"]["is_complete"] is False
        assert "insufficient details" in completeness["education"]["reason"].lower()

    def test_detect_empty_section(self, feedback_gen):
        """
        TC-INCOMP-003: Detect empty section

        Expected: Flagged as empty
        """
        sections = {"projects": ""}

        completeness = feedback_gen.check_section_completeness(sections)

        assert completeness["projects"]["is_complete"] is False
        assert "empty" in completeness["projects"]["reason"].lower()

    def test_detect_multiple_incomplete_sections(
        self, feedback_gen, incomplete_sections
    ):
        """
        TC-INCOMP-004: Detect multiple incomplete sections

        Expected: All incomplete sections identified
        """
        completeness = feedback_gen.check_section_completeness(incomplete_sections)

        incomplete_count = sum(
            1 for status in completeness.values() if not status["is_complete"]
        )

        assert incomplete_count == 4  # All sections incomplete

    def test_generate_incomplete_feedback_messages(
        self, feedback_gen, incomplete_sections
    ):
        """
        TC-INCOMP-005: Generate feedback messages for incomplete sections

        Expected: Clear, actionable feedback for each incomplete section
        Requirements: NFR-004 (Meaningful error messages)
        """
        feedback = feedback_gen.generate_incomplete_section_feedback(
            incomplete_sections
        )

        assert len(feedback) == 4  # All sections incomplete
        assert all("message" in item for item in feedback)
        assert all("suggestion" in item for item in feedback)
        assert all("section" in item for item in feedback)

    def test_feedback_includes_suggestions(self, feedback_gen):
        """
        Test that feedback includes actionable suggestions

        Requirements: NFR-005 (Meaningful feedback)
        """
        sections = {"education": "BS CS"}

        feedback = feedback_gen.generate_incomplete_section_feedback(sections)

        assert len(feedback) == 1
        assert "suggestion" in feedback[0]
        assert len(feedback[0]["suggestion"]) > 20  # Meaningful suggestion

    def test_word_count_tracked(self, feedback_gen):
        """
        Test that word count is tracked for incomplete sections
        """
        sections = {"skills": "Python Java"}

        completeness = feedback_gen.check_section_completeness(sections)

        assert "content_length" in completeness["skills"]
        assert completeness["skills"]["content_length"] == 2

    def test_section_specific_suggestions(self, feedback_gen):
        """
        Test that suggestions are specific to section type

        Requirements: NFR-005
        """
        sections = {
            "education": "BSc",
            "skills": "Python",
            "experience": "Engineer",
            "projects": "App",
        }

        feedback = feedback_gen.generate_incomplete_section_feedback(sections)

        # Each section should have unique suggestion
        suggestions = [item["suggestion"] for item in feedback]
        assert len(set(suggestions)) == 4  # All unique


class TestComprehensiveFeedback:
    """Unit tests for comprehensive feedback generation"""

    @pytest.fixture
    def feedback_gen(self):
        """Initialize feedback generator"""
        return FeedbackGenerator()

    def test_generate_comprehensive_feedback(self, feedback_gen):
        """
        TC-FEED-001: Generate complete feedback structure

        Expected: Includes strengths, improvements, suggestions
        Requirements: NFR-009 (Balanced feedback)
        """
        sections = {
            "education": "BS Computer Science, MIT, 2020, GPA 3.8",
            "skills": "Python JavaScript React",
            "experience": "Software Engineer",  # Incomplete
            "projects": "",  # Empty
        }

        validation = {
            "has_all_required": True,
            "missing_sections": [],
            "present_sections": ["education", "skills", "experience", "projects"],
            "completeness_score": 100.0,
        }

        feedback = feedback_gen.generate_comprehensive_feedback(sections, validation)

        assert "strengths" in feedback
        assert "incomplete_sections" in feedback
        assert "suggestions" in feedback
        assert "overall_score" in feedback

    def test_balanced_feedback_tone(self, feedback_gen):
        """
        TC-FEED-002: Verify balanced positive/negative feedback

        Expected: Both strengths and improvements present
        Requirements: NFR-009 (Balanced tone)
        """
        sections = {
            "education": "Bachelor of Science in Computer Science, Stanford",
            "skills": "Python",  # Incomplete
            "experience": "Software Engineer at Google for 2 years",
            "projects": "",  # Empty
        }

        validation = {
            "has_all_required": True,
            "missing_sections": [],
            "present_sections": ["education", "skills", "experience", "projects"],
            "completeness_score": 100.0,
        }

        feedback = feedback_gen.generate_comprehensive_feedback(sections, validation)

        assert len(feedback["strengths"]) > 0
        assert len(feedback["incomplete_sections"]) > 0
        assert len(feedback["suggestions"]) > 0

    def test_score_penalty_for_incomplete_sections(self, feedback_gen):
        """
        TC-FEED-003: Verify score is reduced for incomplete sections

        Expected: Score reduced by 5 points per incomplete section
        """
        sections = {
            "education": "BS",  # Incomplete
            "skills": "Python",  # Incomplete
            "experience": "Engineer",  # Incomplete
            "projects": "",  # Empty/incomplete
        }

        validation = {
            "has_all_required": True,
            "missing_sections": [],
            "present_sections": ["education", "skills", "experience", "projects"],
            "completeness_score": 100.0,
        }

        feedback = feedback_gen.generate_comprehensive_feedback(sections, validation)

        # 100 - (4 incomplete * 5 points) = 80
        assert feedback["overall_score"] == 80

    def test_suggestions_limited_to_five(self, feedback_gen):
        """
        Test that suggestions are limited to top 5

        Requirements: NFR-006 (Minimize cognitive overload)
        """
        sections = {"education": "BS", "skills": "P", "experience": "E", "projects": ""}

        validation = {
            "has_all_required": False,
            "missing_sections": ["certifications", "awards"],
            "present_sections": ["education", "skills", "experience", "projects"],
            "completeness_score": 50.0,
        }

        feedback = feedback_gen.generate_comprehensive_feedback(sections, validation)

        assert len(feedback["suggestions"]) <= 5
