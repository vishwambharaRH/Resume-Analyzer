"""
Employment Gap & Word Count Detector
Implements FR-009: Detect employment gaps (>6 months) & word count
"""

from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dateutil.relativedelta import relativedelta
import re


class GapDetector:
    """
    Detects employment gaps and analyzes resume length
    Test Cases: TC-GAP-001 to TC-GAP-010
    """

    # Thresholds
    MIN_WORD_COUNT = 300
    MAX_WORD_COUNT = 1500
    GAP_THRESHOLD_MONTHS = 6

    # Date format patterns
    DATE_PATTERNS = [
        r"(\d{1,2})/(\d{4})",  # MM/YYYY or M/YYYY
        r"(\d{1,2})-(\d{4})",  # MM-YYYY
        r"([A-Za-z]+)\s+(\d{4})",  # Month YYYY (e.g., "January 2020")
        r"([A-Za-z]{3})\s+(\d{4})",  # Mon YYYY (e.g., "Jan 2020")
        r"(\d{4})",  # YYYY only
    ]

    MONTH_MAP = {
        "january": 1,
        "jan": 1,
        "february": 2,
        "feb": 2,
        "march": 3,
        "mar": 3,
        "april": 4,
        "apr": 4,
        "may": 5,
        "june": 6,
        "jun": 6,
        "july": 7,
        "jul": 7,
        "august": 8,
        "aug": 8,
        "september": 9,
        "sep": 9,
        "october": 10,
        "oct": 10,
        "november": 11,
        "nov": 11,
        "december": 12,
        "dec": 12,
    }

    def analyze_resume(self, resume_text: str, experience_data: List[Dict]) -> Dict:
        """
        Complete analysis: word count + employment gaps

        Args:
            resume_text: Full resume text
            experience_data: List of work experience entries
                [
                    {
                        "title": "Software Engineer",
                        "company": "ABC Corp",
                        "start_date": "01/2020",
                        "end_date": "12/2022"
                    }
                ]

        Returns:
            {
                "word_count": int,
                "word_count_feedback": str,
                "employment_gaps": List[Dict],
                "gap_feedback": List[str]
            }
        """
        # Analyze word count
        word_analysis = self.analyze_word_count(resume_text)

        # Detect employment gaps
        gap_analysis = self.detect_employment_gaps(experience_data)

        return {**word_analysis, **gap_analysis}

    def analyze_word_count(self, resume_text: str) -> Dict:
        """
        Analyze resume word count

        Args:
            resume_text: Full resume text

        Returns:
            {
                "word_count": int,
                "word_count_status": "too_short" | "optimal" | "too_long",
                "word_count_feedback": str
            }

        Test Case: TC-WORD-001 to TC-WORD-005
        """
        # Clean text: remove extra whitespace, special characters
        cleaned_text = re.sub(r"\s+", " ", resume_text)
        words = [word for word in cleaned_text.split() if word.strip()]
        word_count = len(words)

        # Determine status
        if word_count < self.MIN_WORD_COUNT:
            status = "too_short"
            feedback = (
                f"Your resume is only {word_count} words. "
                f"Aim for at least {self.MIN_WORD_COUNT} words to provide "
                "sufficient detail about your experience and skills."
            )
        elif word_count > self.MAX_WORD_COUNT:
            status = "too_long"
            feedback = (
                f"Your resume is {word_count} words, which is quite lengthy. "
                f"Consider condensing to under {self.MAX_WORD_COUNT} words "
                "to maintain recruiter attention."
            )
        else:
            status = "optimal"
            feedback = (
                f"Your resume length ({word_count} words) is appropriate. "
                "Good balance of detail and brevity."
            )

        return {
            "word_count": word_count,
            "word_count_status": status,
            "word_count_feedback": feedback,
        }

    def detect_employment_gaps(self, experience_data: List[Dict]) -> Dict:
        """
        Detect gaps in employment history

        Args:
            experience_data: List of work experience with dates

        Returns:
            {
                "employment_gaps": [
                    {
                        "gap_start": "2020-12-01",
                        "gap_end": "2021-06-01",
                        "gap_months": 6,
                        "previous_job": "Software Engineer at XYZ",
                        "next_job": "Senior Engineer at ABC"
                    }
                ],
                "gap_count": int,
                "gap_feedback": List[str]
            }

        Test Case: TC-GAP-001 to TC-GAP-010
        """
        if not experience_data:
            return {
                "employment_gaps": [],
                "gap_count": 0,
                "gap_feedback": ["No employment history provided"],
            }

        # Parse and sort experiences by date
        parsed_experiences = []
        for exp in experience_data:
            start_date = self._parse_date(exp.get("start_date", ""))
            end_date = self._parse_date(exp.get("end_date", ""))

            if start_date and end_date:
                parsed_experiences.append(
                    {
                        "title": exp.get("title", "Unknown Position"),
                        "company": exp.get("company", "Unknown Company"),
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )

        # Sort by end date (most recent last)
        parsed_experiences.sort(key=lambda x: x["end_date"])

        # Detect gaps
        gaps = []
        feedback_messages = []

        for i in range(len(parsed_experiences) - 1):
            current_job = parsed_experiences[i]
            next_job = parsed_experiences[i + 1]

            gap_start = current_job["end_date"]
            gap_end = next_job["start_date"]

            # Calculate gap in months
            gap_months = self._calculate_month_difference(gap_start, gap_end)

            if gap_months > self.GAP_THRESHOLD_MONTHS:
                gap_info = {
                    "gap_start": gap_start.strftime("%b %Y"),
                    "gap_end": gap_end.strftime("%b %Y"),
                    "gap_months": gap_months,
                    "previous_job": current_job["company"],
                    "next_job": next_job["company"],
                }
                gaps.append(gap_info)

                feedback_messages.append(
                    f"Gap detected: {gap_months} months between "
                    f"{current_job['company']} and {next_job['company']} "
                    f"({gap_start.strftime('%b %Y')} - {gap_end.strftime('%b %Y')}). "
                    "Consider adding explanation or including relevant activities."
                )

        # Overall feedback
        if not gaps:
            feedback_messages.append(
                "No significant employment gaps detected. "
                "Your work history shows consistent employment."
            )

        return {
            "employment_gaps": gaps,
            "gap_count": len(gaps),
            "gap_feedback": feedback_messages,
        }

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string in various formats

        Supported formats:
        - MM/YYYY or M/YYYY
        - MM-YYYY
        - Month YYYY (e.g., "January 2020")
        - Mon YYYY (e.g., "Jan 2020")
        - YYYY (defaults to January 1st)
        - "Present" or "Current" (returns today's date)

        Test Case: TC-DATE-001 to TC-DATE-010
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Handle "Present" or "Current"
        if any(
            keyword in date_str.lower() for keyword in ["present", "current", "now"]
        ):
            return datetime.now()

        # Try each pattern
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                groups = match.groups()

                # Pattern: Month name + Year
                if len(groups) == 2 and groups[0].isalpha():
                    month_str = groups[0].lower()
                    year = int(groups[1])
                    month = self.MONTH_MAP.get(month_str, 1)
                    return datetime(year, month, 1)

                # Pattern: MM/YYYY or MM-YYYY
                elif len(groups) == 2 and groups[0].isdigit():
                    month = int(groups[0])
                    year = int(groups[1])
                    return datetime(year, month, 1)

                # Pattern: YYYY only
                elif len(groups) == 1:
                    year = int(groups[0])
                    return datetime(year, 1, 1)

        return None

    def _calculate_month_difference(
        self, start_date: datetime, end_date: datetime
    ) -> int:
        """
        Calculate difference in months between two dates

        Test Case: TC-MONTH-001 to TC-MONTH-005
        """
        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months
