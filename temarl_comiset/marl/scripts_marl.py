# -*- coding: utf-8 -*-
"""
TEMARL v7-COMISET — the attacker, grounded in the COMISET Lab corpus
====================================================================
This is the ONLY substantive difference between `temarl_comiset/marl/` and the
pre-registered CAM-LDS study `temarl_marl/` (commit 33782b1). It exposes the
same interface (`scripts()`, `script_ids()`, `max_horizon()`, `loso_folds()`,
`step_marginals()`, `estimate_chain()`, `equivalence_check()`), so the
environment, the reference ladder, the gates, the calibration, MAPPO and the
analysis all run unchanged. `verify_copy.py` proves that.

WHAT COMISET LAB IS (measured 2026-09-19, before this module existed)
---------------------------------------------------------------------
  * ONE host (desktop-4pvps6e.phoenix.local), 10 days (2022-11-16..25),
    11 user accounts, 26,628 process sessions, 1,713,654 labelled records.
  * No network and no cross-host movement.
  * The 10 days look alike: every day is dominated by Persistence
    (T1574 ~32%, T1543 ~17%, T1053 ~10%). There are no named attack playbooks.
  * 6,796 usable sessions (repeats collapsed, >= 2 techniques), 19 techniques,
    8 tactics -- the corpus of the COMISET encoder study (`prereg_comiset`).

CAM-LDS supplies named scripts with real geography. COMISET supplies neither,
so every quantity below is fixed by a rule written BEFORE any COMISET ladder,
gate or learned result existed, chosen to mirror the CAM-LDS logic as closely
as the data allows.

PRE-DECLARED RULES (2026-09-19)
-------------------------------
  sessions   exactly the encoder study's corpus: each process session's
             techniques mapped by the frozen vocabulary, out-of-vocabulary
             dropped, consecutive repeats collapsed, >= 2 techniques kept.
             (CAM-LDS runs keep repeats; COMISET sessions cannot -- one
             process repeats a single detection up to 418,367 times.)
  script     all sessions sharing a TERMINAL tactic (the tactic of the last
             technique), mirroring CAM-LDS, whose scripts are characterised
             by their terminal tactic. A group needs >= MIN_SESSIONS sessions
             to be a script; smaller groups are dropped and reported.
  goal       the script's terminal tactic (its declared objective in CAM-LDS
             terms). Objective = first goal-tactic technique on a real host
             in the target zone (G = 1), as in v7.
  geography  entry zone = target zone = User: the only host is a desktop
             workstation. Movement away from it and back (p_goal / p_stay)
             and breadcrumb-following are the same modelled mechanics as in
             v7, calibrated by the same architecture-blind grid.
  chain      the unchanged v5 estimator (FLOOR 0.02, BIGRAM 4.0, INIT 2.0,
             no drift) over the script's sessions, in session-key order.
  horizon    a real session length of the script, capped at 61 (the CAM-LDS
             maximum) so both datasets share one episode-length regime.
  LOSO       hold out one script (= one terminal tactic): "an unseen attack
             objective" is the COMISET analogue of an unseen attack script.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from typing import Dict, List

import numpy as np

import _frozen  # noqa: F401  (verifies frozen inputs, sets sys.path)
from _frozen import DATA_DIR
from env_v2 import DEFENDED_ZONES, ZONES, technique_to_id
from profiles_v5 import BIGRAM_WEIGHT, FLOOR, INIT_WEIGHT
from vocab_v2 import NUM_TECHNIQUES, TACTIC_ORDER, tactic_of

NT = NUM_TECHNIQUES
ZONE_ID = {z: i for i, z in enumerate(ZONES)}
HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS_GZ = os.path.join(HERE, "..", "data_local", "comiset_lab_sessions.json.gz")
CORPUS_SHA256 = "deb2f2f784a3eda1fb6812c3e3676ca7cb11710f237f6779fb2fbfc15cd34190"
EXPECTED_SESSIONS = 6796             # the COMISET encoder-study corpus
MIN_SESSIONS = 30
HORIZON_CAP = 61                     # the CAM-LDS maximum run length
HOST_ZONE = "User"                   # the single host is a desktop workstation
GROUNDING_PATH = os.path.join(DATA_DIR, "camlds_grounding.json")

_CACHE = None
_SESSIONS = None

_TACTIC_CODE = {"Reconnaissance": "REC", "Resource Development": "RES",
                "Initial Access": "IA", "Execution": "EXE",
                "Persistence": "PER", "Privilege Escalation": "PRV",
                "Defense Evasion": "DEF", "Credential Access": "CRD",
                "Discovery": "DIS", "Lateral Movement": "LAT",
                "Collection": "COL", "Command and Control": "C2",
                "Exfiltration": "EXF", "Impact": "IMP"}


def _collapse(ids):
    out = []
    for i in ids:
        if not out or out[-1] != i:
            out.append(i)
    return out


def comiset_sessions() -> List[List[int]]:
    """The encoder-study corpus, read from the tracked .gz (hash-verified)."""
    global _SESSIONS
    if _SESSIONS is not None:
        return _SESSIONS
    raw = open(CORPUS_GZ, "rb").read()
    if hashlib.sha256(raw).hexdigest() != CORPUS_SHA256:
        raise RuntimeError("COMISET corpus changed: %s does not match the "
                           "pre-declared sha256" % CORPUS_GZ)
    blob = json.loads(gzip.decompress(raw))
    out = []
    for key in sorted(blob["sessions"]):
        rec = blob["sessions"][key]
        rt = rec.get("raw_techniques") if isinstance(rec, dict) else rec
        ids = [technique_to_id(t) for t in (rt or [])]
        ids = _collapse([i for i in ids if i < NT])
        if len(ids) >= 2:
            out.append(ids)
    if len(out) != EXPECTED_SESSIONS:
        raise RuntimeError("expected %d usable sessions, found %d"
                           % (EXPECTED_SESSIONS, len(out)))
    _SESSIONS = out
    return out


def estimate_chain(member_seqs: List[List[int]]):
    """The v5 estimator, verbatim (identical to temarl_marl/scripts_marl.py)."""
    T = np.full((NT, NT), FLOOR)
    init = np.zeros(NT) + FLOOR
    for sq in member_seqs:
        init[sq[0]] += INIT_WEIGHT
        for a, b in zip(sq, sq[1:]):
            T[a, b] += BIGRAM_WEIGHT
    T = T / T.sum(1, keepdims=True)
    return T, init / init.sum()


def grouping() -> Dict[str, dict]:
    """Sessions grouped by terminal tactic; which groups become scripts."""
    groups: Dict[str, List[List[int]]] = {}
    for s in comiset_sessions():
        groups.setdefault(tactic_of(s[-1]), []).append(s)
    return {tac: {"sessions": seqs, "kept": len(seqs) >= MIN_SESSIONS}
            for tac, seqs in groups.items()}


def build_scripts() -> Dict[str, dict]:
    zone = ZONE_ID[HOST_ZONE]
    assert zone in DEFENDED_ZONES
    out = {}
    for tac, g in sorted(grouping().items(),
                         key=lambda kv: TACTIC_ORDER.index(kv[0])):
        if not g["kept"]:
            continue
        rs = g["sessions"]
        T, init = estimate_chain(rs)
        sid = "C-" + _TACTIC_CODE[tac]
        goal_ids = [j for j in range(NT) if tactic_of(j) == tac]
        out[sid] = {
            "id": sid, "name": "COMISET sessions ending in %s" % tac,
            "T": T, "init": init,
            "cumT": np.cumsum(T, axis=1), "cuminit": np.cumsum(init),
            "entry": zone, "target": zone,
            "target_raw": "desktop-4pvps6e (%s)" % HOST_ZONE,
            "goal_tactic": tac, "goal_declared": tac,
            "goal_rule": "declared",   # the terminal tactic, by construction
            "goal_ids": goal_ids,
            "goal_mask": np.isin(np.arange(NT), goal_ids),
            "horizons": sorted(min(len(r), HORIZON_CAP) for r in rs),
            "n_runs": len(rs),
            "goal_steps_per_run": float(np.mean(
                [sum(tactic_of(i) == tac for i in r) for r in rs])),
        }
    if len(out) < 3:
        raise RuntimeError("fewer than 3 scripts: leave-one-script-out is impossible")
    return out


def scripts() -> Dict[str, dict]:
    global _CACHE
    if _CACHE is None:
        _CACHE = build_scripts()
    return _CACHE


def script_ids() -> List[str]:
    return sorted(scripts())


def max_horizon() -> int:
    return max(max(sc["horizons"]) for sc in scripts().values())


def loso_folds() -> List[dict]:
    ids = script_ids()
    return [{"held_out": h, "train": [s for s in ids if s != h]} for h in ids]


def step_marginals(sid: str, n_steps: int) -> np.ndarray:
    sc = scripts()[sid]
    out = np.zeros((n_steps, NT))
    p = sc["init"].copy()
    for t in range(n_steps):
        out[t] = p
        p = p @ sc["T"]
    return out


# ── estimator identity (the same check as temarl_marl) ───────────────────────

def _camlds_reconstruction():
    g = json.load(open(GROUNDING_PATH, encoding="utf-8"))
    out = {}
    for s in g["scenarios"]:
        raw = [x for x in s["technique_sequence"] if not x.startswith("<")]
        ids = [i for i in (technique_to_id(x) for x in raw) if i < NT]
        if len(ids) >= 2:
            out[s["id"]] = ids
    return out


def equivalence_check() -> dict:
    from profiles_v5 import build_profiles_v5
    v5p, con = build_profiles_v5()
    seqs = _camlds_reconstruction()
    exact, worst = True, 0.0
    for cls, members in con["members"].items():
        T, init = estimate_chain([seqs[m] for m in members])
        exact &= bool(np.array_equal(T, v5p[cls]["T"])
                      and np.array_equal(init, v5p[cls]["init"]))
        worst = max(worst, float(np.abs(T - v5p[cls]["T"]).max()))
    return {"bit_exact": exact, "max_abs_T": worst, "max_abs_init": 0.0,
            "groups": con["members"]}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 100)
    print("  TEMARL v7-COMISET — attacker models from the COMISET Lab corpus")
    print("=" * 100)
    eq = equivalence_check()
    print("  estimator identity vs profiles_v5: %s" % ("PASS" if eq["bit_exact"] else "FAIL"))
    print("  usable sessions: %d (expected %d)" % (len(comiset_sessions()), EXPECTED_SESSIONS))
    print("\n  terminal-tactic groups (script if >= %d sessions):" % MIN_SESSIONS)
    for tac, g in sorted(grouping().items(), key=lambda kv: TACTIC_ORDER.index(kv[0])):
        print("    %-22s %5d sessions  %s" % (tac, len(g["sessions"]),
                                             "SCRIPT" if g["kept"] else "dropped (too few)"))
    print("\n  %-6s %-40s %6s %-11s %s" % ("id", "name", "runs", "horizon", "goal steps/run"))
    for sid in script_ids():
        sc = scripts()[sid]
        hz = sc["horizons"]
        print("  %-6s %-40s %6d %3d..%-7d %.2f  (median %d)"
              % (sid, sc["name"], sc["n_runs"], hz[0], hz[-1],
                 sc["goal_steps_per_run"], int(np.median(hz))))
    print("  zone: entry = target = %s for every script; max horizon %d"
          % (HOST_ZONE, max_horizon()))
    print("=" * 100)
