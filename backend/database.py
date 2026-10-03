import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from config import DATABASE_PATH

def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection with dict-like row access."""
    db_path = Path(DATABASE_PATH)
    if not db_path.is_absolute():
        from config import BACKEND_DIR
        db_path = (BACKEND_DIR / db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize SQLite schema if it does not already exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL DEFAULT 'Other',
                deadline TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.commit()

def create_task_record(
    title: str,
    description: Optional[str] = None,
    category: str = "Other",
    deadline: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert a new task into SQLite using parameterized queries."""
    allowed_categories = {"Academic", "Personal", "Campus", "Technical", "Other"}
    if category not in allowed_categories:
        category = "Other"

    created_at = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (title, description, category, deadline, completed, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
            """,
            (title.strip(), description.strip() if description else None, category, deadline, created_at),
        )
        task_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row)

def get_all_tasks() -> List[Dict[str, Any]]:
    """Retrieve all tasks from SQLite ordered by creation time descending."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single task by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_task_record(task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update allowed fields of a task (e.g. completed, title, etc.)."""
    allowed_fields = {"completed", "title", "description", "category", "deadline"}
    fields_to_update = {k: v for k, v in updates.items() if k in allowed_fields and v is not None}

    if not fields_to_update:
        return get_task_by_id(task_id)

    set_clauses = []
    params = []
    for key, value in fields_to_update.items():
        if key == "completed":
            value = 1 if value else 0
        set_clauses.append(f"{key} = ?")
        params.append(value)
    params.append(task_id)

    query = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return get_task_by_id(task_id)

def delete_task_record(task_id: int) -> bool:
    """Delete a task by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
