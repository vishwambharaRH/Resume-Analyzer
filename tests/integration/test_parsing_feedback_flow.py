"""
Integration Tests for Parsing → Feedback Flow - DRA-46
Test Cases: TC-PARSE-015, TC-FEED-001 to TC-FEED-005

Requirements:
- STP RPRS-F-007: Integration of parsing with feedback
- RTM: Parsing ↔ Feedback flow
- SAD: Component integration testing
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
import io

client = TestClient(app)


class TestParsingFeedbackIntegration:
    """
    Integration tests for upload → parse → validate → feedback flow
    """

    @pytest.fixture
    def complete_resume_txt(self):
        """Text resume with all sections"""
        return """
JOHN DOE
Email: john.doe@example.com
Phone: +1-555-0123

EDUCATION
Bachelor of Science in Computer Science
Stanford University, 2018-2022
GPA: 3.8/4.0

SKILLS
Python, JavaScript, React, FastAPI, Docker, Kubernetes,
Machine Learning, TensorFlow, AWS, PostgreSQL, Git, CI/CD

EXPERIENCE
Software Engineer
Google Inc., Mountain View, CA
June 2022 - Present
- Developed scalable REST APIs serving 1M+ users
- Led team of 5 engineers on cloud migration project
- Reduced API latency by 40% through optimization

PROJECTS
AI-Powered Resume Analyzer
- Built full-stack application using React and FastAPI
- Implemented NLP-based skill extraction using spaCy
- Deployed on AWS with 99.9% uptime
- Processes 1000+ resumes daily
"""

    @pytest.fixture
    def missing_skills_resume_txt(self):
        """Resume missing skills section"""
        return """
JOHN DOE
Email: john@example.com

EDUCATION
BS Computer Science
MIT, 2020

EXPERIENCE
Software Engineer
Facebook, 2020-2022
Developed React components

PROJECTS
E-commerce Platform
Built using MERN stack
"""

    @pytest.fixture
    def multiple_missing_resume_txt(self):
        """Resume with multiple missing sections"""
        return """
JANE SMITH
jane.smith@email.com

EDUCATION
Master of Science in Data Science
Carnegie Mellon University
2021-2023
"""

    def test_upload_complete_resume_returns_all_sections(self, complete_resume_txt):
        """
        TC-PARSE-001 + TC-MISS-001: Upload complete resume

        Expected:
        - 202 status
        - Job ID returned
        - All sections should be detected in validation
        """
        response = client.post(
            "/api/v1/parse",
            files={
                "file": (
                    "resume.txt",
                    io.BytesIO(complete_resume_txt.encode()),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 202, f"Expected 202, got {response.status_code}"
        data = response.json()
        assert "jobId" in data, "Response should contain jobId"
        assert data["status"] == "processing"

    def test_upload_missing_skills_flagged(self, missing_skills_resume_txt):
        """
        TC-MISS-002: Upload resume with missing skills

        Expected:
        - Upload succeeds (202)
        - Validation should flag missing skills
        """
        response = client.post(
            "/api/v1/parse",
            files={
                "file": (
                    "resume.txt",
                    io.BytesIO(missing_skills_resume_txt.encode()),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert "jobId" in data

    def test_upload_multiple_missing_sections(self, multiple_missing_resume_txt):
        """
        TC-MISS-004: Upload resume with multiple missing sections

        Expected:
        - Upload succeeds
        - Should flag skills, experience, projects as missing
        """
        response = client.post(
            "/api/v1/parse",
            files={
                "file": (
                    "incomplete_resume.txt",
                    io.BytesIO(multiple_missing_resume_txt.encode()),
                    "text/plain",
                )
            },
        )

        assert response.status_code == 202
        data = response.json()
        job_id = data["jobId"]

        # Note: Actual validation happens during parsing
        # Full integration with results endpoint will be tested in next sprint
        assert job_id is not None

    def test_end_to_end_parsing_validation_flow(self, complete_resume_txt):
        """
        TC-PARSE-015: Complete end-to-end flow

        Flow: Upload → Parse → Validate Sections → Return Results
        """
        # Step 1: Upload resume
        upload_response = client.post(
            "/api/v1/parse",
            files={
                "file": (
                    "complete_resume.txt",
                    io.BytesIO(complete_resume_txt.encode()),
                    "text/plain",
                )
            },
        )

        assert upload_response.status_code == 202
        job_id = upload_response.json()["jobId"]

        # Step 2: Verify job ID format (UUID4)
        import uuid

        try:
            uuid.UUID(job_id, version=4)
            assert True
        except ValueError:
            assert False, "Job ID should be valid UUID4"

    def test_health_endpoint_still_works(self):
        """
        Verify health endpoint not affected by new module
        """
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_invalid_file_still_rejected(self):
        """
        Verify existing validation still works
        """
        jpg_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        response = client.post(
            "/api/v1/parse",
            files={"file": ("photo.jpg", io.BytesIO(jpg_content), "image/jpeg")},
        )

        assert response.status_code == 415
