from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search, tool
import google.genai.types as types

@tool
def save_budget(context, budget: str) -> dict:
    context.state["user:budget"] = budget
    return {"status": "saved", "budget": budget}

@tool
def save_comparison_artifact(context, text: str) -> dict:
    part = types.Part.from_bytes(
        data=text.encode("utf-8"),
        mime_type="text/plain"
    )
    context.artifacts.save_artifact(
        filename="comparison.txt",
        artifact=part
    )
    return {"status": "artifact_saved"}

root_agent = Agent(
    name="personal_shopper",
    model="gemini-2.5-flash",
    description="An AI personal shopping assistant that compares products.",
    instruction=(
        "You are a smart shopping assistant.\n"
        "- ALWAYS use google_search\n"
        "- Compare at least 3 options\n"
        "- Include price range\n"
        "- Recommend best one\n"
        "- Save the final comparison using save_comparison_artifact\n"
    ),
    tools=[google_search, save_budget, save_comparison_artifact],
)