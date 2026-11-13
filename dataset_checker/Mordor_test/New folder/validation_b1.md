# Mordor B1 Validation

## Scope and method

This review covers all 11 ordered B1 sessions in `raw_telemetry/annotated/sequences.json`.
For each generated step, the normalized event was joined to the original archive member using
`file` and `record_index`. The original record was checked for timestamp, host, provider,
event ID, process, command line, or script content. Metadata comparison uses
`raw_telemetry/annotated/metadata_comparison.json`.

The labels are mapper annotations, not ground-truth labels. `Validated` below means that the
recorded behavior is directly supported and the chain is operationally coherent; it does not
prove attacker intent, successful execution, or that the entire capture is malicious.

## Results

| Sequence | Capture / host | Techniques | Metadata overlap | Evidence checked | Result |
|-|-|-|-|-|-|
| B1-01 | LSASS_campaign_01 / mkt01 | T1059.001 -> T1082 -> T1033 -> T1059.001 -> T1057 -> T1543.003 -> T1033 -> T1059.001 -> T1059.005 -> T1059.003 -> T1082 -> T1059.003 -> T1057 -> T1059.003 -> T1016 -> T1059.003 -> T1059.001 | T1033, T1057, T1082 | PowerShell 4104, systeminfo, whoami, tasklist, service 7045, cscript, cmd, ipconfig; records 50622-50676 | **Uncertain**: coherent discovery and execution activity, but most labels are outside the metadata inventory and the service record lacks sufficient context to establish persistence. |
| B1-02 | LSASS_campaign_02 / acct01 | T1059.001 -> T1082 -> T1033 -> T1003.001 -> T1059.005 -> T1059.003 -> T1082 -> T1059.003 -> T1057 -> T1059.001 | T1003.001, T1033, T1082 | PowerShell 4104, systeminfo, whoami, `procdump.exe -accepteula -ma lsass.exe ...lsass_dump.dmp`, cscript, cmd, tasklist; records 39411-39444 | **Validated behavioral chain**: direct LSASS dump command is present, the order is plausible, and the dump technique plus discovery techniques overlap metadata. Intent and success still require qualification. |
| B1-03 | LSASS_campaign_03 / prd01 | T1059.001 -> T1082 -> T1033 -> T1057 -> T1543.003 -> T1059.001 -> T1059.005 -> T1059.003 -> T1082 -> T1059.003 -> T1059.001 | T1033, T1057, T1082, T1543.003 | PowerShell 4104 with encoded IEX, systeminfo, whoami, tasklist, service 7045, cscript, cmd; records 38842-38922 and 35160-38353 | **Uncertain**: plausible discovery-to-service sequence and four metadata overlaps, but the service details and encoded script outcome are not enough to prove an attack. |
| B1-04 | LSASS_campaign_04 / it01 | T1059.001 -> T1082 -> T1033 -> T1059.001 | T1033, T1082 | PowerShell 4104, systeminfo, whoami, encoded IEX PowerShell; records 37308-37314 and 1044-1140 | **Uncertain**: concrete discovery and PowerShell evidence, but no direct credential-dumping evidence and only partial metadata overlap. |
| B1-05 | LSASS_campaign_05 / mkt01 | T1082 -> T1033 -> T1012 -> T1059.005 -> T1059.003 -> T1059.001 | T1012, T1033, T1082 | systeminfo, whoami, `reg query HKLM\Software\Microsoft\Net Framework Setup\NDP /s`, cscript, cmd/gpresult, PowerShell 4104; records 20152-59599 | **Uncertain**: commands are real and the sequence is reconnaissance-consistent, but no attack-specific objective is established. |
| B1-06 | LSASS_campaign_06 / mkt01 | T1082 -> T1033 -> T1059.001 | T1033, T1082 | systeminfo, whoami, PowerShell 4104; records 17255, 20542, 57983 | **Uncertain**: discovery is directly evidenced, but the final PowerShell script block is generic and metadata lacks a matching execution objective. |
| B1-07 | LSASS_campaign_07 / mkt01 | T1082 -> T1033 -> T1059.001 | T1033, T1082 | systeminfo, whoami, PowerShell 4104; records 17298, 20547, 57614 | **Uncertain**: same limitation as B1-06; behavior is supported, attack interpretation is not. |
| B1-08 | apt29 day1 / nashua | T1059.001 -> T1543.003 -> T1059.001 | None; no matching metadata capture | PowerShell `Get-Process`, Service Control Manager 7045, PowerShell `prompt`; records 90851, 94192, 103508 | **Uncertain / not validated**: a service-install event exists, but its service details are not sufficient here to distinguish persistence from legitimate administration. |
| B1-09 | apt29 day1 / newyork | T1059.001 | None; no matching metadata capture | PowerShell 4104 localized feature-install/help text; record 34966 | **Not validated**: one generic script-block event does not establish an attack sequence. |
| B1-10 | apt29 day1 / scranton | T1059.001 -> T1543.003 -> T1059.001 -> T1547.001 -> T1016 -> T1059.003 -> T1021.001 -> T1016 -> T1059.003 -> T1059.001 -> T1059.003 -> T1059.001 -> T1059.003 -> T1059.001 | None; no matching metadata capture | PowerShell persistence text, Service Control Manager 7045, Run key write, ipconfig, Azure domain-extension commands, RDP logon, Defender `MsMpEng.exe`; records 1043-183900 | **Not validated; likely benign administrative activity**: Azure extension paths, Defender process context, and generic RDP/logon telemetry explain the chain better than an attack interpretation. |
| B1-11 | apt29 day2 / newyork | T1059.001 | None; no matching metadata capture | PowerShell 4104 `$executionContext.SessionState.LanguageMode`; record 248173 | **Not validated**: a single language-mode query is insufficient evidence of an attack. |

