"""
Parser Integration Module
Integrates section detection with parsing engine (FR-007 extraction)
"""
from typing import Dict, List
from src.parser.section_detector import SectionDetector, SectionType


class ResumeParser:
    """
    Extended resume parser with section detection
    Integrates DRA-44 with existing FR-001 parsing
    """

    def __init__(self):
        self.section_detector = SectionDetector()

    def parse_resume(self, file_path: str) -> Dict:
        """
        Parse resume and detect missing sections

        Args:
            file_path: Path to uploaded resume file

        Returns:
            {
                "sections": {...},  # Extracted sections (FR-007)
                "validation": {...},  # Section validation (FR-010)
                "metadata": {...}
            }

        Test Case: TC-PARSE-001 to TC-PARSE-015, TC-MISS-001 to TC-MISS-005
        """
        # Step 1: Extract text (uses PyMuPDF/python-docx from FR-001)
        resume_text = self._extract_text(file_path)

        # Step 2: Parse sections (FR-007)
        sections = self._extract_sections(resume_text)

        # Step 3: Detect missing sections (FR-010)
        validation = self.section_detector.validate_resume_structure(
            resume_text
        )

        # Step 4: Check section completeness
        validation["incomplete_sections"] = self._check_completeness(sections)

        return {
            "sections": sections,
            "validation": validation,
            "metadata": {
                "total_words": len(resume_text.split()),
                "total_chars": len(resume_text),
            },
        }

    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF/DOCX/TXT (implemented in FR-001)"""
        # Uses PyMuPDF for PDF, python-docx for DOCX
        # Placeholder - actual implementation in parsing_engine.py
        return ""

    def _extract_sections(self, text: str) -> Dict:
        """Extract individual sections (FR-007)"""
        # Placeholder - actual implementation in parsing_engine.py
        return {}

    def _check_completeness(self, sections: Dict) -> List[str]:
        """Check which sections are incomplete"""
        incomplete = []

        for section_name, content in sections.items():
            try:
                section_type = SectionType(section_name)
                if not self.section_detector.is_section_complete(
                    content,
                    section_type
                ):
                    incomplete.append(section_name)
            except ValueError:
                continue  # Skip non-standard sections

        return incomplete
