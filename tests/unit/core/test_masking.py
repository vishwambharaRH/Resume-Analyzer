"""
Unit tests for the new anonymization masking rules.
(Implements DRA-99)
"""

from src.core.masking import mask_email, mask_phone


def test_mask_email_simple():
    assert mask_email("user@example.com") == "u*****r@example.com"


def test_mask_email_complex():
    assert mask_email("test.user.long@company.co.in") == "t*****g@company.co.in"


def test_mask_phone_international():
    assert mask_phone("+91 98765 43210") == "+91 XXXXX 43210"


def test_mask_phone_10_digit():
    assert mask_phone("9876543210") == "XXXXX43210"


def test_mask_phone_empty():
    assert mask_phone("") == ""


def test_mask_email_empty():
    assert mask_email("") == ""
