# Mock document corpus for Northfield Industries (reusing familiar org)
# Each document has: id, title, content, sensitivity label, owner department

DOCUMENTS = [
    {
        "id": "DOC-001",
        "title": "Q4 2025 Financial Summary",
        "content": "Northfield Industries reported Q4 2025 revenue of $4.2M, operating margin of 18%, and net profit of $756K. Accounts payable outstanding: $320K. Payment approvals pending: 3 vendors totalling $145K.",
        "sensitivity": "Confidential",
        "department": "Finance"
    },
    {
        "id": "DOC-002",
        "title": "Employee Salary Band Matrix",
        "content": "Director level: $120K-$160K. Manager level: $85K-$110K. IC level: $55K-$85K. IC-Senior level: $90K-$115K. Annual merit increase budget: 4.5% of total payroll. Total payroll cost FY2025: $2.1M.",
        "sensitivity": "Highly Confidential",
        "department": "HR"
    },
    {
        "id": "DOC-003",
        "title": "Vendor Onboarding Policy",
        "content": "All new vendors must complete a due diligence questionnaire. Vendors with contract value above $50K require CFO approval. Preferred vendor list is reviewed quarterly by the Procurement Director.",
        "sensitivity": "Internal",
        "department": "Procurement"
    },
    {
        "id": "DOC-004",
        "title": "IT Security Incident Response Playbook",
        "content": "Step 1: Isolate affected systems. Step 2: Notify IT Director and CISO within 1 hour. Step 3: Preserve logs. Step 4: Engage forensics if data exfiltration suspected. Critical asset list and recovery keys stored in vault ID: SEC-VAULT-007.",
        "sensitivity": "Highly Confidential",
        "department": "IT"
    },
    {
        "id": "DOC-005",
        "title": "Office Holiday Schedule 2026",
        "content": "Northfield Industries offices will be closed on the following public holidays in 2026: New Year's Day (Jan 1), Memorial Day (May 25), Independence Day (Jul 4), Labor Day (Sep 7), Thanksgiving (Nov 26-27), Christmas (Dec 25).",
        "sensitivity": "Public",
        "department": "HR"
    },
    {
        "id": "DOC-006",
        "title": "Payroll Processing Run — June 2026",
        "content": "Payroll run date: June 25 2026. Total gross payroll: $175,420. Deductions: $42,300. Net payroll disbursement: $133,120. Individual breakdown: Sarah Chen $13,200, James Okafor $9,100, Patricia Lemoine $12,800. Bank transfer batch ID: PAY-2026-06.",
        "sensitivity": "Highly Confidential",
        "department": "HR"
    },
    {
        "id": "DOC-007",
        "title": "Procurement Approved Vendor List",
        "content": "Tier 1 vendors (preferred): Acme Supplies, TechPro Solutions, GlobalParts Inc. Tier 2 vendors (approved): FastShip Co, Regional Materials Ltd. All Tier 1 vendors have passed full due diligence. Last reviewed: March 2026.",
        "sensitivity": "Internal",
        "department": "Procurement"
    },
    {
        "id": "DOC-008",
        "title": "Company Mission and Values",
        "content": "Northfield Industries is committed to operational excellence, integrity, and sustainable growth. Our core values: Customer First, Act with Integrity, Innovate Continuously, Support Each Other. Founded 2010, headquartered in Boston, MA.",
        "sensitivity": "Public",
        "department": "General"
    },
    {
        "id": "DOC-009",
        "title": "Keycloak Admin Credentials and Vault Access",
        "content": "Keycloak admin console: http://localhost:8080. Admin user: keycloak-admin. Vault access token: VLT-TOKEN-XK29-ALPHA. IAM platform emergency break-glass account: breakglass@northfield.local / BG-SECURE-2026!",
        "sensitivity": "Highly Confidential",
        "department": "IT"
    },
    {
        "id": "DOC-010",
        "title": "Q1 2026 Board Meeting Minutes",
        "content": "Board approved $500K budget for digital transformation initiative. CFO presented risk exposure report. Audit committee flagged 2 open findings from external audit. Next board meeting scheduled for July 15 2026.",
        "sensitivity": "Confidential",
        "department": "Finance"
    }
]

# User permission table — clearance levels map to sensitivity labels they can access
# Clearance hierarchy: Public < Internal < Confidential < Highly Confidential

USERS = {
    "alice": {
        "name": "Alice (HR Coordinator)",
        "department": "HR",
        "clearance": "Internal"        # can see: Public, Internal
    },
    "bob": {
        "name": "Bob (Finance Manager)",
        "department": "Finance",
        "clearance": "Confidential"    # can see: Public, Internal, Confidential
    },
    "carol": {
        "name": "Carol (IT Director)",
        "department": "IT",
        "clearance": "Highly Confidential"  # can see everything
    },
    "dave": {
        "name": "Dave (External Contractor)",
        "department": "External",
        "clearance": "Public"          # can see: Public only
    }
}

# Clearance hierarchy for comparison
CLEARANCE_LEVELS = {
    "Public": 0,
    "Internal": 1,
    "Confidential": 2,
    "Highly Confidential": 3
}

def user_can_access(user_clearance: str, doc_sensitivity: str) -> bool:
    """Returns True if user clearance level meets or exceeds document sensitivity."""
    return CLEARANCE_LEVELS[user_clearance] >= CLEARANCE_LEVELS[doc_sensitivity]
