import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS, HOST, PORT
from database import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    create_task_record,
    update_task_record,
)
from schemas import (
    AgentResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)
from agent import FixItAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fixit.server")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite schema
    logger.info("Initializing FixIt SQLite database...")
    init_db()
    yield
    logger.info("FixIt backend shutting down.")

app = FastAPI(
    title="FixIt API",
    description="Multimodal AI Action Agent — See a problem. Get an action.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="Health check")
def health_check():
    """Returns backend system status."""
    return {"status": "ok"}

@app.post("/agent", response_model=AgentResponse, summary="Process image through multimodal action agent")
async def process_agent_request(
    image: UploadFile = File(..., description="Uploaded image file (PNG, JPG, WEBP)"),
    message: Optional[str] = Form(None, description="Optional user prompt or instruction"),
):
    """
    Multimodal entry point:
    Receives image + optional message, orchestrates Gemma 4 reasoning,
    executes registered application tools, and returns actionable results.
    """
    try:
        image_bytes = await image.read()
        content_type = image.content_type or "image/png"
        
        agent = FixItAgent()
        result = agent.process(
            image_bytes=image_bytes,
            content_type=content_type,
            user_message=message,
        )
        return result
    except Exception as e:
        logger.exception("Unexpected error in /agent endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FixIt backend error: {str(e)}",
        )

@app.get("/tasks", response_model=List[TaskResponse], summary="Retrieve all persisted tasks")
def get_tasks():
    """Returns all tasks stored in SQLite."""
    try:
        rows = get_all_tasks()
        return [TaskResponse.from_row(r) for r in rows]
    except Exception as e:
        logger.exception("Failed to retrieve tasks")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task_endpoint(task_in: TaskCreate):
    """Creates a task in SQLite."""
    try:
        row = create_task_record(
            title=task_in.title,
            description=task_in.description,
            category=task_in.category,
            deadline=task_in.deadline,
        )
        return TaskResponse.from_row(row)
    except Exception as e:
        logger.exception("Failed to create task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

@app.patch("/tasks/{task_id}", response_model=TaskResponse, summary="Update task completion state or details")
def update_task_endpoint(task_id: int, task_update: TaskUpdate):
    """Update task completion or fields."""
    existing = get_task_by_id(task_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    updates = task_update.model_dump(exclude_unset=True)
    try:
        updated = update_task_record(task_id, updates)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found",
            )
        return TaskResponse.from_row(updated)
    except Exception as e:
        logger.exception(f"Failed to update task {task_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
