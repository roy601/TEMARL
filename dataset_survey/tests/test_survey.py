"""Tests for the dataset reader, on small made-up archives.

    python -m unittest discover -s dataset_survey/tests
"""
import gzip
import io
import json
import os
import sys
import tarfile
import tempfile
import unittest
import zipfile
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import survey as S  # noqa: E402


def zip_bytes(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return b.getvalue()


class Reader(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "data")
        os.makedirs(self.data)

    def scan(self, only=None):
        return S.scan(self.data, os.path.join(self.tmp.name, "tmp"), only)

    def put(self, name, data):
        path = os.path.join(self.data, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)

    def test_counts_every_file_line_and_byte_also_in_nested_archives(self):
        inner = zip_bytes({"run1/a.log": b"one\ntwo\nthree\n", "run2/a.log": b"x\ny"})
        self.put("outer.zip", zip_bytes({"logs.zip": inner, "readme.txt": b"hello\n", "blob.bin": b"\x00\x01\x02" * 10}))
        sc = self.scan()
        self.assertEqual(sc.tot["files"], 4)
        self.assertEqual(sc.tot["lines"], 3 + 2 + 1)
        self.assertEqual(sc.tot["bytes"], 14 + 3 + 6 + 30)
        self.assertEqual(sc.tot["binary"], 1)
        self.assertEqual(sc.tot["archives"], 2)
        self.assertEqual(sc.tot["read_errors"], 0)
        self.assertEqual(sc.classes["outer.zip::logs.zip::run#/a.log"]["files"], 2)      # grouped by pattern

    def test_reads_tar_gz_and_plain_gz(self):
        b = io.BytesIO()
        with tarfile.open(fileobj=b, mode="w:gz") as t:
            info = tarfile.TarInfo("d/x.txt")
            info.size = 4
            t.addfile(info, io.BytesIO(b"a\nb\n"))
        self.put("pack.tar.gz", b.getvalue())
        self.put("single.log.gz", gzip.compress(b"l1\nl2\nl3\n"))
        sc = self.scan()
        self.assertEqual((sc.tot["files"], sc.tot["lines"], sc.tot["read_errors"]), (2, 5, 0))

    def test_finds_technique_ids_even_across_read_blocks(self):
        old = S.CHUNK
        S.CHUNK = 64                                            # force many small blocks
        try:
            lines = [f"step {i} used T1059.004 and T1105 then xT1000x {'pad' * 9}\n" for i in range(50)]
            self.put("a.log", "".join(lines).encode())
            sc = self.scan()
        finally:
            S.CHUNK = old
        c = sc.classes["a.log"]
        self.assertEqual(dict(c["tech"]), {"T1059.004": 50, "T1105": 50})      # xT1000x is not an ID
        self.assertEqual(c["lines"], 50)
        self.assertEqual(c["tech_per_file"], [100])

    def test_csv_fields_and_ragged_rows(self):
        self.put("labels.csv", b"scenario;technique;n\ns1;T1059;1\ns1;T1105;2\ns2;T1059;3\nbroken;row\n")
        c = self.scan().classes["labels.csv"]
        self.assertEqual((c["kind"], c["rows"], c["parsed"], c["ragged"]), ("csv", 4, 4, 1))
        self.assertEqual(c["fields"]["technique"]["tech"], 3)
        self.assertEqual(len(c["fields"]["scenario"]["vals"]), 2)

    def test_csv_records_with_line_breaks_inside_quotes(self):
        data = (b'id,message,technique\r\n'
                b'1,"Process created:\r\n\r\nImage: cmd.exe",T1059\r\n'
                b'2,"he said ""hi""\r\nthen left",T1105\r\n'
                b'3,plain,T1083\r\n')
        old = S.CHUNK
        for chunk in (old, 16):                                  # also when blocks split a record
            S.CHUNK = chunk
            try:
                self.put("ev.csv", data)
                c = self.scan().classes["ev.csv"]
            finally:
                S.CHUNK = old
            self.assertEqual((c["rows"], c["parsed"], c["ragged"]), (3, 3, 0), chunk)
            self.assertEqual(c["fields"]["technique"]["tech"], 3)
            self.assertEqual(c["lines"], 7)                      # physical lines are still counted

    def test_an_unclosed_quote_counts_one_bad_record(self):
        self.put("bad.csv", b'a,b\n1,"never closed\n2,x\n')
        c = self.scan().classes["bad.csv"]
        self.assertEqual((c["rows"], c["ragged"]), (1, 1))

    def test_json_lines_and_whole_json_documents(self):
        self.put("a.jsonl", b'{"cmd": "ls", "meta": {"technique": "T1083"}}\n{"cmd": "id"}\nnot json\n')
        self.put("doc.json", json.dumps({"records": [{"k": 1}, {"k": 2}, {"k": 3}]}, indent=2).encode())
        sc = self.scan()
        a, d = sc.classes["a.jsonl"], sc.classes["doc.json"]
        self.assertEqual((a["kind"], a["parsed"], a["ragged"]), ("jsonl", 3, 1))
        self.assertEqual(a["fields"]["meta.technique"]["tech"], 1)
        self.assertEqual((d["kind"], d["rows"]), ("json", 3))
        self.assertEqual(d["fields"]["k"]["filled"], 3)

    def test_json_document_inside_a_gz_is_parsed(self):
        doc = "[" + ",\n".join(json.dumps({"sig": f"s{i % 3}", "team": "t1"}) for i in range(30)) + "]"
        self.put("repo.zip", zip_bytes({"alerts/t1.json.gz": gzip.compress(doc.encode())}))
        c = self.scan().classes["repo.zip::alerts/t#.json"]
        self.assertEqual((c["kind"], c["rows"]), ("json", 30))
        self.assertEqual(len(c["fields"]["sig"]["vals"]), 3)

    def test_counts_lines_that_are_not_utf8(self):
        self.put("x.log", b"good\n\xff\xfe bad\nalso good\n")
        sc = self.scan()
        self.assertEqual(sc.tot["bad_utf8"], 1)

    def test_a_damaged_member_is_reported_and_the_rest_is_still_read(self):
        z = bytearray(zip_bytes({"a.txt": b"A" * 5000, "b.txt": b"fine\n"}))
        z[40] ^= 0xFF                                           # corrupt the first member's data
        self.put("bad.zip", bytes(z))
        sc = self.scan()
        self.assertEqual(sc.tot["read_errors"], 1)
        self.assertEqual(sc.classes["bad.zip::b.txt"]["lines"], 1)

    def test_only_filter_and_report_files(self):
        self.put("repo.zip", zip_bytes({"r/alerts/t1.json": b'{"sig": "x"}\n', "r/code.py": b"print(1)\n"}))
        sc = self.scan(only="/alerts/")
        self.assertEqual((sc.tot["files"], sc.tot["skipped_files"]), (1, 1))
        out = os.path.join(self.tmp.name, "out")
        ds = {"name": "t", "title": "Test"}
        summ = S.write_report(ds, {"status": "downloaded", "note": "test", "files": []}, sc, out, 1.0)
        self.assertEqual(summ["files"], 1)
        text = open(os.path.join(out, "REPORT.txt"), encoding="utf-8").read()
        self.assertIn("none. This dataset has no technique IDs", text)
        json.load(open(os.path.join(out, "report.json"), encoding="utf-8"))

    def test_a_file_blocked_by_the_antivirus_is_recorded_and_the_rest_downloads(self):
        items = [{"name": "good.csv", "url": "u1", "size": 4, "algo": None, "digest": None},
                 {"name": "flagged.csv", "url": "u2", "size": 4, "algo": None, "digest": None}]

        def fake_fetch(item, dest):
            if item["name"] == "flagged.csv":
                return False, S.BLOCKED
            with open(dest, "wb") as fh:
                fh.write(b"a,b\n")
            return True, "downloaded"
        ds = {"name": "t", "title": "T", "source": ("zenodo", "1")}
        folder = os.path.join(self.tmp.name, "dl")
        with mock.patch.object(S, "listing", return_value=(items, "test source")), mock.patch.object(S, "fetch", fake_fetch):
            dl = S.download(ds, folder, False)
        self.assertEqual(dl["status"], "downloaded")
        self.assertEqual([f["download"] for f in dl["files"]], ["downloaded", S.BLOCKED])
        self.assertIn("WARNING: 1 of 2 files were blocked", dl["note"])
        sc = S.scan(folder, os.path.join(self.tmp.name, "tmp"))
        summ = S.write_report(ds, dl, sc, os.path.join(self.tmp.name, "out"), 1.0)
        self.assertEqual(summ["blocked_files"], 1)

    @unittest.skipUnless(os.name == "nt", "Windows error codes")
    def test_windows_errors_that_mean_blocked(self):
        self.assertTrue(S.blocked_by_antivirus(OSError(22, "Invalid argument")))
        self.assertTrue(S.blocked_by_antivirus(OSError(None, "virus", None, 225)))
        self.assertFalse(S.blocked_by_antivirus(OSError(2, "No such file")))

    def test_report_says_where_ids_sit_and_which_files_are_labels(self):
        self.put("alerts.jsonl", b'{"rule": {"mitre": {"id": ["T1078"]}}}\n')
        self.put("labels.csv", b"scenario,attack\ns1,scan\n")
        sc = self.scan()
        out = os.path.join(self.tmp.name, "out")
        S.write_report({"name": "t", "title": "T"}, {"status": "downloaded", "note": "n", "files": []}, sc, out, 1.0)
        text = open(os.path.join(out, "REPORT.txt"), encoding="utf-8").read()
        self.assertIn("CAUTION: an ID written in the data is not automatically a label", text)
        self.assertRegex(text, r"1\s+rule\.mitre\.id\[\]\s+alerts\.jsonl")
        self.assertRegex(text, r"3b\..*\n\s+labels\.csv\s+\(files 1, records 1, IDs 0\)")

    def test_long_tokens_are_masked_in_samples(self):
        self.assertIn("<token:40>", S.mask("key " + "A" * 40))


if __name__ == "__main__":
    unittest.main()
