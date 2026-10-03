import pytest
from tools.analyze_image import analyze_image
from tools.action_plan import generate_action_plan
from tools.checklist import generate_checklist
from tools.task_creator import create_task
from database import init_db, get_all_tasks, delete_task_record

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_analyze_image_tool():
    res = analyze_image(
        category="technical_error",
        title="Missing Python dependency",
        problem="ModuleNotFoundError: No module named 'fastapi'",
        important_details=["fastapi", "Python", "ModuleNotFoundError"],
        confidence="high",
    )
    assert res["status"] == "success"
    assert res["category"] == "technical_error"
    assert res["title"] == "Missing Python dependency"
    assert len(res["important_details"]) == 3
    assert res["confidence"] == "high"

def test_generate_action_plan_tool():
    res = generate_action_plan(
        summary="Install FastAPI and re-run application",
        actions=[
            "Install FastAPI in the active environment",
            "Verify environment activation",
            "Run application again",
        ],
        priority="high",
    )
    assert res["status"] == "success"
    assert len(res["actions"]) == 3
    assert res["priority"] == "high"

def test_generate_checklist_tool():
    res = generate_checklist(
        items=[
            "Install dependency",
            "Verify environment",
            "Run application",
        ]
    )
    assert res["status"] == "success"
    assert len(res["items"]) == 3
    assert res["items"][0] == "Install dependency"

def test_create_task_tool():
    res = create_task(
        title="Submit Project Report",
        description="Submit hardcopy to department desk",
        category="Academic",
        deadline="2026-10-08",
    )
    assert res["status"] == "success"
    assert res["task_id"] > 0
    assert res["title"] == "Submit Project Report"
    assert res["category"] == "Academic"
    assert res["deadline"] == "2026-10-08"

    # Cleanup test task
    delete_task_record(res["task_id"])
