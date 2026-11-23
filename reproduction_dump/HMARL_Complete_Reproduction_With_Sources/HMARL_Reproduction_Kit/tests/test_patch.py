import tempfile
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "scripts"))
from patch_metrics import patch

class PatchTests(unittest.TestCase):
    def test_dry_run_preserves_source(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'BlueFlatWrapper_CC4.py'
            p.write_text('COMPUTE_METRICS = False # evaluation\n',encoding='utf-8')
            x=patch(p,dry_run=True)
            self.assertEqual(x['change'],'would_enable')
            self.assertIn('False',''.join(p.read_text()))
            self.assertFalse(p.with_suffix('.py.original.bak').exists())
    def test_patch_backup_and_idempotency(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'BlueFlatWrapper_CC4.py'
            original='COMPUTE_METRICS = False # evaluation\n'
            p.write_text(original,encoding='utf-8')
            x=patch(p)
            self.assertEqual(x['change'],'enabled')
            self.assertIn('COMPUTE_METRICS = True',p.read_text())
            self.assertEqual(Path(x['backup']).read_text(),original)
            self.assertEqual(patch(p)['change'],'already_enabled')
