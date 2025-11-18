"""
Unit tests for Gap Detector (FR-009)
Test Cases: DRA-66
"""

import pytest
from datetime import datetime
from src.parser.gap_detector import GapDetector


class TestWordCountAnalysis:
    """Test word count detection - TC-WORD-001 to TC-WORD-005"""

    def setup_method(self):
        self.detector = GapDetector()

    def test_short_resume_flagged(self):
        """TC-WORD-001: Resume with <300 words flagged as too short"""
        short_text = "John Doe. Software Engineer. " * 20  # ~60 words
        result = self.detector.analyze_word_count(short_text)

        assert result["word_count"] < 300
        assert result["word_count_status"] == "too_short"
        assert "at least 300 words" in result["word_count_feedback"]

    def test_long_resume_flagged(self):
        """TC-WORD-002: Resume with >1500 words flagged as too long"""
        # Create text with exactly 1600 words
        single_phrase = (
            "Experienced software engineer with expertise and knowledge. "  # 7 words
        )
        long_text = single_phrase * 230  # 7 × 230 = 1610 words
        result = self.detector.analyze_word_count(long_text)

        assert result["word_count"] > 1500
        assert result["word_count_status"] == "too_long"
        assert (
            "condensing" in result["word_count_feedback"].lower()
            or "lengthy" in result["word_count_feedback"].lower()
        )

    def test_optimal_word_count(self):
        """TC-WORD-003: Resume with 300-1500 words is optimal"""
        optimal_text = "Software engineer with 5 years experience. " * 100  # ~700 words
        result = self.detector.analyze_word_count(optimal_text)

        assert 300 <= result["word_count"] <= 1500
        assert result["word_count_status"] == "optimal"
        assert "appropriate" in result["word_count_feedback"].lower()

    def test_word_count_ignores_extra_whitespace(self):
        """TC-WORD-004: Word count handles extra whitespace"""
        text_with_spaces = "Word1    Word2\n\nWord3\tWord4"
        result = self.detector.analyze_word_count(text_with_spaces)

        assert result["word_count"] == 4

    def test_empty_resume(self):
        """TC-WORD-005: Empty resume has 0 words"""
        result = self.detector.analyze_word_count("")

        assert result["word_count"] == 0
        assert result["word_count_status"] == "too_short"


class TestDateParsing:
    """Test date parsing - TC-DATE-001 to TC-DATE-010"""

    def setup_method(self):
        self.detector = GapDetector()

    def test_parse_mm_yyyy_format(self):
        """TC-DATE-001: Parse MM/YYYY format"""
        date = self.detector._parse_date("01/2020")
        assert date == datetime(2020, 1, 1)

    def test_parse_mm_dash_yyyy_format(self):
        """TC-DATE-002: Parse MM-YYYY format"""
        date = self.detector._parse_date("12-2021")
        assert date == datetime(2021, 12, 1)

    def test_parse_month_name_format(self):
        """TC-DATE-003: Parse 'January 2020' format"""
        date = self.detector._parse_date("January 2020")
        assert date == datetime(2020, 1, 1)

    def test_parse_abbreviated_month_format(self):
        """TC-DATE-004: Parse 'Jan 2020' format"""
        date = self.detector._parse_date("Jan 2020")
        assert date == datetime(2020, 1, 1)

    def test_parse_year_only_format(self):
        """TC-DATE-005: Parse YYYY format (defaults to January)"""
        date = self.detector._parse_date("2020")
        assert date == datetime(2020, 1, 1)

    def test_parse_present(self):
        """TC-DATE-006: Parse 'Present' as current date"""
        date = self.detector._parse_date("Present")
        assert date.year == datetime.now().year

    def test_parse_current(self):
        """TC-DATE-007: Parse 'Current' as current date"""
        date = self.detector._parse_date("Current")
        assert date.year == datetime.now().year

    def test_parse_invalid_date(self):
        """TC-DATE-008: Invalid date returns None"""
        date = self.detector._parse_date("invalid date")
        assert date is None

    def test_parse_empty_string(self):
        """TC-DATE-009: Empty string returns None"""
        date = self.detector._parse_date("")
        assert date is None

    def test_parse_case_insensitive(self):
        """TC-DATE-010: Date parsing is case-insensitive"""
        date1 = self.detector._parse_date("JANUARY 2020")
        date2 = self.detector._parse_date("january 2020")
        assert date1 == date2


