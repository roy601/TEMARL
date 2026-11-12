# -*- coding: utf-8 -*-
"""Reproduce "Unveiling Evolving Threats" (SRDS 2025), route A, from the authors' released data.

    python reproductions/shell_attack_evolution/run.py
    python reproductions/shell_attack_evolution/run.py --out <folder>     # second-machine check

1. Downloads the authors' repository at commit d5f7fe1 (zip, about 92 MB) into data/ (not committed)
   and records its SHA-256. Resumes and retries; never re-downloads a complete file.
2. Reads dataset/sessions/*.jsonl and dataset/commands/*.jsonl straight from the zip (nothing is
   extracted or changed) and records the SHA-256 of each file read.
3. Computes every route-A target of TARGETS.csv with the PRIMARY definition of DECISIONS.md, plus the
   alternates, and gives each target its verdict by the fixed rules (DECISIONS.md 16).
4. Writes out/results.json, out/REPORT_TABLE.md, out/HASHES.txt (deterministic: no time, no path)
   and out/ENVIRONMENT.json (this machine).
Standard library only.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
COMMIT = "d5f7fe120ebd921e04026b6348c3ec5d399c5df6"
URL = f"https://codeload.github.com/zyw-286/shell-attack-evolution-dataset/zip/{COMMIT}"
ZIP_NAME = f"shell-attack-evolution-dataset-{COMMIT[:7]}.zip"
PERIODS = ("2021_2022", "2024")
TECH_ID = re.compile(r"T\d{4}(?:\.\d{3})?")
# Table VI of the paper: tactic -> techniques (decision 11)
TACTICS = {
    "Discovery": ["T1082", "T1083", "T1087", "T1424", "T1033", "T1016", "T1518", "T1069", "T1124", "T1614"],
    "Collection": ["T1005"],
    "Command and Control": ["T1105", "T1071"],
    "Credential Access": ["T1003"],
    "Defense Evasion": ["T1222", "T1070", "T1655", "T1562", "T1027", "T1564", "T1548"],
    "Execution": ["T1059"],
    "Impact": ["T1489", "T1496"],
    "Persistence": ["T1098", "T1053", "T1547"],
    "Privilege Escalation": ["T1098", "T1053", "T1547", "T1548"],
}
DISCOVERY = TACTICS["Discovery"]
UA = {"User-Agent": "reproduction-study/1.0 (stdlib urllib)"}


# ── download ─────────────────────────────────────────────────────────────────

def download(dest: str, say) -> str:
    if os.path.exists(dest):
        try:
            zipfile.ZipFile(dest).close()
            return "already downloaded"
        except zipfile.BadZipFile:
            os.remove(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=120) as r, open(part, "wb") as fh:
                n = 0
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    fh.write(b)
                    n += len(b)
                    if n % (20 << 20) < (1 << 20):
                        say(f"  downloaded {n / 2**20:.0f} MB")
            zipfile.ZipFile(part).close()
            os.replace(part, dest)
            return "downloaded"
        except (OSError, zipfile.BadZipFile) as e:
            say(f"  attempt {attempt} failed: {type(e).__name__}: {e}")
            time.sleep(5 * attempt)
    raise SystemExit("Download failed 5 times. Check the internet connection and run again.")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_inputs(zpath: str):
    z = zipfile.ZipFile(zpath)
    root = z.namelist()[0].split("/")[0]
    if not root.endswith(COMMIT):
        raise SystemExit(f"zip root {root!r} is not commit {COMMIT}")
    data, hashes = {}, {}
    for kind in ("sessions", "commands"):
        for p in PERIODS:
            name = f"{root}/dataset/{kind}/{p}.jsonl"
            raw = z.read(name)
            hashes[f"dataset/{kind}/{p}.jsonl"] = sha256_bytes(raw)
            data[(kind, p)] = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    return data, hashes


# ── definitions (DECISIONS.md) ───────────────────────────────────────────────

def tech_ids(session) -> list[str]:
    """The technique IDs of a session in order, as released (decision 12: IDs as written)."""
    out = []
    for t in session.get("attack_techniques") or []:
        m = TECH_ID.search(str(t))
        if m:
            out.append(m.group(0))
    return out


def key(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def shares(counter: dict) -> dict:
    tot = sum(counter.values())
    return {k: 100.0 * v / tot for k, v in counter.items()} if tot else {}


def session_measures(sessions: list[dict]) -> dict:
    lens = [len(s.get("commands") or []) for s in sessions]
    kinds = collections.OrderedDict()
    for s in sorted(sessions, key=lambda s: str(s.get("session_id"))):
        kinds.setdefault(key(s.get("commands") or []), len(s.get("commands") or []))
    sets = {key(sorted(set(map(str, s.get("commands") or [])))) for s in sessions}
    pat_len, pat_n = {}, collections.Counter()
    for s in sorted(sessions, key=lambda s: str(s.get("session_id"))):
        k = key(s.get("session_pattern"))
        pat_len.setdefault(k, len(s.get("commands") or []))
        pat_n[k] += 1
    return {
        "session_counts": len(sessions),
        "avg_session_length": statistics.fmean(lens) if lens else 0.0,
        "avg_session_length__alt_command_count": statistics.fmean([s.get("command_count", 0) for s in sessions]) if sessions else 0.0,
        "avg_session_length__alt_authors_08_mean_over_patterns": statistics.fmean(pat_len.values()) if pat_len else 0.0,
        "command_count_equals_len_commands": sum(s.get("command_count") == len(s.get("commands") or []) for s in sessions),
        "session_kinds": len(kinds),
        "session_kinds__alt_distinct_command_sets": len(sets),
        "n_session_patterns": len(pat_len),
        "session_pattern_row__info_patterns_shared_by_2plus": sum(1 for v in pat_n.values() if v >= 2),
        "avg_length_per_kind": statistics.fmean(kinds.values()) if kinds else 0.0,
        "avg_length_per_kind__alt_over_patterns": statistics.fmean(pat_len.values()) if pat_len else 0.0,
    }


def technique_measures(sessions: list[dict]) -> dict:
    pres, occ, cmdw = collections.Counter(), collections.Counter(), collections.Counter()
    pairs, pair_pres = collections.Counter(), collections.Counter()
    tac_pres = collections.Counter()
    no_id = 0
    for s in sessions:
        ids = tech_ids(s)
        no_id += len(s.get("attack_techniques") or []) - len(ids)
        for t in set(ids):
            pres[t] += 1
            cmdw[t] += s.get("command_count", len(s.get("commands") or []))
        occ.update(ids)
        ps = list(zip(ids, ids[1:]))
        pairs.update(ps)
        pair_pres.update(set(ps))
        tac_pres.update({tac for tac, members in TACTICS.items() for t in set(ids) if t in members})
    unmapped = sorted(t for t in pres if not any(t in m for m in TACTICS.values()))
    share_p = shares(pres)
    tac_p = shares({k: v for k, v in tac_pres.items() if k in TACTICS})
    tac_sum = {tac: sum(share_p.get(t, 0.0) for t in members) for tac, members in TACTICS.items()}
    disc = [share_p.get(t, 0.0) / 100 for t in DISCOVERY]
    pair_share = shares(pairs)
    ranked = sorted(pair_share.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "technique_share": share_p,
        "technique_share__alt_occurrence": shares(occ),
        "technique_share__alt_command_weighted": shares(cmdw),
        "technique_share__alt_presence_over_sessions": {t: 100.0 * v / len(sessions) for t, v in pres.items()} if sessions else {},
        "tactic_share": tac_p,
        "tactic_share__alt_sum_of_technique_shares": tac_sum,
        "n_techniques": len(pres),
        "techniques": sorted(pres),
        "unmapped_techniques": unmapped,
        "entries_without_an_id": no_id,
        "discovery_std": statistics.pstdev(disc),
        "discovery_std__alt_sample": statistics.stdev(disc),
        "pair_share": {f"{a}->{b}": v for (a, b), v in pair_share.items()},
        "pair_share__alt_session_presence": {f"{a}->{b}": v for (a, b), v in shares(pair_pres).items()},
        "pair_rank": {f"{a}->{b}": r for r, ((a, b), _) in enumerate(ranked, 1)},
        "top10_pairs": [[f"{a}->{b}", round(v, 6)] for (a, b), v in ranked[:10]],
    }


def command_measures(commands: list[dict]) -> dict:
    by_cmd = sorted(commands, key=lambda c: (-int(c.get("frequency") or 0), str(c.get("command"))))
    pat = collections.Counter()
    for c in commands:
        pat[str(c.get("command_pattern"))] += int(c.get("frequency") or 0)
    top_pat = sorted(pat.items(), key=lambda kv: (-kv[1], kv[0]))
    return {"rank1_command": str(by_cmd[0].get("command")) if by_cmd else "",
            "rank1_command_frequency": int(by_cmd[0].get("frequency") or 0) if by_cmd else 0,
            "top5_commands": [[str(c.get("command")), int(c.get("frequency") or 0)] for c in by_cmd[:5]],
            "rank1_command__alt_pattern": top_pat[0][0] if top_pat else ""}


# ── verdicts (DECISIONS.md 16) ───────────────────────────────────────────────

def norm_text(s: str) -> str:
    return re.sub(r"\s*;\s*", ";", re.sub(r"\s+", " ", s.strip()))


def verdict(published: str, ours, tolerance: str):
    if "route B" in tolerance:
        return "NOT ATTEMPTED", None, "route B (stage 2)"
    if ours is None:
        return "NOT ATTEMPTED", None, "no primary definition (DECISIONS.md 8)"
    if tolerance.startswith("exact text"):
        a, b = norm_text(published), norm_text(str(ours))
        return ("MATCH" if a == b else "NO MATCH"), None, ""
    pub = float(published)
    tol = 0.0 if tolerance.startswith("exact") else float(tolerance.replace("+-", ""))
    diff = float(ours) - pub
    eps = 1e-9
    if abs(diff) <= tol + eps:
        v = "MATCH"
    elif tol > 0 and abs(diff) <= 2 * tol + eps:
        v = "CLOSE"
    else:
        v = "NO MATCH"
    return v, diff, ""


def ours_for(tid: str, quantity: str, M: dict):
    """The primary value for one target id, and the alternates to report next to it."""
    parts = tid.split(".")
    period = parts[-1]
    s, t, c = M[period]["sessions"], M[period]["techniques"], M[period]["commands"]
    if parts[0] == "T1":
        return (s["session_counts"], {}) if parts[1] == "sessions" else (None, {})
    if parts[0] == "T5":
        name = parts[1]
        if name == "session_pattern_row":
            return None, {"info: session_pattern values shared by 2+ sessions": s["session_pattern_row__info_patterns_shared_by_2plus"]}
        alts = {k.split("__", 1)[1]: v for k, v in s.items() if k.startswith(name + "__")}
        return s[name], alts
    if parts[0] == "T6":
        tac = parts[1].replace("_", " ")
        return t["tactic_share"].get(tac, 0.0), {"sum_of_technique_shares": t["tactic_share__alt_sum_of_technique_shares"][tac]}
    if parts[0] == "T7":
        tech = parts[1]
        return t["technique_share"].get(tech, 0.0), {
            "occurrence": t["technique_share__alt_occurrence"].get(tech, 0.0),
            "command_weighted": t["technique_share__alt_command_weighted"].get(tech, 0.0),
            "presence_over_sessions": t["technique_share__alt_presence_over_sessions"].get(tech, 0.0)}
    if parts[0] == "S4D":
        if parts[1] == "n_techniques":
            return t["n_techniques"], {}
        return t["discovery_std"], {"sample_std": t["discovery_std__alt_sample"]}
    if parts[0] == "S4B":
        return None, {}
    if parts[0] == "T8":
        pair = re.search(r"pair (\S+->\S+)", quantity).group(1)
        return t["pair_share"].get(pair, 0.0), {"session_presence": t["pair_share__alt_session_presence"].get(pair, 0.0),
                                                "our_rank": t["pair_rank"].get(pair)}
    if parts[0] == "T4":
        return c["rank1_command"], {"most_frequent_pattern": c["rank1_command__alt_pattern"],
                                    "frequency": c["rank1_command_frequency"]}
    raise ValueError(tid)


def fmt(x):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.4f}"
    return str(x)


def paper_internal_checks(targets: list[dict]) -> dict:
    """Checks of the paper against itself; no data used."""
    pub = {r["id"]: r["published"] for r in targets}
    out = {}
    for p in PERIODS:
        disc = [float(pub[f"T7.{t}.{p}"]) / 100 for t in DISCOVERY]
        out[f"discovery_std_from_published_table_vii.{p}"] = {"population": statistics.pstdev(disc),
                                                               "sample": statistics.stdev(disc),
                                                               "published": pub[f"S4D.discovery_std.{p}"]}
        out[f"techniques_with_nonzero_share_in_table_vii.{p}"] = sum(
            float(pub[f"T7.{t}.{p}"]) > 0 for t in {r["id"].split(".")[1] for r in targets if r["id"].startswith("T7.")})
        tsum = {tac: sum(float(pub[f"T7.{t}.{p}"]) for t in m) for tac, m in TACTICS.items()}
        out[f"tactic_share_as_sum_of_published_technique_shares.{p}"] = {k: round(v, 3) for k, v in tsum.items()}
        out[f"sum_of_published_table_vii.{p}"] = round(sum(float(pub[f"T7.{t}.{p}"]) for t in
                                                         {r["id"].split(".")[1] for r in targets if r["id"].startswith("T7.")}), 3)
        out[f"sum_of_published_table_vi.{p}"] = round(sum(float(pub[r["id"]]) for r in targets
                                                        if r["id"].startswith("T6.") and r["id"].endswith(p)), 2)
    return out


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--data-dir", default=os.path.join(HERE, "data"))
    a = ap.parse_args()
    say = lambda s: print(s, flush=True)  # noqa: E731
    zpath = os.path.join(a.data_dir, ZIP_NAME)
    say(f"authors' repository at {COMMIT[:7]}: {download(zpath, say)}")
    data, hashes = read_inputs(zpath)
    hashes = {"zip": sha256_file(zpath), **hashes}
    M = {p: {"sessions": session_measures(data[("sessions", p)]), "techniques": technique_measures(data[("sessions", p)]),
             "commands": command_measures(data[("commands", p)])} for p in PERIODS}
    with open(os.path.join(HERE, "TARGETS.csv"), encoding="utf-8", newline="") as fh:
        targets = list(csv.DictReader(fh))
    rows = []
    for r in targets:
        ours, alts = ours_for(r["id"], r["quantity"], M)
        v, diff, note = verdict(r["published"], ours, r["tolerance"])
        rows.append({**r, "ours": ours, "difference": diff, "verdict": v, "note": note, "alternates": alts})
    count = collections.Counter(x["verdict"] for x in rows)
    prim = [x for x in rows if x["primary"] == "yes"]
    result = {"commit": COMMIT, "inputs_sha256": hashes, "measures": M, "targets": rows,
              "verdict_counts": dict(sorted(count.items())),
              "primary_verdicts": {x["id"]: x["verdict"] for x in prim},
              "paper_internal_checks": paper_internal_checks(targets)}
    os.makedirs(a.out, exist_ok=True)
    rpath = os.path.join(a.out, "results.json")
    with open(rpath, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False, sort_keys=True)
    L = ["| id | quantity | published | ours | difference | verdict |", "|---|---|---|---|---|---|"]
    for x in rows:
        L.append(f"| {x['id']} | {x['quantity']} | {x['published']} | {fmt(x['ours'])} | {fmt(x['difference'])} | {x['verdict']} |")
    tpath = os.path.join(a.out, "REPORT_TABLE.md")
    with open(tpath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(L) + "\n")
    with open(os.path.join(a.out, "HASHES.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"{sha256_file(rpath)}  results.json\n{sha256_file(tpath)}  REPORT_TABLE.md\n")
    rc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE)
    with open(os.path.join(a.out, "ENVIRONMENT.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"made": time.strftime("%Y-%m-%d %H:%M"), "python": sys.version.split()[0],
                   "platform": platform.platform(), "repository_commit": rc.stdout.strip()}, fh, indent=1)
    say(f"\nverdicts: {dict(sorted(count.items()))}")
    say("primary targets: " + ", ".join(f"{k} {v}" for k, v in result["primary_verdicts"].items()))
    say(f"written: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
