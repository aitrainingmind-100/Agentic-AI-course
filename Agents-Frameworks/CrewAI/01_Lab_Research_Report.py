from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate information on a topic",
    backstory="Expert in deep research and summarization.",
    llm=llm,
    verbose=True
)

writer = Agent(
    role="Technical Writer",
    goal="Write structured professional reports",
    backstory="Expert in business communication.",
    llm=llm,
    verbose=True
)

research_task = Task(
    description="Research latest trends in Agentic AI.",
    expected_output="A detailed list of key trends with explanations.",
    agent=researcher
)

write_task = Task(
    description="Write a structured 5-section report based on research findings.",
    expected_output="A professional report with headings and clear sections.",
    agent=writer,
     context=[research_task] 
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task,write_task],
    verbose=True
)

result = crew.kickoff()
print("\nFinal Output:\n", result)