import logging
from typing import Dict, Any, List, Optional
from config import GEMINI_API_KEY, GEMMA_MODEL
from ai.model_client import FixItModelClient
from tools import TOOLS
from schemas import AgentResponse, TaskResponse
from google.genai import types

import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger("fixit.agent")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}

class FixItAgent:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        # Dynamically reload environment in case user updated backend/.env
        dotenv_path = Path(__file__).resolve().parent / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path, override=True)

        self.api_key = (api_key or os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY or "").strip()
        self.model_name = (model_name or os.getenv("GEMMA_MODEL") or GEMMA_MODEL or "gemma-4-26b-a4b-it").strip()
        self.client = FixItModelClient(api_key=self.api_key, model_name=self.model_name)

    def validate_image(self, image_bytes: bytes, content_type: str) -> Optional[str]:
        """Validate uploaded image format and size."""
        if not image_bytes:
            return "Please upload an image first."
        if len(image_bytes) > MAX_FILE_SIZE:
            return f"Image file is too large (maximum allowed is {MAX_FILE_SIZE // (1024 * 1024)}MB)."
        clean_mime = (content_type or "").lower().split(";")[0].strip()
        if clean_mime not in ALLOWED_MIME_TYPES:
            return "Please upload a PNG, JPG, JPEG, or WEBP image."
        return None

    def process(self, image_bytes: bytes, content_type: str, user_message: Optional[str] = None) -> AgentResponse:
        """
        Core multimodal agent execution loop:
        SEE -> UNDERSTAND -> DECIDE -> ACT
        """
        # Step 1: Validate image
        val_error = self.validate_image(image_bytes, content_type)
        if val_error:
            return AgentResponse(
                success=False,
                error=val_error,
                final_response=val_error,
            )

        # Step 2: Check API Key configuration
        if not self.client.is_configured():
            return AgentResponse(
                success=False,
                error="FixIt could not process this image right now. Check the AI configuration and try again.",
                final_response="FixIt could not process this image right now. Check the AI configuration and try again. Please ensure GEMINI_API_KEY is configured in backend/.env.",
            )

        activity: List[str] = []
        category = "unknown"
        title = ""
        problem = ""
        actions: List[str] = []
        checklist: List[str] = []
        created_tasks: List[TaskResponse] = []
        final_text = ""

        try:
            # Step 3: Send image + prompt to model
            response = self.client.generate_with_tools(
                image_bytes=image_bytes,
                mime_type=content_type,
                user_message=user_message,
            )

            # Check for function calls
            function_calls = getattr(response, "function_calls", None) or []
            tool_executions: List[Dict[str, Any]] = []

            # Execute model-requested tools via Tool Registry
            if function_calls:
                for fc in function_calls:
                    fn_name = getattr(fc, "name", "")
                    fn_args = getattr(fc, "args", {}) or {}

                    if fn_name not in TOOLS:
                        logger.warning(f"Model attempted to call unknown tool: {fn_name}")
                        continue

                    # Execute verified tool
                    tool_fn = TOOLS[fn_name]
                    try:
                        res = tool_fn(**fn_args)
                    except TypeError as te:
                        logger.error(f"Invalid args for {fn_name}: {te}")
                        res = {"status": "error", "message": f"Malformed arguments: {te}"}
                    except Exception as e:
                        logger.error(f"Error running tool {fn_name}: {e}")
                        res = {"status": "error", "message": str(e)}

                    tool_executions.append({"name": fn_name, "result": res})

                    # Map to response state and observable activity
                    if fn_name == "analyze_image":
                        category = res.get("category", "unknown")
                        title = res.get("title", "")
                        problem = res.get("problem", "")
                        if "✓ Image understood" not in activity:
                            activity.append("✓ Image understood")
                        if "✓ Problem identified" not in activity:
                            activity.append("✓ Problem identified")

                    elif fn_name == "generate_action_plan":
                        actions = res.get("actions", [])
                        if "✓ Action plan generated" not in activity:
                            activity.append("✓ Action plan generated")

                    elif fn_name == "generate_checklist":
                        checklist = res.get("items", [])
                        if "✓ Checklist generated" not in activity:
                            activity.append("✓ Checklist generated")

                    elif fn_name == "create_task":
                        if res.get("status") == "success":
                            task_dict = {
                                "id": res.get("task_id"),
                                "title": res.get("title"),
                                "description": fn_args.get("description"),
                                "category": res.get("category", "Other"),
                                "deadline": res.get("deadline"),
                                "completed": res.get("completed", False),
                                "created_at": res.get("created_at", ""),
                            }
                            created_tasks.append(TaskResponse.from_row(task_dict))
                            if "✓ Task created" not in activity:
                                activity.append("✓ Task created")

                # Obtain final conversational response by passing results back
                try:
                    contents_hist = [
                        types.Part.from_bytes(data=image_bytes, mime_type=content_type),
                        (user_message or "Analyze this image and provide actionable steps.").strip(),
                    ]
                    final_call_resp = self.client.send_tool_results(contents_hist, tool_executions)
                    final_text = getattr(final_call_resp, "text", "") or ""
                except Exception as ex:
                    logger.warning(f"Could not get follow-up final text: {ex}")
                    final_text = f"FixIt identified: {title}. {problem}"

            else:
                # Direct text response without tool call
                final_text = getattr(response, "text", "") or ""
                title = "Analysis Result"
                problem = final_text[:200] if len(final_text) > 200 else final_text
                activity.append("✓ Image understood")

            # Fallback checklist if action plan exists but checklist tool wasn't called
            if actions and not checklist:
                checklist = [a.split(". ")[-1] for a in actions]
                activity.append("✓ Checklist generated")

            return AgentResponse(
                success=True,
                category=category,
                title=title or "Analysis Complete",
                problem=problem,
                actions=actions,
                checklist=checklist,
                created_tasks=created_tasks,
                agent_activity=activity,
                final_response=final_text.strip() or f"Action plan generated for: {title}",
            )

        except Exception as e:
            logger.exception("Agent processing failed")
            err_msg = str(e)
            if "API_KEY_INVALID" in err_msg or "401" in err_msg or "403" in err_msg or "PERMISSION_DENIED" in err_msg:
                user_friendly_err = "FixIt could not process this image right now. Check the AI configuration and try again."
            else:
                user_friendly_err = f"FixIt encountered an issue processing the request: {err_msg}"

            return AgentResponse(
                success=False,
                error=user_friendly_err,
                final_response=user_friendly_err,
            )
