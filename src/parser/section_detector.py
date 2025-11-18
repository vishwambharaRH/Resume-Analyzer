"""
Section Detection Module - FR-002 Implementation
Implements FR-010: Detect missing sections in resume
Implements FR-005: Detect and merge duplicate sections
"""

import re
from typing import Dict, List, Any
from enum import Enum
from src.utils.perf import timeit


class SectionType(Enum):
    """Required resume sections as per SRS"""

    EDUCATION = "education"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    CONTACT = "contact"
    SUMMARY = "summary"  # Added for new merge logic


# === LOGIC FOR FR-010 (Original Keyword Detection) ===
# This is your original, proven logic for keyword scanning.
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
    SectionType.SUMMARY: [  # Added for consistency, used by FR-005
        r"\b(summary|objective|profile|about me|professional summary)\b",
    ],
}


# === LOGIC FOR FR-005 (New Merge Logic) ===
# These patterns are for *merging* and MUST match headers,
# not keywords.
MERGE_HEADER_SYNONYMS = {
    # Canonical Name -> List of synonyms
    "summary": ["summary", "objective", "profile", "professional summary"],
    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "technical skills & competencies",
    ],
    "experience": [
        "experience",
        "employment",
        "work experience",
        "professional experience",
    ],
    "projects": ["projects", "portfolio", "personal projects", "academic projects"],
    "education": ["education", "academic background"],
}

# Reverse map for quick lookup: "technical skills" -> "skills"
CANONICAL_HEADER_MAP = {
    synonym.lower(): canonical
    for canonical, synonyms in MERGE_HEADER_SYNONYMS.items()
    for synonym in synonyms
}


class SectionDetector:
    """
    Detects and validates resume sections
    """

    def __init__(self):
        # This is the original set of *required* sections for FR-010
        self.required_sections = {
            SectionType.EDUCATION,
            SectionType.SKILLS,
            SectionType.EXPERIENCE,
            SectionType.PROJECTS,
        }

    # --- ORIGINAL METHODS (FR-010) - DO NOT CHANGE ---
    # These methods use SECTION_PATTERNS (keyword search)
    # and are required for your original tests to pass.

    def detect_sections(self, resume_text: str) -> Dict[str, bool]:
        """
        Detect which sections are present in resume (Keyword-based)
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
        Find missing sections in resume (Keyword-based)
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

    @timeit("is_section_complete")
    def is_section_complete(
        self, section_text: str, section_type: SectionType, min_words: int = 10
    ) -> bool:
        """
        Check if section has meaningful content (not just header)
        """
        if not section_text:
            return False

        for pattern in SECTION_PATTERNS[section_type]:
            section_text = re.sub(pattern, "", section_text, flags=re.IGNORECASE)

        words = [
            word
            for word in section_text.split()
            if (len(word) > 2 and word.lower() not in {"the", "and", "for", "with"})
        ]

        return len(words) >= min_words

    # --- NEW METHOD (FR-005) ---

    def _split_and_merge_sections(self, resume_text: str) -> Dict[str, str]:
        """
        (Subtask 1: Duplicate detection & merge logic - FR-005)

        Splits text by headers defined in CANONICAL_HEADER_MAP
        and merges their content. (Line-parser-based)
        """
        merged_sections = {}
        current_canonical: str | None = None
        current_content: List[str] = []

        def save_previous_section():
            """Helper to save the content for the current_canonical."""
            if not current_canonical:
                return

            content_str = "\n".join(current_content).strip()
            if content_str:  # Only save if there is content
                if current_canonical not in merged_sections:
                    merged_sections[current_canonical] = content_str
                else:
                    # This is a duplicate, merge it
                    merged_sections[current_canonical] += "\n\n" + content_str

        for line in resume_text.split("\n"):
            line_clean = line.strip().lower()

            # Check if this line IS a header in our merge list
            if line_clean in CANONICAL_HEADER_MAP:
                # 1. Save the previous section
                save_previous_section()

                # 2. Start new section
                current_canonical = CANONICAL_HEADER_MAP[line_clean]
                current_content = []

            elif current_canonical:
                # 3. This is content, append it
                current_content.append(line)

        # Save the very last section
        save_previous_section()

        return merged_sections

    # --- UPDATED ORCHESTRATOR METHOD ---

    def validate_resume_structure(self, resume_text: str) -> Dict:
        """
        Comprehensive resume structure validation.
        (Runs FR-010 detection AND FR-005 merging)
        """

        # --- FR-010 Logic (Original) ---
        # This logic is for keyword detection and completeness score.
        # It uses the original, robust keyword-based methods.
        detected = self.detect_sections(resume_text)
        missing = self.find_missing_sections(resume_text, required_only=True)
        present = [section for section, found in detected.items() if found]
        total_required = len(self.required_sections)
        present_required = total_required - len(missing)
        completeness_score = (present_required / total_required) * 100

        # --- FR-005 Logic (New) ---
        # This logic is for splitting and merging content.
        # It uses the new line-parser-based method.
        merged_sections_content = self._split_and_merge_sections(resume_text)

        # --- Return data from BOTH features ---
        # NEW, FIXED CODE
        return {
            # From FR-010 (original logic)
            "has_all_required": len(missing) == 0,
            "missing_sections": missing,
            "incomplete_sections": [],  # Populated by parsing engine
            "present_sections": present,
            "completeness_score": round(completeness_score, 2),
            # From FR-005 (new logic)
            "merged_sections": merged_sections_content,
        }
