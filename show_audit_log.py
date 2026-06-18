import json

with open("audit_log.jsonl") as f:
    entries = [json.loads(line) for line in f]

print(f"\n{'='*65}")
print(f"  AUDIT LOG — RAG Document Assistant — Northfield Industries")
print(f"{'='*65}")

for i, e in enumerate(entries, 1):
    decision_label = "✓ ALLOWED" if e["decision"] == "ALLOWED" else "✗ REFUSED"
    print(f"\n[{i}] {e['timestamp'][:19].replace('T', ' ')}")
    print(f"  User      : {e['username']} (clearance: {e['clearance']})")
    print(f"  Query     : {e['query']}")
    print(f"  Decision  : {decision_label}")
    if e["blocked_docs"]:
        print(f"  Blocked   : {', '.join(e['blocked_docs'])}")
    if e["cleared_docs"]:
        print(f"  Cleared   : {', '.join(e['cleared_docs'])}")
    print(f"  Response  : {e['response'][:80]}...")

print(f"\n{'='*65}")
print(f"  Total queries: {len(entries)}")
print(f"  Refused      : {sum(1 for e in entries if e['decision'] == 'REFUSED')}")
print(f"  Allowed      : {sum(1 for e in entries if e['decision'] == 'ALLOWED')}")
print(f"{'='*65}\n")
