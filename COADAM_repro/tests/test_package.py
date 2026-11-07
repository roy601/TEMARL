import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from scipy.io import savemat
from prepare import ROOT, prepare, replace
from report_results import METHODS, METRICS, extract, report
from run_study import write_json, matlab_stage

class PackageTests(unittest.TestCase):
    def test_patch_and_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            for track in ('release','paper_aligned'):
                cell=Path(tmp)/track
                prepare(cell,{'track':track})
                main=(cell/'code/Phase_3and4.m').read_text()
                baseline=(cell/'code/Phase5_Baselines.m').read_text()
                self.assertNotIn('/Users/ujw',main)
                self.assertIn('assert(has_tabular',baseline)
                self.assertNotIn('env_adapt.reset',baseline)
                self.assertIn('function res = aggregate_metrics',baseline)
                if track=='paper_aligned':
                    self.assertIn('repro_adam',main)
                    self.assertIn('mod(total_steps, target_update_freq)',main)
                    self.assertIn('100000 + ep',baseline)
        with self.assertRaises(ValueError): replace('a a','a','b')

    def test_full_raw_report_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); cell=root/'release/seed_00'; (cell/'results').mkdir(parents=True)
            data=[]
            for method in METHODS:
                item={'name':method}
                item.update({metric:{'raw':np.array([.1,.2,.3])} for metric in METRICS})
                data.append(item)
            result=cell/'results/baseline_results_final.mat'
            savemat(result,{'results_tableA':np.array(data,dtype=object),'results_tableB':np.array(data,dtype=object)})
            self.assertEqual(len(extract(result,3)),480)
            with self.assertRaises(ValueError): extract(result,4)
            write_json(root/'manifest.json',{'mode':'smoke','expected_cells':2,'protocol':{'tracks':['release','paper_aligned']}})
            write_json(cell/'settings.json',{'track':'release','seed':0,'eval_episodes':3})
            write_json(cell/'complete.json',{})
            self.assertEqual(report(root),1)
            text=(root/'RESULTS.md').read_text()
            self.assertIn('1/2',text); self.assertIn('Pending',text)
            self.assertIn('Degradation score',text)
            self.assertTrue((root/'episodes.csv').exists())

    def test_resume_rejects_missing_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            cell=Path(tmp)
            write_json(cell/'dqn.done.json',{'artifacts':{'results/missing.mat':'bad-hash'}})
            with self.assertRaisesRegex(RuntimeError,'changed/missing'):
                matlab_stage('not-invoked',cell,'dqn','')

if __name__=='__main__': unittest.main()
