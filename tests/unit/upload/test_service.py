"""
Unit Tests for Upload Service
Tests file storage and management operations

Requirements: FR-001, DRA-41
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from fastapi import UploadFile
from src.upload.service import save_file, delete_file, UPLOAD_DIR


class TestSaveFile:
    """Unit tests for save_file function"""

    @pytest.fixture
    async def mock_upload_file(self):
        """Create mock UploadFile object"""
        file = Mock(spec=UploadFile)
        file.filename = "test_resume.pdf"
        file.read = Mock(return_value=b"fake pdf content")
        return file

    @pytest.mark.asyncio
    async def test_save_file_creates_unique_job_id(self, mock_upload_file):
        """
        Test that save_file generates unique UUID4 job ID

        Expected: job_id is valid UUID4 format
        """
        result = await save_file(mock_upload_file)

        assert "job_id" in result
        assert len(result["job_id"]) == 36  # UUID4 length with hyphens

        # Verify UUID4 format
        import uuid
        try:
            uuid.UUID(result["job_id"], version=4)
            assert True
        except ValueError:
            assert False, "job_id should be valid UUID4"

    @pytest.mark.asyncio
    async def test_save_file_preserves_extension(self, mock_upload_file):
        """
        Test that file extension is preserved in stored filename

        Expected: stored_filename ends with .pdf
        """
        result = await save_file(mock_upload_file)

        assert result["stored_filename"].endswith(".pdf")
        assert ".pdf" in result["file_path"]

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_save_file_records_original_filename(self, mock_upload_file):
        """
        Test that original filename is recorded

        Expected: original_filename matches input
        """
        result = await save_file(mock_upload_file)

        assert result["original_filename"] == "test_resume.pdf"

    @pytest.mark.asyncio
    async def test_save_file_records_file_size(self, mock_upload_file):
        """
        Test that file size is recorded correctly

        Expected: file_size matches content length
        """
        result = await save_file(mock_upload_file)

        assert result["file_size"] == len(b"fake pdf content")
        assert result["file_size"] > 0

    @pytest.mark.asyncio
    async def test_save_file_includes_timestamp(self, mock_upload_file):
        """
        Test that upload timestamp is included

        Expected: upload_time is ISO format string
        """
        result = await save_file(mock_upload_file)

        assert "upload_time" in result
        assert "T" in result["upload_time"]  # ISO format includes 'T'
        assert ":" in result["upload_time"]  # Includes time

    @pytest.mark.asyncio
    async def test_save_file_status_is_uploaded(self, mock_upload_file):
        """
        Test that status is set to 'uploaded'

        Expected: status field is 'uploaded'
        """
        result = await save_file(mock_upload_file)

        assert result["status"] == "uploaded"

    @pytest.mark.asyncio
    async def test_save_file_with_docx(self):
        """
        Test saving DOCX file preserves extension

        Expected: .docx extension maintained
        """
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "resume.docx"
        mock_file.read = Mock(return_value=b"fake docx content")

        result = await save_file(mock_file)

        assert result["stored_filename"].endswith(".docx")
        assert result["original_filename"] == "resume.docx"

    @pytest.mark.asyncio
    async def test_save_file_with_txt(self):
        """
        Test saving TXT file preserves extension

        Expected: .txt extension maintained
        """
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "resume.txt"
        mock_file.read = Mock(return_value=b"plain text content")

        result = await save_file(mock_file)

        assert result["stored_filename"].endswith(".txt")

    @pytest.mark.asyncio
    async def test_save_file_creates_upload_directory(self, mock_upload_file):
        """
        Test that upload directory is created if not exists

        Expected: UPLOAD_DIR exists after save_file
        """
        await save_file(mock_upload_file)

        assert UPLOAD_DIR.exists()
        assert UPLOAD_DIR.is_dir()

    @pytest.mark.asyncio
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


class TestDeleteFile:
    """Unit tests for delete_file function"""

    def test_delete_existing_file(self, tmp_path):
        """
        Test deleting an existing file

        Expected: Returns True and file is deleted
        """
        # Create temporary test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()

        # Delete file
        result = delete_file(str(test_file))

        assert result is True
        assert not test_file.exists()

    def test_delete_nonexistent_file(self):
        """
        Test deleting a file that doesn't exist

        Expected: Returns False
        """
        result = delete_file("nonexistent_file.txt")

        assert result is False

    def test_delete_file_with_invalid_path(self):
        """
        Test deleting file with invalid path

        Expected: Returns False gracefully
        """
        result = delete_file("")

        assert result is False

    def test_delete_file_handles_oserror(self):
        """
        Test that OSError is handled gracefully

        Expected: Returns False on OSError
        """
        with patch('pathlib.Path.unlink', side_effect=OSError("Permission denied")):
            result = delete_file("some_file.txt")

            assert result is False

    def test_delete_file_with_directory(self, tmp_path):
        """
        Test deleting a directory (should fail gracefully)

        Expected: Returns False for directory
        """
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        result = delete_file(str(test_dir))

        assert result is False or not test_dir.exists()

    def test_delete_file_returns_false_for_protected_file(self):
        """
        Test deleting a protected/locked file

        Expected: Returns False
        """
        # This test simulates a locked file scenario
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.unlink', side_effect=PermissionError):
                result = delete_file("protected_file.txt")

                # Should return False due to OSError catch
                # PermissionError is a subclass of OSError
                assert result is False


class TestUploadDirectory:
    """Tests for upload directory management"""

    def test_upload_directory_exists(self):
        """
        Test that UPLOAD_DIR is created on import

        Expected: uploads/ directory exists
        """
        assert UPLOAD_DIR.exists()
        assert UPLOAD_DIR.is_dir()

    def test_upload_directory_path(self):
        """
        Test that UPLOAD_DIR has correct path

        Expected: Path is 'uploads'
        """
        assert UPLOAD_DIR.name == "uploads"
