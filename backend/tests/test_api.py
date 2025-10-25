from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_create_and_list_projects():
    # Create project
    resp = client.post("/api/projects", json={"youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "id" in data
    pid = data["id"]

    # List projects
    resp2 = client.get("/api/projects")
    assert resp2.status_code == 200
    items = resp2.json()
    assert any(p["id"] == pid for p in items)

