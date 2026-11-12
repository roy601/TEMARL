# -*- coding: utf-8 -*-
"""Download and read candidate datasets, and write one plain report per dataset.

    python dataset_survey/survey.py                 # everything: download, read, report
    python dataset_survey/survey.py --plan          # only show what would be downloaded
    python dataset_survey/survey.py --only casinolimit ait_ads
    python dataset_survey/survey.py --force         # read again even if a report exists

What "read" means here, for every file inside every archive (archives inside archives too):
  * every byte is read, so a damaged archive member is caught (CRC);
  * every line is counted and checked for valid UTF-8;
  * every line is searched for MITRE ATT&CK technique IDs (T1xxx, T1xxx.xxx);
  * CSV and JSON-lines files are parsed into fields. Files up to FULL_PARSE_BYTES are parsed in
    full; larger ones are parsed for their first FULL_PARSE_LINES lines and then 1 line in
    SAMPLE_EVERY. The report states, per file group, how many lines were parsed.

Nothing is changed in the datasets. Downloads go to dataset_survey/data/ (not committed). Reports go
to dataset_survey/out/<dataset>/ (REPORT.txt, report.json) and dataset_survey/out/SUMMARY.txt.
Standard library only. Safe to stop and run again: finished downloads and reports are kept.
"""
from __future__ import annotations

import argparse
import collections
import csv
import errno
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tarfile
import time
import traceback
import urllib.error
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "dataset-survey/1.0 (research; stdlib urllib)"}
CHUNK = 4 << 20
FULL_PARSE_BYTES, FULL_PARSE_LINES, SAMPLE_EVERY = 300 << 20, 200_000, 50
MAX_DISTINCT, MAX_FIELDS, NEST_DEPTH, NEST_SPOOL_BYTES = 300, 400, 3, 12 << 30
TECH = re.compile(rb"(?<![A-Za-z0-9])T1\d{3}(?:\.\d{3})?(?![A-Za-z0-9])")
ARCHIVE_EXT = (".zip", ".tar", ".tgz", ".tar.gz", ".tar.bz2", ".tar.xz", ".gz")

DATASETS = [
    {"name": "casinolimit", "title": "CasinoLimit (RAID 2025)", "source": ("zenodo", "17256954")},
    {"name": "ait_ads", "title": "AIT Alert Data Set (CSET 2024)", "source": ("zenodo", "8263181")},
    {"name": "windows_apt_2025", "title": "Windows-APT 2025 (Data in Brief 2026)", "source": ("mendeley", "b8fmtzvpy8")},
    {"name": "shell_attack_evolution", "title": "Shell Attack Evolution Dataset (SRDS 2025)",
     "source": ("github", "zyw-286/shell-attack-evolution-dataset", "main"), "approx": 110 << 20},
    {"name": "cptc_sage_alerts", "title": "CPTC and CCDC alerts, from the SAGE repository",
     "source": ("github", "tudelft-cda-lab/SAGE", "main"), "only": "/alerts/", "approx": 100 << 20},
    {"name": "unraveled", "title": "Unraveled / DAPT2021 (Computer Networks 2023), labelled part only",
     "source": ("s3", "dapt2021", "processed/")},
    {"name": "pwnjutsu", "title": "PWNJUTSU (IEEE TNSM 2022)", "source": ("manual",
     "IEEE DataPort needs a subscription (https://ieee-dataport.org/documents/pwnjutsu-dataset). "
     "If you get pwnjutsu_dataset.tar (81 GB), put it in this folder and run again.")},
    {"name": "camlds", "title": "CAM-LDS (IJIS 2026)", "source": ("done",
     "Already read line by line on 2026-11-07: camlds_real/DATASET_REPORT.md and camlds_real/out/scan/.")},
]


def say(msg=""):
    print(msg, flush=True)


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


# ── downloading ───────────────────────────────────────────────────────────────

