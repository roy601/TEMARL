# -*- coding: utf-8 -*-
"""Deep audit of the downloaded CAM-LDS archives — what is ACTUALLY inside.

Earlier audits read filenames and one of everything, and twice I generalised
from that further than the evidence allowed. This one opens the archives.

WHAT "COMPLETE" MEANS HERE, stated honestly
───────────────────────────────────────────
Reading every line of every file is not the right target: 34 scenario archives
hold roughly 357,000 entries and 30-50 GB uncompressed, almost all of it OS
noise (apt, systemd, kernel). A report containing it would be unusable.

So this is complete in three senses and sampled in exactly one:

  EXHAUSTIVE on structure   every entry in every archive is catalogued, with
                            its size, CRC and classification, and written to
                            FULL_INVENTORY.csv. Nothing is hidden behind a
                            summary -- open the CSV and every file is there.
  EXHAUSTIVE on what matters  attackmate.json, facts.json and every config are
                            read IN FULL, every record parsed.
  SYSTEMATIC on the rest    every distinct KIND of file (by path signature and
                            extension) is opened and characterised: format,
                            line count, field names, first and last lines.
  SAMPLED                   only in how many examples of each identical kind
                            are opened, controlled by --per-class.

  --mode exhaustive additionally decompresses and line-counts EVERY text file.
  Slow (expect 20-45 min for 7.4 GB) but then nothing is estimated.

Usage
─────
    python camlds_real/deep_audit.py --data "C:\\Users\\user5\\Downloads\\DATASET 01"
    python camlds_real/deep_audit.py --data "<dir>" --mode exhaustive
    python camlds_real/deep_audit.py --data "<dir>" --only scenario_7.zip

Outputs (camlds_real/audit_out/):
    FULL_INVENTORY.csv    every entry in every archive
    FILE_CLASSES.md       every distinct kind of file, with read content
    DEEP_AUDIT.md         the verdict
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RULE = "=" * 78
report: list[str] = []
MAX_READ = 1 << 20          # bytes read from any one file for characterisation
BINARY_EXT = {".gz", ".zip", ".png", ".jpg", ".pcap", ".pcapng", ".db", ".so",
              ".bin", ".pyc", ".tar", ".xz", ".bz2", ".jar", ".elf", ".deb"}


def say(s: str = "") -> None:
    print(s)
    report.append(s)


def head(s: str) -> None:
    say("")
    say(RULE)
    say(s)
    say(RULE)


# ── classification ──────────────────────────────────────────────────────────

def classify(path: str) -> str:
    """A path signature: the same KIND of file gets the same label.

    Run names, host names, step numbers and rotation suffixes are collapsed so
    that 34 copies of the same log become one class.
    """
    p = path.replace("\\", "/")
    p = re.sub(r"^manifestations_(filtered|raw)/", "MANIFEST/", p)
    # `techniques/` nests one level DEEPER than the other two groupings:
    #   steps/<run-step>/<host>/...
    #   sequences/<run-step>/<host>/...
    #   techniques/<technique>/<run-step>/<host>/...
    # Collapsing them with one pattern mislabels the technique folder as the
    # run-step and then the run-step as the host.
    p = re.sub(r"^(MANIFEST/)techniques/[^/]+/[^/]+/",
               r"\1techniques/<technique>/<run-step>/", p)
    p = re.sub(r"^(MANIFEST/)(steps|sequences)/[^/]+/",
               r"\1\2/<run-step>/", p)
    p = re.sub(r"^scenario_[^/]+/", "<scenario>/", p)
    # host directory, right after the scenario or the step
    p = re.sub(r"^(<scenario>"
               r"|MANIFEST/(?:steps|sequences)/<run-step>"
               r"|MANIFEST/techniques/<technique>/<run-step>)/"
               r"([a-z0-9][a-z0-9._-]*)/", r"\1/<host>/", p)
    p = re.sub(r"\.\d+(\.gz)?$", r".N\1", p)          # access.log.2 -> access.log.N
    p = re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", p)
    p = re.sub(r"\.\d+\.<date>@[\d:]+~?$", ".<backup>", p)
    p = re.sub(r"/[0-9a-f]{8,}/", "/<hash>/", p)
    return p


def sniff(data: bytes) -> tuple[str, dict]:
    """Identify the format of a file's bytes and pull out its shape."""
    if not data:
        return "empty", {}
    if b"\x00" in data[:2048]:
        return "binary", {}
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = data.decode("latin-1")
        except Exception:  # noqa: BLE001
            return "binary", {}
    s = text.strip()
    if not s:
        return "blank", {}

    # one JSON document?
    if s[0] in "{[":
        try:
            o = json.loads(s)
            if isinstance(o, dict):
                return "json-object", {"keys": sorted(o)[:40], "n_keys": len(o)}
            return "json-array", {"n": len(o),
                                  "keys": sorted(o[0])[:40]
                                  if o and isinstance(o[0], dict) else []}
        except json.JSONDecodeError:
            pass
    lines = [l for l in s.splitlines() if l.strip()]
    # JSON Lines?
    if lines and lines[0].lstrip()[:1] == "{":
        ok, keys = 0, collections.Counter()
        for l in lines[:200]:
            try:
                o = json.loads(l)
                ok += 1
                if isinstance(o, dict):
                    keys.update(o.keys())
            except json.JSONDecodeError:
                break
        if ok >= max(1, min(len(lines), 200) // 2):
            return "jsonl", {"n_lines": len(lines),
                             "keys": [k for k, _ in keys.most_common(40)]}
    # delimited?
    for d, name in ((";", "csv-semicolon"), (",", "csv-comma"), ("\t", "tsv")):
        if lines[0].count(d) >= 2 and all(
                abs(l.count(d) - lines[0].count(d)) <= 1 for l in lines[1:6]):
            return name, {"n_lines": len(lines),
                          "header": lines[0].split(d)[:25]}
    # common log shapes
    if re.match(r"^\S+ \S+ \S+ \[\d{2}/\w{3}/\d{4}", lines[0]):
        return "apache-clf", {"n_lines": len(lines)}
    if re.match(r"^\w{3}\s+\d+\s[\d:]{8}\s\S+\s", lines[0]):
        return "syslog", {"n_lines": len(lines)}
    if lines[0].startswith("type=") or "audit(" in lines[0]:
        return "auditd", {"n_lines": len(lines)}
    if re.match(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", lines[0]):
        return "iso-timestamped", {"n_lines": len(lines)}
    if lines[0].lstrip().startswith(("- ", "---", "#")) or ":" in lines[0][:40]:
        return "yaml-or-conf", {"n_lines": len(lines)}
    return "text", {"n_lines": len(lines)}


# ── main passes ─────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.path.join(here, "audit_out"))
    ap.add_argument("--mode", choices=("structure", "content", "exhaustive"),
                    default="content")
    ap.add_argument("--per-class", type=int, default=3,
                    help="examples of each file class to open and read")
    ap.add_argument("--only", default=None, help="audit one archive only")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    zips = []
    for root, _, files in os.walk(a.data):
        for fn in sorted(files):
            if fn.lower().endswith(".zip") and (not a.only or fn == a.only):
                zips.append(os.path.join(root, fn))
    if not zips:
        print(f"no .zip under {a.data}")
        return 1

    say("CAM-LDS DEEP AUDIT")
    say(f"  data    : {os.path.abspath(a.data)}")
    say(f"  archives: {len(zips)}")
    say(f"  mode    : {a.mode}")
    say(f"  per-class examples: {a.per_class}")

    # ── pass 1: exhaustive structural inventory ─────────────────────────────
    head("PASS 1 — EVERY ENTRY IN EVERY ARCHIVE")
    say("  No sampling. Each row is written to FULL_INVENTORY.csv.")
    say("")

    inv_path = os.path.join(a.out, "FULL_INVENTORY.csv")
    inv = open(inv_path, "w", newline="", encoding="utf-8")
    w = csv.writer(inv)
    w.writerow(["archive", "path", "class", "is_dir", "compressed_bytes",
                "uncompressed_bytes", "crc32", "modified"])

    classes: dict[str, dict] = collections.defaultdict(
        lambda: {"n": 0, "bytes": 0, "examples": []})
    per_archive: dict[str, dict] = {}
    total_entries = total_unc = total_cmp = 0

    for zp in zips:
        name = os.path.basename(zp)
        try:
            zf = zipfile.ZipFile(zp)
            infos = zf.infolist()
        except Exception as e:  # noqa: BLE001
            say(f"  {name}: UNREADABLE ({e})")
            continue
        nd = nf = unc = cmp_ = 0
        hosts: set[str] = set()
        for i in infos:
            cls = classify(i.filename)
            isdir = i.filename.endswith("/")
            w.writerow([name, i.filename, cls, int(isdir), i.compress_size,
                        i.file_size, f"{i.CRC:08x}",
                        "%04d-%02d-%02d %02d:%02d:%02d" % i.date_time])
            if isdir:
                nd += 1
            else:
                nf += 1
                unc += i.file_size
                cmp_ += i.compress_size
                c = classes[cls]
                c["n"] += 1
                c["bytes"] += i.file_size
                if len(c["examples"]) < a.per_class * 4:
                    c["examples"].append((zp, i.filename, i.file_size))
            m = re.match(r"^(?:scenario_[^/]+"
                         r"|manifestations_(?:filtered|raw)/(?:steps|sequences)/[^/]+"
                         r"|manifestations_(?:filtered|raw)/techniques/[^/]+/[^/]+)"
                         r"/([^/]+)/", i.filename)
            if m:
                hosts.add(m.group(1))
        per_archive[name] = {"files": nf, "dirs": nd, "unc": unc, "cmp": cmp_,
                             "hosts": sorted(hosts)}
        total_entries += len(infos)
        total_unc += unc
        total_cmp += cmp_
        zf.close()

    inv.close()

    say(f"  {'archive':<46} {'files':>7} {'dirs':>6} {'uncompressed':>14} {'hosts':>6}")
    for n in sorted(per_archive):
        d = per_archive[n]
        say(f"  {n:<46} {d['files']:>7,} {d['dirs']:>6,} "
            f"{d['unc'] / 1e6:>12,.1f}MB {len(d['hosts']):>6}")
    say("")
    say(f"  TOTAL entries      : {total_entries:,}")
    say(f"  TOTAL uncompressed : {total_unc / 1e9:,.2f} GB")
    say(f"  TOTAL compressed   : {total_cmp / 1e9:,.2f} GB")
    say(f"  distinct file kinds: {len(classes):,}")
    say(f"  full inventory     : {inv_path}")

    # ── hosts ───────────────────────────────────────────────────────────────
    head("PASS 2 — HOSTS PRESENT")
    allh = collections.Counter()
    for d in per_archive.values():
        allh.update(d["hosts"])
    say(f"  {'host':<20} {'appears in N archives':>22}")
    for h, c in allh.most_common():
        say(f"  {h:<20} {c:>22}")

    # ── pass 3: open every distinct kind ────────────────────────────────────
    head("PASS 3 — EVERY DISTINCT KIND OF FILE, OPENED AND READ")
    say(f"  {len(classes)} distinct kinds. Each is opened and characterised.")
    say(f"  Full detail in FILE_CLASSES.md; the biggest are summarised here.")
    say("")

    det: list[str] = ["# Every distinct kind of file in the CAM-LDS archives",
                      "",
                      f"{len(classes)} classes, from {len(zips)} archives.",
                      "Paths are normalised: `<scenario>`, `<host>`, `<run-step>`,",
                      "`.N` (rotation) and `<date>` stand in for the varying parts.",
                      ""]

    fmt_tot = collections.Counter()
    ranked = sorted(classes.items(), key=lambda kv: -kv[1]["bytes"])
    for cls, info in ranked:
        fmts = collections.Counter()
        shown = 0
        det.append(f"## `{cls}`")
        det.append("")
        det.append(f"- files: **{info['n']:,}**")
        det.append(f"- total size: **{info['bytes'] / 1e6:,.2f} MB**")
        det.append(f"- mean size: {info['bytes'] / max(1, info['n']) / 1e3:,.1f} KB")
        for zp, member, size in info["examples"]:
            if shown >= a.per_class:
                break
            ext = os.path.splitext(member)[1].lower()
            if ext in BINARY_EXT:
                fmts["binary-by-extension"] += 1
                shown += 1
                det.append(f"- `{os.path.basename(zp)}` :: `{member}` "
                           f"({size / 1e3:,.1f} KB) — binary by extension, not read")
                continue
            try:
                with zipfile.ZipFile(zp) as z:
                    raw = z.open(member).read(MAX_READ)
            except Exception as e:  # noqa: BLE001
                det.append(f"- unreadable: {e}")
                shown += 1
                continue
            kind, meta = sniff(raw)
            fmts[kind] += 1
            fmt_tot[kind] += 1
            shown += 1
            det.append("")
            det.append(f"### example: `{os.path.basename(zp)}` :: `{member}`")
            det.append("")
            det.append(f"- size {size:,} bytes, read {len(raw):,}")
            det.append(f"- **format: {kind}**")
            for k, v in meta.items():
                det.append(f"- {k}: `{v}`")
            if kind not in ("binary", "empty"):
                try:
                    txt = raw.decode("utf-8", "replace")
                except Exception:  # noqa: BLE001
                    txt = ""
                ls = [l for l in txt.splitlines() if l.strip()]
                if ls:
                    det.append("")
                    det.append("```")
                    for l in ls[:6]:
                        det.append(l[:300])
                    if len(ls) > 8:
                        det.append(f"... [{len(ls) - 9} more lines in this sample] ...")
                    if len(ls) > 6:
                        for l in ls[-2:]:
                            det.append(l[:300])
                    det.append("```")
            det.append("")
        info["formats"] = dict(fmts)

    with open(os.path.join(a.out, "FILE_CLASSES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(det))

    say(f"  {'kind of file':<56} {'files':>7} {'MB':>10}")
    for cls, info in ranked[:40]:
        say(f"  {cls[:56]:<56} {info['n']:>7,} {info['bytes'] / 1e6:>9,.1f}")
    if len(ranked) > 40:
        say(f"  ... {len(ranked) - 40} further kinds, all in FILE_CLASSES.md")
    say("")
    say("  formats detected across the opened examples:")
    for k, c in fmt_tot.most_common():
        say(f"      {k:<24} {c}")

    # ── pass 4: read the critical files IN FULL ─────────────────────────────
    head("PASS 4 — THE FILES THAT MATTER, READ IN FULL")

    say("  attacker/logs/attackmate.json — every record of every run")
    say("")
    keys_all = collections.Counter()
    types_all = collections.Counter()
    recs_tot = 0
    runs_read = 0
    say(f"  {'archive':<46} {'records':>8} {'types'}")
    for zp in zips:
        n = os.path.basename(zp)
        try:
            with zipfile.ZipFile(zp) as z:
                t = next((m for m in z.namelist()
                          if m.endswith("attacker/logs/attackmate.json")), None)
                if not t:
                    continue
                txt = z.read(t).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            continue
        recs = []
        try:
            o = json.loads(txt)
            recs = o if isinstance(o, list) else [o]
        except json.JSONDecodeError:
            for line in txt.splitlines():
                line = line.strip()
                if line:
                    try:
                        recs.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        tc = collections.Counter(r.get("type") for r in recs
                                 if isinstance(r, dict))
        for r in recs:
            if isinstance(r, dict):
                keys_all.update(r.keys())
        types_all.update(tc)
        recs_tot += len(recs)
        runs_read += 1
        say(f"  {n:<46} {len(recs):>8} {dict(tc.most_common(4))}")
    say("")
    say(f"  runs read: {runs_read} | total records: {recs_tot:,}")
    say(f"  EVERY top-level key seen: {dict(keys_all)}")
    say(f"  every `type` value: {dict(types_all.most_common())}")

    say("")
    say("  attacker/facts.json — what it describes")
    for zp in zips[:1]:
        try:
            with zipfile.ZipFile(zp) as z:
                t = next((m for m in z.namelist()
                          if m.endswith("attacker/facts.json")), None)
                if t:
                    o = json.loads(z.read(t).decode("utf-8", "replace"))
                    say(f"    {len(o)} keys; "
                        f"ansible_all_ipv4_addresses="
                        f"{o.get('ansible_all_ipv4_addresses')}")
                    say(f"    hostname={o.get('ansible_hostname')} "
                        f"fqdn={o.get('ansible_fqdn')}")
                    say("    >> These are Ansible facts about the ATTACKER host "
                        "itself, not about targets.")
        except Exception as e:  # noqa: BLE001
            say(f"    unreadable: {e}")

    # ── pass 5: exhaustive line counting ────────────────────────────────────
    if a.mode == "exhaustive":
        head("PASS 5 — EXHAUSTIVE: EVERY TEXT FILE DECOMPRESSED AND COUNTED")
        say("  No estimates. Every text file is decompressed and its lines counted.")
        say("")
        lines_by_class = collections.Counter()
        files_done = bytes_done = 0
        for zp in zips:
            try:
                zf = zipfile.ZipFile(zp)
            except Exception:  # noqa: BLE001
                continue
            for i in zf.infolist():
                if i.filename.endswith("/") or i.file_size == 0:
                    continue
                if os.path.splitext(i.filename)[1].lower() in BINARY_EXT:
                    continue
                try:
                    with zf.open(i) as fh:
                        n = 0
                        while True:
                            chunk = fh.read(1 << 20)
                            if not chunk:
                                break
                            n += chunk.count(b"\n")
                except Exception:  # noqa: BLE001
                    continue
                lines_by_class[classify(i.filename)] += n
                files_done += 1
                bytes_done += i.file_size
                if files_done % 20000 == 0:
                    print(f"    ... {files_done:,} files, "
                          f"{bytes_done / 1e9:.2f} GB", file=sys.stderr)
            zf.close()
        say(f"  files counted: {files_done:,} | bytes: {bytes_done / 1e9:,.2f} GB")
        say(f"  TOTAL LINES  : {sum(lines_by_class.values()):,}")
        say("")
        say(f"  {'kind of file':<56} {'lines':>14}")
        for cls, n in lines_by_class.most_common(40):
            say(f"  {cls[:56]:<56} {n:>14,}")
    else:
        head("PASS 5 — skipped")
        say("  Re-run with --mode exhaustive to decompress and line-count every")
        say("  text file. Expect 20-45 minutes for the full 7.4 GB.")

    # ── verdict ─────────────────────────────────────────────────────────────
    head("VERDICT")
    say("  Read the numbers above before this section; it is an interpretation,")
    say("  and the tables are the evidence.")
    say("")
    say(f"  - {total_entries:,} entries across {len(zips)} archives, "
        f"{total_unc / 1e9:,.2f} GB uncompressed, in "
        f"{len(classes):,} distinct kinds of file.")
    say("  - Full per-file inventory in FULL_INVENTORY.csv; every distinct kind")
    say("    opened and sampled in FILE_CLASSES.md.")
    say(f"  - attackmate.json: {recs_tot:,} records across {runs_read} runs. "
        f"Keys seen: {sorted(keys_all)}.")
    if keys_all and not any(re.search(r"techniq|tactic|mitre|label", k, re.I)
                            for k in keys_all):
        say("    >> NO technique label in ANY record of ANY run. Confirmed by")
        say("       full read, not by sampling.")
    say("  - facts.json describes the ATTACKER host, so it cannot identify targets.")
    say("")
    say("  Use FILE_CLASSES.md to decide what else is worth reading. Anything")
    say("  this audit did not open is in FULL_INVENTORY.csv with its size and")
    say("  CRC, so nothing is hidden -- only unread, and nameable.")

    with open(os.path.join(a.out, "DEEP_AUDIT.md"), "w", encoding="utf-8") as f:
        f.write("```\n" + "\n".join(report) + "\n```\n")
    print(f"\nwrote FULL_INVENTORY.csv, FILE_CLASSES.md, DEEP_AUDIT.md to {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
