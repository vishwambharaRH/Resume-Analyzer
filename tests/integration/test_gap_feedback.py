"""
Integration test for Gap Detection + Feedback
Test Case: DRA-67
"""

import pytest
from src.parser.text_extractor import TextExtractor
from src.parser.experience_parser import ExperienceParser
from src.parser.gap_detector import GapDetector


class TestGapDetectionIntegration:
    """Test complete flow: extract → parse → detect gaps"""

    def test_end_to_end_gap_detection(self, tmp_path):
        """Test complete gap detection flow with real file"""
        # Create test resume file
        resume_content = """
        John Doe
        Software Engineer
        
        WORK EXPERIENCE
        
        Senior Software Engineer
        TechCorp Inc
        January 2020 - December 2020
        - Developed web applications
        
        Software Engineer
        StartupXYZ
        June 2022 - Present
        - Built microservices
        
        EDUCATION
        BS Computer Science
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

        # Verify gap detected (18-month gap between Dec 2020 and June 2022)
        assert analysis["gap_count"] >= 1
        assert any(
            "18" in msg or "gap" in msg.lower() for msg in analysis["gap_feedback"]
        )
