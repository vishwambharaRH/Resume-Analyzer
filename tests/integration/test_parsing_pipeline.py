import pytest
from pathlib import Path

# Import all the real components
from src.parser.skill_parser import get_text_from_parser, extract_skills
from src.parser.section_detector import SectionDetector

# Path to our test file
TEST_RESUME_PATH = Path("tests/test_resumes/resume.pdf")


@pytest.fixture(scope="module")
def extracted_text():
    """
    A fixture that runs once, parses the real test resume,
    and returns its text content.
    """
    if not TEST_RESUME_PATH.exists():
        pytest.skip(f"Test resume not found at {TEST_RESUME_PATH}")

    text = get_text_from_parser(TEST_RESUME_PATH)
    assert text is not None
    assert len(text.strip()) > 0, "Test resume file is empty"
    return text


def test_skill_parser_integration(extracted_text):
    """
    Tests that the real extract_skills function
    can find skills in the real parsed text.
    """
    # Run the skill parser on the real text
    skill_report = extract_skills(extracted_text)

    # --- IMPORTANT ---
    # You MUST update these assertions to match
    # the skills in your 'resume.pdf' file.

    assert "technical_skills" in skill_report
    assert "Python" in skill_report["technical_skills"]
    assert "JavaScript" in skill_report["technical_skills"]


def test_section_detector_integration(extracted_text):
    """
    Tests that the real SectionDetector
    can find sections in the real parsed text.
    """
    # Run the section detector on the real text
    detector = SectionDetector()
    structure_report = detector.validate_resume_structure(extracted_text)

    # --- IMPORTANT ---
    # You MUST update these assertions to match
    # the sections in your 'resume.pdf' file.

    assert "missing_sections" in structure_report
    assert "present_sections" in structure_report

    # Example: Check that it found the 'education' section
    assert "education" in structure_report["present_sections"]


# --- ADD THIS NEW TEST FOR FR-005 ---


def test_fr005_section_detector_merge_integration():
    """
    Tests that the real SectionDetector correctly integrates
    the new merge logic (FR-005).

    This test uses a mock text string to guarantee
    duplicates are present for testing.
    """
    # 1. Define mock text with duplicates
    mock_resume_with_duplicates = """
    EDUCATION
    My University
    
    SKILLS
    Python, Java, C++
    
    EXPERIENCE
    My Job 1 at Company A
    
    TECHNICAL SKILLS
    SQL, Docker, Git
    
    Work Experience
    My Job 2 at Company B
    """

    # 2. Run the section detector on this mock text
    detector = SectionDetector()
    structure_report = detector.validate_resume_structure(mock_resume_with_duplicates)

    # --- 3. Assertions for FR-005 ---

    # AC: Check that the new 'merged_sections' key exists
    assert (
        "merged_sections" in structure_report
    ), "FR-005: 'merged_sections' key is missing"

    merged_content = structure_report["merged_sections"]

    # AC: Check for no duplicate titles
    assert "skills" in merged_content
    assert "experience" in merged_content
    assert "education" in merged_content

    # AC: Check that content is merged and not lost
    skills_content = merged_content["skills"]
    exp_content = merged_content["experience"]

    assert "Python, Java, C++" in skills_content
    assert "SQL, Docker, Git" in skills_content
    assert "My Job 1 at Company A" in exp_content
    assert "My Job 2 at Company B" in exp_content

    # Also check the *rest* of the report to ensure
    # it's based on the merged data.

    # 'present_sections' should list canonical names
    assert "skills" in structure_report["present_sections"]
    assert "experience" in structure_report["present_sections"]

    # 'missing_sections' should be correct
    assert "projects" in structure_report["missing_sections"]
    assert "skills" not in structure_report["missing_sections"]

    # Score should be based on merged sections (2/4 required)
    assert structure_report["completeness_score"] == 75.0
