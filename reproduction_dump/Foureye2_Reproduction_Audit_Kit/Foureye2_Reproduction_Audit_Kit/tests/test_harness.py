import importlib.util
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / 'foureye2_runner.py'
spec = importlib.util.spec_from_file_location('repro', FILE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class HarnessTests(unittest.TestCase):
    def test_eight_schemes(self):
        self.assertEqual(len(mod.SCHEMES), 8)
        self.assertEqual(mod.SCHEMES['DD-ML-IPI'][-1], 2)
        self.assertEqual(mod.SCHEMES['DD-IPI'][-1], 1)

    def test_models(self):
        with tempfile.TemporaryDirectory() as folder:
            r = mod.required_models(Path(folder), 'DD-ML-IPI', 'aap')
            self.assertEqual(len(r), 6)
            self.assertTrue(all('trained_classi_model_ML_collect_data_IPI.pkl' in str(p) for p in r))
            self.assertEqual(mod.required_models(Path(folder), 'DD-IPI'), [])

    def test_no_lucky_seed_selection(self):
        sample = [
            {'status': 'ok', 'outcome': {'scheme': 'DD-IPI', 'aap': None, 'lifetime': 10,
                                       'TPR_history': [0.5, 1.0], 'FPR_history': [0.2],
                                       'HNE_equilibrium_matching': [True, False]}},
            {'status': 'failed'},
            {'status': 'ok', 'outcome': {'scheme': 'DD-IPI', 'aap': None, 'lifetime': 20,
                                       'TPR_history': [0.5], 'FPR_history': [0.1],
                                       'HNE_equilibrium_matching': [False, False]}}
        ]
        r = mod.aggregate(sample)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['successful_runs'], 2)
        self.assertEqual(r[0]['MTTSF'], 15.0)
        self.assertEqual(r[0]['mean_HNE_equilibrium_matching'], 0.25)

    def test_preflight_reports_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            r = mod.preflight(Path(folder))
            self.assertFalse(r['reproduction_ready'])
            self.assertTrue(r['issues'])

    def test_patch_copies_without_changing_original(self):
        with tempfile.TemporaryDirectory() as folder:
            original = Path(folder)/'original'
            prepared = Path(folder)/'prepared'
            original.mkdir()
            for filename in mod.SOURCE_FILES[:5]:
                (original / filename).write_text('from networkx import nx\n' if filename == 'graph_function.py' else
                                                 'from game_function import *\n' if filename == 'main.py' else 'print("ok")\n')
            mod.prepare(original, prepared)
            self.assertIn('import networkx as nx', (prepared/'graph_function.py').read_text())
            self.assertIn('from networkx import nx', (original/'graph_function.py').read_text())
            self.assertIn('display = False', (prepared/'main.py').read_text())


if __name__ == '__main__':
    unittest.main()
