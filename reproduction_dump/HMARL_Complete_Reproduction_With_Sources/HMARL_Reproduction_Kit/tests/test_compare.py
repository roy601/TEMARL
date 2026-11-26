"""Synthetic test fixtures only: never write test values into real results/."""
import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('comparison',ROOT/'scripts/compare_results.py')
compare=importlib.util.module_from_spec(spec);spec.loader.exec_module(compare)

class ComparisonTests(unittest.TestCase):
    def test_only_real_summaries_enable_instrument_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            results=Path(d)
            ref=compare.read_csv(ROOT/'paper_reference/table3_published.csv')
            args=argparse.Namespace(reference=ROOT/'paper_reference/table3_published.csv',results=results,measured_metrics=None,abs_tolerance=.01)
            self.assertEqual(compare.summarize(args)['status'],'NOT_EXECUTED')
            for slug, strategy in compare.ALIASES.items():
                sub=results/slug
                sub.mkdir()
                vals={col:float(ref[strategy][col]) for col in compare.COLUMNS}
                (sub/'summary.json').write_text(json.dumps({'parameters':{'max_episodes':100},'reward':{'mean':vals['reward']}}))
                (sub/'table3_instrumented.json').write_text(json.dumps({'episode_count':100, **vals}))
            info=compare.summarize(args)
            self.assertTrue(info['all_18_table3_cells_measured'])
            self.assertTrue(info['instrumented_metrics_available_for_both'])
            self.assertAlmostEqual(info['experimental_red_impact_reduction_percent'],22.81,places=2)
            self.assertEqual(info['status'],'TABLE3_NUMERICALLY_CLOSE_INSTRUMENTED_REPRODUCTION_NEEDS_INDEPENDENT_AUDIT')
            # Fixture values are from published table solely to exercise parser;
            # the actual package's results directory has no measured results.