## Representative evidence traces

The following traces show the raw evidence for all long B1 chains and representative short chains.
Times are Unix timestamps as stored in the generated event data; the host is the sequence host.

### B1-02: strongest candidate

```text
Host: acct01.pandalab.com
T1059.001 | 1692077631.746 | PowerShell 4104 | command: prompt | record 39411
T1082     | 1692077701.615 | Security 4688 | systeminfo.exe: systeminfo | record 918
T1033     | 1692077711.671 | Security 4688 | whoami.exe: whoami | record 991
T1003.001 | 1692077867.023 | Security 4688 | procdump.exe: -accepteula -ma lsass.exe C:\Windows\Temp\lsass_dump.dmp | record 1081
T1059.005 | 1692078011.504 | Sysmon 1 | cscript.exe gatherNetworkInfo.vbs | record 34935
T1059.003 | 1692078013.067 | Sysmon 1 | cmd.exe /c gpresult /scope:computer /v | record 35111
T1082     | 1692078024.435 | Sysmon 1 | systeminfo.exe: systeminfo | record 37828
T1059.003 | 1692078027.081 | Sysmon 1 | cmd.exe /c set u >> config\osinfo.txt | record 38285
T1057     | 1692078028.056 | Sysmon 1 | tasklist.exe: tasklist /svc | record 38494
T1059.001 | 1692078100.743 | PowerShell 4104 | Get-NetAdapter/Get-NetAdapterBinding script block | record 39444
```

Assessment: the LSASS target and dump output path are explicit, unlike an inference-only match.
The sequence moves from shell/discovery to credential-access tooling and then collection of host
information. This is the only B1 sequence that can be called validated behavioral evidence with
high confidence from the inspected sample.

### B1-01: long chain

```text
Host: mkt01.pandalab.com
T1059.001 -> T1082 -> T1033 -> T1059.001 -> T1057 -> T1543.003 -> T1033
  -> T1059.001 -> T1059.005 -> T1059.003 -> T1082 -> T1059.003 -> T1057
  -> T1059.003 -> T1016 -> T1059.003 -> T1059.001

Key raw records:
T1082     | 1692093298.252 | systeminfo.exe systeminfo | record 1016
T1033     | 1692093307.041 | whoami.exe whoami | record 1073
T1057     | 1692093331.379 | tasklist.exe /fo table /svc | record 1936
T1543.003 | 1692093375.588 | Service Control Manager 7045 | record 50145
T1059.005 | 1692093568.237 | cscript.exe gatherNetworkInfo.vbs | record 37319
T1059.003 | 1692093569.931 | cmd.exe /c gpresult /scope:computer /v | record 37445
T1016     | 1692093590.617 | ipconfig.exe /all | record 43242
```

Assessment: the discovery order makes operational sense, but the initial `prompt` script block,
service event, and PowerShell telemetry are not enough to prove malicious persistence. The chain
is uncertain, with only three exact metadata overlaps.

### B1-03: long chain

