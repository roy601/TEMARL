import json, collections, itertools, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"C:/Users/User/thesis_project_pev_V2/thesis_project_pev/thesis_project/camlds_real/out/steps.jsonl"
steps = [json.loads(l) for l in open(P, encoding="utf-8")]

runs = collections.defaultdict(list)
for s in sorted(steps, key=lambda s: (s["run"], s["exec_index"])):
    runs[s["run"]].append(s)

# flat parent-technique sequence per run
seq = {r: [t for s in v for t in s["techniques_parent"]] for r, v in runs.items()}
sets = {r: set(v) for r, v in seq.items()}

def jac(a, b): return len(a & b) / len(a | b) if (a | b) else 0.0
def lcs_ratio(a, b):
    # cheap similarity: longest common prefix + suffix over max length
    p = 0
    while p < min(len(a), len(b)) and a[p] == b[p]: p += 1
    s = 0
    while s < min(len(a), len(b)) - p and a[-1-s] == b[-1-s]: s += 1
    return (p + s) / max(len(a), len(b))

print("### Inter-variant similarity WITHIN each base scenario")
print("   (this is what a variant-held-out split is actually testing)")
print()
for base in sorted({s["base_scenario"] for s in steps}):
    rs = sorted(r for r in runs if r.split("_")[0] == base)
    if len(rs) < 2:
        print(f"  S{base}: 1 run — cannot hold out a variant")
        continue
    js, ls, ident = [], [], 0
    for a, b in itertools.combinations(rs, 2):
        js.append(jac(sets[a], sets[b]))
        ls.append(lcs_ratio(seq[a], seq[b]))
        ident += seq[a] == seq[b]
    print(f"  S{base}: {len(rs)} variants, {len(js)} pairs")
    print(f"      technique-set Jaccard : min {min(js):.3f}  mean {sum(js)/len(js):.3f}  max {max(js):.3f}")
    print(f"      prefix+suffix overlap : min {min(ls):.3f}  mean {sum(ls)/len(ls):.3f}  max {max(ls):.3f}")
    print(f"      ORDER-IDENTICAL pairs : {ident} / {len(js)}")
print()
print("### Cross-scenario (what a scenario-held-out split tests)")
bases = sorted({s["base_scenario"] for s in steps})
bset = {b: set().union(*[sets[r] for r in runs if r.split("_")[0] == b]) for b in bases}
cj = [(a, b, jac(bset[a], bset[b])) for a, b in itertools.combinations(bases, 2)]
vals = [v for _, _, v in cj]
print(f"  {len(cj)} scenario pairs | Jaccard min {min(vals):.3f}  mean {sum(vals)/len(vals):.3f}  max {max(vals):.3f}")
for a, b, v in sorted(cj, key=lambda x: -x[2])[:5]:
    print(f"      S{a} vs S{b}: {v:.3f}")
print()
print("### Timestamp integrity")
ties = ov = 0
for r, v in runs.items():
    ts = [s["start"] for s in v]
    ties += len(ts) - len(set(ts))
    for a, b in zip(v, v[1:]):
        if b["start"] < a["end"]: ov += 1
print(f"  duplicate start timestamps within a run : {ties}")
print(f"  steps starting before the previous ended: {ov}")
