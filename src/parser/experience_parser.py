"""
Experience section parser
Extracts work history from resume text
"""

import re
from typing import List, Dict, Optional
from datetime import datetime


class ExperienceParser:
    """Parse work experience from resume text"""

    # Common section headers for experience
    EXPERIENCE_HEADERS = [
        r"work\s+experience",
        r"professional\s+experience",
        r"employment\s+history",
        r"work\s+history",
        r"experience",
        r"career\s+history",
    ]

    # Date patterns
    DATE_PATTERNS = [
        r"(\d{1,2})/(\d{4})",  # MM/YYYY
        r"(\d{1,2})-(\d{4})",  # MM-YYYY
        r"([A-Za-z]+)\s+(\d{4})",  # Month YYYY
        r"([A-Za-z]{3})\s+(\d{4})",  # Mon YYYY
        r"(\d{4})",  # YYYY
        r"(present|current|now)",  # Present
    ]

    def parse_experience_section(self, resume_text: str) -> List[Dict]:
        """
        Extract work experience entries from resume text

        Args:
            resume_text: Full resume text

        Returns:
            List of experience dictionaries:
            [
                {
                    "title": "Software Engineer",
                    "company": "ABC Corp",
                    "start_date": "01/2020",
                    "end_date": "12/2022",
                    "description": "..."
                }
            ]
        """
        # Find experience section
        experience_text = self._extract_experience_section(resume_text)

        if not experience_text:
            return []

        # Split into individual job entries
        jobs = self._split_into_jobs(experience_text)

        # Parse each job
        parsed_jobs = []
        for job_text in jobs:
            parsed_job = self._parse_single_job(job_text)
            if parsed_job:
                parsed_jobs.append(parsed_job)

        return parsed_jobs

    def _extract_experience_section(self, text: str) -> str:
        """Find and extract the experience section"""
        lines = text.split("\n")

        # Find experience section start
        start_idx = None
        for i, line in enumerate(lines):
            for pattern in self.EXPERIENCE_HEADERS:
                if re.search(pattern, line, re.IGNORECASE):
                    start_idx = i
                    break
            if start_idx is not None:
                break

        if start_idx is None:
            return ""

        # Find next major section (education, skills, etc.)
        next_section_keywords = [
            "education",
            "skills",
            "projects",
            "certifications",
            "publications",
            "awards",
            "references",
        ]

        end_idx = len(lines)
        for i in range(start_idx + 1, len(lines)):
            for keyword in next_section_keywords:
                if re.match(rf"^{keyword}", lines[i], re.IGNORECASE):
                    end_idx = i
                    break
            if end_idx != len(lines):
                break

        return "\n".join(lines[start_idx:end_idx])

    def _split_into_jobs(self, experience_text: str) -> List[str]:
        """Split experience section into individual job entries"""
        # Split by common job entry patterns
        # Jobs usually start with a title or company in ALL CAPS or bold

        lines = experience_text.split("\n")
        jobs = []
        current_job = []

        for line in lines:
            # Check if line looks like a new job entry
            # (Company name in caps, or date range pattern)
            if self._is_job_header(line) and current_job:
                jobs.append("\n".join(current_job))
                current_job = [line]
            else:
                current_job.append(line)

        if current_job:
            jobs.append("\n".join(current_job))

        return jobs

    def _is_job_header(self, line: str) -> bool:
        """Check if line is likely a job entry header"""
        # Check for date patterns (common in headers)
        has_dates = any(
            re.search(pattern, line, re.IGNORECASE) for pattern in self.DATE_PATTERNS
        )

        # Check for capitalized words (company names)
        has_caps = bool(re.search(r"[A-Z]{2,}", line))

        return has_dates or has_caps

    def _parse_single_job(self, job_text: str) -> Optional[Dict]:
        """Parse a single job entry"""
        lines = [line.strip() for line in job_text.split("\n") if line.strip()]

        if not lines:
            return None

        # Extract title and company (usually in first 2 lines)
        title = lines[0] if len(lines) > 0 else "Unknown Position"
        company = lines[1] if len(lines) > 1 else "Unknown Company"

        # Extract dates
        dates = self._extract_dates(job_text)
        start_date = dates.get("start_date", "")
        end_date = dates.get("end_date", "")

        # Extract description (remaining lines)
        description = "\n".join(lines[2:]) if len(lines) > 2 else ""

        return {
            "title": title,
            "company": company,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
        }

    def _extract_dates(self, text: str) -> Dict[str, str]:
        """Extract start and end dates from text"""
        dates = {"start_date": "", "end_date": ""}

        # Find all date mentions
        found_dates = []
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                found_dates.append(match.group(0))

        # Assume first date is start, second is end
        if len(found_dates) >= 1:
            dates["start_date"] = found_dates[0]
        if len(found_dates) >= 2:
            dates["end_date"] = found_dates[1]
        elif len(found_dates) == 1:
            # If only one date, it might be "YYYY - Present"
            if re.search(r"present|current|now", text, re.IGNORECASE):
                dates["end_date"] = "Present"

        return dates
