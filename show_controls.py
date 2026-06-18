import csv

with open("control_mapping.csv") as f:
    controls = list(csv.DictReader(f))

frameworks = ["OWASP LLM Top 10", "NIST AI RMF", "MITRE ATLAS", "ISO 42001"]

print(f"\n{'='*65}")
print(f"  CONTROL MAPPING — RAG Guardrail Demo")
print(f"  Frameworks: OWASP LLM Top 10 | NIST AI RMF | MITRE ATLAS | ISO 42001")
print(f"{'='*65}")

for framework in frameworks:
    fw_controls = [c for c in controls if c["Framework"] == framework]
    print(f"\n--- {framework} ({len(fw_controls)} controls) ---")
    for c in fw_controls:
        print(f"\n  [{c['ControlID']}] {c['ControlName']}")
        print(f"  Vulnerable : {c['VulnerableState'][:70]}...")
        print(f"  Remediated : {c['RemediatedState'][:70]}...")
        print(f"  Evidence   : {c['EvidenceArtifact']}")

print(f"\n{'='*65}")
print(f"  Total controls mapped: {len(controls)}")
print(f"{'='*65}\n")
