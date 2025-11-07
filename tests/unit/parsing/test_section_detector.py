"""
Unit Tests for Section Detection - DRA-45
Test Cases: TC-MISS-001 to TC-MISS-005

Requirements:
- STP RPRS-F-007: Flagging of missing sections
- RTM: Test coverage for FR-010
- SRS: FR-010 validation
"""

import pytest
from src.parser.section_detector import SectionDetector, SectionType


class TestSectionDetection:
    """
    Unit tests for section detection logic
    Covers TC-MISS-001 to TC-MISS-005
    """

    @pytest.fixture
    def detector(self):
        """Initialize section detector"""
        return SectionDetector()

    @pytest.fixture
    def complete_resume(self):
        """Sample resume with all sections"""
        return """
        JOHN DOE
        Email: john@example.com | Phone: +1-555-0123
        
        EDUCATION
        Bachelor of Science in Computer Science
        Stanford University, 2020
        GPA: 3.8/4.0
        
        SKILLS
        Python, JavaScript, React, FastAPI, Machine Learning,
        TensorFlow, Docker, Kubernetes, AWS, Git, CI/CD
        
        EXPERIENCE
        Software Engineer at Google
        2020 - Present
        - Developed scalable APIs serving 1M+ users
        - Led team of 5 engineers
        - Reduced latency by 40%
        
        PROJECTS
        AI Chatbot using NLP
        - Built using Python and spaCy
        - Deployed on AWS with 99.9% uptime
        - Handles 10k requests/day
        """

    @pytest.fixture
    def missing_skills_resume(self):
        """Resume missing skills section"""
        return """
        JOHN DOE
        john@example.com
        
        EDUCATION
        BS Computer Science, MIT, 2020
        GPA: 3.9/4.0
        
        EXPERIENCE
        Software Engineer at Facebook
        2020-2022
        Developed React components
        
        PROJECTS
        Web application development
        E-commerce platform with 1000+ users
        """

    @pytest.fixture
    def multiple_missing_resume(self):
        """Resume with multiple missing sections"""
        return """
        JOHN DOE
        
        EDUCATION
        BS Computer Science
        Harvard University
        """

    @pytest.fixture
    def resume_with_duplicates(self):
        """
        A resume with duplicate and synonymous sections
        to test the FR-005 merge logic.
        """
        return """
        SUMMARY
        A senior developer.

        SKILLS
        Python, Java, C++

        EXPERIENCE
        My Job 1 at Company A
        
        TECHNICAL SKILLS
        SQL, Docker, Git
        
        Work Experience
        My Job 2 at Company B
        """

    # TC-MISS-001: Test detection when all sections present
    def test_detect_all_sections_present(self, detector, complete_resume):
        """
        TC-MISS-001: Verify all sections detected when present

        Expected: All sections detected = True
        Requirements: SRS FR-010
        """
        detected = detector.detect_sections(complete_resume)

        assert detected["education"] is True, "Education should be detected"
        assert detected["skills"] is True, "Skills should be detected"
        assert detected["experience"] is True, "Experience should be detected"
        assert detected["projects"] is True, "Projects should be detected"
        assert detected["contact"] is True, "Contact should be detected"

    # TC-MISS-002: Test detection of missing skills section
    def test_detect_missing_skills_section(self, detector, missing_skills_resume):
        """
        TC-MISS-002: Verify missing skills section is detected

        Expected: skills = False, others = True
        Requirements: FR-010 (SRS), STP RPRS-F-007
        """
        detected = detector.detect_sections(missing_skills_resume)

        assert detected["skills"] is False, "Skills section should NOT be detected"
        assert detected["education"] is True, "Education should be detected"
        assert detected["experience"] is True, "Experience should be detected"
        assert detected["projects"] is True, "Projects should be detected"

    # TC-MISS-003: Test finding missing sections
    def test_find_missing_sections_with_skills_absent(
        self, detector, missing_skills_resume
    ):
        """
        TC-MISS-003: Verify find_missing_sections() returns correct list

        Expected: Returns ["skills"]
        Requirements: FR-010
        """
        missing = detector.find_missing_sections(missing_skills_resume)

        assert "skills" in missing, "Skills should be in missing list"
        assert len(missing) == 1, "Only skills should be missing"

    # TC-MISS-004: Test multiple missing sections
    def test_find_missing_multiple_sections(self, detector, multiple_missing_resume):
        """
        TC-MISS-004: Verify multiple missing sections are identified

        Expected: Returns all missing section names
        Requirements: FR-010, NFR-005
        """
        missing = detector.find_missing_sections(multiple_missing_resume)

        assert "skills" in missing, "Skills should be missing"
        assert "experience" in missing, "Experience should be missing"
        assert "projects" in missing, "Projects should be missing"
        assert len(missing) == 3, "Three sections should be missing"

    # TC-MISS-005: Test section completeness
    def test_section_completeness_sufficient_content(self, detector):
        """
        TC-MISS-005: Verify section completeness check works

        Expected: Section with >10 meaningful words = complete
        Requirements: FR-007 (incomplete sections)
        """
        section_text = """
        SKILLS
        Python, JavaScript, React, FastAPI, Docker, Kubernetes,
        Machine Learning, TensorFlow, AWS, Git, CI/CD, PostgreSQL
        """

        is_complete = detector.is_section_complete(
            section_text, SectionType.SKILLS, min_words=10
        )

        assert is_complete is True, "Section should be complete"

    def test_section_completeness_insufficient_content(self, detector):
        """
        Test incomplete section (only header, minimal content)

        Expected: incomplete = True
        """
        section_text = """
        SKILLS
        Python
        """

        is_complete = detector.is_section_complete(
            section_text, SectionType.SKILLS, min_words=10
        )

        assert is_complete is False, "Section should be incomplete"

    def test_empty_resume_all_missing(self, detector):
        """
        Edge case: Empty resume should report all sections missing
        """
        missing = detector.find_missing_sections("")

        assert len(missing) == 4, "All 4 required sections should be missing"
        assert "education" in missing
        assert "skills" in missing
        assert "experience" in missing
        assert "projects" in missing

    def test_validate_resume_structure_complete(self, detector, complete_resume):
        """
        Test comprehensive validation for complete resume

        Expected: has_all_required = True, score = 100
        """
        validation = detector.validate_resume_structure(complete_resume)

        assert validation["has_all_required"] is True
        assert validation["completeness_score"] == 100.0
        assert len(validation["missing_sections"]) == 0
        assert len(validation["present_sections"]) >= 4

    def test_validate_resume_structure_missing_skills(
        self, detector, missing_skills_resume
    ):
        """
        Test validation with one missing section

        Expected: has_all_required = False, score = 75
        """
        validation = detector.validate_resume_structure(missing_skills_resume)

        assert validation["has_all_required"] is False
        assert validation["completeness_score"] == 75.0
        assert "skills" in validation["missing_sections"]
        assert len(validation["missing_sections"]) == 1

    def test_case_insensitive_detection(self, detector):
        """
        Verify detection works regardless of case
        """
        resume = """
        education
        BS Computer Science
        
        SKILLS
        Python, Java
        
        Experience
        Software Developer
        
        projects
        Web app
        """

        detected = detector.detect_sections(resume)

        assert detected["education"] is True
        assert detected["skills"] is True
        assert detected["experience"] is True
        assert detected["projects"] is True

    def test_alternate_section_headers(self, detector):
        """
        Test detection of alternate section names
        (e.g., "Technical Skills" vs "Skills")
        """
        resume = """
        ACADEMIC BACKGROUND
        MS Computer Science
        
        TECHNICAL SKILLS & COMPETENCIES
        Python, AI, ML
        
        PROFESSIONAL EXPERIENCE
        Senior Engineer
        
        ACADEMIC PROJECTS
        Thesis on NLP
        """

        detected = detector.detect_sections(resume)

        # Should detect despite different wording
        assert detected["education"] is True
        assert detected["skills"] is True
        assert detected["experience"] is True
        assert detected["projects"] is True

    def test_whitespace_only_resume(self, detector):
        """
        Edge case: Resume with only whitespace
        """
        resume = "   \n\n   \t\t   \n   "

        detected = detector.detect_sections(resume)

        # All should be False
        assert all(not found for found in detected.values())

    def test_completeness_score_calculation(self, detector):
        """
        Test completeness score calculation accuracy
        """
        # 3 out of 4 required sections = 75%
        resume = """
        EDUCATION
        BS CS
        
        SKILLS
        Python
        
        EXPERIENCE
        Engineer
        """

        validation = detector.validate_resume_structure(resume)

        # Missing projects = 75% complete
        assert validation["completeness_score"] == 75.0

    def test_fr005_get_canonical_type(self, detector):
        """
        Unit test for the _get_canonical_type helper.
        Ensures synonyms map to the correct SectionType.
        """
        assert detector._get_canonical_type("SKILLS") == SectionType.SKILLS
        assert detector._get_canonical_type("Technical Skills") == SectionType.SKILLS
        assert detector._get_canonical_type("Work Experience") == SectionType.EXPERIENCE
        assert (
            detector._get_canonical_type("PROFESSIONAL EXPERIENCE")
            == SectionType.EXPERIENCE
        )
        assert detector._get_canonical_type("Unknown Header") is None

    def test_fr005_split_and_merge_sections(self, detector, resume_with_duplicates):
        """
        (Subtask 2) Unit test for the core merge logic.
        Tests _split_and_merge_sections directly.
        """
        merged = detector._split_and_merge_sections(resume_with_duplicates)

        # AC: No duplicate section titles
        # Should merge down to 3 sections: summary, skills, experience
        assert "summary" in merged
        assert "skills" in merged
        assert "experience" in merged
        assert len(merged) == 3

        # AC: Merge their content into one section
        # AC: Content must not be lost
        skills_content = merged["skills"]
        exp_content = merged["experience"]

        assert "Python, Java, C++" in skills_content
        assert "SQL, Docker, Git" in skills_content
        assert skills_content.count("\n\n") == 1  # Check for clean merge

        assert "My Job 1 at Company A" in exp_content
        assert "My Job 2 at Company B" in exp_content
        assert exp_content.count("\n\n") == 1

    def test_fr005_validate_structure_with_merge(
        self, detector, resume_with_duplicates
    ):
        """
        (Subtask 3) Tests that the public validate_resume_structure
        method correctly uses the merge logic.
        """
        report = detector.validate_resume_structure(resume_with_duplicates)

        # Check that the main report is based on *merged* data
        assert "skills" in report["present_sections"]
        assert "experience" in report["present_sections"]
        assert "summary" in report["present_sections"]

        # Check that missing sections are correctly identified
        # (Education and Projects are missing)
        assert "education" in report["missing_sections"]
        assert "projects" in report["missing_sections"]
        assert len(report["missing_sections"]) == 2

        # Check completeness score (2/4 required are present)
        assert report["completeness_score"] == 50.0

        # AC: Merged sections in report
        # Check that the new 'merged_sections' dict is in the report
        assert "merged_sections" in report
        assert "skills" in report["merged_sections"]
        assert "Python, Java, C++" in report["merged_sections"]["skills"]
        assert "SQL, Docker, Git" in report["merged_sections"]["skills"]
