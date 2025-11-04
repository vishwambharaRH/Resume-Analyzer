"""System test: End-to-end resume upload workflow."""

import io
from fastapi.testclient import TestClient

from src.main import app  # Ensure your main FastAPI app is in src/main.py


def test_end_to_end_resume_upload_flow():
    """
    Test complete resume upload process:
    1. Simulate file upload
    2. Verify the API returns jobId & processing status
    """
    client = TestClient(app)

    resume_data = io.BytesIO(b"Sample resume file text")
    response = client.post(
        "/upload/",
        files={"file": ("resume.txt", resume_data, "text/plain")}
    )

    assert response.status_code == 202
    json_data = response.json()

    assert "jobId" in json_data
    assert json_data["status"] == "processing"
