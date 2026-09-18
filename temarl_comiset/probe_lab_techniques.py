# -*- coding: utf-8 -*-
"""How many techniques did the v1 extractor DISCARD from the LAB corpus?

`thesis_system/extract_comiset_sessions.py` mapped with the 25-token v1
vocabulary and skipped anything it called UNK. The shipped comiset_sessions.json
therefore contains only 10 distinct techniques. This streams the raw LAB file and
counts what is actually there, so we know whether that poverty is a property of
the data or an artefact of the extractor.
"""
import io, json, os, sys, time
from collections import Counter

LAB = os.path.join(os.path.expanduser("~"), "Downloads",
                   "Comiset23_Lab_Environment_Dataset", "dataset_comillas2.json")

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.time()
    tech = Counter()
    n = lab = 0
    with io.open(LAB, encoding="utf-8", errors="replace") as f:
        for line in f:
            n += 1
            if n % 10_000_000 == 0:
                print("  [%6.0fs] lines=%s labelled=%s distinct=%d"
                      % (time.time() - t0, format(n, ","), format(lab, ","), len(tech)))
            line = line.strip().rstrip(",")
            if not line or line in "[]":
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            s = d.get("_source") if isinstance(d, dict) else None
            if not isinstance(s, dict):
                continue
            tid = s.get("rule_technique_id")
            if not tid:
                continue
            if isinstance(tid, list):
                tid = tid[0] if tid else None
            if not tid:
                continue
            tech[str(tid)] += 1
            lab += 1
    print("\nlines %s | labelled %s | DISTINCT TECHNIQUES %d | %.0fs"
          % (format(n, ","), format(lab, ","), len(tech), time.time() - t0))
    for k, v in tech.most_common():
        print("   %-14s %10d  %6.2f%%" % (k, v, 100 * v / max(lab, 1)))
    json.dump(tech.most_common(), open("lab_technique_distribution.json", "w"), indent=1)
    print("wrote lab_technique_distribution.json")

if __name__ == "__main__":
    main()
