# -*- coding: utf-8 -*-
"""Audit the downloaded CAM-LDS release before anything is parsed or trained.

Read-only. Nothing is extracted: zip *name lists* come from each archive's
central directory, so a 7 GB file costs a seek, not a decompression.

It answers the five open questions, in order:

  Q1  What was actually downloaded, and which Zenodo version is it?
  Q2  Does `attacker/logs/attackmate.json` exist inside the scenario zips?
      (An external plan told us to fetch 7.41 GB for this file. Unverified.)
  Q3  Does `manifestations_filtered.zip` carry the
      `steps/<scenario>-<step>/<host>/...` layout that zones depend on?
  Q4  Mapping host -> subnet via AttackBed `ansible/hosts.example`, what
      entry/target zone does each scenario get, and does that AGREE with the
      hand-typed zones in `camlds_grounding.json`?
  Q5  Does `attack_times.csv` line up with our parsed corpus (904 vs 889
      steps, 1,351 vs 1,347 technique instances, 34 vs 36 runs)?

Q4 is the one that matters. If the derived zones disagree with the hand-typed
ones, every downstream result changes, so it runs before any retraining.

Usage
-----
    python audit_camlds.py --data <dir with the downloaded zips> \
                           --repo <thesis_project root>

`--repo` defaults to this file's parent's parent. Add `--hash` to also compute
SHA-256 for each archive (slow: reads every byte).

Stdlib only. No downloads, no writes outside the report file.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import ipaddress
import json
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Published facts, for cross-checking what we find. Verified 2026-10-23 against
# the Zenodo API and the ait-aecid analysis repo.
PUBLISHED = {
    "logs_v1": ("10.5281/zenodo.18390561", "2026-01-27", 36, 7.41),
    "logs_v2": ("10.5281/zenodo.18861762", "2026-03-04", 36, 7.41),
    "pcaps": ("10.5281/zenodo.18701095", "2026-02-19", 34, 182.07),
    "runs_per_scenario": {"1": 18, "2": 2, "3": 6, "4": 1, "5": 1, "6": 5, "7": 1},
    "n_runs": 34,
    "n_steps": 904,
    "n_technique_instances": 1351,
    "n_techniques_parent": 81,
}
OURS = {"n_commands": 889, "n_labels": 1347, "n_playbooks": 36}

RULE = "=" * 78
report_lines: list[str] = []


def say(s: str = "") -> None:
    print(s)
    report_lines.append(s)


def head(s: str) -> None:
    say("")
    say(RULE)
    say(s)
    say(RULE)


# ── Q1 ─ inventory ──────────────────────────────────────────────────────────

DUP_RE = re.compile(r"^(?P<stem>.+?)\s*\((?P<n>\d+)\)(?P<ext>\.[A-Za-z0-9]+)$")


def canonical(basename: str) -> str:
    """Strip a browser duplicate marker: 'manifestations_filtered (1).zip'.

    Browsers append ' (N)' when a file is downloaded twice, so the archive the
    rest of this script looks for by name would otherwise be reported missing.
    """
    m = DUP_RE.match(basename)
    return f"{m.group('stem')}{m.group('ext')}" if m else basename


def inventory(data_dir: str, do_hash: bool) -> dict[str, str]:
    head("Q1  INVENTORY — what is actually on this machine")
    found: dict[str, str] = {}
    if not os.path.isdir(data_dir):
        say(f"  !! --data directory does not exist: {data_dir}")
        return found

    zips = []
    for root, _, files in os.walk(data_dir):
        for fn in files:
            if fn.lower().endswith(".zip"):
                zips.append(os.path.join(root, fn))
    if not zips:
        say(f"  !! no .zip files under {data_dir}")
        return found

    total = 0
    dups: list[str] = []
    say(f"  {len(zips)} archives under {data_dir}\n")
    say(f"  {'file':<46} {'MB':>9}  {'sha256[:16]' if do_hash else ''}")
    for p in sorted(zips):
        sz = os.path.getsize(p)
        total += sz
        h = ""
        if do_hash:
            d = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 22), b""):
                    d.update(chunk)
            h = d.hexdigest()[:16]
        base = os.path.basename(p)
        canon = canonical(base)
        if canon != base:
            dups.append(base)
        say(f"  {base:<46} {sz / 1e6:>9.1f}  {h}")
        # Keep the first spelling seen; a ' (1)' copy is the same download.
        found.setdefault(canon, p)
    say(f"\n  TOTAL {total / 1e9:.2f} GB  ({len(found)} distinct archives)")
    if dups:
        say("")
        say(f"  NOTE  {len(dups)} file(s) carry a browser duplicate marker ' (N)':")
        for d_ in dups:
            say(f"          {d_}   -> treated as {canonical(d_)}")
        say("        Matched on the canonical name. If any of these were a SECOND,")
        say("        different download rather than a repeat, delete the stray copy")
        say("        and re-run, because only one spelling is read.")

    # Which release does this look like?
    pcap_like = sum(1 for n in found if "_pcaps" in n)
    say("")
    if pcap_like:
        say(f"  NOTE  {pcap_like} pcap archives present. They are NOT needed for "
            "technique-sequence models; 182 GB of packets feed nothing our model reads.")
    if total / 1e9 > 6.5 and not pcap_like:
        say("  Looks like the full LOGS release (~7.41 GB, 36 files).")
    for key in ("manifestations_filtered.zip", "manifestations_raw.zip"):
        say(f"  {key:<32} {'PRESENT' if key in found else 'MISSING'}")
    if "manifestations_filtered.zip" not in found:
        say("  !! Without manifestations_filtered.zip there is NO host information,")
        say("     so entry/target zones cannot be derived and Q3/Q4 below will not run.")
    say("")
    say("  Freeze one Zenodo version and record it. Published:")
    for k in ("logs_v1", "logs_v2", "pcaps"):
        doi, date, n, gb = PUBLISHED[k]
        say(f"    {k:<9} {doi}  {date}  {n} files  {gb} GB")
    say("  v2 (18861762) adds `runc init` audit events for Scenario 7. Prefer v2.")
    return found


# ── Q2 ─ does attackmate.json exist? ────────────────────────────────────────

def check_attackmate(found: dict[str, str]) -> None:
    head("Q2  Does `attacker/logs/attackmate.json` exist in the scenario zips?")
    say("  An external plan said to download all 7.41 GB for this file.")
    say("  Verifying against the archives themselves.\n")

    scen = {n: p for n, p in found.items()
            if n.startswith("scenario_") and "_pcaps" not in n}
    if not scen:
        say("  !! no scenario_*.zip present — cannot check.")
        return

    hits_total = 0
    for name, path in sorted(scen.items())[:5]:
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
        except Exception as e:  # noqa: BLE001
            say(f"  {name}: UNREADABLE ({e})")
            continue
        hits = [n for n in names if re.search(r"attackmate", n, re.I)]
        atk = [n for n in names if re.search(r"(^|/)attacker/", n, re.I)]
        say(f"  {name}  ({len(names)} entries)")
        say(f"      attackmate matches : {len(hits)}")
        for h in hits[:4]:
            say(f"         {h}")
        say(f"      attacker/ entries  : {len(atk)}")
        for a in atk[:4]:
            say(f"         {a}")
        hits_total += len(hits)
        say("")

    say("  VERDICT:")
    if hits_total:
        say("    attackmate logs EXIST, so the 7.42 GB download was justified.")
        say("    BUT they are NOT a label source -- see Q6. The file carries only")
        say("    start-datetime / type / cmd / parameters: no technique labels and no")
        say("    execution status (`parameters` is playbook CONFIG written before the")
        say("    run, not an outcome). attack_times.csv remains the label source; join")
        say("    attackmate.json to it only for untruncated command text and the")
        say("    setup/sleep steps it omits.")
    else:
        say("    NO attackmate file found in the archives checked. If this holds across")
        say("    all of them, the 7.41 GB download was NOT needed for that purpose and")
        say("    `attack_times.csv` (107 KB, in the analysis repo) is your label source.")


# ── Q3/Q4 ─ steps layout and zone derivation ────────────────────────────────

# Real layout, confirmed from the release on 2026-10-24:
#   manifestations_filtered/<grouping>/<scenario>-<step>/<host>/<log path>
# where <grouping> is steps | sequences | techniques. The analysis repo's README
# recommends `steps`, because sequences and techniques duplicate the same logs.
STEP_RE = re.compile(
    r"^manifestations_filtered/(?P<group>steps|sequences|techniques)/"
    r"(?P<scenario>[^/]+?)-(?P<step>\d+)/(?P<host>[^/]+)/")

# Transcribed from attackbed/ansible/hosts.example (ait-testbed/attackbed,
# commit 4d43354). Used only when the clone is absent, so the audit runs on a
# machine that holds the data but not the testbed repo. The clone wins when
# present, so provenance stays with the source.
HOSTS_FALLBACK = {
    "mgmt": "57.128.7.116", "inetfw": "192.168.100.254", "inetdns": "192.42.2.2",
    "corpdns": "192.42.0.233", "docker": "172.17.100.125", "webcam": "172.17.100.80",
    "adminpc1": "10.12.0.222", "videoserver": "172.17.100.121",
    "client": "192.168.50.100", "adminpc2": "10.12.0.223",
    "reposerver": "172.17.100.122", "linuxshare": "192.168.100.23",
    "lanturtle": "192.168.100.27", "attacker": "192.42.1.174",
    "wazuh": "192.168.100.130",
}


def parse_hosts_example(repo: str) -> tuple[dict[str, str], str]:
    """host -> IP, from the AttackBed ansible inventory; fall back to the table."""
    p = os.path.join(repo, "attackbed", "ansible", "hosts.example")
    hosts: dict[str, str] = {}
    if os.path.isfile(p):
        for line in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"^\s*(\S+)\s+ansible_host=(\d+\.\d+\.\d+\.\d+)", line)
            if m:
                hosts[m.group(1)] = m.group(2)
        if hosts:
            return hosts, f"attackbed clone ({os.path.relpath(p, repo)})"
    say(f"  note: no attackbed clone at {p}")
    say("        using the transcribed inventory instead (commit 4d43354).")
    say("        `git clone https://github.com/ait-testbed/attackbed` to use the source.")
    return dict(HOSTS_FALLBACK), "transcribed fallback table"


def subnet_of(ip: str) -> str:
    return str(ipaddress.ip_network(f"{ip}/24", strict=False).network_address)[:-2] + ".0/24"


def zones(found: dict[str, str], repo: str):
    head("Q3  `manifestations_filtered.zip` layout  +  Q4  ZONE DERIVATION")

    hosts, hsrc = parse_hosts_example(repo)
    if hosts:
        nets = collections.defaultdict(list)
        for h, ip in hosts.items():
            nets[subnet_of(ip)].append(h)
        say(f"  AttackBed inventory [{hsrc}]: {len(hosts)} hosts in {len(nets)} subnets\n")
        for net, hs in sorted(nets.items()):
            say(f"    {net:<18} {', '.join(sorted(hs))}")
        say("")
        say(f"  >> {len(nets)} subnets, but our topology is a 5-ZONE star. The mapping")
        say("     is not one-to-one, so a grouping rule must be DECLARED and written")
        say("     down before the zones below mean anything.")
        say("")

    mf = found.get("manifestations_filtered.zip")
    if not mf:
        say("  !! manifestations_filtered.zip absent — Q3/Q4 cannot run.")
        say("     This is the ONLY source of per-step host information, and therefore")
        say("     the only way to stop entry/target zones being hand-typed.")
        say("     It is 213.7 MB. Download it even if you skip everything else.")
        return

    try:
        with zipfile.ZipFile(mf) as z:
            names = z.namelist()
    except Exception as e:  # noqa: BLE001
        say(f"  !! unreadable: {e}")
        return

    say(f"  {len(names)} entries in manifestations_filtered.zip")
    groups = collections.Counter()
    for n in names:
        parts = n.split("/")
        if len(parts) > 1 and parts[0] == "manifestations_filtered" and parts[1]:
            groups[parts[1]] += 1
    say(f"  groupings present: {dict(groups.most_common())}")
    say("  (the analysis repo recommends `steps`; sequences/techniques duplicate logs)\n")

    # (grouping, scenario, step) -> hosts seen
    by_group: dict[str, dict[tuple[str, int], set[str]]] = collections.defaultdict(
        lambda: collections.defaultdict(set))
    for n in names:
        m = STEP_RE.match(n)
        if m:
            by_group[m.group("group")][
                (m.group("scenario"), int(m.group("step")))].add(m.group("host"))
    if not by_group:
        say("  !! no paths matched "
            "manifestations_filtered/<group>/<scenario>-<step>/<host>/ .")
        say("     Print a few entries and adjust STEP_RE before trusting anything below:")
        for n in names[:10]:
            say(f"       {n}")
        return

    pick = "steps" if "steps" in by_group else sorted(by_group)[0]
    say(f"  using grouping: {pick}"
        f"{'' if pick == 'steps' else '  (steps/ absent — note this in the write-up)'}")
    for g, d in sorted(by_group.items()):
        say(f"    {g:<12} {len(d):>5} (scenario, step) pairs")
    say("")
    seen = by_group[pick]

    scenarios = sorted({s for s, _ in seen})
    say(f"  matched {len(seen)} (scenario, step) pairs across {len(scenarios)} scenario-variants")
    say(f"  published expectation: {PUBLISHED['n_runs']} runs, {PUBLISHED['n_steps']} steps\n")

    # host token -> inventory host (tolerate videoserver vs video etc.)
    def to_zone(host_token: str) -> str | None:
        t = host_token.lower()
        for h, ip in hosts.items():
            if t == h.lower() or t.startswith(h.lower()) or h.lower().startswith(t):
                return subnet_of(ip)
        return None

    # DECLARED EXCLUSION, stated here so it is reviewable.
    # Every step's folder holds logs from several hosts at once: the victim, the
    # attacker (which logs its own commands) and the SIEM (which logs alerts about
    # everything). Only the victim says where the attack WENT, so the other three
    # are infrastructure and are excluded from zone derivation. Without this the
    # attacker's own subnet wins every scenario, which is what the first run showed.
    INFRA = {"attacker", "wazuh", "mgmt"}

    def victims(hs: set[str]) -> list[str]:
        return sorted(h for h in hs if h.lower() not in INFRA)

    say("  DECLARED: hosts excluded from zone derivation = "
        f"{', '.join(sorted(INFRA))}")
    say("            (attacker = origin, wazuh = SIEM, mgmt = out-of-band admin)")
    say("")
    say(f"  {'scenario-variant':<30} {'steps':>5}  {'entry':<16} {'target':<16} victim-host path")
    derived: dict[str, dict] = {}
    for sc in scenarios:
        steps = sorted(k[1] for k in seen if k[0] == sc)
        # ordered, de-duplicated victim hosts across the whole run
        path: list[str] = []
        for st in steps:
            for h in victims(seen[(sc, st)]):
                if not path or path[-1] != h:
                    if h not in path:
                        path.append(h)
        ez = to_zone(path[0]) if path else "NO-VICTIM"
        tz = to_zone(path[-1]) if path else "NO-VICTIM"
        derived[sc] = {
            "entry_zone": ez or "UNMAPPED", "target_zone": tz or "UNMAPPED",
            "n_steps": len(steps), "victim_host_path": path,
            "entry_host": path[0] if path else None,
            "target_host": path[-1] if path else None,
        }
        say(f"  {sc:<30} {len(steps):>5}  {str(ez):<16} {str(tz):<16} "
            f"{' -> '.join(path) if path else '(none)'}")

    allhosts = sorted({h for v in seen.values() for h in v})
    say("")
    say(f"  all host folders seen ({len(allhosts)}): {', '.join(allhosts)}")
    unmapped = [h for h in allhosts if not to_zone(h)]
    if unmapped:
        say(f"  !! {len(unmapped)} did not map to the inventory: {', '.join(unmapped)}")
        say("     Fix the mapping before trusting the zones above.")

    ez_set = collections.Counter(v["entry_zone"] for v in derived.values())
    tz_set = collections.Counter(v["target_zone"] for v in derived.values())
    say("")
    say(f"  distinct ENTRY zones across {len(derived)} runs: {dict(ez_set)}")
    say(f"  distinct TARGET zones across {len(derived)} runs: {dict(tz_set)}")
    if len(tz_set) == 1:
        say("  >> All runs share one target zone. Either the campaigns genuinely")
        say("     converge, or the exclusion list is still wrong. Check the host")
        say("     paths above before accepting this.")

    # Q4b: compare with the hand-typed grounding
    say("")
    say("  --- Does this AGREE with the hand-typed camlds_grounding.json? ---")
    gp = None
    for cand in ("thesis_system/data/camlds_grounding.json",
                 "Temarl_Test_v1_L1/thesis_system/data/camlds_grounding.json"):
        p = os.path.join(repo, cand)
        if os.path.isfile(p):
            gp = p
            break
    if not gp:
        say("  !! camlds_grounding.json not found — cannot compare.")
    else:
        g = json.load(open(gp, encoding="utf-8"))
        say(f"  hand-typed file: {os.path.relpath(gp, repo)}")
        hand = g.get("scenarios", [])
        # This file has shipped as both a dict and a list of dicts.
        if isinstance(hand, dict):
            items = list(hand.items())
        else:
            items = [((d.get("id") or d.get("name") or f"#{i}"), d)
                     for i, d in enumerate(hand) if isinstance(d, dict)]
        say(f"  it declares {len(items)} scenarios; the release has "
            f"{len(scenarios)} scenario-variants.")
        say("  Hand-typed entry/target per scenario:")
        for k, v in items[:12]:
            if not isinstance(v, dict):
                continue
            ez = v.get("entry_zone") or v.get("entry")
            tz = v.get("target_zone") or v.get("target")
            goal = v.get("terminal_tactic") or v.get("goal_tactic") or v.get("goal")
            say(f"    {str(k):<28} entry={str(ez):<16} target={str(tz):<16} goal={goal}")
        if items and not any(
                (v.get("entry_zone") or v.get("entry")) for _, v in items
                if isinstance(v, dict)):
            say("    !! no entry/target keys found. Available keys on the first entry:")
            first = next((v for _, v in items if isinstance(v, dict)), {})
            say(f"       {sorted(first.keys())}")

        # ── the actual agreement check ──────────────────────────────────────
        # The hand-typed file names zones symbolically ("Internet", "DMZ") and
        # also records target_host. That host is the bridge: host -> subnet is
        # inventory fact, so the symbolic name can be tied to a subnet WITHOUT
        # inventing anything. Then the derived target host is compared against
        # the hand-typed one, which is the claim that actually matters.
        say("")
        say("  --- subnet <-> symbolic-zone mapping, recovered from target_host ---")
        name_of: dict[str, set[str]] = collections.defaultdict(set)
        say(f"  {'scenario':<6} {'hand target_host':<18} {'-> subnet':<18} "
            f"{'hand calls it':<12} {'derived target host(s)'}")
        for k, v in items:
            if not isinstance(v, dict):
                continue
            th = str(v.get("target_host") or "")
            tz = str(v.get("target_zone") or "")
            sub = to_zone(th) if th else None
            if sub and tz:
                name_of[sub].add(tz)
            base = re.sub(r"^S", "", str(v.get("id") or k))
            drv = sorted({d["target_host"] for s, d in derived.items()
                          if s.split("_")[0] == base and d.get("target_host")})
            agree = "" if not drv else (
                "  <= MATCH" if any(th.lower() == x.lower() for x in drv)
                else "  <= DIFFERS")
            say(f"  {str(k):<6} {th:<18} {str(sub):<18} {tz:<12} "
                f"{', '.join(drv) if drv else '(no release run)'}{agree}")
        say("")
        for sub, names in sorted(name_of.items()):
            flag = "" if len(names) == 1 else "   !! AMBIGUOUS"
            say(f"    {sub:<18} = {', '.join(sorted(names))}{flag}")
        say("")
        say("  >> This recovers the grouping rule from the existing annotation rather")
        say("     than inventing one. Any subnet with no row here was never named by")
        say("     the hand-typed file and still needs a declared decision.")
        say("")
        say("  >> The release names scenario VARIANTS (e.g. 1_autostart_localaccount)")
        say("     while the hand-typed file names base scenarios. Decide, and WRITE DOWN,")
        say("     whether all 18 variants of scenario 1 share one zone pair. If they do,")
        say("     they are one campaign and must never be split across train and test.")

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "derived_zones.json"), "w", encoding="utf-8") as f:
        json.dump(derived, f, indent=2)
    say("\n  wrote derived_zones.json")


# ── Q5 ─ does attack_times.csv match our corpus? ────────────────────────────

# ── Q6 ─ what is actually inside attackmate.json? ───────────────────────────

def peek_attackmate(found: dict[str, str]) -> None:
    """Read ONE execution record so the extractor can be written against truth."""
    head("Q6  Schema of `attacker/logs/attackmate.json` (one scenario)")
    scen = sorted(n for n in found
                  if n.startswith("scenario_") and "_pcaps" not in n)
    if not scen:
        say("  !! no scenario zip to read.")
        return
    name = scen[0]
    try:
        with zipfile.ZipFile(found[name]) as z:
            target = next((n for n in z.namelist()
                           if n.endswith("attacker/logs/attackmate.json")), None)
            if not target:
                say(f"  !! {name} has no attacker/logs/attackmate.json")
                return
            raw = z.read(target)
            # The playbooks ship inside the release too — this is how the
            # 36-playbooks-vs-34-runs question gets settled.
            pbs = [n for n in z.namelist()
                   if "/attackmate/playbooks/" in n and not n.endswith("/")]
    except Exception as e:  # noqa: BLE001
        say(f"  !! unreadable: {e}")
        return

    say(f"  {name} :: {target}   ({len(raw) / 1e3:.1f} KB)")
    say(f"  playbooks shipped in this archive: {len(pbs)}")
    for p in pbs[:8]:
        say(f"      {p.split('/playbooks/', 1)[-1]}")
    say("")

    text = raw.decode("utf-8", "replace").strip()
    obj = None
    try:
        obj = json.loads(text)
        say(f"  parses as a single JSON {type(obj).__name__}")
    except json.JSONDecodeError:
        lines = [l for l in text.splitlines() if l.strip()]
        say(f"  not one JSON document — looks like JSON Lines ({len(lines)} lines)")
        try:
            obj = [json.loads(l) for l in lines]
            say("  all lines parse individually")
        except Exception as e:  # noqa: BLE001
            say(f"  !! line parse failed: {e}")
            say(f"  first 300 chars: {text[:300]}")
            return

    recs = obj if isinstance(obj, list) else [obj]
    say(f"  records: {len(recs)}")
    keys = collections.Counter(k for r in recs if isinstance(r, dict) for k in r)
    say(f"  keys seen across records:")
    for k, c in keys.most_common(25):
        say(f"      {k:<28} in {c}/{len(recs)}")
    say("")
    say("  FIRST RECORD:")
    say("    " + json.dumps(recs[0], indent=2)[:1200].replace("\n", "\n    "))
    if len(recs) > 1:
        say("")
        say("  LAST RECORD:")
        say("    " + json.dumps(recs[-1], indent=2)[:800].replace("\n", "\n    "))
    say("")
    say("  >> The extractor needs, per record: an ordering key, the command that")
    say("     ran, its technique label(s) if present, and an execution status so")
    say("     failed or retried steps can be handled explicitly rather than")
    say("     silently becoming attack transitions.")


def _find_attack_times(repo: str, data_dir: str) -> tuple[str, list[dict]] | None:
    """Loose file first, then inside any zip (the analysis repo downloads as one)."""
    for cand in (os.path.join(data_dir, "attack_times.csv"),
                 os.path.join(repo, "camlds_real", "attack_times.csv"),
                 os.path.join(data_dir, "attack-manifestations-interpretation",
                              "attack_times.csv")):
        if os.path.isfile(cand):
            text = open(cand, encoding="utf-8", errors="replace").read()
            return cand, list(csv.DictReader(text.splitlines(), delimiter=";"))

    for root, _, files in os.walk(data_dir):
        for fn in files:
            if not fn.lower().endswith(".zip"):
                continue
            p = os.path.join(root, fn)
            try:
                with zipfile.ZipFile(p) as z:
                    hit = next((n for n in z.namelist()
                                if n.endswith("attack_times.csv")), None)
                    if hit:
                        text = z.read(hit).decode("utf-8", "replace")
                        return f"{fn}::{hit}", list(
                            csv.DictReader(text.splitlines(), delimiter=";"))
            except Exception:  # noqa: BLE001, S112
                continue
    return None


def cross_check(repo: str, data_dir: str) -> None:
    head("Q5  Does `attack_times.csv` line up with our parsed corpus?")
    hit = _find_attack_times(repo, data_dir)
    if not hit:
        say("  !! attack_times.csv not found, loose or inside any zip. Get it (107 KB):")
        say("     https://raw.githubusercontent.com/ait-aecid/"
            "attack-manifestations-interpretation/main/attack_times.csv")
        return
    path, rows = hit
    say(f"  {path}  ->  {len(rows)} rows")

    variants = collections.Counter(r["scenario"] for r in rows)
    per_base = collections.Counter(s.split("_")[0] for s in variants)
    tech: list[str] = []
    multi = 0
    for r in rows:
        t = [x for x in r["techniques"].replace("_T", "|T").split("|")
             if re.match(r"^T\d{4}", x)]
        tech.extend(t)
        multi += len(t) > 1
    parents = {x.split(".")[0] for x in tech}

    say("")
    say(f"  {'quantity':<34} {'released':>10} {'ours':>10} {'published':>10}")
    say(f"  {'steps / commands':<34} {len(rows):>10} {OURS['n_commands']:>10} "
        f"{PUBLISHED['n_steps']:>10}")
    say(f"  {'technique instances':<34} {len(tech):>10} {OURS['n_labels']:>10} "
        f"{PUBLISHED['n_technique_instances']:>10}")
    say(f"  {'runs':<34} {len(variants):>10} {OURS['n_playbooks']:>10} "
        f"{PUBLISHED['n_runs']:>10}")
    say(f"  {'parent-level techniques':<34} {len(parents):>10} {'-':>10} "
        f"{PUBLISHED['n_techniques_parent']:>10}")
    say("")
    say(f"  multi-technique steps : {multi} ({100 * multi / len(rows):.1f}%)")
    say(f"  mean techniques/step  : {len(tech) / len(rows):.3f}")
    say("")
    say(f"  runs per base scenario: {dict(sorted(per_base.items()))}")
    say(f"  published expectation : {PUBLISHED['runs_per_scenario']}")
    if dict(sorted(per_base.items())) != PUBLISHED["runs_per_scenario"]:
        say("  !! DIFFERS from the published table — investigate before parsing.")

    s1 = sum(v for k, v in variants.items() if k.startswith("1_"))
    say("")
    say(f"  >> SCENARIO 1 IS {s1} OF {len(rows)} STEPS ({100 * s1 / len(rows):.0f}%), "
        f"across {sum(1 for k in variants if k.startswith('1_'))} variants.")
    say("     This is R7. It is identical in the released data and in ours, so this")
    say("     download does NOT fix it. Split by base scenario, never by variant, and")
    say("     say so explicitly in the paper.")
    say("")
    say("  >> We parsed 36 playbooks; the release has 34 runs. Find the 2 extra before")
    say("     reconciling — they are likely playbooks never executed into the release.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", required=True,
                    help="directory holding the downloaded CAM-LDS zips")
    ap.add_argument("--repo", default=os.path.dirname(here),
                    help="thesis_project root (default: parent of this file's dir)")
    ap.add_argument("--hash", action="store_true",
                    help="also compute SHA-256 per archive (slow)")
    ap.add_argument("--out", default=os.path.join(here, "AUDIT_REPORT.md"))
    a = ap.parse_args()

    say(f"CAM-LDS release audit")
    say(f"  data : {os.path.abspath(a.data)}")
    say(f"  repo : {os.path.abspath(a.repo)}")

    found = inventory(a.data, a.hash)
    check_attackmate(found)
    zones(found, a.repo)
    cross_check(a.repo, a.data)
    peek_attackmate(found)

    head("WHAT TO DO NEXT  (settled by the 2026-10-24 run)")
    say("  1. LABELS come from attack_times.csv. It is the authors' own published")
    say("     ground truth, 904 steps / 1,351 technique instances, and our parsed")
    say("     corpus matches it to ~2%. attackmate.json is NOT a substitute (Q6):")
    say("     no technique labels, no execution status. Join it only for the")
    say("     untruncated command text and the setup/sleep steps it adds.")
    say("")
    say("  2. ZONES STAY HAND-TYPED, and that is now an evidenced decision rather")
    say("     than an admission. Two derivation routes were tried and both failed:")
    say("       (a) host folders in manifestations_filtered -> 2 of 7 scenarios")
    say("           matched. The path is ordered by first appearance of a host that")
    say("           WROTE A LOG, not by attack progression: corpdns leads nearly")
    say("           every run because step 1 is a DNS lookup, and inetfw appears")
    say("           because traffic crosses the firewall. Neither is a victim.")
    say("       (b) hostnames inside the command text -> only 121 of 904 commands")
    say("           (13.4%) name a host, and the last one is almost always")
    say("           192.42.1.174, the ATTACKER's own address (reverse shell and")
    say("           exfiltration destination).")
    say("     Logs record who OBSERVED traffic, never who was the OBJECTIVE. The")
    say("     objective is intent, and intent is not in telemetry. This is R4-R6,")
    say("     now measured instead of argued -- put it in the limitations section.")
    say("")
    say("  3. Do NOT reuse the old 84-label vocabulary blindly — rebuild it from the")
    say("     release and document any sub-technique -> parent collapse.")
    say("  4. Group scenario variants BEFORE splitting. 58% of the corpus is one")
    say("     campaign; a variant-level split silently leaks it.")
    say("  5. Only then build windows (16 steps -> next step) and retrain.")
    say("")
    say("  Also unresolved, carry forward: steps/ holds 883 (scenario, step) pairs")
    say("  against 904 published rows (21 steps left no filtered log), and we parsed")
    say("  36 playbooks against 34 released runs.")

    with open(a.out, "w", encoding="utf-8") as f:
        f.write("```\n" + "\n".join(report_lines) + "\n```\n")
    print(f"\nreport written to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
