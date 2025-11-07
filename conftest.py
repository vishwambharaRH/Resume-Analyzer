"""
Pytest configuration and fixtures
Fixes import paths and provides test utilities
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"✓ Python path configured: {project_root}")


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_pdf_content():
    """Return sample PDF content"""
    return b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"


@pytest.fixture
def sample_txt_content():
    """Return sample text content"""
    return b"John Doe\nSoftware Engineer\nSkills: Python, FastAPI"


@pytest.fixture
def sample_docx_bytes():
    """Return sample DOCX magic bytes"""
    return b"PK\x03\x04"  # ZIP format (DOCX is ZIP)


@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Clean up uploads directory after each test"""
    yield
    upload_dir = Path("uploads")
    if upload_dir.exists():
        for file in upload_dir.glob("*"):
            if file.is_file():
                file.unlink()


@pytest.fixture
def test_client():
    """Return FastAPI test client for integration tests"""
    from src.main import app

    return TestClient(app)
