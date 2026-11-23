"""Unittest checks for this reproducibility ZIP (do not modify source artifacts)."""
import sys
import unittest
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from verify_package import audit, sha256

class CadoReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit(ROOT)

    def test_original_zip_present(self):
        p=ROOT/'original_archive/futureinternet-18-00552-s001.zip'
        self.assertTrue(p.is_file())
        self.assertEqual(len(sha256(p)),64)

    def test_archive_manifest_discrepancy_explicit(self):
        self.assertEqual(self.report['publisher_manifest']['matched'],56)
        self.assertEqual(self.report['publisher_manifest']['missing'],['README.md'])
        self.assertFalse(self.report['publisher_manifest']['mismatched'])

    def test_primary_reproduction(self):
        self.assertTrue(self.report['table2_reproduced'])
        matches={x['file']:x for x in self.report['main_scientific_csv_comparisons']}
        self.assertEqual(matches['primary_episode_metrics.csv']['archived_rows'],1440)
        self.assertEqual(matches['primary_episode_metrics.csv']['status'],'PASS')

    def test_heldout_reproduction(self):
        self.assertTrue(self.report['table4_heldout_reproduced'])
        matches={x['file']:x for x in self.report['main_scientific_csv_comparisons']}
        self.assertEqual(matches['ood_episode_metrics.csv']['archived_rows'],360)
        self.assertEqual(matches['ood_episode_metrics.csv']['status'],'PASS')

    def test_ablations(self):
        matches={x['file']:x for x in self.report['main_scientific_csv_comparisons']}
        self.assertEqual(matches['ablation_episode_metrics.csv']['archived_rows'],1710)
        self.assertEqual(matches['ablation_episode_metrics.csv']['status'],'PASS')

    def test_p_value_exception_not_hidden(self):
        matches={x['file']:x for x in self.report['main_scientific_csv_comparisons']}
        self.assertEqual(matches['paired_statistical_comparisons.csv']['status'],'NUMERIC_DIFFERENCES')
        self.assertEqual(set(matches['paired_statistical_comparisons.csv']['failed_columns']),{'p_raw','p_holm'})

    def test_all_heldout_statistical_files_match(self):
        for item in self.report['revision_csv_comparisons']:
            self.assertEqual(item['status'],'PASS',item['file'])

    def test_published_primary_values(self):
        with (ROOT/'tables/table2_primary_independently_reproduced.csv').open(newline='',encoding='utf-8') as f:
            vals={r['metric_key']:r for r in csv.DictReader(f)}
        self.assertAlmostEqual(float(vals['utility']['CADO_mean']),0.702014,delta=0.000001)
        self.assertAlmostEqual(float(vals['redirection_precision']['CADO_mean']),0.728191,delta=0.000001)

    def test_published_heldout_values(self):
        with (ROOT/'tables/table4_heldout_independently_reproduced.csv').open(newline='',encoding='utf-8') as f:
            vals={r['metric_key']:r for r in csv.DictReader(f)}
        self.assertAlmostEqual(float(vals['utility']['CADO_mean']),0.6590,delta=0.0001)
        self.assertAlmostEqual(float(vals['redirection_precision']['CADO_mean']),0.5745,delta=0.0001)

if __name__=='__main__':unittest.main()
