import os
import tempfile
from uuid import uuid4

import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter  # ✅ FIXED IMPORT
from langchain_core.prompts import PromptTemplate

from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import (
    HuggingFaceEmbeddings,
    HuggingFaceEndpoint,
    ChatHuggingFace,
)

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
COLLECTION_NAME = "rag_demo"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 384 dims

st.set_page_config(page_title="PDF RAG – Qdrant + Qwen", layout="wide")
st.title("📄 PDF RAG Demo (Qdrant + Qwen – Conversational)")


# --------------------------------------------------
# Qdrant setup
# --------------------------------------------------
client = QdrantClient(url=QDRANT_URL)

# Embeddings (init early so we can auto-detect vector size reliably)
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
VECTOR_SIZE = len(embeddings.embed_query("dimension check"))  # ✅ avoids mismatch

existing = {c.name for c in client.get_collections().collections}
if COLLECTION_NAME not in existing:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)


# --------------------------------------------------
# LLM (Qwen – CHAT)
# --------------------------------------------------
# NOTE: Some HF endpoints reject params like do_sample/repetition_penalty.
# Keep minimal unless you have a dedicated endpoint.
hf_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-30B-A3B",
    max_new_tokens=512,
    huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
)

chat_llm = ChatHuggingFace(llm=hf_endpoint, verbose=False)


# --------------------------------------------------
# Prompt
# --------------------------------------------------
rag_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "Answer the question using ONLY the context below.\n"
        "If the answer is not present, say \"I don't know\".\n\n"
        "Context:\n{context}\n\n"
        "Question:\n{question}\n\n"
        "Answer:\n"
    ),
)


# --------------------------------------------------
# Sidebar – PDF Upload
# --------------------------------------------------
st.sidebar.header("📥 Upload PDF")
uploaded_file = st.sidebar.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name

    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # Keep metadata for traceability
    for d in docs:
        d.metadata = d.metadata or {}
        d.metadata["source"] = uploaded_file.name

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    with st.spinner("Indexing PDF into Qdrant..."):
        # Prefer add_documents to preserve metadata in Qdrant payload
        vector_store.add_documents(
            documents=chunks,
            ids=[str(uuid4()) for _ in chunks],
        )

    os.remove(pdf_path)
    st.sidebar.success(f"Indexed {len(chunks)} chunks into Qdrant")


# --------------------------------------------------
# Main Chat UI
# --------------------------------------------------
st.subheader("💬 Ask questions about your documents")

question = st.text_input("Enter your question")

if st.button("Ask") and question:
    with st.spinner("Retrieving relevant context..."):
        docs = vector_store.similarity_search(question, k=5)

    if not docs:
        st.warning("No relevant context found.")
    else:
        # Include page/source in context for better grounding
        context_parts = []
        for d in docs:
            src = d.metadata.get("source", "unknown")
            page = d.metadata.get("page", "n/a")
            context_parts.append(f"[source={src} page={page}]\n{d.page_content}")

        context = "\n\n---\n\n".join(context_parts)

        prompt = rag_prompt.format(context=context, question=question)

        with st.spinner("Generating answer..."):
            response = chat_llm.invoke(prompt)

        st.markdown("### 🤖 Answer")
        st.write(response.content)

        with st.expander("🔎 Retrieved Context"):
            st.write(context)