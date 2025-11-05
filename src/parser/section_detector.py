"""
Section Detection Module - FR-002 Implementation
Implements FR-010: Detect missing sections in resume

Requirements Addressed:
- SRS FR-010: Detect missing sections
- SAD: Parsing Engine component
- STP: RPRS-F-007
- RTM: TC-MISS-001 to TC-MISS-005
"""

import re
from typing import Dict, List
from enum import Enum


class SectionType(Enum):
    """Required resume sections as per SRS"""

    EDUCATION = "education"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    CONTACT = "contact"


# Section header patterns (regex) - cached in Redis per SW-004
SECTION_PATTERNS = {
    SectionType.EDUCATION: [
        r"\b(education|academic|qualification|degree|university|college)\b",
        r"\b(bachelor|master|phd|bs|ms|mba|be|btech|mtech)\b",
    ],
    SectionType.SKILLS: [
        r"\b(skills?|technical skills?|core competenc|technologies?)\b",
        r"\b(expertise|proficienc|capabilities)\b",
    ],
    SectionType.EXPERIENCE: [
        r"\b(experience|employment|work history|professional)\b",
        r"\b(career|positions?|jobs?)\b",
    ],
    SectionType.PROJECTS: [
        r"\b(projects?|portfolio|work samples?)\b",
        r"\b(academic projects?|personal projects?)\b",
    ],
    SectionType.CONTACT: [
        r"\b(contact|email|phone|mobile|address)\b",
        r"[\w\.-]+@[\w\.-]+\.\w+",  # Email pattern
        r"\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # Phone
    ],
}


class SectionDetector:
    """
    Detects and validates resume sections

    Methods:
        detect_sections: Identify present sections in resume text
        find_missing_sections: List missing required sections
        is_section_complete: Check if section has meaningful content
        validate_resume_structure: Comprehensive validation
    """

    def __init__(self):
        self.required_sections = {
            SectionType.EDUCATION,
            SectionType.SKILLS,
            SectionType.EXPERIENCE,
            SectionType.PROJECTS,
        }

    def detect_sections(self, resume_text: str) -> Dict[str, bool]:
        """
        Detect which sections are present in resume

        Args:
            resume_text: Full resume text (extracted by parsing engine)

        Returns:
            Dictionary mapping section names to presence boolean
            Example: {"education": True, "skills": False, ...}

        Test Cases: TC-MISS-001, TC-MISS-002
        Requirements: SRS FR-010
        """
        if not resume_text or len(resume_text.strip()) == 0:
            return {section.value: False for section in SectionType}

        resume_lower = resume_text.lower()
        detected = {}

        for section_type in SectionType:
            patterns = SECTION_PATTERNS[section_type]
            section_found = False

            for pattern in patterns:
                if re.search(pattern, resume_lower, re.IGNORECASE):
                    section_found = True
                    break

            detected[section_type.value] = section_found

        return detected

    def find_missing_sections(
        self, resume_text: str, required_only: bool = True
    ) -> List[str]:
        """
        Find missing sections in resume

        Args:
            resume_text: Full resume text
            required_only: If True, only check required sections

        Returns:
            List of missing section names
            Example: ["skills", "projects"]

        Test Cases: TC-MISS-003, TC-MISS-004
        Requirements: FR-010 (SRS), SAD Matching Engine
        """
        detected = self.detect_sections(resume_text)

        sections_to_check = (
            self.required_sections if required_only else set(SectionType)
        )

        missing = [
            section.value
            for section in sections_to_check
            if not detected.get(section.value, False)
        ]

        return sorted(missing)

    def is_section_complete(
        self, section_text: str, section_type: SectionType, min_words: int = 10
    ) -> bool:
        """
        Check if section has meaningful content (not just header)

        Args:
            section_text: Text content of the section
            section_type: Type of section being checked
            min_words: Minimum word count for completeness

        Returns:
            True if section is complete, False if incomplete

        Test Cases: TC-MISS-005
        Requirements: FR-007 (Flag incomplete sections)
        """
        if not section_text:
            return False

        # Remove section header from word count
        for pattern in SECTION_PATTERNS[section_type]:
            section_text = re.sub(
                pattern,
                "",
                section_text,
                flags=re.IGNORECASE
            )

        # Count meaningful words (exclude common filler)
        words = [
            word
            for word in section_text.split()
            if len(word) > 2 and word.lower() not in {
                "the", "and", "for", "with"
            }
        ]

        return len(words) >= min_words

    def validate_resume_structure(self, resume_text: str) -> Dict:
        """
        Comprehensive resume structure validation

        Returns:
            {
                "has_all_required": bool,
                "missing_sections": List[str],
                "incomplete_sections": List[str],
                "present_sections": List[str],
                "completeness_score": float  # 0-100
            }

        Requirements: FR-010, NFR-005 (Meaningful feedback)
        RTM: Component-level traceability for Matching Engine
        """
        detected = self.detect_sections(resume_text)
        missing = self.find_missing_sections(resume_text, required_only=True)

        present = [section for section, found in detected.items() if found]

        # Calculate completeness score
        total_required = len(self.required_sections)
        present_required = total_required - len(missing)
        completeness_score = (present_required / total_required) * 100

        return {
            "has_all_required": len(missing) == 0,
            "missing_sections": missing,
            "incomplete_sections": [],  # Populated by parsing engine
            "present_sections": present,
            "completeness_score": round(
                completeness_score, 2
            ),
        }
