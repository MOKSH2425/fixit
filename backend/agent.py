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

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "application/pdf"}

class FixItAgent:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        # Dynamically reload environment in case user updated backend/.env
        dotenv_path = Path(__file__).resolve().parent / ".env"
        if dotenv_path.exists():
            load_dotenv(dotenv_path, override=True)

        self.api_key = (api_key or os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY or "").strip()
        self.model_name = (model_name or os.getenv("GEMMA_MODEL") or GEMMA_MODEL or "gemma-4-26b-a4b-it").strip()
        self.client = FixItModelClient(api_key=self.api_key, model_name=self.model_name)

    def validate_file(self, file_bytes: bytes, content_type: str) -> Optional[str]:
        """Validate uploaded file format and size."""
        if not file_bytes:
            return "Please upload a file first."
        if len(file_bytes) > MAX_FILE_SIZE:
            return f"File is too large (maximum allowed is {MAX_FILE_SIZE // (1024 * 1024)}MB)."
        clean_mime = (content_type or "").lower().split(";")[0].strip()
        if clean_mime not in ALLOWED_MIME_TYPES:
            return "Please upload a PNG, JPG, JPEG, WEBP, or PDF document."
        return None

    def process(self, file_bytes: bytes, content_type: str, user_message: Optional[str] = None, history_json: Optional[str] = None) -> AgentResponse:
        """
        Core multimodal agent execution loop:
        SEE -> UNDERSTAND -> DECIDE -> ACT
        """
        # Step 1: Validate file
        val_error = self.validate_file(file_bytes, content_type)
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
            # Step 3: Run chat loop for up to 5 turns to execute all model-triggered tools
            chat = self.client.create_chat()

            final_prompt = user_message
            if history_json:
                final_prompt = f"Previous context: {history_json}\n\nUser follow-up request: {user_message}\n\nPlease regenerate the analysis, action plan, and checklist addressing this follow-up request."

            initial_contents = [
                types.Part.from_bytes(data=file_bytes, mime_type=content_type),
            ]
            prompt_text = (final_prompt or "").strip()
            if prompt_text:
                initial_contents.append(prompt_text)
            else:
                initial_contents.append("Analyze this file, diagnose any problem or actionable requirement, and generate an action plan and checklist.")

            activity.append("✓ File received by FixIt agent")

            response = chat.send_message(initial_contents)

            for turn in range(5):
                function_calls = getattr(response, "function_calls", None) or []
                if not function_calls:
                    resp_text = getattr(response, "text", "") or ""
                    if resp_text:
                        final_text = (final_text + " " + resp_text).strip()
                    break

                fn_response_parts = []
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

                    fn_response_parts.append(
                        types.Part.from_function_response(name=fn_name, response={"result": res})
                    )

                    # Map tool output to response state & activity
                    if fn_name == "analyze_image":
                        category = res.get("category", category)
                        title = res.get("title", title)
                        problem = res.get("problem", problem)
                        if "✓ Image understood" not in activity:
                            activity.append("✓ Image understood")
                        if "✓ Problem identified" not in activity:
                            activity.append("✓ Problem identified")

                    elif fn_name == "generate_action_plan":
                        res_actions = res.get("actions", [])
                        if res_actions:
                            actions = res_actions
                        if "✓ Action plan generated" not in activity:
                            activity.append("✓ Action plan generated")

                    elif fn_name == "generate_checklist":
                        res_items = res.get("items", [])
                        if res_items:
                            checklist = res_items
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

                # Feed execution results back into chat session
                if fn_response_parts:
                    response = chat.send_message(fn_response_parts)
                else:
                    break

            # Fallbacks if tools were not invoked by model
            if not title:
                title = "Analysis Complete"
            if not problem and final_text:
                problem = final_text[:200]
            
            if not actions and checklist:
                actions = list(checklist)

            if actions and not checklist:
                checklist = [a.split(". ")[-1] for a in actions]
                if "✓ Checklist generated" not in activity:
                    activity.append("✓ Checklist generated")

            if not actions and (problem or final_text):
                text_to_parse = final_text or problem
                raw_steps = [s.strip("- *•0123456789.") for s in text_to_parse.split("\n") if len(s.strip()) > 5]
                if raw_steps:
                    actions = raw_steps[:5]
                    checklist = list(actions)

            return AgentResponse(
                success=True,
                category=category,
                title=title or "Analysis Complete",
                problem=problem or "Visual input processed successfully.",
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
