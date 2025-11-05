import pytest
import pytest_asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from fastapi import UploadFile
from src.upload.service import save_file, delete_file, UPLOAD_DIR
import uuid

# Fixtures should be outside the class
@pytest_asyncio.fixture
async def mock_upload_file():
    """Create mock UploadFile object"""
    file = Mock(spec=UploadFile)
    file.filename = "test_resume.pdf"
    file.read = AsyncMock(return_value=b"fake pdf content")  # Use AsyncMock here
    return file

@pytest.mark.asyncio
class TestSaveFile:
    """Unit tests for save_file function"""

    async def test_save_file_creates_unique_job_id(self, mock_upload_file):
        """
        Test that save_file generates unique UUID4 job ID

        Expected: job_id is valid UUID4 format
        """
        result = await save_file(mock_upload_file)

        assert "job_id" in result
        assert len(result["job_id"]) == 36  # UUID4 length with hyphens

        # Verify UUID4 format
        try:
            uuid.UUID(result["job_id"], version=4)
            assert True
        except ValueError:
            assert False, "job_id should be valid UUID4"

    async def test_save_file_preserves_extension(self, mock_upload_file):
        """
        Test that file extension is preserved in stored filename

        Expected: stored_filename ends with .pdf
        """
        result = await save_file(mock_upload_file)

        assert result["stored_filename"].endswith(".pdf")
        assert ".pdf" in result["file_path"]

    async def test_save_file_returns_metadata(self, mock_upload_file):
        """
        Test that save_file returns complete metadata

        Expected: All required fields present
        """
        result = await save_file(mock_upload_file)

        assert "job_id" in result
        assert "original_filename" in result
        assert "stored_filename" in result
        assert "file_path" in result
        assert "file_size" in result
        assert "upload_time" in result
        assert "status" in result

    async def test_save_file_records_original_filename(self, mock_upload_file):
        """
        Test that original filename is recorded

        Expected: original_filename matches input
        """
        result = await save_file(mock_upload_file)

        assert result["original_filename"] == "test_resume.pdf"

    async def test_save_file_records_file_size(self, mock_upload_file):
        """
        Test that file size is recorded correctly

        Expected: file_size matches content length
        """
        result = await save_file(mock_upload_file)

        assert result["file_size"] == len(b"fake pdf content")
        assert result["file_size"] > 0

    async def test_save_file_includes_timestamp(self, mock_upload_file):
        """
        Test that upload timestamp is included

        Expected: upload_time is ISO format string
        """
        result = await save_file(mock_upload_file)

        assert "upload_time" in result
        assert "T" in result["upload_time"]  # ISO format includes 'T'
        assert ":" in result["upload_time"]  # Includes time

    async def test_save_file_status_is_uploaded(self, mock_upload_file):
        """
        Test that status is set to 'uploaded'

        Expected: status field is 'uploaded'
        """
        result = await save_file(mock_upload_file)

        assert result["status"] == "uploaded"

    async def test_save_file_with_docx(self):
        """
        Test saving DOCX file preserves extension

        Expected: .docx extension maintained
        """
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "resume.docx"
        mock_file.read = AsyncMock(return_value=b"fake docx content")

        result = await save_file(mock_file)

        assert result["stored_filename"].endswith(".docx")
        assert result["original_filename"] == "resume.docx"

    async def test_save_file_with_txt(self):
        """
        Test saving TXT file preserves extension

        Expected: .txt extension maintained
        """
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "resume.txt"
        mock_file.read = AsyncMock(return_value=b"plain text content")  # Use AsyncMock here

        result = await save_file(mock_file)

        assert result["stored_filename"].endswith(".txt")

    async def test_save_file_creates_upload_directory(self, mock_upload_file, tmp_path):
        """
        Test that upload directory is created if not exists

        Expected: UPLOAD_DIR exists after save_file
        """
        original_dir = save_file.__globals__["UPLOAD_DIR"]
        save_file.__globals__["UPLOAD_DIR"] = tmp_path

        await save_file(mock_upload_file)

        assert tmp_path.exists()
        assert tmp_path.is_dir()

        # Restore original directory
        save_file.__globals__["UPLOAD_DIR"] = original_dir

    async def test_save_file_actually_writes_content(self, mock_upload_file):
        """
        Test that file content is actually written to disk

        Expected: File exists at file_path with correct content
        """
        result = await save_file(mock_upload_file)
        file_path = Path(result["file_path"])

        try:
            assert file_path.exists()
            assert file_path.is_file()

            # Verify content
            content = file_path.read_bytes()
            assert content == b"fake pdf content"
        finally:
            # Cleanup
            if file_path.exists():
                file_path.unlink()
