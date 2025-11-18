import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.main import app
from src.api.results import get_results

client = TestClient(app)


# ===============================================================
# 1. Missing Job ID -> 404
# ===============================================================
@pytest.mark.asyncio
async def test_get_results_missing_job_id():
    with pytest.raises(HTTPException) as exc:
        await get_results("")

    err = exc.value
    assert err.status_code == 404
    assert "Job ID not found" in err.detail


# ===============================================================
# 2. Successful Response Structure
# ===============================================================
@pytest.mark.asyncio
async def test_get_results_success_structure():
    job_id = "12345"
    result = await get_results(job_id)

    assert result["status"] == "completed"
    assert result["jobId"] == job_id

    assert "sections" in result
    assert "validation" in result
    assert "feedback" in result

    # FR-003: incomplete feedback exists
    assert len(result["feedback"]["incomplete_sections"]) > 0


# ===============================================================
# 3. API route test using FastAPI TestClient
# ===============================================================
def test_results_api_route():
    response = client.get("/api/v1/results/abc123")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "completed"
    assert body["jobId"] == "abc123"
    assert "sections" in body
    assert "feedback" in body
    assert len(body["feedback"]["incomplete_sections"]) > 0
