import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from analyze_comiset import analyze, labels


class AnalyzerTests(unittest.TestCase):
    def test_exact_length_counts_from_compressed_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            rows = []
            for process, size in enumerate((10, 2, 2, 1)):
                for n in range(size):
                    rows.append({'_id': f'{process}-{n}', '_source': {
                        'host_name': 'h', 'process_guid': str(process),
                        '@timestamp': f'2023-01-01T00:00:{n:02d}Z',
                        'rule_technique_id': ['T1105', 'T1059.001']}})
            rows.append(rows[0])
            with zipfile.ZipFile(base/'download.zip', 'w', zipfile.ZIP_DEFLATED) as z:
                z.writestr('nested/data.ndjson', '\n'.join(map(json.dumps, reversed(rows))))
            result = analyze(base/'download.zip', base/'raw')
            expected = [{'sequence_length': n, 'sequence_count': c}
                        for n, c in ((1, 1), (2, 2), (10, 1))]
            self.assertEqual(result['sequence_length_counts'], expected)
            self.assertTrue(result['complete_archive_scan'])
            self.assertEqual(sum(r['sequence_length'] * r['sequence_count']
                                 for r in expected), result['counts']['events_kept'])
            with (base/'raw'/'sequence_length_counts.csv').open(newline='') as f:
                self.assertEqual(list(csv.reader(f)), [
                    ['sequence_length', 'sequence_count'], ['1', '1'], ['2', '2'], ['10', '1']])
            report = (base/'raw'/'RESULTS.md').read_text()
            self.assertIn('| 2 | 2 |', report)
            self.assertNotIn('Mean length', report)
            collapsed = analyze(base/'download.zip', base/'collapsed',
                                length_metric='collapsed_label_steps')
            self.assertEqual(collapsed['sequence_length_counts'],
                             [{'sequence_length': 1, 'sequence_count': 4}])
            partial = analyze(base/'download.zip', base/'partial', max_lines=1)
            self.assertFalse(partial['complete_archive_scan'])
            self.assertIn('PARTIAL SMOKE TEST', (base/'partial'/'RESULTS.md').read_text())

    def test_empty_and_gap_split_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            with zipfile.ZipFile(base/'empty.zip', 'w') as z:
                z.writestr('data.json', '{}\ninvalid')
            result = analyze(base/'empty.zip', base/'empty')
            self.assertEqual(result['sequence_length_counts'], [])
            self.assertIn('No usable sequences', (base/'empty'/'RESULTS.md').read_text())
            rows = [{'_source': {'host_name': 'h', 'process_guid': 'p',
                     '@timestamp': f'2023-01-01T{hour:02d}:00:00Z',
                     'rule_technique_id': 'T1105'}} for hour in (0, 1)]
            with zipfile.ZipFile(base/'gap.zip', 'w') as z:
                z.writestr('data.json', '\n'.join(map(json.dumps, rows)))
            result = analyze(base/'gap.zip', base/'split', gap_minutes=30)
            self.assertEqual(result['sequence_length_counts'],
                             [{'sequence_length': 1, 'sequence_count': 2}])

    def test_repetitions_multilabel_and_missing_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            rows = []
            for i, ids in enumerate(['T1105', 'T1105', ['T1059.001', 'T1105']]):
                rows.append({'_id': str(i), '_source': {
                    'host_name': 'h', 'process_guid': 'p',
                    '@timestamp': f'2023-01-01T00:00:0{i}Z', 'rule_technique_id': ids}})
            rows.append({'_source': {'rule_technique_id': 'T1105'}})
            with zipfile.ZipFile(base/'sample.zip', 'w') as z:
                z.writestr('data.json', '\n'.join(json.dumps(r) for r in rows) + '\ninvalid')
            result = analyze(base/'sample.zip', base/'out')
            self.assertEqual(result['metrics']['raw_events']['max'], 3)
            self.assertEqual(result['metrics']['collapsed_label_steps']['max'], 2)
            self.assertEqual(result['metrics']['unambiguous_collapsed_sequences']['count'], 0)
            self.assertEqual(result['counts']['missing_host_or_process_guid'], 1)
            self.assertEqual(result['counts']['malformed_json_lines'], 1)
            record = json.loads((base/'out'/'sequences.jsonl').read_text())
            self.assertIsNone(record['scalar_sequence'])

    def test_labels(self):
        self.assertEqual(labels("['T1059.001', 'T1105']"), ['T1059.001', 'T1105'])

    def test_thresholds_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            rows = []
            for size in (25, 26, 30, 31):
                for n in reversed(range(size)):
                    rows.append({"_id": f"{size}-{n}", "_source": {
                        "host_name": "host", "process_guid": str(size),
                        "@timestamp": f"2023-01-01T00:00:{n:02d}Z",
                        "rule_technique_id": "T1105" if n % 2 else "T1059.001"}})
            rows.append(rows[0])
            with zipfile.ZipFile(base / "sample.zip", "w") as z:
                z.writestr("dataset.json", '\n'.join(json.dumps(r) for r in rows))
            result = analyze(base / "sample.zip", base / "out")
            stats = result['metrics']['unambiguous_collapsed_sequences']
            self.assertEqual(stats['more_than_25'], 3)
            self.assertEqual(stats['more_than_30'], 1)
            self.assertEqual(result['counts']['duplicate_records'], 1)
            seqs = [json.loads(s) for s in (base/'out'/'sequences.jsonl').read_text().splitlines()]
            self.assertEqual(seqs[0]['scalar_sequence'][0], 'T1059.001')
            partial = analyze(base/'sample.zip', base/'partial', max_lines=1)
            self.assertFalse(partial['complete_archive_scan'])


if __name__ == '__main__':
    unittest.main()
