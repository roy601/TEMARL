"""Fetch every input of the Kuwano et al. (2023) reproduction, and record what was fetched.

Kuwano, Okuma, Okada & Mitsunaga, "The Attacker Might Also Do Next: ATT&CK Behavior
Forecasting by Attacker-based Collaborative Filtering and Graph Databases",
J. Information Processing 31, 802-811 (2023), doi:10.2197/ipsjjip.31.802

Standard library only. Every file lands in data/raw/<id>/ and is recorded in
data/raw/MANIFEST.json with its byte count and SHA-256, so two machines can prove
they hold identical inputs.

    python download.py                  # fetch everything that is missing
    python download.py --verify         # re-hash data/raw against MANIFEST.json, fetch nothing
    python download.py --out D:/elsewhere

Two kinds of source:
  auto    fetched by this script.
  manual  cisa.gov refuses scripted downloads (HTTP 403). Open the URL in a browser,
          save the file under the path printed, then rerun: the script hashes it and
          records it. These are cross-checks; the primary test pages are the Wayback
          snapshots, which are auto.

An existing file is never overwritten. If it is already present it is hashed and
reported; delete it by hand to fetch it again. A gzip-encoded response is stored
decoded, and the manifest says so.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (kuwano-repro; research reproduction)"
AUTO, MANUAL = "auto", "manual"

# id, how, role, url, filename
SOURCES = [
    # --- training data: MITRE ATT&CK Enterprise, STIX 2.0, pinned by git tag ---
    ("attack_v11.0", AUTO, "TRAIN primary - the version the paper names (v11, 2022-04-25)",
     "https://raw.githubusercontent.com/mitre/cti/ATT%26CK-v11.0/enterprise-attack/enterprise-attack.json",
     "enterprise-attack.json"),
    ("attack_v11.3", AUTO, "TRAIN sensitivity - last v11 patch release",
     "https://raw.githubusercontent.com/mitre/cti/ATT%26CK-v11.3/enterprise-attack/enterprise-attack.json",
     "enterprise-attack.json"),
    ("attack_v12.1", AUTO, "TRAIN sensitivity - live on attack.mitre.org at the paper's access date (2023-01-31)",
     "https://raw.githubusercontent.com/mitre/cti/ATT%26CK-v12.1/enterprise-attack/enterprise-attack.json",
     "enterprise-attack.json"),

    # --- test data: CISA advisories as archived closest to the paper's access date ---
    ("cisa_aa22-277a_wayback", AUTO, "TEST primary - AA22-277A, Wayback snapshot 2023-01-29",
     "http://web.archive.org/web/20230129215752id_/https://www.cisa.gov/uscert/ncas/alerts/aa22-277a",
     "aa22-277a_20230129.html"),
    ("cisa_aa22-138b_wayback", AUTO, "TEST primary - AA22-138B, Wayback snapshot 2023-01-29",
     "http://web.archive.org/web/20230129001025id_/https://www.cisa.gov/uscert/ncas/alerts/aa22-138b",
     "aa22-138b_20230129.html"),
    ("cisa_aa22-174a_wayback", AUTO, "TEST primary - AA22-174A, Wayback snapshot 2023-02-01",
     "http://web.archive.org/web/20230201002818id_/https://www.cisa.gov/uscert/ncas/alerts/aa22-174a",
     "aa22-174a_20230201.html"),

    # --- test data: current CISA pages and official attachments (cross-check, manual) ---
    ("cisa_aa22-277a_live", MANUAL, "TEST cross-check - current page (Last Revised 2022-10-05)",
     "https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-277a", "aa22-277a_live.html"),
    ("cisa_aa22-138b_live", MANUAL, "TEST cross-check - current page (Last Revised 2022-06-02)",
     "https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-138b", "aa22-138b_live.html"),
    ("cisa_aa22-174a_live", MANUAL, "TEST cross-check - current page (Last Revised 2022-07-18)",
     "https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-174a", "aa22-174a_live.html"),
    ("cisa_aa22-277a_pdf", MANUAL, "TEST cross-check - official PDF",
     "https://www.cisa.gov/sites/default/files/publications/aa22-277a-impacket-and-exfiltration-tool-used-to-steal-sensitive-information-from-defense-industrial-base-organization.pdf",
     "aa22-277a.pdf"),
    ("cisa_aa22-138b_pdf", MANUAL, "TEST cross-check - official PDF",
     "https://www.cisa.gov/sites/default/files/publications/AA22-138B_Threat_Actors_Chaining_VMware_Unpatched_Vulnerabilities_for_Full_System_Control.pdf",
     "aa22-138b.pdf"),
    ("cisa_aa22-174a_pdf", MANUAL, "TEST cross-check - official PDF",
     "https://www.cisa.gov/sites/default/files/publications/AA22-174A_Joint_CSA_Malicious_Cyber_Actors_Exploiting_Log4Shell_in_Unpatched_VMware_Horizon_Systems_FINAL.pdf",
     "aa22-174a.pdf"),
    ("cisa_aa22-138b_stix", MANUAL, "TEST cross-check - official STIX attachment",
     "https://www.cisa.gov/sites/default/files/publications/AA22-138B.stix.xml", "aa22-138b.stix.xml"),
    ("cisa_aa22-174a_stix", MANUAL, "TEST cross-check - official STIX attachment",
     "https://www.cisa.gov/sites/default/files/publications/AA22-174A.stix.xml", "aa22-174a.stix.xml"),

    # --- the paper itself (copyright IPSJ: kept out of git) ---
    ("paper", AUTO, "ORACLE - the paper; Tables 5-7 are the reproduction target",
     "https://www.jstage.jst.go.jp/article/ipsjjip/31/0/31_802/_pdf/-char/en", "kuwano2023.pdf"),
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: str, tries: int = 4) -> dict:
    """Download url to dest via a .part file; decode gzip. Returns response facts."""
    part = dest + ".part"
    last = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
                enc = (r.headers.get("Content-Encoding") or "").lower()
                facts = {"http_status": r.status, "final_url": r.geturl(),
                         "content_type": r.headers.get("Content-Type")}
            if enc == "gzip" or (body[:2] == b"\x1f\x8b" and not dest.endswith(".gz")):
                body = gzip.decompress(body)
                facts["content_encoding"] = "gzip (stored decoded)"
            with open(part, "wb") as out:
                out.write(body)
            os.replace(part, dest)
            return facts
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404, 410):
                raise RuntimeError(f"HTTP {e.code} for {url}") from e
            last = e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
        if os.path.exists(part):
            os.remove(part)
        print(f"      attempt {attempt}/{tries} failed: {last}", file=sys.stderr)
        time.sleep(3 * attempt)
    raise RuntimeError(f"giving up on {url}: {last}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw"))
    ap.add_argument("--verify", action="store_true", help="re-hash against MANIFEST.json; fetch nothing")
    ap.add_argument("--reference", help="with --verify: hash against this manifest instead, "
                                        "e.g. reference/REFERENCE_MANIFEST.json from another machine")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    man_path = os.path.join(a.out, "MANIFEST.json")
    manifest = {}
    src = a.reference if (a.verify and a.reference) else man_path
    if os.path.exists(src):
        with open(src, encoding="utf-8") as fh:
            manifest = json.load(fh)
    elif a.reference:
        print(f"no such reference manifest: {a.reference}")
        return 1

    if a.verify:
        bad = pending = 0
        for sid, how, *_ in SOURCES:
            rec = manifest.get(sid)
            p = os.path.join(a.out, rec["path"]) if rec else None
            if not rec or not os.path.exists(p):
                tag = "PENDING " if how == MANUAL else "MISSING "
                pending += how == MANUAL
                bad += how == AUTO
                print(f"  {tag} {sid}")
            elif sha256(p) != rec["sha256"]:
                print(f"  CHANGED  {sid}: hash differs from manifest")
                bad += 1
            else:
                print(f"  ok       {sid:<26} {rec['bytes']:>12,}  {rec['sha256'][:16]}")
        print(f"\n{len(SOURCES) - bad - pending}/{len(SOURCES)} verified; "
              f"{bad} missing or changed; {pending} manual pending")
        return 1 if bad else 0

    failed, pending = [], []
    for sid, how, role, url, fname in SOURCES:
        d = os.path.join(a.out, sid)
        os.makedirs(d, exist_ok=True)
        dest = os.path.join(d, fname)
        rel = os.path.relpath(dest, a.out).replace(os.sep, "/")
        print(f"[{sid}] ({how}) {role}")
        prev = manifest.get(sid, {})
        if os.path.exists(dest):
            print("      present, not overwritten")
            facts = {k: prev[k] for k in ("http_status", "final_url", "content_type", "content_encoding")
                     if k in prev}
            if how == MANUAL and "http_status" not in prev:
                facts["obtained"] = "manual browser download"
        elif how == MANUAL:
            print(f"      MANUAL: open {url}\n              save as {dest}")
            pending.append(sid)
            continue
        else:
            try:
                facts = fetch(url, dest)
            except RuntimeError as e:
                print(f"      FAILED: {e}")
                failed.append(sid)
                continue
        manifest[sid] = {
            "how": how, "role": role, "url": url, "path": rel, **facts,
            "bytes": os.path.getsize(dest), "sha256": sha256(dest),
            "recorded_utc": prev.get("recorded_utc")
                            or dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        }
        print(f"      {manifest[sid]['bytes']:>12,} bytes  sha256 {manifest[sid]['sha256']}")
        with open(man_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)

    print(f"\nmanifest: {man_path}")
    if pending:
        print(f"manual pending ({len(pending)}): {', '.join(pending)}")
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)}  -- rerun to retry; nothing else is touched")
        return 1
    print("all auto sources present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
