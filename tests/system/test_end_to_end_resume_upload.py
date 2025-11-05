"""
System test: End-to-end resume upload workflow.
"""

import io
from fastapi.testclient import TestClient

from src.main import app


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
        "/api/v1/parse",
        files={"file": ("resume.txt", resume_data, "text/plain")}
    )

    # Assert response
    assert response.status_code == 202, f"Expected 202, got {response.status_code}. Response: {response.json()}"
    json_data = response.json()

    # Verify response structure
    assert "jobId" in json_data, f"Missing jobId in response: {json_data}"
    assert json_data["status"] == "processing", f"Expected status 'processing', got {json_data.get('status')}"
    assert "message" in json_data
    assert json_data["message"] == "Resume received for analysis."


def test_end_to_end_pdf_upload():
    """
    Test PDF upload with proper magic bytes
    """
    client = TestClient(app)

    # Create minimal PDF with proper header
    pdf_data = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF'
    
    response = client.post(
        "/api/v1/parse",
        files={"file": ("resume.pdf", io.BytesIO(pdf_data), "application/pdf")}
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
    jpg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    
    response = client.post(
        "/api/v1/parse",
        files={"file": ("photo.jpg", io.BytesIO(jpg_data), "image/jpeg")}
    )

    # Should be rejected with 415
    assert response.status_code == 415
    assert "Unsupported" in response.json()["detail"]