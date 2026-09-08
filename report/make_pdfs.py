# -*- coding: utf-8 -*-
"""Render the TEMARL reports to PDF using headless Chrome.

Chrome is used rather than a Python PDF library because Bengali is a complex
script: it needs proper glyph shaping for conjuncts (ক্ষ, জ্ঞ, স্ট্র). Chrome's
text engine does this correctly via HarfBuzz; reportlab's basic TTF support does
not, and would render broken conjuncts.

The Bengali document requests 'Nirmala UI' (C:/Windows/Fonts/Nirmala.ttc), which
ships with Windows and covers Bengali.
"""

from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

DOCS = [("TEMARL_Report_English.html", "TEMARL_Report_English.pdf"),
        ("TEMARL_Report_Bangla.html", "TEMARL_Report_Bangla.pdf"),
        ("TEMARL_Presentation.html", "TEMARL_Presentation.pdf")]


def find_chrome():
    for p in CHROME_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("No Chrome or Edge found; cannot render PDFs.")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    chrome = find_chrome()
    print("renderer:", chrome)
    for src, dst in DOCS:
        s = os.path.join(HERE, src)
        d = os.path.join(HERE, dst)
        if not os.path.exists(s):
            print("  [skip] missing", src)
            continue
        if os.path.exists(d):
            os.remove(d)
        cmd = [chrome, "--headless", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer",
               "--print-to-pdf-no-header",
               "--print-to-pdf=%s" % d,
               "file:///" + s.replace("\\", "/")]
        subprocess.run(cmd, capture_output=True, timeout=180)
        if os.path.exists(d):
            print("  OK   %-34s %8.1f KB" % (dst, os.path.getsize(d) / 1024))
        else:
            print("  FAIL %s" % dst)


if __name__ == "__main__":
    main()
