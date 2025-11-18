import os
from fastapi.testclient import TestClient
from src.main import app


def test_http_exception_structured_response():
    client = TestClient(app)

    # send an invalid file type (simulate .exe) by posting raw data
    files = {"file": ("bad.exe", b"dummy content")}
    resp = client.post("/api/v1/parse/", files=files)

    assert resp.status_code in (415, 400, 422, 500)
    data = resp.json()
    # Ensure structured error fields exist
    assert isinstance(data, dict)
    assert "error" in data
