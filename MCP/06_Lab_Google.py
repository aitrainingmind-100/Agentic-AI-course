# app.py  (Streamlit + LangChain (new API) + Google hosted Maps MCP server)
import os
import asyncio
import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


def run_async(coro):
    """Run async code from Streamlit reliably."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def build_agent():
    """Connect to Google's hosted MCP server and build an agent (no AgentExecutor needed)."""
    load_dotenv()

    google_key = os.getenv("GOOGLE_MAPS_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not google_key:
        raise RuntimeError("Missing GOOGLE_MAPS_API_KEY in .env")
    if not openai_key:
        raise RuntimeError("Missing OPENAI_API_KEY in .env")

    # Google hosted MCP (Maps Grounding Lite)
    mcp_client = MultiServerMCPClient(
        {
            "google_maps": {
                "transport": "streamable_http",
                "url": "https://mapstools.googleapis.com/mcp",
                "headers": {"X-Goog-Api-Key": google_key},
            }
        }
    )

    tools = await mcp_client.get_tools()
    tool_names = [t.name for t in tools]

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are a helpful local assistant.\n"
            "Use tools when needed (places, routes, weather).\n"
            "When listing places: show name, address, rating if available, and a Google Maps link.\n"
            "Keep answers concise."
        ),
    )

    return agent, tool_names


async def agent_reply(agent, chat_history, user_text: str) -> str:
    """Invoke the agent using the new messages-based API."""
    messages = chat_history + [HumanMessage(content=user_text)]
    result = await agent.ainvoke({"messages": messages})
    # create_agent returns a messages dict; last message is the assistant response
    return result["messages"][-1].content


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Google Maps MCP Chat", page_icon="🗺️", layout="centered")
st.title("🗺️ Google Maps MCP Chat (Streamlit)")
st.caption("LangChain (new agent API) + tool-calling LLM + Google hosted Maps MCP server")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []  # list[dict]: {role, content}
if "lc_history" not in st.session_state:
    st.session_state.lc_history = []  # list[HumanMessage|AIMessage]
if "agent" not in st.session_state:
    st.session_state.agent = None
if "tool_names" not in st.session_state:
    st.session_state.tool_names = None
if "init_error" not in st.session_state:
    st.session_state.init_error = None

# Sidebar
with st.sidebar:
    st.header("Controls")

    if st.button("🔌 Connect / Reconnect", use_container_width=True):
        st.session_state.init_error = None
        try:
            agent, tool_names = run_async(build_agent())
            st.session_state.agent = agent
            st.session_state.tool_names = tool_names
            st.success("Connected to Google Maps MCP ✅")
        except Exception as e:
            st.session_state.agent = None
            st.session_state.tool_names = None
            st.session_state.init_error = str(e)
            st.error(f"Failed to connect: {e}")

    if st.button("🧹 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.lc_history = []
        st.rerun()

    if st.session_state.tool_names:
        with st.expander("Available MCP tools"):
            for name in st.session_state.tool_names:
                st.write(f"- `{name}`")

    st.markdown("---")
    st.markdown(
        "Examples:\n"
        "- coffee shops near Downtown Minneapolis\n"
        "- find vegetarian restaurants near 55401\n"
        "- route from Minneapolis to Saint Paul\n"
        "- weather near Mall of America tomorrow morning"
    )

# Auto-connect once
if st.session_state.agent is None and st.session_state.init_error is None:
    try:
        agent, tool_names = run_async(build_agent())
        st.session_state.agent = agent
        st.session_state.tool_names = tool_names
    except Exception as e:
        st.session_state.init_error = str(e)

if st.session_state.init_error:
    st.warning(st.session_state.init_error)

# Render chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat input
user_text = st.chat_input("Ask about places, routes, or weather…")

if user_text:
    if st.session_state.agent is None:
        st.error("Not connected. Click **Connect / Reconnect** in the sidebar.")
        st.stop()

    # User message
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.session_state.lc_history.append(HumanMessage(content=user_text))
    with st.chat_message("user"):
        st.markdown(user_text)

    # Assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking + calling tools…"):
            try:
                reply = run_async(agent_reply(st.session_state.agent, st.session_state.lc_history[:-1], user_text))
            except Exception as e:
                reply = f"⚠️ Error: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.lc_history.append(AIMessage(content=reply))