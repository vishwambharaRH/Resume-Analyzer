"""
Masking Service
Provides standalone functions for masking sensitive PII.
(Implements DRA-98)
"""

import re


def mask_email(email: str) -> str:
    """
    Masks the middle of an email.
    e.g., "v.sinha@gmail.com" -> "v*****a@gmail.com"
    """
    if not email:
        return ""
    # Use regex to find the first char, last char before @, and the domain
    return re.sub(
        r"(\b[A-Za-z0-9])[A-Za-z0-9._%+-]*([A-Za-z0-9])(@)", r"\1*****\2\3", email
    )


def mask_phone(phone: str) -> str:
    """
    Masks the middle digits of a phone number.
    e.g., "+91 98765 43210" -> "+91 XXXXX 43210"
    e.g., "9876543210" -> "XXXXX43210"
    """
    if not phone:
        return ""

    # --- 🔴 NEW RULE START 🔴 ---
    # Rule for 10-digit US-style numbers (e.g., 555-555-5555)
    # This will match our placeholder and mask it.
    if re.fullmatch(r"\d{3}-\d{3}-\d{4}", phone):
        # Masks to "XXX-XXX-5555"
        return re.sub(r"(\d{3})-(\d{3})-(\d{4})", r"XXX-XXX-\3", phone)
    # --- 🔴 NEW RULE END 🔴 ---

    # Rule for 10-digit numbers (e.g., 9876543210)
    if re.fullmatch(r"\d{10}", phone):
        return re.sub(r"(\d{5})(\d{5})", r"XXXXX\2", phone)

    # Rule for international numbers
    return re.sub(r"(\+?\d{1,3}[-.\s]?)(\d{5})([-.\s]?)(\d{5})", r"\1XXXXX\3\4", phone)
