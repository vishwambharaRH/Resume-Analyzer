"""
Unit tests for the batch upload service logic.
(Implements DRA-102)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import UploadFile
from src.upload.service import process_batch_upload

# Mark all tests in this file as asyncio, which is required
# for testing async functions.
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_files(mocker):
    """Creates a list of mock UploadFile objects."""
    file1 = mocker.MagicMock(spec=UploadFile)
    file1.filename = "resume1.pdf"

    file2 = mocker.MagicMock(spec=UploadFile)
    file2.filename = "resume2.docx"

    return [file1, file2]


async def test_process_batch_upload_calls_helpers(mock_files, mocker):
    """
    Tests that process_batch_upload calls save_file
    for each file in the batch.
    """
    # 1. Mock save_file (which internally calls run_analysis)
    mock_save = AsyncMock(
        return_value={"job_id": "job-1", "file_path": "path/1.pdf"}  # ✅ Fix key name
    )

    # 2. Patch save_file in the service module
    mocker.patch("src.upload.service.save_file", mock_save)

    # 3. Call the function with our mock files
    results = await process_batch_upload(mock_files)

    # 4. Assert the results are correct
    assert len(results) == 2
    assert results[0]["filename"] == "resume1.pdf"
    assert results[1]["filename"] == "resume2.docx"
    assert results[0]["status"] == "processing"
    assert results[1]["status"] == "processing"

    # 5. Assert that save_file was called twice
    assert mock_save.call_count == 2
