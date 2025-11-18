import os
import importlib
from fastapi.testclient import TestClient


def test_https_enforcement_redirect(monkeypatch):
    """Test stub for HTTPS enforcement middleware.

    This test sets ENFORCE_HTTPS and reloads the main app to validate that
    HTTP requests (via X-Forwarded-Proto header) are redirected to HTTPS.
    """
    monkeypatch.setenv("ENFORCE_HTTPS", "true")

    # reload module to pick up env var
    import src.main as main_mod

    importlib.reload(main_mod)

    client = TestClient(main_mod.app)

    headers = {"x-forwarded-proto": "http"}
    resp = client.get("/", headers=headers, follow_redirects=False)

    # When enforcement is enabled, requests should be redirected to https
    assert resp.status_code in (301, 307)
    # Location header should contain https scheme
    loc = resp.headers.get("location") or resp.headers.get("Location")
    assert loc is not None
    assert loc.startswith("https://")