def http_json(url):
    req = urllib.request.Request(url, headers={**UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def http_text(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def file_hash(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def listing(ds):
    """[{name, url, size, algo, digest}] for a dataset; raises on network problems."""
    kind = ds["source"][0]
    if kind == "zenodo":
        rec = http_json(f"https://zenodo.org/api/records/{ds['source'][1]}")
        out = []
        for f in rec["files"]:
            algo, _, digest = f["checksum"].partition(":")
            out.append({"name": f["key"], "url": f["links"]["self"], "size": f["size"], "algo": algo, "digest": digest})
        return out, f"Zenodo record {ds['source'][1]}, DOI {rec.get('doi', '?')}"
    if kind == "mendeley":
        base = f"https://data.mendeley.com/public-api/datasets/{ds['source'][1]}"
        meta = http_json(base)
        files = http_json(f"{base}/files?folder_id=root&version={meta['version']}")
        out = [{"name": f["filename"], "url": f["content_details"]["download_url"], "size": f["content_details"]["size"],
                "algo": "sha256", "digest": f["content_details"]["sha256_hash"]} for f in files]
        return out, f"Mendeley Data {ds['source'][1]} version {meta['version']}, DOI {meta['doi']['id']}"
    if kind == "github":
        repo, branch = ds["source"][1], ds["source"][2]          # no GitHub API: it is rate-limited
        return ([{"name": f"{repo.split('/')[1]}-{branch}.zip", "url": f"https://codeload.github.com/{repo}/zip/refs/heads/{branch}",
                  "size": None, "algo": None, "digest": None, "approx": ds.get("approx", 0)}],
                f"GitHub {repo}, branch {branch}")
    if kind == "s3":
        bucket, prefix = ds["source"][1], ds["source"][2]
        out, token = [], None
        while True:
            url = f"https://{bucket}.s3.amazonaws.com/?list-type=2&prefix={prefix}" + (
                f"&continuation-token={urllib.request.quote(token, safe='')}" if token else "")
            xml = http_text(url)
            for block in re.findall(r"<Contents>(.*?)</Contents>", xml, flags=re.S):
                key = re.search(r"<Key>(.*?)</Key>", block).group(1)
                size = int(re.search(r"<Size>(\d+)</Size>", block).group(1))
                etag = re.search(r"<ETag>(.*?)</ETag>", block).group(1).replace("&quot;", "").strip('"')
                if size and not key.endswith("/"):
                    md5 = etag if re.fullmatch(r"[0-9a-f]{32}", etag) else None
                    out.append({"name": key, "url": f"https://{bucket}.s3.amazonaws.com/{urllib.request.quote(key)}",
                                "size": size, "algo": "md5" if md5 else None, "digest": md5})
            m = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", xml)
            if not m:
                break
            token = m.group(1)
        return out, f"S3 bucket {bucket}, prefix {prefix}"
    return [], ds["source"][1]


BLOCKED = "BLOCKED (Windows would not open it; usually the antivirus)"


def blocked_by_antivirus(e):
    """Windows refusing to open a file it just wrote: error 225 ('contains a virus'), or EINVAL, which is
    what Defender gave on 2026-11-11 for a Windows-APT 2025 file it flagged. Attack logs often contain
    attack scripts as text, so this is expected."""
    return isinstance(e, OSError) and (getattr(e, "winerror", None) == 225 or (os.name == "nt" and e.errno == errno.EINVAL))


def fetch(item, dest):
    """Download one file with resume and retries. Returns (ok, note)."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and (item["size"] is None or os.path.getsize(dest) == item["size"]):
        return True, "already here"
    part = dest + ".part"
    for attempt in range(1, 7):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        try:
            req = urllib.request.Request(item["url"], headers={**UA, **({"Range": f"bytes={have}-"} if have else {})})
            with urllib.request.urlopen(req, timeout=120) as r:
                if have and r.status != 206:
                    have = 0
                with open(part, "ab" if have else "wb") as fh:
                    done, t0 = have, time.time()
                    for block in iter(lambda: r.read(1 << 20), b""):
                        fh.write(block)
                        done += len(block)
                        if time.time() - t0 > 20:
                            t0 = time.time()
                            say(f"      {os.path.basename(dest)}: {human(done)}" + (f" of {human(item['size'])}" if item["size"] else ""))
            if item["size"] is not None and os.path.getsize(part) != item["size"]:
                raise IOError(f"size {os.path.getsize(part)} is not the expected {item['size']}")
            os.replace(part, dest)
            return True, "downloaded"
        except urllib.error.HTTPError as e:
            if e.code == 416 and item["size"] is not None and have == item["size"]:
                os.replace(part, dest)
                return True, "downloaded"
            err = f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001  network errors are retried
            if blocked_by_antivirus(e):
                return False, BLOCKED
            err = f"{type(e).__name__}: {e}"
        say(f"      attempt {attempt} failed ({err}); retrying")
        time.sleep(min(60, 5 * attempt))
    return False, err


def download(ds, folder, plan_only):
    kind = ds["source"][0]
    if kind in ("manual", "done"):
        if kind == "manual" and not plan_only:
            os.makedirs(folder, exist_ok=True)                   # so the file can be dropped in
        return {"status": kind, "note": ds["source"][1], "files": []}
    try:
        items, origin = listing(ds)
    except Exception as e:  # noqa: BLE001
        return {"status": "listing failed", "note": f"{type(e).__name__}: {e}", "files": []}
    total = sum((i["size"] or i.get("approx", 0)) for i in items)
    say(f"  {len(items)} files, {human(total)} ({origin})")
    if plan_only:
        for i in items[:12]:
            say(f"      {i['name']}  {human(i['size']) if i['size'] else 'size unknown'}")
        return {"status": "plan", "note": origin, "files": [], "planned_bytes": total}
    os.makedirs(folder, exist_ok=True)
    have = sum(os.path.getsize(os.path.join(folder, *i["name"].split("/"))) for i in items
               if os.path.exists(os.path.join(folder, *i["name"].split("/"))))
    free = shutil.disk_usage(folder).free
    if free < (total - have) + (2 << 30):
        return {"status": "not enough disk space", "note": f"needs {human(total - have)}, free {human(free)}", "files": []}
    files, ok_all, n_blocked = [], True, 0
    for i in items:
        dest = os.path.join(folder, *i["name"].split("/"))
        ok, note = fetch(i, dest)
        rec = {"name": i["name"], "size": None, "download": note, "checksum": "none published"}
        try:
            if ok:
                rec["size"] = os.path.getsize(dest)
                if i["algo"]:
                    good = file_hash(dest, i["algo"]) == i["digest"]
                    rec["checksum"] = f"{i['algo']} {'matches' if good else 'DOES NOT MATCH'}"
                    ok &= good
                else:
                    rec["checksum"] = "none published; sha256 " + file_hash(dest, "sha256")
        except OSError as e:                                     # the file vanished or cannot be opened
            if not (blocked_by_antivirus(e) or not os.path.exists(dest)):
                raise
            ok, note = False, BLOCKED
        if note == BLOCKED:                                      # a blocked file does not stop the rest
            rec.update(size=None, download=BLOCKED, checksum=BLOCKED + ": not read")
            n_blocked += 1
            ok = True
        files.append(rec)
        ok_all &= ok
    if n_blocked:
        origin += (f". WARNING: {n_blocked} of {len(items)} files were blocked by Windows (usually the antivirus) "
                   f"and are NOT in this report")
    if kind == "github" and ok_all:                              # GitHub writes the commit into the zip
        try:
            with zipfile.ZipFile(os.path.join(folder, items[0]["name"])) as zf:
                origin += f", commit {zf.comment.decode('ascii', 'replace') or 'unknown'}"
        except zipfile.BadZipFile:
            ok_all = False
    return {"status": "downloaded" if ok_all else "download incomplete", "note": origin, "files": files}


# ── reading ───────────────────────────────────────────────────────────────────

def class_of(path):
    p = re.sub(r"[0-9a-fA-F]{8}-[0-9a-fA-F-]{27}", "<uuid>", path)
    p = re.sub(r"(?<![A-Za-z])[0-9a-f]{12,}(?![A-Za-z])", "<hex>", p)
    return re.sub(r"\d+", "#", p)


def mask(text, width=220):
    text = re.sub(r"[A-Za-z0-9+/=_\-]{28,}", lambda m: f"<token:{len(m.group(0))}>", text.replace("\t", " ").strip())
    return text[:width] + ("..." if len(text) > width else "")


def new_class():
    return {"files": 0, "bytes": 0, "lines": 0, "binary": 0, "bad_utf8": 0, "kind": "text", "tech": collections.Counter(),
            "tech_per_file": [], "fields": {}, "rows": 0, "parsed": 0, "ragged": 0, "samples": [], "tech_samples": [],
            "example": None, "delim": None, "note": ""}


def add_value(cls, name, value):
    f = cls["fields"].get(name)
    if f is None:
        if len(cls["fields"]) >= MAX_FIELDS:
            return
        f = cls["fields"][name] = {"n": 0, "filled": 0, "vals": collections.Counter(), "overflow": False, "tech": 0}
    f["n"] += 1
    if value in ("", None):
        return
    f["filled"] += 1
    v = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
    if TECH.search(v.encode("utf-8", "replace")):
        f["tech"] += 1
    if not f["overflow"]:
        f["vals"][v[:80]] += 1
        if len(f["vals"]) > MAX_DISTINCT:
            f["overflow"] = True


def flatten(obj, prefix="", depth=0):
    if isinstance(obj, dict) and depth < 3:
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}{k}." if isinstance(v, dict) and depth < 2 else f"{prefix}{k}", depth + 1)
    elif isinstance(obj, list):
        yield prefix.rstrip(".") + "[]", f"list of {len(obj)}" if len(obj) > 3 else obj
    else:
        yield prefix.rstrip("."), obj


def add_record(cls, obj):
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj[:20]):
        for x in obj:                                            # a whole list of records on one line
            add_record(cls, x)
        return
    cls["rows"] += 1
    if isinstance(obj, dict):
        for k, v in flatten(obj):
            add_value(cls, k, v)
    else:
        add_value(cls, "(value)", obj)


class Scanner:
    def __init__(self, tmp_dir, only=None):
        self.classes = collections.defaultdict(new_class)
        self.ext = collections.defaultdict(lambda: [0, 0, 0])
        self.tot = collections.Counter()
        self.problems = []
        self.tmp_dir, self.only, self.t0 = tmp_dir, only, time.time()

    # one leaf file, read as a stream
    def leaf(self, fh, path, size_hint):
        if self.only and self.only not in "/" + path:
            for _ in iter(lambda: fh.read(CHUNK), b""):
                pass
            self.tot["skipped_files"] += 1
            return
        cls = self.classes[class_of(path)]
        cls["files"] += 1
        cls["example"] = cls["example"] or path
        low = path.lower()
        ext = os.path.splitext(low)[1] if "." in os.path.basename(low) else "(none)"
        state = {"kind": None, "n": 0, "header": None, "doc": None, "doc_bytes": 0, "tech": 0, "binary": False,
                 "first": True, "size_unknown": size_hint is None, "pending": None}
        full = size_hint is not None and size_hint <= FULL_PARSE_BYTES
        carry, nbytes, nlines = b"", 0, 0
        while True:
            block = fh.read(CHUNK)
            nbytes += len(block)
            if state["first"] and block:
                state["first"] = False
                state["binary"] = b"\x00" in block[:8192]
            if state["binary"]:
                if not block:
                    break
                continue
            buf = carry + block
            if block:
                cut = buf.rfind(b"\n")
                if cut < 0 and len(buf) < (64 << 20):
                    carry = buf
                    continue
                region, carry = (buf, b"") if cut < 0 else (buf[:cut + 1], buf[cut + 1:])
            else:
                region, carry = buf, b""
            if region:
                nlines += region.count(b"\n") + (0 if region.endswith(b"\n") else 1)
                self.region(cls, region, path, low, state, full)
            if not block:
                break
        if state["doc"] is not None:
            self.whole_json(cls, b"".join(state["doc"]), path)
        if state["pending"] is not None:                         # the file ended inside quotes
            cls["rows"] += 1
            cls["ragged"] += 1
        cls["bytes"] += nbytes
        cls["lines"] += nlines
        cls["binary"] += state["binary"]
        if state["tech"]:
            cls["tech_per_file"].append(state["tech"])
        e = self.ext[ext]
        e[0] += 1; e[1] += nbytes; e[2] += nlines
        self.tot["files"] += 1; self.tot["bytes"] += nbytes; self.tot["lines"] += nlines
        self.tot["binary"] += state["binary"]; self.tot["empty"] += nbytes == 0
        if time.time() - self.t0 > 30:
            self.t0 = time.time()
            say(f"      read {self.tot['files']:,} files, {human(self.tot['bytes'])}, {self.tot['lines']:,} lines")

    def region(self, cls, region, path, low, state, full):
        for m in TECH.finditer(region):
            cls["tech"][m.group(0).decode()] += 1
            state["tech"] += 1
        try:
            region.decode("utf-8")
        except UnicodeDecodeError:
            bad = 0
            for ln in region.split(b"\n"):
                try:
                    ln.decode("utf-8")
                except UnicodeDecodeError:
                    bad += 1
            cls["bad_utf8"] += bad
            self.tot["bad_utf8"] += bad
        if state["doc"] is not None:
            state["doc"].append(region)
            state["doc_bytes"] += len(region)
            if state["doc_bytes"] > FULL_PARSE_BYTES:            # size was unknown and it turned out too large
                state["doc"], state["kind"], cls["kind"] = None, "text", "text"
                cls["note"] = "large single JSON document: not parsed into fields"
            return
        lines = None
        if state["kind"] is None:                                # decide once, from the first lines
            lines = region.split(b"\n")
            first = lines[0].decode("utf-8", "replace").strip()
            kind = "text"
            if first and first[0] in "{[":
                try:
                    json.loads(first)
                    kind = "jsonl"
                except ValueError:                               # a document spread over many lines
                    kind = "json" if low.endswith((".json", ".geojson")) or first in ("{", "[", "[{") else "text"
            if kind == "text" and low.endswith((".csv", ".tsv")):
                kind = "csv"
                counts = {d: first.count(d) for d in (",", ";", "\t", "|")}
                cls["delim"] = cls["delim"] or max(counts, key=counts.get)
            if kind == "json":
                if full or state["size_unknown"]:
                    state["doc"], state["doc_bytes"] = [region], len(region)
                    cls["kind"] = "json"
                    state["kind"] = "json"
                    return
                kind, cls["note"] = "text", "large single JSON document: not parsed into fields"
            state["kind"] = kind
            if cls["kind"] == "text" or kind != "text":
                cls["kind"] = kind
            if len(cls["samples"]) < 3:
                cls["samples"] += [mask(x.decode("utf-8", "replace")) for x in lines[:3 - len(cls["samples"])] if x.strip()]
        if state["tech"] and len(cls["tech_samples"]) < 5:
            for m in TECH.finditer(region):
                a, b = region.rfind(b"\n", 0, m.start()) + 1, region.find(b"\n", m.end())
                b = b if b >= 0 else len(region)
                a, b = max(a, m.start() - 110), min(b, m.end() + 110)      # the part of the line around the ID
                cls["tech_samples"].append(mask(region[a:b].decode("utf-8", "replace")))
                if len(cls["tech_samples"]) >= 5:
                    break
        if state["kind"] not in ("csv", "jsonl"):
            return
        if lines is None:
            lines = region.split(b"\n")
        if region.endswith(b"\n"):
            lines = lines[:-1]                                   # the empty piece after the last newline
        for raw in lines:
            if state["kind"] == "csv":                           # a quoted field may hold line breaks
                if state["pending"] is not None:
                    raw = state["pending"] + b"\n" + raw
                if raw.count(b'"') % 2:                          # still inside quotes: the record goes on
                    state["pending"] = raw if len(raw) < (8 << 20) else None
                    if state["pending"] is None:                 # an unclosed quote: give up on this record
                        cls["rows"] += 1
                        cls["ragged"] += 1
                    continue
                state["pending"] = None
            if not raw.strip():
                continue
            n = state["n"]
            state["n"] += 1
            if state["kind"] == "csv" and n == 0:
                state["header"] = next(csv.reader([raw.decode("utf-8", "replace").strip("\r﻿")], delimiter=cls["delim"]))
                continue
            if not (full or n < FULL_PARSE_LINES or n % SAMPLE_EVERY == 0):
                cls["rows"] += 1
                continue
            cls["parsed"] += 1
            text = raw.decode("utf-8", "replace").rstrip("\r")
            if state["kind"] == "jsonl":
                try:
                    add_record(cls, json.loads(text))
                except ValueError:
                    cls["ragged"] += 1
                    cls["rows"] += 1
            else:
                try:
                    row = next(csv.reader([text], delimiter=cls["delim"]))
                except (csv.Error, StopIteration):
                    row = []
                cls["rows"] += 1
                if len(row) != len(state["header"]):
                    cls["ragged"] += 1
                    continue
                for k, v in zip(state["header"], row):
                    add_value(cls, k, v)

    def whole_json(self, cls, data, path):
        try:
            doc = json.loads(data.decode("utf-8", "replace"))
        except ValueError as e:
            self.problems.append(f"JSON did not parse: {path}: {e}")
            return
        records = doc if isinstance(doc, list) else None
        if isinstance(doc, dict):
            lists = [v for v in doc.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
            if len(lists) == 1 and len(doc) <= 6:
                records = lists[0]
                cls["note"] = "one JSON document; records taken from its only list"
        if records is not None:
            for r in records:
                cls["parsed"] += 1
                add_record(cls, r)
        else:
            cls["parsed"] += 1
            add_record(cls, doc)

    # archives, also nested
    def any_file(self, opener, path, size, depth=0):
        low = path.lower()
        if low.endswith(ARCHIVE_EXT) and depth < NEST_DEPTH:
            if depth == 0:
                try:
                    fh = opener()
                except OSError as e:
                    self.tot["read_errors"] += 1
                    self.problems.append(f"{BLOCKED if blocked_by_antivirus(e) else 'cannot open'}: {path}: {e}")
                    return None
                return self.archive(fh, path, depth, real_path=opener.path)
            if size is not None and size > NEST_SPOOL_BYTES:
                self.problems.append(f"nested archive too large to unpack, counted as one file: {path} ({human(size)})")
            else:
                os.makedirs(self.tmp_dir, exist_ok=True)
                tmp = os.path.join(self.tmp_dir, f"nested_{depth}_{os.getpid()}")
                with opener() as src, open(tmp, "wb") as dst:
                    shutil.copyfileobj(src, dst, CHUNK)
                try:
                    with open(tmp, "rb") as fh:
                        return self.archive(fh, path, depth, real_path=tmp)
                finally:
                    os.remove(tmp)
        try:
            with opener() as fh:
                self.leaf(fh, path, size)
        except Exception as e:  # noqa: BLE001  one bad member must not stop the scan
            self.tot["read_errors"] += 1
            self.problems.append(f"{BLOCKED if blocked_by_antivirus(e) else 'read error'}: {path}: {type(e).__name__}: {e}")

    def archive(self, fh, path, depth, real_path):
        self.tot["archives"] += 1
        low = path.lower()
        try:
            if low.endswith(".zip"):
                fh.close()
                with zipfile.ZipFile(real_path) as zf:
                    for info in zf.infolist():
                        if not info.is_dir():
                            self.any_file(_Open(lambda i=info: zf.open(i)), f"{path}::{info.filename}", info.file_size, depth + 1)
            elif low.endswith(".gz") and not low.endswith((".tar.gz", ".tgz")):
                fh.close()
                self.any_file(_Open(lambda: gzip.open(real_path, "rb")), path[:-3], None, depth + 1)
            else:
                fh.close()
                with tarfile.open(real_path, "r|*") as tf:
                    for member in tf:
                        if member.isfile():
                            self.any_file(_Open(lambda m=member: tf.extractfile(m)), f"{path}::{member.name}", member.size, depth + 1)
        except Exception as e:  # noqa: BLE001
            self.tot["read_errors"] += 1
            self.problems.append(f"archive error: {path}: {type(e).__name__}: {e}")


class _Open:
    def __init__(self, fn, path=None):
        self.fn, self.path = fn, path

    def __call__(self):
        return self.fn()


def scan(folder, tmp_dir, only=None, skip=()):
    """skip: files already recorded as blocked at download, so they are not counted twice."""
    sc = Scanner(tmp_dir, only)
    for root, dirs, names in os.walk(folder):
        dirs.sort()
        for name in sorted(names):
            if name.endswith(".part") or name == "_manifest.json":
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, folder).replace(os.sep, "/")
            if rel in skip:
                continue
            op = _Open(lambda p=full: open(p, "rb"), full)
            try:
                size = os.path.getsize(full)
            except OSError:
                size = None
            sc.any_file(op, rel, size)
    return sc


# ── reporting ─────────────────────────────────────────────────────────────────

def dist(xs):
    xs = sorted(xs)
    return f"min {xs[0]}, median {xs[len(xs) // 2]}, max {xs[-1]}" if xs else "none"


def field_lines(cls, limit=40):
    out = []
    for name, f in list(cls["fields"].items())[:limit]:
        top = ", ".join(f"{mask(k, 28)} ({c})" for k, c in f["vals"].most_common(3))
        distinct = f"more than {MAX_DISTINCT}" if f["overflow"] else str(len(f["vals"]))
        out.append(f"      {name[:38]:<38} filled {100 * f['filled'] / max(1, cls['parsed']):5.1f}%  distinct {distinct:<14}"
                   f"{'  ATT&CK IDs in ' + str(f['tech']) + ' values' if f['tech'] else ''}  e.g. {top}")
    if len(cls["fields"]) > limit:
        out.append(f"      ... and {len(cls['fields']) - limit} more fields (see report.json)")
    return out


def write_report(ds, dl, sc, out_dir, seconds):
    os.makedirs(out_dir, exist_ok=True)
    L, tot = [], sc.tot
    add = L.append
    tech = collections.Counter()
    for c in sc.classes.values():
        tech.update(c["tech"])
    parents = {t.split(".")[0] for t in tech}
    order = sorted(sc.classes.items(), key=lambda kv: -kv[1]["bytes"])
    add(f"DATASET REPORT: {ds['title']}")
    add(f"Made by dataset_survey/survey.py on {time.strftime('%Y-%m-%d %H:%M')} in {seconds:.0f} s. The dataset was not changed.")
    add(f"Source: {dl['note']}")
    add("")
    add("1. DOWNLOADED FILES")
    for f in dl["files"][:60]:
        add(f"   {f['name'][:70]:<70} {human(f['size']) if f['size'] else '-':>10}  {f['checksum']}")
    if len(dl["files"]) > 60:
        add(f"   ... and {len(dl['files']) - 60} more (see report.json)")
    add("")
    add("2. TOTALS (every byte read)")
    add(f"   archives opened {tot['archives']:,} | files read {tot['files']:,} | size {human(tot['bytes'])} | lines {tot['lines']:,}")
    add(f"   binary files {tot['binary']:,} | empty files {tot['empty']:,} | lines that are not UTF-8 {tot['bad_utf8']:,} | "
        f"read errors {tot['read_errors']:,}" + (f" | files outside the part of interest, skipped {tot['skipped_files']:,}" if tot["skipped_files"] else ""))
    add("")
    add("3. MITRE ATT&CK TECHNIQUE IDS FOUND IN THE TEXT")
    add("   CAUTION: an ID written in the data is not automatically a label of the attack. It can be the ground")
    add("   truth, or only the technique a detector's rule is tagged with (for example every Wazuh alert carries")
    add("   one). Use 3a and 3b to see where the IDs sit and which files say they are labels.")
    add(f"   mentions {sum(tech.values()):,} | distinct IDs {len(tech)} | distinct parent techniques {len(parents)}")
    carriers = sorted(((f["tech"], fname, name) for name, c in sc.classes.items() for fname, f in c["fields"].items() if f["tech"]),
                      reverse=True)
    add("   3a. structured fields whose values contain IDs (values parsed, field name, file group):")
    for n, fname, name in carriers[:12] or [(0, "none", "")]:
        add(f"       {n:>10,}  {fname[:40]:<40} {name[:70]}" if n else "       none found in parsed fields")
    label_like = [(name, c) for name, c in order if re.search(r"label|ground|truth|annotat|manifest", name, re.I)]
    add("   3b. file groups whose name suggests labels or ground truth:")
    for name, c in label_like[:12] or [("", None)]:
        add(f"       {name[:90]}  (files {c['files']:,}, records {c['rows']:,}, IDs {len(c['tech'])})" if c else "       none")
    if tech:
        add("   most frequent: " + ", ".join(f"{t} ({c:,})" for t, c in tech.most_common(25)))
        add("   file groups that contain them (mentions per file show how long one file's sequence could be):")
        with_ids = [kv for kv in sorted(sc.classes.items(), key=lambda kv: -sum(kv[1]["tech"].values())) if kv[1]["tech"]]
        if len(with_ids) > 15:
            add(f"   ({len(with_ids)} file groups contain IDs; the 15 with the most are shown, all are in report.json)")
        for name, c in with_ids[:15]:
            if c["tech"]:
                add(f"     {name[:95]}")
                add(f"        mentions {sum(c['tech'].values()):,} | distinct IDs {len(c['tech'])} | files with IDs {len(c['tech_per_file']):,} "
                    f"of {c['files']:,} | per file: {dist(c['tech_per_file'])}")
                for s in c["tech_samples"][:2]:
                    add(f"        > {s}")
    else:
        add("   none. This dataset has no technique IDs written in it.")
    add("")
    add("4. FILE TYPES")
    for ext, (n, b, ln) in sorted(sc.ext.items(), key=lambda kv: -kv[1][1])[:20]:
        add(f"   {ext:<12} files {n:>9,}  size {human(b):>10}  lines {ln:>15,}")
    add("")
    add(f"5. FILE GROUPS ({len(sc.classes):,} in total; numbers in a path are shown as #). Largest first.")
    for name, c in order[:50]:
        add(f"   {name[:100]}")
        add(f"      files {c['files']:,} | size {human(c['bytes'])} | lines {c['lines']:,} | type {c['kind']}"
            + (f" | binary {c['binary']:,}" if c["binary"] else "") + (f" | ATT&CK IDs {len(c['tech'])}" if c["tech"] else ""))
    add("")
    add("6. FIELDS OF THE STRUCTURED FILE GROUPS (CSV and JSON)")
    shown, seen_sets = 0, {}
    for name, c in sorted(order, key=lambda kv: (not kv[1]["tech"], "label" not in kv[0].lower(), -kv[1]["bytes"])):
        if not c["fields"] or shown >= 40:
            continue
        shown += 1
        add(f"   {name[:100]}")
        add(f"      records {c['rows']:,} | parsed into fields {c['parsed']:,} | records that did not fit {c['ragged']:,}"
            + (f" | {c['note']}" if c["note"] else ""))
        key = tuple(sorted(c["fields"]))
        if key in seen_sets:
            add(f"      same {len(key)} fields as {seen_sets[key][:90]}")
        elif len(seen_sets) >= 14:
            add(f"      {len(key)} fields (see report.json)")
        else:
            seen_sets[key] = name
            L.extend(field_lines(c))
    if not shown:
        add("   none")
    add("")
    add("7. FIRST LINES OF THE LARGEST TEXT FILE GROUPS (long tokens are masked)")
    for name, c in [kv for kv in order if kv[1]["samples"]][:30]:
        add(f"   {name[:100]}   (example file: {c['example'][:90]})")
        for s in c["samples"]:
            add(f"      > {s}")
    add("")
    add("8. PROBLEMS")
    for p in sc.problems[:60] or ["   none"]:
        add(f"   {p}" if not p.startswith("   ") else p)
    if len(sc.problems) > 60:
        add(f"   ... and {len(sc.problems) - 60} more")
    text = "\n".join(L) + "\n"
    with open(os.path.join(out_dir, "REPORT.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    summary = {"dataset": ds["name"], "title": ds["title"], "status": dl["status"], "source": dl["note"], "seconds": round(seconds),
               "archives": tot["archives"], "files": tot["files"], "bytes": tot["bytes"], "lines": tot["lines"],
               "binary": tot["binary"], "bad_utf8": tot["bad_utf8"], "read_errors": tot["read_errors"],
               "technique_mentions": sum(tech.values()), "technique_ids": len(tech), "parent_techniques": len(parents),
               "file_groups": len(sc.classes), "inputs": dl["files"],
               "blocked_files": sum(f.get("download") == BLOCKED for f in dl["files"]) + sum(p.startswith(BLOCKED) for p in sc.problems)}
    full = {**summary, "techniques": dict(tech.most_common()), "problems": sc.problems[:500], "groups": {
        name: {"files": c["files"], "bytes": c["bytes"], "lines": c["lines"], "kind": c["kind"], "binary": c["binary"],
               "rows": c["rows"], "parsed": c["parsed"], "ragged": c["ragged"], "example": c["example"], "note": c["note"],
               "techniques": dict(c["tech"].most_common()), "technique_mentions_per_file": dist(c["tech_per_file"]),
               "fields": {k: {"filled": f["filled"], "seen": f["n"], "distinct": None if f["overflow"] else len(f["vals"]),
                              "with_attack_ids": f["tech"], "top": f["vals"].most_common(8)} for k, f in c["fields"].items()}}
        for name, c in order[:400]}}
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(full, fh, indent=1, ensure_ascii=False)
    return summary


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", choices=[d["name"] for d in DATASETS])
    ap.add_argument("--data-dir", default=os.path.join(HERE, "data"))
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--plan", action="store_true", help="list what would be downloaded, then stop")
    ap.add_argument("--force", action="store_true", help="read again even if a report already exists")
    a = ap.parse_args()
    rows = []
    for ds in DATASETS:
        if a.only and ds["name"] not in a.only:
            continue
        say(f"\n=== {ds['name']}: {ds['title']}")
        folder, out_dir = os.path.join(a.data_dir, ds["name"]), os.path.join(a.out, ds["name"])
        prev = os.path.join(out_dir, "report.json")
        try:
            dl = download(ds, folder, a.plan)
            if a.plan or dl["status"] == "done":
                rows.append({"dataset": ds["name"], "status": dl["status"], "note": dl["note"], "bytes": dl.get("planned_bytes")})
                say(f"  {dl['status']}: {dl['note']}")
                continue
            local = sorted(f for f in os.listdir(folder) if not f.endswith(".part")) if os.path.isdir(folder) else []
            if dl["status"] == "manual" and local:
                dl = {"status": "placed by hand", "note": ds["source"][1], "files": [
                    {"name": f, "size": os.path.getsize(os.path.join(folder, f)), "checksum": "not checked"} for f in local
                    if os.path.isfile(os.path.join(folder, f))]}
            if dl["status"] not in ("downloaded", "placed by hand"):
                say(f"  NOT READ: {dl['status']}: {dl['note']}")
                rows.append({"dataset": ds["name"], "status": dl["status"], "note": dl["note"]})
                continue
            if os.path.exists(prev) and not a.force:
                old = json.load(open(prev, encoding="utf-8"))
                if [(f["name"], f["size"]) for f in old.get("inputs", [])] == [(f["name"], f["size"]) for f in dl["files"]]:
                    say("  report already exists for exactly these files; kept (use --force to read again)")
                    rows.append({k: old.get(k) for k in ("dataset", "status", "files", "bytes", "lines", "read_errors",
                                                         "technique_ids", "parent_techniques", "technique_mentions", "seconds",
                                                         "blocked_files")})
                    continue
            say("  reading every file ...")
            t0 = time.time()
            sc = scan(folder, os.path.join(a.data_dir, "_tmp"), ds.get("only"),
                      skip={f["name"] for f in dl["files"] if f.get("download") == BLOCKED})
            rows.append(write_report(ds, dl, sc, out_dir, time.time() - t0))
            say(f"  done: {sc.tot['files']:,} files, {human(sc.tot['bytes'])}, {sc.tot['lines']:,} lines, "
                f"{rows[-1]['technique_ids']} technique IDs, {sc.tot['read_errors']} read errors -> {os.path.join(out_dir, 'REPORT.txt')}")
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001  one dataset must not stop the others
            say(f"  FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()
            rows.append({"dataset": ds["name"], "status": "failed", "note": f"{type(e).__name__}: {e}"})
    if a.plan:
        say(f"\nTotal to download: {human(sum(r.get('bytes') or 0 for r in rows))}")
        return 0
    os.makedirs(a.out, exist_ok=True)
    lines = [f"DATASET SURVEY SUMMARY, {time.strftime('%Y-%m-%d %H:%M')}", "",
             f"{'dataset':<24}{'status':<24}{'files':>10}{'size':>11}{'lines':>15}{'ATT&CK IDs':>12}{'parents':>9}"
             f"{'errors':>8}{'blocked':>9}"]
    for r in rows:
        if r.get("files") is None:
            lines.append(f"{r['dataset']:<24}{r['status']:<24}  {r.get('note', '')[:150]}")
        else:
            lines.append(f"{r['dataset']:<24}{r['status']:<24}{r['files']:>10,}{human(r['bytes']):>11}{r['lines']:>15,}"
                         f"{r['technique_ids']:>12}{r['parent_techniques']:>9}{r['read_errors']:>8}{r.get('blocked_files', 0):>9}")
    lines += ["",
              "ATT&CK IDs = distinct technique IDs written anywhere in the text. 0 means no technique labels. More than 0 does",
              "  NOT prove labels: the IDs may only be detector rule tags. Check section 3 of the dataset's REPORT.txt.",
              "blocked = downloaded files Windows would not open (usually the antivirus); they are missing from the report.",
              "Each dataset's details: out/<dataset>/REPORT.txt"]
    with open(os.path.join(a.out, "SUMMARY.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    say("\n" + "\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
