# In parser/content_validator.py
"""
Content Validator - FR-006 Implementation
Validates specific content formats within the resume text,
such as date consistency and contact information.
"""

import re
from typing import Dict, List, Any

# --- Regex Patterns for FR-006 ---

# AC: Accept standard date patterns (MMM YYYY, MM/YYYY)
# This will find "Jan 2020", "May 2022", "01/2020", "05/2022"
DATE_PATTERN = re.compile(
    # Group 1: MMM YYYY (e.g., "Jan 2020")
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b"
    # OR
    r"|"
    # Group 2: MM/YYYY (e.g., "05/2022")
    r"(\b(0[1-9]|1[0-2])\/(\d{4})\b)"
)

# Regex for standard email
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Regex for common US/International phone formats
PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?(\d{3}[-.\s]?\d{4})\b"
)


def _check_date_consistency(dates_found: List[str]) -> Dict[str, Any]:
    """
    Checks if all found dates use a consistent format.
    AC: Check date formats consistency
    """
    if not dates_found:
        return {
            "consistent": True,
            "format": None,
            "message": "No dates found to check.",
        }

    # Check format of the first date
    first_date = dates_found[0]
    # Check if it matches "MMM YYYY"
    is_mmm_yyyy = bool(re.match(r"^[A-Za-z]{3}\s+\d{4}$", first_date))

    expected_format = "MMM YYYY" if is_mmm_yyyy else "MM/YYYY"

    for date_str in dates_found[1:]:
        is_current_mmm_yyyy = bool(re.match(r"^[A-Za-z]{3}\s+\d{4}$", date_str))

        if (is_current_mmm_yyyy and not is_mmm_yyyy) or (
            not is_current_mmm_yyyy and is_mmm_yyyy
        ):
            # AC: Error messages include reason
            return {
                "consistent": False,
                "format": "mixed",
                "message": "Invalid date format. Inconsistent formats found. Please use either 'MMM YYYY' or 'MM/YYYY' consistently.",
            }

    return {
        "consistent": True,
        "format": expected_format,
        "message": "Date formats are consistent.",
    }


def validate_content(raw_text: str) -> Dict[str, Any]:
    """
    Runs all content validations for FR-006.
    - Checks date format consistency
    - Checks for email and phone
    """

    # --- 1. Date Validation ---
    all_date_matches = DATE_PATTERN.finditer(raw_text)

    # Extract the full match, cleaning it up
    dates_found = [match.group(0).strip() for match in all_date_matches]

    date_report = _check_date_consistency(dates_found)

    # --- 2. Contact Info Validation ---
    # AC: Flag invalid/missing email or phone number
    email_match = EMAIL_PATTERN.search(raw_text)
    phone_match = PHONE_PATTERN.search(raw_text)

    contact_issues = []
    # AC: Detect missing contact info fields
    if not email_match:
        contact_issues.append(
            {
                "field": "email",
                "error": "Missing",
                "message": "No valid email address found. A professional resume should include an email.",
            }
        )

    if not phone_match:
        contact_issues.append(
            {
                "field": "phone",
                "error": "Missing",
                "message": "No valid phone number found. A professional resume should include a phone number.",
            }
        )

    # --- 3. Final Report ---
    return {
        "dates": date_report,
        "contact_info": {
            "email_found": email_match.group(0) if email_match else None,
            "phone_found": phone_match.group(0) if phone_match else None,
            "issues": contact_issues,
        },
    }
