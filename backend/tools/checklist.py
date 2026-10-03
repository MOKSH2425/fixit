from typing import List, Dict, Any

def generate_checklist(
    items: List[str],
) -> Dict[str, Any]:
    """
    Tool to generate a concise, checkable verification checklist.
    
    Parameters:
      items: List of short, actionable checklist items that can be checked off
    """
    clean_items = [str(item).strip() for item in items if str(item).strip()]
    if not clean_items:
        clean_items = ["Follow up on required item"]

    return {
        "status": "success",
        "items": clean_items,
    }
