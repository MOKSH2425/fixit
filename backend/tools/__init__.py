from .analyze_image import analyze_image
from .action_plan import generate_action_plan
from .checklist import generate_checklist
from .task_creator import create_task

TOOLS = {
    "analyze_image": analyze_image,
    "generate_action_plan": generate_action_plan,
    "generate_checklist": generate_checklist,
    "create_task": create_task,
}

__all__ = [
    "TOOLS",
    "analyze_image",
    "generate_action_plan",
    "generate_checklist",
    "create_task",
]
