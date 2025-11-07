"""
System test: End-to-end resume upload workflow.
"""

import io
from fastapi.testclient import TestClient
import asyncio  # <-- ADD THIS
from unittest.mock import Mock
import pytest

from src.main import app


@pytest.fixture
def duplicate_resume_file():
    """
    Creates an in-memory file-like object with duplicate
    sections for the FR-005 system test.
    """
    resume_text = """
    SUMMARY
    A senior developer.

    SKILLS
    Python, Java, C++
    
    EXPERIENCE
    My Job 1 at Company A
    
    TECHNICAL SKILLS
    SQL, Docker, Git
    
    Work Experience
    My Job 2 at Company B
    """
    # Create an in-memory bytes buffer
    file_io = io.BytesIO(resume_text.encode("utf-8"))

    # Return the format expected by the client.post 'files' argument
    return {"file": ("resume.pdf", file_io, "application/pdf")}


def test_end_to_end_resume_upload_flow():
    """
    Test complete resume upload process:
    1. Simulate file upload
    2. Verify the API returns jobId & processing status
    """
    client = TestClient(app)

    # Create a simple text resume
    resume_data = io.BytesIO(b"Sample resume file text")

    response = client.post(
        "/api/v1/parse", files={"file": ("resume.txt", resume_data, "text/plain")}
    )

    # Assert response
    assert (
        response.status_code == 202
    ), f"Expected 202, got {response.status_code}. Response: {response.json()}"
    json_data = response.json()

    # Verify response structure
    assert "jobId" in json_data, f"Missing jobId in response: {json_data}"
    assert (
        json_data["status"] == "processing"
    ), f"Expected status 'processing', got {json_data.get('status')}"
    assert "message" in json_data
    assert json_data["message"] == "Resume received for analysis."


def test_end_to_end_pdf_upload():
    """
    Test PDF upload with proper magic bytes
    """
    client = TestClient(app)

    # Create minimal PDF with proper header
    pdf_data = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF"

    response = client.post(
        "/api/v1/parse",
        files={"file": ("resume.pdf", io.BytesIO(pdf_data), "application/pdf")},
    )

    assert response.status_code == 202
    json_data = response.json()

    assert "jobId" in json_data
    assert json_data["status"] == "processing"


def test_end_to_end_invalid_file_rejected():
    """
    Test that invalid file types are properly rejected
    """
    client = TestClient(app)

    # Try to upload an image file
    jpg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"

    response = client.post(
        "/api/v1/parse",
        files={"file": ("photo.jpg", io.BytesIO(jpg_data), "image/jpeg")},
    )

    # Should be rejected with 415
    assert response.status_code == 415
    assert "Unsupported" in response.json()["detail"]


def test_upload_triggers_background_analysis(monkeypatch):
    """
    Tests that uploading a file *actually triggers*
    the `asyncio.create_task` with our `run_analysis` function.
    This confirms src.upload.service.py is working.

    (monkeypatch is a fixture provided by pytest)
    """

    # 1. Create a mock for asyncio.create_task
    mock_create_task = Mock()
    monkeypatch.setattr(asyncio, "create_task", mock_create_task)

    # 2. Get the TestClient
    client = TestClient(app)

    # 3. Create a dummy file (matching your other test)
    resume_data = io.BytesIO(b"Sample resume file text")
    files = {"file": ("resume.txt", resume_data, "text/plain")}

    # 4. Make the synchronous API call
    response = client.post("/api/v1/parse", files=files)

    # 5. Assert the response is correct
    assert response.status_code == 202

    # 6. Assert the mock was called
    # Check that `asyncio.create_task` was called exactly once
    assert mock_create_task.call_count == 1

    # 7. Check *what* it was called with
    call_args = mock_create_task.call_args[0]
    background_task = call_args[0]

    # This is the most important check:
    # It confirms the function we wrote in 'analyzer.py'
    # is the one being queued.
    assert background_task.__name__ == "run_analysis"


@pytest.mark.asyncio
async def test_fr005_end_to_end_merge_logic(async_client, duplicate_resume_file):
    """
    Tests the full end-to-end flow for FR-005.
    1. Uploads a resume with duplicate sections.
    2. Polls the results endpoint.
    3. Asserts that the final JSON response contains the merged sections.
    """

    # --- This is an assumption. Change if your endpoint is different ---
    RESULTS_ENDPOINT = "/api/results/"

    # 1. Upload the file to the /api/v1/parse endpoint
    response = await async_client.post("/api/v1/parse", files=duplicate_resume_file)

    assert response.status_code == 202
    data = response.json()
    assert "jobId" in data
    job_id = data["jobId"]

    # 2. Poll the results endpoint until the job is 'complete'
    report = None
    for _ in range(10):  # Poll for 5 seconds (10 * 0.5s)
        response = await async_client.get(f"{RESULTS_ENDPOINT}{job_id}")
        assert response.status_code == 200
        report = response.json()

        if report.get("status") == "complete":
            break

        await asyncio.sleep(0.5)  # Give the background task time to run

    # 3. Assert the final report is complete and correct
    assert report is not None, "Job did not complete in time"
    assert report["status"] == "complete", f"Job failed: {report.get('error')}"

    assert "analysis" in report
    structure_report = report["analysis"]["structure"]

    # AC: Check that the final JSON response has the merged sections
    assert "merged_sections" in structure_report

    # AC: Check that the content is merged
    assert "skills" in structure_report["merged_sections"]
    skills_content = structure_report["merged_sections"]["skills"]
    assert "Python, Java, C++" in skills_content
    assert "SQL, Docker, Git" in skills_content

    # AC: Check that the rest of the report is correct
    assert "skills" in structure_report["present_sections"]
    assert "education" in structure_report["missing_sections"]
    assert "projects" in structure_report["missing_sections"]
