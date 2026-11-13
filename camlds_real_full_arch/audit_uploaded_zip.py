"""Read-only source audit of the supplied S1 archive; never executes its commands."""
from pathlib import Path
import collections
import hashlib
import json
import sys
import zipfile

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO/'camlds_real'))
import reconcile_attackmate as R

def main():
    archive = Path(sys.argv[1])
    run = archive.stem.removeprefix('scenario_')
    out = REPO/'camlds_real_full_arch'/'results'/'archive_audit'
    out.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with archive.open('rb') as fh:
        for block in iter(lambda:fh.read(1024*1024), b''): digest.update(block)
    with zipfile.ZipFile(archive) as z:
        corrupt = z.testzip()  # CRC check of every archive member, not semantic telemetry parsing.
        path = next(n for n in z.namelist() if n.endswith('/attacker/logs/attackmate.json'))
        records = []
        for i,line in enumerate(z.read(path).decode('utf-8').splitlines()):
            if line.strip():
                rec = json.loads(line)
                records.append({'path':path,'index':i,'record':rec,'t':R.usec_iso(rec['start-datetime'])})
        entries = len(z.infolist())
        unpacked = sum(i.file_size for i in z.infolist())
        has_csv = any(n.endswith('attack_times.csv') for n in z.namelist())
    with (REPO/'camlds_real/out/steps.jsonl').open(encoding='utf-8') as fh:
        steps = [s for s in map(json.loads,fh) if s['run']==run]
    pairs, shifted, used = R.join(steps,{run:records})
    missing = [s['source_row'] for s in steps if s['source_row'] not in pairs]
    mismatch = [s['source_row'] for s in steps if s['source_row'] in pairs and s['techniques_sub'] != R.techs(pairs[s['source_row']])]
    parent_mismatch = [s['source_row'] for s in steps if s['techniques_parent'] != sorted({t.split('.')[0] for t in s['techniques_sub']})]
    with (REPO/'camlds_real/out/sidecar/steps_link.jsonl').open(encoding='utf-8') as fh:
        links = {s['source_row']:s for s in map(json.loads,fh) if s['run']==run}
    rank = {r['index']:i for i,r in enumerate(sorted(pairs.values(),key=lambda r:r['index']))}
    sidecar_bad=[]
    for s in steps:
        if s['source_row'] not in pairs: continue
        r=pairs[s['source_row']]; link=links.get(s['source_row'],{})
        if link.get('cmd_full') != r['record']['cmd'] or link.get('execution_rank') != rank[r['index']]:
            sidecar_bad.append(s['source_row'])
    extra = [r for r in records if R.techs(r) and id(r) not in used]
    indices = [pairs[s['source_row']]['index'] for s in sorted(steps,key=lambda s:s['exec_index']) if s['source_row'] in pairs]
    result = dict(archive=str(archive), sha256=digest.hexdigest(), zip_entries=entries,
        unpacked_bytes=unpacked, crc_error=corrupt, archive_has_attack_times_csv=has_csv,
        attackmate_records=len(records), record_types=dict(collections.Counter(r['record']['type'] for r in records)),
        labelled_records=sum(bool(R.techs(r)) for r in records), extracted_steps=len(steps), matched=len(pairs),
        timestamp_adjusted_matches=len(shifted), missing=missing, label_mismatches=mismatch,
        parent_mismatches=parent_mismatch, sidecar_mismatches=sidecar_bad,
        extra_labelled_records=[{'index':r['index'],'type':r['record']['type']} for r in extra],
        label_instances=sum(len(s['techniques_sub']) for s in steps),
        unique_parent_labels=len({t for s in steps for t in s['techniques_parent']}),
        multi_label_steps=sum(len(s['techniques_sub'])>1 for s in steps),
        csv_order_matches_execution=indices==sorted(indices))
    (out/'ZIP_AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=['# Uploaded CAM-LDS archive audit','',
           'All AttackMate JSONL records parsed. All ZIP member CRCs checked. Other telemetry contents were not semantically inspected. No attack commands executed.','',
           '| Check | Result |','|---|---|']
    lines.extend(f'| {k} | {v} |' for k,v in result.items())
    lines += ['', 'This checks one supplied archive against the existing corpus. It does not establish authenticity against a publisher checksum or certify every other archive.',
              'The extractor needs the separately released authors\' attack_times.csv; this ZIP alone is not its complete input. Labels are execution metadata, not detector predictions.']
    (out/'ZIP_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(result,indent=2))
    if corrupt or missing or mismatch or parent_mismatch or sidecar_bad:
        raise SystemExit('Audit failed; see report')

if __name__=='__main__': main()
