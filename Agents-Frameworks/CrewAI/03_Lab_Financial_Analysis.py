from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

financial_agent = Agent(
    role="Financial Analyst",
    goal="Analyze company performance",
    backstory="Expert in financial modeling.",
    llm=llm,
    verbose=True
)

risk_agent = Agent(
    role="Risk Analyst",
    goal="Identify financial and operational risks",
    backstory="Specialist in enterprise risk.",
    llm=llm,
    verbose=True
)

summary_agent = Agent(
    role="Executive Advisor",
    goal="Summarize findings for board-level audience",
    backstory="Experienced board advisor.",
    llm=llm,
    verbose=True

)

financial_task = Task(
    description=(
        "Analyze Tesla's financial performance (revenue, profitability, cash flow, "
        "key trends) and summarize in bullet points."
    ),
    expected_output="A structured analysis with key metrics/trends and 5-10 bullet insights.",
    agent=financial_agent
)

risk_task = Task(
    description=(
        "Identify financial and operational risks based on the financial analysis. "
        "Include severity (Low/Med/High) and mitigations."
    ),
    expected_output="A risk register with 6-10 risks, severity, and mitigation actions.",
    agent=risk_agent,
    context=[financial_task]
)

summary_task = Task(
    description=(
        "Create a board-level executive summary (max 1 page) combining financial "
        "analysis and risks. Include 3 recommended actions."
    ),
    expected_output="A concise executive summary with 3 recommendations.",
    agent=summary_agent,
    context=[financial_task, risk_task]
)

crew = Crew(
    agents=[financial_agent, risk_agent, summary_agent],
    tasks=[financial_task, risk_task, summary_task],
    verbose=True
)

result = crew.kickoff()
print("\nFINAL OUTPUT:\n", result)