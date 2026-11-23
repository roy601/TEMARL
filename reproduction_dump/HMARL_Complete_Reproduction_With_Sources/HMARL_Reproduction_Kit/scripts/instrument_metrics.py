#!/usr/bin/env python3
"""Optionally append observational Table-3-aligned metric logging to original evaluators.

The module does not change policy decisions or simulation actions. It saves
metrics as derived from the authors' in-memory per-episode accumulators. Fields
are estimates of their Table 3 aggregation and should be audited prior to claim
of numerical reproduction. Not used for computation in this restricted run.
"""
import argparse
from pathlib import Path

ANCHOR = '    print(reward_string)\n'
INJECTION = '''
    # Reproduction-only audit export. Original paper's metric definitions are in
    # section 5.5; derived quantities should be independently cross-checked.
    if write_to_file:
        def _subnet_mean(entries):
            return mean(entries) if entries else None

        impact_per_agent = {
            agent_name: (mean(action_counts.get('Impact', [])) if action_counts.get('Impact') else 0.0)
            for agent_name, action_counts in red_actions_crt_mean.items()
        }
        _tp = _subnet_mean(true_pos_all)
        _fp = _subnet_mean(false_pos_all)
        _total_recoveries = ((_tp or 0) + (_fp or 0))
        _audit_table3 = {
            'source': 'Instrumented original H-MARL evaluator, not published reference data',
            'episode_count': max_eps,
            'actual_episode_rewards': total_reward,
            'clean_hosts_ratio': _subnet_mean(noninfection_frac_all),
            'non_escalated_hosts_ratio': _subnet_mean(nonprivileged_frac_all),
            'mean_time_to_recover': _subnet_mean(infection_stride_all),
            'useful_recoveries': _tp,
            'wasted_recoveries': _fp,
            'recovery_precision': (_tp / _total_recoveries) if _total_recoveries else None,
            'recovery_error': (_fp / _total_recoveries) if _total_recoveries else None,
            'red_impact_count': sum(impact_per_agent.values()),
            'red_impact_by_agent': impact_per_agent,
            'reward': reward_mean,
            'aggregation_notes': [
                'Mean of non-contractor subnet/episode fractions accumulated in original evaluator',
                'Recoveries use mean of rounded per-subnet episode averages',
                'Red impacts sum per-agent average counts',
                'Precision/error are ratios of mean recoveries; confirm against paper Table 3 before claiming match',
                'Do not conflate these values with original unmodified evaluator output.'
            ]
        }
        with open(log_path + 'table3_instrumented.json', 'w') as _audit_f:
            json.dump(_audit_table3, _audit_f, indent=2)
'''

def patch_file(f, dry_run=False):
    s=f.read_text(encoding='utf-8')
    if "# Reproduction-only audit export." in s:
        return 'already_instrumented'
    if s.count(ANCHOR)!=1:
        raise ValueError(f'Unexpected original evaluator shape: {f}; anchor count={s.count(ANCHOR)}')
    target=s.replace(ANCHOR,ANCHOR+INJECTION,1)
    compile(target,str(f),'exec')
    if not dry_run:
        f.with_name(f.name+'.instrument.original.bak').write_text(s,encoding='utf-8')
        f.write_text(target,encoding='utf-8')
    return 'would_instrument' if dry_run else 'instrumented'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,default=Path('sources/Hierarchical-MARL'))
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    for sub in ('subpolicies','master'):
        f=a.repo/'h-marl-3policy'/sub/'evaluation_metrics.py'
        print(f'{f}: {patch_file(f,a.dry_run)}')

if __name__=='__main__': main()
