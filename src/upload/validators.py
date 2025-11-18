"""
File validation utilities for resume upload
Implements DRA-41: File format validation
"""

import os
from typing import Tuple
from fastapi import UploadFile, HTTPException, status, File
from typing import List

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


def validate_file_type(filename: str) -> Tuple[bool, str]:
    """
    Validate file extension.

    Args:
        filename (str): Name of the file to validate

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    _, ext = os.path.splitext(filename)
    ext_lower = ext.lower()
    if ext_lower not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        return False, f"Unsupported file type: {ext_lower}. Allowed: {allowed}"

    return True, ""


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """
    Validate file size (must be >0 and <=10MB).

    Args:
        file_size (int): Size of file in bytes

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if file_size == 0:
        return False, "File is empty"

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        error_msg = f"File too large: {size_mb:.2f} MB. Maximum: 10 MB"
        return (False, error_msg)

    return True, ""


def validate_file_content(file_content: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validate actual file content using signature/magic bytes.

    Args:
        file_content (bytes): First bytes of the file
        filename (str): File name for extension-based checks

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    _, ext = os.path.splitext(filename)
    ext_lower = ext.lower()

    if ext_lower == ".pdf":
        if not file_content.startswith(b"%PDF"):
            return False, "File does not appear to be a valid PDF"

    elif ext_lower == ".docx":
        if not file_content.startswith(b"PK"):
            return False, "File does not appear to be a valid DOCX"

    elif ext_lower == ".txt":
        try:
            file_content[:1024].decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return False, "File does not appear to be valid text"

    return True, ""


async def validate_files(
    files: List[UploadFile] = File(..., description="List of files to validate")
) -> List[UploadFile]:
    """
    FastAPI Dependency to validate a list of uploaded files.
    This is the main function imported by routes.py.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files were uploaded.",
        )

    validated_files = []
    for file in files:
        # 1. Validate Type
        is_valid_type, msg = validate_file_type(file.filename)
        if not is_valid_type:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=msg
            )

        # 2. Validate Size
        content = await file.read()
        file_size = len(content)
        is_valid_size, msg = validate_file_size(file_size)
        if not is_valid_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=msg
            )

        # 3. Validate Content (Magic Bytes)
        is_valid_content, msg = validate_file_content(content, file.filename)
        if not is_valid_content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg
            )

        # Reset the file pointer after reading
        await file.seek(0)
        validated_files.append(file)

    return validated_files
