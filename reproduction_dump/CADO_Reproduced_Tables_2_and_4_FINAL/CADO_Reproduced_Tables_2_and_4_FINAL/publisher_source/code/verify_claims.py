"""Check selected manuscript claims directly against decisions and saved outputs."""
from pathlib import Path
from dataclasses import replace
import json
import numpy as np
import pandas as pd
import revision_analysis as ra

ROOT = Path(__file__).resolve().parents[1]
x, meta, episodes = ra.inputs()
base, actions, reasons = ra.decisions(x, ra.Setting())
wide = ra.decisions(x, replace(ra.Setting(), residual_bound=2))[1]
zero = ra.decisions(x, replace(ra.Setting(), residual_bound=0))[1]
benign_changed = int(np.count_nonzero((base != actions) & ~x['malicious'].astype(bool)))
assert benign_changed == 0
assert np.array_equal(wide, actions)
assert np.array_equal(zero, base)
assert np.all(np.abs(base-actions) <= 1)
comparisons = pd.read_csv(ROOT/'revision_results/sensitivity_paired_comparisons.csv')
negative = comparisons[(comparisons.dataset == 'ood') & (comparisons.metric == 'utility') & (comparisons.difference < 0)]
assert len(negative) == 1
assert (negative.ci_low < 0).all() and (negative.ci_high > 0).all()
poc = json.loads((ROOT/'revision_results/poc_summary.json').read_text())
requests = sum(1 for _ in (ROOT/'revision_results/poc_http_requests.jsonl').open(encoding='utf-8'))
journal = sum(1 for _ in (ROOT/'revision_results/poc_state_journal.jsonl').open(encoding='utf-8'))
assert requests == poc['requests'] == 4170
assert journal == poc['journal_entries'] == 1770
assert poc['trials'] == poc['passed_criteria'] == 300
assert sum(c['restored'] for c in poc['cases']) == 240
result = {
    'events_checked': len(actions),
    'default_benign_action_changes': benign_changed,
    'radius_two_same_decisions_as_default': True,
    'radius_zero_same_decisions_as_consensus': True,
    'default_residual_bound_verified': True,
    'negative_heldout_configuration': negative[['setting','difference','ci_low','ci_high']].to_dict(orient='records'),
    'poc_request_count_verified': requests,
    'poc_journal_count_verified': journal,
    'poc_restoration_count_verified': 240,
}
(ROOT/'revision_results/claim_verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
