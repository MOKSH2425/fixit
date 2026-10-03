from typing import List, Dict, Any

ALLOWED_PRIORITIES = {"low", "medium", "high", "critical"}

def generate_action_plan(
    summary: str,
    actions: List[str],
    priority: str = "medium",
) -> Dict[str, Any]:
    """
    Tool to generate an ordered, concrete action plan addressing the identified problem.
    
    Parameters:
      summary: High-level summary of the remediation or next steps
      actions: Ordered concrete steps to solve the issue or satisfy the notice
      priority: 'low', 'medium', 'high', or 'critical'
    """
    clean_actions = [str(a).strip() for a in actions if str(a).strip()]
    if not clean_actions:
        clean_actions = ["Review the item and determine manual resolution."]

    p = priority.lower().strip()
    if p not in ALLOWED_PRIORITIES:
        p = "medium"

    return {
        "status": "success",
        "summary": summary.strip(),
        "priority": p,
        "actions": clean_actions,
    }
