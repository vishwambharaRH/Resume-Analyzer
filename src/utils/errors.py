"""Custom exceptions for the Dynamic Resume Analyzer.

Defines domain-specific exceptions used across the upload, parsing and
reporting modules to provide meaningful error messages (NFR-004).
"""

from typing import Optional


class ResumeUploadError(Exception):
    """Raised when a resume upload or validation fails.

    Attributes:
        message: Human-friendly error message.
        detail: Optional low-level detail for debugging/logs.
    """

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class ResumeParsingError(Exception):
    """Raised when resume parsing fails or produces unreliable output.

    Carries a short message and optional detail for logging.
    """

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class ReportGenerationError(Exception):
    """Raised when generating a report fails (formatting, missing data).

    Use this to surface user-facing messages while preserving debug detail.
    """

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail
