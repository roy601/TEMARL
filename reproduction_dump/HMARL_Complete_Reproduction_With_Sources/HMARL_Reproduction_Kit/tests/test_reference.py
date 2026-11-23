import csv
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reference_arithmetic import calculate
from compare_results import summarize
from preflight import run_check, flag_value
from types import SimpleNamespace

class ReferenceTests(unittest.TestCase):
    def test_table3_rows(self):
        with (ROOT/'paper_reference/table3_published.csv').open(newline='',encoding='utf-8') as f:
            r=list(csv.DictReader(f))
        self.assertEqual(len(r),4)
        self.assertEqual(r[0]['strategy'],'H-MARL Expert')
        self.assertEqual(float(r[0]['reward']), -129.53)
        self.assertEqual(float(r[1]['red_impact_count']), 1.14)
    def test_published_reductions(self):
        x=calculate(ROOT/'paper_reference/table3_published.csv')
        self.assertEqual(x['red_impact_expert_vs_meta']['relative_reduction_percent'],22.81)
        self.assertEqual(x['wasted_recoveries_expert_vs_decentralized']['relative_reduction_percent'],92.14)
    def test_no_false_success_when_unrun(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            a=SimpleNamespace(reference=ROOT/'paper_reference/table3_published.csv',results=Path(tmp),measured_metrics=None,abs_tolerance=0.01)
            r=summarize(a)
            self.assertEqual(r['status'],'NOT_EXECUTED')
            self.assertFalse(r['all_18_table3_cells_measured'])
    def test_preflight_fails_for_missing_inputs(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            r=run_check(Path(tmp)/'nothing',Path(tmp)/'missing')
            self.assertFalse(r['ready_for_100_episode_metrics_run'])
            self.assertEqual(r['checks']['checkpoint_policy_files_found'],0)
if __name__=='__main__':unittest.main()
