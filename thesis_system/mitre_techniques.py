# mitre_techniques.py
"""
File 1 of 8 — Vocabulary & Mapping
====================================
Purpose: Acts as the tokenizer ground truth for the Transformer encoder.
         Maps MITRE ATT&CK techniques to unique integer IDs.

Design rationale:
  - 20 base techniques selected to cover the full network intrusion kill chain
    (Initial Access → Execution → Persistence → Privilege Escalation →
     Discovery → Lateral Movement → Collection/Exfiltration → Impact)
  - 3 additional techniques (ids 20–22) added after real-data analysis of
    COMISET dataset: T1036, T1574, T1553 together cover ~57% of labeled
    records — extending vocab from 20 to 23 raises coverage from 40.7% to
    ~97.5% without altering any existing id assignments.
  - Ordering of original 20 follows temporal attack progression — important
    because the Transformer models attacker INTENT as a SEQUENCE.
  - PAD (id=23) and UNK (id=24) are special tokens, excluded from sequences.
  - VOCAB_SIZE = 25 (23 techniques + 2 special tokens)

IMPORTANT — backward compatibility:
  - IDs 0–19 are IDENTICAL to the pre-trained encoder checkpoint.
    Existing embedding rows are preserved when fine-tuning on COMISET.
  - IDs 20–22 are new rows initialized randomly; fine-tuning trains them.
  - PAD/UNK shifted from 20/21 → 23/24. Update all downstream references.

Reference: MITRE ATT&CK Framework v14 (https://attack.mitre.org)
"""

MITRE_TECHNIQUES = {

    # ── 1. Initial Access ────────────────────────────────────────────────────
    "T1190": {"id": 0,  "name": "Exploit Public-Facing Application",          "tactic": "Initial Access"},
    "T1566": {"id": 1,  "name": "Phishing",                                   "tactic": "Initial Access"},

    # ── 2. Execution ─────────────────────────────────────────────────────────
    "T1059": {"id": 2,  "name": "Command and Scripting Interpreter",          "tactic": "Execution"},
    "T1204": {"id": 3,  "name": "User Execution",                             "tactic": "Execution"},

    # ── 3. Persistence ───────────────────────────────────────────────────────
    "T1053": {"id": 4,  "name": "Scheduled Task/Job",                         "tactic": "Persistence"},
    "T1543": {"id": 5,  "name": "Create or Modify System Process",            "tactic": "Persistence"},
    "T1547": {"id": 6,  "name": "Boot or Logon Autostart Execution",          "tactic": "Persistence"},

    # ── 4. Privilege Escalation ──────────────────────────────────────────────
    "T1068": {"id": 7,  "name": "Exploitation for Privilege Escalation",      "tactic": "Privilege Escalation"},
    "T1055": {"id": 8,  "name": "Process Injection",                          "tactic": "Privilege Escalation"},

    # ── 5. Discovery ─────────────────────────────────────────────────────────
    "T1046": {"id": 9,  "name": "Network Service Scanning",                   "tactic": "Discovery"},
    "T1016": {"id": 10, "name": "System Network Configuration Discovery",     "tactic": "Discovery"},
    "T1083": {"id": 11, "name": "File and Directory Discovery",               "tactic": "Discovery"},

    # ── 6. Lateral Movement ──────────────────────────────────────────────────
    "T1021": {"id": 12, "name": "Remote Services",                            "tactic": "Lateral Movement"},
    "T1550": {"id": 13, "name": "Use Alternate Authentication Material",      "tactic": "Lateral Movement"},
    "T1072": {"id": 14, "name": "Software Deployment Tools",                  "tactic": "Lateral Movement"},

    # ── 7. Collection & Exfiltration ─────────────────────────────────────────
    "T1005": {"id": 15, "name": "Data from Local System",                     "tactic": "Collection"},
    "T1560": {"id": 16, "name": "Archive Collected Data",                     "tactic": "Collection"},
    "T1041": {"id": 17, "name": "Exfiltration Over C2 Channel",               "tactic": "Exfiltration"},

    # ── 8. Impact ────────────────────────────────────────────────────────────
    "T1486": {"id": 18, "name": "Data Encrypted for Impact",                  "tactic": "Impact"},
    "T1489": {"id": 19, "name": "Service Stop",                               "tactic": "Impact"},

    # ── 9. Real-Data Extensions (COMISET analysis — ids preserved) ───────────
    # Added after scanning 5M records of COMISET dataset.
    # These 3 techniques account for ~56.8% of all labeled records in COMISET.
    # IDs start at 20 to preserve backward compatibility with pre-trained
    # encoder checkpoint (embedding rows 0–19 unchanged).
    "T1036": {"id": 20, "name": "Masquerading",                               "tactic": "Defense Evasion"},
    "T1574": {"id": 21, "name": "Hijack Execution Flow",                      "tactic": "Persistence"},
    "T1553": {"id": 22, "name": "Subvert Trust Controls",                     "tactic": "Defense Evasion"},

    # ── Special Tokens ───────────────────────────────────────────────────────
    # NOT part of attack sequences — used by Transformer input pipeline only.
    # Shifted from 20/21 → 23/24 to accommodate real-data extensions above.
    "PAD":   {"id": 23, "name": "Padding Token",                              "tactic": "None"},
    "UNK":   {"id": 24, "name": "Unknown Technique",                          "tactic": "None"},
}

# ── Helper: String → ID ──────────────────────────────────────────────────────
TOKENS = {k: v["id"] for k, v in MITRE_TECHNIQUES.items()}

# ── Helper: ID → String ──────────────────────────────────────────────────────
ID_TO_TECHNIQUE = {v["id"]: k for k, v in MITRE_TECHNIQUES.items()}