class TestEmploymentGapDetection:
    """Test employment gap detection - TC-GAP-001 to TC-GAP-010"""

    def setup_method(self):
        self.detector = GapDetector()

    def test_detect_gap_greater_than_6_months(self):
        """TC-GAP-001: Detect gap > 6 months"""
        experience = [
            {
                "title": "Software Engineer",
                "company": "Company A",
                "start_date": "01/2020",
                "end_date": "06/2020",
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "start_date": "03/2021",  # 9-month gap
                "end_date": "12/2022",
            },
        ]

        result = self.detector.detect_employment_gaps(experience)

        assert result["gap_count"] == 1
        assert len(result["employment_gaps"]) == 1
        assert result["employment_gaps"][0]["gap_months"] == 9

    def test_no_gap_detected_under_6_months(self):
        """TC-GAP-002: Gap ≤ 6 months not flagged"""
        experience = [
            {
                "title": "Developer",
                "company": "Company A",
                "start_date": "01/2020",
                "end_date": "06/2020",
            },
            {
                "title": "Senior Developer",
                "company": "Company B",
                "start_date": "09/2020",  # 3-month gap
                "end_date": "12/2021",
            },
        ]

        result = self.detector.detect_employment_gaps(experience)

        assert result["gap_count"] == 0
        assert len(result["employment_gaps"]) == 0

    def test_multiple_gaps_detected(self):
        """TC-GAP-003: Detect multiple employment gaps"""
        experience = [
            {
                "title": "Junior Dev",
                "company": "Company A",
                "start_date": "01/2018",
                "end_date": "06/2018",
            },
            {
                "title": "Mid Dev",
                "company": "Company B",
                "start_date": "03/2019",  # 9-month gap
                "end_date": "12/2019",
            },
            {
                "title": "Senior Dev",
                "company": "Company C",
                "start_date": "09/2020",  # 9-month gap
                "end_date": "Present",
            },
        ]

        result = self.detector.detect_employment_gaps(experience)

        assert result["gap_count"] == 2
        assert len(result["employment_gaps"]) == 2

    def test_no_employment_history(self):
        """TC-GAP-004: Handle empty employment history"""
        result = self.detector.detect_employment_gaps([])

        assert result["gap_count"] == 0
        assert "No employment history" in result["gap_feedback"][0]

    def test_single_job_no_gap(self):
        """TC-GAP-005: Single job has no gaps"""
        experience = [
            {
                "title": "Engineer",
                "company": "Company A",
                "start_date": "01/2020",
                "end_date": "Present",
            }
        ]

        result = self.detector.detect_employment_gaps(experience)

        assert result["gap_count"] == 0

    def test_overlapping_jobs_no_gap(self):
        """TC-GAP-006: Overlapping jobs (no gap)"""
        experience = [
            {
                "title": "Job 1",
                "company": "Company A",
                "start_date": "01/2020",
                "end_date": "12/2020",
            },
            {
                "title": "Job 2",
                "company": "Company B",
                "start_date": "06/2020",  # Started before first job ended
                "end_date": "12/2021",
            },
        ]

        result = self.detector.detect_employment_gaps(experience)

        # Overlapping jobs should not create a gap
        assert result["gap_count"] == 0

    def test_gap_feedback_message_format(self):
        """TC-GAP-007: Gap feedback includes job details"""
        experience = [
            {
                "title": "Developer",
                "company": "ABC Corp",
                "start_date": "01/2020",
                "end_date": "06/2020",
            },
            {
                "title": "Senior Developer",
                "company": "XYZ Inc",
                "start_date": "04/2021",  # 10-month gap
                "end_date": "12/2022",
            },
        ]

        result = self.detector.detect_employment_gaps(experience)

        feedback = result["gap_feedback"][0]
        assert "ABC Corp" in feedback
        assert "XYZ Inc" in feedback
        assert "months" in feedback

    def test_missing_dates_handled_gracefully(self):
        """TC-GAP-008: Handle missing start/end dates"""
        experience = [
            {
                "title": "Engineer",
                "company": "Company A",
                # Missing dates
            },
            {
                "title": "Senior Engineer",
                "company": "Company B",
                "start_date": "01/2020",
                "end_date": "12/2021",
            },
        ]

        # Should not crash
        result = self.detector.detect_employment_gaps(experience)
        assert isinstance(result, dict)

    def test_gap_info_structure(self):
        """TC-GAP-009: Gap info has correct structure"""
        experience = [
            {
                "title": "Dev",
                "company": "A",
                "start_date": "01/2020",
                "end_date": "06/2020",
            },
            {
                "title": "Senior Dev",
                "company": "B",
                "start_date": "04/2021",
                "end_date": "12/2022",
            },
        ]

        result = self.detector.detect_employment_gaps(experience)
        gap = result["employment_gaps"][0]

        assert "gap_start" in gap
        assert "gap_end" in gap
        assert "gap_months" in gap
        assert "previous_job" in gap
        assert "next_job" in gap

    def test_calculate_month_difference(self):
        """TC-GAP-010: Month calculation is accurate"""
        start = datetime(2020, 1, 1)
        end = datetime(2020, 7, 1)

        months = self.detector._calculate_month_difference(start, end)
        assert months == 6

        # Test year boundary
        start2 = datetime(2020, 10, 1)
        end2 = datetime(2021, 4, 1)
        months2 = self.detector._calculate_month_difference(start2, end2)
        assert months2 == 6


class TestCompleteAnalysis:
    """Test complete resume analysis"""

    def setup_method(self):
        self.detector = GapDetector()

    def test_analyze_resume_complete(self):
        """Test complete analysis with both word count and gaps"""
        resume_text = "Experienced software engineer. " * 100  # ~300 words
        experience = [
            {
                "title": "Engineer",
                "company": "A",
                "start_date": "01/2020",
                "end_date": "06/2020",
            },
            {
                "title": "Senior Engineer",
                "company": "B",
                "start_date": "04/2021",
                "end_date": "Present",
            },
        ]

        result = self.detector.analyze_resume(resume_text, experience)

        # Check word count results
        assert "word_count" in result
        assert "word_count_status" in result
        assert "word_count_feedback" in result

        # Check gap results
        assert "employment_gaps" in result
        assert "gap_count" in result
        assert "gap_feedback" in result