```text
Host: prd01.pandalab.com
T1059.001 -> T1082 -> T1033 -> T1057 -> T1543.003 -> T1059.001
  -> T1059.005 -> T1059.003 -> T1082 -> T1059.003 -> T1059.001

Key raw records:
T1082     | 1692349022.814 | systeminfo.exe systeminfo | record 773
T1033     | 1692349031.048 | whoami.exe whoami | record 914
T1057     | 1692349052.319 | tasklist.exe /fo table /svc /fi "USERNAME eq NT AUTHORITY\SYSTEM" | record 955
T1543.003 | 1692349091.729 | Service Control Manager 7045 | record 38353
T1059.005 | 1692349389.994 | cscript.exe gatherNetworkInfo.vbs | record 35160
T1059.003 | 1692349391.782 | cmd.exe /c gpresult /scope:computer /v | record 35290
```

Assessment: concrete process and service records support the behavior, and four techniques
overlap metadata. The encoded PowerShell and service record require further inspection before
calling this an attack.

### B1-05: shorter representative

```text
Host: mkt01.pandalab.com
T1082     | 1693907630.429 | systeminfo.exe systeminfo | record 20152
T1033     | 1693907652.517 | whoami.exe whoami | record 23236
T1012     | 1693907691.253 | reg.exe query HKLM\Software\Microsoft\Net Framework Setup\NDP /s | record 28070
T1059.005 | 1693907930.007 | cscript.exe gatherNetworkInfo.vbs | record 57770
T1059.003 | 1693907930.882 | cmd.exe /c gpresult /scope:computer /v | record 57897
T1059.001 | 1693908053.823 | PowerShell Get-NetAdapter script block | record 59599
```

Assessment: this is a credible host-reconnaissance sequence, but reconnaissance alone does not
establish an attack. Mark uncertain rather than validated.

### B1-08: service-event representative

```text
Host: nashua.dmevals.local
T1059.001 | 1588388969.929 | PowerShell Get-Process -IncludeUserName ... | record 90851
T1543.003 | 1588389101.241 | Service Control Manager event 7045 | record 94192
T1059.001 | 1588389349.964 | PowerShell script block: prompt | record 103508
```

Assessment: the service event is real, but no service name or image path was used to establish
malicious persistence. There is also no matching scenario metadata, so this remains unvalidated.

### B1-10: long chain rejected as attack evidence

```text
Host: scranton.dmevals.local
T1059.001 | 1588388176.968 | PowerShell script block: prompt | record 1043
T1543.003 | 1588388656.785 | Service Control Manager event 7045 | record 50937
T1547.001 | 1588389601.436 | Sysmon 13, MsMpEng.exe Run-key write | record 133335
T1016     | 1588389606.765 | ipconfig.exe /all | record 135565
T1059.003 | 1588389647.249 | cmd.exe /c Azure JsonADDomainExtension enable.cmd | record 155584
T1021.001 | 1588389649.428 | Security 4624 type-10 logon | record 156970
T1016     | 1588389672.910 | ipconfig.exe /all | record 163152
T1059.001 | 1588389679.896 | powershell.exe -c Start-Process ...hostui.exe -verb runas | record 166205
T1059.003 | 1588389683.299 | cmd.exe /c Azure JsonADDomainExtension enable.cmd | record 167463
T1059.003 | 1588389693.629 | cmd.exe /c Azure CustomScriptExtension enable.cmd | record 170833
```

Assessment: timestamps and commands are genuine, but the Azure extension paths, Defender binary,
and infrastructure activity provide a stronger benign explanation than an attack chain. This is
an important false-positive control case.

## Thesis-ready conclusion

| Category | Count | Interpretation |
|-|-|-|
| Validated behavioral chain | 1 | B1-02, explicit LSASS dump command, plausible order, metadata overlap |
| Uncertain | 7 | Direct evidence exists, but attack intent, service details, or script outcome remain unresolved |
| Not validated / likely benign | 3 | Generic single events or infrastructure/Defender activity; no defensible attack claim |

The B1 reconstruction is useful for locating candidate attack behavior, but it should not be
reported as 11 validated attacks. The defensible conclusion is that one sequence provides strong
validated behavioral evidence, while the remaining sequences require additional context or are
better explained as benign/system activity. B2 should inherit these caveats because it is an
uncertainty-aware representation of the same events, and B3 should remain excluded from primary
validation because its labels are inferred hypotheses rather than ground truth.