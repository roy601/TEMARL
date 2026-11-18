# -*- coding: utf-8 -*-
"""Build attack_v15_1_tactics.json: the ATT&CK Enterprise v15.1 name and tactics of each of
CasinoLimit's 66 parent techniques (protocol CL-D1.0, Section 3).

    python casinolimit_d1/checks/attack_extract.py PATH/TO/enterprise-attack-15.1.json

The bundle is MITRE's official STIX release
https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack-15.1.json
(modified 2024-05-02, the release current when the CasinoLimit commands were recorded, May 2024).
It is about 43 MB, so only this extract is committed; the script refuses a bundle whose SHA-256 differs.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent
URL = ("https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/"
       "enterprise-attack-15.1.json")
BUNDLE_SHA256 = "a57988bffe402bb3e19d92dbe80a12143e1970b814e013e080f9df2fa5a3f6bc"
OUT = ROOT / "attack_v15_1_tactics.json"


def extract(bundle_path: Path) -> dict:
    raw = bundle_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != BUNDLE_SHA256:
        raise SystemExit("this is not the pinned ATT&CK v15.1 bundle (SHA-256 differs)")
    objs = json.loads(raw)["objects"]
    tactic = {o["x_mitre_shortname"]: o["name"] for o in objs if o["type"] == "x-mitre-tactic"}
    tech = {}
    for o in objs:
        if o["type"] != "attack-pattern" or o.get("revoked") or o.get("x_mitre_deprecated"):
            continue
        ids = [r["external_id"] for r in o.get("external_references", []) if r.get("source_name") == "mitre-attack"]
        if ids:
            tech[ids[0]] = {"name": o["name"],
                            "tactics": [tactic[k["phase_name"]] for k in o.get("kill_chain_phases", [])
                                        if k["kill_chain_name"] == "mitre-attack"]}
    labels = json.loads((REPO / "casinolimit_real" / "out" / "vocab.json").read_text(encoding="utf-8"))["parent_techniques"]
    missing = [t for t in labels if t not in tech]
    if missing:
        raise SystemExit(f"not active techniques in ATT&CK v15.1: {missing}")
    return {"source": URL, "version": "15.1", "modified": "2024-05-02T14:00:00.188Z",
            "bundle_sha256": BUNDLE_SHA256, "rule": "active (not revoked, not deprecated) attack-pattern "
            "objects; tactics = the mitre-attack kill-chain phases, in the bundle's order",
            "techniques": {t: tech[t] for t in labels}}


if __name__ == "__main__":
    res = extract(Path(sys.argv[1]))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}: {len(res['techniques'])} techniques")
