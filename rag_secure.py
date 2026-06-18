"""
PHASE 3 — SECURE RAG (Remediated)
Access-aware retrieval: documents are filtered BEFORE the LLM sees them.
Controls implemented:
  1. Pre-retrieval clearance filtering — only cleared docs enter the context
  2. Sensitivity-aware redaction — partial masking on boundary-level docs
  3. Refusal logic — hard block when no cleared docs are found
  4. Audit log — every query, result, and decision is logged
"""

import chromadb
from sentence_transformers import SentenceTransformer
import ollama
import json
import os
from datetime import datetime
from documents import DOCUMENTS, USERS, CLEARANCE_LEVELS, user_can_access

# ── Setup ──────────────────────────────────────────────────────────────────────

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()
collection = client.get_or_create_collection("docs_secure")

AUDIT_LOG_FILE = "audit_log.jsonl"

def build_index():
    collection.add(
        ids=[doc["id"] for doc in DOCUMENTS],
        documents=[doc["content"] for doc in DOCUMENTS],
        metadatas=[{
            "title": doc["title"],
            "sensitivity": doc["sensitivity"],
            "department": doc["department"],
            "doc_id": doc["id"]
        } for doc in DOCUMENTS]
    )
    print(f"[INDEX] {len(DOCUMENTS)} documents indexed\n")

# ── Audit logging ──────────────────────────────────────────────────────────────

def write_audit_log(entry: dict):
    with open(AUDIT_LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# ── Redaction ──────────────────────────────────────────────────────────────────

def redact(text: str, doc_sensitivity: str, user_clearance: str) -> str:
    """
    If user is exactly at the boundary (same level), apply light redaction
    to mask the most sensitive tokens (numbers, IDs, tokens).
    """
    import re
    user_level = CLEARANCE_LEVELS[user_clearance]
    doc_level  = CLEARANCE_LEVELS[doc_sensitivity]

    # Full access — no redaction needed
    if user_level > doc_level:
        return text

    # Boundary access — redact numbers, tokens, IDs
    text = re.sub(r'\$[\d,]+', '[AMOUNT REDACTED]', text)
    text = re.sub(r'\b[A-Z]{2,}-[A-Z0-9\-]+\b', '[ID REDACTED]', text)
    text = re.sub(r'\b\d{4,}\b', '[NUMBER REDACTED]', text)
    text = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL REDACTED]', text)
    return text

# ── Secure RAG query ───────────────────────────────────────────────────────────

def query_secure(username: str, question: str):
    user = USERS.get(username)
    if not user:
        print(f"Unknown user: {username}")
        return

    timestamp = datetime.utcnow().isoformat()

    print("=" * 60)
    print(f"USER     : {user['name']}")
    print(f"CLEARANCE: {user['clearance']}")
    print(f"QUERY    : {question}")
    print("=" * 60)

    # Step 1 — Retrieve top 5 candidates from vector store
    results = collection.query(
        query_texts=[question],
        n_results=5
    )

    # Step 2 — Pre-retrieval clearance filtering
    cleared_docs = []
    blocked_docs = []

    for doc_text, metadata in zip(results["documents"][0], results["metadatas"][0]):
        if user_can_access(user["clearance"], metadata["sensitivity"]):
            cleared_docs.append((doc_text, metadata))
        else:
            blocked_docs.append(metadata)

    # Step 3 — Log blocked documents
    print(f"\n[ACCESS CONTROL]")
    if blocked_docs:
        for m in blocked_docs:
            print(f"  BLOCKED  [{m['sensitivity']}] {m['title']}")
    if cleared_docs:
        for _, m in cleared_docs:
            print(f"  ALLOWED  [{m['sensitivity']}] {m['title']}")

    # Step 4 — Refusal logic if nothing cleared
    if not cleared_docs:
        refusal_msg = (
            f"Access denied. You do not have clearance to view documents "
            f"relevant to this query. Your clearance: {user['clearance']}."
        )
        print(f"\n[REFUSAL] {refusal_msg}")

        write_audit_log({
            "timestamp": timestamp,
            "username": username,
            "clearance": user["clearance"],
            "query": question,
            "decision": "REFUSED",
            "blocked_docs": [m["title"] for m in blocked_docs],
            "cleared_docs": [],
            "response": refusal_msg
        })
        print()
        return

    # Step 5 — Apply redaction on cleared docs
    context_parts = []
    for doc_text, metadata in cleared_docs:
        redacted = redact(doc_text, metadata["sensitivity"], user["clearance"])
        context_parts.append(
            f"Title: {metadata['title']}\nSensitivity: {metadata['sensitivity']}\n{redacted}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Step 6 — Send only cleared + redacted content to LLM
    prompt = f"""You are a secure document assistant. Answer only using the provided documents.
Do not speculate beyond the documents. If the answer is not in the documents, say so.

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
        llm_answer = response["message"]["content"]
        print(llm_answer)
    except Exception as e:
        llm_answer = f"[LLM ERROR] {e}"
        print(llm_answer)

    # Step 7 — Write full audit entry
    write_audit_log({
        "timestamp": timestamp,
        "username": username,
        "clearance": user["clearance"],
        "query": question,
        "decision": "ALLOWED",
        "blocked_docs": [m["title"] for m in blocked_docs],
        "cleared_docs": [m["title"] for _, m in cleared_docs],
        "response": llm_answer
    })
    print()

# ── Demo ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Clear old audit log
    if os.path.exists(AUDIT_LOG_FILE):
        os.remove(AUDIT_LOG_FILE)

    build_index()

    print(">>> SECURE RAG DEMO — Access controls enforced\n")

    # Dave (Public) — same queries as vulnerable demo
    query_secure("dave", "What are employee salaries and payroll details?")
    query_secure("dave", "What are the admin credentials for the IT systems?")

    # Alice (Internal) — tries to access payroll
    query_secure("alice", "Show me the payroll run details for June 2026")

    # Alice — asks something she IS allowed to see
    query_secure("alice", "What is the vendor onboarding policy?")

    # Bob (Confidential) — can access financial docs
    query_secure("bob", "Summarize the Q4 2025 financial results")

    # Carol (Highly Confidential) — full access
    query_secure("carol", "What are the IT admin credentials and vault access details?")
