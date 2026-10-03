from typing import List, Dict, Any

ALLOWED_CATEGORIES = {
    "technical_error",
    "assignment",
    "campus_notice",
    "instructions",
    "document",
    "general_problem",
    "unknown",
}

def analyze_image(
    category: str,
    title: str,
    problem: str,
    important_details: List[str] = None,
    confidence: str = "high",
) -> Dict[str, Any]:
    """
    Tool to record the structured visual analysis of an image.
    
    Parameters:
      category: One of 'technical_error', 'campus_notice', 'assignment', 'instructions', 'document', 'general_problem', 'unknown'
      title: Short headline identifying the problem or notice topic
      problem: Clear description of the error, deadline, or requirement detected
      important_details: List of key details like library names, dates, course codes, error codes
      confidence: Qualitative assessment ('high', 'medium', 'low')
    """
    if category not in ALLOWED_CATEGORIES:
        category = "general_problem"
    if important_details is None:
        important_details = []

    return {
        "status": "success",
        "category": category,
        "title": title.strip(),
        "problem": problem.strip(),
        "important_details": [str(d).strip() for d in important_details if str(d).strip()],
        "confidence": confidence if confidence in {"high", "medium", "low"} else "medium",
    }
