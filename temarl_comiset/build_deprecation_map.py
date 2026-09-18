# -*- coding: utf-8 -*-
"""Build an AUTHORITATIVE old-technique-id -> current-id map from MITRE's data.

Source: mitre-attack/attack-stix-data, enterprise-attack.json. A technique that
MITRE replaced carries a `revoked-by` relationship to its successor; one marked
`x_mitre_deprecated` was retired without a successor. Nothing here is guessed.

Why this exists: COMISET was labelled against an older ATT&CK matrix, so ids like
T1086 (PowerShell) and T1073 (DLL Side-Loading) appear in the corpus but not in
the current matrix or in our vocabulary. `extract_comiset_sessions.py` discarded
them, which is how a 57-technique corpus became a 10-technique one.
"""
import json, os, sys

BUNDLE = sys.argv[1] if len(sys.argv) > 1 else "enterprise-attack.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "attack_deprecation_map.json")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    objs = json.load(open(BUNDLE, encoding="utf-8"))["objects"]

    by_id, ext = {}, {}
    for o in objs:
        by_id[o.get("id")] = o
        if o.get("type") == "attack-pattern":
            for r in o.get("external_references", []):
                if r.get("source_name") == "mitre-attack" and r.get("external_id"):
                    ext[o["id"]] = r["external_id"]

    revoked = {}
    for o in objs:
        if o.get("type") == "relationship" and o.get("relationship_type") == "revoked-by":
            src, tgt = ext.get(o.get("source_ref")), ext.get(o.get("target_ref"))
            if src and tgt:
                revoked[src] = tgt

    # follow chains (A revoked-by B revoked-by C)
    resolved = {}
    for a in revoked:
        seen, cur = {a}, revoked[a]
        while cur in revoked and cur not in seen:
            seen.add(cur)
            cur = revoked[cur]
        resolved[a] = cur

    deprecated = sorted({ext[o["id"]] for o in objs
                         if o.get("type") == "attack-pattern"
                         and o.get("x_mitre_deprecated") and o["id"] in ext})
    current = sorted({v for k, v in ext.items()
                      if not by_id[k].get("x_mitre_deprecated")
                      and not by_id[k].get("revoked")})

    json.dump({"revoked_to_current": resolved,
               "deprecated_no_successor": deprecated,
               "current_ids": current,
               "source": "mitre-attack/attack-stix-data enterprise-attack.json"},
              open(OUT, "w"), indent=1)
    print("revoked/renamed ids  :", len(resolved))
    print("deprecated, no successor:", len(deprecated))
    print("current technique ids:", len(current))

    probe = ["T1086", "T1073", "T1093", "T1130", "T1031", "T1099", "T1202",
             "T1175", "T1089", "T1117", "T1063", "T1064", "T1170", "T1127",
             "T1053", "T1055", "T1543", "T1003", "T1036", "T1047"]
    print("\nCOMISET ids seen in the REAL corpus:")
    for t in probe:
        if t in resolved:
            print("   %-10s -> %-14s (revoked, replaced)" % (t, resolved[t]))
        elif t in deprecated:
            print("   %-10s -> %-14s (deprecated, no successor)" % (t, "--"))
        elif t in current:
            print("   %-10s    %-14s (still current)" % (t, ""))
        else:
            print("   %-10s -> %-14s (NOT FOUND in enterprise matrix)" % (t, "?"))
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
