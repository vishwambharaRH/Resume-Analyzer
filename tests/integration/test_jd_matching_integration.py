"""
Integration test for FR-012 complete flow
Implements DRA-73
"""

import pytest
import io
from fastapi.testclient import TestClient
from src.main import app


class TestJDMatchingIntegration:
    """Test complete JD matching flow"""

    def test_compare_endpoint_complete_flow(self):
        """Test end-to-end comparison flow"""
        client = TestClient(app)

        # Create test resume
        resume_content = b"""
        John Doe
        Software Engineer
        
        SKILLS
        Python, JavaScript, React, Node.js, MongoDB
        
        EXPERIENCE
        Software Engineer at TechCorp
        5 years of experience
        
        EDUCATION
        Bachelor of Science in Computer Science
        Stanford University
        """

        # Job description
        jd_text = """
        We are hiring a Senior Software Engineer.
        
        Required Skills:
        - Python
        - JavaScript
        - React
        - AWS
        - Docker
        
        Requirements:
        - 5+ years of experience
        - Bachelor's degree in Computer Science
        """

        # Make API call
        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", io.BytesIO(resume_content), "text/plain")},
            data={"job_description": jd_text},
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "fit_percentage" in data
        assert "fit_category" in data
        assert "matched_skills" in data
        assert "missing_skills" in data
        assert "recommendations" in data

        # Verify fit percentage is reasonable
        assert 0 <= data["fit_percentage"] <= 100

        # Verify matched skills
        assert len(data["matched_skills"]) > 0
        assert "Python" in data["matched_skills"]

        # Verify missing skills detected
        assert "AWS" in data["missing_skills"] or "Aws" in data["missing_skills"]

    def test_invalid_file_rejected(self):
        """Test that invalid files are rejected"""
        client = TestClient(app)

        # Try to upload an image
        jpg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"

        response = client.post(
            "/api/v1/compare/",
            files={"file": ("photo.jpg", io.BytesIO(jpg_data), "image/jpeg")},
            data={"job_description": "Test JD"},
        )

        assert response.status_code == 415

    def test_empty_jd(self):
        """Test with empty job description"""
        client = TestClient(app)

        resume_content = b"Python developer with 5 years experience"

        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", io.BytesIO(resume_content), "text/plain")},
            data={"job_description": ""},
        )

        assert response.status_code in [200, 422]

    def test_skills_only_jd(self):
        """Test JD with only skills, no exp/edu requirements"""
        client = TestClient(app)

        resume_content = b"""
        SKILLS
        Python JavaScript React AWS Docker
        """

        jd_text = "Python, JavaScript, React required"

        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", io.BytesIO(resume_content), "text/plain")},
            data={"job_description": jd_text},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["fit_percentage"] >= 50
