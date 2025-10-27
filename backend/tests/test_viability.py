from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_viability_endpoint_shape():
    payload = {
        "title": "Build a SaaS with auth and pricing",
        "transcript": "In this tutorial we will build a dashboard with login, signup, pricing and an API. Step by step instructions...",
    }
    resp = client.post("/api/viability-check", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert set(["mvp_viability", "viability_score", "viability_reason"]).issubset(data.keys())
    assert data["mvp_viability"] in {"mvp-ready", "idea-only", "not-a-project"}
    assert 0.0 <= float(data["viability_score"]) <= 1.0


def test_project_read_includes_viability_fields():
    # Create project
    resp = client.post("/api/projects", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert resp.status_code == 200, resp.text
    proj = resp.json()
    # Keys exist even if None initially
    assert "mvp_viability" in proj
    assert "viability_score" in proj
    assert "viability_reason" in proj

