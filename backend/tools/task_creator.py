from typing import Optional, Dict, Any
try:
    from database import create_task_record
except ImportError:
    from backend.database import create_task_record

ALLOWED_TASK_CATEGORIES = {"Academic", "Personal", "Campus", "Technical", "Other"}

def create_task(
    title: str,
    description: Optional[str] = None,
    category: str = "Other",
    deadline: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool to persist a real actionable task into the local SQLite database.
    
    Parameters:
      title: Short, clear title for the task (required)
      description: Detailed notes or context
      category: 'Academic', 'Personal', 'Campus', 'Technical', or 'Other'
      deadline: Optional date string (e.g. YYYY-MM-DD or 'October 8')
    """
    if not title or not title.strip():
        return {
            "status": "error",
            "message": "Task title cannot be empty",
        }

    cat = category.capitalize() if category else "Other"
    if cat not in ALLOWED_TASK_CATEGORIES:
        cat = "Other"

    clean_deadline = deadline.strip() if deadline and deadline.strip() else None

    try:
        record = create_task_record(
            title=title.strip(),
            description=description.strip() if description else None,
            category=cat,
            deadline=clean_deadline,
        )
        return {
            "status": "success",
            "task_id": record["id"],
            "title": record["title"],
            "category": record["category"],
            "deadline": record["deadline"],
            "completed": bool(record["completed"]),
            "created_at": record["created_at"],
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database insertion failed: {str(e)}",
        }
