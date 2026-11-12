# -*- coding: utf-8 -*-
"""Check every reproduction folder against reproductions/STANDARD.md. Reads only.

    python reproductions/audit.py

For each reproductions/<paper>/ it checks what can be checked by a machine:
  files      SOURCES.md, TARGETS.csv, DECISIONS.md, AUTHOR_CONTACT.md, REPORT.md exist and are filled
  targets    every target has an id, a published value and a tolerance; ids are unique; at least
             one target is marked primary
  ORDER      (git history) TARGETS.csv and DECISIONS.md were committed BEFORE the first file in out/,
             and no target was added, removed or changed after that first result
  report     every target id has a row in REPORT.md with a verdict from the fixed list
Writes reproductions/AUDIT.txt. Exit code 1 if any check FAILS.

A folder with no committed out/ is "NOT RUN YET": its ORDER and report checks wait.
"""
from __future__ import annotations

import csv
import io
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"TEMPLATE", "out", "tests", "__pycache__"}
REQUIRED = ("SOURCES.md", "TARGETS.csv", "DECISIONS.md", "AUTHOR_CONTACT.md", "REPORT.md")
HEADER = ["id", "table_or_figure", "quantity", "published", "tolerance", "primary"]
VERDICTS = ("MATCH", "CLOSE", "NO MATCH", "NOT ATTEMPTED")
SOURCE_FIELDS = ("Paper", "Version read", "Code", "Data", "Type", "Stochastic")


