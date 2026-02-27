from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

ceo = Agent(
    role="CEO",
    goal="Drive growth strategy and make an investment recommendation",
    backstory="Exec leader focused on strategy and market positioning.",
    llm=llm,
    verbose=True
)

cto = Agent(
    role="CTO",
    goal="Evaluate technology feasibility and delivery approach",
    backstory="Exec technologist focused on architecture, build vs buy, and scaling.",
    llm=llm,
    verbose=True
)

cfo = Agent(
    role="CFO",
    goal="Analyze financial viability, ROI, and funding allocation",
    backstory="Finance leader focused on ROI, run-rate, and capital efficiency.",
    llm=llm,
    verbose=True
)

risk = Agent(
    role="Chief Risk Officer",
    goal="Identify compliance, security, privacy, and operational risks",
    backstory="Risk leader focused on governance, controls, and regulatory exposure.",
    llm=llm,
    verbose=True
)

# Task 1: CEO recommendation
ceo_task = Task(
    description="Should we invest $10M into building an AI platform? Provide a crisp recommendation and rationale.",
    expected_output="A recommendation (Yes/No/Conditional) with 5-8 bullets and success criteria.",
    agent=ceo
)

# Task 2: CTO feasibility (uses CEO recommendation)
cto_task = Task(
    description="Evaluate tech feasibility: architecture, timeline, team, build vs buy, risks, and dependencies.",
    expected_output="A feasibility assessment with proposed architecture and phased delivery plan (90 days / 6 months / 12 months).",
    agent=cto,
    context=[ceo_task]
)

# Task 3: CFO financial view (uses CEO + CTO)
cfo_task = Task(
    description="Analyze financial impact: cost breakdown, ROI assumptions, payback period, and KPIs to track.",
    expected_output="A financial view with rough budget allocation, ROI model assumptions, and a go/no-go metric set.",
    agent=cfo,
    context=[ceo_task, cto_task]
)

# Task 4: CRO risk assessment (uses all prior)
risk_task = Task(
    description="Identify risks: regulatory/compliance, security, privacy, model risk, operational and reputational risks. Include mitigations.",
    expected_output="A risk register with severity and mitigations; include top 5 must-have controls.",
    agent=risk,
    context=[ceo_task, cto_task, cfo_task]
)

crew = Crew(
    agents=[ceo, cto, cfo, risk],
    tasks=[ceo_task, cto_task, cfo_task, risk_task],
    verbose=True
)

result = crew.kickoff()
print("\nFINAL OUTPUT:\n", result)