# ── Helper: ID → Full metadata ───────────────────────────────────────────────
ID_TO_META = {v["id"]: v for k, v in MITRE_TECHNIQUES.items()}

# ── Sub-technique → Parent ID mapping ────────────────────────────────────────
# Used by COMISET pipeline: T1574.002 → strip suffix → T1574 → id=21
# Any sub-technique not covered maps to UNK_ID.
# This dict is the single authoritative lookup — do not replicate inline.
SUBTECHNIQUE_TO_ID = {}
for k, v in MITRE_TECHNIQUES.items():
    if k not in ("PAD", "UNK"):
        SUBTECHNIQUE_TO_ID[k] = v["id"]  # exact match (e.g. T1059)

def technique_to_id(raw_technique_id: str) -> int:
    """
    Map a raw MITRE technique string (with or without sub-technique suffix)
    to a vocabulary integer ID.

    Examples:
        technique_to_id("T1059")       → 2
        technique_to_id("T1574.002")   → 21   (sub-technique stripped)
        technique_to_id("T1036.004")   → 20   (sub-technique stripped)
        technique_to_id("T1999")       → 24   (UNK — not in vocab)
        technique_to_id("Port Monitors") → 24 (UNK — malformed)
        technique_to_id("")            → 24   (UNK — empty)
    """
    if not raw_technique_id or not isinstance(raw_technique_id, str):
        return UNK_ID
    cleaned = raw_technique_id.strip()
    # Direct match first (handles base techniques)
    if cleaned in SUBTECHNIQUE_TO_ID:
        return SUBTECHNIQUE_TO_ID[cleaned]
    # Strip sub-technique suffix (T1574.002 → T1574)
    parent = cleaned.split('.')[0]
    if parent in SUBTECHNIQUE_TO_ID:
        return SUBTECHNIQUE_TO_ID[parent]
    # Validate format — must start with T followed by digits
    if not (parent.startswith('T') and parent[1:].isdigit()):
        return UNK_ID
    return UNK_ID

# ── Constants ────────────────────────────────────────────────────────────────
NUM_TECHNIQUES  = 23          # Real MITRE techniques (ids 0–22)
PAD_ID          = TOKENS["PAD"]   # 23
UNK_ID          = TOKENS["UNK"]   # 24
VOCAB_SIZE      = 25          # Total embedding table size (NUM_TECHNIQUES + 2)
MAX_SEQ_LEN     = 16          # Max attacker sequence length (thesis arch — unchanged)

# ── Tactic ordering ───────────────────────────────────────────────────────────
TACTIC_ORDER = [
    "Initial Access",
    "Execution",
    "Persistence",
    "Privilege Escalation",
    "Defense Evasion",
    "Discovery",
    "Lateral Movement",
    "Collection",
    "Exfiltration",
    "Impact",
]

# ── Tactic → technique IDs ────────────────────────────────────────────────────
TACTIC_TO_IDS = {}
for k, v in MITRE_TECHNIQUES.items():
    tactic = v["tactic"]
    if tactic != "None":
        TACTIC_TO_IDS.setdefault(tactic, []).append(v["id"])


# ── Verification ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"  MITRE Vocabulary Initialized")
    print(f"{'='*60}")
    print(f"  NUM_TECHNIQUES : {NUM_TECHNIQUES}  (20 base + 3 real-data extensions)")
    print(f"  VOCAB_SIZE     : {VOCAB_SIZE}  (includes PAD + UNK)")
    print(f"  MAX_SEQ_LEN    : {MAX_SEQ_LEN}")
    print(f"  PAD_ID         : {PAD_ID}")
    print(f"  UNK_ID         : {UNK_ID}")
    print(f"{'='*60}")
    print(f"\n  Techniques by tactic:")
    for tactic in TACTIC_ORDER:
        ids = TACTIC_TO_IDS.get(tactic, [])
        techs = [f"{ID_TO_TECHNIQUE[i]}(id={i})" for i in ids]
        print(f"  {tactic:<35} {techs}")
    print(f"\n  Sub-technique mapping tests:")
    test_cases = [
        ("T1059",        2),
        ("T1574.002",   21),
        ("T1036.004",   20),
        ("T1553.004",   22),
        ("T1055.001",    8),
        ("T1999",       24),
        ("Port Monitors",24),
        ("1210",        24),
        ("T",           24),
        ("",            24),
    ]
    all_pass = True
    for raw, expected in test_cases:
        result = technique_to_id(raw)
        status = "✅ PASS" if result == expected else f"❌ FAIL (got {result})"
        print(f"  technique_to_id({raw!r:<20}) → {result}  {status}")
        if result != expected:
            all_pass = False
    print(f"\n  {'All tests passed ✅' if all_pass else 'SOME TESTS FAILED ❌'}")
    print(f"{'='*60}")
    print(f"\n  Backward compatibility check (ids 0–19 unchanged):")
    original = {
        "T1190":0,"T1566":1,"T1059":2,"T1204":3,"T1053":4,
        "T1543":5,"T1547":6,"T1068":7,"T1055":8,"T1046":9,
        "T1016":10,"T1083":11,"T1021":12,"T1550":13,"T1072":14,
        "T1005":15,"T1560":16,"T1041":17,"T1486":18,"T1489":19,
    }
    compat_pass = True
    for tech, expected_id in original.items():
        actual = TOKENS[tech]
        if actual != expected_id:
            print(f"  ❌ COMPAT FAIL: {tech} expected {expected_id}, got {actual}")
            compat_pass = False
    if compat_pass:
        print(f"  ✅ All original 20 technique IDs preserved exactly.")