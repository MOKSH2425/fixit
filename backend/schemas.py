from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Short title of the task")
    description: Optional[str] = Field(None, description="Detailed explanation or instruction")
    category: str = Field("Other", description="Allowed: Academic, Personal, Campus, Technical, Other")
    deadline: Optional[str] = Field(None, description="Optional deadline date string (e.g. YYYY-MM-DD)")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    completed: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    deadline: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: str = "Other"
    deadline: Optional[str] = None
    completed: bool = False
    created_at: str

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "TaskResponse":
        return cls(
            id=row["id"],
            title=row["title"],
            description=row.get("description"),
            category=row.get("category", "Other"),
            deadline=row.get("deadline"),
            completed=bool(row.get("completed", 0)),
            created_at=row.get("created_at", ""),
        )

class ImageAnalysis(BaseModel):
    category: str = Field("unknown", description="technical_error, campus_notice, assignment, instructions, document, general_problem, unknown")
    title: str = Field(..., description="Concise headline")
    problem: str = Field(..., description="Root issue or essential notice message")
    important_details: List[str] = Field(default_factory=list, description="Keywords, deadlines, module names, or dates")
    confidence: str = Field("high", description="Qualitative confidence: low, medium, high")

class ActionPlan(BaseModel):
    summary: str = Field(..., description="Brief overview of recommended remediation or next steps")
    priority: str = Field("medium", description="low, medium, high, critical")
    actions: List[str] = Field(default_factory=list, description="Ordered concrete next steps")

class ChecklistOutput(BaseModel):
    items: List[str] = Field(default_factory=list, description="Concise checklist items")

class AgentResponse(BaseModel):
    success: bool
    category: str = "unknown"
    title: str = ""
    problem: str = ""
    actions: List[str] = Field(default_factory=list)
    checklist: List[str] = Field(default_factory=list)
    created_tasks: List[TaskResponse] = Field(default_factory=list)
    agent_activity: List[str] = Field(default_factory=list)
    final_response: str = ""
    error: Optional[str] = None
