"""
Unit tests for upload validators
Implements DRA-42: Unit tests for file validation
"""

from src.upload.validators import (
    validate_file_type,
    validate_file_size,
    validate_file_content,
)
import pytest  # noqa: F401 (imported for pytest test framework)


class TestFileTypeValidation:
    """Test file type validation"""

    def test_valid_pdf_accepted(self):
        """Test that .pdf files are accepted"""
        is_valid, error = validate_file_type("resume.pdf")
        assert is_valid is True
        assert error == ""

    def test_valid_docx_accepted(self):
        """Test that .docx files are accepted"""
        is_valid, error = validate_file_type("resume.docx")
        assert is_valid is True
        assert error == ""

    def test_valid_txt_accepted(self):
        """Test that .txt files are accepted"""
        is_valid, error = validate_file_type("resume.txt")
        assert is_valid is True
        assert error == ""

    def test_uppercase_extension_accepted(self):
        """Test that uppercase extensions work"""
        is_valid, _ = validate_file_type("resume.PDF")
        assert is_valid is True

    def test_invalid_jpg_rejected(self):
        """Test that .jpg files are rejected"""
        is_valid, error = validate_file_type("photo.jpg")
        assert is_valid is False
        assert "unsupported" in error.lower()

    def test_invalid_exe_rejected(self):
        """Test that .exe files are rejected"""
        is_valid, _ = validate_file_type("virus.exe")
        assert is_valid is False

    def test_no_extension_rejected(self):
        """Test that files without extension are rejected"""
        is_valid, _ = validate_file_type("resume")
        assert is_valid is False


class TestFileSizeValidation:
    """Test file size validation"""

    def test_valid_size_accepted(self):
        """Test that files under 10MB are accepted"""
        size = 5 * 1024 * 1024
        is_valid, error = validate_file_size(size)
        assert is_valid is True
        assert error == ""

    def test_max_size_accepted(self):
        """Test that exactly 10MB is accepted"""
        size = 10 * 1024 * 1024
        is_valid, _ = validate_file_size(size)
        assert is_valid is True

    def test_oversized_file_rejected(self):
        """Test that files over 10MB are rejected"""
        size = 11 * 1024 * 1024
        is_valid, error = validate_file_size(size)
        assert is_valid is False
        assert "too large" in error.lower()

    def test_empty_file_rejected(self):
        """Test that empty files are rejected"""
        is_valid, error = validate_file_size(0)
        assert is_valid is False
        assert "empty" in error.lower()


class TestFileContentValidation:
    """Test file content validation using magic bytes"""

    def test_valid_pdf_magic_bytes(self):
        """Test that valid PDF magic bytes are accepted"""
        pdf_content = b"%PDF-1.4\nSome content here"
        is_valid, error = validate_file_content(pdf_content, "resume.pdf")
        assert is_valid is True
        assert error == ""

    def test_invalid_pdf_magic_bytes(self):
        """Test that invalid PDF magic bytes are rejected"""
        fake_pdf = b"This is not a PDF"
        is_valid, error = validate_file_content(fake_pdf, "resume.pdf")
        assert is_valid is False
        assert "valid pdf" in error.lower()

    def test_valid_docx_magic_bytes(self):
        """Test that valid DOCX magic bytes are accepted"""
        docx_content = b"PK\x03\x04" + b"\x00" * 100
        is_valid, _ = validate_file_content(docx_content, "resume.docx")
        assert is_valid is True

    def test_invalid_docx_magic_bytes(self):
        """Test that invalid DOCX magic bytes are rejected"""
        fake_docx = b"Not a DOCX file"
        is_valid, error = validate_file_content(fake_docx, "resume.docx")
        assert is_valid is False
        assert "valid docx" in error.lower()

    def test_valid_txt_content(self):
        """Test that valid text content is accepted"""
        txt_content = b"John Doe\nSoftware Engineer\nSkills: Python"
        is_valid, _ = validate_file_content(txt_content, "resume.txt")
        assert is_valid is True

    def test_invalid_txt_content(self):
        """Test that non-UTF8 text is rejected"""
        invalid_txt = b"\xff\xfe\x00\x00"
        is_valid, error = validate_file_content(invalid_txt, "resume.txt")
        assert is_valid is False
        assert "valid text" in error.lower()
