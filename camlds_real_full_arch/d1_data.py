# -*- coding: utf-8 -*-
"""Protocol D1.0 data: where each recorded command executes, and which commands are goal commands.

Everything here is derived from released data and the testbed's own documentation; nothing is tuned.

POSITION of a command = the zone of the host on which it EXECUTES (the attacker's position), from
  * AttackMate execution records (camlds_real/out/scan/ATTACKMATE_ALL.jsonl, from the 34 md5-verified
    scenario archives), linked to the corpus by camlds_real/out/sidecar/steps_link.jsonl
    (record type and command text must agree);
  * AttackBed commit 4d43354: ansible/hosts.example (host -> subnet), docs/development/firewall.md
    (subnet -> zone, DNAT ports, reverse-shell origins), docs/development/dns.md, docs/scenarios/*.md.
GOAL COMMAND = a command whose own released tactic labels (`tactics_raw` in camlds_real/out/steps.jsonl,
  i.e. the AttackMate metadata of the dataset authors) contain the scenario's goal tactic. This uses
  the dataset's full tactic membership (e.g. T1556.003 is labelled credential-access, defense-evasion
  and persistence), not our one-tactic-per-technique vocabulary.
See ZONE_GOAL_CHECK.md for the checks behind every rule.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
ATTACKMATE = REPO / "camlds_real/out/scan/ATTACKMATE_ALL.jsonl"
STEPS_LINK = REPO / "camlds_real/out/sidecar/steps_link.jsonl"
STEPS = REPO / "camlds_real/out/steps.jsonl"

# hosts.example + firewall.md + dns.md (192.42.0.0/16 is the testbed's fake internet = 'inet')
HOST_ZONE = {
    "attacker": "Internet", "corpdns": "Internet", "inetdns": "Internet",
    "videoserver": "DMZ", "reposerver": "DMZ", "docker": "DMZ", "webcam": "DMZ",
    "linuxshare": "LAN", "lanturtle": "LAN", "wazuh": "LAN",
    "adminpc": "Admin", "client": "User",
    "firewall": "Firewall",      # firewall.md: the firewall is its own zone 'fw', defended by no agent
}
# firewall.md: DNAT on the public address 192.42.0.254 / fw.attackbed.com
DNAT = {"2222": "videoserver", "10022": "reposerver", "5901": "reposerver"}
# sessions created by exploits, handlers or implants: their host, per scenario documentation
SESSION_HOST = {
    ("1", "foothold"): "videoserver",      # videoserver.md: ZoneMinder exploit (firewall.md: DNAT 80)
    ("1", "root"): "videoserver",          # videoserver.md: privilege escalation on the same host
    ("2", "superimplant"): "videoserver",  # linuxmalware.md: same infrastructure as the videoserver
    ("3", "movement"): "linuxshare",       # firewall.md S3: reverse shell lan(LINUXSHARE) -> inet:4444
    ("4", "sliver1"): "firewall",          # network.md: knock-triggered sliver on the firewall
    ("6", "revshell"): "client",           # client.md: the client is exploited
    ("6", "client"): "client",             # vnc localhost:5902 through the tunnel = the client's screen
    ("6", "social_engineering"): "client",
    ("6", "attacker"): "attacker",         # vnc localhost:5900 = the attacker's own desktop
    ("7", "foothold"): "docker",           # firewall.md S7: DNAT 8080 to CLOUD 172.17.100.125 (docker)
    ("7", "badimplant"): "docker",         # docker.md: breakout to the docker host
}
# commands outside any session run on the attacker machine; in S5 that machine is the LAN Turtle
ATTACKER_HOST = {"5": "lanturtle"}         # lanturtle.md: "already placed inside the LAN network"
HOP = re.compile(r"\bssh\b.*?@([a-z0-9]+)\.attackbed")  # an ssh hop moves the session to that host

# Scenario table for D1.0 (ZONE_GOAL_CHECK.md). entry is used only by the random-walk sensitivity model.
SCENARIOS = {
    #      entry       target      goal tactic (dataset slug)  in P1   source
    "S1": ("Internet", "DMZ", "persistence", True),        # videoserver.md: backdoor (step 10)
    "S2": ("DMZ", "DMZ", "exfiltration", True),            # linuxmalware.md: exfiltrates data
    "S3": ("Internet", "LAN", "impact", True),             # lateralmovement.md: impact on other host
    "S4": ("DMZ", "Firewall", "defense-evasion", False),   # network.md: T1599 on the firewall (undefended)
    "S5": ("LAN", "LAN", "credential-access", True),       # lanturtle.md: auth hash stolen in the LAN
    "S6": ("User", "User", "persistence", True),           # client.md: "Attacker persists"
    "S7": ("Internet", "DMZ", "credential-access", True),  # docker.md: dumps /etc/shadow on the host
}
TACTIC_SLUGS = ("reconnaissance", "resource-development", "initial-access", "execution", "persistence",
                "privilege-escalation", "defense-evasion", "credential-access", "discovery",
                "lateral-movement", "collection", "command-and-control", "exfiltration", "impact")


def _base(run: str) -> str:
    return run.split("_")[0]


def _host_per_record(records: Dict[int, dict], s: str) -> Dict[int, str]:
    """Replay ALL AttackMate records of one run in order (a session may be created outside the corpus)."""
    sessions, host_of = {}, {}
    for idx in sorted(records):
        rec = records[idx]
        p = rec["parameters"]
        sess = p.get("session")
        if sess:
            host = sessions.get(sess) or SESSION_HOST.get((s, sess))
        elif rec["type"] in ("ssh", "vnc", "sftp") and p.get("hostname"):
            host = DNAT.get(str(p.get("port")))
        else:
            host = ATTACKER_HOST.get(s, "attacker")
        cs = p.get("creates_session")
        if cs:
            if rec["type"] in ("ssh", "vnc", "sftp") and p.get("hostname") and str(p.get("port")) in DNAT:
                sessions[cs] = DNAT[str(p.get("port"))]
            elif (s, cs) in SESSION_HOST:
                sessions[cs] = SESSION_HOST[(s, cs)]
        host_of[idx] = host
        m = HOP.search(str(rec.get("cmd", ""))) if sess else None
        if m and m.group(1) in HOST_ZONE:
            sessions[sess] = m.group(1)
    return host_of


def positions() -> Dict[Tuple[str, int], str]:
    """(run, source_row) -> zone name where that command executes. Raises on any unresolved command."""
    am: Dict[str, Dict[int, dict]] = {}
    for line in open(ATTACKMATE, encoding="utf-8"):
        r = json.loads(line)
        am.setdefault(r["path"], {})[r["index"]] = r["record"]
    with open(STEPS_LINK, encoding="utf-8") as fh:
        link = [json.loads(l) for l in fh]
    out = {}
    for run in sorted({r["run"] for r in link}):
        rows = sorted((r for r in link if r["run"] == run), key=lambda r: r["exec_index"])
        hosts = _host_per_record(am[rows[0]["attackmate_path"]], _base(run))
        for r in rows:
            recs = am[r["attackmate_path"]]
            idx = None
            for i in (r["attackmate_index"], r["attackmate_index"] - 1, r["attackmate_index"] + 1):
                c = recs.get(i)
                if c and c["type"] == r["type"] and c["cmd"].strip()[:40] == r["cmd_full"].strip()[:40]:
                    idx = i
                    break
            if idx is None:
                raise RuntimeError(f"no AttackMate record for {run} #{r['exec_index']}")
            if hosts[idx] is None:
                raise RuntimeError(f"no documented host for {run} #{r['exec_index']}")
            out[(run, r["source_row"])] = HOST_ZONE[hosts[idx]]
    return out


def tactics() -> Dict[Tuple[str, int], frozenset]:
    """(run, source_row) -> the set of tactic slugs in the command's released labels."""
    out = {}
    with open(STEPS, encoding="utf-8") as fh:
        for line in fh:
            s = json.loads(line)
            raw = s["tactics_raw"]
            out[(s["run"], s["source_row"])] = frozenset(t for t in TACTIC_SLUGS if t in raw)
    return out


def attach(runs: List[dict], pos=None, tac=None) -> List[dict]:
    """Add 'positions' (zone names) and 'goal' (bool) to each run, aligned with run['source_rows']."""
    pos = positions() if pos is None else pos
    tac = tactics() if tac is None else tac
    for r in runs:
        goal = SCENARIOS[r["scenario"]][2]
        r["positions"] = [pos[(r["id"], sr)] for sr in r["source_rows"]]
        r["goal"] = [goal in tac[(r["id"], sr)] for sr in r["source_rows"]]
    return runs
