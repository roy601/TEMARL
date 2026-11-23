"""Exercise local instrumentation without importing unavailable Ray/Gym dependencies."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
spec=importlib.util.spec_from_file_location('metric_instrument',SCRIPTS/'instrument_metrics.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class InstrumentTests(unittest.TestCase):
    def test_instrument_dryrun_and_backup(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'evaluation_metrics.py'
            original='def f():\n    print(reward_string)\n'
            p.write_text(original)
            self.assertEqual(mod.patch_file(p,True),'would_instrument')
            self.assertEqual(p.read_text(),original)
            self.assertEqual(mod.patch_file(p,False),'instrumented')
            self.assertEqual(mod.patch_file(p,False),'already_instrumented')
            self.assertEqual((Path(str(p)+'.instrument.original.bak')).read_text(),original)
            self.assertIn('table3_instrumented.json',p.read_text())
    def test_instrument_missing_anchor_refused(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'evaluation_metrics.py'
            p.write_text('print("no")\n')
            with self.assertRaises(ValueError): mod.patch_file(p)
