import unittest
from event_mapper import annotate, metadata_comparison


class EventMapperTests(unittest.TestCase):
    def labels(self, event):
        return {m["technique_id"] for m in annotate(event)}

    def process(self, image, command, provider="Microsoft-Windows-Sysmon", event="1"):
        return {"sourcename": provider, "eventid": event, "image": image, "commandline": command}

    def test_process_creation_supported_behaviors(self):
        cases = [
            ("systeminfo.exe", "systeminfo", "T1082"),
            ("whoami.exe", "whoami /all", "T1033"),
            ("tasklist.exe", "tasklist /v", "T1057"),
            ("ipconfig.exe", "ipconfig /all", "T1016"),
            ("netstat.exe", "netstat -ano", "T1049"),
            ("cmd.exe", "cmd.exe /c dir", "T1059.003"),
            ("powershell.exe", "powershell -File script.ps1", "T1059.001"),
            ("wscript.exe", 'wscript "test.vbs"', "T1059.005"),
            ("cscript.exe", 'cscript test.js', "T1059.007"),
            ("schtasks.exe", "schtasks /create /tn example /tr cmd.exe", "T1053.005"),
            ("reg.exe", "reg query HKLM", "T1012"),
            ("sc.exe", "sc create example binpath= app.exe", "T1543.003"),
            ("procdump64.exe", "procdump64 -ma lsass.exe out.dmp", "T1003.001"),
            ("wevtutil.exe", "wevtutil cl Security", "T1070.001"),
        ]
        for image, command, technique in cases:
            with self.subTest(image=image):
                self.assertIn(technique, self.labels(self.process(image, command)))
                self.assertEqual(self.labels(self.process(image, command, event="10")), set())
                self.assertEqual(self.labels(self.process(image, command, provider="Other")), set())

    def test_security_process_creation_aliases(self):
        self.assertEqual(self.labels({"sourcename": "Microsoft-Windows-Security-Auditing", "eventid": 4688,
            "newprocessname": "C:\\Windows\\System32\\systeminfo.exe", "commandline": "systeminfo"}), {"T1082"})

    def test_powershell_and_service_and_task(self):
        e = {"sourcename": "Microsoft-Windows-PowerShell", "eventid": 4104,
             "scriptblocktext": "Invoke-WebRequest https://example.test/payload"}
        self.assertEqual(self.labels(e), {"T1059.001", "T1105"})
        self.assertEqual(self.labels(dict(e, scriptblocktext="Write-Output 'hello'")), {"T1059.001"})
        self.assertEqual(self.labels(dict(e, eventid=4103)), set())
        self.assertEqual(self.labels({"sourcename": "Microsoft-Windows-Security-Auditing", "eventid": 4698,
            "taskname": "test", "taskcontent": "<Actions><Exec><Command>cmd.exe</Command></Exec></Actions>"}), {"T1053.005"})
        self.assertEqual(self.labels({"sourcename": "Service Control Manager", "eventid": 7045,
            "servicename": "test", "imagepath": "C:\\test.exe"}), {"T1543.003"})

    def test_network_requires_context(self):
        e = {"sourcename": "Microsoft-Windows-Sysmon", "eventid": 3, "image": "ssh.exe",
             "initiated": "true", "destinationip": "192.0.2.1", "destinationport": 22}
        self.assertEqual(self.labels(e), {"T1021.004"})
        self.assertEqual(self.labels(dict(e, image="browser.exe")), set())
        self.assertEqual(self.labels(dict(e, initiated="false")), set())
        e = {"sourcename": "Microsoft-Windows-Security-Auditing", "eventid": 4624, "logontype": 10, "ipaddress": "192.0.2.1"}
        self.assertEqual(self.labels(e), {"T1021.001"})
        self.assertEqual(self.labels(dict(e, logontype=3)), set())

    def test_runkey_requires_write_and_value(self):
        e = {"sourcename": "Microsoft-Windows-Sysmon", "eventid": 13,
             "targetobject": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Example", "details": "C:\\app.exe"}
        self.assertEqual(self.labels(e), {"T1547.001"})
        self.assertEqual(self.labels(dict(e, details="")), set())
        self.assertEqual(self.labels(dict(e, eventid=12)), set())

    def test_no_free_text_or_help_matching(self):
        self.assertEqual(self.labels({"message": "powershell mimikatz lsass.exe"}), set())
        self.assertEqual(self.labels(self.process("not-systeminfo.exe", "systeminfo")), set())
        self.assertEqual(self.labels(self.process("systeminfo.exe", "systeminfo /?")), set())
        self.assertEqual(self.labels(self.process("procdump.exe", "procdump -ma other.exe")), set())
        self.assertEqual(self.labels(self.process("powershell.exe", "powershell.exe")), set())

    def test_provenance_and_metadata_does_not_add_labels(self):
        matches = annotate(self.process("systeminfo.exe", "systeminfo"))
        self.assertEqual(matches[0]["evidence"]["image"], "systeminfo.exe")
        self.assertIn("mapper_version", matches[0])
        comparison = metadata_comparison({"T1003.001"}, {"T1082"})
        self.assertEqual(comparison["exact_overlap"], [])
        self.assertEqual(comparison["outside_inventory"], ["T1082"])
        self.assertEqual(comparison["expected_not_observed"], ["T1003.001"])


if __name__ == "__main__":
    unittest.main()
