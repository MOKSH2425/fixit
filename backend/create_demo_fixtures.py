from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

def create_error_screenshot():
    """Generates a realistic terminal / IDE error screenshot."""
    width, height = 800, 420
    img = Image.new("RGB", (width, height), color="#0f172a") # Dark slate background
    draw = ImageDraw.Draw(img)

    # Terminal top bar
    draw.rectangle([(0, 0), (width, 36)], fill="#1e293b")
    # Window dots
    draw.ellipse([(14, 12), (26, 24)], fill="#ef4444")
    draw.ellipse([(34, 12), (46, 24)], fill="#f59e0b")
    draw.ellipse([(54, 12), (66, 24)], fill="#10b981")
    draw.text((320, 10), "bash - python app.py", fill="#94a3b8")

    # Terminal content
    y = 55
    lines = [
        ("$ python main.py", "#38bdf8"),
        ("Traceback (most recent call last):", "#f87171"),
        ('  File "c:/Users/Moksh/Desktop/FIXIT/main.py", line 4, in <module>', "#cbd5e1"),
        ("    from fastapi import FastAPI, HTTPException", "#cbd5e1"),
        ("ModuleNotFoundError: No module named 'fastapi'", "#ef4444"),
        ("", "#ffffff"),
        ("[Process exited with return code 1]", "#64748b"),
        ("$ _", "#38bdf8"),
    ]

    for text, color in lines:
        draw.text((25, y), text, fill=color)
        y += 35

    img.save(DEMO_DIR / "technical_error.png")
    print(f"Created {DEMO_DIR / 'technical_error.png'}")

def create_notice_image():
    """Generates a realistic college notice / announcement."""
    width, height = 800, 520
    img = Image.new("RGB", (width, height), color="#f8fafc") # Paper white
    draw = ImageDraw.Draw(img)

    # Header banner
    draw.rectangle([(0, 0), (width, 90)], fill="#1e3a8a") # Deep Navy
    draw.text((220, 22), "DEPARTMENT OF COMPUTER ENGINEERING", fill="#ffffff")
    draw.text((290, 50), "OFFICIAL ACADEMIC NOTICE", fill="#93c5fd")

    # Body border
    draw.rectangle([(30, 110), (width - 30, height - 30)], outline="#cbd5e1", width=2)

    # Notice content
    y = 135
    draw.text((50, y), "NOTICE REF: CE/2026/OCT-04", fill="#64748b")
    y += 30
    draw.text((50, y), "DATE: 03 OCTOBER 2026", fill="#64748b")
    y += 45

    draw.text((50, y), "SUBJECT: SUBMISSION OF SEMESTER 6 PROJECT REPORT", fill="#0f172a")
    y += 40

    body_lines = [
        "All Semester 6 B.Tech students are hereby informed that the final draft of",
        "the Major Project Report must be submitted to the Department Project Desk.",
        "",
        "CRITICAL DEADLINE: OCTOBER 8, 2026 (5:00 PM)",
        "",
        "Mandatory Actions for Students:",
        "1. Complete final project report verification with assigned guide.",
        "2. Print hardcopy with proper spiral binding.",
        "3. Submit the signed physical copy at the department office before deadline.",
        "",
        "Note: Late submissions will not be accepted under any circumstances.",
    ]

    for line in body_lines:
        color = "#b91c1c" if "CRITICAL DEADLINE" in line else "#334155"
        draw.text((50, y), line, fill=color)
        y += 26

    # Signature block
    draw.text((width - 250, height - 70), "Head of Department", fill="#1e293b")
    draw.text((width - 250, height - 50), "Computer Engineering", fill="#64748b")

    img.save(DEMO_DIR / "sample_notice.png")
    print(f"Created {DEMO_DIR / 'sample_notice.png'}")

if __name__ == "__main__":
    create_error_screenshot()
    create_notice_image()
