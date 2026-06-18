"""
PHASE 2 — VULNERABLE RAG (Baseline)
No access controls. Any user can retrieve and summarize any document
regardless of their clearance level. Reproduces LLM06: Sensitive Information Disclosure.
"""

import chromadb
from sentence_transformers import SentenceTransformer
import ollama
from documents import DOCUMENTS, USERS

# ── Setup ──────────────────────────────────────────────────────────────────────

# Load embedding model (runs locally)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Local ChromaDB (stores data in memory for this demo)
client = chromadb.Client()
collection = client.get_or_create_collection("docs_vulnerable")

# Index ALL documents with NO sensitivity filtering
def build_index():
    collection.add(
        ids=[doc["id"] for doc in DOCUMENTS],
        documents=[doc["content"] for doc in DOCUMENTS],
        metadatas=[{
            "title": doc["title"],
            "sensitivity": doc["sensitivity"],
            "department": doc["department"]
        } for doc in DOCUMENTS]
    )
    print(f"[INDEX] {len(DOCUMENTS)} documents indexed (no access controls)\n")

# ── Vulnerable RAG query ───────────────────────────────────────────────────────

def query_vulnerable(username: str, question: str):
    user = USERS.get(username)
    if not user:
        print(f"Unknown user: {username}")
        return

    print("=" * 60)
    print(f"USER    : {user['name']}")
    print(f"CLEARANCE: {user['clearance']}")
    print(f"QUERY   : {question}")
    print("=" * 60)

    # Retrieve top 3 relevant documents — NO clearance check
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    retrieved_docs = []
    print("\n[RETRIEVED DOCUMENTS — no filtering]")
    for i, (doc_text, metadata) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0]
    )):
        print(f"  {i+1}. [{metadata['sensitivity']}] {metadata['title']}")
        retrieved_docs.append(f"Title: {metadata['title']}\nSensitivity: {metadata['sensitivity']}\n{doc_text}")

    # Send everything to LLM with no restrictions
    context = "\n\n---\n\n".join(retrieved_docs)
    prompt = f"""You are a helpful document assistant. Answer the user's question using the documents provided.

Documents:
{context}

Question: {question}

Answer:"""

    print("\n[LLM RESPONSE]")
    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[{"role": "user", "content": prompt}]
        )
        print(response["message"]["content"])
    except Exception as e:
        print(f"[LLM ERROR] {e}")
    print()

# ── Demo ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    build_index()

    print(">>> VULNERABLE RAG DEMO — No access controls\n")

    # Dave is an external contractor (Public clearance only)
    # He should NOT be able to see payroll or credentials — but he can
    query_vulnerable("dave", "What are employee salaries and payroll details?")
    query_vulnerable("dave", "What are the admin credentials for the IT systems?")

    # Alice is an HR Coordinator (Internal clearance)
    # She should NOT see Highly Confidential docs — but she can
    query_vulnerable("alice", "Show me the payroll run details for June 2026")
