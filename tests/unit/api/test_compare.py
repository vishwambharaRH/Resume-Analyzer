"""
Unit tests for Compare API (FR-012)
"""

import pytest
import io
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from src.main import app


class TestCompareAPI:
    """Test compare endpoint"""

    def test_compare_endpoint_health(self):
        """Test that compare health endpoint works"""
        client = TestClient(app)
        response = client.get("/api/v1/compare/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_missing_file(self):
        """Test compare without file"""
        client = TestClient(app)
        response = client.post(
            "/api/v1/compare/", data={"job_description": "Python required"}
        )
        assert response.status_code == 400
        assert "file is required" in response.json()["detail"].lower()

    def test_missing_jd(self):
        """Test compare without job description"""
        client = TestClient(app)
        resume = io.BytesIO(b"test resume")
        response = client.post(
            "/api/v1/compare/", files={"file": ("resume.txt", resume, "text/plain")}
        )
        assert response.status_code == 400
        assert "job_description" in response.json()["detail"].lower()

    def test_empty_jd(self):
        """Test compare with empty job description"""
        client = TestClient(app)
        resume = io.BytesIO(b"test resume")
        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", resume, "text/plain")},
            data={"job_description": ""},
        )
        assert response.status_code in [200, 422]

    def test_invalid_file_extension(self):
        """Test compare with invalid file type"""
        client = TestClient(app)
        jpg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        response = client.post(
            "/api/v1/compare/",
            files={"file": ("photo.jpg", io.BytesIO(jpg_data), "image/jpeg")},
            data={"job_description": "Python required"},
        )
        assert response.status_code == 415
        assert "Unsupported file type" in response.json()["detail"]

    @patch("src.api.compare.run_analysis", new_callable=AsyncMock)
    def test_successful_comparison(self, mock_run_analysis):
        """Test successful resume vs JD comparison"""
        client = TestClient(app)

        # Mock analyzer response
        mock_run_analysis.return_value = {
            "status": "complete",
            "analysis": {
                "skills": {"technical_skills": ["Python", "JavaScript", "React"]},
                "structure": {
                    "merged_sections": {
                        "skills": "Python, JavaScript, React",
                        "experience": "5 years as Software Engineer",
                        "education": "BS Computer Science",
                    }
                },
            },
        }

        resume_content = b"Test resume content"
        jd_text = "Python JavaScript required"

        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", io.BytesIO(resume_content), "text/plain")},
            data={"job_description": jd_text},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "fit_percentage" in data
        assert "fit_category" in data
        assert "matched_skills" in data
        assert "missing_skills" in data
        assert "recommendations" in data
        assert "explanation" in data

        # Verify types
        assert isinstance(data["fit_percentage"], (int, float))
        assert isinstance(data["matched_skills"], list)
        assert isinstance(data["recommendations"], list)

        # Verify fit percentage is in valid range
        assert 0 <= data["fit_percentage"] <= 100

    @patch("src.api.compare.run_analysis", new_callable=AsyncMock)
    def test_no_skills_matched(self, mock_run_analysis):
        """Test when no skills match"""
        client = TestClient(app)

        mock_run_analysis.return_value = {
            "status": "complete",
            "analysis": {
                "skills": {"technical_skills": ["Java", "Spring"]},
                "structure": {
                    "merged_sections": {
                        "skills": "Java, Spring",
                        "experience": "3 years",
                        "education": "",
                    }
                },
            },
        }

        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", io.BytesIO(b"resume"), "text/plain")},
            data={"job_description": "Python AWS Docker required"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["matched_skills"]) == 0
        assert len(data["missing_skills"]) > 0

    @patch("src.api.compare.run_analysis", new_callable=AsyncMock)
    def test_analyzer_failure(self, mock_run_analysis):
        """Test when analyzer fails"""
        client = TestClient(app)

        mock_run_analysis.return_value = {"status": "failed", "error": "Parse error"}

        response = client.post(
            "/api/v1/compare/",
            files={"file": ("resume.txt", io.BytesIO(b"resume"), "text/plain")},
            data={"job_description": "Python required"},
        )

        assert response.status_code == 500

    def test_pdf_file_accepted(self):
        """Test that PDF files are accepted"""
        client = TestClient(app)

        # Minimal valid PDF
        pdf_data = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"

        with patch("src.api.compare.run_analysis", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "status": "complete",
                "analysis": {
                    "skills": {"technical_skills": ["Python"]},
                    "structure": {
                        "merged_sections": {
                            "skills": "Python",
                            "experience": "",
                            "education": "",
                        }
                    },
                },
            }

            response = client.post(
                "/api/v1/compare/",
                files={"file": ("resume.pdf", io.BytesIO(pdf_data), "application/pdf")},
                data={"job_description": "Python required"},
            )

            assert response.status_code == 200

    def test_docx_file_accepted(self):
        """Test that DOCX files are accepted"""
        client = TestClient(app)

        # Mock DOCX file (just needs .docx extension)
        docx_data = b"PK\x03\x04"  # ZIP header (DOCX is a ZIP file)

        with patch("src.api.compare.run_analysis", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "status": "complete",
                "analysis": {
                    "skills": {"technical_skills": ["Python"]},
                    "structure": {
                        "merged_sections": {
                            "skills": "Python",
                            "experience": "",
                            "education": "",
                        }
                    },
                },
            }

            response = client.post(
                "/api/v1/compare/",
                files={
                    "file": (
                        "resume.docx",
                        io.BytesIO(docx_data),
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
                },
                data={"job_description": "Python required"},
            )

            assert response.status_code == 200


class TestConvertAnalyzerResults:
    """Test analyzer result conversion"""

    def test_convert_complete_result(self):
        """Test converting complete analyzer result"""
        from src.api.compare import convert_analyzer_results_to_standard_format

        analysis = {
            "status": "complete",
            "analysis": {
                "skills": {"technical_skills": ["Python", "JavaScript"]},
                "structure": {
                    "merged_sections": {
                        "skills": "React",
                        "experience": "5 years engineer",
                        "education": "BS CS",
                    }
                },
            },
        }

        result = convert_analyzer_results_to_standard_format(analysis)

        assert "Python" in result["skills"]
        assert "JavaScript" in result["skills"]
        assert "React" in result["skills"]
        assert result["experience"] == "5 years engineer"
        assert result["education"] == "BS CS"

    def test_convert_failed_result(self):
        """Test converting failed analyzer result"""
        from src.api.compare import convert_analyzer_results_to_standard_format

        analysis = {"status": "failed", "error": "Parse error"}

        with pytest.raises(ValueError):
            convert_analyzer_results_to_standard_format(analysis)

    def test_convert_with_empty_sections(self):
        """Test converting result with empty sections"""
        from src.api.compare import convert_analyzer_results_to_standard_format

        analysis = {
            "status": "complete",
            "analysis": {"skills": {}, "structure": {"merged_sections": {}}},
        }

        result = convert_analyzer_results_to_standard_format(analysis)

        assert result["skills"] == []
        assert result["experience"] == ""
        assert result["education"] == ""
