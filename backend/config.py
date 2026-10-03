import os
from pathlib import Path
from dotenv import load_dotenv

# Base backend directory
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# Load .env from backend/.env or root .env
dotenv_path = BACKEND_DIR / ".env"
if not dotenv_path.exists():
    dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it").strip()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# Database path
default_db_dir = PROJECT_ROOT / "data"
default_db_dir.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = os.getenv("DATABASE_URL", str(default_db_dir / "fixit.db"))

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
