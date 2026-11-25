# -*- coding: utf-8 -*-
"""H-MARL report: TARGETS.csv against out/seeds -> out/results.json, out/HASHES.txt, REPORT.md (standard library)."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
from pathlib import Path

import run as R


def read_csv(path: Path) -> list:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_hashes(out: Path) -> dict:
    files = sorted((p for p in out.rglob("*") if p.is_file() and p.name != "HASHES.txt"),
                   key=lambda p: p.relative_to(out).as_posix())
    h = {p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() for p in files}
    (out / "HASHES.txt").write_bytes("".join(f"{v}  {k}\n" for k, v in h.items()).encode("utf-8"))
    return h


def paper_verdict(rows: list) -> str:
    prim = [r for r in rows if r["primary"] and r["verdict"] != "NOT ATTEMPTED"]
    bad = [r["id"] for r in prim if r["verdict"] != "MATCH"]
    if prim and not bad:
        return "reproduced for the three released methods against Default Red (every attempted primary target MATCH)"
    if prim and all(r["verdict"] == "NO MATCH" for r in prim):
        return "not reproduced"
    return "partially reproduced; attempted primary targets not MATCH: " + ", ".join(bad)


def checklist(checks: list, run_machine, asked: bool) -> list:
    other = sorted({c["machine"] for c in checks if c["identical"] and c["machine"] != run_machine})
    bad = [c for c in checks if not c["identical"]]
    second = (f"**no**: DIFFERENT ({', '.join(c['machine'] for c in bad)})" if bad else
              f"identical on a second machine ({', '.join(other)})" if other else "**second machine not yet**")
    rows = [
        ("targets committed before any result", "yes", "`audit.py` ORDER"),
        ("gaps decided before the run", "yes", "`DECISIONS.md` 1-13"),
        ("authors asked about every gap", "yes" if asked else "**not yet**: the issue is drafted, to be posted by the user",
         "`AUTHOR_CONTACT.md`"),
        ("exact sources and licence", "yes", "`SOURCES.md`; 87 policy and code files pinned (`POLICY_SHA256.txt`)"),
        ("variance: two machines identical, or 10+ seeds with CI",
         "partly: one released policy per method, so no training seeds (DECISIONS 8); 10 evaluation seeds with a 95% CI; "
         + second, "`out/RECHECK_*.json`"),
        ("every target reported", "yes", "table above, `audit.py`"),
        ("environment recorded", "yes", "`out/ENVIRONMENT.json`"),
        ("one command from public inputs, outputs hashed", "yes: a fixed sequence of commands (`README.md`); every "
         "output's SHA-256 in `out/HASHES.txt`", "`fetch.py`, `run.py`"),
        ("unit tests for each rule", "yes: parsing, statistics, verdict rule, target ids, pins", "`tests/test_hmarl.py`"),
        ("comparison only after this report; adaptations declared", "not started", "DECISIONS 1"),
    ]
    return (["## Checklist (STANDARD.md, Section 2)", "", "| # | requirement | met? | where |", "|---|---|---|---|"] +
            [f"| {i} | {a} | {b} | {c} |" for i, (a, b, c) in enumerate(rows, 1)] + [""])


def report(out: Path = R.OUT, dest: Path = R.HERE / "REPORT.md") -> dict:
    data = {m: {} for m in R.METHODS}
    for m in R.METHODS:
        for s in R.SEEDS:
            f = R.seed_file(m, s, out)
            if f.exists():
                data[m][s] = json.loads(f.read_text(encoding="utf-8"))
    missing = [(m, s) for m in R.METHODS for s in R.SEEDS if s not in data[m]]
    if missing:
        raise SystemExit(f"runs not finished: {missing}")
    summ = {m: {k: R.summarise([data[m][s]["metrics"][k] for s in R.SEEDS]) for k in R.METRICS} for m in R.METHODS}
    ep_sd = {m: statistics.stdev([r for s in R.SEEDS for r in data[m][s]["rewards"]]) for m in R.METHODS}
    rows = []
    for t in read_csv(R.HERE / "TARGETS.csv"):
        key = R.target_key(t["id"])
        if key is None or t["tolerance"].upper().startswith("NOT ATTEMPTED"):
            rows.append({"id": t["id"], "table": t["table_or_figure"], "quantity": t["quantity"], "published": t["published"],
                         "ours": None, "ci": None, "primary": t["primary"] == "yes", "verdict": "NOT ATTEMPTED",
                         "reason": t["tolerance"].split(":", 1)[1].strip() if ":" in t["tolerance"] else ""})
            continue
        s = summ[key[0]][key[1]]
        rows.append({"id": t["id"], "table": t["table_or_figure"], "quantity": t["quantity"], "published": t["published"],
                     "ours": s["mean"], "ci": s["ci"], "prediction": s["prediction"], "primary": t["primary"] == "yes",
                     "verdict": R.verdict(s, t["published"], t["tolerance"], R.published_sd(t["quantity"]))})
    checks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(out.glob("RECHECK_*.json"))]
    env = json.loads((out / "ENVIRONMENT.json").read_text(encoding="utf-8")) if (out / "ENVIRONMENT.json").exists() else {}
    verify = json.loads((out / "VERIFY.json").read_text(encoding="utf-8"))
    head = paper_verdict(rows)
    count = {k: sum(r["verdict"] == k for r in rows) for k in ("MATCH", "CLOSE", "NO MATCH", "NOT ATTEMPTED")}
    res = {"paper_verdict": head, "counts": count, "summary": summ, "episode_reward_sd": ep_sd, "targets": rows,
           "rechecks": checks, "verify": verify}
    R.write_json(out / "results.json", res)
    asked = "(draft, not sent)" not in (R.HERE / "AUTHOR_CONTACT.md").read_text(encoding="utf-8")
    t2 = {r["id"].split(".")[1]: r for r in rows if r["id"].startswith("T2.") and ".Default." in r["id"]}
    L = ["# H-MARL (Singh et al., RLJ 2025): reproduction of Tables 2 and 3 from the released policies", "",
         f"**Paper verdict: {head}.**", "",
         f"- Targets: {len(rows)}; " + ", ".join(f"{k} {v}" for k, v in count.items()) + ". Attempted: the three methods "
         "whose trained policies were released, against Default Red (DECISIONS 3); every other cell is NOT ATTEMPTED "
         "with its reason below.",
         "- Each method is one released policy, so the intervals cover evaluation randomness only (DECISIONS 8): 10 seeds "
         "x 100 episodes; CI = t over the 10 seed values; prediction interval = where one 100-episode evaluation (as one "
         "published table entry) is expected to fall.",
         "- The authors' evaluator ran unchanged; with its metrics switch on, it gives the same rewards as their plain "
         "evaluator (`out/VERIFY.json`: " + ", ".join(f"{m} {'PASS' if v['pass'] else 'FAIL'}" for m, v in verify["methods"].items()) + ").",
         "", "## Reward against Default Red (Table 2), per method", "",
         "| method | published mean ± std | ours: mean [95% CI] | our seed values (range) | our episode std | verdict |",
         "|---|---|---|---|---|---|"]
    for m in R.METHODS:
        s, r = summ[m]["reward"], t2[m]
        L.append(f"| {m} | {r['published']} ± {R.published_sd(r['quantity'])} | {s['mean']:.2f} [{s['ci'][0]:.2f}, "
                 f"{s['ci'][1]:.2f}] | {s['range'][0]:.2f} to {s['range'][1]:.2f} | {ep_sd[m]:.2f} | {r['verdict']} |")
    L += ["", "## Every target", "", "| id | table | quantity | published | ours [95% CI] | 95% prediction interval | verdict |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["ours"] is None:
            L.append(f"| {r['id']} | {r['table']} | {r['quantity']} ({r['reason']}) | {r['published']} | - | - | {r['verdict']} |")
        else:
            L.append(f"| {r['id']} | {r['table']} | {r['quantity']}{' (primary)' if r['primary'] else ''} | {r['published']} | "
                     f"{r['ours']:.3f} [{r['ci'][0]:.3f}, {r['ci'][1]:.3f}] | [{r['prediction'][0]:.3f}, {r['prediction'][1]:.3f}] | "
                     f"{r['verdict']} |")
    L += ["", "## Notes", "",
          "- Inconsistency in the paper, found before any run (DECISIONS 11): H-MARL Collective against Default Red is "
          "-237.61 in Table 2 and -255.56 in Table 3. Not attempted (no released policy).",
          "- Red Impact Count is our reading of the paper's definition (DECISIONS 7): per episode, the sum over red agents "
          "of their Impact counts on operational hosts; asked of the authors.", ""]
    L += checklist(checks, env.get("machine"), asked)
    L += ["## Environment", "",
          f"- Python {env.get('python', '?').split()[0]}, {env.get('platform', '?')}, machine {env.get('machine', '?')}; "
          f"commits {env.get('commits', {})}; full package list in `out/ENVIRONMENT.json`.",
          "- Rechecks (kept episodes run again): " + ("; ".join(f"{c['method']} seed {c['seed']} on {c['machine']}: "
                                                             f"{'IDENTICAL' if c['identical'] else 'DIFFERENT'}" for c in checks) or "none yet") + ".",
          "- Every output's SHA-256 (LF line endings): `out/HASHES.txt`; the authors' printed output of every run: `out/logs/`.", ""]
    dest.write_text("\n".join(L), encoding="utf-8")
    write_hashes(out)
    print("\n".join(L[:14]))
    return res