def git(root, *args):
    p = subprocess.run(["git", *args], capture_output=True, text=True, cwd=root, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout


def repo_root(path):
    rc, out = git(path, "rev-parse", "--show-toplevel")
    return out.strip() if rc == 0 else None


def rel(repo, path):
    return os.path.relpath(path, repo).replace(os.sep, "/")


def first_commit(repo, relpath):
    """(hash, unix time) of the first commit that touches relpath, or None."""
    rc, out = git(repo, "log", "--reverse", "--format=%H %ct", "--", relpath)
    line = out.strip().splitlines()[0] if rc == 0 and out.strip() else None
    return (line.split()[0], int(line.split()[1])) if line else None


def read_targets(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return rows, (list(rows[0].keys()) if rows else next(csv.reader(io.StringIO(text)), []))


def check_targets(text):
    problems = []
    rows, header = read_targets(text)
    if header != HEADER:
        problems.append(f"TARGETS.csv header must be {','.join(HEADER)}")
        return rows, problems
    if not rows:
        problems.append("TARGETS.csv has no target")
    ids = [r["id"].strip() for r in rows]
    if len(set(ids)) != len(ids) or "" in ids:
        problems.append("TARGETS.csv: ids must be filled and unique")
    for r in rows:
        if not r["published"].strip() or not r["tolerance"].strip():
            problems.append(f"TARGETS.csv: target {r['id']} needs a published value and a tolerance")
    if rows and not any(r["primary"].strip().lower() == "yes" for r in rows):
        problems.append("TARGETS.csv: no target is marked primary (yes)")
    return rows, problems


def source_values(text):
    """field -> value, for lines like '- Field (hint): value'. The colon inside the hint does not count."""
    out = {}
    for line in text.splitlines():
        if not line.startswith("- "):
            continue
        depth, cut = 0, None
        for i, ch in enumerate(line):
            depth += ch == "("
            depth -= ch == ")"
            if ch == ":" and depth == 0:
                cut = i
                break
        if cut is not None:
            label = line[2:cut].split("(")[0].strip()
            out[label] = line[cut + 1:].strip()
    return out


def report_verdicts(text):
    """id -> verdict, from the table rows of REPORT.md."""
    out = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0] and set(cells[0]) != {"-"} and cells[0] != "id":
            out[cells[0]] = cells[5]
    return out


def audit_folder(folder, repo):
    name = os.path.basename(folder)
    fails, waits, passes = [], [], []
    present = {f: os.path.isfile(os.path.join(folder, f)) and os.path.getsize(os.path.join(folder, f)) > 0
               for f in REQUIRED}
    read = lambda f: open(os.path.join(folder, f), encoding="utf-8").read()  # noqa: E731

    first_out = first_commit(repo, rel(repo, os.path.join(folder, "out"))) if repo else None
    ran = first_out is not None
    for f, ok in present.items():
        if ok:
            passes.append(f"{f} present")
        elif f == "REPORT.md" and not ran:
            waits.append("REPORT.md (after the run)")
        else:
            fails.append(f"{f} missing or empty")

    if present["SOURCES.md"]:
        values = source_values(read("SOURCES.md"))
        empty = [k for k in SOURCE_FIELDS if not values.get(k)]
        (fails if empty else passes).append(f"SOURCES.md fields not filled: {', '.join(empty)}" if empty
                                            else "SOURCES.md fields filled")
    rows = []
    if present["TARGETS.csv"]:
        rows, problems = check_targets(read("TARGETS.csv"))
        fails += problems
        if not problems:
            passes.append(f"TARGETS.csv: {len(rows)} targets, {sum(r['primary'].strip().lower() == 'yes' for r in rows)} primary")

    if not ran:
        waits.append("ORDER check (no result committed yet)")
    else:
        h, t_out = first_out
        for f in ("TARGETS.csv", "DECISIONS.md"):
            fc = first_commit(repo, rel(repo, os.path.join(folder, f)))
            if fc is None or fc[1] > t_out or git(repo, "cat-file", "-e", f"{h}^:{rel(repo, os.path.join(folder, f))}")[0] != 0:
                fails.append(f"ORDER: {f} was not committed before the first result ({h[:8]})")
            else:
                passes.append(f"ORDER: {f} committed before the first result")
        rc, old = git(repo, "show", f"{h}^:{rel(repo, os.path.join(folder, 'TARGETS.csv'))}")
        if rc == 0 and present["TARGETS.csv"]:
            key = lambda r: (r["published"].strip(), r["tolerance"].strip(), r["primary"].strip().lower())  # noqa: E731
            before = {r["id"].strip(): key(r) for r in read_targets(old)[0]}
            now = {r["id"].strip(): key(r) for r in rows}
            changed = sorted(set(before) ^ set(now)) + sorted(k for k in set(before) & set(now) if before[k] != now[k])
            (fails if changed else passes).append(
                f"ORDER: targets added, removed or changed after the first result: {', '.join(changed)}" if changed
                else "ORDER: no target changed after the first result")
        if present["REPORT.md"] and rows:
            v = report_verdicts(read("REPORT.md"))
            missing = [r["id"] for r in rows if r["id"].strip() not in v]
            bad = [k for k, x in v.items() if x not in VERDICTS]
            if missing:
                fails.append(f"REPORT.md: no row for targets {', '.join(missing)}")
            if bad:
                fails.append(f"REPORT.md: verdict not in the fixed list for {', '.join(bad)}")
            if not missing and not bad:
                c = {x: sum(1 for k in v.values() if k == x) for x in VERDICTS}
                passes.append("REPORT.md: every target has a verdict (" + ", ".join(f"{k} {n}" for k, n in c.items()) + ")")
    status = "FAIL" if fails else ("NOT RUN YET" if not ran else "PASS")
    return {"name": name, "status": status, "fails": fails, "waits": waits, "passes": passes}


def main(root=HERE):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    repo = repo_root(root)
    folders = sorted(os.path.join(root, d) for d in os.listdir(root)
                     if os.path.isdir(os.path.join(root, d)) and d not in SKIP and not d.startswith("."))
    results = [audit_folder(f, repo) for f in folders]
    L = ["REPRODUCTIONS AUDIT (reproductions/STANDARD.md)", f"made {time.strftime('%Y-%m-%d %H:%M')}", ""]
    if not results:
        L.append("no reproduction folder yet")
    for r in results:
        L.append(f"{r['name']}: {r['status']}")
        L += [f"   FAIL  {x}" for x in r["fails"]] + [f"   wait  {x}" for x in r["waits"]] + [f"   ok    {x}" for x in r["passes"]]
        L.append("")
    text = "\n".join(L).rstrip() + "\n"
    with open(os.path.join(root, "AUDIT.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print(text)
    return 1 if any(r["fails"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
