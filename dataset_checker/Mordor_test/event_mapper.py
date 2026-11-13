"""Versioned, evidence-bearing ATT&CK behavior annotations for Windows telemetry.

These predicates describe behavior consistent with a technique. They do not
establish adversarial intent, execution success, or complete ATT&CK coverage.
No event ID alone, network port alone, or metadata inventory triggers a label.
"""
import re

VERSION = "mordor-event-mapper-1.0"


def canonical(fields):
    """Accept flat/nested exports, excluding ambiguous colliding leaf fields."""
    values = {}
    for key, value in fields.items():
        leaf = key.rsplit(".", 1)[-1].lower()
        if value is not None and str(value).strip() not in ("", "-"):
            values.setdefault(leaf, []).append(value)
    return {k: v[0] for k, v in values.items() if all(x == v[0] for x in v)}


def annotate(fields):
    f = canonical(fields)
    def get(*keys):
        return next((str(f[k]).strip() for k in keys if k in f), "")
    provider = get("sourcename", "providername").lower()
    channel = get("channel").lower()
    event_id = get("eventid", "event_id", "eventcode")
    sysmon = provider == "microsoft-windows-sysmon"
    security = provider == "microsoft-windows-security-auditing"
    powershell = provider in {"microsoft-windows-powershell", "powershell"}
    image = get("image", "newprocessname")
    executable = image.strip('"').replace("\\", "/").rsplit("/", 1)[-1].lower()
    command = get("commandline", "processcommandline")
    matches = []
    def add(rule, technique, reason, **evidence):
        matches.append({"rule_id": rule, "technique_id": technique, "mapper_version": VERSION,
                        "evidence": dict(provider=provider, event_id=event_id, channel=channel, **evidence),
                        "reason": reason, "label_source": "rule_based_annotation",
                        "validation_status": "requires_review_not_ground_truth",
                        "reference": "https://attack.mitre.org/techniques/" + technique.replace(".", "/") + "/"})
    creation = (sysmon and event_id == "1") or (security and event_id == "4688")
    if creation and image and command:
        evidence = {"image": image, "command_line": command}
        # Help/version invocations are not evidence of the tool's principal behavior.
        help_only = bool(re.search(r"(?:^|\s)(?:/\?|--help|-h)(?:\s|$)", command, re.I))
        if not help_only:
            simple = {"systeminfo.exe": ("T1082", "system-information"),
                      "whoami.exe": ("T1033", "current-user"),
                      "tasklist.exe": ("T1057", "process-list"),
                      "ipconfig.exe": ("T1016", "network-configuration"),
                      "netstat.exe": ("T1049", "network-connections")}
            if executable in simple:
                tid, rule = simple[executable]
                add("process-" + rule, tid, "Process creation of a discovery utility", **evidence)
        if executable == "cmd.exe" and re.search(r"(?:^|\s)/[ck](?:\s|\")", command, re.I):
            add("process-cmd-command", "T1059.003", "Command shell invoked with execution arguments", **evidence)
        if executable in {"powershell.exe", "pwsh.exe"} and re.search(r"(?:^|\s)-(?:command|c|encodedcommand|enc|file|f)\s+\S", command, re.I):
            add("process-powershell-execution", "T1059.001", "PowerShell command or script invocation", **evidence)
        if executable in {"cscript.exe", "wscript.exe"}:
            if re.search(r"\.vbs(?:\"|\s|$)", command, re.I):
                add("process-vbscript", "T1059.005", "Script host invoked with a VBScript path", **evidence)
            if re.search(r"\.js(?:\"|\s|$)", command, re.I):
                add("process-jscript", "T1059.007", "Script host invoked with a JavaScript path", **evidence)
        if executable == "schtasks.exe" and re.search(r"\s/create\b", command, re.I) and re.search(r"\s/tr\s+", command, re.I):
            add("process-task-create", "T1053.005", "Scheduled task creation with an action", **evidence)
        if executable == "reg.exe" and re.search(r"\squery\s", command, re.I):
            add("process-registry-query", "T1012", "Registry query command", **evidence)
        if executable == "sc.exe" and re.search(r"\screate\s", command, re.I) and "binpath" in command.lower():
            add("process-service-create", "T1543.003", "Service creation command with binary path", **evidence)
        if executable in {"procdump.exe", "procdump64.exe"} and re.search(r"\blsass(?:\.exe)?\b", command, re.I) and re.search(r"\s-m[a-z]*\b", command, re.I):
            add("process-lsass-dump", "T1003.001", "Dump utility invoked against LSASS", **evidence)
        if executable == "wevtutil.exe" and re.search(r"\s(?:cl|clear-log)\s+", command, re.I):
            add("process-clear-log", "T1070.001", "Event log clear command", **evidence)
    if powershell and event_id == "4104":
        script = get("scriptblocktext")
        if script:
            add("powershell-scriptblock", "T1059.001", "PowerShell script-block telemetry; may include benign scripts",
                script_block=script, script_block_id=get("scriptblockid"), message_number=get("messagenumber"))
            if re.search(r"\b(?:Invoke-WebRequest|Start-BitsTransfer)\b[^\r\n]*https?://", script, re.I) or re.search(r"\.(?:DownloadString|DownloadFile)\s*\(\s*['\"]https?://", script, re.I):
                add("powershell-download", "T1105", "Transfer expression in recorded script; completion not proven", script_block=script)
    if security and event_id == "4698":
        content = get("taskcontent")
        if get("taskname") and re.search(r"<(?:\w+:)?Command>", content, re.I):
            add("security-task-created", "T1053.005", "Task creation record with executable action", task_name=get("taskname"), task_content=content)
    if security and event_id == "4624" and get("logontype") == "10" and get("ipaddress", "sourceaddress") not in {"", "127.0.0.1", "::1"}:
        add("security-rdp-logon", "T1021.001", "Remote-interactive logon; legitimate logons also match",
            logon_type="10", source_address=get("ipaddress", "sourceaddress"), target_user=get("targetusername"))
    if provider == "service control manager" and event_id == "7045" and get("servicename") and get("imagepath", "servicefilename"):
        add("system-service-installed", "T1543.003", "Service installation record; may be legitimate",
            service_name=get("servicename"), binary_path=get("imagepath", "servicefilename"))
    if sysmon and event_id == "13":
        target = get("targetobject")
        if re.search(r"\\software\\microsoft\\windows\\currentversion\\run(?:once)?\\", target, re.I) and get("details"):
            add("sysmon-runkey-write", "T1547.001", "Run/RunOnce value written; malicious persistence not established", target_object=target, details=get("details"))
    if sysmon and event_id == "3" and get("initiated").lower() == "true" and get("destinationip"):
        if executable in {"ssh.exe", "plink.exe"} and get("destinationport") == "22":
            add("sysmon-ssh-connection", "T1021.004", "SSH client outbound connection; successful login not established",
                image=image, destination_ip=get("destinationip"), destination_port="22")
    return matches


def metadata_comparison(expected, observed):
    """Consistency only: overlap is not independent validation of detections."""
    return {"expected_techniques": sorted(expected), "annotated_techniques": sorted(observed),
            "exact_overlap": sorted(expected & observed), "expected_not_observed": sorted(expected - observed),
            "outside_inventory": sorted(observed - expected),
            "interpretation": "metadata consistency check, not precision/recall or validated execution"}
