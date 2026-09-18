# -*- coding: utf-8 -*-
"""Normalise a raw COMISET technique label to a current ATT&CK id.

Three defects in the raw labels, all observed in the corpora:
  * free text appended  -- "T1055; Possible Cobalt Strike post-exploitation jobs."
  * a name instead of an id -- "Port Monitors" (= T1013), and a bare "1210"
  * ids from an older matrix -- T1086, T1073, T1093, ... (MITRE revoked-by)
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_MAP = json.load(open(os.path.join(_HERE, "attack_deprecation_map.json"),
                      encoding="utf-8"))
REVOKED = _MAP["revoked_to_current"]
ALIAS = {"1210": "T1210", "Port Monitors": "T1013"}


def normalise(raw):
    """-> current technique id, or None if the label carries no usable id."""
    if not raw:
        return None
    t = str(raw).split(";")[0].split(",")[0].strip()
    t = ALIAS.get(t, t)
    if not t.startswith("T") or len(t) < 4:
        return None
    return REVOKED.get(t, t)
