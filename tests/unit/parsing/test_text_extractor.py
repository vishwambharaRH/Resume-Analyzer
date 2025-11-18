"""
Unit tests for Text Extractor (FR-009)
"""

import pytest
from pathlib import Path
from src.parser.text_extractor import TextExtractor


class TestTextExtractor:
    """Test text extraction from various file formats"""

    def test_extract_from_txt_file(self, tmp_path):
        """Test TXT file extraction"""
        # Create temp file
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Sample resume text", encoding="utf-8")

        extractor = TextExtractor()
        result = extractor.extract_text(str(txt_file))

        assert result == "Sample resume text"

    def test_extract_from_nonexistent_file(self):
        """Test extraction from non-existent file"""
        extractor = TextExtractor()
        result = extractor.extract_text("nonexistent.txt")

        assert result is None

    def test_extract_unsupported_format(self, tmp_path):
        """Test extraction from unsupported format"""
        jpg_file = tmp_path / "test.jpg"
        jpg_file.write_bytes(b"\xff\xd8\xff\xe0")

        extractor = TextExtractor()
        result = extractor.extract_text(str(jpg_file))

        assert result is None
