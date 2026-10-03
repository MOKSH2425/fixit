import io
import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_task_lifecycle(client):
    # 1. Create task
    payload = {
        "title": "Semester 6 Report",
        "description": "Submit hardcopy to department",
        "category": "Academic",
        "deadline": "2026-10-08",
    }
    create_res = client.post("/tasks", json=payload)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["title"] == "Semester 6 Report"
    assert data["category"] == "Academic"
    assert data["completed"] is False
    task_id = data["id"]

    # 2. Get tasks
    get_res = client.get("/tasks")
    assert get_res.status_code == 200
    tasks = get_res.json()
    assert any(t["id"] == task_id for t in tasks)

    # 3. Update task
    patch_res = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert patch_res.status_code == 200
    assert patch_res.json()["completed"] is True

def test_agent_validation_empty_file(client):
    file_content = b""
    files = {"file": ("test.png", io.BytesIO(file_content), "image/png")}
    res = client.post("/agent", files=files, data={"message": "Analyze this"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "upload a file" in data["error"].lower()

def test_agent_validation_invalid_type(client):
    file_content = b"fake executable content"
    files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}
    res = client.post("/agent", files=files, data={"message": "Analyze this"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "png, jpg" in data["error"].lower()

def test_agent_graceful_missing_api_key(client):
    # Valid PNG image bytes
    # Small 1x1 transparent PNG
    png_1x1 = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("test.png", io.BytesIO(png_1x1), "image/png")}
    res = client.post("/agent", files=files, data={"message": "Analyze this"})
    assert res.status_code == 200
    data = res.json()
    # When API key is empty or valid, check response structure
    assert "success" in data
