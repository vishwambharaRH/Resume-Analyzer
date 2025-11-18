"""
Integration test for the full batch upload workflow.
Validates the /api/v1/parse/batch endpoint.
(Implements DRA-103)
"""

import io
import pytest
import asyncio
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


def test_batch_upload_workflow(client, monkeypatch):
    """
    Tests the /api/v1/parse/batch endpoint with multiple valid files.
    """
    # 1. Mock the background task (asyncio.create_task)
    # We are only testing the upload API, not the full analysis,
    # so we mock this to prevent the analysis from running.
    monkeypatch.setattr("src.upload.service.asyncio.create_task", lambda _: None)

    # 2. Create mock file data
    # We use real file headers (like %PDF) to pass validation.
    file1_data = (
        "resume1.pdf",
        io.BytesIO(b"%PDF-fake-pdf-content"),
        "application/pdf",
    )
    file2_data = ("resume2.txt", io.BytesIO(b"fake text content"), "text/plain")

    # 3. Post the files to the new /batch endpoint.
    # Note: The files are sent as a list of tuples.
    response = client.post(
        "/api/v1/parse/batch", files=[("files", file1_data), ("files", file2_data)]
    )

    # 4. Assert the response is correct
    assert (
        response.status_code == 202
    ), f"API failed with {response.status_code}: {response.json()}"
    data = response.json()

    # Check the message and job list
    assert "Batch of 2 resumes received" in data["message"]
    assert len(data["jobs"]) == 2

    # Check that the job details are correct
    assert data["jobs"][0]["filename"] == "resume1.pdf"
    assert data["jobs"][1]["filename"] == "resume2.txt"
    # ...
    # Check that the job details are correct
    assert data["jobs"][0]["filename"] == "resume1.pdf"
    assert data["jobs"][1]["filename"] == "resume2.txt"
