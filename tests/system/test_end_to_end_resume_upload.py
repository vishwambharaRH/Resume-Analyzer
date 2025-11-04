"""
System test: End-to-end resume upload workflow
Tests complete flow from upload to response
"""

import io
from fastapi.testclient import TestClient
from src.main import app


def test_end_to_end_resume_upload_flow():
    """
    Test complete resume upload process:
    1. Create sample resume file
    2. Upload via API
    3. Verify 202 status and jobId returned
    """
    client = TestClient(app)

    # Create sample resume content
    resume_content = b"""
    JOHN DOE
    Email: john@example.com
    Phone: +1-555-0123
    
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University, 2020
    
    SKILLS
    Python, JavaScript, React, FastAPI
    
    EXPERIENCE
    Software Engineer at Google
    2020-Present
    
    PROJECTS
    AI Resume Analyzer
    Built with FastAPI and React
    """

    # Upload resume
    response = client.post(
        "/api/v1/parse",
        files={"file": ("resume.txt", io.BytesIO(resume_content), "text/plain")},
    )

    # Verify response
    assert response.status_code == 202, f"Expected 202, got {response.status_code}"
    json_data = response.json()

    assert "jobId" in json_data, "Response should contain jobId"
    assert json_data["status"] == "processing", "Status should be 'processing'"
    assert "message" in json_data, "Response should contain message"
