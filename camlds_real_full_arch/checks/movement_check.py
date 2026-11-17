# -*- coding: utf-8 -*-
"""D2 check: does the environment's attacker movement model match the recorded runs?

Read-only. No training, no policy, no test scoring. Writes checks/MOVEMENT_CHECK.txt.

Per-command zone = the zone of the host on which the command EXECUTES (the attacker's position), from:
  * AttackMate execution records (camlds_real/out/scan/ATTACKMATE_ALL.jsonl), linked to the 904 corpus
    commands by camlds_real/out/sidecar/steps_link.jsonl (type and command text must agree);
  * AttackBed commit 4d43354: ansible/hosts.example (host -> subnet), docs/development/firewall.md
    (subnet -> zone, DNAT ports, reverse-shell origins), docs/scenarios/*.md (which host each
    scenario's implants and handlers run on).
Every rule below cites its source. The environment model is run with env_cmd's own _move and the
pre-drawn uniforms of make_spec, with no defence, over each run's full length.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARCH = HERE.parent
REPO = ARCH.parent
sys.path.insert(0, str(ARCH))
import pipeline as P  # noqa: E402  (sets the frozen paths exactly as the study does)

env = P.env

# hosts.example + firewall.md + dns.md (192.42.0.0/16 is the fake internet = inet)
HOST_ZONE = {
    "attacker": "Internet", "corpdns": "Internet", "inetdns": "Internet",
    "videoserver": "DMZ", "reposerver": "DMZ", "docker": "DMZ", "webcam": "DMZ",
    "linuxshare": "LAN", "lanturtle": "LAN", "wazuh": "LAN",
    "adminpc": "Admin", "client": "User",
    "firewall": "fw",          # firewall.md: the firewall is its own zone 'fw', not a defended zone
}
# firewall.md DNAT on the public IP 192.42.0.254 / fw.attackbed.com
DNAT = {"2222": "videoserver", "10022": "reposerver", "5901": "reposerver"}
# sessions created by exploits, handlers or implants: host per scenario documentation
SESSION_HOST = {
    ("1", "foothold"): "videoserver",   # videoserver.md: ZoneMinder exploit (firewall.md: DNAT 80)
    ("1", "root"): "videoserver",       # videoserver.md: privilege escalation on the same host
    ("2", "superimplant"): "videoserver",  # linuxmalware.md: malware on the videoserver
    ("3", "movement"): "linuxshare",    # firewall.md S3: reverse shell lan(LINUXSHARE) -> inet:4444
    ("4", "sliver1"): "firewall",       # network.md: knock-triggered sliver on the firewall
    ("6", "revshell"): "client",        # client.md: client exploited
    ("6", "client"): "client",          # vnc localhost:5902 through the tunnel = the client's screen
    ("6", "social_engineering"): "client",
    ("6", "attacker"): "attacker",      # vnc localhost:5900 = the attacker's own desktop
    ("7", "foothold"): "docker",        # firewall.md S7: DNAT 8080 to CLOUD 172.17.100.125 (= docker)
    ("7", "badimplant"): "docker",      # docker.md: breakout to the docker host
}
# commands with no session run on the attacker machine; in S5 that machine is the LAN Turtle
ATTACKER_HOST = {"5": "lanturtle"}     # lanturtle.md: "an attacker machine is already placed inside the LAN"
HOP = re.compile(r"\bssh\b.*?@([a-z0-9]+)\.attackbed")  # an ssh hop inside a session moves the session


def base(run):
    return run.split("_")[0]


def host_per_record(records, s):
    """Replay ALL AttackMate records of one run in order (session creations may lie outside the corpus)."""
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
            sessions[sess] = m.group(1)   # later commands of this session run on the new host
    return host_of


def recorded_zones():
    am = {}
    for line in open(REPO / "camlds_real/out/scan/ATTACKMATE_ALL.jsonl", encoding="utf-8"):
        r = json.loads(line)
        am.setdefault(r["path"], {})[r["index"]] = r["record"]
    link = [json.loads(l) for l in open(REPO / "camlds_real/out/sidecar/steps_link.jsonl", encoding="utf-8")]
    out = {}
    for run in sorted({r["run"] for r in link}):
        rows = sorted((r for r in link if r["run"] == run), key=lambda r: r["exec_index"])
        s = base(run)
        hosts = host_per_record(am[rows[0]["attackmate_path"]], s)
        zones = []
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
                raise RuntimeError(f"no documented host for {run} #{r['exec_index']}: {recs[idx]['type']}")
            zones.append(HOST_ZONE[hosts[idx]])
        out[run] = zones
    return out


def model_zones(run, n, meta, seed):
    """env_cmd._move, no defence, the run's own entry/target, uniforms drawn as make_spec draws them."""
    e = env.CommandEngagementEnv(env.EnvConfig())
    spec = env.make_spec({"id": run["id"], "scenario": run["scenario"], "commands": run["commands"]},
                         np.random.default_rng(seed), meta)
    e.reset(spec)
    zs = []
    for t in range(n):
        e.zone = e._move(spec.u[env.U_MOVE, t], spec.u[env.U_LATERAL, t])
        zs.append(env.ZONES[e.zone])
    return zs


