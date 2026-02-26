# personal_shopper/agent.py
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search  # safer import path

root_agent = Agent(
    name="personal_shopper",
    model="gemini-2.5-flash",  # must be Gemini 2.x for google_search
    description="An AI personal shopping assistant that compares products.",
    instruction=(
        "You are a smart shopping assistant.\n"
        "When the user asks about products:\n"
        "- ALWAYS use google_search to find latest models\n"
        "- Compare at least 3 options\n"
        "- Include price range\n"
        "- Explain tradeoffs\n"
        "- Recommend one best option\n"
        "- Keep answer structured and clean\n"
    ),
    tools=[google_search],
)