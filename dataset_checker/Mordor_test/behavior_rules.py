"""Small, reviewable behavior hypotheses; NOT attack detection or ground truth.

Only Sysmon process-creation events are considered. Names in arbitrary message
text, file-access events, or unrelated providers do not activate these rules.
Benign administration can match every rule. No numeric confidence is implied.
"""
import re

RULES_VERSION = "mordor-behavior-v1"


def infer(fields):
    provider = str(fields.get("sourcename") or fields.get("providername") or "").lower()
    if provider != "microsoft-windows-sysmon" or str(fields.get("eventid")) != "1":
        return []
    image = str(fields.get("image") or "").strip().strip('"')
    executable = image.replace("\\", "/").rsplit("/", 1)[-1].lower()
    command = str(fields.get("commandline") or "").strip()
    if not command or command == "-":
        return []
    rules = {"systeminfo.exe": ("T1082", "systeminfo-process"),
             "whoami.exe": ("T1033", "whoami-process"),
             "tasklist.exe": ("T1057", "tasklist-process")}
    match = rules.get(executable)
    if executable == "cmd.exe" and re.search(r"(?:^|\s)/[ck](?:\s|\")", command, re.I):
        match = ("T1059.003", "cmd-command-execution")
    if not match:
        return []
    technique, rule = match
    return [{"technique_id": technique, "rule_id": rule, "rules_version": RULES_VERSION,
             "evidence": {"provider": provider, "event_id": 1, "image": image, "command_line": command},
             "interpretation": "observed process consistent with technique; maliciousness and success unknown",
             "reference": "https://attack.mitre.org/techniques/" + technique.replace(".", "/") + "/"}]