def stats(zs, target):
    changes = sum(a != b for a, b in zip(zs, zs[1:]))
    in_t = [z == target for z in zs]
    stay = [b == a for a, b in zip(zs, zs[1:]) if a == target]
    return {"changes": changes, "frac_target": float(np.mean(in_t)),
            "stay_target": float(np.mean(stay)) if stay else float("nan"),
            "frac_undefended": float(np.mean([z in ("Internet", "fw") for z in zs])),
            "zones": len(set(zs))}


def main():
    meta = env.scenario_metadata()
    runs = {}
    for f in P.data.folds():
        for split in ("train", "val", "test"):
            for r in P.runs(f, split):
                runs[r["id"]] = r
    rec = recorded_zones()
    assert set(rec) == set(runs), "recorded and corpus runs differ"
    lines = ["D2 movement check (read-only). Zone = where the command executes.", "",
             "run | n | target | recorded: changes / in-target / stay-in-target / undefended | "
             "model (mean of 20 draws): changes / in-target / stay-in-target", ""]
    agg = {"rec": [], "mod": []}
    for k, (rid, zs) in enumerate(sorted(rec.items())):
        r = runs[rid]
        n = len(r["commands"])
        assert len(zs) == n, (rid, len(zs), n)
        tgt = env.ZONES[meta[r["scenario"]]["target"]]
        a = stats(zs, tgt)
        ms = [stats(model_zones(r, n, meta, 900000 + 100 * k + d), tgt) for d in range(20)]
        b = {key: float(np.nanmean([m[key] for m in ms])) for key in ms[0]}
        agg["rec"].append(a)
        agg["mod"].append(b)
        path = []
        for z in zs:
            if not path or path[-1][0] != z:
                path.append([z, 0])
            path[-1][1] += 1
        lines.append(f"{rid} | {n} | {tgt} | {a['changes']} / {a['frac_target']:.2f} / {a['stay_target']:.2f} / "
                     f"{a['frac_undefended']:.2f} | {b['changes']:.1f} / {b['frac_target']:.2f} / {b['stay_target']:.2f}")
        lines.append("    recorded path: " + " -> ".join(f"{z}x{c}" for z, c in path))
    lines.append("")
    for name in ("rec", "mod"):
        A = agg[name]
        lines.append(f"{'recorded' if name == 'rec' else 'model   '}: mean zone changes per run "
                     f"{np.mean([x['changes'] for x in A]):.2f}; mean share of commands in target "
                     f"{np.mean([x['frac_target'] for x in A]):.3f}; mean stay-in-target "
                     f"{np.nanmean([x['stay_target'] for x in A]):.3f}; mean share in undefended zones "
                     f"{np.mean([x['frac_undefended'] for x in A]):.3f}")
    stay_steps = Counter()
    for rid, zs in rec.items():
        for a_, b_ in zip(zs, zs[1:]):
            stay_steps["same" if a_ == b_ else "move"] += 1
    lines.append(f"recorded: {stay_steps['same']} consecutive command pairs in the same zone, "
                 f"{stay_steps['move']} zone changes, over {sum(len(z) for z in rec.values())} commands")
    (HERE / "MOVEMENT_CHECK.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-4:]))


if __name__ == "__main__":
    main()
