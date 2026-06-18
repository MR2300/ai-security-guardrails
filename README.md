# RAG Guardrail Demo — AI Security Controls

A fully local Python demo that reproduces and remediates **OWASP LLM06: Sensitive Information Disclosure** in a RAG-based document assistant — no cloud account needed.

**Stack:** Python · ChromaDB · sentence-transformers · Ollama (llama3.2:1b) · fully local

**Frameworks mapped:** OWASP LLM Top 10 · NIST AI RMF · MITRE ATLAS · ISO/IEC 42001

---

## The Problem

Most RAG systems retrieve documents based on semantic similarity alone — with no awareness of who is asking or what they are cleared to see. This means an external contractor with Public clearance can ask "what are employee salaries?" and receive Highly Confidential payroll data, because the retrieval layer has no access controls.

This is **OWASP LLM06: Sensitive Information Disclosure** — and it is one of the most common real-world AI security failures.

---

## What This Demo Shows

| State | Behaviour |
|---|---|
| Vulnerable (baseline) | Any user retrieves any document — payroll, credentials, financial data exposed regardless of clearance |
| Secure (remediated) | Pre-retrieval clearance filter, sensitivity-aware redaction, hard refusal, full audit log |

---

## Project Structure

| File | Description |
|---|---|
| `documents.py` | 10 mock documents with sensitivity labels + 4 users with clearance levels |
| `rag_vulnerable.py` | Baseline RAG — no access controls, reproduces LLM06 |
| `rag_secure.py` | Remediated RAG — access-aware retrieval, redaction, refusal, audit log |
| `show_audit_log.py` | Pretty-prints the audit log from the secure system |
| `show_controls.py` | Prints the full control mapping summary |
| `control_mapping.csv` | 12 controls mapped across all 4 frameworks |
| `report.html` | Visual security report — open in browser |

---

## Document Corpus

10 documents across Finance, HR, IT, and Procurement with 4 sensitivity levels:

| Sensitivity | Examples |
|---|---|
| Public | Office holiday schedule, company mission |
| Internal | Vendor onboarding policy, approved vendor list |
| Confidential | Q4 financial summary, board meeting minutes |
| Highly Confidential | Payroll data, salary matrix, IT credentials, incident response playbook |

---

## Users and Clearance Levels

| User | Role | Clearance | Can Access |
|---|---|---|---|
| dave | External Contractor | Public | Public only |
| alice | HR Coordinator | Internal | Public + Internal |
| bob | Finance Manager | Confidential | + Confidential |
| carol | IT Director | Highly Confidential | Everything |

---

## How to Run

**Prerequisites:**
```bash
pip install sentence-transformers chromadb ollama
```

Install Ollama from [ollama.com](https://ollama.com) and pull the model:
```bash
ollama pull llama3.2:1b
```

**Run the vulnerable baseline:**
```bash
python rag_vulnerable.py
```

**Run the secure remediated version:**
```bash
python rag_secure.py
```

**View the audit log:**
```bash
python show_audit_log.py
```

**Open the visual report:**
Open `report.html` in your browser.

---

## Before vs After — Same Query, Different Outcome

**Dave (External Contractor — Public clearance) asks about salaries:**

Vulnerable:
```
[RETRIEVED DOCUMENTS — no filtering]
  1. [Highly Confidential] Payroll Processing Run — June 2026
  2. [Highly Confidential] Employee Salary Band Matrix
  3. [Confidential] Q4 2025 Financial Summary

[LLM RESPONSE]
Sarah Chen's salary is $13,200. James Okafor's salary is $9,100...
```

Secure:
```
[ACCESS CONTROL]
  BLOCKED  [Highly Confidential] Payroll Processing Run — June 2026
  BLOCKED  [Highly Confidential] Employee Salary Band Matrix
  BLOCKED  [Confidential] Q4 2025 Financial Summary

[REFUSAL] Access denied. You do not have clearance to view documents
relevant to this query. Your clearance: Public.
```

---

## Security Controls Implemented

### 1. Pre-Retrieval Clearance Filtering
Documents are filtered against the user's clearance level **before** being passed to the LLM. The LLM never sees unauthorized content — not even as context it "won't use."

### 2. Sensitivity-Aware Redaction
For documents at the boundary of a user's clearance, sensitive tokens (amounts, IDs, emails) are masked before the content reaches the LLM.

### 3. Hard Refusal Logic
If no cleared documents are available for a query, the system refuses entirely — the LLM is not called at all.

### 4. Full Audit Log
Every query is logged with: timestamp, username, clearance level, query text, access decision, blocked document list, cleared document list, and LLM response.

---

## Control Mapping

| Control | Framework | What It Covers |
|---|---|---|
| LLM06 | OWASP LLM Top 10 | Sensitive Information Disclosure — core vulnerability reproduced and remediated |
| LLM01 | OWASP LLM Top 10 | Prompt Injection — system prompt isolation |
| LLM02 | OWASP LLM Top 10 | Insecure Output Handling — redaction layer |
| GOVERN-1 | NIST AI RMF | Policies and accountability — clearance hierarchy |
| MAP-3 | NIST AI RMF | Risk identification — oversharing risk mapped |
| MEASURE-2 | NIST AI RMF | Risk monitoring — audit log |
| MANAGE-1 | NIST AI RMF | Risk response — three-layer control |
| AML-T0048 | MITRE ATLAS | LLM Data Disclosure attack technique |
| AML-T0051 | MITRE ATLAS | LLM Prompt Injection via RAG |
| 6.1 | ISO/IEC 42001 | AI Risk Assessment |
| 6.2 | ISO/IEC 42001 | AI Risk Treatment |
| 8.4 | ISO/IEC 42001 | AI System Logging and Monitoring |

---

## Why the Fix Must Happen Before the LLM

A common misconception is that LLM safety training is a security control. It is not:

- A different model with less safety training would expose credentials directly
- The unauthorized document was already retrieved and sent to the LLM
- An attacker can rephrase queries to bypass model-level refusals
- LLM behavior is non-deterministic and cannot be relied on as a security boundary

**The fix must be architectural — filter before retrieval, not after.**

---

## Related Project

[IAM Governance Program](https://github.com/MR2300/iam-governance-program) — end-to-end simulated IAM governance program covering RBAC, Keycloak deployment, SoD violation detection, access certification, and ISO 27001 / NIST 800-53 control mapping.
