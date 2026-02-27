# 06_Lab_React_Pattern_Showcase.py
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
ddg = DuckDuckGoSearchRun()

# ----------------------------
# CrewAI Tools (BaseTool subclasses)
# ----------------------------
class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for recent info using DuckDuckGo."

    def _run(self, query: str) -> str:
        print(f"\n[ACT] web_search(query={query!r})")
        result = ddg.run(query)
        print(f"[OBSERVE] web_search result preview: {result[:250]}\n")
        return result


class WordCountTool(BaseTool):
    name: str = "word_count"
    description: str = "Count words in a given text."

    def _run(self, text: str) -> str:
        print(f"\n[ACT] word_count(text_preview={text[:80]!r})")
        count = len([w for w in text.split() if w])
        print(f"[OBSERVE] word_count={count}\n")
        return str(count)


tools = [WebSearchTool(), WordCountTool()]

agent = Agent(
    role="ReAct Trace Agent",
    goal="Demonstrate Think→Act→Observe→Reflect→Repeat→Answer with tool usage.",
    backstory=(
        "You show short THINK/OBSERVE/REFLECT lines. "
        "You MUST call web_search at least once and MUST call word_count on your final answer."
    ),
    llm=llm,
    tools=tools,          # ✅ BaseTool instances
    verbose=True,
)

task = Task(
    description="""
Follow this visible loop at least twice:

1) THINK: short plan (1-3 lines)
2) ACT: call a tool when needed
3) OBSERVE: summarize tool output (1-3 lines)
4) REFLECT: decide next step (1-3 lines)
5) REPEAT steps 1-4 at least once
6) ANSWER: final answer

Question: Find 2 recent trends in Agentic AI and then count the words in your final answer.

Hard requirements:
- You MUST call web_search at least once to identify trends.
- You MUST call word_count on your final answer text.
""",
    expected_output="A response with 2 iterations of the loop and a final answer + word count.",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)
result = crew.kickoff()
print("\nFINAL OUTPUT:\n", result)