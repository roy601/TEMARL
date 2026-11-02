"""Phase 1 audit: read every input in full and print the evidence for DECISIONS.md.

    python audit/audit_inputs.py [--raw data/raw]  > audit/AUDIT_OUTPUT.txt

Read-only. Nothing here is the method: similarity is computed only to check whether
the edge cases the paper leaves undefined (D6, D8) actually occur on the test inputs.
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSIONS = ["11.0", "11.3", "12.1"]
ADVISORIES = {  # id -> (wayback file, paper's count after its own exclusions)
    "AA22-277A": ("cisa_aa22-277a_wayback/aa22-277a_20230129.html", 26),
    "AA22-138B": ("cisa_aa22-138b_wayback/aa22-138b_20230129.html", 12),
    "AA22-174A": ("cisa_aa22-174a_wayback/aa22-174a_20230201.html", 13),
}
PRE_ACCESS = {"reconnaissance", "resource-development"}  # TA0043, TA0042
COLD_START = {"T1129": 0, "T1497": 6, "T1039": 7, "T1095": 7, "T1029": 1}  # paper p.810
K = 60


def head(s):
    print(f"\n{'=' * 78}\n{s}\n{'=' * 78}")


def attack_id(o):
    for r in o.get("external_references", []):
        if r.get("source_name") == "mitre-attack":
            return r.get("external_id")
    return None


def live(o):
    return not o.get("revoked") and not o.get("x_mitre_deprecated")


def load_attack(path):
    objs = json.load(open(path, encoding="utf-8"))["objects"]
    by = {o["id"]: o for o in objs}
    parents = {attack_id(o): o for o in objs
               if o["type"] == "attack-pattern" and live(o) and not o.get("x_mitre_is_subtechnique")}
    tech_live = {attack_id(o) for o in objs if o["type"] == "attack-pattern" and live(o)}
    groups = {o["id"]: o for o in objs if o["type"] == "intrusion-set"}
    uses = collections.defaultdict(set)  # group stix id -> parent technique ids (sub-techniques rolled up)
    raw_uses = collections.Counter()
    for o in objs:
        if o["type"] != "relationship" or o["relationship_type"] != "uses" or not live(o):
            continue
        g, t = by.get(o["source_ref"]), by.get(o["target_ref"])
        if g is None or t is None or g["type"] != "intrusion-set" or t["type"] != "attack-pattern":
            continue
        tid = attack_id(t)
        raw_uses["to live technique" if live(t) else "to revoked/deprecated technique"] += 1
        if live(t):
            uses[o["source_ref"]].add(tid.split(".")[0])
    tactics = {tid: [k["phase_name"] for k in o.get("kill_chain_phases", [])
                     if k.get("kill_chain_name") == "mitre-attack"] for tid, o in parents.items()}
    return dict(objs=objs, parents=parents, tech_live=tech_live, groups=groups, uses=uses,
                raw_uses=raw_uses, tactics=tactics)


def parse_advisory(path):
    """Rows of the ATT&CK table(s), in page order: (tactic cell text, technique ids from link hrefs)."""
    t = open(path, encoding="utf-8").read()
    rows = []
    for tb in re.findall(r"<table.*?</table>", t, flags=re.S | re.I):
        if "attack.mitre.org" not in tb and not re.search(r"T1\d{3}", tb):
            continue
        tactic = None
        for tr in re.findall(r"<tr.*?</tr>", tb, flags=re.S | re.I):
            cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, flags=re.S | re.I)
            text = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in cells]
            tac = re.search(r"tactics/(TA\d{4})", tr)
            if tac or (len(text) == 1 and text[0] and not re.search(r"\d{4}", text[0])):
                tactic = tac.group(1) if tac else text[0]
            hrefs = re.findall(r"techniques/(T1\d{3})(?:/(\d{3}))?", tr)
            ids = [a + ("." + b if b else "") for a, b in hrefs]
            if not ids:  # 277A puts ids in a plain cell, not a link
                ids = re.findall(r"\bT1\d{3}(?:\.\d{3})?\b", " ".join(text))
            shown = re.findall(r"\[\s*(T?\d{4}(?:\.\d{3})?)\s*\]", " ".join(text))
            rows.append((tactic, ids, shown, " | ".join(text)))
    return rows


def sdc(a, b):
    return 2 * len(a & b) / (len(a) + len(b)) if (a or b) else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(HERE, "..", "data", "raw"))
    raw = ap.parse_args().raw

    head("A. ATT&CK VERSIONS - object counts")
    A = {}
    for v in VERSIONS:
        A[v] = d = load_attack(os.path.join(raw, f"attack_v{v}", "enterprise-attack.json"))
        st = collections.Counter("live" if live(g) else ("revoked" if g.get("revoked") else "deprecated")
                                 for g in d["groups"].values())
        nonempty = sum(1 for g, o in d["groups"].items() if live(o) and d["uses"][g])
        print(f"  v{v}: {len(d['objs']):,} objects | live parent techniques {len(d['parents'])} "
              f"| groups {dict(st)} | live groups using >=1 technique {nonempty} "
              f"| group->technique 'uses' {dict(d['raw_uses'])}")
    print("  paper: 133 groups, 191 techniques, 14 tactics (v11)")

    head("B. COLD-START COUNTS (paper p.810) - which matrix definition reproduces them")
    for v in VERSIONS:
        d = A[v]
        got = {t: sum(1 for g, o in d["groups"].items() if live(o) and t in d["uses"][g]) for t in COLD_START}
        print(f"  v{v}: {got}  {'MATCH' if got == COLD_START else 'differs'}")
    print(f"  paper : {COLD_START}")
    print("  (definition: live groups, direct 'uses' to live techniques, sub-techniques rolled up to parent)")

    head("C. v11.0 vs v11.3 - does the choice change the matrix?")
    m0 = {attack_id(o): frozenset(A["11.0"]["uses"][g]) for g, o in A["11.0"]["groups"].items() if live(o)}
    m3 = {attack_id(o): frozenset(A["11.3"]["uses"][g]) for g, o in A["11.3"]["groups"].items() if live(o)}
    print(f"  groups only in 11.0: {sorted(set(m0) - set(m3))} | only in 11.3: {sorted(set(m3) - set(m0))}")
    diff = sorted(g for g in set(m0) & set(m3) if m0[g] != m3[g])
    print(f"  groups whose technique set differs: {len(diff)}")
    for g in diff:
        print(f"    {g}: +{sorted(m3[g] - m0[g])} -{sorted(m0[g] - m3[g])}")
    print(f"  parent technique sets identical: {set(A['11.0']['parents']) == set(A['11.3']['parents'])}")

    d = A["11.0"]
    head("D. TACTICS (v11.0)")
    tc = collections.Counter(t for ts in d["tactics"].values() for t in ts)
    for t, n in tc.most_common():
        print(f"  {t:<24} {n}")
    multi = {t: ts for t, ts in d["tactics"].items() if len(ts) > 1}
    print(f"  parents in more than one tactic: {len(multi)}")
    print(f"  parents in a pre-access tactic: {sum(1 for ts in d['tactics'].values() if set(ts) & PRE_ACCESS)} "
          f"(of which also post-access: {sum(1 for ts in d['tactics'].values() if set(ts) & PRE_ACCESS and set(ts) - PRE_ACCESS)})")

    head("E. CISA ADVISORIES - every table row, ids taken from link targets")
    tests = {}
    for adv, (rel, n_paper) in ADVISORIES.items():
        rows = parse_advisory(os.path.join(raw, rel))
        print(f"\n  -- {adv} ({rel})")
        seq, seen = [], set()
        for tactic, ids, shown, text in rows:
            mism = [s for s in shown if s.lstrip("T") not in {i.lstrip("T") for i in ids} or not s.startswith("T")]
            flag = f"   <-- shown text {shown} differs from link" if ids and mism else ""
            if ids or "TA" in str(tactic):
                print(f"    {str(tactic):<10} {','.join(ids) or '(no technique)':<28} {text[:60]}{flag}")
            for i in ids:
                p = i.split(".")[0]
                if p not in seen:
                    seen.add(p)
                    seq.append((p, tactic))
        pre = [p for p, _ in seq if set(d["tactics"].get(p, [])) <= PRE_ACCESS and d["tactics"].get(p)]
        missing = [p for p, _ in seq if p not in d["parents"]]
        used = [p for p, _ in seq if p not in pre]
        tests[adv] = used
        print(f"    distinct parents {len(seq)} | pre-access {pre} | not live in v11.0 {missing} "
              f"| used {len(used)} (paper {n_paper}) {'MATCH' if len(used) == n_paper else 'DIFFERS'}")
        print(f"    order (first occurrence): {' '.join(used)}")
        multi_t = {p: d['tactics'][p] for p in used if len(d['tactics'].get(p, [])) > 1}
        print(f"    multi-tactic in this sequence: {multi_t}")
    print("\n  paper sec.5.3 example inputs for AA22-277A: T1078 T1047 T1059 T1129 "
          f"-> {'MATCH' if tests['AA22-277A'][:4] == ['T1078', 'T1047', 'T1059', 'T1129'] else 'DIFFERS'}")

    head("F. PAPER TABLE 1 (p.806) against v11.0")
    cols = ["T1059", "T1583", "T1203", "T1531", "T1083"]
    by_ext = {attack_id(o): g for g, o in d["groups"].items() if live(o)}
    exact = collections.defaultdict(set)
    by = {o["id"]: o for o in d["objs"]}
    for o in d["objs"]:
        if o["type"] == "relationship" and o["relationship_type"] == "uses" and live(o):
            g, x = by.get(o["source_ref"]), by.get(o["target_ref"])
            if g and x and g["type"] == "intrusion-set" and x["type"] == "attack-pattern" and live(x):
                exact[attack_id(g)].add(attack_id(x))
    # Table 1 prints its first data row as the column header; realigned, row i is the group below it.
    paper = {"G0018": "10101", "G0006": "01000", "G0026": "10001", "G0007": "11101", "G0060": "10101"}
    print("  (paper's rows realigned by one: its header cell 'G0018' is the first data row)")
    for g, want in paper.items():
        roll = "".join(str(int(c in d["uses"][by_ext[g]])) for c in cols)
        ex = "".join(str(int(c in exact[g])) for c in cols)
        print(f"  {g} {d['groups'][by_ext[g]]['name']:<14} paper {want} | roll-up {roll} "
              f"{'ok' if roll == want else 'DIFF'} | exact-id only {ex} {'ok' if ex == want else 'DIFF'}")
    print(f"  G0006 T1059-family links in v11.0: {sorted(t for t in exact['G0006'] if t.startswith('T1059'))}")

    head("G. EDGE CASES ON THE TEST TRAJECTORIES (v11.0, live groups)")
    G = {attack_id(o): d["uses"][g] for g, o in d["groups"].items() if live(o)}
    for adv, seq in tests.items():
        ones, ties = [], []
        for i in range(1, len(seq)):
            obs = set(seq[:i])
            s = sorted(((sdc(obs, T), g) for g, T in G.items()), reverse=True)
            ones += [(i, g) for v, g in s if v == 1.0]
            kth = s[K - 1][0]
            if kth > 0 and (len(s) > K and s[K][0] == kth):
                n_tied = sum(1 for v, _ in s if v == kth)
                inside = sum(1 for v, _ in s[:K] if v == kth)
                ties.append((i, round(kth, 4), f"{inside} of {n_tied} tied kept"))
        print(f"  {adv}: SDC == 1 at {ones or 'never'}")
        print(f"  {adv}: non-zero tie across the k={K} boundary at {len(ties)} of {len(seq) - 1} steps "
              f"{ties[:6]}{' ...' if len(ties) > 6 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
