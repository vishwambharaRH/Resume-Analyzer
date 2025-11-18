"""
Integration test for complete FR-009 flow
"""

import pytest
from pathlib import Path
from src.parser.text_extractor import TextExtractor
from src.parser.experience_parser import ExperienceParser
from src.parser.gap_detector import GapDetector


@pytest.mark.asyncio
async def test_fr009_complete_flow(tmp_path):
    """Test complete FR-009: Text extraction → Experience parsing → Gap detection"""

    # Create test resume file
    resume_content = """
    John Doe
    Software Engineer
    
    EXPERIENCE
    
    Senior Software Engineer
    TechCorp Inc
    January 2020 - December 2020
    Developed cloud applications
    
    Software Engineer
    StartupXYZ
    June 2022 - Present
    Built microservices
    
    EDUCATION
    BS Computer Science
    MIT
    """

    # Save to temp file
    test_file = tmp_path / "test_resume.txt"
    test_file.write_text(resume_content)

    # Step 1: Extract text
    extractor = TextExtractor()
    text = extractor.extract_text(str(test_file))
    assert text is not None
    assert "TechCorp" in text

    # Step 2: Parse experience
    parser = ExperienceParser()
    experience = parser.parse_experience_section(text)
    assert len(experience) >= 2

    # Step 3: Detect gaps
    detector = GapDetector()
    analysis = detector.analyze_resume(text, experience)

    # Verify gap detected (18 months between Dec 2020 and June 2022)
    assert analysis["gap_count"] >= 1
    assert analysis["word_count"] > 0
    assert "gap_feedback" in analysis
