from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

engineer = Agent(
    role="Software Engineer",
    goal="Write production-ready Python code",
    backstory="Expert full-stack developer.",
    llm=llm,
    verbose=True
)

reviewer = Agent(
    role="Senior Code Reviewer",
    goal="Review and improve code quality",
    backstory="Strict reviewer with security mindset.",
    llm=llm,
    verbose=True
)

build_task = Task(
    description=(
        "Build a FastAPI endpoint for an AI chatbot. "
        "Requirements: POST /chat accepts {message: str}, returns {reply: str}. "
        "Include input validation, error handling, and a simple in-memory conversation store keyed by session_id header."
    ),
    expected_output="A complete FastAPI code snippet (single file) that can run locally.",
    agent=engineer
)

review_task = Task(
    description=(
        "Review the code for correctness, security, and maintainability. "
        "Suggest improvements and provide a revised version of the code."
    ),
    expected_output="A review section (bullets) + an improved revised FastAPI code snippet.",
    agent=reviewer,
    context=[build_task]  # ✅ reviewer gets engineer output
)

crew = Crew(
    agents=[engineer, reviewer],
    tasks=[build_task, review_task],
    verbose=True
)

result = crew.kickoff()
print("\nFINAL OUTPUT:\n", result)