"""
Integration tests for upload API
Implements DRA-43: Integration test for Upload → Parsing flow
"""

import io
from fastapi.testclient import TestClient
from src.main import app
import pytest  # noqa: F401 (imported for test framework)

client = TestClient(app)


class TestUploadAPI:
    """Integration tests for upload endpoint"""

    def test_upload_valid_pdf_returns_202(self):
        """Test uploading valid PDF returns 202 Accepted"""
        pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\nHello PDF"

        response = client.post(
            "/api/v1/parse",
            files={"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )

        assert response.status_code == 202
        data = response.json()
        assert "jobId" in data
        assert data["status"] == "processing"
        assert "resume.pdf" in data["originalFilename"]

    def test_upload_valid_docx_returns_202(self):
        """Test uploading valid DOCX returns 202 Accepted"""
        docx_content = b"PK\x03\x04" + b"\x00" * 100

        response = client.post(
            "/api/v1/parse",
            files={
                "file": (
                    "resume.docx",
                    io.BytesIO(docx_content),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert "jobId" in data

    def test_upload_invalid_format_returns_415(self):
        """Test uploading invalid format returns 415 Unsupported Media Type"""
        jpg_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        response = client.post(
            "/api/v1/parse",
            files={"file": ("photo.jpg", io.BytesIO(jpg_content), "image/jpeg")},
        )

        assert response.status_code == 415
        assert "unsupported" in response.json()["detail"].lower()

    def test_upload_oversized_file_returns_413(self):
        """Test uploading file over 10MB returns 413 Payload Too Large"""
        large_content = b"x" * (11 * 1024 * 1024)

        response = client.post(
            "/api/v1/parse",
            files={"file": ("huge.pdf", io.BytesIO(large_content), "application/pdf")},
        )

        assert response.status_code == 413
        assert "too large" in response.json()["detail"].lower()

    def test_upload_empty_file_returns_413(self):
        """Test uploading empty file returns error"""
        response = client.post(
            "/api/v1/parse",
            files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
        )

        assert response.status_code == 413
        assert "empty" in response.json()["detail"].lower()

    def test_health_endpoint_returns_200(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
