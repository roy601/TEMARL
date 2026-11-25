# -*- coding: utf-8 -*-
"""CADO (Future Internet 2026): unpack the authors' Supplementary Material S1 into external/s1 and check it.

    python reproductions/cado/fetch.py                       # the copy committed by a teammate (79ff1e72)
    python reproductions/cado/fetch.py --zip <S1 zip path>   # a copy downloaded from the publisher in a browser

The publisher (MDPI) refuses scripted downloads (HTTP 403, 2026-11-25), so the zip is never downloaded here.
Whichever copy is used must have the SHA-256 below (DECISIONS 3). Every file the authors' manifest
(SHA256SUMS.txt) lists is checked; the one file it lists but the archive lacks (README.md) is reported.
Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
EXT = HERE / "external"
S1 = EXT / "s1"
DEFAULT_ZIP = (REPO / "reproduction_dump" / "CADO_Reproduced_Tables_2_and_4_FINAL" /
               "CADO_Reproduced_Tables_2_and_4_FINAL" / "original_archive" / "futureinternet-18-00552-s001.zip")
ZIP_SHA256 = "edac2fa9db714c6ab7bcad7d0f83a2dd68e52d2760daa8a2ab4172d8252c6447"
ZIP_BYTES = 624_999
MANIFEST_ENTRIES = 57
KNOWN_MISSING = ["README.md"]          # listed in SHA256SUMS.txt, absent from the archive (DECISIONS 3)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(root: Path) -> dict:
    """{name: sha256} from the authors' SHA256SUMS.txt (raw bytes, as the authors hashed them)."""
    out = {}
    for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split("  ", 1)
            out[name] = digest
    return out


def check(root: Path = S1) -> list:
    """Problems with an unpacked supplement (empty list = as published, apart from KNOWN_MISSING)."""
    if not (root / "SHA256SUMS.txt").exists():
        return [f"{root} is not unpacked: run fetch.py"]
    m = manifest(root)
    problems = [] if len(m) == MANIFEST_ENTRIES else [f"manifest has {len(m)} entries, expected {MANIFEST_ENTRIES}"]
    missing = sorted(n for n in m if not (root / n).exists())
    if missing != KNOWN_MISSING:
        problems.append(f"missing files {missing}, expected exactly {KNOWN_MISSING}")
    problems += [f"changed: {n}" for n, d in sorted(m.items()) if (root / n).exists() and sha(root / n) != d]
    return problems


def unpack(zip_path: Path, dest: Path = S1):
    if sha(zip_path) != ZIP_SHA256 or zip_path.stat().st_size != ZIP_BYTES:
        raise SystemExit(f"{zip_path}: not the published S1 archive (SHA-256 or size differs)")
    with zipfile.ZipFile(zip_path) as z:
        if z.testzip() is not None:
            raise SystemExit("the archive has a CRC error")
        root = dest.resolve()
        for name in z.namelist():                           # no member may leave the destination
            if not (root / name).resolve().is_relative_to(root):
                raise SystemExit(f"unsafe member {name}")
        if dest.exists():
            shutil.rmtree(dest)                             # our own unpacked copy, rebuilt from the zip
        dest.mkdir(parents=True)
        z.extractall(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", type=Path, default=DEFAULT_ZIP)
    a = ap.parse_args()
    unpack(a.zip)
    bad = check()
    if bad:
        raise SystemExit("S1 check FAILED:\n  " + "\n  ".join(bad))
    n = len(manifest(S1))
    print(f"S1 unpacked to {S1}: SHA-256 {ZIP_SHA256[:12]}..., {n - len(KNOWN_MISSING)} of {n} manifest files "
          f"present and unchanged; absent as published: {KNOWN_MISSING}")


if __name__ == "__main__":
    sys.exit(main())
