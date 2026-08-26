import json
from collections import Counter

file_path = r"C:\Users\T25301092\Downloads\Comiset23_Lab_Environment_Dataset\dataset_comillas2.json"

MY_VOCAB = {
    "T1190","T1566","T1059","T1204","T1053","T1543","T1547",
    "T1068","T1055","T1046","T1016","T1083","T1021","T1550",
    "T1072","T1005","T1560","T1041","T1486","T1489"
}

technique_counter = Counter()
in_vocab = 0
out_vocab = 0
total_labeled = 0
checked = 0

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        checked += 1

        try:
            src = json.loads(line).get('_source', {})
            tid = src.get('rule_technique_id')
            if not tid:
                continue
            total_labeled += 1
            parent = tid.split('.')[0]  # T1574.002 → T1574
            technique_counter[parent] += 1
            if parent in MY_VOCAB:
                in_vocab += 1
            else:
                out_vocab += 1
        except:
            continue

print(f"\nRecords scanned: {checked:,}")
print(f"Labeled records found: {total_labeled:,}")
print(f"Map to your vocab (in): {in_vocab:,} ({100*in_vocab/max(total_labeled,1):.1f}%)")
print(f"Would become UNK (out): {out_vocab:,} ({100*out_vocab/max(total_labeled,1):.1f}%)")
print(f"\nAll parent techniques found:")
for tech, count in technique_counter.most_common():
    flag = "✅" if tech in MY_VOCAB else "❌"
    print(f"  {flag} {tech}: {count:,}")