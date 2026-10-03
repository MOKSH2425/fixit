import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

logger = logging.getLogger("fixit.ai")

SYSTEM_INSTRUCTION = """You are FixIt, a multimodal AI action agent for MLH Hack Day Surat 2026.
Your purpose: "See a problem. Get an action."
Transform actionable visual information (error screenshots, campus notices, assignment instructions, warnings, documents, PDFs) into structured actions.

Core operational rules:
1. SEE & UNDERSTAND: Examine the image/document thoroughly. Identify the category, core issue/deadline, and key details.
2. TOOL USAGE:
   - Call `analyze_image` to log the classification and diagnosis.
   - Call `generate_action_plan` to provide 3 to 6 ordered, concrete remediation steps.
   - Call `generate_checklist` with concise, checkable items matching the action plan.
   - ONLY call `create_task` if the user's prompt explicitly requests creating/saving tasks (e.g., "Create tasks", "save as tasks"). If not explicitly asked, do NOT call `create_task` directly—the user will click the UI 'Create Tasks' button.
3. SAFETY: Never output or recommend harmful, arbitrary, or destructive commands (like rm -rf, drop database, format). Recommend safe, verifiable actions.
4. TONE: Professional, student-friendly, concise, and focused on solutions.
"""

def get_tool_declarations() -> types.Tool:
    """Explicit FunctionDeclarations for the registered tools to ensure strict schema adherence."""
    analyze_image_func = types.FunctionDeclaration(
        name="analyze_image",
        description="Record structured understanding and classification of the uploaded image or document.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "category": types.Schema(
                    type="STRING",
                    description="Category of the image content.",
                    enum=[
                        "technical_error",
                        "campus_notice",
                        "assignment",
                        "instructions",
                        "document",
                        "general_problem",
                        "unknown",
                    ],
                ),
                "title": types.Schema(
                    type="STRING",
                    description="Concise descriptive title of the detected problem or notice topic.",
                ),
                "problem": types.Schema(
                    type="STRING",
                    description="Detailed explanation of the root problem, notice requirement, or deadline.",
                ),
                "important_details": types.Schema(
                    type="ARRAY",
                    items=types.Schema(type="STRING"),
                    description="List of key entities, dates, module names, course codes, or line numbers.",
                ),
                "confidence": types.Schema(
                    type="STRING",
                    description="Qualitative assessment of diagnosis certainty.",
                    enum=["high", "medium", "low"],
                ),
            },
            required=["category", "title", "problem"],
        ),
    )

    action_plan_func = types.FunctionDeclaration(
        name="generate_action_plan",
        description="Generate an ordered, concrete action plan addressing the identified problem or notice.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "summary": types.Schema(
                    type="STRING",
                    description="High-level overview of the remediation approach.",
                ),
                "priority": types.Schema(
                    type="STRING",
                    description="Urgency level.",
                    enum=["low", "medium", "high", "critical"],
                ),
                "actions": types.Schema(
                    type="ARRAY",
                    items=types.Schema(type="STRING"),
                    description="Ordered concrete steps to solve the issue or complete the requirements.",
                ),
            },
            required=["summary", "actions"],
        ),
    )

    checklist_func = types.FunctionDeclaration(
        name="generate_checklist",
        description="Generate concise checkable items corresponding to the action plan.",
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "items": types.Schema(
                    type="ARRAY",
                    items=types.Schema(type="STRING"),
                    description="List of short, actionable checklist items that the user can tick off.",
                ),
            },
            required=["items"],
        ),
    )



    return types.Tool(
        function_declarations=[
            analyze_image_func,
            action_plan_func,
            checklist_func,
        ]
    )

class FixItModelClient:
    def __init__(self, api_key: str, model_name: str = "gemma-4-26b-a4b-it"):
        self.api_key = api_key
        self.model_name = model_name
        self.client: Optional[genai.Client] = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize genai.Client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        return bool(self.client and self.api_key)

    def create_chat(self):
        """Creates a chat session for multi-turn tool execution."""
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured or invalid.")

        tools = [get_tool_declarations()]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            temperature=0.2,
        )
        return self.client.chats.create(model=self.model_name, config=config)

    def generate_with_tools(
        self,
        file_bytes: bytes,
        mime_type: str,
        user_message: Optional[str] = None,
    ):
        """
        Sends multimodal input (file + optional prompt) to Gemma 4 with tool declarations.
        Returns the raw model response containing text or function calls.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured or invalid.")

        contents: List[Any] = [
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
        ]
        
        prompt_text = (user_message or "").strip()
        if prompt_text:
            contents.append(prompt_text)
        else:
            contents.append("Analyze this file, diagnose any problem or actionable requirement, and generate an action plan and checklist.")

        tools = [get_tool_declarations()]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            temperature=0.2,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )
        return response

    def send_tool_results(
        self,
        previous_contents: List[Any],
        tool_responses: List[Dict[str, Any]],
    ):
        """
        Feeds the tool execution results back to Gemma 4 to produce the final user-friendly response.
        """
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is not configured or invalid.")

        # Create function response parts
        response_parts = []
        for tr in tool_responses:
            fn_name = tr["name"]
            fn_result = tr["result"]
            response_parts.append(
                types.Part.from_function_response(
                    name=fn_name,
                    response={"result": fn_result},
                )
            )

        updated_contents = list(previous_contents)
        updated_contents.append(response_parts)

        tools = [get_tool_declarations()]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            temperature=0.2,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        final_resp = self.client.models.generate_content(
            model=self.model_name,
            contents=updated_contents,
            config=config,
        )
        return final_resp

