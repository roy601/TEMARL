from pathlib import Path
import json
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import run_baselines
import make_comparison
import bootstrap

class HarnessTests(unittest.TestCase):
    def test_pinned_revision_count(self):
        self.assertEqual(set(bootstrap.SOURCES), {"cage","punch","cybermonic"})
        for d in bootstrap.SOURCES.values():
            self.assertEqual(len(d['commit']),40)

    def test_official_eval_command(self):
        c = run_baselines.make_command('punch',100,123,Path('/tmp/out'))
        self.assertEqual(c[1:3], ['-m','CybORG.Evaluation.evaluation'])
        self.assertIn('100',c)
        self.assertIn('123',c)
        self.assertEqual(c[-2],str(run_baselines.AGENT_PATHS['punch']))

    def test_no_fabricated_results(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertEqual(make_comparison.compile_rows(Path(t)), [])

    def test_only_completed_runs_counted(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t)/'results'/'punch'/'episodes_100_seed_3'
            d.mkdir(parents=True)
            (d/'summary.json').write_text(json.dumps({'reward':{'mean':-140.,'stdev':50.}}))
            (d/'invocation.json').write_text(json.dumps({'status':'failed','episodes':100,'steps_per_episode':500,'seed':3}))
            self.assertEqual(make_comparison.compile_rows(Path(t)), [])
            (d/'invocation.json').write_text(json.dumps({'status':'completed','episodes':100,'steps_per_episode':500,'seed':3}))
            rows=make_comparison.compile_rows(Path(t))
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['difference_reproduced_minus_published'],2.)

if __name__ == '__main__':
    unittest.main()
