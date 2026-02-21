from dotenv import load_dotenv
import os

load_dotenv()

import os
import streamlit as st
import pandas as pd
import psycopg2
from openai import OpenAI
import ollama

# ---------------- CONFIG ----------------
DB_HOST = "localhost"
DB_NAME = "mydb"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"

# Prefer secrets/env over hardcoding
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


# ---------------- DATABASE FUNCTION ----------------
def run_query(sql: str) -> pd.DataFrame:
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    try:
        df = pd.read_sql(sql, conn)
        return df
    finally:
        conn.close()


# ---------------- LLM SUMMARY FUNCTION ----------------
def summarize_with_llm(table_text: str, use_ollama: bool = False) -> str:
    prompt = f"""
You are a professional data analyst. Explain the following SQL result table
in clear natural language with insights, trends, and summaries.

Table:
{table_text}

Include:
- What the data represents
- Key insights
- Notable values
- Trends or patterns
"""

    # ---- Option 1: Use Local Llama (Ollama) ----
    if use_ollama:
        result = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return (result.get("message", {}) or {}).get("content", "").strip() or "No insights returned from Ollama."

    # ---- Option 2: Use OpenAI ----
    if client is None:
        return "OpenAI API key not configured. Set OPENAI_API_KEY in Streamlit secrets or environment."

    # Using the OpenAI SDK chat completions style:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )

    text = (resp.choices[0].message.content or "").strip()
    return text or "No insights returned from OpenAI."


# -----------------------------------------------------
# ---------------- STREAMLIT DASHBOARD ----------------
# -----------------------------------------------------
st.set_page_config(page_title="Postgres Data Insights", layout="wide")
st.write("Query your database and get insights powered by an LLM.")

st.sidebar.header("Database Query")
default_sql = """
SELECT id, username, email, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
"""
sql_input = st.sidebar.text_area("SQL Query", default_sql, height=150)
use_ollama = st.sidebar.checkbox("Use Local Llama (Ollama)", value=False)
run_button = st.sidebar.button("Run Analysis")

if run_button:
    st.subheader("SQL Query")
    st.code(sql_input, language="sql")

    try:
        df = run_query(sql_input)
        st.subheader("Raw Table Data")
        st.dataframe(df, use_container_width=True)

        if df.empty:
            st.warning("Query returned no rows.")
            st.stop()

        table_text = df.to_string(index=False)

        st.subheader("LLM Insights")
        with st.spinner("Analyzing data using LLM..."):
            insights = summarize_with_llm(table_text, use_ollama)

        # Ensure string (never None)
        insights = insights or "No insights generated."
        st.write(insights)

        st.subheader("Download Options")
        st.download_button("Download CSV", df.to_csv(index=False), "data.csv", "text/csv")
        st.download_button("Download Insights", insights, "insights.txt", "text/plain")

    except Exception as e:
        st.error(f"Error: {e}")