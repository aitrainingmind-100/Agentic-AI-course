# pip install -U langfuse qdrant-client langchain-qdrant langchain-community langchain-core langchain-text-splitters langchain-huggingface pypdf

import uuid
import atexit

from langfuse import Langfuse

from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore


# ---------------- LANGFUSE ----------------
langfuse = Langfuse(
    public_key="pk-lf-cc811091-134d-43ad-8896-daeff598e766",
    secret_key="sk-lf-33687798-2af5-49b3-9a09-2ad74d454999",
    host="https://us.cloud.langfuse.com",
)

# Make sure we flush when the script exits
atexit.register(lambda: langfuse.flush())


# ---------------- LLM ----------------
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-30B-A3B",
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03,
)
chat = ChatHuggingFace(llm=llm, verbose=True)

# ---------------- EMBEDDINGS ----------------
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
EMBED_DIM = 384

# ---------------- QDRANT ----------------
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "embd_store_1"

qdrant_client = QdrantClient(url=QDRANT_URL)
existing = [c.name for c in qdrant_client.get_collections().collections]
if COLLECTION_NAME not in existing:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embedding=embedding_function,
)

# ---------------- PROMPTS ----------------
store_prompt_template = PromptTemplate(input_variables=["text"], template="{text}")
search_prompt_template = PromptTemplate(
    input_variables=["query"],
    template="Find relevant information related to: {query}",
)

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(pdf_path: str) -> str:
    t = langfuse.trace(name="extract_text_from_pdf", input={"pdf_path": pdf_path})
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        text = "\n".join(doc.page_content for doc in docs)
        t.output = {"num_pages": len(docs)}
        return text
    except Exception as e:
        t.output = {"error": str(e)}
        raise
    finally:
        t.finalize()


def split_text_into_chunks(text: str, chunk_size: int = 1000):
    t = langfuse.trace(name="split_text_into_chunks", input={"chunk_size": chunk_size})
    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=10)
        chunks = splitter.split_text(text)
        t.output = {"num_chunks": len(chunks)}
        return chunks
    finally:
        t.finalize()


def insert_text_from_pdf():
    pdf_path = input("Enter path to PDF file: ").strip()
    t = langfuse.trace(name="insert_text_from_pdf", input={"pdf_path": pdf_path})
    try:
        extracted_text = extract_text_from_pdf(pdf_path)
        chunks = split_text_into_chunks(extracted_text)

        texts, metadatas, ids = [], [], []
        for i, chunk in enumerate(chunks):
            texts.append(store_prompt_template.format(text=chunk))
            metadatas.append({"source": pdf_path, "chunk_index": i})
            ids.append(str(uuid.uuid4()))

        vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        t.output = {"chunks_stored": len(chunks)}
        print(f"Stored {len(chunks)} chunks into Qdrant collection: {COLLECTION_NAME}")

    finally:
        t.finalize()
        langfuse.flush()  # <-- important for CLI scripts


def fetch_matching_text():
    query_text = input("Enter search query: ").strip()
    t = langfuse.trace(name="fetch_matching_text", input={"query": query_text})
    try:
        formatted_query = search_prompt_template.format(query=query_text)
        results = vector_store.similarity_search(formatted_query, k=5)

        if results:
            top = results[0]
            t.output = {"found": True, "top_metadata": top.metadata}
            print("\nTop Match Metadata:", top.metadata)
            print("\nTop Match Text:\n", top.page_content)
            return top.page_content

        t.output = {"found": False}
        print("No matching results found.")
        return None

    finally:
        t.finalize()
        langfuse.flush()


def chat_with_ai():
    relevant_text = fetch_matching_text()
    if not relevant_text:
        return

    user_question = input("\nEnter your question about the retrieved text: ").strip()
    combined_prompt = (
        user_question
        + "\n\nAnswer strictly within the relevant context.\nContext:\n"
        + relevant_text
    )

    t = langfuse.trace(name="chat_with_ai", input={"question": user_question})
    try:
        ai_msg = chat.invoke(combined_prompt)
        response_text = (ai_msg.content or "").split("</think>", 1)[-1].strip()
        t.output = {"response_preview": response_text[:300]}
        print(f"\nLLM Response:\n{response_text}")
    finally:
        t.finalize()
        langfuse.flush()


# ---------------- MENU ----------------
while True:
    choice = input(
        "\nChoose an action:\n"
        "1. Insert Text from PDF (Qdrant)\n"
        "2. Fetch & Interact with AI\n"
        "3. Exit\n"
        "Enter choice: "
    ).strip()

    if choice == "1":
        insert_text_from_pdf()
    elif choice == "2":
        chat_with_ai()
    elif choice == "3":
        langfuse.flush()
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")