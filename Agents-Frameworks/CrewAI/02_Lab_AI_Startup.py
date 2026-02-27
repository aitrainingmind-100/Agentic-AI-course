from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

idea_agent = Agent(
    role="Startup Idea Generator",
    goal="Generate innovative AI startup ideas",
    backstory="Creative technologist.",
    llm=llm,
    verbose=True
)

critic_agent = Agent(
    role="Venture Capital Critic",
    goal="Evaluate feasibility and risks",
    backstory="Experienced VC partner.",
    llm=llm,
    verbose=True
)

refiner_agent = Agent(
    role="Product Strategist",
    goal="Refine idea into business model canvas",
    backstory="Strategic product expert.",
    llm=llm,
    verbose=True
)

# Task 1 — Idea generation
idea_task = Task(
    description="Generate one innovative AI startup idea in 3-5 sentences.",
    expected_output="A clearly defined AI startup idea with target market and core value proposition.",
    agent=idea_agent
)

# Task 2 — Critique (uses idea output)
critic_task = Task(
    description="Critically evaluate the startup idea. Analyze risks, competition, feasibility, and revenue potential.",
    expected_output="A structured evaluation with strengths, weaknesses, risks, and investment viability score.",
    agent=critic_agent,
    context=[idea_task]
)

# Task 3 — Refine (uses idea + critique)
refine_task = Task(
    description="Refine the startup idea into a structured Business Model Canvas.",
    expected_output="""A business model canvas including:
- Customer Segments
- Value Proposition
- Revenue Streams
- Key Activities
- Key Resources
- Channels
- Cost Structure
- Key Partnerships""",
    agent=refiner_agent,
    context=[idea_task, critic_task]
)

crew = Crew(
    agents=[idea_agent, critic_agent, refiner_agent],
    tasks=[idea_task, critic_task, refine_task],
    verbose=True
)

result = crew.kickoff()
print("\nFINAL OUTPUT:\n", result)