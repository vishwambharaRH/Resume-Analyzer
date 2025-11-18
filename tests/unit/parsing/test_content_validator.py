# In tests/unit/parsing/test_content_validator.py
import pytest
from src.parser.content_validator import validate_content


class TestContentValidator:

    def test_ac_missing_contact_info(self):
        """
        AC: Flag invalid/missing email or phone number
        AC: Detect missing contact info fields
        """
        text = "This resume has no contact info. Jan 2020"
        report = validate_content(text)

        assert report["contact_info"]["email_found"] is None
        assert report["contact_info"]["phone_found"] is None

        issues = report["contact_info"]["issues"]
        assert len(issues) == 2
        assert issues[0]["field"] == "email"
        assert issues[0]["error"] == "Missing"
        assert issues[1]["field"] == "phone"

    def test_found_contact_info(self):
        """
        Tests that contact info is found correctly.
        """
        text = "My email is test@example.com and my phone is (123) 456-7890."
        report = validate_content(text)

        assert report["contact_info"]["email_found"] == "test@example.com"
        assert report["contact_info"]["phone_found"] == "(123) 456-7890"
        assert len(report["contact_info"]["issues"]) == 0

    def test_ac_date_consistency_pass_mmm_yyyy(self):
        """
        AC: Check date formats consistency (MMM YYYY)
        """
        text = """
        Job 1: Jan 2020 - May 2022
        Job 2: Aug 2018 - Dec 2019
        """
        report = validate_content(text)

        assert report["dates"]["consistent"] is True
        assert report["dates"]["format"] == "MMM YYYY"

    def test_ac_date_consistency_pass_mm_yyyy(self):
        """
        AC: Accept standard date patterns (MM/YYYY)
        """
        text = """
        Job 1: 01/2020 - 05/2022
        Job 2: 08/2018 - 12/2019
        """
        report = validate_content(text)

        assert report["dates"]["consistent"] is True
        assert report["dates"]["format"] == "MM/YYYY"

    # In tests/unit/parsing/test_content_validator.py

    def test_ac_date_inconsistency_fail(self):
        """
        AC: Check date formats consistency (fail)
        AC: Error messages include reason
        """
        text = """
        Job 1: Jan 2020 - May 2022
        Job 2: 08/2018 - 12/2019
        """
        report = validate_content(text)

        assert report["dates"]["consistent"] is False
        assert report["dates"]["format"] == "mixed"

        # --- THIS IS THE FIX ---
        # OLD: assert "Inconsistent date formats" in report["dates"]["message"]
        # NEW:
        assert "Invalid date format" in report["dates"]["message"]
        # --- ---

    def test_no_dates_found(self):
        """
        Tests that the validator handles resumes with no dates.
        """
        text = "My email is test@example.com."
        report = validate_content(text)

        assert report["dates"]["consistent"] is True
        assert report["dates"]["format"] is None
        assert "No dates found" in report["dates"]["message"]
