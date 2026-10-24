# -*- coding: utf-8 -*-
"""Verification pass: settle what the audit asserted without enough evidence.

The audit (audit_camlds.py) inventoried the release and read one of everything.
Three of its conclusions went beyond what it had measured, and this script
replaces each with a real check.

  V1  INTEGRITY. File presence is not integrity. Fetch the MD5 Zenodo publishes
      for every file in the record and compare it against the bytes on disk.

  V2  SEQUENCE EQUIVALENCE. The audit compared TOTALS (904 vs 889 steps,
      1,351 vs 1,347 labels) and called that agreement. Totals can match while
      sequences differ completely. This compares PER RUN and PER STEP: run
      coverage, step counts, and the ordered technique sequence, reporting the
      first divergence in each run.

  V3  THE 21 MISSING STEPS. steps/ held 883 (scenario, step) pairs against 904
      label rows. Name the specific missing ones instead of assuming anything
      about them.

  V4  attackmate SCHEMA ACROSS ALL RUNS. The audit read one file from one
      scenario and generalised. This reads every run, unions the keys, and
      looks explicitly for any field that could carry a technique label or an
      execution status.

  V5  UNTRIED ZONE EVIDENCE. Zone derivation from log PRESENCE failed. Before
      concluding anything stronger, check the sources that were never opened:
      attacker/facts.json, the techniques/ grouping, and per-host log VOLUME
      (the objective should attract more logging than a host that merely
      resolved a DNS name).

Read-only except for the report. Nothing is extracted. Network is used only by
V1, and only to read checksum metadata; pass --offline to skip it.

Usage
-----
    python camlds_real/verify_camlds.py --data "<dir with the zips>"
    python camlds_real/verify_camlds.py --data "<dir>" --offline
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import os
import re
import sys
import urllib.request
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ZENODO_RECORDS = ("18861762", "18390561")  # v2 then v1
UA = {"User-Agent": "temarl-verify/1.0"}
RULE = "=" * 78
out: list[str] = []


def say(s: str = "") -> None:
    print(s)
    out.append(s)


def head(s: str) -> None:
    say("")
    say(RULE)
    say(s)
    say(RULE)


def canonical(b: str) -> str:
    m = re.match(r"^(?P<s>.+?)\s*\(\d+\)(?P<e>\.[A-Za-z0-9]+)$", b)
    return f"{m.group('s')}{m.group('e')}" if m else b


def find_zips(data_dir: str) -> dict[str, str]:
    d: dict[str, str] = {}
    for root, _, files in os.walk(data_dir):
        for fn in files:
            if fn.lower().endswith(".zip"):
                d.setdefault(canonical(fn), os.path.join(root, fn))
    return d


# ── V1 ─ integrity ──────────────────────────────────────────────────────────

def v1_integrity(found: dict[str, str], offline: bool) -> None:
    head("V1  INTEGRITY — published MD5 vs the bytes on disk")
    if offline:
        say("  --offline: skipped. Re-run without it to verify.")
        return

    published: dict[str, tuple[str, int]] = {}
    for rid in ZENODO_RECORDS:
        try:
            req = urllib.request.Request(
                f"https://zenodo.org/api/records/{rid}", headers=UA)
            rec = json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:  # noqa: BLE001
            say(f"  could not read record {rid}: {e}")
            continue
        for f in rec.get("files", []):
            key = f.get("key")
            cks = str(f.get("checksum", ""))
            if key and key not in published:
                published[key] = (cks.split(":")[-1], int(f.get("size", 0)))
        if published:
            say(f"  checksums from Zenodo record {rid} ({len(published)} files)")
            break

    if not published:
        say("  !! no checksum metadata retrieved — cannot verify.")
        return

    ok = bad = missing = 0
    say("")
    for name in sorted(found):
        if name not in published:
            if name.startswith("attack-manifestations"):
                say(f"  {name:<46} (GitHub zip, not in the Zenodo record)")
            else:
                say(f"  {name:<46} NOT IN RECORD")
                missing += 1
            continue
        want, wsize = published[name]
        path = found[name]
        gsize = os.path.getsize(path)
        d = hashlib.md5()  # noqa: S324 - matching Zenodo's published algorithm
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 22), b""):
                d.update(chunk)
        got = d.hexdigest()
        if got == want and gsize == wsize:
            ok += 1
        else:
            bad += 1
            say(f"  {name:<46} MISMATCH")
            say(f"      size  disk {gsize}  published {wsize}")
            say(f"      md5   disk {got}")
            say(f"            published {want}")
    say("")
    say(f"  verified OK : {ok}")
    say(f"  MISMATCHED  : {bad}")
    say(f"  not in record: {missing}")
    if bad:
        say("  !! Re-download any mismatched archive before using it.")
    else:
        say("  All archives present in the record match their published MD5.")


# ── V2 ─ sequence equivalence, per run and per step ─────────────────────────

def techs_of(cell: str) -> list[str]:
    return [x for x in cell.replace("_T", "|T").split("|") if re.match(r"^T\d{4}", x)]


def load_released(repo: str, data_dir: str) -> list[dict] | None:
    for cand in (os.path.join(repo, "camlds_real", "attack_times.csv"),
                 os.path.join(data_dir, "attack_times.csv")):
        if os.path.isfile(cand):
            return list(csv.DictReader(
                open(cand, encoding="utf-8", errors="replace").read().splitlines(),
                delimiter=";"))
    for name, p in find_zips(data_dir).items():
        try:
            with zipfile.ZipFile(p) as z:
                hit = next((n for n in z.namelist()
                            if n.endswith("attack_times.csv")), None)
                if hit:
                    return list(csv.DictReader(
                        z.read(hit).decode("utf-8", "replace").splitlines(),
                        delimiter=";"))
        except Exception:  # noqa: BLE001, S112
            continue
    return None


def v2_sequences(repo: str, data_dir: str) -> None:
    head("V2  SEQUENCE EQUIVALENCE — per run and per step, not totals")
    say("  The audit compared totals and called it agreement. Totals can match")
    say("  while sequences differ completely. This compares the actual content.")
    say("")

    rel = load_released(repo, data_dir)
    if not rel:
        say("  !! attack_times.csv not found.")
        return

    gp = None
    for cand in ("thesis_system/data/camlds_grounding_verified.json",
                 "Temarl_Test_v1_L1/thesis_system/data/camlds_grounding_verified.json"):
        p = os.path.join(repo, cand)
        if os.path.isfile(p):
            gp = p
            break
    if not gp:
        say("  !! camlds_grounding_verified.json not found — cannot compare.")
        return
    ours = json.load(open(gp, encoding="utf-8"))
    say(f"  ours    : {os.path.relpath(gp, repo)}")
    say(f"  released: attack_times.csv ({len(rel)} rows)")
    say("")

    # released: scenario -> ordered technique lists, by event_id
    rel_runs: dict[str, list[tuple[int, list[str]]]] = collections.defaultdict(list)
    for r in rel:
        rel_runs[r["scenario"]].append((int(r["event_id"]), techs_of(r["techniques"])))
    for k in rel_runs:
        rel_runs[k].sort()

    our_runs: dict[str, list[str]] = {}
    for fn, meta in (ours.get("runs") or {}).items():
        if isinstance(meta, dict):
            seq = (meta.get("sequence") or meta.get("techniques")
                   or meta.get("technique_sequence") or [])
            if seq:
                our_runs[fn] = [str(x) for x in seq]
    if not our_runs:
        say("  !! no per-run technique sequences in our file. Keys on first run:")
        first = next(iter((ours.get("runs") or {}).values()), {})
        say(f"     {sorted(first.keys()) if isinstance(first, dict) else type(first)}")
        return

    # Our playbooks are named scenario_1_a_a.j2; the release names variants
    # 1_autostart_localaccount. Mapping letters to variant names would be a
    # GUESS, so runs are aligned by CONTENT: each released run is matched to the
    # of ours with the highest sequence overlap, and the score is reported.
    say(f"  our runs: {len(our_runs)}   released runs: {len(rel_runs)}")
    say("  Names do not correspond (ours: scenario_1_a_a.j2, release:")
    say("  1_autostart_localaccount), so alignment is by CONTENT, not by name.")
    say("")

    rel_flat: dict[str, list[str]] = {}
    for rk, steps in rel_runs.items():
        f: list[str] = []
        for _, ts in steps:
            f.extend(ts)
        rel_flat[rk] = f

    def jacc(a: list[str], b: list[str]) -> float:
        sa, sb = set(a), set(b)
        return len(sa & sb) / len(sa | sb) if (sa | sb) else 0.0

    used: set[str] = set()
    exact = 0
    say(f"  {'released run':<30} {'rel':>4} {'ours':>5} {'J':>5}  "
        f"{'verdict':<11} best-matching playbook")
    for rk in sorted(rel_flat):
        rseq = rel_flat[rk]
        best, bj = None, -1.0
        for ok, oseq in our_runs.items():
            j = jacc(rseq, oseq)
            if j > bj:
                best, bj = ok, j
        oseq = our_runs[best] if best else []
        same = rseq == oseq
        exact += same
        if best:
            used.add(best)
        verdict = "IDENTICAL" if same else ("same set" if bj == 1.0 else "differs")
        say(f"  {rk:<30} {len(rseq):>4} {len(oseq):>5} {bj:>5.2f}  "
            f"{verdict:<11} {best}")
    say("")
    unused = sorted(set(our_runs) - used)
    say(f"  >> {exact} of {len(rel_flat)} released runs are ORDER-IDENTICAL to a")
    say("     playbook of ours. 'J' is set overlap: J=1.00 with verdict 'same set'")
    say("     means identical techniques in a DIFFERENT order or multiplicity.")
    say("")
    say(f"  >> our playbooks never chosen as a best match ({len(unused)}): "
        f"{', '.join(unused) if unused else 'none'}")
    say("     With 36 ours against 34 released, at least 2 must be unmatched.")
    say("     These are the candidates for the 36-vs-34 discrepancy.")
    say("")
    say("  This per-run comparison, NOT the agreement of totals, is what the")
    say("  claim 'our corpus matches the published ground truth' has to rest on.")


# ── V3 ─ which steps are missing from steps/ ────────────────────────────────

def v3_missing(found: dict[str, str], repo: str, data_dir: str) -> None:
    head("V3  THE MISSING STEPS — name them")
    mf = found.get("manifestations_filtered.zip")
    rel = load_released(repo, data_dir)
    if not mf or not rel:
        say("  !! need manifestations_filtered.zip and attack_times.csv.")
        return
    pat = re.compile(r"^manifestations_filtered/steps/([^/]+?)-(\d+)/")
    have: set[tuple[str, int]] = set()
    with zipfile.ZipFile(mf) as z:
        for n in z.namelist():
            m = pat.match(n)
            if m:
                have.add((m.group(1), int(m.group(2))))
    want = {(r["scenario"], int(r["event_id"])) for r in rel}
    miss = sorted(want - have)
    extra = sorted(have - want)
    say(f"  label rows            : {len(want)}")
    say(f"  steps/ folders        : {len(have)}")
    say(f"  labelled, NO folder   : {len(miss)}")
    say(f"  folder, NO label row  : {len(extra)}")
    say("")
    if miss:
        bysc = collections.Counter(s for s, _ in miss)
        say(f"  missing by scenario: {dict(sorted(bysc.items()))}")
        say("")
        info = {(r["scenario"], int(r["event_id"])): r for r in rel}
        say(f"  {'scenario':<30} {'step':>4}  {'techniques':<22} cmd")
        for s, e in miss[:40]:
            r = info[(s, e)]
            say(f"  {s:<30} {e:>4}  {r['techniques'][:22]:<22} {r['cmd'][:48]}")
        if len(miss) > 40:
            say(f"  ... and {len(miss) - 40} more")
        say("")
        say("  >> These steps ARE labelled and DID run. They produced no log that")
        say("     survived the authors' filtering, which is a statement about")
        say("     OBSERVABILITY, not about whether the attack happened. Keep them")
        say("     in the sequence; drop them only with a stated reason.")
    if extra:
        say(f"\n  folders with no label row: {extra[:20]}")


# ── V4 ─ attackmate schema across every run ─────────────────────────────────

def v4_attackmate(found: dict[str, str]) -> None:
    head("V4  attackmate SCHEMA — every run, not one")
    scen = sorted(n for n in found
                  if n.startswith("scenario_") and "_pcaps" not in n)
    if not scen:
        say("  !! no scenario archives.")
        return

    keys = collections.Counter()
    types = collections.Counter()
    param_keys = collections.Counter()
    recs_per = {}
    label_like: set[str] = set()
    status_like: set[str] = set()
    LABEL = re.compile(r"techniq|tactic|mitre|att.?ck|label", re.I)
    STATUS = re.compile(r"exit|status|returncode|rc|success|fail|result|stderr|stdout",
                        re.I)

    for name in scen:
        try:
            with zipfile.ZipFile(found[name]) as z:
                t = next((n for n in z.namelist()
                          if n.endswith("attacker/logs/attackmate.json")), None)
                if not t:
                    recs_per[name] = -1
                    continue
                txt = z.read(t).decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            say(f"  {name}: unreadable ({e})")
            continue
        try:
            obj = json.loads(txt)
            recs = obj if isinstance(obj, list) else [obj]
        except json.JSONDecodeError:
            recs = []
            for line in txt.splitlines():
                line = line.strip()
                if line:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        recs_per[name] = len(recs)
        for r in recs:
            if not isinstance(r, dict):
                continue
            for k in r:
                keys[k] += 1
                if LABEL.search(k):
                    label_like.add(k)
                if STATUS.search(k):
                    status_like.add(k)
            if isinstance(r.get("type"), str):
                types[r["type"]] += 1
            p = r.get("parameters")
            if isinstance(p, dict):
                for k in p:
                    param_keys[k] += 1
                    if LABEL.search(k):
                        label_like.add(f"parameters.{k}")
                    if STATUS.search(k):
                        status_like.add(f"parameters.{k}")

    total = sum(v for v in recs_per.values() if v > 0)
    say(f"  runs read: {sum(1 for v in recs_per.values() if v >= 0)} / {len(scen)}")
    say(f"  total records across all runs: {total}")
    say("")
    say("  top-level keys (count across all records):")
    for k, c in keys.most_common(20):
        say(f"      {k:<28} {c}")
    say("")
    say("  `type` values:")
    for k, c in types.most_common(15):
        say(f"      {k:<28} {c}")
    say("")
    say("  parameters.* keys:")
    for k, c in param_keys.most_common(25):
        say(f"      {k:<28} {c}")
    say("")
    say(f"  fields that could be a TECHNIQUE LABEL : "
        f"{sorted(label_like) if label_like else 'NONE'}")
    say(f"  fields that could be EXECUTION STATUS  : "
        f"{sorted(status_like) if status_like else 'NONE'}")
    say("")
    if not label_like:
        say("  >> Confirmed across every run: attackmate.json carries no technique")
        say("     label. attack_times.csv stays the label source.")
    if not status_like:
        say("  >> And no outcome field. `parameters` holds playbook CONFIGURATION")
        say("     written before the run, so failures and retries are NOT recorded")
        say("     here. The audit's earlier claim that they were is withdrawn.")
    else:
        say("  >> A status-like field EXISTS. Inspect it: if it records outcomes,")
        say("     failed steps can be handled explicitly after all.")
    say("")
    say(f"  {'run':<40} records")
    for n in scen[:40]:
        say(f"  {n:<40} {recs_per.get(n, '?')}")


# ── V5 ─ zone evidence that was never opened ────────────────────────────────

def v5_zone_evidence(found: dict[str, str]) -> None:
    head("V5  ZONE EVIDENCE NOT YET TRIED")
    say("  Derivation from log PRESENCE failed (2 of 7). That rules out one")
    say("  heuristic, not every route. These sources were never opened.")
    say("")

    scen = sorted(n for n in found
                  if n.startswith("scenario_") and "_pcaps" not in n)
    if scen:
        name = scen[0]
        say(f"  (a) attacker/facts.json  — from {name}")
        try:
            with zipfile.ZipFile(found[name]) as z:
                t = next((n for n in z.namelist()
                          if n.endswith("attacker/facts.json")), None)
                if t:
                    raw = z.read(t).decode("utf-8", "replace")
                    say(f"      {len(raw)} bytes")
                    try:
                        o = json.loads(raw)
                        if isinstance(o, dict):
                            say(f"      keys: {sorted(o)[:30]}")
                            for k in sorted(o)[:12]:
                                say(f"        {k} = {str(o[k])[:90]}")
                    except json.JSONDecodeError:
                        say(f"      not JSON. head: {raw[:300]}")
                else:
                    say("      not present")
        except Exception as e:  # noqa: BLE001
            say(f"      unreadable: {e}")
    say("")

    mf = found.get("manifestations_filtered.zip")
    if mf:
        say("  (b) per-host log VOLUME per run — the objective should attract more")
        say("      logging than a host that merely resolved a DNS name.")
        pat = re.compile(r"^manifestations_filtered/steps/([^/]+?)-(\d+)/([^/]+)/")
        vol: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter)
        with zipfile.ZipFile(mf) as z:
            for i in z.infolist():
                m = pat.match(i.filename)
                if m and not i.filename.endswith("/"):
                    vol[m.group(1)][m.group(3)] += i.file_size
        say("")
        say(f"      {'run':<30} hosts by log bytes (top 4)")
        for run in sorted(vol)[:40]:
            top = vol[run].most_common(4)
            s = "  ".join(f"{h}:{b / 1e3:.0f}KB" for h, b in top)
            say(f"      {run:<30} {s}")
        say("")
        say("      >> Compare the heaviest NON-infrastructure host against the")
        say("         hand-typed target_host. If they agree, volume is the better")
        say("         signal and the zones become source-supported after all.")

        say("")
        say("  (c) the techniques/ grouping — never inspected; it may key steps to")
        say("      techniques directly, which presence-ordering does not.")
        pat2 = re.compile(r"^manifestations_filtered/techniques/([^/]+)/")
        with zipfile.ZipFile(mf) as z:
            names = collections.Counter(
                m.group(1) for m in (pat2.match(n) for n in z.namelist()) if m)
        say(f"      {len(names)} distinct technique-group folders; first 20:")
        say(f"      {sorted(names)[:20]}")
    say("")
    say("  (d) NOT machine-checkable here: the CAM-LDS paper's own scenario")
    say("      descriptions (Sec 3.4, Figs 5-11) are where the hand-typed zones")
    say("      came from. 'Source-supported' via the paper is achievable even")
    say("      though 'derivable from logs alone' is not.")


def main() -> int:
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", required=True)
    ap.add_argument("--repo", default=os.path.dirname(here))
    ap.add_argument("--offline", action="store_true",
                    help="skip the Zenodo checksum fetch in V1")
    ap.add_argument("--out", default=os.path.join(here, "VERIFY_REPORT.md"))
    a = ap.parse_args()

    say("CAM-LDS verification pass")
    say(f"  data : {os.path.abspath(a.data)}")
    say(f"  repo : {os.path.abspath(a.repo)}")
    found = find_zips(a.data)
    say(f"  {len(found)} distinct archives")

    v1_integrity(found, a.offline)
    v2_sequences(a.repo, a.data)
    v3_missing(found, a.repo, a.data)
    v4_attackmate(found)
    v5_zone_evidence(found)

    head("WHAT THIS SETTLES")
    say("  V1 whether the download is intact, by published MD5.")
    say("  V2 whether our corpus matches the release in CONTENT, not just totals.")
    say("  V3 exactly which labelled steps produced no filtered log.")
    say("  V4 whether attackmate.json carries labels or status in ANY run.")
    say("  V5 whether zones are recoverable by a route other than log presence.")

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("```\n" + "\n".join(out) + "\n```\n")
    print(f"\nreport written to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
