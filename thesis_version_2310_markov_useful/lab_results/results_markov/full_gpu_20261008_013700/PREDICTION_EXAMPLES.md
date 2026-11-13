# Deterministic human-readable prediction examples

Same evenly spaced test-window indices for each model. No selection based on correctness. These are examples, not extra independent evaluations.

## markov_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (90.04%); T1201 Password Policy Discovery (9.56%); T1213 Data from Information Repositories (0.06%) | 90.04% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.58%); T1548 Abuse Elevation Control Mechanism (0.27%); T1036 Masquerading (0.06%) | 99.58% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.93%); T1033 System Owner/User Discovery (0.01%); T1049 System Network Connections Discovery (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (80.43%); T1592 Gather Victim Host Information (12.42%); T1190 Exploit Public-Facing Application (6.68%) | 80.43% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.25%); T1059 Command and Scripting Interpreter (4.25%); T1566 Phishing (0.18%) | 95.25% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (81.57%); T1059 Command and Scripting Interpreter (18.21%); T1082 System Information Discovery (0.08%) | 81.57% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.16%); T1124 System Time Discovery (0.15%); T1071 Application Layer Protocol (0.12%) | 99.16% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.73%); T1003 OS Credential Dumping (0.06%); T1083 File and Directory Discovery (0.03%) | 99.73% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (63.78%); T1041 Exfiltration Over C2 Channel (16.84%); T1548 Abuse Elevation Control Mechanism (3.51%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (25.51%); T1033 System Owner/User Discovery (23.29%); T1082 System Information Discovery (15.69%) | 0.00% | False |

## markov_100 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.79%); T1590 Gather Victim Network Information (2.93%); T1087 Account Discovery (0.02%) | 96.79% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.96%); T1548 Abuse Elevation Control Mechanism (0.44%); T1105 Ingress Tool Transfer (0.20%) | 98.96% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1016 System Network Configuration Discovery (0.03%); T1083 File and Directory Discovery (0.02%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (61.22%); T1592 Gather Victim Host Information (27.09%); T1190 Exploit Public-Facing Application (11.27%) | 61.22% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.05%); T1059 Command and Scripting Interpreter (4.49%); T1098 Account Manipulation (0.16%) | 95.05% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (54.12%); T1059 Command and Scripting Interpreter (45.57%); T1105 Ingress Tool Transfer (0.08%) | 54.12% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1124 System Time Discovery (0.02%); T1049 System Network Connections Discovery (0.02%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.95%); T1039 Data from Network Shared Drive (0.39%); T1201 Password Policy Discovery (0.09%) | 98.95% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (19.50%); T1059 Command and Scripting Interpreter (17.57%); T1565 Data Manipulation (9.65%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1518 Software Discovery (39.99%); T1082 System Information Discovery (24.98%); T1078 Valid Accounts (10.90%) | 0.01% | False |

## markov_100 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1136 Create Account (0.02%); T1599 Network Boundary Bridging (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.48%); T1548 Abuse Elevation Control Mechanism (0.16%); T1105 Ingress Tool Transfer (0.09%) | 99.48% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.81%); T1083 File and Directory Discovery (0.04%); T1057 Process Discovery (0.03%) | 99.81% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.41%); T1592 Gather Victim Host Information (1.10%); T1190 Exploit Public-Facing Application (0.18%) | 98.41% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.60%); T1059 Command and Scripting Interpreter (0.16%); T1071 Application Layer Protocol (0.09%) | 99.60% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.04%); T1059 Command and Scripting Interpreter (4.62%); T1105 Ingress Tool Transfer (0.17%) | 95.04% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1124 System Time Discovery (0.06%); T1566 Phishing (0.03%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.31%); T1003 OS Credential Dumping (0.12%); T1083 File and Directory Discovery (0.10%) | 99.31% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (56.25%); T1222 File and Directory Permissions Modification (15.01%); T1205 Traffic Signaling (5.50%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (26.15%); T1033 System Owner/User Discovery (20.88%); T1573 Encrypted Channel (10.28%) | 0.42% | False |

## markov_100 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.88%); T1105 Ingress Tool Transfer (0.03%); T1615 Group Policy Discovery (0.01%) | 99.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.77%); T1548 Abuse Elevation Control Mechanism (2.15%); T1105 Ingress Tool Transfer (0.56%) | 96.77% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1133 External Remote Services (0.02%); T1033 System Owner/User Discovery (0.02%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (76.35%); T1592 Gather Victim Host Information (14.82%); T1190 Exploit Public-Facing Application (8.50%) | 76.35% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.13%); T1059 Command and Scripting Interpreter (0.21%); T1556 Modify Authentication Process (0.12%) | 99.13% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (54.72%); T1087 Account Discovery (44.68%); T1105 Ingress Tool Transfer (0.26%) | 44.68% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.86%); T1124 System Time Discovery (0.06%); T1053 Scheduled Task/Job (0.03%) | 99.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.76%); T1204 User Execution (4.20%); T1021 Remote Services (0.15%) | 94.76% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (46.45%); T1531 Account Access Removal (37.69%); T1007 System Service Discovery (3.55%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (57.20%); T1003 OS Credential Dumping (8.62%); T1078 Valid Accounts (7.73%) | 0.00% | False |

## markov_100 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.55%); T1039 Data from Network Shared Drive (1.96%); T1110 Brute Force (0.06%) | 97.55% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.52%); T1548 Abuse Elevation Control Mechanism (1.14%); T1046 Network Service Scanning (0.05%) | 98.52% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1057 Process Discovery (0.03%); T1201 Password Policy Discovery (0.03%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.69%); T1190 Exploit Public-Facing Application (4.15%); T1592 Gather Victim Host Information (0.94%) | 94.69% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.74%); T1059 Command and Scripting Interpreter (2.24%); T1041 Exfiltration Over C2 Channel (0.18%) | 96.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.62%); T1059 Command and Scripting Interpreter (2.23%); T1105 Ingress Tool Transfer (0.02%) | 97.62% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.62%); T1124 System Time Discovery (0.13%); T1564 Hide Artifacts (0.03%) | 99.62% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.42%); T1033 System Owner/User Discovery (0.17%); T1039 Data from Network Shared Drive (0.16%) | 99.42% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (66.92%); T1036 Masquerading (10.91%); T1078 Valid Accounts (2.37%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (42.33%); T1547 Boot or Logon Autostart Execution (22.67%); T1546 Event Triggered Execution (8.94%) | 0.00% | False |

## markov_100 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1041 Exfiltration Over C2 Channel (0.01%); T1589 Gather Victim Identity Information (0.01%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.43%); T1548 Abuse Elevation Control Mechanism (0.20%); T1190 Exploit Public-Facing Application (0.07%) | 99.43% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.55%); T1133 External Remote Services (0.21%); T1219 Remote Access Tools (0.04%) | 99.55% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (88.18%); T1190 Exploit Public-Facing Application (10.00%); T1592 Gather Victim Host Information (1.56%) | 88.18% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.03%); T1059 Command and Scripting Interpreter (3.27%); T1547 Boot or Logon Autostart Execution (0.21%) | 96.03% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.63%); T1059 Command and Scripting Interpreter (4.98%); T1105 Ingress Tool Transfer (0.12%) | 94.63% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1070 Indicator Removal (0.05%); T1615 Group Policy Discovery (0.04%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.39%); T1021 Remote Services (0.08%); T1072 Software Deployment Tools (0.07%) | 99.39% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1566 Phishing (54.24%); T1083 File and Directory Discovery (10.73%); T1591 Gather Victim Org Information (10.49%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (24.09%); T1041 Exfiltration Over C2 Channel (14.49%); T1574 Hijack Execution Flow (13.21%) | 0.00% | False |

## markov_100 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.28%); T1074 Data Staged (2.45%); T1589 Gather Victim Identity Information (0.03%) | 97.28% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.52%); T1548 Abuse Elevation Control Mechanism (0.25%); T1105 Ingress Tool Transfer (0.08%) | 99.52% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.47%); T1589 Gather Victim Identity Information (0.27%); T1572 Protocol Tunneling (0.02%) | 99.47% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (74.28%); T1592 Gather Victim Host Information (15.44%); T1036 Masquerading (5.73%) | 74.28% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.69%); T1059 Command and Scripting Interpreter (3.10%); T1083 File and Directory Discovery (0.02%) | 96.69% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.30%); T1059 Command and Scripting Interpreter (4.45%); T1018 Remote System Discovery (0.04%) | 95.30% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.91%); T1059 Command and Scripting Interpreter (0.02%); T1049 System Network Connections Discovery (0.01%) | 99.91% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.91%); T1120 Peripheral Device Discovery (0.26%); T1039 Data from Network Shared Drive (0.17%) | 98.91% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1547 Boot or Logon Autostart Execution (91.15%); T1033 System Owner/User Discovery (0.86%); T1124 System Time Discovery (0.67%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1547 Boot or Logon Autostart Execution (83.51%); T1595 Active Scanning (2.77%); T1105 Ingress Tool Transfer (2.03%) | 0.07% | False |

## markov_100 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1007 System Service Discovery (0.03%); T1059 Command and Scripting Interpreter (0.03%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.50%); T1105 Ingress Tool Transfer (0.24%); T1548 Abuse Elevation Control Mechanism (0.16%) | 99.50% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1222 File and Directory Permissions Modification (0.02%); T1176 Software Extensions (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (92.72%); T1190 Exploit Public-Facing Application (6.78%); T1592 Gather Victim Host Information (0.14%) | 92.72% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.91%); T1059 Command and Scripting Interpreter (0.24%); T1222 File and Directory Permissions Modification (0.16%) | 98.91% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.16%); T1059 Command and Scripting Interpreter (5.59%); T1068 Exploitation for Privilege Escalation (0.07%) | 94.16% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1205 Traffic Signaling (0.14%); T1615 Group Policy Discovery (0.06%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.35%); T1039 Data from Network Shared Drive (0.25%); T1547 Boot or Logon Autostart Execution (0.09%) | 99.35% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1098 Account Manipulation (48.51%); T1010 Application Window Discovery (20.64%); T1591 Gather Victim Org Information (8.90%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1010 Application Window Discovery (44.10%); T1222 File and Directory Permissions Modification (24.48%); T1574 Hijack Execution Flow (5.96%) | 0.01% | False |

## markov_100 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1078 Valid Accounts (0.02%); T1055 Process Injection (0.02%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.56%); T1548 Abuse Elevation Control Mechanism (0.09%); T1105 Ingress Tool Transfer (0.08%) | 99.56% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1518 Software Discovery (0.02%); T1018 Remote System Discovery (0.02%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (84.17%); T1190 Exploit Public-Facing Application (9.32%); T1592 Gather Victim Host Information (6.00%) | 84.17% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.85%); T1059 Command and Scripting Interpreter (0.15%); T1213 Data from Information Repositories (0.12%) | 98.85% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.61%); T1059 Command and Scripting Interpreter (4.36%); T1105 Ingress Tool Transfer (0.86%) | 94.61% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1210 Exploitation of Remote Services (0.04%); T1219 Remote Access Tools (0.02%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.53%); T1120 Peripheral Device Discovery (0.23%); T1039 Data from Network Shared Drive (0.21%) | 98.53% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1566 Phishing (47.93%); T1222 File and Directory Permissions Modification (35.91%); T1219 Remote Access Tools (3.43%) | 0.56% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (32.03%); T1021 Remote Services (15.85%); T1531 Account Access Removal (7.58%) | 0.02% | False |

## markov_100 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (90.40%); T1486 Data Encrypted for Impact (4.24%); T1115 Clipboard Data (2.65%) | 90.40% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.74%); T1548 Abuse Elevation Control Mechanism (0.15%); T1218 System Binary Proxy Execution (0.03%) | 99.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.75%); T1057 Process Discovery (0.04%); T1003 OS Credential Dumping (0.03%) | 99.75% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (90.27%); T1190 Exploit Public-Facing Application (9.49%); T1592 Gather Victim Host Information (0.07%) | 90.27% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.16%); T1059 Command and Scripting Interpreter (0.36%); T1053 Scheduled Task/Job (0.09%) | 99.16% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (88.00%); T1059 Command and Scripting Interpreter (11.14%); T1105 Ingress Tool Transfer (0.47%) | 88.00% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1003 OS Credential Dumping (0.01%); T1543 Create or Modify System Process (0.01%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.83%); T1599 Network Boundary Bridging (0.25%); T1039 Data from Network Shared Drive (0.14%) | 98.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1574 Hijack Execution Flow (59.09%); T1133 External Remote Services (5.84%); T1003 OS Credential Dumping (5.62%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1548 Abuse Elevation Control Mechanism (30.01%); T1564 Hide Artifacts (16.59%); T1574 Hijack Execution Flow (7.84%) | 0.00% | False |

## markov_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.93%); T1201 Password Policy Discovery (4.46%); T1595 Active Scanning (0.06%) | 94.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.40%); T1548 Abuse Elevation Control Mechanism (1.14%); T1036 Masquerading (0.15%) | 98.40% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1057 Process Discovery (0.00%); T1201 Password Policy Discovery (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (79.87%); T1592 Gather Victim Host Information (12.05%); T1190 Exploit Public-Facing Application (7.81%) | 79.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.63%); T1059 Command and Scripting Interpreter (0.22%); T1136 Create Account (0.04%) | 99.63% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (76.99%); T1059 Command and Scripting Interpreter (22.73%); T1083 File and Directory Discovery (0.04%) | 76.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.50%); T1574 Hijack Execution Flow (0.13%); T1046 Network Service Scanning (0.04%) | 99.50% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.29%); T1039 Data from Network Shared Drive (0.18%); T1078 Valid Accounts (0.07%) | 99.29% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (90.18%); T1110 Brute Force (1.62%); T1021 Remote Services (1.40%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (74.28%); T1110 Brute Force (6.91%); T1550 Use Alternate Authentication Material (4.45%) | 0.01% | False |

## markov_100 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.96%); T1590 Gather Victim Network Information (2.55%); T1110 Brute Force (0.10%) | 96.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.72%); T1036 Masquerading (0.06%); T1548 Abuse Elevation Control Mechanism (0.06%) | 99.72% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.91%); T1201 Password Policy Discovery (0.02%); T1204 User Execution (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (65.87%); T1592 Gather Victim Host Information (24.31%); T1190 Exploit Public-Facing Application (9.42%) | 65.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.89%); T1059 Command and Scripting Interpreter (1.92%); T1595 Active Scanning (0.02%) | 97.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (55.85%); T1059 Command and Scripting Interpreter (43.79%); T1105 Ingress Tool Transfer (0.13%) | 55.85% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.88%); T1124 System Time Discovery (0.05%); T1082 System Information Discovery (0.01%) | 99.88% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.48%); T1039 Data from Network Shared Drive (0.08%); T1082 System Information Discovery (0.07%) | 99.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (62.90%); T1566 Phishing (11.97%); T1497 Virtualization/Sandbox Evasion (6.67%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (58.53%); T1059 Command and Scripting Interpreter (15.43%); T1566 Phishing (7.59%) | 0.01% | False |

## markov_100 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.69%); T1071 Application Layer Protocol (0.04%); T1556 Modify Authentication Process (0.04%) | 99.69% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.36%); T1548 Abuse Elevation Control Mechanism (0.26%); T1614 System Location Discovery (0.06%) | 99.36% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.76%); T1057 Process Discovery (0.07%); T1124 System Time Discovery (0.04%) | 99.76% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.49%); T1190 Exploit Public-Facing Application (2.35%); T1592 Gather Victim Host Information (1.85%) | 95.49% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.22%); T1068 Exploitation for Privilege Escalation (0.15%); T1078 Valid Accounts (0.12%) | 99.22% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (92.07%); T1059 Command and Scripting Interpreter (7.55%); T1057 Process Discovery (0.05%) | 92.07% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.70%); T1201 Password Policy Discovery (0.05%); T1007 System Service Discovery (0.04%) | 99.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.05%); T1039 Data from Network Shared Drive (0.25%); T1614 System Location Discovery (0.13%) | 99.05% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (43.49%); T1566 Phishing (31.37%); T1525 Implant Internal Image (6.71%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1566 Phishing (73.72%); T1053 Scheduled Task/Job (10.27%); T1105 Ingress Tool Transfer (3.04%) | 0.00% | False |

## markov_100 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.61%); T1595 Active Scanning (0.09%); T1105 Ingress Tool Transfer (0.08%) | 99.61% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.14%); T1548 Abuse Elevation Control Mechanism (0.36%); T1059 Command and Scripting Interpreter (0.23%) | 99.14% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.59%); T1133 External Remote Services (0.16%); T1021 Remote Services (0.05%) | 99.59% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (71.07%); T1190 Exploit Public-Facing Application (15.69%); T1592 Gather Victim Host Information (12.76%) | 71.07% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.50%); T1059 Command and Scripting Interpreter (0.76%); T1087 Account Discovery (0.18%) | 98.50% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (56.00%); T1059 Command and Scripting Interpreter (41.79%); T1105 Ingress Tool Transfer (1.88%) | 56.00% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.64%); T1033 System Owner/User Discovery (0.08%); T1124 System Time Discovery (0.04%) | 99.64% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.48%); T1204 User Execution (0.74%); T1222 File and Directory Permissions Modification (0.12%) | 98.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (20.42%); T1531 Account Access Removal (17.97%); T1489 Service Stop (15.54%) | 0.60% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1573 Encrypted Channel (16.04%); T1039 Data from Network Shared Drive (13.38%); T1556 Modify Authentication Process (12.61%) | 0.01% | False |

## markov_100 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.80%); T1039 Data from Network Shared Drive (2.99%); T1595 Active Scanning (0.25%) | 95.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.54%); T1548 Abuse Elevation Control Mechanism (0.32%); T1070 Indicator Removal (0.02%) | 99.54% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1057 Process Discovery (0.03%); T1039 Data from Network Shared Drive (0.03%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (93.06%); T1190 Exploit Public-Facing Application (4.28%); T1592 Gather Victim Host Information (2.30%) | 93.06% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.51%); T1059 Command and Scripting Interpreter (1.98%); T1036 Masquerading (0.09%) | 97.51% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.29%); T1059 Command and Scripting Interpreter (1.48%); T1105 Ingress Tool Transfer (0.05%) | 98.29% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.30%); T1105 Ingress Tool Transfer (0.20%); T1005 Data from Local System (0.07%) | 99.30% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.38%); T1222 File and Directory Permissions Modification (0.16%); T1083 File and Directory Discovery (0.10%) | 99.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (26.60%); T1072 Software Deployment Tools (22.11%); T1546 Event Triggered Execution (12.54%) | 0.73% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1566 Phishing (18.06%); T1219 Remote Access Tools (13.83%); T1564 Hide Artifacts (11.78%) | 0.24% | False |

## markov_100 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.84%); T1078 Valid Accounts (0.02%); T1610 Deploy Container (0.02%) | 99.84% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (94.67%); T1548 Abuse Elevation Control Mechanism (2.92%); T1190 Exploit Public-Facing Application (0.58%) | 94.67% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.68%); T1072 Software Deployment Tools (0.14%); T1201 Password Policy Discovery (0.02%) | 99.68% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (90.68%); T1190 Exploit Public-Facing Application (8.49%); T1592 Gather Victim Host Information (0.69%) | 90.68% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.56%); T1059 Command and Scripting Interpreter (4.64%); T1547 Boot or Logon Autostart Execution (0.17%) | 94.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (96.77%); T1059 Command and Scripting Interpreter (2.99%); T1105 Ingress Tool Transfer (0.05%) | 96.77% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.47%); T1053 Scheduled Task/Job (0.08%); T1485 Data Destruction (0.05%) | 99.47% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.33%); T1573 Encrypted Channel (0.10%); T1595 Active Scanning (0.07%) | 99.33% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (31.58%); T1591 Gather Victim Org Information (25.22%); T1610 Deploy Container (24.84%) | 1.12% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1213 Data from Information Repositories (35.06%); T1564 Hide Artifacts (34.76%); T1039 Data from Network Shared Drive (8.20%) | 0.00% | False |

## markov_100 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.84%); T1074 Data Staged (2.77%); T1557 Adversary-in-the-Middle (0.06%) | 96.84% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.20%); T1548 Abuse Elevation Control Mechanism (4.11%); T1005 Data from Local System (0.24%) | 95.20% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.68%); T1589 Gather Victim Identity Information (1.08%); T1222 File and Directory Permissions Modification (0.03%) | 98.68% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.10%); T1592 Gather Victim Host Information (12.05%); T1036 Masquerading (3.53%) | 81.10% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.16%); T1059 Command and Scripting Interpreter (0.58%); T1547 Boot or Logon Autostart Execution (0.04%) | 99.16% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (91.38%); T1059 Command and Scripting Interpreter (7.90%); T1595 Active Scanning (0.15%) | 91.38% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1120 Peripheral Device Discovery (0.02%); T1547 Boot or Logon Autostart Execution (0.02%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.82%); T1039 Data from Network Shared Drive (0.26%); T1591 Gather Victim Org Information (0.21%) | 98.82% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1049 System Network Connections Discovery (23.90%); T1105 Ingress Tool Transfer (16.80%); T1110 Brute Force (16.34%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1049 System Network Connections Discovery (20.07%); T1080 Taint Shared Content (18.92%); T1110 Brute Force (15.67%) | 0.07% | False |

## markov_100 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.65%); T1010 Application Window Discovery (0.09%); T1592 Gather Victim Host Information (0.04%) | 99.65% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.02%); T1548 Abuse Elevation Control Mechanism (0.68%); T1105 Ingress Tool Transfer (0.22%) | 99.02% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.78%); T1007 System Service Discovery (0.05%); T1590 Gather Victim Network Information (0.03%) | 99.78% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (83.99%); T1190 Exploit Public-Facing Application (15.78%); T1573 Encrypted Channel (0.03%) | 83.99% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.20%); T1059 Command and Scripting Interpreter (0.31%); T1566 Phishing (0.11%) | 99.20% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (61.57%); T1087 Account Discovery (37.75%); T1105 Ingress Tool Transfer (0.39%) | 37.75% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.75%); T1205 Traffic Signaling (0.10%); T1204 User Execution (0.03%) | 99.75% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.51%); T1003 OS Credential Dumping (0.15%); T1573 Encrypted Channel (0.08%) | 99.51% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (38.47%); T1219 Remote Access Tools (32.53%); T1550 Use Alternate Authentication Material (7.58%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (37.72%); T1574 Hijack Execution Flow (17.84%); T1219 Remote Access Tools (15.99%) | 0.00% | False |

## markov_100 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.83%); T1071 Application Layer Protocol (0.02%); T1068 Exploitation for Privilege Escalation (0.02%) | 99.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (87.54%); T1548 Abuse Elevation Control Mechanism (10.48%); T1550 Use Alternate Authentication Material (0.64%) | 87.54% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.79%); T1082 System Information Discovery (0.03%); T1222 File and Directory Permissions Modification (0.02%) | 99.79% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (79.19%); T1190 Exploit Public-Facing Application (11.79%); T1592 Gather Victim Host Information (8.80%) | 79.19% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.04%); T1059 Command and Scripting Interpreter (0.09%); T1547 Boot or Logon Autostart Execution (0.07%) | 99.04% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (93.23%); T1059 Command and Scripting Interpreter (6.14%); T1105 Ingress Tool Transfer (0.24%) | 93.23% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1124 System Time Discovery (0.11%); T1591 Gather Victim Org Information (0.05%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.98%); T1039 Data from Network Shared Drive (0.30%); T1003 OS Credential Dumping (0.24%) | 98.98% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (79.22%); T1059 Command and Scripting Interpreter (4.96%); T1041 Exfiltration Over C2 Channel (3.38%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (87.96%); T1005 Data from Local System (2.64%); T1218 System Binary Proxy Execution (1.86%) | 0.01% | False |

## markov_100 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (89.12%); T1486 Data Encrypted for Impact (3.66%); T1115 Clipboard Data (3.22%) | 89.12% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.52%); T1548 Abuse Elevation Control Mechanism (0.22%); T1105 Ingress Tool Transfer (0.06%) | 99.52% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.78%); T1201 Password Policy Discovery (0.04%); T1018 Remote System Discovery (0.04%) | 99.78% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (88.10%); T1190 Exploit Public-Facing Application (10.60%); T1592 Gather Victim Host Information (0.96%) | 88.10% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (91.37%); T1059 Command and Scripting Interpreter (6.47%); T1082 System Information Discovery (1.32%) | 91.37% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (85.12%); T1059 Command and Scripting Interpreter (14.48%); T1105 Ingress Tool Transfer (0.24%) | 85.12% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1486 Data Encrypted for Impact (0.04%); T1590 Gather Victim Network Information (0.04%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.42%); T1033 System Owner/User Discovery (1.21%); T1039 Data from Network Shared Drive (0.45%) | 97.42% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1210 Exploitation of Remote Services (15.12%); T1615 Group Policy Discovery (9.50%); T1055 Process Injection (7.09%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1210 Exploitation of Remote Services (32.40%); T1528 Steal Application Access Token (28.16%); T1550 Use Alternate Authentication Material (5.54%) | 0.00% | False |

## markov_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.57%); T1201 Password Policy Discovery (3.05%); T1614 System Location Discovery (0.08%) | 96.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (63.39%); T1548 Abuse Elevation Control Mechanism (34.84%); T1546 Event Triggered Execution (0.46%) | 63.39% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1083 File and Directory Discovery (0.00%); T1556 Modify Authentication Process (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (46.36%); T1190 Exploit Public-Facing Application (29.51%); T1592 Gather Victim Host Information (23.64%) | 46.36% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.64%); T1039 Data from Network Shared Drive (0.58%); T1059 Command and Scripting Interpreter (0.54%) | 98.64% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (86.18%); T1087 Account Discovery (13.01%); T1105 Ingress Tool Transfer (0.73%) | 13.01% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.78%); T1136 Create Account (0.10%); T1574 Hijack Execution Flow (0.03%) | 99.78% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.34%); T1074 Data Staged (1.33%); T1041 Exfiltration Over C2 Channel (0.13%) | 98.34% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (64.64%); T1059 Command and Scripting Interpreter (22.68%); T1082 System Information Discovery (3.23%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (17.11%); T1222 File and Directory Permissions Modification (15.89%); T1201 Password Policy Discovery (10.22%) | 0.22% | False |

## markov_100 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.78%); T1590 Gather Victim Network Information (2.00%); T1592 Gather Victim Host Information (0.05%) | 97.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (92.49%); T1548 Abuse Elevation Control Mechanism (5.36%); T1059 Command and Scripting Interpreter (0.71%) | 92.49% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.80%); T1003 OS Credential Dumping (0.03%); T1078 Valid Accounts (0.02%) | 99.80% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (40.67%); T1190 Exploit Public-Facing Application (36.49%); T1592 Gather Victim Host Information (22.38%) | 40.67% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.08%); T1059 Command and Scripting Interpreter (0.42%); T1486 Data Encrypted for Impact (0.17%) | 99.08% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (89.53%); T1087 Account Discovery (9.89%); T1105 Ingress Tool Transfer (0.33%) | 9.89% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1016 System Network Configuration Discovery (0.01%); T1072 Software Deployment Tools (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.15%); T1021 Remote Services (0.22%); T1531 Account Access Removal (0.10%) | 99.15% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (70.36%); T1219 Remote Access Tools (5.97%); T1078 Valid Accounts (5.77%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1518 Software Discovery (39.47%); T1222 File and Directory Permissions Modification (15.99%); T1564 Hide Artifacts (8.63%) | 0.19% | False |

## markov_100 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1071 Application Layer Protocol (0.00%); T1040 Network Sniffing (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (65.24%); T1548 Abuse Elevation Control Mechanism (33.79%); T1005 Data from Local System (0.31%) | 65.24% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1120 Peripheral Device Discovery (0.00%); T1518 Software Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (48.64%); T1190 Exploit Public-Facing Application (46.40%); T1592 Gather Victim Host Information (3.60%) | 48.64% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.71%); T1068 Exploitation for Privilege Escalation (0.51%); T1485 Data Destruction (0.31%) | 98.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (69.87%); T1087 Account Discovery (28.53%); T1105 Ingress Tool Transfer (1.38%) | 28.53% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.05%); T1528 Steal Application Access Token (0.33%); T1083 File and Directory Discovery (0.19%) | 99.05% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.99%); T1021 Remote Services (0.44%); T1055 Process Injection (0.11%) | 98.99% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1490 Inhibit System Recovery (41.03%); T1573 Encrypted Channel (27.73%); T1218 System Binary Proxy Execution (7.78%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (72.74%); T1222 File and Directory Permissions Modification (9.99%); T1614 System Location Discovery (5.22%) | 0.02% | False |

## markov_100 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1528 Steal Application Access Token (0.02%); T1218 System Binary Proxy Execution (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (73.09%); T1548 Abuse Elevation Control Mechanism (25.64%); T1218 System Binary Proxy Execution (0.40%) | 73.09% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.78%); T1133 External Remote Services (0.13%); T1057 Process Discovery (0.02%) | 99.78% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (42.86%); T1190 Exploit Public-Facing Application (33.99%); T1592 Gather Victim Host Information (22.85%) | 42.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.85%); T1059 Command and Scripting Interpreter (2.61%); T1087 Account Discovery (0.48%) | 95.85% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (66.29%); T1087 Account Discovery (33.24%); T1105 Ingress Tool Transfer (0.18%) | 33.24% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1124 System Time Discovery (0.07%); T1518 Software Discovery (0.04%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.16%); T1204 User Execution (0.69%); T1574 Hijack Execution Flow (0.36%) | 98.16% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1531 Account Access Removal (21.70%); T1014 Rootkit (13.05%); T1528 Steal Application Access Token (11.83%) | 0.53% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1041 Exfiltration Over C2 Channel (30.04%); T1003 OS Credential Dumping (14.83%); T1528 Steal Application Access Token (13.66%) | 0.47% | False |

## markov_100 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.32%); T1039 Data from Network Shared Drive (2.26%); T1557 Adversary-in-the-Middle (0.06%) | 97.32% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (89.86%); T1548 Abuse Elevation Control Mechanism (9.65%); T1036 Masquerading (0.15%) | 89.86% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1078 Valid Accounts (0.02%); T1059 Command and Scripting Interpreter (0.01%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (54.58%); T1190 Exploit Public-Facing Application (33.55%); T1592 Gather Victim Host Information (10.45%) | 54.58% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.31%); T1059 Command and Scripting Interpreter (0.32%); T1105 Ingress Tool Transfer (0.10%) | 99.31% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (75.90%); T1087 Account Discovery (23.81%); T1105 Ingress Tool Transfer (0.17%) | 23.81% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1222 File and Directory Permissions Modification (0.02%); T1018 Remote System Discovery (0.02%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.68%); T1564 Hide Artifacts (0.05%); T1021 Remote Services (0.05%) | 99.68% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1036 Masquerading (31.20%); T1210 Exploitation of Remote Services (19.90%); T1005 Data from Local System (11.68%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1005 Data from Local System (44.63%); T1055 Process Injection (25.34%); T1080 Taint Shared Content (9.00%) | 0.00% | False |

## markov_100 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1133 External Remote Services (0.01%); T1078 Valid Accounts (0.00%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (77.65%); T1548 Abuse Elevation Control Mechanism (17.71%); T1078 Valid Accounts (1.42%) | 77.65% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1133 External Remote Services (0.07%); T1592 Gather Victim Host Information (0.06%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (55.40%); T1190 Exploit Public-Facing Application (36.84%); T1592 Gather Victim Host Information (7.34%) | 55.40% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.44%); T1059 Command and Scripting Interpreter (4.65%); T1547 Boot or Logon Autostart Execution (0.13%) | 94.44% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (79.10%); T1087 Account Discovery (20.07%); T1105 Ingress Tool Transfer (0.34%) | 20.07% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.63%); T1589 Gather Victim Identity Information (0.13%); T1072 Software Deployment Tools (0.06%) | 99.63% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.63%); T1547 Boot or Logon Autostart Execution (0.05%); T1592 Gather Victim Host Information (0.05%) | 99.63% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1610 Deploy Container (22.90%); T1046 Network Service Scanning (18.80%); T1021 Remote Services (17.59%) | 0.64% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1046 Network Service Scanning (25.42%); T1595 Active Scanning (22.29%); T1592 Gather Victim Host Information (11.73%) | 0.01% | False |

## markov_100 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.76%); T1074 Data Staged (1.10%); T1110 Brute Force (0.01%) | 98.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (57.61%); T1548 Abuse Elevation Control Mechanism (40.36%); T1005 Data from Local System (0.33%) | 57.61% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.53%); T1589 Gather Victim Identity Information (0.30%); T1566 Phishing (0.03%) | 99.53% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (50.37%); T1595 Active Scanning (33.86%); T1592 Gather Victim Host Information (13.47%) | 33.86% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.36%); T1059 Command and Scripting Interpreter (0.22%); T1218 System Binary Proxy Execution (0.09%) | 99.36% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (82.12%); T1087 Account Discovery (15.77%); T1105 Ingress Tool Transfer (1.88%) | 15.77% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1557 Adversary-in-the-Middle (0.02%); T1053 Scheduled Task/Job (0.01%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.53%); T1120 Peripheral Device Discovery (0.08%); T1049 System Network Connections Discovery (0.07%) | 99.53% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1610 Deploy Container (43.33%); T1572 Protocol Tunneling (14.97%); T1105 Ingress Tool Transfer (11.31%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1176 Software Extensions (37.31%); T1080 Taint Shared Content (9.86%); T1074 Data Staged (7.89%) | 0.02% | False |

## markov_100 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.95%); T1573 Encrypted Channel (0.01%); T1592 Gather Victim Host Information (0.01%) | 99.95% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.66%); T1548 Abuse Elevation Control Mechanism (2.09%); T1105 Ingress Tool Transfer (0.07%) | 97.66% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1033 System Owner/User Discovery (0.03%); T1136 Create Account (0.02%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (54.16%); T1190 Exploit Public-Facing Application (43.69%); T1592 Gather Victim Host Information (1.65%) | 54.16% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.71%); T1018 Remote System Discovery (0.08%); T1564 Hide Artifacts (0.03%) | 99.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (59.70%); T1087 Account Discovery (38.49%); T1105 Ingress Tool Transfer (1.44%) | 38.49% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.56%); T1014 Rootkit (0.15%); T1190 Exploit Public-Facing Application (0.07%) | 99.56% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.53%); T1553 Subvert Trust Controls (0.16%); T1072 Software Deployment Tools (0.06%) | 99.53% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (35.36%); T1098 Account Manipulation (24.68%); T1213 Data from Information Repositories (12.82%) | 0.34% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (85.50%); T1222 File and Directory Permissions Modification (8.38%); T1018 Remote System Discovery (2.13%) | 0.01% | False |

## markov_100 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.86%); T1018 Remote System Discovery (0.03%); T1589 Gather Victim Identity Information (0.02%) | 99.86% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (64.71%); T1548 Abuse Elevation Control Mechanism (25.17%); T1550 Use Alternate Authentication Material (4.02%) | 64.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1136 Create Account (0.02%); T1614 System Location Discovery (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (40.39%); T1595 Active Scanning (37.95%); T1592 Gather Victim Host Information (20.34%) | 37.95% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.47%); T1070 Indicator Removal (0.05%); T1525 Implant Internal Image (0.04%) | 99.47% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (86.06%); T1087 Account Discovery (13.42%); T1105 Ingress Tool Transfer (0.41%) | 13.42% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1553 Subvert Trust Controls (0.05%); T1190 Exploit Public-Facing Application (0.05%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.60%); T1120 Peripheral Device Discovery (0.06%); T1021 Remote Services (0.06%) | 99.60% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (31.11%); T1070 Indicator Removal (6.91%); T1566 Phishing (5.81%) | 0.41% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (24.18%); T1120 Peripheral Device Discovery (17.35%); T1005 Data from Local System (12.03%) | 0.00% | False |

## markov_100 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (92.94%); T1110 Brute Force (2.92%); T1115 Clipboard Data (1.87%) | 92.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.59%); T1548 Abuse Elevation Control Mechanism (5.64%); T1218 System Binary Proxy Execution (0.28%) | 93.59% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1007 System Service Discovery (0.01%); T1557 Adversary-in-the-Middle (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (47.20%); T1190 Exploit Public-Facing Application (43.35%); T1592 Gather Victim Host Information (9.10%) | 47.20% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.33%); T1059 Command and Scripting Interpreter (0.11%); T1556 Modify Authentication Process (0.05%) | 99.33% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (71.58%); T1087 Account Discovery (27.59%); T1105 Ingress Tool Transfer (0.51%) | 27.59% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.74%); T1590 Gather Victim Network Information (0.09%); T1057 Process Discovery (0.03%) | 99.74% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.37%); T1041 Exfiltration Over C2 Channel (0.10%); T1021 Remote Services (0.09%) | 99.37% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (87.21%); T1078 Valid Accounts (3.89%); T1055 Process Injection (3.23%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1021 Remote Services (31.42%); T1547 Boot or Logon Autostart Execution (30.97%); T1564 Hide Artifacts (13.64%) | 0.00% | False |

## markov_200 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.71%); T1201 Password Policy Discovery (1.11%); T1615 Group Policy Discovery (0.04%) | 98.71% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.50%); T1548 Abuse Elevation Control Mechanism (0.80%); T1036 Masquerading (0.35%) | 98.50% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1590 Gather Victim Network Information (0.01%); T1490 Inhibit System Recovery (0.01%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (77.13%); T1592 Gather Victim Host Information (19.43%); T1190 Exploit Public-Facing Application (3.23%) | 77.13% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.00%); T1059 Command and Scripting Interpreter (3.74%); T1087 Account Discovery (0.05%) | 96.00% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (78.61%); T1059 Command and Scripting Interpreter (21.12%); T1105 Ingress Tool Transfer (0.10%) | 78.61% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.54%); T1040 Network Sniffing (0.11%); T1053 Scheduled Task/Job (0.09%) | 99.54% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.50%); T1120 Peripheral Device Discovery (0.19%); T1574 Hijack Execution Flow (0.04%) | 99.50% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1018 Remote System Discovery (22.97%); T1222 File and Directory Permissions Modification (13.79%); T1041 Exfiltration Over C2 Channel (8.04%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (72.73%); T1497 Virtualization/Sandbox Evasion (6.23%); T1049 System Network Connections Discovery (3.34%) | 0.00% | False |

## markov_200 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.75%); T1590 Gather Victim Network Information (1.00%); T1046 Network Service Scanning (0.11%) | 98.75% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.33%); T1548 Abuse Elevation Control Mechanism (3.35%); T1547 Boot or Logon Autostart Execution (0.06%) | 96.33% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1589 Gather Victim Identity Information (0.03%); T1005 Data from Local System (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (56.90%); T1190 Exploit Public-Facing Application (26.02%); T1592 Gather Victim Host Information (16.91%) | 56.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.09%); T1059 Command and Scripting Interpreter (0.68%); T1547 Boot or Logon Autostart Execution (0.08%) | 99.09% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (74.66%); T1059 Command and Scripting Interpreter (23.76%); T1105 Ingress Tool Transfer (0.97%) | 74.66% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.86%); T1049 System Network Connections Discovery (0.05%); T1485 Data Destruction (0.03%) | 99.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.98%); T1201 Password Policy Discovery (0.49%); T1046 Network Service Scanning (0.11%) | 98.98% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (24.27%); T1105 Ingress Tool Transfer (20.23%); T1564 Hide Artifacts (13.76%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (56.99%); T1014 Rootkit (10.72%); T1070 Indicator Removal (5.71%) | 0.00% | False |

## markov_200 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1003 OS Credential Dumping (0.01%); T1136 Create Account (0.01%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1553 Subvert Trust Controls (0.05%); T1098 Account Manipulation (0.04%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.55%); T1569 System Services (0.30%); T1057 Process Discovery (0.02%) | 99.55% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (86.25%); T1190 Exploit Public-Facing Application (9.84%); T1592 Gather Victim Host Information (3.60%) | 86.25% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.81%); T1071 Application Layer Protocol (0.07%); T1059 Command and Scripting Interpreter (0.04%) | 99.81% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (67.88%); T1059 Command and Scripting Interpreter (31.94%); T1105 Ingress Tool Transfer (0.04%) | 67.88% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.98%); T1124 System Time Discovery (0.02%); T1566 Phishing (0.00%) | 99.98% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.19%); T1489 Service Stop (0.29%); T1120 Peripheral Device Discovery (0.16%) | 99.19% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (43.12%); T1222 File and Directory Permissions Modification (16.51%); T1098 Account Manipulation (15.74%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1098 Account Manipulation (44.15%); T1033 System Owner/User Discovery (27.63%); T1105 Ingress Tool Transfer (11.93%) | 0.02% | False |

## markov_200 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1059 Command and Scripting Interpreter (0.01%); T1566 Phishing (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.97%); T1548 Abuse Elevation Control Mechanism (0.01%); T1490 Inhibit System Recovery (0.00%) | 99.97% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.82%); T1133 External Remote Services (0.03%); T1614 System Location Discovery (0.03%) | 99.82% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.34%); T1592 Gather Victim Host Information (10.41%); T1190 Exploit Public-Facing Application (8.05%) | 81.34% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.98%); T1059 Command and Scripting Interpreter (2.57%); T1547 Boot or Logon Autostart Execution (0.18%) | 96.98% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.09%); T1059 Command and Scripting Interpreter (13.25%); T1105 Ingress Tool Transfer (0.45%) | 86.09% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.68%); T1016 System Network Configuration Discovery (0.08%); T1124 System Time Discovery (0.06%) | 99.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.89%); T1204 User Execution (0.03%); T1021 Remote Services (0.02%) | 99.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1614 System Location Discovery (29.31%); T1610 Deploy Container (19.13%); T1518 Software Discovery (12.18%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1528 Steal Application Access Token (20.46%); T1589 Gather Victim Identity Information (19.25%); T1569 System Services (16.05%) | 0.00% | False |

## markov_200 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.96%); T1039 Data from Network Shared Drive (1.71%); T1213 Data from Information Repositories (0.06%) | 97.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.68%); T1548 Abuse Elevation Control Mechanism (0.20%); T1614 System Location Discovery (0.02%) | 99.68% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.93%); T1201 Password Policy Discovery (0.01%); T1078 Valid Accounts (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (87.47%); T1592 Gather Victim Host Information (7.10%); T1190 Exploit Public-Facing Application (5.08%) | 87.47% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.57%); T1059 Command and Scripting Interpreter (1.04%); T1124 System Time Discovery (0.07%) | 98.57% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (85.37%); T1059 Command and Scripting Interpreter (13.56%); T1105 Ingress Tool Transfer (0.92%) | 85.37% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.64%); T1124 System Time Discovery (0.15%); T1120 Peripheral Device Discovery (0.08%) | 99.64% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.93%); T1039 Data from Network Shared Drive (0.03%); T1115 Clipboard Data (0.01%) | 99.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (36.41%); T1550 Use Alternate Authentication Material (25.00%); T1547 Boot or Logon Autostart Execution (10.57%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1124 System Time Discovery (67.78%); T1219 Remote Access Tools (13.93%); T1550 Use Alternate Authentication Material (4.33%) | 0.00% | False |

## markov_200 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1057 Process Discovery (0.04%); T1078 Valid Accounts (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.93%); T1190 Exploit Public-Facing Application (0.04%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.93% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.93%); T1204 User Execution (0.04%); T1133 External Remote Services (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (61.56%); T1190 Exploit Public-Facing Application (36.99%); T1592 Gather Victim Host Information (0.90%) | 61.56% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.18%); T1059 Command and Scripting Interpreter (2.05%); T1033 System Owner/User Discovery (0.23%) | 97.18% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (68.71%); T1059 Command and Scripting Interpreter (31.07%); T1105 Ingress Tool Transfer (0.05%) | 68.71% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1573 Encrypted Channel (0.02%); T1016 System Network Configuration Discovery (0.01%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.76%); T1021 Remote Services (0.10%); T1564 Hide Artifacts (0.02%) | 99.76% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (57.67%); T1098 Account Manipulation (19.96%); T1016 System Network Configuration Discovery (5.58%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1615 Group Policy Discovery (55.16%); T1016 System Network Configuration Discovery (17.53%); T1098 Account Manipulation (8.09%) | 0.00% | False |

## markov_200 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.65%); T1074 Data Staged (2.12%); T1565 Data Manipulation (1.96%) | 94.65% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.64%); T1566 Phishing (0.68%); T1548 Abuse Elevation Control Mechanism (0.27%) | 98.64% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.64%); T1589 Gather Victim Identity Information (0.15%); T1046 Network Service Scanning (0.04%) | 99.64% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (69.57%); T1592 Gather Victim Host Information (16.87%); T1190 Exploit Public-Facing Application (8.96%) | 69.57% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.45%); T1059 Command and Scripting Interpreter (1.12%); T1218 System Binary Proxy Execution (0.20%) | 98.45% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (85.31%); T1059 Command and Scripting Interpreter (14.35%); T1105 Ingress Tool Transfer (0.16%) | 85.31% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.90%); T1049 System Network Connections Discovery (0.02%); T1595 Active Scanning (0.01%) | 99.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.46%); T1071 Application Layer Protocol (0.11%); T1120 Peripheral Device Discovery (0.10%) | 99.46% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (32.10%); T1059 Command and Scripting Interpreter (25.70%); T1087 Account Discovery (10.45%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (90.50%); T1565 Data Manipulation (2.73%); T1548 Abuse Elevation Control Mechanism (1.06%) | 0.00% | False |

## markov_200 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.93%); T1573 Encrypted Channel (0.02%); T1556 Modify Authentication Process (0.02%) | 99.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.66%); T1068 Exploitation for Privilege Escalation (0.13%); T1105 Ingress Tool Transfer (0.10%) | 99.66% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.89%); T1007 System Service Discovery (0.97%); T1003 OS Credential Dumping (0.04%) | 98.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (51.21%); T1595 Active Scanning (45.75%); T1592 Gather Victim Host Information (2.63%) | 45.75% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.30%); T1059 Command and Scripting Interpreter (0.42%); T1615 Group Policy Discovery (0.09%) | 99.30% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (96.68%); T1059 Command and Scripting Interpreter (3.16%); T1105 Ingress Tool Transfer (0.04%) | 96.68% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.86%); T1566 Phishing (0.02%); T1490 Inhibit System Recovery (0.02%) | 99.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.80%); T1547 Boot or Logon Autostart Execution (0.06%); T1072 Software Deployment Tools (0.05%) | 99.80% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1007 System Service Discovery (37.61%); T1082 System Information Discovery (36.20%); T1497 Virtualization/Sandbox Evasion (6.36%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (29.02%); T1222 File and Directory Permissions Modification (15.26%); T1105 Ingress Tool Transfer (10.40%) | 0.01% | False |

## markov_200 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1055 Process Injection (0.02%); T1595 Active Scanning (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.34%); T1548 Abuse Elevation Control Mechanism (0.40%); T1105 Ingress Tool Transfer (0.32%) | 98.34% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1124 System Time Discovery (0.05%); T1531 Account Access Removal (0.02%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (71.95%); T1190 Exploit Public-Facing Application (15.92%); T1592 Gather Victim Host Information (11.90%) | 71.95% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.45%); T1059 Command and Scripting Interpreter (0.49%); T1053 Scheduled Task/Job (0.25%) | 98.45% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (88.37%); T1059 Command and Scripting Interpreter (10.58%); T1105 Ingress Tool Transfer (0.78%) | 88.37% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.82%); T1210 Exploitation of Remote Services (0.05%); T1016 System Network Configuration Discovery (0.02%) | 99.82% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.38%); T1564 Hide Artifacts (0.09%); T1120 Peripheral Device Discovery (0.06%) | 99.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (74.81%); T1564 Hide Artifacts (13.73%); T1566 Phishing (4.26%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (84.27%); T1574 Hijack Execution Flow (5.61%); T1033 System Owner/User Discovery (2.57%) | 0.23% | False |

## markov_200 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (90.63%); T1525 Implant Internal Image (3.03%); T1110 Brute Force (2.17%) | 90.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.50%); T1548 Abuse Elevation Control Mechanism (0.28%); T1070 Indicator Removal (0.09%) | 99.50% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1003 OS Credential Dumping (0.03%); T1087 Account Discovery (0.03%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (87.54%); T1190 Exploit Public-Facing Application (6.26%); T1592 Gather Victim Host Information (6.10%) | 87.54% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.58%); T1056 Input Capture (0.10%); T1059 Command and Scripting Interpreter (0.07%) | 99.58% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (66.28%); T1087 Account Discovery (33.33%); T1105 Ingress Tool Transfer (0.31%) | 33.33% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.86%); T1590 Gather Victim Network Information (0.09%); T1176 Software Extensions (0.01%) | 99.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.55%); T1003 OS Credential Dumping (0.09%); T1105 Ingress Tool Transfer (0.09%) | 99.55% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1574 Hijack Execution Flow (55.94%); T1036 Masquerading (19.58%); T1016 System Network Configuration Discovery (7.69%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1590 Gather Victim Network Information (72.61%); T1021 Remote Services (8.17%); T1531 Account Access Removal (3.22%) | 0.00% | False |

## markov_200 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.11%); T1201 Password Policy Discovery (1.70%); T1557 Adversary-in-the-Middle (0.04%) | 98.11% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.11%); T1548 Abuse Elevation Control Mechanism (0.97%); T1036 Masquerading (0.40%) | 98.11% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.87%); T1590 Gather Victim Network Information (0.02%); T1072 Software Deployment Tools (0.02%) | 99.87% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (85.22%); T1592 Gather Victim Host Information (11.01%); T1190 Exploit Public-Facing Application (3.68%) | 85.22% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.09%); T1059 Command and Scripting Interpreter (2.65%); T1136 Create Account (0.09%) | 97.09% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (54.93%); T1087 Account Discovery (44.90%); T1136 Create Account (0.05%) | 44.90% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.90%); T1040 Network Sniffing (0.02%); T1055 Process Injection (0.02%) | 99.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.78%); T1074 Data Staged (0.05%); T1041 Exfiltration Over C2 Channel (0.04%) | 99.78% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1049 System Network Connections Discovery (29.91%); T1222 File and Directory Permissions Modification (19.89%); T1046 Network Service Scanning (15.42%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (83.09%); T1057 Process Discovery (6.05%); T1497 Virtualization/Sandbox Evasion (3.07%) | 0.01% | False |

## markov_200 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.73%); T1590 Gather Victim Network Information (1.86%); T1110 Brute Force (0.12%) | 97.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.08%); T1548 Abuse Elevation Control Mechanism (0.53%); T1059 Command and Scripting Interpreter (0.20%) | 99.08% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1489 Service Stop (0.05%); T1201 Password Policy Discovery (0.04%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (64.95%); T1190 Exploit Public-Facing Application (18.08%); T1592 Gather Victim Host Information (16.81%) | 64.95% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.23%); T1059 Command and Scripting Interpreter (0.45%); T1133 External Remote Services (0.08%) | 99.23% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.38%); T1059 Command and Scripting Interpreter (12.13%); T1105 Ingress Tool Transfer (1.10%) | 86.38% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.82%); T1124 System Time Discovery (0.10%); T1485 Data Destruction (0.03%) | 99.82% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.80%); T1082 System Information Discovery (0.07%); T1201 Password Policy Discovery (0.04%) | 99.80% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1205 Traffic Signaling (73.91%); T1082 System Information Discovery (10.80%); T1059 Command and Scripting Interpreter (5.06%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1205 Traffic Signaling (61.90%); T1033 System Owner/User Discovery (19.50%); T1082 System Information Discovery (5.56%) | 0.00% | False |

## markov_200 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.93%); T1071 Application Layer Protocol (0.02%); T1205 Traffic Signaling (0.01%) | 99.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.62%); T1548 Abuse Elevation Control Mechanism (1.71%); T1098 Account Manipulation (0.24%) | 97.62% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.79%); T1569 System Services (0.13%); T1057 Process Discovery (0.03%) | 99.79% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (89.04%); T1592 Gather Victim Host Information (5.47%); T1190 Exploit Public-Facing Application (5.17%) | 89.04% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.85%); T1059 Command and Scripting Interpreter (0.04%); T1610 Deploy Container (0.02%) | 99.85% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (75.75%); T1087 Account Discovery (24.05%); T1033 System Owner/User Discovery (0.04%) | 24.05% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1564 Hide Artifacts (0.03%); T1039 Data from Network Shared Drive (0.00%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.93%); T1021 Remote Services (0.18%); T1083 File and Directory Discovery (0.16%) | 98.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1218 System Binary Proxy Execution (11.07%); T1557 Adversary-in-the-Middle (9.66%); T1543 Create or Modify System Process (9.05%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (17.75%); T1564 Hide Artifacts (13.80%); T1543 Create or Modify System Process (13.46%) | 0.00% | False |

## markov_200 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1528 Steal Application Access Token (0.02%); T1531 Account Access Removal (0.02%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.83%); T1548 Abuse Elevation Control Mechanism (1.80%); T1082 System Information Discovery (0.20%) | 97.83% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.69%); T1614 System Location Discovery (0.14%); T1518 Software Discovery (0.05%) | 99.69% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (77.42%); T1592 Gather Victim Host Information (11.99%); T1190 Exploit Public-Facing Application (10.39%) | 77.42% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.86%); T1059 Command and Scripting Interpreter (6.03%); T1087 Account Discovery (0.63%) | 92.86% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (91.85%); T1059 Command and Scripting Interpreter (7.24%); T1105 Ingress Tool Transfer (0.50%) | 91.85% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.69%); T1033 System Owner/User Discovery (0.11%); T1068 Exploitation for Privilege Escalation (0.10%) | 99.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.83%); T1039 Data from Network Shared Drive (0.03%); T1204 User Execution (0.02%) | 99.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (41.63%); T1039 Data from Network Shared Drive (24.84%); T1599 Network Boundary Bridging (12.89%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1010 Application Window Discovery (30.47%); T1039 Data from Network Shared Drive (17.66%); T1053 Scheduled Task/Job (12.86%) | 0.00% | False |

## markov_200 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.19%); T1039 Data from Network Shared Drive (2.39%); T1569 System Services (0.05%) | 97.19% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.89%); T1548 Abuse Elevation Control Mechanism (1.78%); T1105 Ingress Tool Transfer (0.07%) | 97.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1518 Software Discovery (0.01%); T1087 Account Discovery (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (84.44%); T1592 Gather Victim Host Information (10.05%); T1190 Exploit Public-Facing Application (4.96%) | 84.44% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.74%); T1059 Command and Scripting Interpreter (1.14%); T1219 Remote Access Tools (0.03%) | 98.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (82.05%); T1059 Command and Scripting Interpreter (10.69%); T1105 Ingress Tool Transfer (7.02%) | 82.05% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.28%); T1105 Ingress Tool Transfer (0.40%); T1124 System Time Discovery (0.05%) | 99.28% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.16%); T1039 Data from Network Shared Drive (0.31%); T1082 System Information Discovery (0.19%) | 99.16% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1071 Application Layer Protocol (31.40%); T1222 File and Directory Permissions Modification (23.51%); T1059 Command and Scripting Interpreter (21.96%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1574 Hijack Execution Flow (18.02%); T1105 Ingress Tool Transfer (14.30%); T1078 Valid Accounts (9.08%) | 0.00% | False |

## markov_200 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.79%); T1057 Process Discovery (0.08%); T1078 Valid Accounts (0.07%) | 99.79% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.83%); T1190 Exploit Public-Facing Application (0.05%); T1548 Abuse Elevation Control Mechanism (0.04%) | 99.83% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.87%); T1485 Data Destruction (0.04%); T1072 Software Deployment Tools (0.01%) | 99.87% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (52.90%); T1595 Active Scanning (43.19%); T1592 Gather Victim Host Information (3.71%) | 43.19% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.70%); T1059 Command and Scripting Interpreter (3.12%); T1547 Boot or Logon Autostart Execution (0.39%) | 95.70% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (63.30%); T1059 Command and Scripting Interpreter (36.43%); T1105 Ingress Tool Transfer (0.13%) | 63.30% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1120 Peripheral Device Discovery (0.11%); T1072 Software Deployment Tools (0.04%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.48%); T1547 Boot or Logon Autostart Execution (0.19%); T1565 Data Manipulation (0.07%) | 99.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (22.98%); T1213 Data from Information Repositories (20.90%); T1049 System Network Connections Discovery (13.84%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1213 Data from Information Repositories (43.10%); T1049 System Network Connections Discovery (17.00%); T1564 Hide Artifacts (13.10%) | 0.03% | False |

## markov_200 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.94%); T1074 Data Staged (1.89%); T1565 Data Manipulation (1.85%) | 94.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.88%); T1548 Abuse Elevation Control Mechanism (0.82%); T1005 Data from Local System (0.19%) | 98.88% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.55%); T1589 Gather Victim Identity Information (0.35%); T1133 External Remote Services (0.01%) | 99.55% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (88.76%); T1592 Gather Victim Host Information (4.94%); T1190 Exploit Public-Facing Application (4.45%) | 88.76% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.61%); T1218 System Binary Proxy Execution (0.58%); T1059 Command and Scripting Interpreter (0.49%) | 98.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (49.70%); T1087 Account Discovery (43.07%); T1105 Ingress Tool Transfer (6.78%) | 43.07% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1557 Adversary-in-the-Middle (0.02%); T1589 Gather Victim Identity Information (0.01%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.29%); T1039 Data from Network Shared Drive (0.19%); T1083 File and Directory Discovery (0.08%) | 99.29% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1547 Boot or Logon Autostart Execution (54.52%); T1033 System Owner/User Discovery (18.42%); T1548 Abuse Elevation Control Mechanism (7.60%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1489 Service Stop (17.06%); T1120 Peripheral Device Discovery (15.13%); T1565 Data Manipulation (9.37%) | 5.73% | False |

## markov_200 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1059 Command and Scripting Interpreter (0.03%); T1219 Remote Access Tools (0.02%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1105 Ingress Tool Transfer (0.07%); T1059 Command and Scripting Interpreter (0.03%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.05%); T1007 System Service Discovery (1.79%); T1550 Use Alternate Authentication Material (0.03%) | 98.05% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (52.17%); T1190 Exploit Public-Facing Application (45.78%); T1592 Gather Victim Host Information (1.59%) | 52.17% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.77%); T1059 Command and Scripting Interpreter (1.34%); T1136 Create Account (0.28%) | 97.77% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (74.21%); T1059 Command and Scripting Interpreter (24.56%); T1105 Ingress Tool Transfer (1.10%) | 74.21% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1124 System Time Discovery (0.02%); T1205 Traffic Signaling (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.81%); T1021 Remote Services (0.05%); T1573 Encrypted Channel (0.02%) | 99.81% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1219 Remote Access Tools (39.91%); T1190 Exploit Public-Facing Application (18.13%); T1082 System Information Discovery (10.41%) | 0.19% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (53.12%); T1531 Account Access Removal (8.29%); T1059 Command and Scripting Interpreter (7.71%) | 0.00% | False |

## markov_200 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1599 Network Boundary Bridging (0.02%); T1083 File and Directory Discovery (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.14%); T1548 Abuse Elevation Control Mechanism (3.28%); T1070 Indicator Removal (0.20%) | 96.14% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1057 Process Discovery (0.02%); T1497 Virtualization/Sandbox Evasion (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (64.48%); T1190 Exploit Public-Facing Application (19.31%); T1592 Gather Victim Host Information (15.92%) | 64.48% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.43%); T1059 Command and Scripting Interpreter (0.09%); T1547 Boot or Logon Autostart Execution (0.05%) | 99.43% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (82.46%); T1087 Account Discovery (17.29%); T1105 Ingress Tool Transfer (0.12%) | 17.29% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1124 System Time Discovery (0.05%); T1083 File and Directory Discovery (0.04%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.81%); T1543 Create or Modify System Process (0.26%); T1049 System Network Connections Discovery (0.23%) | 98.81% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (58.50%); T1136 Create Account (10.21%); T1033 System Owner/User Discovery (5.88%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1074 Data Staged (30.20%); T1033 System Owner/User Discovery (13.69%); T1218 System Binary Proxy Execution (11.78%) | 0.00% | False |

## markov_200 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (88.88%); T1525 Implant Internal Image (3.23%); T1486 Data Encrypted for Impact (2.97%) | 88.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.49%); T1548 Abuse Elevation Control Mechanism (0.31%); T1105 Ingress Tool Transfer (0.08%) | 99.49% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.91%); T1201 Password Policy Discovery (0.01%); T1556 Modify Authentication Process (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (89.88%); T1190 Exploit Public-Facing Application (6.65%); T1592 Gather Victim Host Information (3.29%) | 89.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.13%); T1059 Command and Scripting Interpreter (4.13%); T1082 System Information Discovery (1.00%) | 94.13% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (68.16%); T1059 Command and Scripting Interpreter (31.50%); T1105 Ingress Tool Transfer (0.27%) | 68.16% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.65%); T1486 Data Encrypted for Impact (0.14%); T1218 System Binary Proxy Execution (0.03%) | 99.65% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.32%); T1003 OS Credential Dumping (0.27%); T1039 Data from Network Shared Drive (0.08%) | 99.32% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1133 External Remote Services (41.09%); T1033 System Owner/User Discovery (20.52%); T1059 Command and Scripting Interpreter (13.22%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1133 External Remote Services (23.80%); T1124 System Time Discovery (15.62%); T1007 System Service Discovery (9.76%) | 0.00% | False |

## markov_200 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.15%); T1201 Password Policy Discovery (0.72%); T1595 Active Scanning (0.02%) | 99.15% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (49.33%); T1548 Abuse Elevation Control Mechanism (49.06%); T1078 Valid Accounts (0.40%) | 49.33% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.96%); T1033 System Owner/User Discovery (0.01%); T1543 Create or Modify System Process (0.00%) | 99.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (65.60%); T1190 Exploit Public-Facing Application (22.29%); T1592 Gather Victim Host Information (11.81%) | 65.60% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.31%); T1059 Command and Scripting Interpreter (0.54%); T1614 System Location Discovery (0.05%) | 99.31% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (75.01%); T1087 Account Discovery (23.21%); T1105 Ingress Tool Transfer (1.51%) | 23.21% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.78%); T1136 Create Account (0.05%); T1574 Hijack Execution Flow (0.04%) | 99.78% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.09%); T1041 Exfiltration Over C2 Channel (0.51%); T1083 File and Directory Discovery (0.11%) | 99.09% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (43.48%); T1041 Exfiltration Over C2 Channel (36.30%); T1059 Command and Scripting Interpreter (10.59%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1497 Virtualization/Sandbox Evasion (45.05%); T1222 File and Directory Permissions Modification (29.81%); T1057 Process Discovery (8.24%) | 0.02% | False |

## markov_200 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.03%); T1590 Gather Victim Network Information (0.75%); T1074 Data Staged (0.05%) | 99.03% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (90.83%); T1548 Abuse Elevation Control Mechanism (6.82%); T1059 Command and Scripting Interpreter (1.03%) | 90.83% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1003 OS Credential Dumping (0.05%); T1083 File and Directory Discovery (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (38.87%); T1595 Active Scanning (38.26%); T1592 Gather Victim Host Information (22.61%) | 38.26% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.44%); T1059 Command and Scripting Interpreter (0.51%); T1068 Exploitation for Privilege Escalation (0.29%) | 98.44% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (53.17%); T1087 Account Discovery (44.83%); T1105 Ingress Tool Transfer (1.32%) | 44.83% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.98%); T1614 System Location Discovery (0.01%); T1041 Exfiltration Over C2 Channel (0.00%) | 99.98% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.66%); T1078 Valid Accounts (0.08%); T1201 Password Policy Discovery (0.03%) | 99.66% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (96.19%); T1005 Data from Local System (1.11%); T1201 Password Policy Discovery (0.58%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (77.05%); T1222 File and Directory Permissions Modification (3.51%); T1105 Ingress Tool Transfer (2.43%) | 0.06% | False |

## markov_200 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.95%); T1071 Application Layer Protocol (0.01%); T1572 Protocol Tunneling (0.01%) | 99.95% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (56.98%); T1033 System Owner/User Discovery (42.07%); T1005 Data from Local System (0.35%) | 42.07% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.75%); T1569 System Services (0.19%); T1525 Implant Internal Image (0.02%) | 99.75% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (58.27%); T1190 Exploit Public-Facing Application (35.78%); T1592 Gather Victim Host Information (4.53%) | 58.27% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.87%); T1059 Command and Scripting Interpreter (0.06%); T1068 Exploitation for Privilege Escalation (0.01%) | 99.87% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (82.69%); T1087 Account Discovery (11.94%); T1105 Ingress Tool Transfer (5.15%) | 11.94% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.82%); T1528 Steal Application Access Token (0.14%); T1573 Encrypted Channel (0.01%) | 99.82% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.17%); T1003 OS Credential Dumping (0.20%); T1021 Remote Services (0.18%) | 99.17% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1490 Inhibit System Recovery (39.58%); T1040 Network Sniffing (20.65%); T1528 Steal Application Access Token (13.24%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (27.99%); T1201 Password Policy Discovery (24.17%); T1518 Software Discovery (6.65%) | 0.10% | False |

## markov_200 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1590 Gather Victim Network Information (0.04%); T1489 Service Stop (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (94.56%); T1548 Abuse Elevation Control Mechanism (4.84%); T1218 System Binary Proxy Execution (0.26%) | 94.56% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.64%); T1614 System Location Discovery (0.22%); T1201 Password Policy Discovery (0.03%) | 99.64% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (43.25%); T1190 Exploit Public-Facing Application (34.92%); T1592 Gather Victim Host Information (21.52%) | 43.25% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.12%); T1059 Command and Scripting Interpreter (3.83%); T1087 Account Discovery (0.38%) | 95.12% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (60.21%); T1087 Account Discovery (37.26%); T1105 Ingress Tool Transfer (1.69%) | 37.26% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.86%); T1124 System Time Discovery (0.06%); T1572 Protocol Tunneling (0.03%) | 99.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.06%); T1204 User Execution (0.43%); T1574 Hijack Execution Flow (0.15%) | 99.06% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1074 Data Staged (51.72%); T1014 Rootkit (15.43%); T1531 Account Access Removal (9.49%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1080 Taint Shared Content (20.43%); T1176 Software Extensions (19.28%); T1040 Network Sniffing (13.35%) | 0.53% | False |

## markov_200 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.13%); T1039 Data from Network Shared Drive (0.68%); T1046 Network Service Scanning (0.03%) | 99.13% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (73.91%); T1548 Abuse Elevation Control Mechanism (25.59%); T1036 Masquerading (0.20%) | 73.91% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1059 Command and Scripting Interpreter (0.01%); T1105 Ingress Tool Transfer (0.01%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (46.18%); T1190 Exploit Public-Facing Application (36.88%); T1592 Gather Victim Host Information (15.76%) | 46.18% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.66%); T1059 Command and Scripting Interpreter (0.22%); T1219 Remote Access Tools (0.01%) | 99.66% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (77.00%); T1087 Account Discovery (21.53%); T1105 Ingress Tool Transfer (1.37%) | 21.53% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.74%); T1105 Ingress Tool Transfer (0.13%); T1059 Command and Scripting Interpreter (0.04%) | 99.74% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.91%); T1133 External Remote Services (0.02%); T1021 Remote Services (0.01%) | 99.91% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1098 Account Manipulation (25.87%); T1053 Scheduled Task/Job (12.58%); T1213 Data from Information Repositories (8.16%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1219 Remote Access Tools (63.22%); T1222 File and Directory Permissions Modification (8.78%); T1080 Taint Shared Content (5.21%) | 0.08% | False |

## markov_200 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1078 Valid Accounts (0.00%); T1056 Input Capture (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (49.15%); T1033 System Owner/User Discovery (48.10%); T1003 OS Credential Dumping (0.67%) | 48.10% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1010 Application Window Discovery (0.01%); T1133 External Remote Services (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (48.08%); T1595 Active Scanning (40.47%); T1592 Gather Victim Host Information (10.55%) | 40.47% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.79%); T1059 Command and Scripting Interpreter (1.65%); T1610 Deploy Container (0.19%) | 97.79% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (73.87%); T1087 Account Discovery (25.10%); T1105 Ingress Tool Transfer (0.74%) | 25.10% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.87%); T1614 System Location Discovery (0.03%); T1589 Gather Victim Identity Information (0.03%) | 99.87% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.83%); T1041 Exfiltration Over C2 Channel (0.05%); T1518 Software Discovery (0.02%) | 99.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1041 Exfiltration Over C2 Channel (39.29%); T1046 Network Service Scanning (38.52%); T1201 Password Policy Discovery (3.41%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1046 Network Service Scanning (24.03%); T1041 Exfiltration Over C2 Channel (18.61%); T1592 Gather Victim Host Information (18.49%) | 0.01% | False |

## markov_200 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.12%); T1074 Data Staged (1.57%); T1565 Data Manipulation (1.28%) | 96.12% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (65.76%); T1548 Abuse Elevation Control Mechanism (33.29%); T1070 Indicator Removal (0.19%) | 65.76% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.42%); T1589 Gather Victim Identity Information (0.38%); T1049 System Network Connections Discovery (0.06%) | 99.42% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (46.27%); T1595 Active Scanning (33.60%); T1592 Gather Victim Host Information (18.04%) | 33.60% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.59%); T1218 System Binary Proxy Execution (0.66%); T1592 Gather Victim Host Information (0.35%) | 98.59% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.78%); T1087 Account Discovery (17.22%); T1105 Ingress Tool Transfer (3.78%) | 17.22% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1547 Boot or Logon Autostart Execution (0.02%); T1557 Adversary-in-the-Middle (0.01%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.26%); T1120 Peripheral Device Discovery (0.27%); T1078 Valid Accounts (0.07%) | 99.26% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1610 Deploy Container (64.23%); T1219 Remote Access Tools (6.81%); T1572 Protocol Tunneling (5.61%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (47.54%); T1082 System Information Discovery (21.47%); T1176 Software Extensions (6.38%) | 0.00% | False |

## markov_200 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.99%); T1072 Software Deployment Tools (0.00%); T1213 Data from Information Repositories (0.00%) | 99.99% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.54%); T1548 Abuse Elevation Control Mechanism (2.88%); T1105 Ingress Tool Transfer (0.21%) | 96.54% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.67%); T1007 System Service Discovery (0.21%); T1590 Gather Victim Network Information (0.05%) | 99.67% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (60.26%); T1595 Active Scanning (38.10%); T1592 Gather Victim Host Information (1.47%) | 38.10% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.02%); T1518 Software Discovery (0.20%); T1059 Command and Scripting Interpreter (0.13%) | 99.02% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (54.06%); T1087 Account Discovery (45.62%); T1105 Ingress Tool Transfer (0.10%) | 45.62% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.95%); T1124 System Time Discovery (0.01%); T1014 Rootkit (0.01%) | 99.95% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.64%); T1553 Subvert Trust Controls (0.11%); T1072 Software Deployment Tools (0.04%) | 99.64% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1610 Deploy Container (35.82%); T1098 Account Manipulation (32.74%); T1485 Data Destruction (3.84%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (71.18%); T1010 Application Window Discovery (8.42%); T1176 Software Extensions (6.04%) | 0.00% | False |

## markov_200 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1589 Gather Victim Identity Information (0.00%); T1565 Data Manipulation (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (53.84%); T1548 Abuse Elevation Control Mechanism (42.72%); T1036 Masquerading (0.48%) | 53.84% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1201 Password Policy Discovery (0.04%); T1007 System Service Discovery (0.03%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (40.27%); T1190 Exploit Public-Facing Application (36.70%); T1592 Gather Victim Host Information (21.44%) | 40.27% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.71%); T1070 Indicator Removal (0.06%); T1525 Implant Internal Image (0.03%) | 99.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (88.06%); T1087 Account Discovery (10.59%); T1105 Ingress Tool Transfer (0.85%) | 10.59% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1553 Subvert Trust Controls (0.02%); T1204 User Execution (0.02%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.61%); T1486 Data Encrypted for Impact (0.07%); T1590 Gather Victim Network Information (0.04%) | 99.61% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1057 Process Discovery (31.68%); T1072 Software Deployment Tools (15.47%); T1543 Create or Modify System Process (10.10%) | 0.38% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (46.82%); T1564 Hide Artifacts (41.30%); T1080 Taint Shared Content (4.33%) | 0.03% | False |

## markov_200 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (89.58%); T1525 Implant Internal Image (4.55%); T1110 Brute Force (2.29%) | 89.58% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (88.82%); T1548 Abuse Elevation Control Mechanism (9.90%); T1070 Indicator Removal (0.69%) | 88.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1553 Subvert Trust Controls (0.01%); T1087 Account Discovery (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (45.23%); T1190 Exploit Public-Facing Application (35.21%); T1592 Gather Victim Host Information (19.38%) | 45.23% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.09%); T1059 Command and Scripting Interpreter (0.56%); T1036 Masquerading (0.47%) | 98.09% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (63.99%); T1087 Account Discovery (35.06%); T1105 Ingress Tool Transfer (0.64%) | 35.06% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1590 Gather Victim Network Information (0.02%); T1589 Gather Victim Identity Information (0.01%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.70%); T1021 Remote Services (0.96%); T1003 OS Credential Dumping (0.05%) | 98.70% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (49.22%); T1055 Process Injection (30.46%); T1190 Exploit Public-Facing Application (6.23%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1213 Data from Information Repositories (28.02%); T1007 System Service Discovery (8.43%); T1485 Data Destruction (6.72%) | 1.39% | False |

## markov_25 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.22%); T1201 Password Policy Discovery (3.19%); T1213 Data from Information Repositories (0.10%) | 96.22% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.38%); T1548 Abuse Elevation Control Mechanism (0.43%); T1105 Ingress Tool Transfer (0.03%) | 99.38% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.80%); T1018 Remote System Discovery (0.03%); T1033 System Owner/User Discovery (0.02%) | 99.80% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.71%); T1592 Gather Victim Host Information (0.61%); T1190 Exploit Public-Facing Application (0.48%) | 98.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.79%); T1059 Command and Scripting Interpreter (0.55%); T1219 Remote Access Tools (0.10%) | 98.79% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (64.21%); T1087 Account Discovery (35.51%); T1566 Phishing (0.03%) | 35.51% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.52%); T1566 Phishing (0.04%); T1201 Password Policy Discovery (0.04%) | 99.52% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.26%); T1083 File and Directory Discovery (0.38%); T1039 Data from Network Shared Drive (0.25%) | 98.26% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1548 Abuse Elevation Control Mechanism (44.45%); T1222 File and Directory Permissions Modification (11.01%); T1105 Ingress Tool Transfer (7.16%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1071 Application Layer Protocol (23.63%); T1548 Abuse Elevation Control Mechanism (19.81%); T1222 File and Directory Permissions Modification (15.69%) | 0.01% | False |

## markov_25 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.67%); T1595 Active Scanning (0.06%); T1087 Account Discovery (0.04%) | 99.67% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.05%); T1105 Ingress Tool Transfer (0.28%); T1095 Non-Application Layer Protocol (0.16%) | 99.05% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.72%); T1615 Group Policy Discovery (0.05%); T1083 File and Directory Discovery (0.03%) | 99.72% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.49%); T1190 Exploit Public-Facing Application (0.22%); T1592 Gather Victim Host Information (0.05%) | 99.49% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.04%); T1059 Command and Scripting Interpreter (0.54%); T1547 Boot or Logon Autostart Execution (0.05%) | 99.04% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.35%); T1059 Command and Scripting Interpreter (0.25%); T1053 Scheduled Task/Job (0.06%) | 99.35% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.39%); T1485 Data Destruction (0.14%); T1124 System Time Discovery (0.08%) | 99.39% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.48%); T1120 Peripheral Device Discovery (0.56%); T1039 Data from Network Shared Drive (0.23%) | 98.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (57.19%); T1219 Remote Access Tools (7.99%); T1222 File and Directory Permissions Modification (7.57%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (21.69%); T1591 Gather Victim Org Information (10.04%); T1222 File and Directory Permissions Modification (8.45%) | 0.28% | False |

## markov_25 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.75%); T1136 Create Account (0.02%); T1486 Data Encrypted for Impact (0.02%) | 99.75% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.74%); T1082 System Information Discovery (0.06%); T1548 Abuse Elevation Control Mechanism (0.05%) | 99.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1057 Process Discovery (0.07%); T1531 Account Access Removal (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.88%); T1592 Gather Victim Host Information (2.97%); T1190 Exploit Public-Facing Application (0.83%) | 95.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.15%); T1059 Command and Scripting Interpreter (0.36%); T1071 Application Layer Protocol (0.12%) | 99.15% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (84.78%); T1059 Command and Scripting Interpreter (14.91%); T1083 File and Directory Discovery (0.04%) | 84.78% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.06%); T1556 Modify Authentication Process (0.35%); T1124 System Time Discovery (0.14%) | 99.06% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.85%); T1083 File and Directory Discovery (0.36%); T1120 Peripheral Device Discovery (0.11%) | 98.85% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (37.67%); T1213 Data from Information Repositories (18.53%); T1222 File and Directory Permissions Modification (16.05%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (81.01%); T1033 System Owner/User Discovery (5.05%); T1078 Valid Accounts (3.96%) | 0.06% | False |

## markov_25 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.64%); T1105 Ingress Tool Transfer (0.08%); T1078 Valid Accounts (0.06%) | 99.64% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.65%); T1105 Ingress Tool Transfer (0.58%); T1548 Abuse Elevation Control Mechanism (0.45%) | 98.65% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.82%); T1176 Software Extensions (0.03%); T1133 External Remote Services (0.02%) | 99.82% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.01%); T1190 Exploit Public-Facing Application (3.40%); T1589 Gather Victim Identity Information (0.15%) | 96.01% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.78%); T1059 Command and Scripting Interpreter (3.31%); T1547 Boot or Logon Autostart Execution (0.39%) | 94.78% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.30%); T1059 Command and Scripting Interpreter (4.23%); T1105 Ingress Tool Transfer (0.15%) | 95.30% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.41%); T1124 System Time Discovery (0.12%); T1190 Exploit Public-Facing Application (0.09%) | 99.41% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.36%); T1204 User Execution (2.31%); T1120 Peripheral Device Discovery (0.22%) | 96.36% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (42.70%); T1110 Brute Force (9.60%); T1133 External Remote Services (8.64%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1070 Indicator Removal (44.55%); T1078 Valid Accounts (22.57%); T1546 Event Triggered Execution (5.40%) | 0.00% | False |

## markov_25 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.60%); T1205 Traffic Signaling (0.03%); T1053 Scheduled Task/Job (0.03%) | 99.60% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.70%); T1548 Abuse Elevation Control Mechanism (0.09%); T1105 Ingress Tool Transfer (0.04%) | 99.70% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.60%); T1201 Password Policy Discovery (0.08%); T1057 Process Discovery (0.07%) | 99.60% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.58%); T1190 Exploit Public-Facing Application (0.14%); T1592 Gather Victim Host Information (0.12%) | 99.58% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.51%); T1059 Command and Scripting Interpreter (6.81%); T1105 Ingress Tool Transfer (0.14%) | 92.51% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (51.19%); T1087 Account Discovery (48.35%); T1083 File and Directory Discovery (0.11%) | 48.35% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.58%); T1124 System Time Discovery (0.08%); T1610 Deploy Container (0.04%) | 99.58% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.24%); T1039 Data from Network Shared Drive (0.18%); T1072 Software Deployment Tools (0.08%) | 99.24% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1007 System Service Discovery (34.76%); T1041 Exfiltration Over C2 Channel (12.91%); T1016 System Network Configuration Discovery (11.63%) | 0.41% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1041 Exfiltration Over C2 Channel (45.57%); T1078 Valid Accounts (11.46%); T1546 Event Triggered Execution (11.07%) | 0.00% | False |

## markov_25 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.58%); T1083 File and Directory Discovery (0.05%); T1531 Account Access Removal (0.03%) | 99.58% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.43%); T1190 Exploit Public-Facing Application (0.14%); T1548 Abuse Elevation Control Mechanism (0.10%) | 99.43% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.55%); T1072 Software Deployment Tools (0.08%); T1201 Password Policy Discovery (0.04%) | 99.55% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.52%); T1190 Exploit Public-Facing Application (4.30%); T1592 Gather Victim Host Information (0.59%) | 94.52% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.35%); T1059 Command and Scripting Interpreter (2.30%); T1547 Boot or Logon Autostart Execution (0.19%) | 96.35% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (57.20%); T1059 Command and Scripting Interpreter (41.83%); T1105 Ingress Tool Transfer (0.46%) | 57.20% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.70%); T1072 Software Deployment Tools (0.05%); T1070 Indicator Removal (0.04%) | 99.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.06%); T1039 Data from Network Shared Drive (0.69%); T1071 Application Layer Protocol (0.14%) | 98.06% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (17.88%); T1574 Hijack Execution Flow (14.54%); T1105 Ingress Tool Transfer (12.72%) | 0.22% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (18.82%); T1574 Hijack Execution Flow (15.47%); T1105 Ingress Tool Transfer (12.28%) | 0.01% | False |

## markov_25 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (91.84%); T1074 Data Staged (7.39%); T1589 Gather Victim Identity Information (0.11%) | 91.84% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (89.98%); T1548 Abuse Elevation Control Mechanism (9.17%); T1105 Ingress Tool Transfer (0.16%) | 89.98% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.59%); T1046 Network Service Scanning (0.05%); T1057 Process Discovery (0.04%) | 99.59% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.46%); T1592 Gather Victim Host Information (3.08%); T1190 Exploit Public-Facing Application (0.15%) | 96.46% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (90.43%); T1059 Command and Scripting Interpreter (8.62%); T1083 File and Directory Discovery (0.09%) | 90.43% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.75%); T1059 Command and Scripting Interpreter (1.77%); T1083 File and Directory Discovery (0.11%) | 97.75% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1049 System Network Connections Discovery (0.02%); T1547 Boot or Logon Autostart Execution (0.01%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.20%); T1033 System Owner/User Discovery (0.38%); T1039 Data from Network Shared Drive (0.33%) | 98.20% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (47.56%); T1059 Command and Scripting Interpreter (27.69%); T1105 Ingress Tool Transfer (9.76%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (56.46%); T1176 Software Extensions (10.79%); T1564 Hide Artifacts (5.42%) | 0.07% | False |

## markov_25 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.61%); T1589 Gather Victim Identity Information (0.11%); T1059 Command and Scripting Interpreter (0.04%) | 99.61% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.71%); T1548 Abuse Elevation Control Mechanism (0.09%); T1105 Ingress Tool Transfer (0.09%) | 99.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1557 Adversary-in-the-Middle (0.02%); T1201 Password Policy Discovery (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.73%); T1190 Exploit Public-Facing Application (0.11%); T1589 Gather Victim Identity Information (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.15%); T1059 Command and Scripting Interpreter (0.28%); T1105 Ingress Tool Transfer (0.07%) | 99.15% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (96.74%); T1059 Command and Scripting Interpreter (2.81%); T1565 Data Manipulation (0.11%) | 96.74% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.62%); T1059 Command and Scripting Interpreter (0.04%); T1566 Phishing (0.04%) | 99.62% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.71%); T1039 Data from Network Shared Drive (0.22%); T1003 OS Credential Dumping (0.11%) | 98.71% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (68.42%); T1222 File and Directory Permissions Modification (3.87%); T1059 Command and Scripting Interpreter (3.42%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (51.90%); T1222 File and Directory Permissions Modification (23.08%); T1201 Password Policy Discovery (2.80%) | 0.01% | False |

## markov_25 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.67%); T1595 Active Scanning (0.02%); T1589 Gather Victim Identity Information (0.02%) | 99.67% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.32%); T1557 Adversary-in-the-Middle (0.20%); T1548 Abuse Elevation Control Mechanism (0.10%) | 99.32% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.63%); T1518 Software Discovery (0.06%); T1087 Account Discovery (0.04%) | 99.63% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.83%); T1190 Exploit Public-Facing Application (0.44%); T1592 Gather Victim Host Information (0.42%) | 98.83% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (93.71%); T1059 Command and Scripting Interpreter (3.86%); T1547 Boot or Logon Autostart Execution (0.53%) | 93.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (79.10%); T1087 Account Discovery (20.61%); T1070 Indicator Removal (0.06%) | 20.61% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.12%); T1105 Ingress Tool Transfer (0.12%); T1124 System Time Discovery (0.10%) | 99.12% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.24%); T1039 Data from Network Shared Drive (0.58%); T1120 Peripheral Device Discovery (0.21%) | 98.24% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (55.50%); T1566 Phishing (9.31%); T1069 Permission Groups Discovery (6.43%) | 0.11% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (59.33%); T1566 Phishing (11.69%); T1557 Adversary-in-the-Middle (3.35%) | 0.04% | False |

## markov_25 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (91.96%); T1115 Clipboard Data (7.25%); T1018 Remote System Discovery (0.06%) | 91.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.55%); T1548 Abuse Elevation Control Mechanism (1.11%); T1218 System Binary Proxy Execution (0.09%) | 98.55% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.66%); T1057 Process Discovery (0.03%); T1003 OS Credential Dumping (0.03%) | 99.66% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.55%); T1190 Exploit Public-Facing Application (0.20%); T1589 Gather Victim Identity Information (0.08%) | 99.55% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.56%); T1059 Command and Scripting Interpreter (0.12%); T1053 Scheduled Task/Job (0.04%) | 99.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.35%); T1059 Command and Scripting Interpreter (0.40%); T1133 External Remote Services (0.03%) | 99.35% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1572 Protocol Tunneling (0.02%); T1490 Inhibit System Recovery (0.02%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.50%); T1039 Data from Network Shared Drive (0.57%); T1033 System Owner/User Discovery (0.26%) | 97.50% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1071 Application Layer Protocol (20.23%); T1133 External Remote Services (17.32%); T1565 Data Manipulation (8.79%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (54.44%); T1553 Subvert Trust Controls (8.60%); T1218 System Binary Proxy Execution (6.27%) | 0.01% | False |

## markov_25 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.69%); T1201 Password Policy Discovery (2.41%); T1074 Data Staged (0.10%) | 96.69% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.74%); T1548 Abuse Elevation Control Mechanism (0.85%); T1036 Masquerading (0.14%) | 98.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.77%); T1518 Software Discovery (0.04%); T1543 Create or Modify System Process (0.02%) | 99.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.28%); T1592 Gather Victim Host Information (0.30%); T1190 Exploit Public-Facing Application (0.19%) | 99.28% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.99%); T1059 Command and Scripting Interpreter (0.58%); T1055 Process Injection (0.04%) | 98.99% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.86%); T1082 System Information Discovery (0.02%); T1083 File and Directory Discovery (0.01%) | 99.86% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1124 System Time Discovery (0.05%); T1055 Process Injection (0.04%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.12%); T1039 Data from Network Shared Drive (0.37%); T1078 Valid Accounts (0.19%) | 98.12% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (64.92%); T1222 File and Directory Permissions Modification (25.67%); T1120 Peripheral Device Discovery (1.89%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (60.16%); T1222 File and Directory Permissions Modification (19.16%); T1120 Peripheral Device Discovery (5.90%) | 0.03% | False |

## markov_25 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.51%); T1110 Brute Force (0.06%); T1595 Active Scanning (0.03%) | 99.51% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.19%); T1036 Masquerading (0.33%); T1548 Abuse Elevation Control Mechanism (0.31%) | 98.19% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.69%); T1083 File and Directory Discovery (0.07%); T1204 User Execution (0.05%) | 99.69% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.51%); T1190 Exploit Public-Facing Application (0.23%); T1589 Gather Victim Identity Information (0.06%) | 99.51% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.61%); T1059 Command and Scripting Interpreter (1.66%); T1069 Permission Groups Discovery (0.12%) | 97.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.37%); T1059 Command and Scripting Interpreter (1.23%); T1033 System Owner/User Discovery (0.09%) | 98.37% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.72%); T1124 System Time Discovery (0.05%); T1546 Event Triggered Execution (0.03%) | 99.72% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.57%); T1039 Data from Network Shared Drive (0.21%); T1082 System Information Discovery (0.16%) | 98.57% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1068 Exploitation for Privilege Escalation (37.72%); T1072 Software Deployment Tools (14.67%); T1082 System Information Discovery (9.80%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (86.95%); T1566 Phishing (2.82%); T1003 OS Credential Dumping (2.53%) | 0.01% | False |

## markov_25 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.35%); T1556 Modify Authentication Process (0.15%); T1071 Application Layer Protocol (0.08%) | 99.35% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.44%); T1548 Abuse Elevation Control Mechanism (0.68%); T1190 Exploit Public-Facing Application (0.18%) | 98.44% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1057 Process Discovery (0.05%); T1485 Data Destruction (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.61%); T1592 Gather Victim Host Information (1.97%); T1190 Exploit Public-Facing Application (0.94%) | 96.61% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.35%); T1059 Command and Scripting Interpreter (1.40%); T1071 Application Layer Protocol (0.25%) | 97.35% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (80.31%); T1087 Account Discovery (19.41%); T1124 System Time Discovery (0.03%) | 19.41% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.53%); T1219 Remote Access Tools (0.05%); T1556 Modify Authentication Process (0.05%) | 99.53% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.25%); T1083 File and Directory Discovery (0.22%); T1518 Software Discovery (0.18%) | 98.25% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (61.67%); T1003 OS Credential Dumping (5.53%); T1213 Data from Information Repositories (3.45%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (33.46%); T1222 File and Directory Permissions Modification (21.90%); T1033 System Owner/User Discovery (20.65%) | 0.02% | False |

## markov_25 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.57%); T1105 Ingress Tool Transfer (0.12%); T1557 Adversary-in-the-Middle (0.05%) | 99.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.16%); T1548 Abuse Elevation Control Mechanism (0.50%); T1218 System Binary Proxy Execution (0.09%) | 99.16% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.55%); T1133 External Remote Services (0.15%); T1021 Remote Services (0.03%) | 99.55% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.96%); T1190 Exploit Public-Facing Application (3.36%); T1592 Gather Victim Host Information (0.23%) | 95.96% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.25%); T1059 Command and Scripting Interpreter (0.91%); T1078 Valid Accounts (0.13%) | 98.25% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (88.59%); T1059 Command and Scripting Interpreter (11.07%); T1082 System Information Discovery (0.04%) | 88.59% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.50%); T1033 System Owner/User Discovery (0.04%); T1124 System Time Discovery (0.04%) | 99.50% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.31%); T1003 OS Credential Dumping (1.51%); T1204 User Execution (0.21%) | 97.31% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (40.63%); T1059 Command and Scripting Interpreter (19.79%); T1070 Indicator Removal (8.26%) | 1.35% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (50.80%); T1039 Data from Network Shared Drive (7.79%); T1036 Masquerading (7.43%) | 0.09% | False |

## markov_25 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.36%); T1569 System Services (0.07%); T1595 Active Scanning (0.04%) | 99.36% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (94.51%); T1548 Abuse Elevation Control Mechanism (4.38%); T1574 Hijack Execution Flow (0.24%) | 94.51% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.58%); T1057 Process Discovery (0.07%); T1039 Data from Network Shared Drive (0.02%) | 99.58% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.49%); T1190 Exploit Public-Facing Application (0.18%); T1589 Gather Victim Identity Information (0.09%) | 99.49% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.77%); T1059 Command and Scripting Interpreter (0.52%); T1218 System Binary Proxy Execution (0.08%) | 98.77% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (96.87%); T1059 Command and Scripting Interpreter (2.73%); T1574 Hijack Execution Flow (0.04%) | 96.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.26%); T1574 Hijack Execution Flow (0.10%); T1564 Hide Artifacts (0.09%) | 99.26% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.62%); T1039 Data from Network Shared Drive (0.72%); T1083 File and Directory Discovery (0.26%) | 97.62% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1546 Event Triggered Execution (25.69%); T1222 File and Directory Permissions Modification (24.65%); T1120 Peripheral Device Discovery (9.86%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (30.37%); T1546 Event Triggered Execution (12.02%); T1120 Peripheral Device Discovery (11.09%) | 0.01% | False |

## markov_25 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.57%); T1083 File and Directory Discovery (0.06%); T1569 System Services (0.06%) | 99.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.40%); T1548 Abuse Elevation Control Mechanism (1.63%); T1566 Phishing (0.21%) | 97.40% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.21%); T1033 System Owner/User Discovery (0.11%); T1072 Software Deployment Tools (0.09%) | 99.21% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.51%); T1190 Exploit Public-Facing Application (3.82%); T1592 Gather Victim Host Information (0.90%) | 94.51% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.33%); T1059 Command and Scripting Interpreter (3.01%); T1053 Scheduled Task/Job (0.30%) | 94.33% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.09%); T1059 Command and Scripting Interpreter (1.26%); T1105 Ingress Tool Transfer (0.10%) | 98.09% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.02%); T1573 Encrypted Channel (0.27%); T1204 User Execution (0.15%) | 99.02% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.01%); T1039 Data from Network Shared Drive (0.13%); T1040 Network Sniffing (0.07%) | 99.01% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1566 Phishing (14.27%); T1115 Clipboard Data (12.09%); T1036 Masquerading (11.21%) | 0.29% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1486 Data Encrypted for Impact (23.74%); T1213 Data from Information Repositories (16.82%); T1565 Data Manipulation (7.88%) | 1.63% | False |

## markov_25 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.22%); T1074 Data Staged (4.63%); T1110 Brute Force (0.16%) | 94.22% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.89%); T1548 Abuse Elevation Control Mechanism (2.38%); T1547 Boot or Logon Autostart Execution (0.07%) | 96.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.58%); T1222 File and Directory Permissions Modification (0.07%); T1485 Data Destruction (0.04%) | 99.58% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.15%); T1592 Gather Victim Host Information (2.33%); T1190 Exploit Public-Facing Application (0.21%) | 97.15% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (93.21%); T1059 Command and Scripting Interpreter (5.61%); T1573 Encrypted Channel (0.14%) | 93.21% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.08%); T1059 Command and Scripting Interpreter (2.27%); T1105 Ingress Tool Transfer (0.19%) | 97.08% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.53%); T1018 Remote System Discovery (0.13%); T1564 Hide Artifacts (0.07%) | 99.53% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.27%); T1041 Exfiltration Over C2 Channel (0.33%); T1039 Data from Network Shared Drive (0.24%) | 98.27% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (49.68%); T1548 Abuse Elevation Control Mechanism (9.85%); T1564 Hide Artifacts (7.48%) | 0.13% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (22.43%); T1033 System Owner/User Discovery (10.03%); T1531 Account Access Removal (8.60%) | 0.02% | False |

## markov_25 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.46%); T1592 Gather Victim Host Information (0.12%); T1589 Gather Victim Identity Information (0.06%) | 99.46% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.92%); T1548 Abuse Elevation Control Mechanism (0.31%); T1218 System Binary Proxy Execution (0.27%) | 98.92% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.67%); T1518 Software Discovery (0.04%); T1053 Scheduled Task/Job (0.02%) | 99.67% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.58%); T1190 Exploit Public-Facing Application (0.15%); T1589 Gather Victim Identity Information (0.04%) | 99.58% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.93%); T1059 Command and Scripting Interpreter (0.23%); T1105 Ingress Tool Transfer (0.12%) | 98.93% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.44%); T1059 Command and Scripting Interpreter (0.12%); T1033 System Owner/User Discovery (0.09%) | 99.44% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.64%); T1205 Traffic Signaling (0.07%); T1124 System Time Discovery (0.03%) | 99.64% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.68%); T1003 OS Credential Dumping (0.21%); T1039 Data from Network Shared Drive (0.20%) | 98.68% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1016 System Network Configuration Discovery (67.63%); T1003 OS Credential Dumping (12.27%); T1518 Software Discovery (4.56%) | 0.40% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (16.47%); T1070 Indicator Removal (14.11%); T1566 Phishing (10.42%) | 0.03% | False |

## markov_25 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.52%); T1087 Account Discovery (0.03%); T1105 Ingress Tool Transfer (0.03%) | 99.52% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.30%); T1548 Abuse Elevation Control Mechanism (0.90%); T1557 Adversary-in-the-Middle (0.16%) | 98.30% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.63%); T1614 System Location Discovery (0.06%); T1136 Create Account (0.03%) | 99.63% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.09%); T1190 Exploit Public-Facing Application (0.46%); T1592 Gather Victim Host Information (0.07%) | 99.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (81.05%); T1059 Command and Scripting Interpreter (16.77%); T1547 Boot or Logon Autostart Execution (0.24%) | 81.05% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (72.53%); T1059 Command and Scripting Interpreter (27.20%); T1070 Indicator Removal (0.02%) | 72.53% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.47%); T1518 Software Discovery (0.06%); T1124 System Time Discovery (0.04%) | 99.47% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.59%); T1003 OS Credential Dumping (0.91%); T1039 Data from Network Shared Drive (0.34%) | 97.59% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (36.63%); T1574 Hijack Execution Flow (18.84%); T1021 Remote Services (12.33%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (48.23%); T1059 Command and Scripting Interpreter (13.60%); T1574 Hijack Execution Flow (13.41%) | 0.16% | False |

## markov_25 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (92.09%); T1115 Clipboard Data (6.65%); T1553 Subvert Trust Controls (0.13%) | 92.09% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.31%); T1548 Abuse Elevation Control Mechanism (0.30%); T1490 Inhibit System Recovery (0.05%) | 99.31% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.44%); T1057 Process Discovery (0.08%); T1610 Deploy Container (0.07%) | 99.44% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.11%); T1190 Exploit Public-Facing Application (0.47%); T1589 Gather Victim Identity Information (0.13%) | 99.11% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (93.56%); T1059 Command and Scripting Interpreter (4.91%); T1082 System Information Discovery (0.90%) | 93.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.32%); T1059 Command and Scripting Interpreter (0.43%); T1083 File and Directory Discovery (0.06%) | 99.32% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.43%); T1074 Data Staged (0.09%); T1485 Data Destruction (0.08%) | 99.43% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.21%); T1039 Data from Network Shared Drive (0.36%); T1033 System Owner/User Discovery (0.25%) | 98.21% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (27.54%); T1566 Phishing (27.45%); T1053 Scheduled Task/Job (8.62%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1590 Gather Victim Network Information (14.20%); T1614 System Location Discovery (13.27%); T1595 Active Scanning (7.16%) | 0.01% | False |

## markov_25 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.55%); T1201 Password Policy Discovery (2.01%); T1595 Active Scanning (0.03%) | 97.55% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (83.96%); T1548 Abuse Elevation Control Mechanism (15.11%); T1105 Ingress Tool Transfer (0.16%) | 83.96% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1543 Create or Modify System Process (0.01%); T1083 File and Directory Discovery (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (61.47%); T1190 Exploit Public-Facing Application (29.31%); T1592 Gather Victim Host Information (8.67%) | 61.47% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.85%); T1059 Command and Scripting Interpreter (0.79%); T1078 Valid Accounts (0.05%) | 98.85% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (74.74%); T1087 Account Discovery (24.95%); T1095 Non-Application Layer Protocol (0.03%) | 24.95% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.60%); T1036 Masquerading (0.06%); T1055 Process Injection (0.05%) | 99.60% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.30%); T1041 Exfiltration Over C2 Channel (0.07%); T1083 File and Directory Discovery (0.06%) | 99.30% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (45.81%); T1059 Command and Scripting Interpreter (32.78%); T1201 Password Policy Discovery (4.82%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (54.72%); T1564 Hide Artifacts (41.02%); T1018 Remote System Discovery (1.18%) | 0.01% | False |

## markov_25 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.74%); T1592 Gather Victim Host Information (0.04%); T1057 Process Discovery (0.03%) | 99.74% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (79.89%); T1548 Abuse Elevation Control Mechanism (18.34%); T1059 Command and Scripting Interpreter (0.27%) | 79.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.64%); T1614 System Location Discovery (0.04%); T1083 File and Directory Discovery (0.03%) | 99.64% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (62.85%); T1190 Exploit Public-Facing Application (35.76%); T1592 Gather Victim Host Information (0.79%) | 62.85% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.96%); T1059 Command and Scripting Interpreter (0.26%); T1615 Group Policy Discovery (0.14%) | 98.96% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (54.96%); T1059 Command and Scripting Interpreter (44.50%); T1574 Hijack Execution Flow (0.07%) | 54.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.68%); T1595 Active Scanning (0.03%); T1016 System Network Configuration Discovery (0.02%) | 99.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.98%); T1049 System Network Connections Discovery (0.49%); T1021 Remote Services (0.40%) | 97.98% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (39.67%); T1007 System Service Discovery (20.85%); T1057 Process Discovery (9.14%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (33.76%); T1219 Remote Access Tools (17.34%); T1564 Hide Artifacts (17.33%) | 0.41% | False |

## markov_25 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.74%); T1083 File and Directory Discovery (0.03%); T1556 Modify Authentication Process (0.03%) | 99.74% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (92.95%); T1548 Abuse Elevation Control Mechanism (5.60%); T1556 Modify Authentication Process (0.21%) | 92.95% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.74%); T1518 Software Discovery (0.07%); T1003 OS Credential Dumping (0.02%) | 99.74% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (52.30%); T1190 Exploit Public-Facing Application (43.62%); T1592 Gather Victim Host Information (3.37%) | 52.30% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (93.11%); T1059 Command and Scripting Interpreter (4.18%); T1033 System Owner/User Discovery (0.98%) | 93.11% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (82.23%); T1087 Account Discovery (17.46%); T1105 Ingress Tool Transfer (0.06%) | 17.46% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.59%); T1528 Steal Application Access Token (0.06%); T1531 Account Access Removal (0.03%) | 99.59% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.83%); T1021 Remote Services (0.24%); T1071 Application Layer Protocol (0.16%) | 98.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (82.07%); T1574 Hijack Execution Flow (3.42%); T1190 Exploit Public-Facing Application (2.13%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (78.30%); T1564 Hide Artifacts (15.46%); T1574 Hijack Execution Flow (1.05%) | 0.24% | False |

## markov_25 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.68%); T1489 Service Stop (0.04%); T1614 System Location Discovery (0.03%) | 99.68% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (92.14%); T1548 Abuse Elevation Control Mechanism (6.36%); T1059 Command and Scripting Interpreter (0.27%) | 92.14% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.81%); T1133 External Remote Services (0.06%); T1082 System Information Discovery (0.03%) | 99.81% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.09%); T1190 Exploit Public-Facing Application (17.95%); T1592 Gather Victim Host Information (0.42%) | 81.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.71%); T1059 Command and Scripting Interpreter (3.74%); T1105 Ingress Tool Transfer (0.17%) | 94.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (51.52%); T1087 Account Discovery (47.81%); T1082 System Information Discovery (0.14%) | 47.81% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.24%); T1518 Software Discovery (0.16%); T1124 System Time Discovery (0.12%) | 99.24% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.23%); T1204 User Execution (2.75%); T1574 Hijack Execution Flow (0.65%) | 94.23% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1190 Exploit Public-Facing Application (53.71%); T1595 Active Scanning (8.02%); T1589 Gather Victim Identity Information (3.01%) | 0.91% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (29.45%); T1105 Ingress Tool Transfer (15.59%); T1039 Data from Network Shared Drive (12.13%) | 3.19% | False |

## markov_25 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.64%); T1610 Deploy Container (0.05%); T1573 Encrypted Channel (0.02%) | 99.64% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.29%); T1548 Abuse Elevation Control Mechanism (5.54%); T1036 Masquerading (0.24%) | 93.29% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.77%); T1068 Exploitation for Privilege Escalation (0.02%); T1078 Valid Accounts (0.02%) | 99.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (47.09%); T1190 Exploit Public-Facing Application (46.32%); T1592 Gather Victim Host Information (3.57%) | 47.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.24%); T1059 Command and Scripting Interpreter (0.98%); T1105 Ingress Tool Transfer (0.24%) | 98.24% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.80%); T1087 Account Discovery (20.91%); T1486 Data Encrypted for Impact (0.08%) | 20.91% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.42%); T1016 System Network Configuration Discovery (0.21%); T1005 Data from Local System (0.05%) | 99.42% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.75%); T1021 Remote Services (0.21%); T1573 Encrypted Channel (0.15%) | 98.75% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1531 Account Access Removal (15.11%); T1003 OS Credential Dumping (11.73%); T1105 Ingress Tool Transfer (9.65%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (25.62%); T1033 System Owner/User Discovery (18.78%); T1120 Peripheral Device Discovery (8.18%) | 0.15% | False |

## markov_25 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1083 File and Directory Discovery (0.02%); T1021 Remote Services (0.02%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (83.98%); T1548 Abuse Elevation Control Mechanism (14.34%); T1078 Valid Accounts (0.40%) | 83.98% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.67%); T1072 Software Deployment Tools (0.05%); T1592 Gather Victim Host Information (0.04%) | 99.67% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (49.97%); T1595 Active Scanning (46.76%); T1592 Gather Victim Host Information (2.53%) | 46.76% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.32%); T1059 Command and Scripting Interpreter (0.19%); T1083 File and Directory Discovery (0.04%) | 99.32% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.75%); T1087 Account Discovery (20.95%); T1136 Create Account (0.03%) | 20.95% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.46%); T1614 System Location Discovery (0.18%); T1573 Encrypted Channel (0.09%) | 99.46% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.18%); T1021 Remote Services (0.44%); T1574 Hijack Execution Flow (0.30%) | 98.18% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1566 Phishing (55.06%); T1591 Gather Victim Org Information (9.36%); T1210 Exploitation of Remote Services (4.06%) | 0.29% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1592 Gather Victim Host Information (44.44%); T1595 Active Scanning (16.05%); T1564 Hide Artifacts (13.83%) | 0.01% | False |

## markov_25 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.85%); T1074 Data Staged (3.60%); T1176 Software Extensions (0.06%) | 95.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.38%); T1548 Abuse Elevation Control Mechanism (5.63%); T1547 Boot or Logon Autostart Execution (0.11%) | 93.38% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.63%); T1049 System Network Connections Discovery (0.05%); T1041 Exfiltration Over C2 Channel (0.03%) | 99.63% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (62.01%); T1190 Exploit Public-Facing Application (30.43%); T1592 Gather Victim Host Information (7.01%) | 62.01% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.46%); T1059 Command and Scripting Interpreter (0.58%); T1615 Group Policy Discovery (0.23%) | 98.46% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (61.04%); T1087 Account Discovery (37.98%); T1105 Ingress Tool Transfer (0.21%) | 37.98% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.47%); T1040 Network Sniffing (0.07%); T1557 Adversary-in-the-Middle (0.07%) | 99.47% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.66%); T1078 Valid Accounts (0.33%); T1049 System Network Connections Discovery (0.26%) | 97.66% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (81.48%); T1033 System Owner/User Discovery (6.72%); T1059 Command and Scripting Interpreter (3.85%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1071 Application Layer Protocol (26.90%); T1176 Software Extensions (17.67%); T1564 Hide Artifacts (11.46%) | 0.19% | False |

## markov_25 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1592 Gather Victim Host Information (0.06%); T1589 Gather Victim Identity Information (0.03%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.71%); T1548 Abuse Elevation Control Mechanism (0.88%); T1218 System Binary Proxy Execution (0.06%) | 98.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.56%); T1087 Account Discovery (0.08%); T1518 Software Discovery (0.04%) | 99.56% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (61.39%); T1190 Exploit Public-Facing Application (38.03%); T1592 Gather Victim Host Information (0.16%) | 61.39% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.14%); T1105 Ingress Tool Transfer (0.24%); T1564 Hide Artifacts (0.14%) | 99.14% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (69.65%); T1059 Command and Scripting Interpreter (29.91%); T1095 Non-Application Layer Protocol (0.10%) | 69.65% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.65%); T1014 Rootkit (0.64%); T1007 System Service Discovery (0.10%) | 98.65% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.37%); T1120 Peripheral Device Discovery (0.36%); T1547 Boot or Logon Autostart Execution (0.20%) | 98.37% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1485 Data Destruction (13.33%); T1016 System Network Configuration Discovery (12.08%); T1213 Data from Information Repositories (9.93%) | 1.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (27.38%); T1222 File and Directory Permissions Modification (11.38%); T1018 Remote System Discovery (7.75%) | 0.73% | False |

## markov_25 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.61%); T1589 Gather Victim Identity Information (0.08%); T1595 Active Scanning (0.05%) | 99.61% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (91.28%); T1548 Abuse Elevation Control Mechanism (6.92%); T1070 Indicator Removal (0.32%) | 91.28% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.72%); T1120 Peripheral Device Discovery (0.04%); T1614 System Location Discovery (0.04%) | 99.72% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (56.57%); T1190 Exploit Public-Facing Application (34.07%); T1592 Gather Victim Host Information (8.67%) | 56.57% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.97%); T1070 Indicator Removal (0.17%); T1564 Hide Artifacts (0.15%) | 98.97% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (67.30%); T1087 Account Discovery (32.26%); T1033 System Owner/User Discovery (0.07%) | 32.26% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.45%); T1080 Taint Shared Content (0.10%); T1120 Peripheral Device Discovery (0.05%) | 99.45% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.71%); T1041 Exfiltration Over C2 Channel (0.14%); T1574 Hijack Execution Flow (0.13%) | 98.71% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (38.15%); T1569 System Services (8.46%); T1553 Subvert Trust Controls (8.00%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (47.63%); T1087 Account Discovery (9.99%); T1059 Command and Scripting Interpreter (8.25%) | 0.09% | False |

## markov_25 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.57%); T1115 Clipboard Data (3.50%); T1543 Create or Modify System Process (0.12%) | 95.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (74.43%); T1548 Abuse Elevation Control Mechanism (24.75%); T1218 System Binary Proxy Execution (0.25%) | 74.43% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1190 Exploit Public-Facing Application (0.04%); T1007 System Service Discovery (0.04%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (57.50%); T1190 Exploit Public-Facing Application (41.46%); T1592 Gather Victim Host Information (0.56%) | 57.50% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.73%); T1218 System Binary Proxy Execution (0.05%); T1046 Network Service Scanning (0.03%) | 99.73% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (59.45%); T1087 Account Discovery (40.14%); T1053 Scheduled Task/Job (0.09%) | 40.14% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.64%); T1057 Process Discovery (0.07%); T1072 Software Deployment Tools (0.04%) | 99.64% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.95%); T1021 Remote Services (0.39%); T1041 Exfiltration Over C2 Channel (0.09%) | 98.95% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (86.74%); T1072 Software Deployment Tools (1.82%); T1040 Network Sniffing (1.26%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (59.96%); T1590 Gather Victim Network Information (21.58%); T1018 Remote System Discovery (5.62%) | 0.03% | False |

## markov_50 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.20%); T1201 Password Policy Discovery (2.38%); T1213 Data from Information Repositories (0.05%) | 97.20% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.63%); T1548 Abuse Elevation Control Mechanism (0.13%); T1036 Masquerading (0.10%) | 99.63% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.91%); T1033 System Owner/User Discovery (0.01%); T1018 Remote System Discovery (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (92.14%); T1592 Gather Victim Host Information (4.99%); T1190 Exploit Public-Facing Application (2.31%) | 92.14% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.40%); T1059 Command and Scripting Interpreter (1.11%); T1566 Phishing (0.10%) | 98.40% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (96.84%); T1059 Command and Scripting Interpreter (2.98%); T1082 System Information Discovery (0.05%) | 96.84% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.60%); T1543 Create or Modify System Process (0.05%); T1018 Remote System Discovery (0.04%) | 99.60% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.85%); T1039 Data from Network Shared Drive (0.35%); T1041 Exfiltration Over C2 Channel (0.17%) | 98.85% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1548 Abuse Elevation Control Mechanism (31.42%); T1082 System Information Discovery (21.33%); T1564 Hide Artifacts (17.21%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1548 Abuse Elevation Control Mechanism (27.40%); T1564 Hide Artifacts (17.24%); T1071 Application Layer Protocol (7.98%) | 0.02% | False |

## markov_50 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.73%); T1595 Active Scanning (0.05%); T1057 Process Discovery (0.03%) | 99.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.53%); T1105 Ingress Tool Transfer (0.10%); T1548 Abuse Elevation Control Mechanism (0.10%) | 99.53% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1615 Group Policy Discovery (0.03%); T1083 File and Directory Discovery (0.02%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (90.20%); T1592 Gather Victim Host Information (9.13%); T1190 Exploit Public-Facing Application (0.33%) | 90.20% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.29%); T1059 Command and Scripting Interpreter (0.39%); T1098 Account Manipulation (0.06%) | 99.29% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (70.56%); T1059 Command and Scripting Interpreter (29.02%); T1547 Boot or Logon Autostart Execution (0.05%) | 70.56% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1124 System Time Discovery (0.07%); T1486 Data Encrypted for Impact (0.03%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.65%); T1120 Peripheral Device Discovery (0.41%); T1039 Data from Network Shared Drive (0.40%) | 98.65% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (65.56%); T1059 Command and Scripting Interpreter (9.58%); T1518 Software Discovery (6.94%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1591 Gather Victim Org Information (39.01%); T1518 Software Discovery (10.97%); T1053 Scheduled Task/Job (8.08%) | 0.02% | False |

## markov_50 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.79%); T1218 System Binary Proxy Execution (0.02%); T1599 Network Boundary Bridging (0.02%) | 99.79% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.50%); T1548 Abuse Elevation Control Mechanism (0.22%); T1098 Account Manipulation (0.04%) | 99.50% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.78%); T1057 Process Discovery (0.04%); T1531 Account Access Removal (0.02%) | 99.78% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.71%); T1592 Gather Victim Host Information (3.08%); T1190 Exploit Public-Facing Application (0.75%) | 95.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.36%); T1059 Command and Scripting Interpreter (1.98%); T1071 Application Layer Protocol (0.18%) | 97.36% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.00%); T1059 Command and Scripting Interpreter (2.41%); T1033 System Owner/User Discovery (0.19%) | 97.00% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1124 System Time Discovery (0.04%); T1543 Create or Modify System Process (0.02%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.00%); T1120 Peripheral Device Discovery (0.19%); T1039 Data from Network Shared Drive (0.10%) | 99.00% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (30.61%); T1222 File and Directory Permissions Modification (21.86%); T1098 Account Manipulation (8.34%) | 0.18% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1098 Account Manipulation (36.39%); T1222 File and Directory Permissions Modification (17.28%); T1110 Brute Force (11.46%) | 0.06% | False |

## markov_50 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1040 Network Sniffing (0.02%); T1105 Ingress Tool Transfer (0.02%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.60%); T1548 Abuse Elevation Control Mechanism (0.14%); T1105 Ingress Tool Transfer (0.06%) | 99.60% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1176 Software Extensions (0.03%); T1133 External Remote Services (0.02%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (86.90%); T1190 Exploit Public-Facing Application (9.64%); T1592 Gather Victim Host Information (2.86%) | 86.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.56%); T1059 Command and Scripting Interpreter (1.27%); T1213 Data from Information Repositories (0.16%) | 97.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (93.87%); T1087 Account Discovery (6.00%); T1082 System Information Discovery (0.02%) | 6.00% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.68%); T1124 System Time Discovery (0.05%); T1190 Exploit Public-Facing Application (0.02%) | 99.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.38%); T1204 User Execution (1.96%); T1003 OS Credential Dumping (0.06%) | 97.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1531 Account Access Removal (31.28%); T1003 OS Credential Dumping (20.73%); T1078 Valid Accounts (10.18%) | 0.17% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (43.79%); T1489 Service Stop (13.71%); T1546 Event Triggered Execution (11.15%) | 0.01% | False |

## markov_50 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.08%); T1039 Data from Network Shared Drive (3.93%); T1205 Traffic Signaling (0.17%) | 95.08% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.56%); T1548 Abuse Elevation Control Mechanism (2.03%); T1078 Valid Accounts (0.24%) | 96.56% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1204 User Execution (0.05%); T1007 System Service Discovery (0.04%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.82%); T1592 Gather Victim Host Information (1.19%); T1190 Exploit Public-Facing Application (0.74%) | 97.82% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.29%); T1059 Command and Scripting Interpreter (1.22%); T1547 Boot or Logon Autostart Execution (0.09%) | 98.29% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.28%); T1059 Command and Scripting Interpreter (0.54%); T1083 File and Directory Discovery (0.03%) | 99.28% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.55%); T1124 System Time Discovery (0.09%); T1041 Exfiltration Over C2 Channel (0.03%) | 99.55% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.49%); T1039 Data from Network Shared Drive (0.22%); T1041 Exfiltration Over C2 Channel (0.03%) | 99.49% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (22.13%); T1105 Ingress Tool Transfer (21.17%); T1486 Data Encrypted for Impact (17.44%) | 0.25% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (36.00%); T1078 Valid Accounts (30.97%); T1105 Ingress Tool Transfer (7.00%) | 0.00% | False |

## markov_50 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.49%); T1083 File and Directory Discovery (0.06%); T1565 Data Manipulation (0.05%) | 99.49% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.55%); T1105 Ingress Tool Transfer (0.08%); T1548 Abuse Elevation Control Mechanism (0.06%) | 99.55% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.51%); T1485 Data Destruction (0.08%); T1133 External Remote Services (0.05%) | 99.51% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (91.88%); T1190 Exploit Public-Facing Application (6.67%); T1592 Gather Victim Host Information (0.85%) | 91.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.44%); T1059 Command and Scripting Interpreter (0.16%); T1033 System Owner/User Discovery (0.09%) | 99.44% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.49%); T1105 Ingress Tool Transfer (0.18%); T1059 Command and Scripting Interpreter (0.10%) | 99.49% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.75%); T1070 Indicator Removal (0.05%); T1059 Command and Scripting Interpreter (0.02%) | 99.75% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.03%); T1071 Application Layer Protocol (0.43%); T1059 Command and Scripting Interpreter (0.23%) | 98.03% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1083 File and Directory Discovery (20.49%); T1490 Inhibit System Recovery (13.88%); T1531 Account Access Removal (9.28%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1490 Inhibit System Recovery (15.58%); T1083 File and Directory Discovery (10.35%); T1222 File and Directory Permissions Modification (9.63%) | 0.10% | False |

## markov_50 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (93.29%); T1074 Data Staged (6.10%); T1589 Gather Victim Identity Information (0.05%) | 93.29% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.30%); T1548 Abuse Elevation Control Mechanism (0.48%); T1005 Data from Local System (0.04%) | 99.30% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.53%); T1222 File and Directory Permissions Modification (0.06%); T1574 Hijack Execution Flow (0.04%) | 99.53% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (83.47%); T1592 Gather Victim Host Information (15.16%); T1190 Exploit Public-Facing Application (0.78%) | 83.47% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.27%); T1059 Command and Scripting Interpreter (0.98%); T1083 File and Directory Discovery (0.18%) | 98.27% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.38%); T1059 Command and Scripting Interpreter (0.17%); T1083 File and Directory Discovery (0.10%) | 99.38% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1547 Boot or Logon Autostart Execution (0.17%); T1124 System Time Discovery (0.03%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.34%); T1039 Data from Network Shared Drive (1.12%); T1120 Peripheral Device Discovery (0.19%) | 97.34% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (77.20%); T1059 Command and Scripting Interpreter (6.00%); T1547 Boot or Logon Autostart Execution (2.14%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (19.24%); T1547 Boot or Logon Autostart Execution (17.77%); T1564 Hide Artifacts (11.80%) | 0.08% | False |

## markov_50 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.61%); T1589 Gather Victim Identity Information (0.08%); T1059 Command and Scripting Interpreter (0.04%) | 99.61% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.13%); T1548 Abuse Elevation Control Mechanism (0.50%); T1105 Ingress Tool Transfer (0.11%) | 99.13% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.72%); T1082 System Information Discovery (0.03%); T1055 Process Injection (0.03%) | 99.72% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.84%); T1190 Exploit Public-Facing Application (0.05%); T1589 Gather Victim Identity Information (0.01%) | 99.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.27%); T1059 Command and Scripting Interpreter (1.22%); T1547 Boot or Logon Autostart Execution (0.07%) | 98.27% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (80.27%); T1059 Command and Scripting Interpreter (19.37%); T1083 File and Directory Discovery (0.05%) | 80.27% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.51%); T1489 Service Stop (0.05%); T1071 Application Layer Protocol (0.04%) | 99.51% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.31%); T1021 Remote Services (0.10%); T1039 Data from Network Shared Drive (0.10%) | 99.31% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1098 Account Manipulation (45.33%); T1564 Hide Artifacts (12.23%); T1040 Network Sniffing (10.52%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (65.22%); T1098 Account Manipulation (4.94%); T1222 File and Directory Permissions Modification (4.80%) | 0.00% | False |

## markov_50 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.73%); T1095 Non-Application Layer Protocol (0.04%); T1595 Active Scanning (0.02%) | 99.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.53%); T1557 Adversary-in-the-Middle (0.10%); T1548 Abuse Elevation Control Mechanism (0.09%) | 99.53% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1033 System Owner/User Discovery (0.01%); T1201 Password Policy Discovery (0.01%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (82.85%); T1190 Exploit Public-Facing Application (15.06%); T1592 Gather Victim Host Information (1.62%) | 82.85% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.64%); T1059 Command and Scripting Interpreter (0.81%); T1095 Non-Application Layer Protocol (0.26%) | 97.64% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (82.26%); T1059 Command and Scripting Interpreter (16.85%); T1105 Ingress Tool Transfer (0.57%) | 82.26% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1105 Ingress Tool Transfer (0.04%); T1219 Remote Access Tools (0.01%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.67%); T1564 Hide Artifacts (0.28%); T1039 Data from Network Shared Drive (0.23%) | 98.67% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (81.13%); T1069 Permission Groups Discovery (4.79%); T1204 User Execution (2.54%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1566 Phishing (23.37%); T1069 Permission Groups Discovery (15.12%); T1222 File and Directory Permissions Modification (13.00%) | 0.01% | False |

## markov_50 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (93.20%); T1115 Clipboard Data (6.33%); T1018 Remote System Discovery (0.10%) | 93.20% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.19%); T1548 Abuse Elevation Control Mechanism (1.14%); T1105 Ingress Tool Transfer (0.29%) | 98.19% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1057 Process Discovery (0.03%); T1080 Taint Shared Content (0.03%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.81%); T1190 Exploit Public-Facing Application (3.63%); T1589 Gather Victim Identity Information (0.10%) | 95.81% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.78%); T1518 Software Discovery (0.04%); T1105 Ingress Tool Transfer (0.02%) | 99.78% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (71.01%); T1059 Command and Scripting Interpreter (28.66%); T1082 System Information Discovery (0.05%) | 71.01% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.83%); T1486 Data Encrypted for Impact (0.04%); T1003 OS Credential Dumping (0.01%) | 99.83% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.96%); T1599 Network Boundary Bridging (0.38%); T1049 System Network Connections Discovery (0.28%) | 97.96% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1553 Subvert Trust Controls (22.51%); T1071 Application Layer Protocol (18.03%); T1548 Abuse Elevation Control Mechanism (7.40%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (52.52%); T1553 Subvert Trust Controls (9.53%); T1057 Process Discovery (6.89%) | 0.00% | False |

## markov_50 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.73%); T1201 Password Policy Discovery (3.57%); T1074 Data Staged (0.09%) | 95.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.39%); T1548 Abuse Elevation Control Mechanism (1.10%); T1036 Masquerading (0.23%) | 98.39% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1518 Software Discovery (0.01%); T1033 System Owner/User Discovery (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (89.42%); T1592 Gather Victim Host Information (6.70%); T1190 Exploit Public-Facing Application (3.46%) | 89.42% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.12%); T1055 Process Injection (0.09%); T1547 Boot or Logon Autostart Execution (0.08%) | 99.12% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (96.70%); T1059 Command and Scripting Interpreter (3.08%); T1082 System Information Discovery (0.03%) | 96.70% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.70%); T1124 System Time Discovery (0.16%); T1610 Deploy Container (0.01%) | 99.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.15%); T1039 Data from Network Shared Drive (0.32%); T1041 Exfiltration Over C2 Channel (0.23%) | 98.15% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (54.29%); T1566 Phishing (7.08%); T1033 System Owner/User Discovery (6.91%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (44.17%); T1614 System Location Discovery (25.97%); T1564 Hide Artifacts (9.75%) | 0.16% | False |

## markov_50 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.66%); T1573 Encrypted Channel (0.06%); T1595 Active Scanning (0.05%) | 99.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.70%); T1059 Command and Scripting Interpreter (0.06%); T1036 Masquerading (0.06%) | 99.70% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1201 Password Policy Discovery (0.03%); T1083 File and Directory Discovery (0.02%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (90.99%); T1592 Gather Victim Host Information (8.23%); T1190 Exploit Public-Facing Application (0.50%) | 90.99% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.63%); T1497 Virtualization/Sandbox Evasion (0.06%); T1595 Active Scanning (0.05%) | 99.63% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.46%); T1059 Command and Scripting Interpreter (2.21%); T1543 Create or Modify System Process (0.10%) | 97.46% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.78%); T1124 System Time Discovery (0.08%); T1546 Event Triggered Execution (0.03%) | 99.78% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.98%); T1039 Data from Network Shared Drive (0.62%); T1083 File and Directory Discovery (0.27%) | 97.98% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1068 Exploitation for Privilege Escalation (77.74%); T1564 Hide Artifacts (7.64%); T1072 Software Deployment Tools (2.14%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (31.06%); T1566 Phishing (22.72%); T1614 System Location Discovery (6.58%) | 0.01% | False |

## markov_50 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.63%); T1556 Modify Authentication Process (0.07%); T1071 Application Layer Protocol (0.05%) | 99.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.68%); T1548 Abuse Elevation Control Mechanism (0.08%); T1053 Scheduled Task/Job (0.03%) | 99.68% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.78%); T1057 Process Discovery (0.03%); T1071 Application Layer Protocol (0.02%) | 99.78% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (89.55%); T1190 Exploit Public-Facing Application (5.20%); T1592 Gather Victim Host Information (4.48%) | 89.55% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.08%); T1059 Command and Scripting Interpreter (1.14%); T1053 Scheduled Task/Job (0.13%) | 98.08% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.12%); T1059 Command and Scripting Interpreter (2.08%); T1083 File and Directory Discovery (0.18%) | 97.12% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.66%); T1124 System Time Discovery (0.04%); T1610 Deploy Container (0.03%) | 99.66% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.77%); T1039 Data from Network Shared Drive (0.20%); T1614 System Location Discovery (0.14%) | 98.77% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (18.32%); T1105 Ingress Tool Transfer (12.76%); T1036 Masquerading (8.95%) | 1.13% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (44.25%); T1222 File and Directory Permissions Modification (29.83%); T1557 Adversary-in-the-Middle (3.78%) | 0.13% | False |

## markov_50 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.63%); T1105 Ingress Tool Transfer (0.10%); T1531 Account Access Removal (0.02%) | 99.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.44%); T1548 Abuse Elevation Control Mechanism (0.27%); T1218 System Binary Proxy Execution (0.09%) | 99.44% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.98%); T1133 External Remote Services (3.44%); T1021 Remote Services (0.12%) | 95.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (80.26%); T1190 Exploit Public-Facing Application (14.01%); T1592 Gather Victim Host Information (4.97%) | 80.26% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.09%); T1547 Boot or Logon Autostart Execution (0.13%); T1078 Valid Accounts (0.11%) | 99.09% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.81%); T1059 Command and Scripting Interpreter (12.96%); T1105 Ingress Tool Transfer (0.05%) | 86.81% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.59%); T1033 System Owner/User Discovery (0.07%); T1124 System Time Discovery (0.03%) | 99.59% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.07%); T1039 Data from Network Shared Drive (0.14%); T1105 Ingress Tool Transfer (0.13%) | 99.07% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1531 Account Access Removal (62.87%); T1070 Indicator Removal (7.57%); T1056 Input Capture (3.33%) | 3.33% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1036 Masquerading (21.61%); T1039 Data from Network Shared Drive (17.75%); T1105 Ingress Tool Transfer (7.48%) | 0.15% | False |

## markov_50 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (93.52%); T1039 Data from Network Shared Drive (5.22%); T1595 Active Scanning (0.14%) | 93.52% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.76%); T1548 Abuse Elevation Control Mechanism (0.71%); T1205 Traffic Signaling (0.17%) | 98.76% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.76%); T1057 Process Discovery (0.02%); T1039 Data from Network Shared Drive (0.02%) | 99.76% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.46%); T1592 Gather Victim Host Information (1.18%); T1190 Exploit Public-Facing Application (0.18%) | 98.46% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.74%); T1059 Command and Scripting Interpreter (0.65%); T1547 Boot or Logon Autostart Execution (0.11%) | 98.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (92.33%); T1059 Command and Scripting Interpreter (7.41%); T1574 Hijack Execution Flow (0.06%) | 92.33% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.23%); T1005 Data from Local System (0.16%); T1016 System Network Configuration Discovery (0.06%) | 99.23% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.79%); T1083 File and Directory Discovery (0.24%); T1039 Data from Network Shared Drive (0.22%) | 98.79% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (32.31%); T1546 Event Triggered Execution (17.24%); T1222 File and Directory Permissions Modification (11.40%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1546 Event Triggered Execution (11.41%); T1105 Ingress Tool Transfer (10.74%); T1486 Data Encrypted for Impact (10.00%) | 0.00% | False |

## markov_50 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.61%); T1083 File and Directory Discovery (0.08%); T1610 Deploy Container (0.04%) | 99.61% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.61%); T1548 Abuse Elevation Control Mechanism (1.31%); T1190 Exploit Public-Facing Application (0.30%) | 97.61% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.89%); T1133 External Remote Services (0.24%); T1003 OS Credential Dumping (0.12%) | 98.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (93.86%); T1190 Exploit Public-Facing Application (5.20%); T1592 Gather Victim Host Information (0.36%) | 93.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.27%); T1059 Command and Scripting Interpreter (0.74%); T1547 Boot or Logon Autostart Execution (0.16%) | 98.27% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.55%); T1105 Ingress Tool Transfer (0.58%); T1059 Command and Scripting Interpreter (0.34%) | 98.55% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.57%); T1573 Encrypted Channel (0.11%); T1124 System Time Discovery (0.04%) | 99.57% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.82%); T1039 Data from Network Shared Drive (0.28%); T1120 Peripheral Device Discovery (0.10%) | 98.82% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1610 Deploy Container (36.49%); T1564 Hide Artifacts (17.67%); T1049 System Network Connections Discovery (9.63%) | 0.77% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1213 Data from Information Repositories (31.55%); T1573 Encrypted Channel (10.61%); T1565 Data Manipulation (6.62%) | 0.81% | False |

## markov_50 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.29%); T1074 Data Staged (3.95%); T1557 Adversary-in-the-Middle (0.09%) | 95.29% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.02%); T1548 Abuse Elevation Control Mechanism (1.47%); T1005 Data from Local System (0.43%) | 97.02% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.91%); T1201 Password Policy Discovery (0.17%); T1222 File and Directory Permissions Modification (0.16%) | 98.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.16%); T1592 Gather Victim Host Information (17.47%); T1190 Exploit Public-Facing Application (0.89%) | 81.16% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.06%); T1059 Command and Scripting Interpreter (2.08%); T1573 Encrypted Channel (0.13%) | 97.06% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.34%); T1059 Command and Scripting Interpreter (0.16%); T1033 System Owner/User Discovery (0.09%) | 99.34% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.60%); T1547 Boot or Logon Autostart Execution (0.11%); T1018 Remote System Discovery (0.04%) | 99.60% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.84%); T1039 Data from Network Shared Drive (0.36%); T1591 Gather Victim Org Information (0.11%) | 98.84% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1018 Remote System Discovery (30.22%); T1615 Group Policy Discovery (15.13%); T1033 System Owner/User Discovery (14.37%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1615 Group Policy Discovery (14.54%); T1018 Remote System Discovery (9.49%); T1049 System Network Connections Discovery (9.04%) | 0.14% | False |

## markov_50 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.63%); T1589 Gather Victim Identity Information (0.04%); T1201 Password Policy Discovery (0.04%) | 99.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.40%); T1548 Abuse Elevation Control Mechanism (2.71%); T1218 System Binary Proxy Execution (0.14%) | 96.40% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.57%); T1053 Scheduled Task/Job (0.08%); T1531 Account Access Removal (0.04%) | 99.57% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.73%); T1190 Exploit Public-Facing Application (0.10%); T1219 Remote Access Tools (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.26%); T1566 Phishing (0.29%); T1059 Command and Scripting Interpreter (0.09%) | 99.26% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.78%); T1083 File and Directory Discovery (0.04%); T1059 Command and Scripting Interpreter (0.03%) | 99.78% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.53%); T1205 Traffic Signaling (0.09%); T1124 System Time Discovery (0.04%) | 99.53% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.74%); T1003 OS Credential Dumping (0.29%); T1039 Data from Network Shared Drive (0.26%) | 98.74% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (65.93%); T1222 File and Directory Permissions Modification (15.74%); T1219 Remote Access Tools (3.53%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (55.29%); T1082 System Information Discovery (17.89%); T1071 Application Layer Protocol (3.18%) | 0.01% | False |

## markov_50 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.73%); T1068 Exploitation for Privilege Escalation (0.03%); T1599 Network Boundary Bridging (0.02%) | 99.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.60%); T1548 Abuse Elevation Control Mechanism (0.47%); T1557 Adversary-in-the-Middle (0.19%) | 98.60% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.77%); T1222 File and Directory Permissions Modification (0.04%); T1136 Create Account (0.02%) | 99.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (73.09%); T1190 Exploit Public-Facing Application (25.23%); T1592 Gather Victim Host Information (1.28%) | 73.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.78%); T1059 Command and Scripting Interpreter (0.91%); T1087 Account Discovery (0.22%) | 97.78% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (76.69%); T1087 Account Discovery (22.18%); T1105 Ingress Tool Transfer (0.77%) | 22.18% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.58%); T1014 Rootkit (0.15%); T1124 System Time Discovery (0.04%) | 99.58% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.66%); T1003 OS Credential Dumping (0.27%); T1039 Data from Network Shared Drive (0.22%) | 98.66% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (35.64%); T1041 Exfiltration Over C2 Channel (13.61%); T1082 System Information Discovery (10.35%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (66.32%); T1033 System Owner/User Discovery (12.00%); T1574 Hijack Execution Flow (11.62%) | 0.00% | False |

## markov_50 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (93.30%); T1115 Clipboard Data (6.02%); T1553 Subvert Trust Controls (0.07%) | 93.30% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.14%); T1548 Abuse Elevation Control Mechanism (0.37%); T1105 Ingress Tool Transfer (0.11%) | 99.14% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.64%); T1057 Process Discovery (0.06%); T1018 Remote System Discovery (0.04%) | 99.64% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (92.50%); T1190 Exploit Public-Facing Application (6.73%); T1592 Gather Victim Host Information (0.19%) | 92.50% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.38%); T1059 Command and Scripting Interpreter (2.81%); T1082 System Information Discovery (0.34%) | 96.38% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.65%); T1059 Command and Scripting Interpreter (0.09%); T1083 File and Directory Discovery (0.08%) | 99.65% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.71%); T1124 System Time Discovery (0.05%); T1566 Phishing (0.03%) | 99.71% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.40%); T1033 System Owner/User Discovery (0.30%); T1003 OS Credential Dumping (0.30%) | 98.40% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1219 Remote Access Tools (51.16%); T1098 Account Manipulation (10.19%); T1005 Data from Local System (6.86%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1219 Remote Access Tools (32.72%); T1547 Boot or Logon Autostart Execution (11.08%); T1528 Steal Application Access Token (9.86%) | 0.02% | False |

## markov_50 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.40%); T1201 Password Policy Discovery (2.19%); T1595 Active Scanning (0.04%) | 97.40% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.24%); T1548 Abuse Elevation Control Mechanism (3.30%); T1546 Event Triggered Execution (0.09%) | 96.24% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1083 File and Directory Discovery (0.01%); T1039 Data from Network Shared Drive (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (52.15%); T1190 Exploit Public-Facing Application (37.43%); T1592 Gather Victim Host Information (10.02%) | 52.15% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.70%); T1082 System Information Discovery (0.06%); T1059 Command and Scripting Interpreter (0.04%) | 99.70% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (89.75%); T1087 Account Discovery (10.09%); T1105 Ingress Tool Transfer (0.08%) | 10.09% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.90%); T1615 Group Policy Discovery (0.02%); T1201 Password Policy Discovery (0.01%) | 99.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.94%); T1074 Data Staged (0.14%); T1531 Account Access Removal (0.11%) | 98.94% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (72.65%); T1059 Command and Scripting Interpreter (17.06%); T1041 Exfiltration Over C2 Channel (2.72%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (64.07%); T1222 File and Directory Permissions Modification (33.11%); T1071 Application Layer Protocol (0.66%) | 0.02% | False |

## markov_50 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1595 Active Scanning (0.04%); T1592 Gather Victim Host Information (0.02%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.24%); T1548 Abuse Elevation Control Mechanism (4.29%); T1059 Command and Scripting Interpreter (1.27%) | 93.24% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.64%); T1083 File and Directory Discovery (0.12%); T1003 OS Credential Dumping (0.03%) | 99.64% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (47.76%); T1190 Exploit Public-Facing Application (35.83%); T1592 Gather Victim Host Information (15.99%) | 47.76% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.14%); T1059 Command and Scripting Interpreter (0.52%); T1069 Permission Groups Discovery (0.06%) | 99.14% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (65.36%); T1087 Account Discovery (34.19%); T1105 Ingress Tool Transfer (0.19%) | 34.19% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.88%); T1556 Modify Authentication Process (0.01%); T1595 Active Scanning (0.01%) | 99.88% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.33%); T1053 Scheduled Task/Job (0.10%); T1531 Account Access Removal (0.06%) | 99.33% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (42.65%); T1490 Inhibit System Recovery (9.66%); T1018 Remote System Discovery (8.64%) | 0.15% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1518 Software Discovery (51.15%); T1059 Command and Scripting Interpreter (19.32%); T1222 File and Directory Permissions Modification (3.92%) | 0.05% | False |

## markov_50 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.84%); T1219 Remote Access Tools (0.03%); T1071 Application Layer Protocol (0.01%) | 99.84% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (72.33%); T1548 Abuse Elevation Control Mechanism (25.63%); T1105 Ingress Tool Transfer (0.37%) | 72.33% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1003 OS Credential Dumping (0.01%); T1518 Software Discovery (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (59.77%); T1190 Exploit Public-Facing Application (34.96%); T1592 Gather Victim Host Information (3.35%) | 59.77% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.77%); T1059 Command and Scripting Interpreter (3.51%); T1105 Ingress Tool Transfer (0.12%) | 95.77% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.11%); T1087 Account Discovery (20.48%); T1105 Ingress Tool Transfer (1.16%) | 20.48% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.70%); T1528 Steal Application Access Token (0.04%); T1083 File and Directory Discovery (0.03%) | 99.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.77%); T1021 Remote Services (0.17%); T1083 File and Directory Discovery (0.13%) | 98.77% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (48.14%); T1222 File and Directory Permissions Modification (7.88%); T1213 Data from Information Repositories (7.08%) | 0.32% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (50.24%); T1222 File and Directory Permissions Modification (26.34%); T1201 Password Policy Discovery (7.06%) | 0.32% | False |

## markov_50 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1614 System Location Discovery (0.04%); T1489 Service Stop (0.03%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.01%); T1548 Abuse Elevation Control Mechanism (2.58%); T1059 Command and Scripting Interpreter (0.07%) | 97.01% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.69%); T1133 External Remote Services (0.15%); T1082 System Information Discovery (0.02%) | 99.69% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (55.68%); T1190 Exploit Public-Facing Application (35.27%); T1592 Gather Victim Host Information (8.36%) | 55.68% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.32%); T1059 Command and Scripting Interpreter (3.66%); T1547 Boot or Logon Autostart Execution (0.12%) | 95.32% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (87.54%); T1087 Account Discovery (12.01%); T1105 Ingress Tool Transfer (0.21%) | 12.01% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.39%); T1124 System Time Discovery (0.19%); T1518 Software Discovery (0.07%) | 99.39% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.55%); T1204 User Execution (1.96%); T1574 Hijack Execution Flow (0.28%) | 96.55% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1531 Account Access Removal (31.90%); T1190 Exploit Public-Facing Application (17.16%); T1595 Active Scanning (14.29%) | 1.31% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (24.07%); T1039 Data from Network Shared Drive (23.12%); T1222 File and Directory Permissions Modification (22.03%) | 0.67% | False |

## markov_50 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.36%); T1039 Data from Network Shared Drive (4.04%); T1083 File and Directory Discovery (0.08%) | 95.36% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (89.53%); T1548 Abuse Elevation Control Mechanism (9.67%); T1105 Ingress Tool Transfer (0.18%) | 89.53% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.71%); T1083 File and Directory Discovery (0.07%); T1210 Exploitation of Remote Services (0.06%) | 99.71% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (49.51%); T1190 Exploit Public-Facing Application (40.32%); T1592 Gather Victim Host Information (7.42%) | 49.51% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.95%); T1059 Command and Scripting Interpreter (0.30%); T1105 Ingress Tool Transfer (0.26%) | 98.95% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (70.87%); T1087 Account Discovery (28.89%); T1105 Ingress Tool Transfer (0.05%) | 28.89% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.42%); T1005 Data from Local System (0.17%); T1016 System Network Configuration Discovery (0.10%) | 99.42% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.38%); T1573 Encrypted Channel (0.10%); T1021 Remote Services (0.09%) | 99.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (20.04%); T1003 OS Credential Dumping (15.56%); T1572 Protocol Tunneling (11.45%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (28.47%); T1070 Indicator Removal (19.13%); T1033 System Owner/User Discovery (10.37%) | 0.06% | False |

## markov_50 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1547 Boot or Logon Autostart Execution (0.03%); T1115 Clipboard Data (0.02%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (88.11%); T1548 Abuse Elevation Control Mechanism (10.28%); T1105 Ingress Tool Transfer (0.32%) | 88.11% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.42%); T1133 External Remote Services (0.17%); T1072 Software Deployment Tools (0.11%) | 99.42% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (55.69%); T1190 Exploit Public-Facing Application (39.48%); T1592 Gather Victim Host Information (4.20%) | 55.69% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.70%); T1059 Command and Scripting Interpreter (0.84%); T1087 Account Discovery (0.05%) | 98.70% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (59.95%); T1087 Account Discovery (39.52%); T1105 Ingress Tool Transfer (0.17%) | 39.52% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.72%); T1543 Create or Modify System Process (0.05%); T1614 System Location Discovery (0.03%) | 99.72% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.14%); T1036 Masquerading (0.13%); T1021 Remote Services (0.10%) | 99.14% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1046 Network Service Scanning (26.67%); T1056 Input Capture (11.69%); T1573 Encrypted Channel (9.75%) | 11.69% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (53.45%); T1592 Gather Victim Host Information (17.93%); T1595 Active Scanning (4.50%) | 0.02% | False |

## markov_50 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.39%); T1074 Data Staged (4.26%); T1176 Software Extensions (0.05%) | 95.39% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (82.01%); T1548 Abuse Elevation Control Mechanism (16.60%); T1078 Valid Accounts (0.23%) | 82.01% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.80%); T1201 Password Policy Discovery (0.02%); T1021 Remote Services (0.01%) | 99.80% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (46.00%); T1595 Active Scanning (44.99%); T1592 Gather Victim Host Information (8.48%) | 44.99% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.24%); T1059 Command and Scripting Interpreter (1.70%); T1615 Group Policy Discovery (0.17%) | 97.24% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (74.79%); T1087 Account Discovery (22.77%); T1105 Ingress Tool Transfer (2.05%) | 22.77% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.69%); T1557 Adversary-in-the-Middle (0.09%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.86%); T1592 Gather Victim Host Information (0.10%); T1078 Valid Accounts (0.10%) | 98.86% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (41.34%); T1059 Command and Scripting Interpreter (18.77%); T1033 System Owner/User Discovery (10.37%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (39.49%); T1071 Application Layer Protocol (11.68%); T1564 Hide Artifacts (8.68%) | 0.52% | False |

## markov_50 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1592 Gather Victim Host Information (0.02%); T1589 Gather Victim Identity Information (0.02%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.15%); T1548 Abuse Elevation Control Mechanism (2.66%); T1105 Ingress Tool Transfer (0.65%) | 96.15% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.49%); T1082 System Information Discovery (0.12%); T1590 Gather Victim Network Information (0.05%) | 99.49% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (58.39%); T1190 Exploit Public-Facing Application (41.06%); T1110 Brute Force (0.12%) | 58.39% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.10%); T1564 Hide Artifacts (0.26%); T1059 Command and Scripting Interpreter (0.21%) | 99.10% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (77.89%); T1059 Command and Scripting Interpreter (21.45%); T1095 Non-Application Layer Protocol (0.21%) | 77.89% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.08%); T1014 Rootkit (0.26%); T1190 Exploit Public-Facing Application (0.13%) | 99.08% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.65%); T1553 Subvert Trust Controls (0.12%); T1016 System Network Configuration Discovery (0.07%) | 99.65% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1046 Network Service Scanning (22.56%); T1564 Hide Artifacts (11.91%); T1485 Data Destruction (8.12%) | 0.39% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (23.75%); T1046 Network Service Scanning (18.52%); T1222 File and Directory Permissions Modification (17.18%) | 0.10% | False |

## markov_50 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1589 Gather Victim Identity Information (0.04%); T1018 Remote System Discovery (0.03%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (57.35%); T1548 Abuse Elevation Control Mechanism (37.74%); T1550 Use Alternate Authentication Material (1.28%) | 57.35% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1557 Adversary-in-the-Middle (0.03%); T1120 Peripheral Device Discovery (0.03%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (59.28%); T1190 Exploit Public-Facing Application (35.55%); T1592 Gather Victim Host Information (4.62%) | 59.28% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.28%); T1070 Indicator Removal (0.08%); T1560 Archive Collected Data (0.07%) | 99.28% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (84.31%); T1087 Account Discovery (15.32%); T1033 System Owner/User Discovery (0.17%) | 15.32% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.56%); T1080 Taint Shared Content (0.08%); T1120 Peripheral Device Discovery (0.06%) | 99.56% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.03%); T1041 Exfiltration Over C2 Channel (0.13%); T1569 System Services (0.09%) | 99.03% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (47.13%); T1005 Data from Local System (9.94%); T1057 Process Discovery (3.56%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (92.53%); T1564 Hide Artifacts (1.78%); T1525 Implant Internal Image (0.86%) | 0.02% | False |

## markov_50 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.18%); T1115 Clipboard Data (3.13%); T1553 Subvert Trust Controls (0.11%) | 96.18% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (91.71%); T1548 Abuse Elevation Control Mechanism (7.06%); T1105 Ingress Tool Transfer (0.29%) | 91.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1557 Adversary-in-the-Middle (0.03%); T1057 Process Discovery (0.01%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (57.85%); T1190 Exploit Public-Facing Application (41.26%); T1592 Gather Victim Host Information (0.46%) | 57.85% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.18%); T1068 Exploitation for Privilege Escalation (0.17%); T1059 Command and Scripting Interpreter (0.14%) | 99.18% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (54.99%); T1087 Account Discovery (44.58%); T1574 Hijack Execution Flow (0.08%) | 44.58% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.70%); T1057 Process Discovery (0.08%); T1083 File and Directory Discovery (0.04%) | 99.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.30%); T1021 Remote Services (0.10%); T1041 Exfiltration Over C2 Channel (0.09%) | 99.30% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1055 Process Injection (65.59%); T1003 OS Credential Dumping (15.24%); T1046 Network Service Scanning (3.34%) | 0.23% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1590 Gather Victim Network Information (25.53%); T1547 Boot or Logon Autostart Execution (23.07%); T1564 Hide Artifacts (11.97%) | 0.04% | False |

## real_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.66%); T1213 Data from Information Repositories (0.04%); T1589 Gather Victim Identity Information (0.02%) | 99.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.28%); T1036 Masquerading (0.29%); T1548 Abuse Elevation Control Mechanism (0.22%) | 99.28% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.67%); T1490 Inhibit System Recovery (0.05%); T1018 Remote System Discovery (0.04%) | 99.67% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.49%); T1190 Exploit Public-Facing Application (0.31%); T1589 Gather Victim Identity Information (0.03%) | 99.49% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.11%); T1059 Command and Scripting Interpreter (0.17%); T1566 Phishing (0.12%) | 99.11% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.67%); T1105 Ingress Tool Transfer (0.03%); T1546 Event Triggered Execution (0.02%) | 99.67% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.40%); T1124 System Time Discovery (0.08%); T1201 Password Policy Discovery (0.08%) | 99.40% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.48%); T1039 Data from Network Shared Drive (0.18%); T1591 Gather Victim Org Information (0.12%) | 98.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (50.16%); T1222 File and Directory Permissions Modification (10.97%); T1595 Active Scanning (7.13%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (52.62%); T1071 Application Layer Protocol (12.35%); T1070 Indicator Removal (9.98%) | 0.01% | False |

## real_100 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.52%); T1003 OS Credential Dumping (0.06%); T1595 Active Scanning (0.05%) | 99.52% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.91%); T1548 Abuse Elevation Control Mechanism (1.93%); T1105 Ingress Tool Transfer (0.18%) | 96.91% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.61%); T1057 Process Discovery (0.03%); T1136 Create Account (0.03%) | 99.61% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.45%); T1190 Exploit Public-Facing Application (0.21%); T1589 Gather Victim Identity Information (0.06%) | 99.45% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.25%); T1059 Command and Scripting Interpreter (1.61%); T1083 File and Directory Discovery (0.14%) | 97.25% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.73%); T1059 Command and Scripting Interpreter (0.75%); T1591 Gather Victim Org Information (0.05%) | 98.73% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.30%); T1124 System Time Discovery (0.17%); T1072 Software Deployment Tools (0.09%) | 99.30% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.58%); T1039 Data from Network Shared Drive (0.36%); T1120 Peripheral Device Discovery (0.35%) | 98.58% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (67.32%); T1591 Gather Victim Org Information (16.34%); T1566 Phishing (1.50%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (42.55%); T1218 System Binary Proxy Execution (9.33%); T1204 User Execution (7.81%) | 4.64% | False |

## real_100 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.59%); T1218 System Binary Proxy Execution (0.06%); T1036 Masquerading (0.02%) | 99.59% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.43%); T1548 Abuse Elevation Control Mechanism (1.68%); T1082 System Information Discovery (0.25%) | 97.43% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.60%); T1057 Process Discovery (0.10%); T1219 Remote Access Tools (0.04%) | 99.60% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.66%); T1190 Exploit Public-Facing Application (0.10%); T1589 Gather Victim Identity Information (0.06%) | 99.66% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.85%); T1059 Command and Scripting Interpreter (0.40%); T1071 Application Layer Protocol (0.07%) | 98.85% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (50.59%); T1059 Command and Scripting Interpreter (48.77%); T1083 File and Directory Discovery (0.06%) | 50.59% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.36%); T1018 Remote System Discovery (0.08%); T1124 System Time Discovery (0.04%) | 99.36% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.90%); T1039 Data from Network Shared Drive (0.14%); T1201 Password Policy Discovery (0.10%) | 98.90% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (58.23%); T1222 File and Directory Permissions Modification (24.89%); T1033 System Owner/User Discovery (3.36%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (55.04%); T1070 Indicator Removal (20.06%); T1222 File and Directory Permissions Modification (13.67%) | 0.07% | False |

## real_100 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.63%); T1007 System Service Discovery (0.03%); T1078 Valid Accounts (0.02%) | 99.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.20%); T1548 Abuse Elevation Control Mechanism (0.30%); T1105 Ingress Tool Transfer (0.13%) | 99.20% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.67%); T1003 OS Credential Dumping (0.04%); T1080 Taint Shared Content (0.03%) | 99.67% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.54%); T1190 Exploit Public-Facing Application (0.15%); T1589 Gather Victim Identity Information (0.11%) | 99.54% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.04%); T1059 Command and Scripting Interpreter (1.36%); T1547 Boot or Logon Autostart Execution (0.24%) | 97.04% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (77.06%); T1059 Command and Scripting Interpreter (22.07%); T1082 System Information Discovery (0.30%) | 77.06% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.44%); T1124 System Time Discovery (0.14%); T1485 Data Destruction (0.02%) | 99.44% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.46%); T1039 Data from Network Shared Drive (0.26%); T1120 Peripheral Device Discovery (0.23%) | 98.46% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (34.62%); T1564 Hide Artifacts (7.53%); T1003 OS Credential Dumping (7.28%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (34.17%); T1033 System Owner/User Discovery (8.11%); T1564 Hide Artifacts (7.66%) | 0.02% | False |

## real_100 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.63%); T1205 Traffic Signaling (0.04%); T1595 Active Scanning (0.03%) | 99.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.56%); T1548 Abuse Elevation Control Mechanism (0.16%); T1082 System Information Discovery (0.06%) | 99.56% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.56%); T1057 Process Discovery (0.09%); T1201 Password Policy Discovery (0.07%) | 99.56% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.61%); T1190 Exploit Public-Facing Application (0.14%); T1589 Gather Victim Identity Information (0.07%) | 99.61% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (90.50%); T1059 Command and Scripting Interpreter (8.54%); T1105 Ingress Tool Transfer (0.13%) | 90.50% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.58%); T1059 Command and Scripting Interpreter (1.87%); T1083 File and Directory Discovery (0.14%) | 97.58% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.36%); T1124 System Time Discovery (0.09%); T1098 Account Manipulation (0.04%) | 99.36% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.45%); T1083 File and Directory Discovery (0.17%); T1039 Data from Network Shared Drive (0.14%) | 98.45% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (74.33%); T1486 Data Encrypted for Impact (4.16%); T1071 Application Layer Protocol (3.26%) | 0.15% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1041 Exfiltration Over C2 Channel (23.43%); T1003 OS Credential Dumping (13.49%); T1078 Valid Accounts (11.18%) | 0.00% | False |

## real_100 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.58%); T1083 File and Directory Discovery (0.06%); T1531 Account Access Removal (0.03%) | 99.58% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.25%); T1548 Abuse Elevation Control Mechanism (0.29%); T1083 File and Directory Discovery (0.07%) | 99.25% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.45%); T1219 Remote Access Tools (0.05%); T1201 Password Policy Discovery (0.05%) | 99.45% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.70%); T1589 Gather Victim Identity Information (0.10%); T1190 Exploit Public-Facing Application (0.05%) | 99.70% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.08%); T1059 Command and Scripting Interpreter (1.88%); T1547 Boot or Logon Autostart Execution (0.14%) | 97.08% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.55%); T1486 Data Encrypted for Impact (0.04%); T1531 Account Access Removal (0.04%) | 99.55% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.39%); T1072 Software Deployment Tools (0.13%); T1059 Command and Scripting Interpreter (0.06%) | 99.39% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.42%); T1039 Data from Network Shared Drive (0.46%); T1573 Encrypted Channel (0.12%) | 98.42% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1083 File and Directory Discovery (15.25%); T1222 File and Directory Permissions Modification (12.34%); T1564 Hide Artifacts (8.85%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1083 File and Directory Discovery (18.86%); T1105 Ingress Tool Transfer (10.03%); T1016 System Network Configuration Discovery (8.43%) | 0.02% | False |

## real_100 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.66%); T1589 Gather Victim Identity Information (0.06%); T1110 Brute Force (0.03%) | 99.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.38%); T1548 Abuse Elevation Control Mechanism (0.32%); T1566 Phishing (0.06%) | 99.38% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.41%); T1528 Steal Application Access Token (0.06%); T1218 System Binary Proxy Execution (0.04%) | 99.41% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.65%); T1190 Exploit Public-Facing Application (0.09%); T1589 Gather Victim Identity Information (0.04%) | 99.65% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.11%); T1059 Command and Scripting Interpreter (0.97%); T1547 Boot or Logon Autostart Execution (0.10%) | 98.11% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.38%); T1083 File and Directory Discovery (0.14%); T1548 Abuse Elevation Control Mechanism (0.06%) | 99.38% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.57%); T1124 System Time Discovery (0.05%); T1040 Network Sniffing (0.03%) | 99.57% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.14%); T1039 Data from Network Shared Drive (0.53%); T1120 Peripheral Device Discovery (0.46%) | 98.14% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (69.87%); T1053 Scheduled Task/Job (7.52%); T1105 Ingress Tool Transfer (6.15%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (78.72%); T1595 Active Scanning (4.40%); T1557 Adversary-in-the-Middle (2.64%) | 0.00% | False |

## real_100 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.53%); T1059 Command and Scripting Interpreter (0.04%); T1007 System Service Discovery (0.03%) | 99.53% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.69%); T1548 Abuse Elevation Control Mechanism (0.11%); T1105 Ingress Tool Transfer (0.07%) | 99.69% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.62%); T1003 OS Credential Dumping (0.04%); T1053 Scheduled Task/Job (0.03%) | 99.62% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.56%); T1190 Exploit Public-Facing Application (0.23%); T1589 Gather Victim Identity Information (0.06%) | 99.56% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.74%); T1059 Command and Scripting Interpreter (0.47%); T1033 System Owner/User Discovery (0.09%) | 98.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.37%); T1059 Command and Scripting Interpreter (0.22%); T1222 File and Directory Permissions Modification (0.05%) | 99.37% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.33%); T1059 Command and Scripting Interpreter (0.12%); T1566 Phishing (0.10%) | 99.33% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.19%); T1039 Data from Network Shared Drive (0.23%); T1003 OS Credential Dumping (0.16%) | 98.19% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (51.59%); T1497 Virtualization/Sandbox Evasion (10.06%); T1222 File and Directory Permissions Modification (8.34%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (61.99%); T1222 File and Directory Permissions Modification (13.23%); T1566 Phishing (4.21%) | 0.04% | False |

## real_100 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.51%); T1595 Active Scanning (0.04%); T1497 Virtualization/Sandbox Evasion (0.04%) | 99.51% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.35%); T1548 Abuse Elevation Control Mechanism (0.17%); T1105 Ingress Tool Transfer (0.10%) | 99.35% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.62%); T1033 System Owner/User Discovery (0.04%); T1201 Password Policy Discovery (0.03%) | 99.62% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.55%); T1589 Gather Victim Identity Information (0.11%); T1190 Exploit Public-Facing Application (0.10%) | 99.55% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.92%); T1059 Command and Scripting Interpreter (0.67%); T1547 Boot or Logon Autostart Execution (0.24%) | 97.92% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (91.84%); T1059 Command and Scripting Interpreter (6.99%); T1033 System Owner/User Discovery (0.24%) | 91.84% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.32%); T1110 Brute Force (0.08%); T1124 System Time Discovery (0.07%) | 99.32% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.20%); T1039 Data from Network Shared Drive (0.58%); T1003 OS Credential Dumping (0.15%) | 98.20% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (13.45%); T1033 System Owner/User Discovery (12.21%); T1204 User Execution (11.04%) | 0.23% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (40.68%); T1078 Valid Accounts (7.43%); T1566 Phishing (5.20%) | 0.01% | False |

## real_100 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.64%); T1018 Remote System Discovery (0.02%); T1564 Hide Artifacts (0.02%) | 99.64% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.03%); T1548 Abuse Elevation Control Mechanism (0.62%); T1036 Masquerading (0.59%) | 98.03% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.38%); T1003 OS Credential Dumping (0.09%); T1057 Process Discovery (0.09%) | 99.38% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.43%); T1190 Exploit Public-Facing Application (0.28%); T1589 Gather Victim Identity Information (0.08%) | 99.43% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.61%); T1059 Command and Scripting Interpreter (0.62%); T1556 Modify Authentication Process (0.05%) | 98.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.58%); T1003 OS Credential Dumping (0.06%); T1059 Command and Scripting Interpreter (0.05%) | 99.58% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.41%); T1560 Archive Collected Data (0.06%); T1124 System Time Discovery (0.03%) | 99.41% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.34%); T1039 Data from Network Shared Drive (0.25%); T1049 System Network Connections Discovery (0.19%) | 98.34% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (17.36%); T1564 Hide Artifacts (13.09%); T1222 File and Directory Permissions Modification (11.68%) | 0.35% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (85.09%); T1218 System Binary Proxy Execution (2.70%); T1591 Gather Victim Org Information (1.47%) | 0.00% | False |

## real_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.37%); T1595 Active Scanning (0.11%); T1074 Data Staged (0.04%) | 99.37% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.13%); T1548 Abuse Elevation Control Mechanism (1.38%); T1036 Masquerading (0.94%) | 97.13% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.52%); T1518 Software Discovery (0.07%); T1543 Create or Modify System Process (0.05%) | 99.52% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.60%); T1190 Exploit Public-Facing Application (0.17%); T1589 Gather Victim Identity Information (0.03%) | 99.60% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.89%); T1059 Command and Scripting Interpreter (1.10%); T1005 Data from Local System (0.07%) | 97.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.90%); T1059 Command and Scripting Interpreter (3.61%); T1599 Network Boundary Bridging (0.04%) | 95.90% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.51%); T1124 System Time Discovery (0.06%); T1210 Exploitation of Remote Services (0.04%) | 99.51% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.18%); T1039 Data from Network Shared Drive (0.64%); T1078 Valid Accounts (0.34%) | 97.18% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (72.45%); T1222 File and Directory Permissions Modification (7.02%); T1105 Ingress Tool Transfer (3.91%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (26.85%); T1614 System Location Discovery (10.52%); T1222 File and Directory Permissions Modification (9.91%) | 0.05% | False |

## real_100 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.34%); T1595 Active Scanning (0.07%); T1040 Network Sniffing (0.06%) | 99.34% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.39%); T1548 Abuse Elevation Control Mechanism (0.66%); T1036 Masquerading (0.20%) | 98.39% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.59%); T1083 File and Directory Discovery (0.03%); T1204 User Execution (0.03%) | 99.59% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.64%); T1190 Exploit Public-Facing Application (0.10%); T1589 Gather Victim Identity Information (0.07%) | 99.64% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.57%); T1059 Command and Scripting Interpreter (5.68%); T1190 Exploit Public-Facing Application (0.17%) | 92.57% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.39%); T1059 Command and Scripting Interpreter (0.16%); T1095 Non-Application Layer Protocol (0.04%) | 99.39% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.50%); T1124 System Time Discovery (0.08%); T1485 Data Destruction (0.03%) | 99.50% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.83%); T1082 System Information Discovery (0.35%); T1564 Hide Artifacts (0.29%) | 97.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (22.91%); T1078 Valid Accounts (22.82%); T1082 System Information Discovery (15.94%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (82.78%); T1033 System Owner/User Discovery (5.76%); T1548 Abuse Elevation Control Mechanism (3.27%) | 0.04% | False |

## real_100 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.39%); T1010 Application Window Discovery (0.06%); T1219 Remote Access Tools (0.05%) | 99.39% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.52%); T1548 Abuse Elevation Control Mechanism (0.18%); T1136 Create Account (0.04%) | 99.52% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.45%); T1057 Process Discovery (0.11%); T1204 User Execution (0.04%) | 99.45% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.52%); T1190 Exploit Public-Facing Application (0.11%); T1589 Gather Victim Identity Information (0.06%) | 99.52% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.97%); T1059 Command and Scripting Interpreter (0.93%); T1201 Password Policy Discovery (0.12%) | 97.97% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (92.22%); T1059 Command and Scripting Interpreter (7.18%); T1204 User Execution (0.06%) | 92.22% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.37%); T1124 System Time Discovery (0.07%); T1574 Hijack Execution Flow (0.05%) | 99.37% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.80%); T1120 Peripheral Device Discovery (0.26%); T1041 Exfiltration Over C2 Channel (0.23%) | 97.80% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (57.67%); T1222 File and Directory Permissions Modification (11.49%); T1003 OS Credential Dumping (5.46%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (41.85%); T1053 Scheduled Task/Job (38.86%); T1222 File and Directory Permissions Modification (7.69%) | 0.03% | False |

## real_100 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.45%); T1110 Brute Force (0.05%); T1071 Application Layer Protocol (0.05%) | 99.45% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.28%); T1548 Abuse Elevation Control Mechanism (0.30%); T1105 Ingress Tool Transfer (0.08%) | 99.28% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.42%); T1057 Process Discovery (0.10%); T1201 Password Policy Discovery (0.06%) | 99.42% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.92%); T1190 Exploit Public-Facing Application (0.33%); T1589 Gather Victim Identity Information (0.18%) | 98.92% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.34%); T1059 Command and Scripting Interpreter (0.67%); T1547 Boot or Logon Autostart Execution (0.12%) | 98.34% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.49%); T1201 Password Policy Discovery (0.09%); T1059 Command and Scripting Interpreter (0.08%) | 99.49% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.34%); T1124 System Time Discovery (0.10%); T1041 Exfiltration Over C2 Channel (0.05%) | 99.34% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.34%); T1003 OS Credential Dumping (0.38%); T1039 Data from Network Shared Drive (0.28%) | 98.34% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (39.80%); T1039 Data from Network Shared Drive (29.38%); T1531 Account Access Removal (4.03%) | 0.11% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (85.78%); T1039 Data from Network Shared Drive (2.43%); T1083 File and Directory Discovery (2.04%) | 0.04% | False |

## real_100 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.40%); T1021 Remote Services (0.06%); T1595 Active Scanning (0.04%) | 99.40% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.72%); T1548 Abuse Elevation Control Mechanism (1.41%); T1036 Masquerading (0.17%) | 97.72% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.57%); T1057 Process Discovery (0.05%); T1068 Exploitation for Privilege Escalation (0.02%) | 99.57% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.63%); T1589 Gather Victim Identity Information (0.10%); T1190 Exploit Public-Facing Application (0.05%) | 99.63% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (91.73%); T1059 Command and Scripting Interpreter (6.98%); T1105 Ingress Tool Transfer (0.14%) | 91.73% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.34%); T1059 Command and Scripting Interpreter (0.25%); T1040 Network Sniffing (0.05%) | 99.34% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.35%); T1124 System Time Discovery (0.08%); T1016 System Network Configuration Discovery (0.07%) | 99.35% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.27%); T1039 Data from Network Shared Drive (0.50%); T1070 Indicator Removal (0.21%) | 98.27% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (69.98%); T1120 Peripheral Device Discovery (5.10%); T1222 File and Directory Permissions Modification (4.09%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (79.85%); T1486 Data Encrypted for Impact (5.52%); T1546 Event Triggered Execution (2.25%) | 0.01% | False |

## real_100 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.53%); T1083 File and Directory Discovery (0.05%); T1569 System Services (0.04%) | 99.53% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.35%); T1548 Abuse Elevation Control Mechanism (0.81%); T1566 Phishing (0.21%) | 98.35% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.50%); T1219 Remote Access Tools (0.05%); T1485 Data Destruction (0.05%) | 99.50% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.21%); T1589 Gather Victim Identity Information (0.26%); T1190 Exploit Public-Facing Application (0.23%) | 99.21% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.89%); T1059 Command and Scripting Interpreter (1.67%); T1190 Exploit Public-Facing Application (0.17%) | 96.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.68%); T1059 Command and Scripting Interpreter (0.04%); T1007 System Service Discovery (0.02%) | 99.68% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.46%); T1136 Create Account (0.06%); T1573 Encrypted Channel (0.05%) | 99.46% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.58%); T1039 Data from Network Shared Drive (0.31%); T1573 Encrypted Channel (0.21%) | 98.58% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (18.73%); T1053 Scheduled Task/Job (16.00%); T1036 Masquerading (13.27%) | 0.44% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1566 Phishing (19.19%); T1564 Hide Artifacts (18.07%); T1565 Data Manipulation (15.57%) | 0.59% | False |

## real_100 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.31%); T1110 Brute Force (0.09%); T1213 Data from Information Repositories (0.06%) | 99.31% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.53%); T1548 Abuse Elevation Control Mechanism (0.61%); T1070 Indicator Removal (0.25%) | 97.53% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.43%); T1033 System Owner/User Discovery (0.06%); T1105 Ingress Tool Transfer (0.04%) | 99.43% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.34%); T1190 Exploit Public-Facing Application (0.28%); T1589 Gather Victim Identity Information (0.11%) | 99.34% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.43%); T1059 Command and Scripting Interpreter (0.47%); T1039 Data from Network Shared Drive (0.07%) | 98.43% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.98%); T1059 Command and Scripting Interpreter (0.74%); T1565 Data Manipulation (0.03%) | 98.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.42%); T1218 System Binary Proxy Execution (0.08%); T1124 System Time Discovery (0.06%) | 99.42% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.13%); T1039 Data from Network Shared Drive (0.57%); T1120 Peripheral Device Discovery (0.11%) | 98.13% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (27.80%); T1204 User Execution (9.66%); T1018 Remote System Discovery (8.60%) | 0.22% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (30.60%); T1110 Brute Force (7.91%); T1105 Ingress Tool Transfer (5.79%) | 0.03% | False |

## real_100 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.50%); T1592 Gather Victim Host Information (0.08%); T1557 Adversary-in-the-Middle (0.05%) | 99.50% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.45%); T1548 Abuse Elevation Control Mechanism (0.22%); T1218 System Binary Proxy Execution (0.10%) | 99.45% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.57%); T1053 Scheduled Task/Job (0.06%); T1190 Exploit Public-Facing Application (0.03%) | 99.57% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.53%); T1190 Exploit Public-Facing Application (0.18%); T1589 Gather Victim Identity Information (0.12%) | 99.53% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.30%); T1547 Boot or Logon Autostart Execution (0.11%); T1068 Exploitation for Privilege Escalation (0.04%) | 99.30% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.66%); T1068 Exploitation for Privilege Escalation (0.04%); T1083 File and Directory Discovery (0.02%) | 99.66% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.57%); T1490 Inhibit System Recovery (0.03%); T1124 System Time Discovery (0.02%) | 99.57% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.20%); T1039 Data from Network Shared Drive (0.37%); T1003 OS Credential Dumping (0.28%) | 98.20% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (59.53%); T1071 Application Layer Protocol (14.25%); T1204 User Execution (5.61%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1070 Indicator Removal (27.46%); T1082 System Information Discovery (20.29%); T1003 OS Credential Dumping (17.98%) | 0.00% | False |

## real_100 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.48%); T1557 Adversary-in-the-Middle (0.07%); T1573 Encrypted Channel (0.04%) | 99.48% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.06%); T1548 Abuse Elevation Control Mechanism (0.44%); T1518 Software Discovery (0.11%) | 99.06% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.60%); T1136 Create Account (0.04%); T1201 Password Policy Discovery (0.03%) | 99.60% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.56%); T1589 Gather Victim Identity Information (0.13%); T1190 Exploit Public-Facing Application (0.09%) | 99.56% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.95%); T1059 Command and Scripting Interpreter (0.24%); T1547 Boot or Logon Autostart Execution (0.11%) | 98.95% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.77%); T1059 Command and Scripting Interpreter (0.04%); T1591 Gather Victim Org Information (0.02%) | 99.77% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.42%); T1518 Software Discovery (0.11%); T1033 System Owner/User Discovery (0.04%) | 99.42% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.94%); T1039 Data from Network Shared Drive (0.24%); T1003 OS Credential Dumping (0.09%) | 98.94% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1546 Event Triggered Execution (20.89%); T1041 Exfiltration Over C2 Channel (20.02%); T1003 OS Credential Dumping (14.90%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (75.52%); T1574 Hijack Execution Flow (5.75%); T1041 Exfiltration Over C2 Channel (5.73%) | 0.01% | False |

## real_100 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.43%); T1005 Data from Local System (0.07%); T1595 Active Scanning (0.05%) | 99.43% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.60%); T1548 Abuse Elevation Control Mechanism (0.43%); T1219 Remote Access Tools (0.31%) | 98.60% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.49%); T1057 Process Discovery (0.06%); T1018 Remote System Discovery (0.05%) | 99.49% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.50%); T1589 Gather Victim Identity Information (0.11%); T1190 Exploit Public-Facing Application (0.10%) | 99.50% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.02%); T1059 Command and Scripting Interpreter (4.92%); T1105 Ingress Tool Transfer (0.15%) | 94.02% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.54%); T1033 System Owner/User Discovery (0.09%); T1486 Data Encrypted for Impact (0.08%) | 99.54% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.54%); T1548 Abuse Elevation Control Mechanism (0.07%); T1485 Data Destruction (0.06%) | 99.54% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.11%); T1039 Data from Network Shared Drive (0.09%); T1070 Indicator Removal (0.09%) | 99.11% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (30.68%); T1574 Hijack Execution Flow (11.17%); T1010 Application Window Discovery (7.57%) | 0.24% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (19.69%); T1049 System Network Connections Discovery (9.65%); T1574 Hijack Execution Flow (9.00%) | 0.12% | False |

## real_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.65%); T1592 Gather Victim Host Information (0.02%); T1528 Steal Application Access Token (0.02%) | 99.65% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (60.07%); T1548 Abuse Elevation Control Mechanism (38.24%); T1078 Valid Accounts (0.28%) | 60.07% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.66%); T1039 Data from Network Shared Drive (0.04%); T1083 File and Directory Discovery (0.03%) | 99.66% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (56.61%); T1190 Exploit Public-Facing Application (42.65%); T1083 File and Directory Discovery (0.08%) | 56.61% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.98%); T1082 System Information Discovery (0.10%); T1078 Valid Accounts (0.08%) | 98.98% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (82.49%); T1087 Account Discovery (17.23%); T1082 System Information Discovery (0.03%) | 17.23% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.26%); T1614 System Location Discovery (0.06%); T1072 Software Deployment Tools (0.05%) | 99.26% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.13%); T1041 Exfiltration Over C2 Channel (0.36%); T1039 Data from Network Shared Drive (0.27%) | 98.13% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (63.40%); T1059 Command and Scripting Interpreter (24.99%); T1082 System Information Discovery (6.12%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (35.73%); T1564 Hide Artifacts (30.99%); T1574 Hijack Execution Flow (14.03%) | 0.14% | False |

## real_100 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.47%); T1592 Gather Victim Host Information (0.08%); T1222 File and Directory Permissions Modification (0.05%) | 99.47% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.11%); T1548 Abuse Elevation Control Mechanism (2.22%); T1036 Masquerading (0.12%) | 97.11% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.56%); T1083 File and Directory Discovery (0.09%); T1021 Remote Services (0.03%) | 99.56% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (63.42%); T1595 Active Scanning (35.64%); T1059 Command and Scripting Interpreter (0.20%) | 35.64% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.43%); T1059 Command and Scripting Interpreter (0.55%); T1136 Create Account (0.09%) | 98.43% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (86.25%); T1087 Account Discovery (13.33%); T1053 Scheduled Task/Job (0.07%) | 13.33% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.51%); T1036 Masquerading (0.05%); T1016 System Network Configuration Discovery (0.04%) | 99.51% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.39%); T1049 System Network Connections Discovery (0.29%); T1120 Peripheral Device Discovery (0.13%) | 98.39% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (31.46%); T1105 Ingress Tool Transfer (22.55%); T1021 Remote Services (14.46%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (23.19%); T1564 Hide Artifacts (17.77%); T1059 Command and Scripting Interpreter (11.82%) | 0.09% | False |

## real_100 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.48%); T1071 Application Layer Protocol (0.14%); T1595 Active Scanning (0.03%) | 99.48% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (94.04%); T1548 Abuse Elevation Control Mechanism (4.55%); T1059 Command and Scripting Interpreter (0.32%) | 94.04% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.67%); T1124 System Time Discovery (0.03%); T1036 Masquerading (0.02%) | 99.67% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (50.40%); T1595 Active Scanning (48.74%); T1059 Command and Scripting Interpreter (0.07%) | 48.74% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.07%); T1059 Command and Scripting Interpreter (0.19%); T1078 Valid Accounts (0.12%) | 99.07% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (66.15%); T1087 Account Discovery (33.29%); T1120 Peripheral Device Discovery (0.08%) | 33.29% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.90%); T1204 User Execution (0.41%); T1566 Phishing (0.20%) | 97.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.19%); T1049 System Network Connections Discovery (0.25%); T1021 Remote Services (0.21%) | 98.19% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (46.13%); T1222 File and Directory Permissions Modification (19.12%); T1033 System Owner/User Discovery (6.29%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (55.62%); T1564 Hide Artifacts (17.20%); T1070 Indicator Removal (14.76%) | 0.14% | False |

## real_100 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.60%); T1218 System Binary Proxy Execution (0.03%); T1615 Group Policy Discovery (0.03%) | 99.60% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (81.71%); T1548 Abuse Elevation Control Mechanism (14.13%); T1105 Ingress Tool Transfer (2.16%) | 81.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.71%); T1083 File and Directory Discovery (0.05%); T1003 OS Credential Dumping (0.03%) | 99.71% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (51.04%); T1595 Active Scanning (48.14%); T1589 Gather Victim Identity Information (0.11%) | 48.14% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.69%); T1059 Command and Scripting Interpreter (3.05%); T1547 Boot or Logon Autostart Execution (0.18%) | 95.69% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (70.12%); T1087 Account Discovery (29.33%); T1095 Non-Application Layer Protocol (0.07%) | 29.33% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.30%); T1518 Software Discovery (0.09%); T1525 Implant Internal Image (0.08%) | 99.30% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.11%); T1049 System Network Connections Discovery (0.44%); T1133 External Remote Services (0.33%) | 97.11% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (10.77%); T1589 Gather Victim Identity Information (8.75%); T1218 System Binary Proxy Execution (7.34%) | 0.18% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (15.71%); T1016 System Network Configuration Discovery (10.04%); T1218 System Binary Proxy Execution (7.84%) | 2.05% | False |

## real_100 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1592 Gather Victim Host Information (0.03%); T1595 Active Scanning (0.02%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.39%); T1548 Abuse Elevation Control Mechanism (2.22%); T1105 Ingress Tool Transfer (0.45%) | 96.39% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.62%); T1068 Exploitation for Privilege Escalation (0.10%); T1518 Software Discovery (0.02%) | 99.62% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (80.87%); T1190 Exploit Public-Facing Application (18.51%); T1589 Gather Victim Identity Information (0.18%) | 80.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.18%); T1105 Ingress Tool Transfer (0.24%); T1218 System Binary Proxy Execution (0.18%) | 99.18% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (62.57%); T1087 Account Discovery (36.92%); T1053 Scheduled Task/Job (0.06%) | 36.92% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.43%); T1016 System Network Configuration Discovery (0.65%); T1083 File and Directory Discovery (0.15%) | 98.43% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.89%); T1049 System Network Connections Discovery (0.42%); T1021 Remote Services (0.18%) | 97.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (54.84%); T1078 Valid Accounts (9.80%); T1033 System Owner/User Discovery (4.37%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (36.99%); T1564 Hide Artifacts (15.83%); T1105 Ingress Tool Transfer (12.27%) | 0.30% | False |

## real_100 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.67%); T1021 Remote Services (0.03%); T1033 System Owner/User Discovery (0.02%) | 99.67% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (87.76%); T1548 Abuse Elevation Control Mechanism (10.47%); T1105 Ingress Tool Transfer (0.70%) | 87.76% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.58%); T1016 System Network Configuration Discovery (0.06%); T1614 System Location Discovery (0.03%) | 99.58% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (73.86%); T1190 Exploit Public-Facing Application (25.14%); T1592 Gather Victim Host Information (0.30%) | 73.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.52%); T1059 Command and Scripting Interpreter (0.73%); T1041 Exfiltration Over C2 Channel (0.06%) | 98.52% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (77.12%); T1087 Account Discovery (22.51%); T1095 Non-Application Layer Protocol (0.08%) | 22.51% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.49%); T1070 Indicator Removal (0.08%); T1614 System Location Discovery (0.06%) | 99.49% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.84%); T1574 Hijack Execution Flow (0.39%); T1053 Scheduled Task/Job (0.25%) | 97.84% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1087 Account Discovery (16.00%); T1573 Encrypted Channel (14.30%); T1591 Gather Victim Org Information (5.79%) | 1.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (56.47%); T1592 Gather Victim Host Information (7.44%); T1222 File and Directory Permissions Modification (6.97%) | 0.03% | False |

## real_100 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1610 Deploy Container (0.02%); T1040 Network Sniffing (0.01%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.87%); T1548 Abuse Elevation Control Mechanism (2.59%); T1059 Command and Scripting Interpreter (0.45%) | 95.87% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.64%); T1115 Clipboard Data (0.03%); T1049 System Network Connections Discovery (0.02%) | 99.64% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (55.08%); T1595 Active Scanning (44.19%); T1053 Scheduled Task/Job (0.09%) | 44.19% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.52%); T1059 Command and Scripting Interpreter (1.02%); T1105 Ingress Tool Transfer (0.19%) | 97.52% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (60.52%); T1087 Account Discovery (39.03%); T1095 Non-Application Layer Protocol (0.05%) | 39.03% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.68%); T1120 Peripheral Device Discovery (0.03%); T1557 Adversary-in-the-Middle (0.02%) | 99.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.37%); T1201 Password Policy Discovery (0.23%); T1569 System Services (0.12%) | 98.37% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (73.70%); T1071 Application Layer Protocol (7.71%); T1219 Remote Access Tools (6.69%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (55.16%); T1071 Application Layer Protocol (25.28%); T1219 Remote Access Tools (4.65%) | 0.11% | False |

## real_100 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.62%); T1592 Gather Victim Host Information (0.10%); T1573 Encrypted Channel (0.02%) | 99.62% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.50%); T1548 Abuse Elevation Control Mechanism (0.94%); T1059 Command and Scripting Interpreter (0.52%) | 97.50% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.57%); T1518 Software Discovery (0.04%); T1087 Account Discovery (0.04%) | 99.57% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (57.90%); T1190 Exploit Public-Facing Application (41.38%); T1589 Gather Victim Identity Information (0.11%) | 57.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.04%); T1564 Hide Artifacts (0.10%); T1105 Ingress Tool Transfer (0.09%) | 99.04% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (57.47%); T1059 Command and Scripting Interpreter (41.98%); T1095 Non-Application Layer Protocol (0.06%) | 57.47% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.38%); T1547 Boot or Logon Autostart Execution (0.06%); T1049 System Network Connections Discovery (0.05%) | 99.38% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.12%); T1120 Peripheral Device Discovery (0.15%); T1041 Exfiltration Over C2 Channel (0.14%) | 99.12% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1485 Data Destruction (31.86%); T1005 Data from Local System (10.17%); T1531 Account Access Removal (6.95%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (55.01%); T1219 Remote Access Tools (12.48%); T1222 File and Directory Permissions Modification (5.67%) | 0.51% | False |

## real_100 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.57%); T1018 Remote System Discovery (0.04%); T1095 Non-Application Layer Protocol (0.04%) | 99.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (80.38%); T1548 Abuse Elevation Control Mechanism (17.07%); T1078 Valid Accounts (0.48%) | 80.38% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.52%); T1033 System Owner/User Discovery (0.12%); T1614 System Location Discovery (0.03%) | 99.52% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (57.67%); T1190 Exploit Public-Facing Application (40.81%); T1592 Gather Victim Host Information (0.36%) | 57.67% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.38%); T1059 Command and Scripting Interpreter (0.30%); T1547 Boot or Logon Autostart Execution (0.21%) | 98.38% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (60.72%); T1059 Command and Scripting Interpreter (37.99%); T1033 System Owner/User Discovery (0.19%) | 60.72% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.32%); T1518 Software Discovery (0.13%); T1120 Peripheral Device Discovery (0.05%) | 99.32% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.72%); T1041 Exfiltration Over C2 Channel (0.23%); T1133 External Remote Services (0.10%) | 98.72% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (91.67%); T1098 Account Manipulation (2.14%); T1136 Create Account (1.35%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (26.48%); T1564 Hide Artifacts (15.27%); T1556 Modify Authentication Process (10.58%) | 0.70% | False |

## real_100 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.59%); T1543 Create or Modify System Process (0.06%); T1595 Active Scanning (0.05%) | 99.59% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.31%); T1548 Abuse Elevation Control Mechanism (2.06%); T1105 Ingress Tool Transfer (0.10%) | 97.31% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1557 Adversary-in-the-Middle (0.03%); T1057 Process Discovery (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (59.26%); T1190 Exploit Public-Facing Application (39.77%); T1592 Gather Victim Host Information (0.21%) | 59.26% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.43%); T1059 Command and Scripting Interpreter (0.73%); T1614 System Location Discovery (0.11%) | 98.43% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (65.84%); T1059 Command and Scripting Interpreter (33.37%); T1082 System Information Discovery (0.11%) | 65.84% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.34%); T1072 Software Deployment Tools (0.10%); T1057 Process Discovery (0.06%) | 99.34% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.03%); T1041 Exfiltration Over C2 Channel (0.22%); T1049 System Network Connections Discovery (0.11%) | 99.03% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (66.91%); T1485 Data Destruction (3.67%); T1213 Data from Information Repositories (3.30%) | 0.33% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (82.68%); T1018 Remote System Discovery (6.33%); T1528 Steal Application Access Token (1.10%) | 0.01% | False |

## real_25 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.99%); T1589 Gather Victim Identity Information (0.32%); T1213 Data from Information Repositories (0.19%) | 96.99% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (60.68%); T1033 System Owner/User Discovery (7.00%); T1057 Process Discovery (5.73%) | 7.00% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (96.41%); T1053 Scheduled Task/Job (0.47%); T1018 Remote System Discovery (0.36%) | 96.41% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.38%); T1190 Exploit Public-Facing Application (3.68%); T1592 Gather Victim Host Information (0.18%) | 94.38% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1021 Remote Services (18.48%); T1566 Phishing (15.16%); T1059 Command and Scripting Interpreter (10.63%) | 0.23% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.52%); T1059 Command and Scripting Interpreter (2.81%); T1082 System Information Discovery (0.38%) | 94.52% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.11%); T1124 System Time Discovery (1.14%); T1543 Create or Modify System Process (0.34%) | 93.11% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1078 Valid Accounts (53.98%); T1105 Ingress Tool Transfer (6.70%); T1021 Remote Services (5.56%) | 2.67% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (36.62%); T1595 Active Scanning (25.38%); T1018 Remote System Discovery (5.87%) | 0.13% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (38.80%); T1595 Active Scanning (24.97%); T1071 Application Layer Protocol (4.09%) | 0.01% | False |

## real_25 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.30%); T1595 Active Scanning (0.54%); T1003 OS Credential Dumping (0.33%) | 96.30% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1105 Ingress Tool Transfer (31.28%); T1078 Valid Accounts (21.59%); T1036 Masquerading (14.57%) | 1.22% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.19%); T1057 Process Discovery (0.24%); T1201 Password Policy Discovery (0.15%) | 97.19% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.65%); T1190 Exploit Public-Facing Application (0.89%); T1589 Gather Victim Identity Information (0.14%) | 97.65% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (86.94%); T1205 Traffic Signaling (3.20%); T1078 Valid Accounts (1.98%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (91.76%); T1059 Command and Scripting Interpreter (3.15%); T1219 Remote Access Tools (0.63%) | 91.76% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.00%); T1124 System Time Discovery (1.42%); T1485 Data Destruction (0.34%) | 93.00% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1105 Ingress Tool Transfer (65.40%); T1071 Application Layer Protocol (13.85%); T1078 Valid Accounts (2.42%) | 0.24% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (18.07%); T1591 Gather Victim Org Information (16.49%); T1082 System Information Discovery (5.14%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (9.39%); T1564 Hide Artifacts (6.15%); T1218 System Binary Proxy Execution (5.12%) | 0.81% | False |

## real_25 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.40%); T1218 System Binary Proxy Execution (0.36%); T1071 Application Layer Protocol (0.19%) | 96.40% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.49%); T1548 Abuse Elevation Control Mechanism (1.36%); T1105 Ingress Tool Transfer (0.75%) | 95.49% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.66%); T1057 Process Discovery (0.93%); T1201 Password Policy Discovery (0.43%) | 95.66% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.58%); T1190 Exploit Public-Facing Application (1.47%); T1592 Gather Victim Host Information (0.12%) | 96.58% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1078 Valid Accounts (49.33%); T1059 Command and Scripting Interpreter (11.09%); T1547 Boot or Logon Autostart Execution (8.65%) | 0.11% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (55.86%); T1087 Account Discovery (40.72%); T1083 File and Directory Discovery (0.39%) | 40.72% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (95.67%); T1124 System Time Discovery (0.51%); T1543 Create or Modify System Process (0.36%) | 95.67% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (83.37%); T1021 Remote Services (1.57%); T1201 Password Policy Discovery (1.29%) | 83.37% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (36.92%); T1033 System Owner/User Discovery (17.43%); T1222 File and Directory Permissions Modification (12.45%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (34.87%); T1003 OS Credential Dumping (16.12%); T1070 Indicator Removal (15.19%) | 0.56% | False |

## real_25 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.14%); T1007 System Service Discovery (0.20%); T1589 Gather Victim Identity Information (0.18%) | 97.14% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1547 Boot or Logon Autostart Execution (26.25%); T1078 Valid Accounts (15.50%); T1599 Network Boundary Bridging (9.05%) | 0.08% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (96.35%); T1003 OS Credential Dumping (0.51%); T1057 Process Discovery (0.33%) | 96.35% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.05%); T1190 Exploit Public-Facing Application (0.62%); T1589 Gather Victim Identity Information (0.45%) | 97.05% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (16.82%); T1003 OS Credential Dumping (13.20%); T1548 Abuse Elevation Control Mechanism (9.61%) | 0.12% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (77.39%); T1059 Command and Scripting Interpreter (17.11%); T1614 System Location Discovery (0.52%) | 77.39% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (95.31%); T1124 System Time Discovery (1.00%); T1592 Gather Victim Host Information (0.17%) | 95.31% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1078 Valid Accounts (75.82%); T1547 Boot or Logon Autostart Execution (7.88%); T1059 Command and Scripting Interpreter (2.59%) | 0.37% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (27.78%); T1070 Indicator Removal (8.33%); T1564 Hide Artifacts (5.40%) | 0.12% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (14.67%); T1033 System Owner/User Discovery (8.54%); T1543 Create or Modify System Process (8.17%) | 0.35% | False |

## real_25 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.48%); T1595 Active Scanning (0.25%); T1033 System Owner/User Discovery (0.23%) | 96.48% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.20%); T1548 Abuse Elevation Control Mechanism (1.95%); T1205 Traffic Signaling (0.48%) | 95.20% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (92.41%); T1057 Process Discovery (1.67%); T1201 Password Policy Discovery (1.21%) | 92.41% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.45%); T1190 Exploit Public-Facing Application (2.24%); T1589 Gather Victim Identity Information (0.26%) | 95.45% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.23%); T1059 Command and Scripting Interpreter (4.79%); T1041 Exfiltration Over C2 Channel (0.17%) | 92.23% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (89.79%); T1083 File and Directory Discovery (2.83%); T1059 Command and Scripting Interpreter (2.74%) | 89.79% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.32%); T1124 System Time Discovery (0.76%); T1059 Command and Scripting Interpreter (0.35%) | 93.32% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (82.44%); T1039 Data from Network Shared Drive (4.63%); T1083 File and Directory Discovery (1.20%) | 82.44% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1083 File and Directory Discovery (12.90%); T1003 OS Credential Dumping (9.73%); T1071 Application Layer Protocol (9.41%) | 1.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (12.61%); T1041 Exfiltration Over C2 Channel (8.22%); T1072 Software Deployment Tools (6.37%) | 0.06% | False |

## real_25 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.21%); T1083 File and Directory Discovery (0.43%); T1205 Traffic Signaling (0.38%) | 96.21% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1105 Ingress Tool Transfer (48.83%); T1057 Process Discovery (8.05%); T1205 Traffic Signaling (4.92%) | 0.76% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (94.37%); T1219 Remote Access Tools (0.61%); T1057 Process Discovery (0.57%) | 94.37% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.04%); T1190 Exploit Public-Facing Application (1.71%); T1589 Gather Victim Identity Information (0.44%) | 96.04% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (91.16%); T1059 Command and Scripting Interpreter (6.23%); T1068 Exploitation for Privilege Escalation (0.25%) | 91.16% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (75.87%); T1059 Command and Scripting Interpreter (19.21%); T1222 File and Directory Permissions Modification (0.31%) | 75.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (92.42%); T1059 Command and Scripting Interpreter (1.90%); T1124 System Time Discovery (0.41%) | 92.42% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (88.29%); T1039 Data from Network Shared Drive (2.20%); T1059 Command and Scripting Interpreter (0.75%) | 88.29% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (15.66%); T1010 Application Window Discovery (10.25%); T1201 Password Policy Discovery (6.89%) | 0.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (19.84%); T1059 Command and Scripting Interpreter (12.16%); T1041 Exfiltration Over C2 Channel (10.75%) | 0.16% | False |

## real_25 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.02%); T1595 Active Scanning (0.39%); T1589 Gather Victim Identity Information (0.34%) | 97.02% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1546 Event Triggered Execution (35.31%); T1036 Masquerading (10.43%); T1105 Ingress Tool Transfer (10.01%) | 0.93% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (96.06%); T1528 Steal Application Access Token (0.34%); T1543 Create or Modify System Process (0.29%) | 96.06% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.49%); T1190 Exploit Public-Facing Application (1.19%); T1070 Indicator Removal (0.17%) | 96.49% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.84%); T1059 Command and Scripting Interpreter (0.55%); T1033 System Owner/User Discovery (0.09%) | 97.84% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (79.26%); T1059 Command and Scripting Interpreter (17.00%); T1083 File and Directory Discovery (1.06%) | 79.26% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.21%); T1124 System Time Discovery (0.41%); T1557 Adversary-in-the-Middle (0.22%) | 96.21% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (72.25%); T1039 Data from Network Shared Drive (6.61%); T1120 Peripheral Device Discovery (5.04%) | 72.25% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1120 Peripheral Device Discovery (17.59%); T1059 Command and Scripting Interpreter (11.23%); T1003 OS Credential Dumping (7.99%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (9.35%); T1003 OS Credential Dumping (8.13%); T1105 Ingress Tool Transfer (6.97%) | 0.05% | False |

## real_25 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.29%); T1589 Gather Victim Identity Information (0.28%); T1070 Indicator Removal (0.24%) | 96.29% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (85.46%); T1548 Abuse Elevation Control Mechanism (9.61%); T1105 Ingress Tool Transfer (1.36%) | 85.46% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.87%); T1003 OS Credential Dumping (0.49%); T1557 Adversary-in-the-Middle (0.31%) | 95.87% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.64%); T1190 Exploit Public-Facing Application (1.58%); T1589 Gather Victim Identity Information (0.24%) | 96.64% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (87.94%); T1071 Application Layer Protocol (2.77%); T1548 Abuse Elevation Control Mechanism (1.41%) | 0.02% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.18%); T1059 Command and Scripting Interpreter (10.53%); T1083 File and Directory Discovery (0.35%) | 86.18% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.04%); T1059 Command and Scripting Interpreter (0.63%); T1615 Group Policy Discovery (0.48%) | 94.04% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1078 Valid Accounts (65.90%); T1120 Peripheral Device Discovery (6.80%); T1105 Ingress Tool Transfer (2.43%) | 1.54% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1497 Virtualization/Sandbox Evasion (14.69%); T1222 File and Directory Permissions Modification (11.01%); T1098 Account Manipulation (7.12%) | 0.55% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (19.19%); T1014 Rootkit (12.32%); T1564 Hide Artifacts (7.00%) | 0.25% | False |

## real_25 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.93%); T1589 Gather Victim Identity Information (0.24%); T1564 Hide Artifacts (0.19%) | 96.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (87.65%); T1548 Abuse Elevation Control Mechanism (7.29%); T1546 Event Triggered Execution (0.49%) | 87.65% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.41%); T1201 Password Policy Discovery (0.53%); T1057 Process Discovery (0.37%) | 95.41% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.27%); T1190 Exploit Public-Facing Application (0.61%); T1589 Gather Victim Identity Information (0.28%) | 97.27% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.04%); T1059 Command and Scripting Interpreter (1.63%); T1033 System Owner/User Discovery (0.22%) | 95.04% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (82.87%); T1059 Command and Scripting Interpreter (11.93%); T1053 Scheduled Task/Job (0.46%) | 82.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (84.39%); T1105 Ingress Tool Transfer (2.13%); T1219 Remote Access Tools (1.42%) | 84.39% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (87.36%); T1039 Data from Network Shared Drive (2.88%); T1041 Exfiltration Over C2 Channel (0.70%) | 87.36% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1046 Network Service Scanning (14.67%); T1222 File and Directory Permissions Modification (11.74%); T1566 Phishing (6.76%) | 1.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1046 Network Service Scanning (12.96%); T1057 Process Discovery (10.20%); T1566 Phishing (9.65%) | 0.14% | False |

## real_25 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.49%); T1543 Create or Modify System Process (0.42%); T1005 Data from Local System (0.26%) | 96.49% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1078 Valid Accounts (57.02%); T1036 Masquerading (7.10%); T1547 Boot or Logon Autostart Execution (5.47%) | 0.08% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (94.84%); T1057 Process Discovery (1.02%); T1003 OS Credential Dumping (0.41%) | 94.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.92%); T1190 Exploit Public-Facing Application (1.94%); T1589 Gather Victim Identity Information (0.18%) | 95.92% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1110 Brute Force (21.85%); T1133 External Remote Services (15.25%); T1485 Data Destruction (8.00%) | 0.45% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.39%); T1059 Command and Scripting Interpreter (1.27%); T1083 File and Directory Discovery (0.67%) | 94.39% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.66%); T1490 Inhibit System Recovery (0.15%); T1124 System Time Discovery (0.14%) | 96.66% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (84.78%); T1039 Data from Network Shared Drive (2.70%); T1049 System Network Connections Discovery (1.50%) | 84.78% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (6.94%); T1219 Remote Access Tools (5.53%); T1057 Process Discovery (4.89%) | 1.12% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (28.47%); T1222 File and Directory Permissions Modification (9.02%); T1057 Process Discovery (4.27%) | 0.15% | False |

## real_25 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.57%); T1595 Active Scanning (0.55%); T1589 Gather Victim Identity Information (0.33%) | 95.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1547 Boot or Logon Autostart Execution (14.48%); T1021 Remote Services (10.92%); T1543 Create or Modify System Process (9.40%) | 3.61% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.86%); T1543 Create or Modify System Process (0.48%); T1053 Scheduled Task/Job (0.33%) | 95.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.38%); T1190 Exploit Public-Facing Application (1.34%); T1589 Gather Victim Identity Information (0.16%) | 96.38% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1021 Remote Services (16.17%); T1120 Peripheral Device Discovery (15.98%); T1003 OS Credential Dumping (9.19%) | 0.49% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.93%); T1059 Command and Scripting Interpreter (2.03%); T1083 File and Directory Discovery (0.25%) | 94.93% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.74%); T1124 System Time Discovery (0.66%); T1210 Exploitation of Remote Services (0.54%) | 94.74% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1078 Valid Accounts (93.63%); T1210 Exploitation of Remote Services (0.46%); T1053 Scheduled Task/Job (0.41%) | 0.28% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (82.08%); T1543 Create or Modify System Process (2.62%); T1219 Remote Access Tools (2.24%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (30.89%); T1219 Remote Access Tools (9.38%); T1543 Create or Modify System Process (9.02%) | 0.16% | False |

## real_25 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (93.98%); T1595 Active Scanning (0.90%); T1110 Brute Force (0.55%) | 93.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (25.52%); T1071 Application Layer Protocol (9.34%); T1205 Traffic Signaling (7.60%) | 1.54% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.76%); T1201 Password Policy Discovery (0.44%); T1057 Process Discovery (0.31%) | 95.76% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.44%); T1190 Exploit Public-Facing Application (0.49%); T1589 Gather Victim Identity Information (0.16%) | 97.44% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1218 System Binary Proxy Execution (13.05%); T1105 Ingress Tool Transfer (12.29%); T1041 Exfiltration Over C2 Channel (8.61%) | 0.13% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (90.64%); T1095 Non-Application Layer Protocol (1.49%); T1218 System Binary Proxy Execution (1.12%) | 90.64% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (92.41%); T1124 System Time Discovery (0.91%); T1072 Software Deployment Tools (0.34%) | 92.41% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1105 Ingress Tool Transfer (45.85%); T1573 Encrypted Channel (14.49%); T1071 Application Layer Protocol (6.49%) | 0.67% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (36.88%); T1003 OS Credential Dumping (12.56%); T1078 Valid Accounts (10.24%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (73.63%); T1033 System Owner/User Discovery (5.00%); T1566 Phishing (4.13%) | 0.06% | False |

## real_25 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.63%); T1071 Application Layer Protocol (0.54%); T1557 Adversary-in-the-Middle (0.38%) | 94.63% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (84.92%); T1548 Abuse Elevation Control Mechanism (9.13%); T1218 System Binary Proxy Execution (0.40%) | 84.92% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.15%); T1057 Process Discovery (0.41%); T1485 Data Destruction (0.33%) | 95.15% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.70%); T1190 Exploit Public-Facing Application (1.52%); T1592 Gather Victim Host Information (0.50%) | 94.70% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1078 Valid Accounts (45.20%); T1059 Command and Scripting Interpreter (13.98%); T1120 Peripheral Device Discovery (7.93%) | 0.04% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (88.38%); T1059 Command and Scripting Interpreter (7.14%); T1083 File and Directory Discovery (0.61%) | 88.38% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.69%); T1525 Implant Internal Image (0.66%); T1124 System Time Discovery (0.42%) | 94.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (81.36%); T1039 Data from Network Shared Drive (1.99%); T1486 Data Encrypted for Impact (1.87%) | 81.36% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (50.29%); T1222 File and Directory Permissions Modification (10.24%); T1105 Ingress Tool Transfer (6.21%) | 0.11% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (33.19%); T1222 File and Directory Permissions Modification (19.18%); T1033 System Owner/User Discovery (10.39%) | 0.18% | False |

## real_25 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.64%); T1105 Ingress Tool Transfer (0.46%); T1071 Application Layer Protocol (0.42%) | 95.64% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1105 Ingress Tool Transfer (23.53%); T1547 Boot or Logon Autostart Execution (21.52%); T1078 Valid Accounts (8.17%) | 1.35% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (94.23%); T1057 Process Discovery (1.07%); T1201 Password Policy Discovery (0.75%) | 94.23% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.31%); T1190 Exploit Public-Facing Application (1.31%); T1589 Gather Victim Identity Information (0.52%) | 94.31% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1490 Inhibit System Recovery (12.91%); T1083 File and Directory Discovery (11.51%); T1049 System Network Connections Discovery (7.45%) | 0.57% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (77.24%); T1059 Command and Scripting Interpreter (18.56%); T1201 Password Policy Discovery (0.28%) | 77.24% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.00%); T1124 System Time Discovery (1.35%); T1018 Remote System Discovery (0.19%) | 94.00% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1078 Valid Accounts (75.64%); T1070 Indicator Removal (3.47%); T1547 Boot or Logon Autostart Execution (1.86%) | 0.05% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1039 Data from Network Shared Drive (13.66%); T1105 Ingress Tool Transfer (11.47%); T1222 File and Directory Permissions Modification (10.24%) | 0.67% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (44.45%); T1105 Ingress Tool Transfer (7.25%); T1059 Command and Scripting Interpreter (4.39%) | 0.40% | False |

## real_25 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.62%); T1595 Active Scanning (0.65%); T1589 Gather Victim Identity Information (0.30%) | 94.62% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (92.42%); T1548 Abuse Elevation Control Mechanism (2.15%); T1205 Traffic Signaling (0.65%) | 92.42% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (89.65%); T1201 Password Policy Discovery (0.87%); T1078 Valid Accounts (0.58%) | 89.65% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.33%); T1190 Exploit Public-Facing Application (0.64%); T1589 Gather Victim Identity Information (0.51%) | 96.33% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.21%); T1059 Command and Scripting Interpreter (0.32%); T1218 System Binary Proxy Execution (0.16%) | 97.21% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (90.19%); T1083 File and Directory Discovery (1.50%); T1059 Command and Scripting Interpreter (0.53%) | 90.19% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (91.06%); T1059 Command and Scripting Interpreter (1.47%); T1124 System Time Discovery (1.10%) | 91.06% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (78.08%); T1039 Data from Network Shared Drive (3.15%); T1083 File and Directory Discovery (1.89%) | 78.08% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (37.43%); T1546 Event Triggered Execution (18.86%); T1120 Peripheral Device Discovery (7.15%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (25.11%); T1078 Valid Accounts (18.21%); T1546 Event Triggered Execution (9.21%) | 0.12% | False |

## real_25 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (94.97%); T1083 File and Directory Discovery (0.84%); T1078 Valid Accounts (0.37%) | 94.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (12.41%); T1599 Network Boundary Bridging (12.18%); T1078 Valid Accounts (11.73%) | 0.06% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (94.43%); T1201 Password Policy Discovery (0.45%); T1219 Remote Access Tools (0.37%) | 94.43% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.69%); T1190 Exploit Public-Facing Application (1.40%); T1589 Gather Victim Identity Information (0.51%) | 95.69% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.39%); T1059 Command and Scripting Interpreter (1.83%); T1087 Account Discovery (0.27%) | 95.39% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (89.13%); T1059 Command and Scripting Interpreter (5.45%); T1136 Create Account (0.37%) | 89.13% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.45%); T1124 System Time Discovery (0.74%); T1204 User Execution (0.31%) | 93.45% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (76.54%); T1039 Data from Network Shared Drive (5.81%); T1120 Peripheral Device Discovery (2.03%) | 76.54% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1046 Network Service Scanning (15.47%); T1082 System Information Discovery (7.28%); T1049 System Network Connections Discovery (5.99%) | 0.39% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1021 Remote Services (10.48%); T1565 Data Manipulation (6.21%); T1213 Data from Information Repositories (5.64%) | 2.21% | False |

## real_25 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.00%); T1589 Gather Victim Identity Information (0.53%); T1557 Adversary-in-the-Middle (0.41%) | 95.00% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1546 Event Triggered Execution (42.00%); T1033 System Owner/User Discovery (17.99%); T1069 Permission Groups Discovery (5.12%) | 17.99% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.83%); T1528 Steal Application Access Token (0.37%); T1201 Password Policy Discovery (0.28%) | 95.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.41%); T1190 Exploit Public-Facing Application (0.72%); T1589 Gather Victim Identity Information (0.38%) | 96.41% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.61%); T1059 Command and Scripting Interpreter (1.57%); T1033 System Owner/User Discovery (0.27%) | 95.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (91.11%); T1059 Command and Scripting Interpreter (2.85%); T1083 File and Directory Discovery (0.89%) | 91.11% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.97%); T1124 System Time Discovery (0.50%); T1120 Peripheral Device Discovery (0.33%) | 94.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (79.99%); T1039 Data from Network Shared Drive (3.38%); T1041 Exfiltration Over C2 Channel (2.66%) | 79.99% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (7.60%); T1614 System Location Discovery (6.43%); T1595 Active Scanning (5.93%) | 0.51% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1531 Account Access Removal (10.99%); T1082 System Information Discovery (6.53%); T1518 Software Discovery (5.57%) | 0.10% | False |

## real_25 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.96%); T1592 Gather Victim Host Information (0.67%); T1589 Gather Victim Identity Information (0.47%) | 95.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (87.00%); T1548 Abuse Elevation Control Mechanism (6.87%); T1105 Ingress Tool Transfer (0.86%) | 87.00% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (94.74%); T1082 System Information Discovery (0.37%); T1053 Scheduled Task/Job (0.36%) | 94.74% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.07%); T1190 Exploit Public-Facing Application (1.93%); T1589 Gather Victim Identity Information (0.50%) | 95.07% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1033 System Owner/User Discovery (50.29%); T1105 Ingress Tool Transfer (17.86%); T1003 OS Credential Dumping (7.78%) | 0.06% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (84.62%); T1059 Command and Scripting Interpreter (10.67%); T1083 File and Directory Discovery (0.45%) | 84.62% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (95.63%); T1124 System Time Discovery (0.29%); T1098 Account Manipulation (0.27%) | 95.63% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1078 Valid Accounts (91.60%); T1021 Remote Services (1.65%); T1041 Exfiltration Over C2 Channel (0.66%) | 0.07% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (45.50%); T1082 System Information Discovery (9.75%); T1071 Application Layer Protocol (8.19%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (31.92%); T1078 Valid Accounts (14.84%); T1033 System Owner/User Discovery (8.91%) | 0.05% | False |

## real_25 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.18%); T1557 Adversary-in-the-Middle (0.41%); T1589 Gather Victim Identity Information (0.39%) | 95.18% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.03%); T1548 Abuse Elevation Control Mechanism (2.18%); T1574 Hijack Execution Flow (0.86%) | 93.03% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.56%); T1057 Process Discovery (0.44%); T1201 Password Policy Discovery (0.41%) | 95.56% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.66%); T1190 Exploit Public-Facing Application (1.34%); T1589 Gather Victim Identity Information (0.35%) | 95.66% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.37%); T1059 Command and Scripting Interpreter (3.61%); T1087 Account Discovery (0.40%) | 92.37% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (90.32%); T1059 Command and Scripting Interpreter (5.71%); T1053 Scheduled Task/Job (0.36%) | 90.32% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.21%); T1518 Software Discovery (0.85%); T1124 System Time Discovery (0.47%) | 93.21% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (85.62%); T1039 Data from Network Shared Drive (1.98%); T1041 Exfiltration Over C2 Channel (1.88%) | 85.62% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (16.26%); T1003 OS Credential Dumping (16.19%); T1041 Exfiltration Over C2 Channel (14.06%) | 0.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1041 Exfiltration Over C2 Channel (23.70%); T1059 Command and Scripting Interpreter (20.52%); T1003 OS Credential Dumping (8.54%) | 0.53% | False |

## real_25 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (95.04%); T1543 Create or Modify System Process (0.47%); T1005 Data from Local System (0.40%) | 95.04% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (29.88%); T1543 Create or Modify System Process (10.87%); T1070 Indicator Removal (7.27%) | 6.25% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (93.56%); T1057 Process Discovery (1.38%); T1018 Remote System Discovery (0.48%) | 93.56% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (95.34%); T1190 Exploit Public-Facing Application (1.36%); T1592 Gather Victim Host Information (0.33%) | 95.34% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (87.09%); T1021 Remote Services (1.22%); T1201 Password Policy Discovery (0.84%) | 0.10% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (88.38%); T1059 Command and Scripting Interpreter (5.46%); T1083 File and Directory Discovery (0.71%) | 88.38% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.49%); T1485 Data Destruction (0.55%); T1124 System Time Discovery (0.32%) | 94.49% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (85.25%); T1039 Data from Network Shared Drive (2.76%); T1021 Remote Services (1.25%) | 85.25% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1219 Remote Access Tools (27.57%); T1105 Ingress Tool Transfer (15.69%); T1136 Create Account (6.51%) | 0.22% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1219 Remote Access Tools (12.33%); T1525 Implant Internal Image (8.85%); T1010 Application Window Discovery (6.92%) | 1.23% | False |

## real_25 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.57%); T1565 Data Manipulation (0.19%); T1589 Gather Victim Identity Information (0.16%) | 96.57% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (16.04%); T1120 Peripheral Device Discovery (14.40%); T1556 Modify Authentication Process (9.26%) | 16.04% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (96.41%); T1543 Create or Modify System Process (0.37%); T1039 Data from Network Shared Drive (0.31%) | 96.41% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (53.83%); T1595 Active Scanning (42.01%); T1592 Gather Victim Host Information (0.38%) | 42.01% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1033 System Owner/User Discovery (32.00%); T1016 System Network Configuration Discovery (24.75%); T1003 OS Credential Dumping (6.05%) | 0.08% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (71.37%); T1087 Account Discovery (24.70%); T1486 Data Encrypted for Impact (0.58%) | 24.70% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.33%); T1201 Password Policy Discovery (0.22%); T1574 Hijack Execution Flow (0.19%) | 96.33% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (46.33%); T1105 Ingress Tool Transfer (8.83%); T1041 Exfiltration Over C2 Channel (6.36%) | 46.33% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (84.79%); T1059 Command and Scripting Interpreter (3.09%); T1016 System Network Configuration Discovery (2.43%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (57.54%); T1105 Ingress Tool Transfer (5.87%); T1018 Remote System Discovery (3.80%) | 0.19% | False |

## real_25 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.28%); T1595 Active Scanning (0.42%); T1053 Scheduled Task/Job (0.32%) | 96.28% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (37.20%); T1548 Abuse Elevation Control Mechanism (20.89%); T1105 Ingress Tool Transfer (5.13%) | 0.76% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.94%); T1083 File and Directory Discovery (0.56%); T1082 System Information Discovery (0.21%) | 95.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (53.69%); T1190 Exploit Public-Facing Application (38.84%); T1592 Gather Victim Host Information (3.24%) | 53.69% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1033 System Owner/User Discovery (26.91%); T1070 Indicator Removal (25.96%); T1543 Create or Modify System Process (11.36%) | 0.06% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (88.07%); T1087 Account Discovery (9.81%); T1105 Ingress Tool Transfer (0.39%) | 9.81% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (95.05%); T1016 System Network Configuration Discovery (0.58%); T1610 Deploy Container (0.32%) | 95.05% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1071 Application Layer Protocol (17.77%); T1105 Ingress Tool Transfer (14.74%); T1213 Data from Information Repositories (12.19%) | 12.19% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1201 Password Policy Discovery (22.67%); T1078 Valid Accounts (17.40%); T1007 System Service Discovery (11.51%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (17.53%); T1222 File and Directory Permissions Modification (9.67%); T1219 Remote Access Tools (8.66%) | 1.60% | False |

## real_25 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.05%); T1071 Application Layer Protocol (0.65%); T1070 Indicator Removal (0.30%) | 96.05% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (49.47%); T1548 Abuse Elevation Control Mechanism (38.88%); T1036 Masquerading (1.41%) | 49.47% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.77%); T1124 System Time Discovery (0.25%); T1518 Software Discovery (0.23%) | 95.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (52.57%); T1595 Active Scanning (38.66%); T1592 Gather Victim Host Information (2.61%) | 38.66% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1059 Command and Scripting Interpreter (16.11%); T1046 Network Service Scanning (8.78%); T1136 Create Account (8.72%) | 0.22% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (64.09%); T1087 Account Discovery (32.11%); T1082 System Information Discovery (0.58%) | 32.11% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (90.80%); T1566 Phishing (1.23%); T1204 User Execution (1.04%) | 90.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (48.43%); T1021 Remote Services (24.22%); T1049 System Network Connections Discovery (4.01%) | 48.43% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (13.36%); T1070 Indicator Removal (11.70%); T1018 Remote System Discovery (6.16%) | 0.53% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (46.35%); T1574 Hijack Execution Flow (8.34%); T1564 Hide Artifacts (5.23%) | 0.75% | False |

## real_25 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.30%); T1595 Active Scanning (0.27%); T1053 Scheduled Task/Job (0.21%) | 96.30% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1218 System Binary Proxy Execution (40.44%); T1070 Indicator Removal (8.58%); T1036 Masquerading (7.61%) | 0.38% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (96.22%); T1003 OS Credential Dumping (0.42%); T1082 System Information Discovery (0.38%) | 96.22% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (51.47%); T1190 Exploit Public-Facing Application (42.42%); T1592 Gather Victim Host Information (0.80%) | 51.47% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1033 System Owner/User Discovery (83.88%); T1059 Command and Scripting Interpreter (2.34%); T1218 System Binary Proxy Execution (1.54%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (79.18%); T1087 Account Discovery (16.42%); T1105 Ingress Tool Transfer (0.76%) | 16.42% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.91%); T1525 Implant Internal Image (0.38%); T1518 Software Discovery (0.31%) | 93.91% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (45.70%); T1049 System Network Connections Discovery (12.64%); T1041 Exfiltration Over C2 Channel (9.86%) | 45.70% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (13.01%); T1589 Gather Victim Identity Information (10.69%); T1218 System Binary Proxy Execution (10.52%) | 0.19% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (15.08%); T1016 System Network Configuration Discovery (14.61%); T1219 Remote Access Tools (8.06%) | 0.83% | False |

## real_25 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.83%); T1610 Deploy Container (0.18%); T1595 Active Scanning (0.17%) | 96.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (61.43%); T1548 Abuse Elevation Control Mechanism (25.97%); T1036 Masquerading (3.49%) | 61.43% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.98%); T1615 Group Policy Discovery (0.29%); T1219 Remote Access Tools (0.28%) | 95.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (54.03%); T1190 Exploit Public-Facing Application (41.87%); T1592 Gather Victim Host Information (0.75%) | 54.03% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.74%); T1105 Ingress Tool Transfer (0.34%); T1218 System Binary Proxy Execution (0.15%) | 97.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.35%); T1087 Account Discovery (19.46%); T1033 System Owner/User Discovery (0.20%) | 19.46% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.68%); T1016 System Network Configuration Discovery (0.62%); T1083 File and Directory Discovery (0.42%) | 93.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (76.49%); T1049 System Network Connections Discovery (3.37%); T1201 Password Policy Discovery (2.32%) | 76.49% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1592 Gather Victim Host Information (13.34%); T1543 Create or Modify System Process (13.18%); T1531 Account Access Removal (12.25%) | 0.25% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (17.13%); T1222 File and Directory Permissions Modification (10.30%); T1082 System Information Discovery (4.61%) | 0.23% | False |

## real_25 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.54%); T1082 System Information Discovery (0.26%); T1136 Create Account (0.21%) | 96.54% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (37.11%); T1548 Abuse Elevation Control Mechanism (19.29%); T1049 System Network Connections Discovery (5.19%) | 0.09% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.44%); T1016 System Network Configuration Discovery (0.55%); T1614 System Location Discovery (0.41%) | 95.44% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (46.50%); T1190 Exploit Public-Facing Application (46.36%); T1592 Gather Victim Host Information (2.53%) | 46.50% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.31%); T1059 Command and Scripting Interpreter (4.75%); T1033 System Owner/User Discovery (0.25%) | 92.31% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (87.03%); T1087 Account Discovery (11.14%); T1095 Non-Application Layer Protocol (0.24%) | 11.14% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (94.40%); T1078 Valid Accounts (1.28%); T1070 Indicator Removal (0.47%) | 94.40% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (72.45%); T1053 Scheduled Task/Job (3.13%); T1049 System Network Connections Discovery (2.02%) | 72.45% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (13.57%); T1110 Brute Force (5.80%); T1124 System Time Discovery (5.27%) | 1.39% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (14.25%); T1592 Gather Victim Host Information (8.45%); T1550 Use Alternate Authentication Material (6.64%) | 0.19% | False |

## real_25 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.04%); T1110 Brute Force (0.26%); T1560 Archive Collected Data (0.19%) | 97.04% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (23.73%); T1033 System Owner/User Discovery (11.90%); T1546 Event Triggered Execution (7.22%) | 11.90% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.17%); T1049 System Network Connections Discovery (0.50%); T1105 Ingress Tool Transfer (0.48%) | 95.17% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (55.03%); T1595 Active Scanning (38.22%); T1592 Gather Victim Host Information (1.89%) | 38.22% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (92.42%); T1059 Command and Scripting Interpreter (3.32%); T1105 Ingress Tool Transfer (0.60%) | 92.42% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (74.59%); T1087 Account Discovery (22.62%); T1095 Non-Application Layer Protocol (0.36%) | 22.62% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (92.22%); T1120 Peripheral Device Discovery (0.65%); T1041 Exfiltration Over C2 Channel (0.62%) | 92.22% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (63.16%); T1041 Exfiltration Over C2 Channel (2.80%); T1569 System Services (2.68%) | 63.16% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (44.45%); T1071 Application Layer Protocol (9.15%); T1036 Masquerading (8.35%) | 0.26% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (53.79%); T1599 Network Boundary Bridging (11.59%); T1071 Application Layer Protocol (7.94%) | 0.20% | False |

## real_25 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.59%); T1592 Gather Victim Host Information (0.47%); T1573 Encrypted Channel (0.25%) | 96.59% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (82.36%); T1548 Abuse Elevation Control Mechanism (11.12%); T1057 Process Discovery (1.11%) | 82.36% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.26%); T1518 Software Discovery (0.72%); T1082 System Information Discovery (0.29%) | 95.26% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (70.80%); T1190 Exploit Public-Facing Application (25.01%); T1592 Gather Victim Host Information (0.82%) | 70.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1098 Account Manipulation (43.28%); T1018 Remote System Discovery (7.14%); T1046 Network Service Scanning (5.84%) | 0.35% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (69.18%); T1087 Account Discovery (28.00%); T1486 Data Encrypted for Impact (0.42%) | 28.00% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.91%); T1049 System Network Connections Discovery (0.46%); T1489 Service Stop (0.39%) | 93.91% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (20.59%); T1049 System Network Connections Discovery (12.11%); T1041 Exfiltration Over C2 Channel (9.41%) | 20.59% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1219 Remote Access Tools (21.98%); T1485 Data Destruction (8.06%); T1115 Clipboard Data (6.41%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (21.83%); T1219 Remote Access Tools (19.81%); T1010 Application Window Discovery (6.59%) | 1.10% | False |

## real_25 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.64%); T1589 Gather Victim Identity Information (0.19%); T1595 Active Scanning (0.13%) | 97.64% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (54.63%); T1548 Abuse Elevation Control Mechanism (33.68%); T1078 Valid Accounts (1.19%) | 54.63% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (95.41%); T1033 System Owner/User Discovery (0.30%); T1614 System Location Discovery (0.28%) | 95.41% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (48.61%); T1595 Active Scanning (46.61%); T1592 Gather Victim Host Information (0.71%) | 46.61% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.16%); T1059 Command and Scripting Interpreter (0.37%); T1222 File and Directory Permissions Modification (0.32%) | 97.16% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (90.24%); T1087 Account Discovery (8.31%); T1105 Ingress Tool Transfer (0.27%) | 8.31% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.28%); T1190 Exploit Public-Facing Application (0.89%); T1518 Software Discovery (0.59%) | 93.28% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (80.06%); T1041 Exfiltration Over C2 Channel (3.20%); T1049 System Network Connections Discovery (2.05%) | 80.06% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (37.34%); T1057 Process Discovery (8.50%); T1136 Create Account (4.76%) | 0.32% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (24.43%); T1033 System Owner/User Discovery (11.04%); T1069 Permission Groups Discovery (5.78%) | 0.51% | False |

## real_25 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.51%); T1543 Create or Modify System Process (0.51%); T1592 Gather Victim Host Information (0.22%) | 96.51% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (12.57%); T1003 OS Credential Dumping (10.37%); T1033 System Owner/User Discovery (9.20%) | 9.20% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (96.21%); T1057 Process Discovery (0.32%); T1557 Adversary-in-the-Middle (0.28%) | 96.21% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (57.18%); T1595 Active Scanning (35.00%); T1592 Gather Victim Host Information (1.96%) | 35.00% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1003 OS Credential Dumping (18.49%); T1016 System Network Configuration Discovery (13.42%); T1071 Application Layer Protocol (12.28%) | 0.05% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (85.37%); T1087 Account Discovery (12.75%); T1053 Scheduled Task/Job (0.20%) | 12.75% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (92.05%); T1057 Process Discovery (0.64%); T1083 File and Directory Discovery (0.61%) | 92.05% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (73.12%); T1041 Exfiltration Over C2 Channel (4.46%); T1201 Password Policy Discovery (2.12%) | 73.12% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (47.50%); T1574 Hijack Execution Flow (7.59%); T1485 Data Destruction (4.71%) | 0.62% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1614 System Location Discovery (7.35%); T1018 Remote System Discovery (6.86%); T1528 Steal Application Access Token (6.36%) | 0.21% | False |

## real_50 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.56%); T1213 Data from Information Repositories (0.13%); T1589 Gather Victim Identity Information (0.11%) | 98.56% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.62%); T1036 Masquerading (1.28%); T1548 Abuse Elevation Control Mechanism (1.00%) | 96.62% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.75%); T1057 Process Discovery (0.13%); T1053 Scheduled Task/Job (0.12%) | 98.75% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.23%); T1190 Exploit Public-Facing Application (1.08%); T1592 Gather Victim Host Information (0.08%) | 98.23% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1021 Remote Services (31.93%); T1078 Valid Accounts (31.23%); T1547 Boot or Logon Autostart Execution (6.96%) | 0.18% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (76.89%); T1059 Command and Scripting Interpreter (21.26%); T1082 System Information Discovery (0.50%) | 76.89% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.85%); T1124 System Time Discovery (0.69%); T1201 Password Policy Discovery (0.24%) | 96.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.38%); T1591 Gather Victim Org Information (0.64%); T1041 Exfiltration Over C2 Channel (0.35%) | 95.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (45.66%); T1595 Active Scanning (22.28%); T1071 Application Layer Protocol (5.56%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (39.80%); T1595 Active Scanning (17.86%); T1071 Application Layer Protocol (15.31%) | 0.01% | False |

## real_50 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.20%); T1595 Active Scanning (0.24%); T1087 Account Discovery (0.18%) | 98.20% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.53%); T1548 Abuse Elevation Control Mechanism (1.56%); T1105 Ingress Tool Transfer (0.24%) | 96.53% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.83%); T1057 Process Discovery (0.14%); T1201 Password Policy Discovery (0.07%) | 98.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.74%); T1190 Exploit Public-Facing Application (0.47%); T1589 Gather Victim Identity Information (0.13%) | 98.74% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (83.35%); T1205 Traffic Signaling (4.02%); T1059 Command and Scripting Interpreter (2.76%) | 0.02% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.09%); T1059 Command and Scripting Interpreter (1.21%); T1098 Account Manipulation (0.18%) | 97.09% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.51%); T1124 System Time Discovery (0.38%); T1016 System Network Configuration Discovery (0.20%) | 97.51% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.06%); T1039 Data from Network Shared Drive (1.74%); T1120 Peripheral Device Discovery (1.40%) | 92.06% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (20.54%); T1222 File and Directory Permissions Modification (19.58%); T1591 Gather Victim Org Information (12.68%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (66.14%); T1218 System Binary Proxy Execution (4.60%); T1105 Ingress Tool Transfer (3.92%) | 0.99% | False |

## real_50 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.38%); T1218 System Binary Proxy Execution (0.18%); T1574 Hijack Execution Flow (0.10%) | 98.38% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.26%); T1548 Abuse Elevation Control Mechanism (0.20%); T1082 System Information Discovery (0.07%) | 99.26% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.26%); T1057 Process Discovery (0.48%); T1219 Remote Access Tools (0.13%) | 98.26% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.55%); T1190 Exploit Public-Facing Application (0.60%); T1589 Gather Victim Identity Information (0.06%) | 98.55% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1078 Valid Accounts (30.60%); T1059 Command and Scripting Interpreter (13.83%); T1204 User Execution (11.30%) | 0.07% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (93.72%); T1059 Command and Scripting Interpreter (3.63%); T1082 System Information Discovery (0.85%) | 93.72% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.96%); T1124 System Time Discovery (0.21%); T1486 Data Encrypted for Impact (0.14%) | 97.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.96%); T1201 Password Policy Discovery (1.04%); T1039 Data from Network Shared Drive (1.01%) | 92.96% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (66.83%); T1222 File and Directory Permissions Modification (8.84%); T1033 System Owner/User Discovery (6.95%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (29.45%); T1070 Indicator Removal (25.87%); T1003 OS Credential Dumping (18.33%) | 0.27% | False |

## real_50 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.96%); T1078 Valid Accounts (0.08%); T1007 System Service Discovery (0.07%) | 98.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.08%); T1548 Abuse Elevation Control Mechanism (1.72%); T1105 Ingress Tool Transfer (0.59%) | 96.08% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.86%); T1057 Process Discovery (0.17%); T1564 Hide Artifacts (0.09%) | 98.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.54%); T1589 Gather Victim Identity Information (0.34%); T1190 Exploit Public-Facing Application (0.33%) | 98.54% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1003 OS Credential Dumping (18.63%); T1105 Ingress Tool Transfer (16.24%); T1548 Abuse Elevation Control Mechanism (14.56%) | 0.06% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (69.25%); T1059 Command and Scripting Interpreter (28.64%); T1082 System Information Discovery (0.22%) | 69.25% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.41%); T1124 System Time Discovery (0.19%); T1018 Remote System Discovery (0.09%) | 98.41% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.12%); T1039 Data from Network Shared Drive (1.17%); T1120 Peripheral Device Discovery (0.53%) | 94.12% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (13.37%); T1070 Indicator Removal (12.09%); T1007 System Service Discovery (9.06%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1201 Password Policy Discovery (15.78%); T1543 Create or Modify System Process (13.94%); T1033 System Owner/User Discovery (12.95%) | 0.06% | False |

## real_50 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.26%); T1053 Scheduled Task/Job (0.14%); T1595 Active Scanning (0.11%) | 98.26% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.73%); T1548 Abuse Elevation Control Mechanism (0.54%); T1205 Traffic Signaling (0.13%) | 98.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.59%); T1057 Process Discovery (0.49%); T1201 Password Policy Discovery (0.36%) | 97.59% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.83%); T1190 Exploit Public-Facing Application (1.28%); T1589 Gather Victim Identity Information (0.11%) | 97.83% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.28%); T1059 Command and Scripting Interpreter (1.15%); T1547 Boot or Logon Autostart Execution (0.15%) | 97.28% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.46%); T1059 Command and Scripting Interpreter (10.21%); T1033 System Owner/User Discovery (0.81%) | 86.46% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.06%); T1124 System Time Discovery (0.32%); T1564 Hide Artifacts (0.19%) | 97.06% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.48%); T1039 Data from Network Shared Drive (1.04%); T1018 Remote System Discovery (0.26%) | 95.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (15.62%); T1083 File and Directory Discovery (8.28%); T1016 System Network Configuration Discovery (7.95%) | 1.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (24.22%); T1003 OS Credential Dumping (14.39%); T1222 File and Directory Permissions Modification (10.43%) | 0.03% | False |

## real_50 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.13%); T1083 File and Directory Discovery (0.23%); T1205 Traffic Signaling (0.13%) | 98.13% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (90.77%); T1548 Abuse Elevation Control Mechanism (5.26%); T1105 Ingress Tool Transfer (0.81%) | 90.77% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.73%); T1219 Remote Access Tools (0.34%); T1057 Process Discovery (0.22%) | 97.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.53%); T1190 Exploit Public-Facing Application (0.54%); T1589 Gather Victim Identity Information (0.22%) | 98.53% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.56%); T1059 Command and Scripting Interpreter (1.62%); T1068 Exploitation for Privilege Escalation (0.21%) | 96.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (93.05%); T1059 Command and Scripting Interpreter (5.11%); T1486 Data Encrypted for Impact (0.27%) | 93.05% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.59%); T1059 Command and Scripting Interpreter (0.47%); T1072 Software Deployment Tools (0.15%) | 97.59% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.80%); T1039 Data from Network Shared Drive (1.97%); T1573 Encrypted Channel (0.52%) | 92.80% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (17.22%); T1105 Ingress Tool Transfer (8.02%); T1010 Application Window Discovery (7.98%) | 0.19% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (13.10%); T1105 Ingress Tool Transfer (9.89%); T1201 Password Policy Discovery (9.03%) | 0.03% | False |

## real_50 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.62%); T1589 Gather Victim Identity Information (0.18%); T1595 Active Scanning (0.11%) | 98.62% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (90.96%); T1548 Abuse Elevation Control Mechanism (3.59%); T1566 Phishing (0.98%) | 90.96% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.98%); T1528 Steal Application Access Token (0.18%); T1218 System Binary Proxy Execution (0.17%) | 97.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.45%); T1190 Exploit Public-Facing Application (0.63%); T1592 Gather Victim Host Information (0.08%) | 98.45% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.00%); T1059 Command and Scripting Interpreter (1.43%); T1204 User Execution (0.13%) | 97.00% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (64.00%); T1087 Account Discovery (34.59%); T1083 File and Directory Discovery (0.29%) | 34.59% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.86%); T1124 System Time Discovery (0.21%); T1040 Network Sniffing (0.12%) | 97.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (90.97%); T1039 Data from Network Shared Drive (2.01%); T1120 Peripheral Device Discovery (1.76%) | 90.97% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (37.60%); T1059 Command and Scripting Interpreter (31.89%); T1546 Event Triggered Execution (3.57%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (57.21%); T1059 Command and Scripting Interpreter (8.15%); T1053 Scheduled Task/Job (7.52%) | 0.01% | False |

## real_50 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.68%); T1070 Indicator Removal (0.09%); T1201 Password Policy Discovery (0.09%) | 98.68% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (89.08%); T1548 Abuse Elevation Control Mechanism (6.75%); T1105 Ingress Tool Transfer (1.72%) | 89.08% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.53%); T1003 OS Credential Dumping (0.14%); T1053 Scheduled Task/Job (0.12%) | 98.53% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.62%); T1190 Exploit Public-Facing Application (0.62%); T1589 Gather Victim Identity Information (0.15%) | 98.62% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (96.66%); T1071 Application Layer Protocol (0.63%); T1548 Abuse Elevation Control Mechanism (0.46%) | 0.00% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (51.43%); T1059 Command and Scripting Interpreter (46.34%); T1083 File and Directory Discovery (0.47%) | 51.43% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.13%); T1566 Phishing (0.58%); T1205 Traffic Signaling (0.25%) | 97.13% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.92%); T1039 Data from Network Shared Drive (1.37%); T1548 Abuse Elevation Control Mechanism (0.47%) | 92.92% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (34.44%); T1497 Virtualization/Sandbox Evasion (7.83%); T1014 Rootkit (4.70%) | 0.60% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (36.67%); T1014 Rootkit (11.53%); T1566 Phishing (9.74%) | 0.14% | False |

## real_50 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.65%); T1595 Active Scanning (0.12%); T1204 User Execution (0.09%) | 98.65% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (91.82%); T1548 Abuse Elevation Control Mechanism (3.16%); T1105 Ingress Tool Transfer (1.68%) | 91.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.32%); T1201 Password Policy Discovery (0.18%); T1518 Software Discovery (0.13%) | 98.32% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.12%); T1190 Exploit Public-Facing Application (0.74%); T1589 Gather Victim Identity Information (0.17%) | 98.12% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.25%); T1059 Command and Scripting Interpreter (2.18%); T1610 Deploy Container (0.17%) | 95.25% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (78.88%); T1059 Command and Scripting Interpreter (19.14%); T1083 File and Directory Discovery (0.17%) | 78.88% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.04%); T1105 Ingress Tool Transfer (0.43%); T1219 Remote Access Tools (0.38%) | 96.04% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (93.30%); T1039 Data from Network Shared Drive (1.29%); T1564 Hide Artifacts (0.49%) | 93.30% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (13.20%); T1033 System Owner/User Discovery (12.50%); T1204 User Execution (11.98%) | 0.33% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (53.61%); T1566 Phishing (5.24%); T1069 Permission Groups Discovery (4.30%) | 0.02% | False |

## real_50 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.52%); T1005 Data from Local System (0.13%); T1543 Create or Modify System Process (0.11%) | 98.52% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1036 Masquerading (23.58%); T1078 Valid Accounts (17.29%); T1547 Boot or Logon Autostart Execution (15.85%) | 0.11% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.86%); T1057 Process Discovery (0.37%); T1557 Adversary-in-the-Middle (0.19%) | 97.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.66%); T1190 Exploit Public-Facing Application (1.42%); T1589 Gather Victim Identity Information (0.17%) | 97.66% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1110 Brute Force (23.97%); T1565 Data Manipulation (11.70%); T1087 Account Discovery (6.27%) | 0.28% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.00%); T1059 Command and Scripting Interpreter (1.39%); T1083 File and Directory Discovery (0.24%) | 97.00% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.28%); T1124 System Time Discovery (0.11%); T1016 System Network Configuration Discovery (0.09%) | 98.28% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.56%); T1039 Data from Network Shared Drive (0.66%); T1049 System Network Connections Discovery (0.48%) | 94.56% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1219 Remote Access Tools (25.68%); T1595 Active Scanning (7.86%); T1057 Process Discovery (5.69%) | 0.83% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (12.11%); T1222 File and Directory Permissions Modification (11.29%); T1057 Process Discovery (8.34%) | 0.04% | False |

## real_50 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.88%); T1595 Active Scanning (0.24%); T1589 Gather Victim Identity Information (0.15%) | 97.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.73%); T1548 Abuse Elevation Control Mechanism (2.24%); T1036 Masquerading (0.88%) | 95.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.25%); T1543 Create or Modify System Process (0.25%); T1057 Process Discovery (0.21%) | 98.25% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.42%); T1190 Exploit Public-Facing Application (0.60%); T1592 Gather Victim Host Information (0.14%) | 98.42% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1021 Remote Services (21.98%); T1082 System Information Discovery (18.36%); T1591 Gather Victim Org Information (7.61%) | 0.45% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.20%); T1059 Command and Scripting Interpreter (1.31%); T1082 System Information Discovery (0.25%) | 97.20% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.08%); T1124 System Time Discovery (0.20%); T1210 Exploitation of Remote Services (0.14%) | 98.08% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (90.56%); T1078 Valid Accounts (1.75%); T1039 Data from Network Shared Drive (1.55%) | 90.56% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (39.51%); T1105 Ingress Tool Transfer (9.73%); T1222 File and Directory Permissions Modification (8.83%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (26.37%); T1222 File and Directory Permissions Modification (15.14%); T1614 System Location Discovery (10.93%) | 0.08% | False |

## real_50 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.01%); T1595 Active Scanning (0.31%); T1110 Brute Force (0.29%) | 97.01% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.02%); T1548 Abuse Elevation Control Mechanism (1.08%); T1070 Indicator Removal (0.30%) | 97.02% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.27%); T1201 Password Policy Discovery (0.15%); T1518 Software Discovery (0.10%) | 98.27% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.31%); T1190 Exploit Public-Facing Application (0.61%); T1589 Gather Victim Identity Information (0.23%) | 98.31% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (37.07%); T1218 System Binary Proxy Execution (15.75%); T1201 Password Policy Discovery (7.01%) | 0.06% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (92.51%); T1059 Command and Scripting Interpreter (5.58%); T1218 System Binary Proxy Execution (0.12%) | 92.51% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.12%); T1124 System Time Discovery (0.28%); T1485 Data Destruction (0.13%) | 97.12% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (89.11%); T1039 Data from Network Shared Drive (2.06%); T1564 Hide Artifacts (0.57%) | 89.11% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (43.12%); T1082 System Information Discovery (15.14%); T1078 Valid Accounts (5.83%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (63.27%); T1003 OS Credential Dumping (9.75%); T1566 Phishing (6.06%) | 0.08% | False |

## real_50 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.56%); T1071 Application Layer Protocol (0.30%); T1557 Adversary-in-the-Middle (0.19%) | 97.56% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.28%); T1548 Abuse Elevation Control Mechanism (0.68%); T1190 Exploit Public-Facing Application (0.08%) | 98.28% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.02%); T1057 Process Discovery (0.20%); T1485 Data Destruction (0.15%) | 98.02% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.29%); T1190 Exploit Public-Facing Application (0.47%); T1589 Gather Victim Identity Information (0.16%) | 98.29% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1078 Valid Accounts (20.37%); T1120 Peripheral Device Discovery (12.23%); T1071 Application Layer Protocol (11.43%) | 0.07% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.57%); T1059 Command and Scripting Interpreter (2.25%); T1124 System Time Discovery (0.16%) | 95.57% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.89%); T1124 System Time Discovery (0.16%); T1525 Implant Internal Image (0.14%) | 97.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (93.89%); T1039 Data from Network Shared Drive (0.69%); T1041 Exfiltration Over C2 Channel (0.47%) | 93.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (58.73%); T1222 File and Directory Permissions Modification (10.18%); T1003 OS Credential Dumping (3.49%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (41.95%); T1222 File and Directory Permissions Modification (24.81%); T1033 System Owner/User Discovery (5.98%) | 0.17% | False |

## real_50 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.55%); T1105 Ingress Tool Transfer (0.15%); T1557 Adversary-in-the-Middle (0.13%) | 98.55% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (67.12%); T1548 Abuse Elevation Control Mechanism (22.45%); T1136 Create Account (1.50%) | 67.12% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.14%); T1201 Password Policy Discovery (0.20%); T1057 Process Discovery (0.16%) | 98.14% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.21%); T1190 Exploit Public-Facing Application (0.68%); T1592 Gather Victim Host Information (0.41%) | 97.21% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1615 Group Policy Discovery (12.18%); T1083 File and Directory Discovery (10.90%); T1018 Remote System Discovery (10.60%) | 0.41% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (93.62%); T1059 Command and Scripting Interpreter (3.65%); T1486 Data Encrypted for Impact (0.30%) | 93.62% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.33%); T1124 System Time Discovery (0.27%); T1041 Exfiltration Over C2 Channel (0.10%) | 98.33% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.66%); T1039 Data from Network Shared Drive (1.41%); T1041 Exfiltration Over C2 Channel (0.79%) | 92.66% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1039 Data from Network Shared Drive (46.26%); T1222 File and Directory Permissions Modification (5.57%); T1218 System Binary Proxy Execution (5.03%) | 0.31% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (52.99%); T1039 Data from Network Shared Drive (11.36%); T1083 File and Directory Discovery (6.03%) | 0.34% | False |

## real_50 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (96.88%); T1595 Active Scanning (0.54%); T1589 Gather Victim Identity Information (0.18%) | 96.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.18%); T1548 Abuse Elevation Control Mechanism (0.91%); T1574 Hijack Execution Flow (0.30%) | 97.18% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.51%); T1057 Process Discovery (0.27%); T1486 Data Encrypted for Impact (0.18%) | 97.51% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.35%); T1190 Exploit Public-Facing Application (0.33%); T1589 Gather Victim Identity Information (0.17%) | 98.35% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.24%); T1059 Command and Scripting Interpreter (1.23%); T1573 Encrypted Channel (0.19%) | 96.24% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (93.85%); T1059 Command and Scripting Interpreter (3.44%); T1083 File and Directory Discovery (0.32%) | 93.85% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.87%); T1059 Command and Scripting Interpreter (0.32%); T1124 System Time Discovery (0.31%) | 96.87% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (93.38%); T1039 Data from Network Shared Drive (1.22%); T1070 Indicator Removal (0.54%) | 93.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (46.49%); T1120 Peripheral Device Discovery (12.88%); T1059 Command and Scripting Interpreter (4.30%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (27.98%); T1486 Data Encrypted for Impact (16.38%); T1120 Peripheral Device Discovery (11.45%) | 0.26% | False |

## real_50 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.32%); T1083 File and Directory Discovery (0.46%); T1078 Valid Accounts (0.15%) | 97.32% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (83.35%); T1548 Abuse Elevation Control Mechanism (11.56%); T1036 Masquerading (0.41%) | 83.35% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.61%); T1201 Password Policy Discovery (0.25%); T1057 Process Discovery (0.18%) | 97.61% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.89%); T1589 Gather Victim Identity Information (0.45%); T1190 Exploit Public-Facing Application (0.38%) | 97.89% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.34%); T1059 Command and Scripting Interpreter (0.62%); T1547 Boot or Logon Autostart Execution (0.22%) | 97.34% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (90.52%); T1059 Command and Scripting Interpreter (7.13%); T1136 Create Account (0.21%) | 90.52% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.34%); T1213 Data from Information Repositories (0.21%); T1059 Command and Scripting Interpreter (0.20%) | 97.34% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (90.15%); T1573 Encrypted Channel (1.84%); T1039 Data from Network Shared Drive (0.60%) | 90.15% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (9.09%); T1049 System Network Connections Discovery (6.03%); T1082 System Information Discovery (5.17%) | 0.81% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1213 Data from Information Repositories (14.96%); T1565 Data Manipulation (13.94%); T1059 Command and Scripting Interpreter (8.97%) | 1.65% | False |

## real_50 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (97.44%); T1110 Brute Force (0.38%); T1589 Gather Victim Identity Information (0.19%) | 97.44% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.60%); T1548 Abuse Elevation Control Mechanism (1.89%); T1546 Event Triggered Execution (0.83%) | 93.60% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.90%); T1528 Steal Application Access Token (0.19%); T1201 Password Policy Discovery (0.15%) | 97.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.24%); T1190 Exploit Public-Facing Application (0.57%); T1589 Gather Victim Identity Information (0.11%) | 98.24% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.20%); T1059 Command and Scripting Interpreter (1.53%); T1046 Network Service Scanning (0.22%) | 96.20% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.49%); T1083 File and Directory Discovery (0.36%); T1059 Command and Scripting Interpreter (0.33%) | 97.49% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.93%); T1124 System Time Discovery (0.15%); T1071 Application Layer Protocol (0.15%) | 97.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (90.21%); T1039 Data from Network Shared Drive (2.16%); T1041 Exfiltration Over C2 Channel (1.32%) | 90.21% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (20.72%); T1082 System Information Discovery (16.32%); T1018 Remote System Discovery (4.52%) | 0.55% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1531 Account Access Removal (10.60%); T1110 Brute Force (9.49%); T1082 System Information Discovery (7.15%) | 0.19% | False |

## real_50 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.66%); T1592 Gather Victim Host Information (0.21%); T1589 Gather Victim Identity Information (0.13%) | 98.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (83.89%); T1548 Abuse Elevation Control Mechanism (12.17%); T1105 Ingress Tool Transfer (0.26%) | 83.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.07%); T1053 Scheduled Task/Job (0.20%); T1082 System Information Discovery (0.12%) | 98.07% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.21%); T1190 Exploit Public-Facing Application (0.74%); T1589 Gather Victim Identity Information (0.24%) | 98.21% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (56.56%); T1033 System Owner/User Discovery (22.26%); T1003 OS Credential Dumping (6.37%) | 0.02% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (92.41%); T1059 Command and Scripting Interpreter (5.52%); T1083 File and Directory Discovery (0.45%) | 92.41% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.03%); T1136 Create Account (0.16%); T1124 System Time Discovery (0.15%) | 98.03% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.04%); T1039 Data from Network Shared Drive (0.98%); T1565 Data Manipulation (0.33%) | 95.04% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (17.10%); T1071 Application Layer Protocol (17.08%); T1082 System Information Discovery (16.68%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1219 Remote Access Tools (30.17%); T1566 Phishing (8.57%); T1070 Indicator Removal (8.37%) | 0.03% | False |

## real_50 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.06%); T1557 Adversary-in-the-Middle (0.15%); T1589 Gather Victim Identity Information (0.14%) | 98.06% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (93.74%); T1548 Abuse Elevation Control Mechanism (3.59%); T1136 Create Account (0.44%) | 93.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.12%); T1201 Password Policy Discovery (0.19%); T1057 Process Discovery (0.18%) | 98.12% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.92%); T1190 Exploit Public-Facing Application (0.93%); T1589 Gather Victim Identity Information (0.18%) | 97.92% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (94.63%); T1059 Command and Scripting Interpreter (2.58%); T1087 Account Discovery (0.32%) | 94.63% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.77%); T1059 Command and Scripting Interpreter (3.89%); T1053 Scheduled Task/Job (0.08%) | 94.77% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.08%); T1518 Software Discovery (0.46%); T1124 System Time Discovery (0.22%) | 97.08% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (93.07%); T1039 Data from Network Shared Drive (1.36%); T1041 Exfiltration Over C2 Channel (0.52%) | 93.07% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (23.04%); T1033 System Owner/User Discovery (21.47%); T1059 Command and Scripting Interpreter (14.51%) | 0.18% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (68.85%); T1059 Command and Scripting Interpreter (10.48%); T1041 Exfiltration Over C2 Channel (4.31%) | 0.25% | False |

## real_50 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.22%); T1005 Data from Local System (0.24%); T1543 Create or Modify System Process (0.17%) | 98.22% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1219 Remote Access Tools (27.92%); T1033 System Owner/User Discovery (21.45%); T1036 Masquerading (16.37%) | 21.45% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.17%); T1018 Remote System Discovery (0.23%); T1057 Process Discovery (0.14%) | 98.17% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.77%); T1190 Exploit Public-Facing Application (0.61%); T1589 Gather Victim Identity Information (0.23%) | 97.77% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (88.06%); T1021 Remote Services (3.11%); T1486 Data Encrypted for Impact (1.41%) | 0.05% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (94.42%); T1059 Command and Scripting Interpreter (4.30%); T1033 System Owner/User Discovery (0.13%) | 94.42% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.82%); T1124 System Time Discovery (0.27%); T1485 Data Destruction (0.19%) | 97.82% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.26%); T1039 Data from Network Shared Drive (0.69%); T1033 System Owner/User Discovery (0.45%) | 94.26% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1219 Remote Access Tools (38.31%); T1105 Ingress Tool Transfer (9.35%); T1083 File and Directory Discovery (6.49%) | 0.23% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1525 Implant Internal Image (12.35%); T1219 Remote Access Tools (11.85%); T1010 Application Window Discovery (5.91%) | 0.44% | False |

## real_50 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.85%); T1528 Steal Application Access Token (0.06%); T1033 System Owner/User Discovery (0.05%) | 98.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (79.13%); T1033 System Owner/User Discovery (14.98%); T1036 Masquerading (0.86%) | 14.98% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.66%); T1039 Data from Network Shared Drive (0.23%); T1053 Scheduled Task/Job (0.16%) | 98.66% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (50.81%); T1190 Exploit Public-Facing Application (47.49%); T1573 Encrypted Channel (0.13%) | 50.81% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1016 System Network Configuration Discovery (55.16%); T1033 System Owner/User Discovery (17.94%); T1003 OS Credential Dumping (6.65%) | 0.03% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (56.32%); T1087 Account Discovery (42.22%); T1083 File and Directory Discovery (0.26%) | 42.22% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (96.90%); T1201 Password Policy Discovery (0.31%); T1082 System Information Discovery (0.25%) | 96.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.12%); T1486 Data Encrypted for Impact (1.02%); T1039 Data from Network Shared Drive (0.85%) | 94.12% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (83.33%); T1059 Command and Scripting Interpreter (11.17%); T1222 File and Directory Permissions Modification (0.99%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (89.75%); T1105 Ingress Tool Transfer (2.33%); T1574 Hijack Execution Flow (1.64%) | 0.05% | False |

## real_50 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.48%); T1592 Gather Victim Host Information (0.14%); T1595 Active Scanning (0.13%) | 98.48% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (75.88%); T1548 Abuse Elevation Control Mechanism (20.14%); T1036 Masquerading (0.74%) | 75.88% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.97%); T1021 Remote Services (0.33%); T1083 File and Directory Discovery (0.20%) | 97.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (63.79%); T1190 Exploit Public-Facing Application (33.50%); T1592 Gather Victim Host Information (0.97%) | 63.79% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1543 Create or Modify System Process (33.17%); T1033 System Owner/User Discovery (23.03%); T1070 Indicator Removal (10.42%) | 0.13% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (77.82%); T1087 Account Discovery (20.77%); T1053 Scheduled Task/Job (0.30%) | 20.77% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.20%); T1016 System Network Configuration Discovery (0.18%); T1610 Deploy Container (0.09%) | 98.20% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (90.61%); T1120 Peripheral Device Discovery (1.63%); T1041 Exfiltration Over C2 Channel (0.72%) | 90.61% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (53.55%); T1105 Ingress Tool Transfer (6.95%); T1071 Application Layer Protocol (5.71%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (19.19%); T1222 File and Directory Permissions Modification (8.64%); T1059 Command and Scripting Interpreter (7.01%) | 0.77% | False |

## real_50 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.52%); T1071 Application Layer Protocol (0.19%); T1070 Indicator Removal (0.13%) | 98.52% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (74.94%); T1548 Abuse Elevation Control Mechanism (21.45%); T1592 Gather Victim Host Information (0.33%) | 74.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.26%); T1531 Account Access Removal (0.11%); T1124 System Time Discovery (0.10%) | 98.26% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (52.60%); T1190 Exploit Public-Facing Application (44.27%); T1592 Gather Victim Host Information (0.67%) | 52.60% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1136 Create Account (17.79%); T1059 Command and Scripting Interpreter (13.34%); T1046 Network Service Scanning (5.43%) | 0.15% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (50.80%); T1059 Command and Scripting Interpreter (46.89%); T1082 System Information Discovery (0.34%) | 50.80% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (83.43%); T1204 User Execution (2.41%); T1083 File and Directory Discovery (1.39%) | 83.43% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (88.52%); T1021 Remote Services (2.42%); T1049 System Network Connections Discovery (1.14%) | 88.52% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (42.25%); T1070 Indicator Removal (12.69%); T1053 Scheduled Task/Job (8.80%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (44.24%); T1564 Hide Artifacts (36.09%); T1105 Ingress Tool Transfer (6.41%) | 0.19% | False |

## real_50 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.75%); T1566 Phishing (0.09%); T1595 Active Scanning (0.08%) | 98.75% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (46.15%); T1033 System Owner/User Discovery (41.02%); T1070 Indicator Removal (2.82%) | 41.02% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.60%); T1003 OS Credential Dumping (0.15%); T1083 File and Directory Discovery (0.13%) | 98.60% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (51.32%); T1190 Exploit Public-Facing Application (46.22%); T1589 Gather Victim Identity Information (0.29%) | 51.32% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1033 System Owner/User Discovery (89.53%); T1059 Command and Scripting Interpreter (3.84%); T1218 System Binary Proxy Execution (0.81%) | 0.00% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.65%); T1087 Account Discovery (19.75%); T1082 System Information Discovery (0.29%) | 19.75% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.52%); T1525 Implant Internal Image (0.21%); T1518 Software Discovery (0.21%) | 97.52% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (91.15%); T1564 Hide Artifacts (1.57%); T1041 Exfiltration Over C2 Channel (0.69%) | 91.15% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (17.38%); T1589 Gather Victim Identity Information (11.53%); T1218 System Binary Proxy Execution (6.41%) | 0.30% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (16.19%); T1010 Application Window Discovery (9.53%); T1016 System Network Configuration Discovery (8.35%) | 1.07% | False |

## real_50 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.50%); T1592 Gather Victim Host Information (0.12%); T1610 Deploy Container (0.11%) | 98.50% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (87.27%); T1548 Abuse Elevation Control Mechanism (6.69%); T1105 Ingress Tool Transfer (2.30%) | 87.27% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.44%); T1078 Valid Accounts (0.24%); T1105 Ingress Tool Transfer (0.11%) | 98.44% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (52.64%); T1190 Exploit Public-Facing Application (45.38%); T1592 Gather Victim Host Information (0.34%) | 52.64% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.34%); T1218 System Binary Proxy Execution (0.31%); T1105 Ingress Tool Transfer (0.14%) | 98.34% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (87.73%); T1087 Account Discovery (11.43%); T1053 Scheduled Task/Job (0.16%) | 11.43% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (93.69%); T1016 System Network Configuration Discovery (2.21%); T1083 File and Directory Discovery (0.36%) | 93.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.19%); T1049 System Network Connections Discovery (1.36%); T1021 Remote Services (1.08%) | 92.19% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (12.55%); T1105 Ingress Tool Transfer (11.71%); T1531 Account Access Removal (8.41%) | 0.15% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (51.25%); T1564 Hide Artifacts (26.97%); T1053 Scheduled Task/Job (4.22%) | 0.21% | False |

## real_50 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.62%); T1082 System Information Discovery (0.19%); T1021 Remote Services (0.07%) | 98.62% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (58.21%); T1548 Abuse Elevation Control Mechanism (32.42%); T1105 Ingress Tool Transfer (2.40%) | 58.21% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.22%); T1564 Hide Artifacts (0.12%); T1592 Gather Victim Host Information (0.11%) | 98.22% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (65.21%); T1190 Exploit Public-Facing Application (31.34%); T1592 Gather Victim Host Information (0.96%) | 65.21% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.91%); T1059 Command and Scripting Interpreter (1.04%); T1087 Account Discovery (0.08%) | 97.91% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (76.64%); T1087 Account Discovery (22.25%); T1095 Non-Application Layer Protocol (0.14%) | 22.25% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.90%); T1070 Indicator Removal (0.26%); T1078 Valid Accounts (0.23%) | 97.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (92.85%); T1049 System Network Connections Discovery (0.68%); T1071 Application Layer Protocol (0.48%) | 92.85% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (16.90%); T1591 Gather Victim Org Information (6.32%); T1124 System Time Discovery (5.82%) | 1.26% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1592 Gather Victim Host Information (22.42%); T1564 Hide Artifacts (14.23%); T1222 File and Directory Permissions Modification (7.65%) | 0.07% | False |

## real_50 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.96%); T1110 Brute Force (0.09%); T1610 Deploy Container (0.06%) | 98.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (81.75%); T1548 Abuse Elevation Control Mechanism (11.07%); T1036 Masquerading (1.12%) | 81.75% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (97.77%); T1049 System Network Connections Discovery (0.31%); T1115 Clipboard Data (0.12%) | 97.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (58.72%); T1190 Exploit Public-Facing Application (37.73%); T1592 Gather Victim Host Information (1.20%) | 58.72% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.86%); T1105 Ingress Tool Transfer (0.29%); T1218 System Binary Proxy Execution (0.28%) | 97.86% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (73.57%); T1087 Account Discovery (25.38%); T1083 File and Directory Discovery (0.14%) | 25.38% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.85%); T1120 Peripheral Device Discovery (0.33%); T1124 System Time Discovery (0.19%) | 97.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (89.43%); T1041 Exfiltration Over C2 Channel (1.17%); T1569 System Services (0.91%) | 89.43% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (30.25%); T1564 Hide Artifacts (18.87%); T1219 Remote Access Tools (12.58%) | 0.12% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (47.56%); T1071 Application Layer Protocol (14.69%); T1222 File and Directory Permissions Modification (9.62%) | 0.66% | False |

## real_50 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.61%); T1592 Gather Victim Host Information (0.30%); T1573 Encrypted Channel (0.11%) | 98.61% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (92.86%); T1548 Abuse Elevation Control Mechanism (4.29%); T1036 Masquerading (0.51%) | 92.86% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.12%); T1082 System Information Discovery (0.28%); T1518 Software Discovery (0.18%) | 98.12% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (69.43%); T1190 Exploit Public-Facing Application (28.64%); T1592 Gather Victim Host Information (0.24%) | 69.43% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1098 Account Manipulation (18.80%); T1556 Modify Authentication Process (13.33%); T1046 Network Service Scanning (8.16%) | 0.33% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (79.67%); T1087 Account Discovery (19.51%); T1486 Data Encrypted for Impact (0.10%) | 19.51% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.09%); T1489 Service Stop (0.23%); T1049 System Network Connections Discovery (0.15%) | 98.09% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.63%); T1049 System Network Connections Discovery (0.47%); T1614 System Location Discovery (0.46%) | 95.63% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1485 Data Destruction (16.29%); T1115 Clipboard Data (11.99%); T1219 Remote Access Tools (10.61%) | 0.27% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (53.41%); T1219 Remote Access Tools (14.79%); T1531 Account Access Removal (6.03%) | 0.69% | False |

## real_50 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.91%); T1018 Remote System Discovery (0.10%); T1595 Active Scanning (0.07%) | 98.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (51.74%); T1033 System Owner/User Discovery (34.46%); T1078 Valid Accounts (2.26%) | 34.46% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.31%); T1007 System Service Discovery (0.17%); T1614 System Location Discovery (0.15%) | 98.31% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (52.40%); T1190 Exploit Public-Facing Application (45.38%); T1592 Gather Victim Host Information (0.27%) | 52.40% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.36%); T1222 File and Directory Permissions Modification (0.23%); T1564 Hide Artifacts (0.15%) | 98.36% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (83.62%); T1087 Account Discovery (15.54%); T1105 Ingress Tool Transfer (0.08%) | 15.54% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.94%); T1518 Software Discovery (0.26%); T1190 Exploit Public-Facing Application (0.16%) | 97.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (91.41%); T1041 Exfiltration Over C2 Channel (1.08%); T1049 System Network Connections Discovery (0.65%) | 91.41% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (60.71%); T1057 Process Discovery (4.13%); T1098 Account Manipulation (2.19%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (53.45%); T1564 Hide Artifacts (10.26%); T1033 System Owner/User Discovery (4.54%) | 0.56% | False |

## real_50 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.77%); T1543 Create or Modify System Process (0.20%); T1592 Gather Victim Host Information (0.06%) | 98.77% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1548 Abuse Elevation Control Mechanism (23.94%); T1033 System Owner/User Discovery (14.64%); T1105 Ingress Tool Transfer (9.54%) | 14.64% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (98.86%); T1557 Adversary-in-the-Middle (0.11%); T1190 Exploit Public-Facing Application (0.08%) | 98.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (61.48%); T1595 Active Scanning (35.81%); T1592 Gather Victim Host Information (0.56%) | 35.81% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (90.82%); T1078 Valid Accounts (2.82%); T1016 System Network Configuration Discovery (2.80%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (89.51%); T1087 Account Discovery (9.83%); T1053 Scheduled Task/Job (0.07%) | 9.83% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.53%); T1057 Process Discovery (0.23%); T1071 Application Layer Protocol (0.14%) | 97.53% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.23%); T1041 Exfiltration Over C2 Channel (0.80%); T1201 Password Policy Discovery (0.48%) | 94.23% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (76.75%); T1574 Hijack Execution Flow (3.18%); T1485 Data Destruction (2.18%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1018 Remote System Discovery (15.56%); T1222 File and Directory Permissions Modification (13.18%); T1210 Exploitation of Remote Services (8.39%) | 0.12% | False |

## real_75 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.44%); T1213 Data from Information Repositories (0.07%); T1589 Gather Victim Identity Information (0.03%) | 99.44% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.15%); T1036 Masquerading (0.52%); T1548 Abuse Elevation Control Mechanism (0.08%) | 99.15% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.42%); T1018 Remote System Discovery (0.07%); T1057 Process Discovery (0.06%) | 99.42% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.33%); T1190 Exploit Public-Facing Application (0.36%); T1589 Gather Victim Identity Information (0.04%) | 99.33% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1078 Valid Accounts (21.46%); T1021 Remote Services (15.69%); T1547 Boot or Logon Autostart Execution (12.31%) | 0.11% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.58%); T1059 Command and Scripting Interpreter (0.03%); T1219 Remote Access Tools (0.02%) | 99.58% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.22%); T1124 System Time Discovery (0.19%); T1201 Password Policy Discovery (0.06%) | 99.22% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.93%); T1591 Gather Victim Org Information (0.24%); T1039 Data from Network Shared Drive (0.20%) | 97.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (44.89%); T1595 Active Scanning (8.23%); T1548 Abuse Elevation Control Mechanism (7.73%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (46.78%); T1105 Ingress Tool Transfer (15.96%); T1071 Application Layer Protocol (7.96%) | 0.01% | False |

## real_75 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.29%); T1595 Active Scanning (0.11%); T1059 Command and Scripting Interpreter (0.07%) | 99.29% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.47%); T1548 Abuse Elevation Control Mechanism (0.98%); T1105 Ingress Tool Transfer (0.32%) | 97.47% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.45%); T1057 Process Discovery (0.06%); T1083 File and Directory Discovery (0.04%) | 99.45% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.44%); T1190 Exploit Public-Facing Application (0.22%); T1589 Gather Victim Identity Information (0.05%) | 99.44% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (93.25%); T1205 Traffic Signaling (1.81%); T1059 Command and Scripting Interpreter (1.10%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.05%); T1059 Command and Scripting Interpreter (0.37%); T1591 Gather Victim Org Information (0.06%) | 99.05% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.10%); T1124 System Time Discovery (0.16%); T1072 Software Deployment Tools (0.06%) | 99.10% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.31%); T1120 Peripheral Device Discovery (0.75%); T1039 Data from Network Shared Drive (0.74%) | 96.31% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (62.70%); T1591 Gather Victim Org Information (11.98%); T1082 System Information Discovery (3.67%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (31.51%); T1564 Hide Artifacts (23.26%); T1105 Ingress Tool Transfer (14.89%) | 0.83% | False |

## real_75 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.35%); T1218 System Binary Proxy Execution (0.08%); T1082 System Information Discovery (0.04%) | 99.35% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.04%); T1548 Abuse Elevation Control Mechanism (0.47%); T1082 System Information Discovery (0.07%) | 99.04% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.34%); T1057 Process Discovery (0.13%); T1219 Remote Access Tools (0.07%) | 99.34% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.42%); T1190 Exploit Public-Facing Application (0.25%); T1589 Gather Victim Identity Information (0.04%) | 99.42% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.13%); T1059 Command and Scripting Interpreter (0.86%); T1071 Application Layer Protocol (0.14%) | 98.13% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.35%); T1059 Command and Scripting Interpreter (12.76%); T1599 Network Boundary Bridging (0.10%) | 86.35% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.93%); T1124 System Time Discovery (0.11%); T1599 Network Boundary Bridging (0.10%) | 98.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.53%); T1039 Data from Network Shared Drive (0.18%); T1201 Password Policy Discovery (0.13%) | 98.53% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (63.55%); T1222 File and Directory Permissions Modification (21.04%); T1033 System Owner/User Discovery (3.75%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1070 Indicator Removal (36.95%); T1222 File and Directory Permissions Modification (22.18%); T1003 OS Credential Dumping (20.50%) | 0.23% | False |

## real_75 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.48%); T1007 System Service Discovery (0.03%); T1218 System Binary Proxy Execution (0.03%) | 99.48% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.16%); T1036 Masquerading (0.17%); T1548 Abuse Elevation Control Mechanism (0.17%) | 99.16% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.43%); T1057 Process Discovery (0.07%); T1543 Create or Modify System Process (0.04%) | 99.43% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.11%); T1190 Exploit Public-Facing Application (0.32%); T1589 Gather Victim Identity Information (0.18%) | 99.11% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (89.25%); T1059 Command and Scripting Interpreter (8.03%); T1547 Boot or Logon Autostart Execution (0.42%) | 89.25% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (87.12%); T1059 Command and Scripting Interpreter (11.88%); T1082 System Information Discovery (0.21%) | 87.12% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.26%); T1124 System Time Discovery (0.15%); T1046 Network Service Scanning (0.04%) | 99.26% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.92%); T1120 Peripheral Device Discovery (0.21%); T1039 Data from Network Shared Drive (0.19%) | 97.92% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (39.24%); T1078 Valid Accounts (18.69%); T1222 File and Directory Permissions Modification (7.85%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (31.88%); T1543 Create or Modify System Process (11.17%); T1033 System Owner/User Discovery (8.83%) | 0.04% | False |

## real_75 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.39%); T1543 Create or Modify System Process (0.05%); T1595 Active Scanning (0.05%) | 99.39% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.15%); T1548 Abuse Elevation Control Mechanism (0.42%); T1205 Traffic Signaling (0.09%) | 99.15% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.21%); T1057 Process Discovery (0.23%); T1201 Password Policy Discovery (0.11%) | 99.21% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.52%); T1190 Exploit Public-Facing Application (0.17%); T1589 Gather Victim Identity Information (0.07%) | 99.52% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.99%); T1059 Command and Scripting Interpreter (0.23%); T1547 Boot or Logon Autostart Execution (0.09%) | 98.99% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (51.13%); T1059 Command and Scripting Interpreter (47.95%); T1083 File and Directory Discovery (0.11%) | 51.13% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.10%); T1124 System Time Discovery (0.14%); T1489 Service Stop (0.06%) | 99.10% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.70%); T1039 Data from Network Shared Drive (0.67%); T1018 Remote System Discovery (0.11%) | 97.70% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (30.08%); T1071 Application Layer Protocol (18.91%); T1072 Software Deployment Tools (9.16%) | 0.75% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (29.35%); T1003 OS Credential Dumping (17.63%); T1041 Exfiltration Over C2 Channel (7.55%) | 0.01% | False |

## real_75 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.25%); T1083 File and Directory Discovery (0.09%); T1531 Account Access Removal (0.06%) | 99.25% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.64%); T1548 Abuse Elevation Control Mechanism (0.42%); T1105 Ingress Tool Transfer (0.21%) | 98.64% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.18%); T1219 Remote Access Tools (0.09%); T1201 Password Policy Discovery (0.09%) | 99.18% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.43%); T1190 Exploit Public-Facing Application (0.24%); T1589 Gather Victim Identity Information (0.09%) | 99.43% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.57%); T1059 Command and Scripting Interpreter (0.48%); T1547 Boot or Logon Autostart Execution (0.11%) | 98.57% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (86.88%); T1059 Command and Scripting Interpreter (12.30%); T1486 Data Encrypted for Impact (0.14%) | 86.88% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.74%); T1072 Software Deployment Tools (0.23%); T1059 Command and Scripting Interpreter (0.22%) | 98.74% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.02%); T1039 Data from Network Shared Drive (0.54%); T1573 Encrypted Channel (0.19%) | 98.02% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (19.70%); T1083 File and Directory Discovery (12.83%); T1574 Hijack Execution Flow (10.37%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (35.52%); T1574 Hijack Execution Flow (14.35%); T1083 File and Directory Discovery (12.41%) | 0.01% | False |

## real_75 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.49%); T1589 Gather Victim Identity Information (0.06%); T1595 Active Scanning (0.03%) | 99.49% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.14%); T1548 Abuse Elevation Control Mechanism (0.45%); T1105 Ingress Tool Transfer (0.04%) | 99.14% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.27%); T1528 Steal Application Access Token (0.08%); T1046 Network Service Scanning (0.07%) | 99.27% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.46%); T1190 Exploit Public-Facing Application (0.18%); T1589 Gather Victim Identity Information (0.05%) | 99.46% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.17%); T1059 Command and Scripting Interpreter (0.84%); T1083 File and Directory Discovery (0.14%) | 98.17% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.27%); T1059 Command and Scripting Interpreter (0.40%); T1083 File and Directory Discovery (0.09%) | 99.27% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.06%); T1124 System Time Discovery (0.12%); T1565 Data Manipulation (0.06%) | 99.06% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.38%); T1120 Peripheral Device Discovery (1.61%); T1039 Data from Network Shared Drive (0.99%) | 95.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (48.75%); T1053 Scheduled Task/Job (10.26%); T1105 Ingress Tool Transfer (8.01%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (49.27%); T1595 Active Scanning (6.84%); T1557 Adversary-in-the-Middle (5.96%) | 0.01% | False |

## real_75 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.30%); T1201 Password Policy Discovery (0.05%); T1592 Gather Victim Host Information (0.05%) | 99.30% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.35%); T1548 Abuse Elevation Control Mechanism (0.26%); T1105 Ingress Tool Transfer (0.07%) | 99.35% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.30%); T1053 Scheduled Task/Job (0.11%); T1003 OS Credential Dumping (0.08%) | 99.30% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.51%); T1190 Exploit Public-Facing Application (0.17%); T1589 Gather Victim Identity Information (0.09%) | 99.51% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (95.72%); T1078 Valid Accounts (1.73%); T1547 Boot or Logon Autostart Execution (0.55%) | 0.00% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.16%); T1222 File and Directory Permissions Modification (0.11%); T1083 File and Directory Discovery (0.08%) | 99.16% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.97%); T1566 Phishing (0.13%); T1124 System Time Discovery (0.11%) | 98.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.42%); T1039 Data from Network Shared Drive (0.65%); T1564 Hide Artifacts (0.20%) | 97.42% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1497 Virtualization/Sandbox Evasion (30.04%); T1564 Hide Artifacts (14.58%); T1222 File and Directory Permissions Modification (10.99%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (46.29%); T1222 File and Directory Permissions Modification (19.50%); T1078 Valid Accounts (5.77%) | 0.11% | False |

## real_75 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.42%); T1595 Active Scanning (0.06%); T1564 Hide Artifacts (0.04%) | 99.42% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.24%); T1548 Abuse Elevation Control Mechanism (0.23%); T1547 Boot or Logon Autostart Execution (0.07%) | 99.24% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.48%); T1201 Password Policy Discovery (0.05%); T1036 Masquerading (0.04%) | 99.48% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.46%); T1190 Exploit Public-Facing Application (0.13%); T1589 Gather Victim Identity Information (0.12%) | 99.46% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.54%); T1059 Command and Scripting Interpreter (2.39%); T1547 Boot or Logon Autostart Execution (0.24%) | 95.54% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (79.97%); T1059 Command and Scripting Interpreter (19.34%); T1033 System Owner/User Discovery (0.07%) | 79.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.78%); T1110 Brute Force (0.11%); T1124 System Time Discovery (0.11%) | 98.78% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.10%); T1039 Data from Network Shared Drive (0.83%); T1057 Process Discovery (0.42%) | 95.10% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (28.53%); T1222 File and Directory Permissions Modification (15.84%); T1204 User Execution (10.28%) | 0.22% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (45.61%); T1566 Phishing (8.57%); T1021 Remote Services (6.87%) | 0.01% | False |

## real_75 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.48%); T1018 Remote System Discovery (0.04%); T1005 Data from Local System (0.03%) | 99.48% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.94%); T1548 Abuse Elevation Control Mechanism (1.84%); T1036 Masquerading (0.44%) | 95.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.16%); T1057 Process Discovery (0.10%); T1003 OS Credential Dumping (0.05%) | 99.16% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.28%); T1190 Exploit Public-Facing Application (0.35%); T1589 Gather Victim Identity Information (0.09%) | 99.28% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1087 Account Discovery (31.39%); T1110 Brute Force (12.89%); T1548 Abuse Elevation Control Mechanism (10.72%) | 0.09% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.14%); T1059 Command and Scripting Interpreter (0.17%); T1083 File and Directory Discovery (0.08%) | 99.14% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.12%); T1560 Archive Collected Data (0.06%); T1124 System Time Discovery (0.05%) | 99.12% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.97%); T1039 Data from Network Shared Drive (0.28%); T1083 File and Directory Discovery (0.24%) | 97.97% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (10.63%); T1219 Remote Access Tools (10.46%); T1595 Active Scanning (10.35%) | 0.42% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (51.19%); T1057 Process Discovery (6.19%); T1218 System Binary Proxy Execution (5.06%) | 0.01% | False |

## real_75 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.00%); T1595 Active Scanning (0.12%); T1589 Gather Victim Identity Information (0.07%) | 99.00% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.85%); T1548 Abuse Elevation Control Mechanism (0.94%); T1036 Masquerading (0.71%) | 97.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.38%); T1518 Software Discovery (0.09%); T1543 Create or Modify System Process (0.07%) | 99.38% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.39%); T1190 Exploit Public-Facing Application (0.28%); T1589 Gather Victim Identity Information (0.03%) | 99.39% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1003 OS Credential Dumping (29.03%); T1021 Remote Services (7.60%); T1120 Peripheral Device Discovery (7.54%) | 0.55% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.30%); T1059 Command and Scripting Interpreter (0.29%); T1082 System Information Discovery (0.06%) | 99.30% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.39%); T1124 System Time Discovery (0.06%); T1210 Exploitation of Remote Services (0.05%) | 99.39% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.33%); T1039 Data from Network Shared Drive (0.88%); T1078 Valid Accounts (0.35%) | 96.33% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (45.35%); T1222 File and Directory Permissions Modification (8.18%); T1087 Account Discovery (4.39%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1614 System Location Discovery (17.83%); T1564 Hide Artifacts (14.96%); T1033 System Owner/User Discovery (12.58%) | 0.08% | False |

## real_75 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.92%); T1110 Brute Force (0.14%); T1595 Active Scanning (0.12%) | 98.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.69%); T1548 Abuse Elevation Control Mechanism (0.90%); T1036 Masquerading (0.24%) | 97.69% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.34%); T1201 Password Policy Discovery (0.06%); T1057 Process Discovery (0.04%) | 99.34% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.10%); T1190 Exploit Public-Facing Application (0.42%); T1589 Gather Victim Identity Information (0.14%) | 99.10% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1218 System Binary Proxy Execution (24.59%); T1556 Modify Authentication Process (17.61%); T1136 Create Account (12.48%) | 0.07% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.79%); T1059 Command and Scripting Interpreter (3.11%); T1218 System Binary Proxy Execution (0.15%) | 95.79% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.00%); T1124 System Time Discovery (0.18%); T1072 Software Deployment Tools (0.13%) | 99.00% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.48%); T1039 Data from Network Shared Drive (0.64%); T1078 Valid Accounts (0.31%) | 96.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (35.64%); T1105 Ingress Tool Transfer (29.35%); T1078 Valid Accounts (8.57%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (45.09%); T1566 Phishing (22.17%); T1003 OS Credential Dumping (7.01%) | 0.11% | False |

## real_75 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.07%); T1204 User Execution (0.07%); T1071 Application Layer Protocol (0.07%) | 99.07% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.55%); T1548 Abuse Elevation Control Mechanism (1.37%); T1136 Create Account (0.12%) | 97.55% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.35%); T1057 Process Discovery (0.08%); T1485 Data Destruction (0.05%) | 99.35% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.17%); T1190 Exploit Public-Facing Application (0.28%); T1589 Gather Victim Identity Information (0.11%) | 99.17% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.89%); T1059 Command and Scripting Interpreter (0.86%); T1201 Password Policy Discovery (0.24%) | 97.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.16%); T1204 User Execution (0.09%); T1057 Process Discovery (0.07%) | 99.16% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.04%); T1074 Data Staged (0.09%); T1124 System Time Discovery (0.07%) | 99.04% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.50%); T1573 Encrypted Channel (0.26%); T1120 Peripheral Device Discovery (0.24%) | 97.50% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (36.90%); T1222 File and Directory Permissions Modification (11.71%); T1059 Command and Scripting Interpreter (6.06%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (50.63%); T1033 System Owner/User Discovery (16.21%); T1053 Scheduled Task/Job (13.63%) | 0.04% | False |

## real_75 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.27%); T1071 Application Layer Protocol (0.09%); T1557 Adversary-in-the-Middle (0.08%) | 99.27% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.91%); T1548 Abuse Elevation Control Mechanism (0.42%); T1059 Command and Scripting Interpreter (0.16%) | 98.91% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.10%); T1057 Process Discovery (0.15%); T1201 Password Policy Discovery (0.10%) | 99.10% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.63%); T1190 Exploit Public-Facing Application (0.38%); T1589 Gather Victim Identity Information (0.25%) | 98.63% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.54%); T1059 Command and Scripting Interpreter (1.32%); T1041 Exfiltration Over C2 Channel (0.09%) | 97.54% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.28%); T1201 Password Policy Discovery (0.27%); T1059 Command and Scripting Interpreter (0.06%) | 99.28% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.22%); T1124 System Time Discovery (0.11%); T1041 Exfiltration Over C2 Channel (0.05%) | 99.22% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.48%); T1003 OS Credential Dumping (0.59%); T1039 Data from Network Shared Drive (0.48%) | 97.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (33.35%); T1039 Data from Network Shared Drive (19.77%); T1053 Scheduled Task/Job (7.38%) | 0.17% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (60.00%); T1039 Data from Network Shared Drive (6.61%); T1053 Scheduled Task/Job (4.87%) | 0.22% | False |

## real_75 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (98.96%); T1595 Active Scanning (0.08%); T1136 Create Account (0.08%) | 98.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.31%); T1548 Abuse Elevation Control Mechanism (0.85%); T1543 Create or Modify System Process (0.09%) | 98.31% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.19%); T1057 Process Discovery (0.09%); T1486 Data Encrypted for Impact (0.05%) | 99.19% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.22%); T1589 Gather Victim Identity Information (0.20%); T1190 Exploit Public-Facing Application (0.15%) | 99.22% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.62%); T1059 Command and Scripting Interpreter (0.21%); T1105 Ingress Tool Transfer (0.13%) | 98.62% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.51%); T1059 Command and Scripting Interpreter (1.61%); T1083 File and Directory Discovery (0.09%) | 97.51% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.99%); T1124 System Time Discovery (0.10%); T1033 System Owner/User Discovery (0.05%) | 98.99% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.26%); T1039 Data from Network Shared Drive (0.82%); T1565 Data Manipulation (0.22%) | 97.26% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (88.93%); T1120 Peripheral Device Discovery (1.89%); T1016 System Network Configuration Discovery (1.05%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (65.91%); T1546 Event Triggered Execution (4.55%); T1120 Peripheral Device Discovery (3.55%) | 0.03% | False |

## real_75 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.04%); T1083 File and Directory Discovery (0.13%); T1057 Process Discovery (0.12%) | 99.04% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.90%); T1548 Abuse Elevation Control Mechanism (1.30%); T1566 Phishing (0.09%) | 97.90% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.22%); T1003 OS Credential Dumping (0.10%); T1219 Remote Access Tools (0.08%) | 99.22% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (98.80%); T1190 Exploit Public-Facing Application (0.56%); T1589 Gather Victim Identity Information (0.21%) | 98.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.39%); T1059 Command and Scripting Interpreter (0.45%); T1039 Data from Network Shared Drive (0.13%) | 98.39% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.16%); T1059 Command and Scripting Interpreter (0.30%); T1574 Hijack Execution Flow (0.07%) | 99.16% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.88%); T1573 Encrypted Channel (0.13%); T1124 System Time Discovery (0.11%) | 98.88% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.72%); T1573 Encrypted Channel (0.46%); T1565 Data Manipulation (0.24%) | 96.72% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1049 System Network Connections Discovery (14.63%); T1036 Masquerading (12.98%); T1573 Encrypted Channel (6.92%) | 0.65% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1036 Masquerading (9.30%); T1213 Data from Information Repositories (9.27%); T1565 Data Manipulation (8.01%) | 0.54% | False |

## real_75 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.18%); T1557 Adversary-in-the-Middle (0.08%); T1222 File and Directory Permissions Modification (0.05%) | 99.18% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.34%); T1548 Abuse Elevation Control Mechanism (0.17%); T1070 Indicator Removal (0.03%) | 99.34% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.32%); T1528 Steal Application Access Token (0.06%); T1222 File and Directory Permissions Modification (0.04%) | 99.32% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.21%); T1190 Exploit Public-Facing Application (0.33%); T1589 Gather Victim Identity Information (0.11%) | 99.21% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.71%); T1059 Command and Scripting Interpreter (1.12%); T1564 Hide Artifacts (0.10%) | 97.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.43%); T1565 Data Manipulation (0.10%); T1557 Adversary-in-the-Middle (0.04%) | 99.43% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.18%); T1564 Hide Artifacts (0.09%); T1124 System Time Discovery (0.06%) | 99.18% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.01%); T1039 Data from Network Shared Drive (0.76%); T1041 Exfiltration Over C2 Channel (0.42%) | 97.01% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (28.95%); T1018 Remote System Discovery (10.72%); T1614 System Location Discovery (7.13%) | 0.29% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1486 Data Encrypted for Impact (11.80%); T1082 System Information Discovery (8.93%); T1490 Inhibit System Recovery (8.41%) | 0.08% | False |

## real_75 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.29%); T1592 Gather Victim Host Information (0.14%); T1557 Adversary-in-the-Middle (0.06%) | 99.29% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.58%); T1548 Abuse Elevation Control Mechanism (0.51%); T1218 System Binary Proxy Execution (0.20%) | 98.58% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.45%); T1053 Scheduled Task/Job (0.06%); T1190 Exploit Public-Facing Application (0.04%) | 99.45% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.44%); T1190 Exploit Public-Facing Application (0.13%); T1589 Gather Victim Identity Information (0.13%) | 99.44% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1033 System Owner/User Discovery (84.33%); T1105 Ingress Tool Transfer (9.92%); T1071 Application Layer Protocol (1.68%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.54%); T1033 System Owner/User Discovery (0.05%); T1083 File and Directory Discovery (0.04%) | 99.54% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.48%); T1124 System Time Discovery (0.05%); T1059 Command and Scripting Interpreter (0.04%) | 99.48% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.48%); T1003 OS Credential Dumping (0.42%); T1039 Data from Network Shared Drive (0.39%) | 97.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1098 Account Manipulation (21.31%); T1204 User Execution (20.07%); T1082 System Information Discovery (15.70%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1566 Phishing (32.87%); T1219 Remote Access Tools (18.74%); T1070 Indicator Removal (15.34%) | 0.04% | False |

## real_75 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.13%); T1589 Gather Victim Identity Information (0.08%); T1557 Adversary-in-the-Middle (0.07%) | 99.13% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.44%); T1548 Abuse Elevation Control Mechanism (0.81%); T1518 Software Discovery (0.10%) | 98.44% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.37%); T1222 File and Directory Permissions Modification (0.08%); T1201 Password Policy Discovery (0.06%) | 99.37% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.04%); T1589 Gather Victim Identity Information (0.30%); T1190 Exploit Public-Facing Application (0.25%) | 99.04% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.67%); T1059 Command and Scripting Interpreter (2.39%); T1087 Account Discovery (0.20%) | 95.67% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.48%); T1591 Gather Victim Org Information (0.07%); T1053 Scheduled Task/Job (0.05%) | 99.48% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.06%); T1518 Software Discovery (0.22%); T1033 System Owner/User Discovery (0.06%) | 99.06% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.16%); T1039 Data from Network Shared Drive (0.49%); T1574 Hijack Execution Flow (0.17%) | 98.16% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (19.03%); T1041 Exfiltration Over C2 Channel (18.17%); T1574 Hijack Execution Flow (14.07%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (63.11%); T1105 Ingress Tool Transfer (10.50%); T1574 Hijack Execution Flow (10.09%) | 0.06% | False |

## real_75 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.15%); T1543 Create or Modify System Process (0.09%); T1005 Data from Local System (0.08%) | 99.15% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.77%); T1548 Abuse Elevation Control Mechanism (1.26%); T1036 Masquerading (0.69%) | 96.77% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.21%); T1057 Process Discovery (0.11%); T1083 File and Directory Discovery (0.05%) | 99.21% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (94.02%); T1190 Exploit Public-Facing Application (4.61%); T1222 File and Directory Permissions Modification (0.15%) | 94.02% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (89.21%); T1486 Data Encrypted for Impact (3.54%); T1021 Remote Services (1.11%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.93%); T1059 Command and Scripting Interpreter (0.62%); T1083 File and Directory Discovery (0.05%) | 98.93% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.34%); T1485 Data Destruction (0.09%); T1124 System Time Discovery (0.07%) | 99.34% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.78%); T1070 Indicator Removal (0.33%); T1033 System Owner/User Discovery (0.19%) | 97.78% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1083 File and Directory Discovery (50.75%); T1485 Data Destruction (5.85%); T1566 Phishing (3.94%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1016 System Network Configuration Discovery (12.12%); T1525 Implant Internal Image (8.30%); T1566 Phishing (8.09%) | 0.14% | False |

## real_75 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.35%); T1565 Data Manipulation (0.04%); T1082 System Information Discovery (0.03%) | 99.35% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (59.29%); T1548 Abuse Elevation Control Mechanism (38.49%); T1078 Valid Accounts (0.32%) | 59.29% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.54%); T1039 Data from Network Shared Drive (0.05%); T1053 Scheduled Task/Job (0.04%) | 99.54% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (62.59%); T1190 Exploit Public-Facing Application (36.59%); T1589 Gather Victim Identity Information (0.10%) | 62.59% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1016 System Network Configuration Discovery (68.87%); T1033 System Owner/User Discovery (10.61%); T1083 File and Directory Discovery (2.23%) | 0.03% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (64.48%); T1087 Account Discovery (34.91%); T1095 Non-Application Layer Protocol (0.06%) | 34.91% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.90%); T1082 System Information Discovery (0.18%); T1087 Account Discovery (0.09%) | 98.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.00%); T1120 Peripheral Device Discovery (0.26%); T1039 Data from Network Shared Drive (0.15%) | 98.00% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (91.48%); T1059 Command and Scripting Interpreter (5.93%); T1082 System Information Discovery (0.41%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (57.72%); T1564 Hide Artifacts (32.31%); T1018 Remote System Discovery (2.17%) | 0.06% | False |

## real_75 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.11%); T1592 Gather Victim Host Information (0.13%); T1573 Encrypted Channel (0.10%) | 99.11% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (87.57%); T1548 Abuse Elevation Control Mechanism (10.27%); T1105 Ingress Tool Transfer (0.33%) | 87.57% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.28%); T1021 Remote Services (0.07%); T1040 Network Sniffing (0.06%) | 99.28% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (57.51%); T1595 Active Scanning (41.22%); T1592 Gather Victim Host Information (0.18%) | 41.22% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1218 System Binary Proxy Execution (37.15%); T1033 System Owner/User Discovery (17.40%); T1070 Indicator Removal (14.94%) | 0.07% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (53.18%); T1059 Command and Scripting Interpreter (45.62%); T1053 Scheduled Task/Job (0.21%) | 53.18% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.10%); T1016 System Network Configuration Discovery (0.08%); T1610 Deploy Container (0.07%) | 99.10% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (93.30%); T1049 System Network Connections Discovery (2.04%); T1021 Remote Services (0.97%) | 93.30% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (50.27%); T1021 Remote Services (10.20%); T1105 Ingress Tool Transfer (9.70%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (23.44%); T1564 Hide Artifacts (15.73%); T1083 File and Directory Discovery (7.84%) | 0.25% | False |

## real_75 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.41%); T1071 Application Layer Protocol (0.12%); T1070 Indicator Removal (0.05%) | 99.41% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (63.97%); T1548 Abuse Elevation Control Mechanism (32.91%); T1036 Masquerading (0.62%) | 63.97% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.35%); T1518 Software Discovery (0.06%); T1007 System Service Discovery (0.05%) | 99.35% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (68.24%); T1190 Exploit Public-Facing Application (30.71%); T1592 Gather Victim Host Information (0.13%) | 68.24% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.69%); T1059 Command and Scripting Interpreter (0.15%); T1068 Exploitation for Privilege Escalation (0.10%) | 98.69% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (72.82%); T1059 Command and Scripting Interpreter (25.99%); T1082 System Information Discovery (0.18%) | 72.82% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.23%); T1574 Hijack Execution Flow (0.50%); T1204 User Execution (0.29%) | 97.23% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (96.84%); T1021 Remote Services (0.44%); T1071 Application Layer Protocol (0.32%) | 96.84% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (46.66%); T1070 Indicator Removal (21.93%); T1053 Scheduled Task/Job (8.46%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (82.41%); T1564 Hide Artifacts (8.49%); T1574 Hijack Execution Flow (2.85%) | 0.11% | False |

## real_75 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.42%); T1557 Adversary-in-the-Middle (0.04%); T1595 Active Scanning (0.04%) | 99.42% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.63%); T1548 Abuse Elevation Control Mechanism (2.38%); T1059 Command and Scripting Interpreter (0.26%) | 96.63% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.37%); T1518 Software Discovery (0.06%); T1082 System Information Discovery (0.06%) | 99.37% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (64.28%); T1595 Active Scanning (34.38%); T1589 Gather Victim Identity Information (0.17%) | 34.38% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (88.56%); T1059 Command and Scripting Interpreter (9.35%); T1547 Boot or Logon Autostart Execution (0.45%) | 88.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (71.58%); T1087 Account Discovery (27.54%); T1082 System Information Discovery (0.27%) | 27.54% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.48%); T1518 Software Discovery (0.19%); T1201 Password Policy Discovery (0.10%) | 98.48% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.14%); T1049 System Network Connections Discovery (0.46%); T1120 Peripheral Device Discovery (0.36%) | 97.14% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1005 Data from Local System (10.71%); T1589 Gather Victim Identity Information (9.99%); T1190 Exploit Public-Facing Application (8.11%) | 0.30% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (49.98%); T1222 File and Directory Permissions Modification (11.03%); T1564 Hide Artifacts (8.58%) | 0.39% | False |

## real_75 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.54%); T1592 Gather Victim Host Information (0.06%); T1573 Encrypted Channel (0.03%) | 99.54% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (94.19%); T1548 Abuse Elevation Control Mechanism (4.35%); T1105 Ingress Tool Transfer (0.34%) | 94.19% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.50%); T1068 Exploitation for Privilege Escalation (0.05%); T1615 Group Policy Discovery (0.03%) | 99.50% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (50.39%); T1595 Active Scanning (48.66%); T1589 Gather Victim Identity Information (0.16%) | 48.66% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.23%); T1105 Ingress Tool Transfer (0.12%); T1218 System Binary Proxy Execution (0.11%) | 99.23% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (72.24%); T1087 Account Discovery (27.21%); T1053 Scheduled Task/Job (0.07%) | 27.21% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.13%); T1016 System Network Configuration Discovery (0.35%); T1615 Group Policy Discovery (0.15%) | 98.13% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.03%); T1049 System Network Connections Discovery (0.46%); T1573 Encrypted Channel (0.36%) | 97.03% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (12.23%); T1543 Create or Modify System Process (11.00%); T1531 Account Access Removal (7.07%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (44.47%); T1564 Hide Artifacts (39.29%); T1010 Application Window Discovery (1.91%) | 0.22% | False |

## real_75 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.41%); T1592 Gather Victim Host Information (0.08%); T1082 System Information Discovery (0.08%) | 99.41% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (61.00%); T1548 Abuse Elevation Control Mechanism (36.30%); T1105 Ingress Tool Transfer (0.35%) | 61.00% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.37%); T1049 System Network Connections Discovery (0.05%); T1592 Gather Victim Host Information (0.05%) | 99.37% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (66.93%); T1190 Exploit Public-Facing Application (31.76%); T1592 Gather Victim Host Information (0.38%) | 66.93% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.27%); T1059 Command and Scripting Interpreter (0.64%); T1083 File and Directory Discovery (0.09%) | 98.27% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (78.61%); T1087 Account Discovery (20.95%); T1201 Password Policy Discovery (0.04%) | 20.95% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.25%); T1070 Indicator Removal (0.39%); T1078 Valid Accounts (0.19%) | 98.25% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.38%); T1049 System Network Connections Discovery (0.18%); T1021 Remote Services (0.13%) | 98.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (13.94%); T1087 Account Discovery (13.02%); T1591 Gather Victim Org Information (6.67%) | 0.47% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (44.30%); T1592 Gather Victim Host Information (12.49%); T1595 Active Scanning (5.93%) | 0.04% | False |

## real_75 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.60%); T1610 Deploy Container (0.03%); T1589 Gather Victim Identity Information (0.02%) | 99.60% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.22%); T1548 Abuse Elevation Control Mechanism (1.00%); T1120 Peripheral Device Discovery (0.10%) | 98.22% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.39%); T1049 System Network Connections Discovery (0.05%); T1087 Account Discovery (0.04%) | 99.39% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (55.96%); T1595 Active Scanning (43.06%); T1053 Scheduled Task/Job (0.16%) | 43.06% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.26%); T1218 System Binary Proxy Execution (0.30%); T1059 Command and Scripting Interpreter (0.29%) | 98.26% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (81.78%); T1087 Account Discovery (17.77%); T1053 Scheduled Task/Job (0.04%) | 17.77% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.17%); T1120 Peripheral Device Discovery (0.11%); T1557 Adversary-in-the-Middle (0.10%) | 99.17% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (94.67%); T1041 Exfiltration Over C2 Channel (1.19%); T1049 System Network Connections Discovery (0.46%) | 94.67% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (74.10%); T1071 Application Layer Protocol (11.41%); T1219 Remote Access Tools (2.13%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1071 Application Layer Protocol (35.97%); T1564 Hide Artifacts (33.54%); T1222 File and Directory Permissions Modification (4.64%) | 0.37% | False |

## real_75 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.47%); T1592 Gather Victim Host Information (0.11%); T1573 Encrypted Channel (0.04%) | 99.47% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.15%); T1548 Abuse Elevation Control Mechanism (0.43%); T1105 Ingress Tool Transfer (0.16%) | 99.15% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.20%); T1087 Account Discovery (0.11%); T1518 Software Discovery (0.10%) | 99.20% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (62.37%); T1190 Exploit Public-Facing Application (36.70%); T1589 Gather Victim Identity Information (0.10%) | 62.37% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1098 Account Manipulation (47.52%); T1018 Remote System Discovery (11.18%); T1556 Modify Authentication Process (8.66%) | 0.17% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (61.08%); T1059 Command and Scripting Interpreter (38.02%); T1543 Create or Modify System Process (0.09%) | 61.08% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.20%); T1547 Boot or Logon Autostart Execution (0.07%); T1489 Service Stop (0.06%) | 99.20% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.97%); T1016 System Network Configuration Discovery (0.35%); T1049 System Network Connections Discovery (0.31%) | 97.97% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1485 Data Destruction (36.83%); T1486 Data Encrypted for Impact (12.34%); T1219 Remote Access Tools (6.20%) | 0.24% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (44.36%); T1219 Remote Access Tools (18.31%); T1222 File and Directory Permissions Modification (10.32%) | 0.28% | False |

## real_75 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.42%); T1589 Gather Victim Identity Information (0.08%); T1595 Active Scanning (0.05%) | 99.42% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (74.73%); T1548 Abuse Elevation Control Mechanism (22.71%); T1078 Valid Accounts (0.26%) | 74.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.39%); T1614 System Location Discovery (0.05%); T1615 Group Policy Discovery (0.04%) | 99.39% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (65.96%); T1190 Exploit Public-Facing Application (32.70%); T1083 File and Directory Discovery (0.22%) | 65.96% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.65%); T1547 Boot or Logon Autostart Execution (0.26%); T1564 Hide Artifacts (0.08%) | 98.65% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (58.29%); T1087 Account Discovery (40.97%); T1070 Indicator Removal (0.09%) | 40.97% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (98.72%); T1518 Software Discovery (0.34%); T1120 Peripheral Device Discovery (0.09%) | 98.72% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.89%); T1041 Exfiltration Over C2 Channel (0.55%); T1569 System Services (0.13%) | 97.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (22.04%); T1105 Ingress Tool Transfer (17.45%); T1098 Account Manipulation (8.23%) | 0.12% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (56.85%); T1556 Modify Authentication Process (10.34%); T1564 Hide Artifacts (7.49%) | 0.65% | False |

## real_75 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.47%); T1543 Create or Modify System Process (0.05%); T1595 Active Scanning (0.04%) | 99.47% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.41%); T1548 Abuse Elevation Control Mechanism (1.16%); T1105 Ingress Tool Transfer (0.51%) | 97.41% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.61%); T1190 Exploit Public-Facing Application (0.04%); T1557 Adversary-in-the-Middle (0.03%) | 99.61% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (64.98%); T1190 Exploit Public-Facing Application (33.78%); T1592 Gather Victim Host Information (0.31%) | 64.98% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1105 Ingress Tool Transfer (84.51%); T1016 System Network Configuration Discovery (4.71%); T1078 Valid Accounts (2.11%) | 0.01% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (52.34%); T1087 Account Discovery (46.92%); T1486 Data Encrypted for Impact (0.10%) | 46.92% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (97.41%); T1083 File and Directory Discovery (0.40%); T1057 Process Discovery (0.27%) | 97.41% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (95.10%); T1021 Remote Services (0.81%); T1041 Exfiltration Over C2 Channel (0.68%) | 95.10% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (93.77%); T1213 Data from Information Repositories (0.90%); T1485 Data Destruction (0.50%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (30.29%); T1222 File and Directory Permissions Modification (24.46%); T1018 Remote System Discovery (7.48%) | 0.14% | False |

## repeat_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1213 Data from Information Repositories (0.01%); T1120 Peripheral Device Discovery (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.92%); T1036 Masquerading (0.05%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.92% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.96%); T1490 Inhibit System Recovery (0.00%); T1018 Remote System Discovery (0.00%) | 99.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.88%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.04%) | 99.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.69%); T1059 Command and Scripting Interpreter (0.08%); T1566 Phishing (0.04%) | 99.69% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.97%); T1059 Command and Scripting Interpreter (0.01%); T1082 System Information Discovery (0.01%) | 99.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.88%); T1543 Create or Modify System Process (0.02%); T1124 System Time Discovery (0.02%) | 99.88% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.47%); T1039 Data from Network Shared Drive (0.16%); T1003 OS Credential Dumping (0.07%) | 99.47% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (26.96%); T1222 File and Directory Permissions Modification (15.69%); T1003 OS Credential Dumping (15.22%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (85.42%); T1595 Active Scanning (3.95%); T1071 Application Layer Protocol (3.06%) | 0.00% | False |

## repeat_100 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.93%); T1595 Active Scanning (0.02%); T1003 OS Credential Dumping (0.01%) | 99.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.67%); T1548 Abuse Elevation Control Mechanism (0.16%); T1070 Indicator Removal (0.04%) | 99.67% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1040 Network Sniffing (0.01%); T1082 System Information Discovery (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.89%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.02%) | 99.89% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.76%); T1083 File and Directory Discovery (0.04%); T1078 Valid Accounts (0.02%) | 99.76% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.95%); T1591 Gather Victim Org Information (0.01%); T1059 Command and Scripting Interpreter (0.01%) | 99.95% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.84%); T1124 System Time Discovery (0.06%); T1072 Software Deployment Tools (0.03%) | 99.84% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.62%); T1039 Data from Network Shared Drive (0.12%); T1120 Peripheral Device Discovery (0.12%) | 99.62% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (51.25%); T1591 Gather Victim Org Information (38.90%); T1003 OS Credential Dumping (4.42%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (41.02%); T1591 Gather Victim Org Information (10.32%); T1204 User Execution (8.90%) | 3.91% | False |

## repeat_100 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1218 System Binary Proxy Execution (0.01%); T1010 Application Window Discovery (0.01%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.74%); T1548 Abuse Elevation Control Mechanism (0.15%); T1082 System Information Discovery (0.03%) | 99.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1057 Process Discovery (0.01%); T1219 Remote Access Tools (0.01%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.89%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.02%) | 99.89% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.64%); T1059 Command and Scripting Interpreter (0.11%); T1105 Ingress Tool Transfer (0.03%) | 99.64% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.98%); T1041 Exfiltration Over C2 Channel (0.00%); T1083 File and Directory Discovery (0.00%) | 99.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1018 Remote System Discovery (0.01%); T1124 System Time Discovery (0.01%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.77%); T1039 Data from Network Shared Drive (0.05%); T1078 Valid Accounts (0.03%) | 99.77% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (59.86%); T1222 File and Directory Permissions Modification (32.72%); T1033 System Owner/User Discovery (1.41%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (47.34%); T1003 OS Credential Dumping (30.85%); T1070 Indicator Removal (18.37%) | 0.05% | False |

## repeat_100 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.95%); T1557 Adversary-in-the-Middle (0.01%); T1589 Gather Victim Identity Information (0.00%) | 99.95% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.80%); T1548 Abuse Elevation Control Mechanism (0.06%); T1105 Ingress Tool Transfer (0.06%) | 99.80% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1080 Taint Shared Content (0.01%); T1564 Hide Artifacts (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.90%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.02%) | 99.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.63%); T1059 Command and Scripting Interpreter (0.04%); T1564 Hide Artifacts (0.04%) | 99.63% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1078 Valid Accounts (0.01%); T1059 Command and Scripting Interpreter (0.01%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.91%); T1124 System Time Discovery (0.02%); T1485 Data Destruction (0.01%) | 99.91% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.75%); T1003 OS Credential Dumping (0.04%); T1120 Peripheral Device Discovery (0.03%) | 99.75% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (37.85%); T1222 File and Directory Permissions Modification (18.01%); T1564 Hide Artifacts (12.87%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (27.51%); T1564 Hide Artifacts (15.41%); T1003 OS Credential Dumping (12.45%) | 0.01% | False |

## repeat_100 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1098 Account Manipulation (0.01%); T1205 Traffic Signaling (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.90%); T1205 Traffic Signaling (0.02%); T1082 System Information Discovery (0.01%) | 99.90% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.93%); T1057 Process Discovery (0.01%); T1003 OS Credential Dumping (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.94%); T1589 Gather Victim Identity Information (0.02%); T1190 Exploit Public-Facing Application (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.59%); T1059 Command and Scripting Interpreter (0.17%); T1105 Ingress Tool Transfer (0.06%) | 99.59% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.76%); T1059 Command and Scripting Interpreter (0.18%); T1083 File and Directory Discovery (0.01%) | 99.76% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.83%); T1124 System Time Discovery (0.03%); T1564 Hide Artifacts (0.02%) | 99.83% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.48%); T1003 OS Credential Dumping (0.15%); T1082 System Information Discovery (0.06%) | 99.48% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (57.38%); T1071 Application Layer Protocol (10.53%); T1007 System Service Discovery (8.33%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (27.64%); T1041 Exfiltration Over C2 Channel (19.85%); T1078 Valid Accounts (10.20%) | 0.00% | False |

## repeat_100 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1083 File and Directory Discovery (0.01%); T1115 Clipboard Data (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.84%); T1548 Abuse Elevation Control Mechanism (0.03%); T1485 Data Destruction (0.01%) | 99.84% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.91%); T1201 Password Policy Discovery (0.02%); T1110 Brute Force (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.87%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.03%) | 99.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.56%); T1059 Command and Scripting Interpreter (0.16%); T1547 Boot or Logon Autostart Execution (0.06%) | 99.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.96%); T1204 User Execution (0.01%); T1486 Data Encrypted for Impact (0.00%) | 99.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1072 Software Deployment Tools (0.10%); T1070 Indicator Removal (0.03%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.72%); T1039 Data from Network Shared Drive (0.14%); T1497 Virtualization/Sandbox Evasion (0.01%) | 99.72% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (42.42%); T1010 Application Window Discovery (10.85%); T1110 Brute Force (6.28%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (17.71%); T1222 File and Directory Permissions Modification (9.95%); T1110 Brute Force (7.64%) | 0.02% | False |

## repeat_100 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1595 Active Scanning (0.01%); T1589 Gather Victim Identity Information (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.94%); T1548 Abuse Elevation Control Mechanism (0.02%); T1566 Phishing (0.01%) | 99.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1528 Steal Application Access Token (0.00%); T1057 Process Discovery (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.93%); T1589 Gather Victim Identity Information (0.03%); T1190 Exploit Public-Facing Application (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.59%); T1059 Command and Scripting Interpreter (0.10%); T1071 Application Layer Protocol (0.07%) | 99.59% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.97%); T1018 Remote System Discovery (0.00%); T1083 File and Directory Discovery (0.00%) | 99.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1040 Network Sniffing (0.01%); T1110 Brute Force (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.87%); T1039 Data from Network Shared Drive (0.04%); T1120 Peripheral Device Discovery (0.02%) | 99.87% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (61.71%); T1105 Ingress Tool Transfer (29.82%); T1546 Event Triggered Execution (1.57%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (87.44%); T1548 Abuse Elevation Control Mechanism (2.25%); T1557 Adversary-in-the-Middle (1.65%) | 0.00% | False |

## repeat_100 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1059 Command and Scripting Interpreter (0.01%); T1595 Active Scanning (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.95%); T1548 Abuse Elevation Control Mechanism (0.01%); T1105 Ingress Tool Transfer (0.01%) | 99.95% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1003 OS Credential Dumping (0.01%); T1053 Scheduled Task/Job (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.87%); T1190 Exploit Public-Facing Application (0.05%); T1589 Gather Victim Identity Information (0.04%) | 99.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.61%); T1059 Command and Scripting Interpreter (0.14%); T1105 Ingress Tool Transfer (0.05%) | 99.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.96%); T1059 Command and Scripting Interpreter (0.00%); T1565 Data Manipulation (0.00%) | 99.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1566 Phishing (0.02%); T1124 System Time Discovery (0.01%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.95%); T1003 OS Credential Dumping (0.65%); T1039 Data from Network Shared Drive (0.07%) | 98.95% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (33.19%); T1059 Command and Scripting Interpreter (27.93%); T1497 Virtualization/Sandbox Evasion (20.17%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (87.30%); T1059 Command and Scripting Interpreter (4.20%); T1201 Password Policy Discovery (1.71%) | 0.00% | False |

## repeat_100 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1497 Virtualization/Sandbox Evasion (0.01%); T1204 User Execution (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.89%); T1548 Abuse Elevation Control Mechanism (0.03%); T1105 Ingress Tool Transfer (0.01%) | 99.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1033 System Owner/User Discovery (0.01%); T1201 Password Policy Discovery (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.88%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.54%); T1059 Command and Scripting Interpreter (0.08%); T1547 Boot or Logon Autostart Execution (0.05%) | 99.54% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1059 Command and Scripting Interpreter (0.01%); T1033 System Owner/User Discovery (0.01%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1110 Brute Force (0.02%); T1210 Exploitation of Remote Services (0.01%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.53%); T1039 Data from Network Shared Drive (0.14%); T1003 OS Credential Dumping (0.12%) | 99.53% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1566 Phishing (23.46%); T1222 File and Directory Permissions Modification (12.21%); T1518 Software Discovery (10.30%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (59.69%); T1222 File and Directory Permissions Modification (6.53%); T1057 Process Discovery (4.85%) | 0.01% | False |

## repeat_100 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1018 Remote System Discovery (0.00%); T1218 System Binary Proxy Execution (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.77%); T1548 Abuse Elevation Control Mechanism (0.06%); T1036 Masquerading (0.04%) | 99.77% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1057 Process Discovery (0.01%); T1003 OS Credential Dumping (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.84%); T1190 Exploit Public-Facing Application (0.06%); T1589 Gather Victim Identity Information (0.05%) | 99.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.62%); T1059 Command and Scripting Interpreter (0.12%); T1556 Modify Authentication Process (0.04%) | 99.62% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.94%); T1059 Command and Scripting Interpreter (0.94%); T1033 System Owner/User Discovery (0.01%) | 98.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1560 Archive Collected Data (0.01%); T1485 Data Destruction (0.01%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.74%); T1083 File and Directory Discovery (0.06%); T1039 Data from Network Shared Drive (0.06%) | 99.74% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1068 Exploitation for Privilege Escalation (14.35%); T1564 Hide Artifacts (9.72%); T1222 File and Directory Permissions Modification (8.85%) | 0.61% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (76.57%); T1573 Encrypted Channel (5.78%); T1014 Rootkit (1.85%) | 0.00% | False |

## repeat_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1595 Active Scanning (0.04%); T1082 System Information Discovery (0.02%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.67%); T1548 Abuse Elevation Control Mechanism (0.17%); T1036 Masquerading (0.09%) | 99.67% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1518 Software Discovery (0.02%); T1033 System Owner/User Discovery (0.02%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.71%); T1190 Exploit Public-Facing Application (0.19%); T1589 Gather Victim Identity Information (0.04%) | 99.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.85%); T1059 Command and Scripting Interpreter (0.02%); T1219 Remote Access Tools (0.01%) | 99.85% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.96%); T1082 System Information Discovery (0.01%); T1205 Traffic Signaling (0.00%) | 99.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.90%); T1124 System Time Discovery (0.02%); T1222 File and Directory Permissions Modification (0.01%) | 99.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.51%); T1078 Valid Accounts (0.13%); T1039 Data from Network Shared Drive (0.10%) | 99.51% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (90.39%); T1105 Ingress Tool Transfer (6.60%); T1222 File and Directory Permissions Modification (0.80%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (48.28%); T1078 Valid Accounts (11.36%); T1105 Ingress Tool Transfer (9.28%) | 0.02% | False |

## repeat_100 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1566 Phishing (0.01%); T1595 Active Scanning (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.71%); T1548 Abuse Elevation Control Mechanism (0.11%); T1036 Masquerading (0.07%) | 99.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1204 User Execution (0.01%); T1565 Data Manipulation (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.76%); T1589 Gather Victim Identity Information (0.09%); T1190 Exploit Public-Facing Application (0.09%) | 99.76% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.69%); T1190 Exploit Public-Facing Application (0.04%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.69% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.96%); T1059 Command and Scripting Interpreter (0.01%); T1003 OS Credential Dumping (0.00%) | 99.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1124 System Time Discovery (0.01%); T1485 Data Destruction (0.00%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.71%); T1039 Data from Network Shared Drive (0.08%); T1003 OS Credential Dumping (0.03%) | 99.71% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1546 Event Triggered Execution (13.40%); T1082 System Information Discovery (11.99%); T1548 Abuse Elevation Control Mechanism (8.27%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (59.94%); T1548 Abuse Elevation Control Mechanism (28.10%); T1546 Event Triggered Execution (5.01%) | 0.00% | False |

## repeat_100 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.89%); T1486 Data Encrypted for Impact (0.01%); T1049 System Network Connections Discovery (0.01%) | 99.89% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.83%); T1548 Abuse Elevation Control Mechanism (0.06%); T1036 Masquerading (0.02%) | 99.83% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1485 Data Destruction (0.01%); T1565 Data Manipulation (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.82%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.03%) | 99.82% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.78%); T1078 Valid Accounts (0.04%); T1201 Password Policy Discovery (0.02%) | 99.78% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.96%); T1204 User Execution (0.01%); T1531 Account Access Removal (0.00%) | 99.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.91%); T1525 Implant Internal Image (0.01%); T1074 Data Staged (0.01%) | 99.91% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.70%); T1083 File and Directory Discovery (0.07%); T1039 Data from Network Shared Drive (0.05%) | 99.70% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (72.42%); T1222 File and Directory Permissions Modification (8.66%); T1046 Network Service Scanning (3.48%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (47.51%); T1033 System Owner/User Discovery (21.12%); T1222 File and Directory Permissions Modification (15.76%) | 0.06% | False |

## repeat_100 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1110 Brute Force (0.03%); T1071 Application Layer Protocol (0.02%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.87%); T1548 Abuse Elevation Control Mechanism (0.04%); T1059 Command and Scripting Interpreter (0.02%) | 99.87% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1057 Process Discovery (0.02%); T1564 Hide Artifacts (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.84%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.03%) | 99.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.70%); T1059 Command and Scripting Interpreter (0.03%); T1078 Valid Accounts (0.03%) | 99.70% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1201 Password Policy Discovery (0.02%); T1110 Brute Force (0.00%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1040 Network Sniffing (0.01%); T1041 Exfiltration Over C2 Channel (0.01%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.67%); T1003 OS Credential Dumping (0.12%); T1039 Data from Network Shared Drive (0.07%) | 99.67% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (57.35%); T1039 Data from Network Shared Drive (13.06%); T1098 Account Manipulation (5.46%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (87.90%); T1039 Data from Network Shared Drive (2.43%); T1556 Modify Authentication Process (1.15%) | 0.01% | False |

## repeat_100 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1595 Active Scanning (0.02%); T1136 Create Account (0.01%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.59%); T1548 Abuse Elevation Control Mechanism (0.17%); T1036 Masquerading (0.09%) | 99.59% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1095 Non-Application Layer Protocol (0.01%); T1057 Process Discovery (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.88%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.03%) | 99.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.59%); T1105 Ingress Tool Transfer (0.10%); T1059 Command and Scripting Interpreter (0.05%) | 99.59% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (57.97%); T1059 Command and Scripting Interpreter (41.83%); T1574 Hijack Execution Flow (0.01%) | 57.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.90%); T1124 System Time Discovery (0.02%); T1016 System Network Configuration Discovery (0.01%) | 99.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.81%); T1039 Data from Network Shared Drive (0.05%); T1070 Indicator Removal (0.02%) | 99.81% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (60.30%); T1120 Peripheral Device Discovery (7.44%); T1574 Hijack Execution Flow (4.38%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (64.70%); T1486 Data Encrypted for Impact (12.65%); T1546 Event Triggered Execution (4.93%) | 0.02% | False |

## repeat_100 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1057 Process Discovery (0.01%); T1569 System Services (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.80%); T1548 Abuse Elevation Control Mechanism (0.06%); T1566 Phishing (0.04%) | 99.80% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1057 Process Discovery (0.01%); T1219 Remote Access Tools (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.78%); T1589 Gather Victim Identity Information (0.11%); T1190 Exploit Public-Facing Application (0.05%) | 99.78% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.75%); T1547 Boot or Logon Autostart Execution (0.02%); T1053 Scheduled Task/Job (0.02%) | 99.75% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.95%); T1007 System Service Discovery (0.00%); T1614 System Location Discovery (0.00%) | 99.95% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1573 Encrypted Channel (0.01%); T1124 System Time Discovery (0.01%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.60%); T1039 Data from Network Shared Drive (0.06%); T1573 Encrypted Channel (0.06%) | 99.60% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (41.52%); T1222 File and Directory Permissions Modification (9.32%); T1049 System Network Connections Discovery (5.36%) | 0.15% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (34.00%); T1053 Scheduled Task/Job (16.77%); T1486 Data Encrypted for Impact (10.00%) | 0.15% | False |

## repeat_100 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1222 File and Directory Permissions Modification (0.01%); T1213 Data from Information Repositories (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.81%); T1070 Indicator Removal (0.08%); T1087 Account Discovery (0.02%) | 99.81% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1222 File and Directory Permissions Modification (0.01%); T1528 Steal Application Access Token (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.87%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.04%) | 99.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.74%); T1039 Data from Network Shared Drive (0.04%); T1222 File and Directory Permissions Modification (0.03%) | 99.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.44%); T1059 Command and Scripting Interpreter (0.53%); T1083 File and Directory Discovery (0.01%) | 99.44% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1124 System Time Discovery (0.01%); T1564 Hide Artifacts (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.83%); T1039 Data from Network Shared Drive (0.04%); T1041 Exfiltration Over C2 Channel (0.03%) | 99.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (36.50%); T1614 System Location Discovery (31.02%); T1018 Remote System Discovery (5.64%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (52.48%); T1083 File and Directory Discovery (9.69%); T1490 Inhibit System Recovery (7.58%) | 0.01% | False |

## repeat_100 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.93%); T1557 Adversary-in-the-Middle (0.01%); T1592 Gather Victim Host Information (0.01%) | 99.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.83%); T1548 Abuse Elevation Control Mechanism (0.07%); T1218 System Binary Proxy Execution (0.04%) | 99.83% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1053 Scheduled Task/Job (0.01%); T1485 Data Destruction (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.84%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.05%) | 99.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.74%); T1547 Boot or Logon Autostart Execution (0.04%); T1068 Exploitation for Privilege Escalation (0.03%) | 99.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1573 Encrypted Channel (0.01%); T1041 Exfiltration Over C2 Channel (0.01%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1059 Command and Scripting Interpreter (0.01%); T1566 Phishing (0.01%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.72%); T1016 System Network Configuration Discovery (0.06%); T1039 Data from Network Shared Drive (0.05%) | 99.72% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (28.49%); T1204 User Execution (12.99%); T1036 Masquerading (7.91%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (25.62%); T1566 Phishing (23.57%); T1219 Remote Access Tools (16.40%) | 0.01% | False |

## repeat_100 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1557 Adversary-in-the-Middle (0.01%); T1497 Virtualization/Sandbox Evasion (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.86%); T1548 Abuse Elevation Control Mechanism (0.04%); T1550 Use Alternate Authentication Material (0.02%) | 99.86% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1201 Password Policy Discovery (0.01%); T1136 Create Account (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.86%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.02%) | 99.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.64%); T1547 Boot or Logon Autostart Execution (0.07%); T1078 Valid Accounts (0.04%) | 99.64% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1059 Command and Scripting Interpreter (0.01%); T1082 System Information Discovery (0.01%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.87%); T1518 Software Discovery (0.02%); T1124 System Time Discovery (0.01%) | 99.87% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.76%); T1003 OS Credential Dumping (0.10%); T1039 Data from Network Shared Drive (0.05%) | 99.76% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1574 Hijack Execution Flow (49.02%); T1082 System Information Discovery (19.82%); T1041 Exfiltration Over C2 Channel (8.74%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (57.41%); T1574 Hijack Execution Flow (35.02%); T1041 Exfiltration Over C2 Channel (2.30%) | 0.00% | False |

## repeat_100 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.89%); T1543 Create or Modify System Process (0.01%); T1005 Data from Local System (0.01%) | 99.89% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.80%); T1548 Abuse Elevation Control Mechanism (0.08%); T1219 Remote Access Tools (0.03%) | 99.80% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1057 Process Discovery (0.01%); T1071 Application Layer Protocol (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.79%); T1589 Gather Victim Identity Information (0.08%); T1190 Exploit Public-Facing Application (0.05%) | 99.79% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.40%); T1059 Command and Scripting Interpreter (0.34%); T1105 Ingress Tool Transfer (0.06%) | 99.40% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.95%); T1059 Command and Scripting Interpreter (0.01%); T1036 Masquerading (0.00%) | 99.95% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1124 System Time Discovery (0.01%); T1485 Data Destruction (0.01%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.71%); T1039 Data from Network Shared Drive (0.06%); T1003 OS Credential Dumping (0.04%) | 99.71% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (31.41%); T1082 System Information Discovery (14.00%); T1219 Remote Access Tools (10.22%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (37.31%); T1222 File and Directory Permissions Modification (15.36%); T1543 Create or Modify System Process (6.55%) | 0.03% | False |

## repeat_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1098 Account Manipulation (0.01%); T1614 System Location Discovery (0.00%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.07%); T1548 Abuse Elevation Control Mechanism (0.68%); T1059 Command and Scripting Interpreter (0.06%) | 99.07% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1039 Data from Network Shared Drive (0.02%); T1005 Data from Local System (0.00%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (66.10%); T1190 Exploit Public-Facing Application (33.61%); T1589 Gather Victim Identity Information (0.07%) | 66.10% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.61%); T1059 Command and Scripting Interpreter (0.20%); T1078 Valid Accounts (0.03%) | 99.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (67.45%); T1087 Account Discovery (32.45%); T1082 System Information Discovery (0.01%) | 32.45% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1614 System Location Discovery (0.02%); T1082 System Information Discovery (0.02%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.65%); T1071 Application Layer Protocol (0.05%); T1039 Data from Network Shared Drive (0.04%) | 99.65% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (76.91%); T1105 Ingress Tool Transfer (20.24%); T1219 Remote Access Tools (0.61%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (91.11%); T1222 File and Directory Permissions Modification (7.82%); T1018 Remote System Discovery (0.41%) | 0.00% | False |

## repeat_100 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1592 Gather Victim Host Information (0.02%); T1573 Encrypted Channel (0.02%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.93%); T1548 Abuse Elevation Control Mechanism (0.60%); T1036 Masquerading (0.20%) | 98.93% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.92%); T1018 Remote System Discovery (0.01%); T1021 Remote Services (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (54.23%); T1190 Exploit Public-Facing Application (45.44%); T1059 Command and Scripting Interpreter (0.09%) | 54.23% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.77%); T1218 System Binary Proxy Execution (0.03%); T1548 Abuse Elevation Control Mechanism (0.02%) | 99.77% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (84.97%); T1087 Account Discovery (14.90%); T1053 Scheduled Task/Job (0.05%) | 14.90% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.92%); T1072 Software Deployment Tools (0.03%); T1080 Taint Shared Content (0.00%) | 99.92% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.77%); T1120 Peripheral Device Discovery (0.06%); T1049 System Network Connections Discovery (0.04%) | 99.77% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1021 Remote Services (30.19%); T1078 Valid Accounts (26.40%); T1046 Network Service Scanning (6.43%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (38.37%); T1083 File and Directory Discovery (13.61%); T1201 Password Policy Discovery (9.45%) | 0.26% | False |

## repeat_100 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1071 Application Layer Protocol (0.01%); T1033 System Owner/User Discovery (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.13%); T1548 Abuse Elevation Control Mechanism (0.71%); T1059 Command and Scripting Interpreter (0.02%) | 99.13% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1124 System Time Discovery (0.01%); T1083 File and Directory Discovery (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (67.71%); T1190 Exploit Public-Facing Application (32.02%); T1589 Gather Victim Identity Information (0.06%) | 67.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.71%); T1059 Command and Scripting Interpreter (0.14%); T1033 System Owner/User Discovery (0.02%) | 99.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (82.44%); T1087 Account Discovery (17.43%); T1071 Application Layer Protocol (0.02%) | 17.43% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1486 Data Encrypted for Impact (0.05%); T1485 Data Destruction (0.02%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.77%); T1021 Remote Services (0.04%); T1573 Encrypted Channel (0.03%) | 99.77% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (46.93%); T1070 Indicator Removal (45.09%); T1110 Brute Force (1.43%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (86.72%); T1564 Hide Artifacts (5.45%); T1105 Ingress Tool Transfer (2.39%) | 0.09% | False |

## repeat_100 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1218 System Binary Proxy Execution (0.01%); T1098 Account Manipulation (0.01%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1548 Abuse Elevation Control Mechanism (0.10%); T1136 Create Account (0.02%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1083 File and Directory Discovery (0.01%); T1057 Process Discovery (0.00%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (56.22%); T1190 Exploit Public-Facing Application (43.52%); T1573 Encrypted Channel (0.05%) | 56.22% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.62%); T1059 Command and Scripting Interpreter (0.08%); T1218 System Binary Proxy Execution (0.06%) | 99.62% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (52.74%); T1059 Command and Scripting Interpreter (46.71%); T1082 System Information Discovery (0.10%) | 52.74% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.79%); T1124 System Time Discovery (0.04%); T1525 Implant Internal Image (0.03%) | 99.79% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.49%); T1041 Exfiltration Over C2 Channel (0.07%); T1573 Encrypted Channel (0.06%) | 99.49% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1014 Rootkit (18.90%); T1589 Gather Victim Identity Information (11.75%); T1218 System Binary Proxy Execution (7.04%) | 0.23% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (28.17%); T1564 Hide Artifacts (13.22%); T1005 Data from Local System (10.82%) | 0.37% | False |

## repeat_100 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1592 Gather Victim Host Information (0.01%); T1110 Brute Force (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1548 Abuse Elevation Control Mechanism (0.05%); T1105 Ingress Tool Transfer (0.03%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.93%); T1068 Exploitation for Privilege Escalation (0.03%); T1049 System Network Connections Discovery (0.00%) | 99.93% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (65.82%); T1190 Exploit Public-Facing Application (33.87%); T1592 Gather Victim Host Information (0.07%) | 65.82% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.75%); T1105 Ingress Tool Transfer (0.13%); T1218 System Binary Proxy Execution (0.02%) | 99.75% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (59.71%); T1059 Command and Scripting Interpreter (40.06%); T1053 Scheduled Task/Job (0.04%) | 59.71% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1016 System Network Configuration Discovery (0.04%); T1615 Group Policy Discovery (0.01%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.57%); T1573 Encrypted Channel (0.08%); T1021 Remote Services (0.08%) | 99.57% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (56.52%); T1033 System Owner/User Discovery (17.25%); T1564 Hide Artifacts (5.92%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (79.54%); T1222 File and Directory Permissions Modification (11.90%); T1105 Ingress Tool Transfer (2.80%) | 0.05% | False |

## repeat_100 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1592 Gather Victim Host Information (0.01%); T1021 Remote Services (0.01%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.52%); T1548 Abuse Elevation Control Mechanism (0.26%); T1222 File and Directory Permissions Modification (0.06%) | 99.52% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1525 Implant Internal Image (0.01%); T1614 System Location Discovery (0.01%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (86.31%); T1190 Exploit Public-Facing Application (13.40%); T1589 Gather Victim Identity Information (0.11%) | 86.31% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.83%); T1059 Command and Scripting Interpreter (0.06%); T1136 Create Account (0.01%) | 99.83% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (91.26%); T1087 Account Discovery (8.67%); T1105 Ingress Tool Transfer (0.01%) | 8.67% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.55%); T1057 Process Discovery (0.08%); T1614 System Location Discovery (0.07%) | 99.55% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.85%); T1049 System Network Connections Discovery (0.03%); T1071 Application Layer Protocol (0.02%) | 99.85% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1087 Account Discovery (32.45%); T1053 Scheduled Task/Job (25.93%); T1124 System Time Discovery (6.25%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (88.16%); T1486 Data Encrypted for Impact (3.80%); T1595 Active Scanning (2.02%) | 0.00% | False |

## repeat_100 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1569 System Services (0.00%); T1039 Data from Network Shared Drive (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.75%); T1548 Abuse Elevation Control Mechanism (0.11%); T1070 Indicator Removal (0.03%) | 99.75% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.96%); T1049 System Network Connections Discovery (0.01%); T1124 System Time Discovery (0.00%) | 99.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (72.05%); T1190 Exploit Public-Facing Application (27.78%); T1589 Gather Victim Identity Information (0.07%) | 72.05% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.72%); T1218 System Binary Proxy Execution (0.07%); T1105 Ingress Tool Transfer (0.03%) | 99.72% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (83.24%); T1087 Account Discovery (16.68%); T1053 Scheduled Task/Job (0.01%) | 16.68% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.78%); T1201 Password Policy Discovery (0.08%); T1021 Remote Services (0.02%) | 99.78% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.79%); T1041 Exfiltration Over C2 Channel (0.07%); T1049 System Network Connections Discovery (0.04%) | 99.79% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (62.18%); T1071 Application Layer Protocol (27.81%); T1036 Masquerading (1.80%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1071 Application Layer Protocol (68.38%); T1564 Hide Artifacts (27.64%); T1003 OS Credential Dumping (0.81%) | 0.03% | False |

## repeat_100 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.93%); T1592 Gather Victim Host Information (0.04%); T1573 Encrypted Channel (0.01%) | 99.93% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.35%); T1548 Abuse Elevation Control Mechanism (0.53%); T1105 Ingress Tool Transfer (0.04%) | 99.35% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.94%); T1016 System Network Configuration Discovery (0.01%); T1082 System Information Discovery (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (91.85%); T1190 Exploit Public-Facing Application (8.02%); T1589 Gather Victim Identity Information (0.05%) | 91.85% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.81%); T1105 Ingress Tool Transfer (0.03%); T1120 Peripheral Device Discovery (0.02%) | 99.81% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (75.89%); T1087 Account Discovery (23.98%); T1033 System Owner/User Discovery (0.04%) | 23.98% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.93%); T1490 Inhibit System Recovery (0.01%); T1489 Service Stop (0.01%) | 99.93% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.92%); T1120 Peripheral Device Discovery (0.01%); T1016 System Network Configuration Discovery (0.01%) | 99.92% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1486 Data Encrypted for Impact (26.58%); T1485 Data Destruction (20.30%); T1219 Remote Access Tools (11.42%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (45.79%); T1219 Remote Access Tools (34.44%); T1222 File and Directory Permissions Modification (6.50%) | 0.86% | False |

## repeat_100 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1595 Active Scanning (0.02%); T1110 Brute Force (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.82%); T1548 Abuse Elevation Control Mechanism (0.12%); T1059 Command and Scripting Interpreter (0.01%) | 99.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1007 System Service Discovery (0.01%); T1033 System Owner/User Discovery (0.01%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (68.66%); T1190 Exploit Public-Facing Application (31.03%); T1589 Gather Victim Identity Information (0.07%) | 68.66% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.80%); T1222 File and Directory Permissions Modification (0.04%); T1485 Data Destruction (0.02%) | 99.80% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (72.03%); T1059 Command and Scripting Interpreter (27.69%); T1053 Scheduled Task/Job (0.03%) | 72.03% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.36%); T1518 Software Discovery (0.23%); T1204 User Execution (0.12%) | 99.36% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.75%); T1003 OS Credential Dumping (0.05%); T1120 Peripheral Device Discovery (0.03%) | 99.75% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (96.48%); T1490 Inhibit System Recovery (0.47%); T1082 System Information Discovery (0.33%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (60.48%); T1564 Hide Artifacts (17.40%); T1556 Modify Authentication Process (8.77%) | 0.23% | False |

## repeat_100 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.92%); T1120 Peripheral Device Discovery (0.01%); T1564 Hide Artifacts (0.01%) | 99.92% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.61%); T1548 Abuse Elevation Control Mechanism (0.79%); T1070 Indicator Removal (0.27%) | 98.61% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.95%); T1057 Process Discovery (0.01%); T1557 Adversary-in-the-Middle (0.00%) | 99.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (74.14%); T1190 Exploit Public-Facing Application (25.62%); T1589 Gather Victim Identity Information (0.06%) | 74.14% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.74%); T1218 System Binary Proxy Execution (0.07%); T1614 System Location Discovery (0.02%) | 99.74% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (50.59%); T1087 Account Discovery (49.10%); T1033 System Owner/User Discovery (0.06%) | 49.10% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1057 Process Discovery (0.07%); T1072 Software Deployment Tools (0.03%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.83%); T1021 Remote Services (0.07%); T1049 System Network Connections Discovery (0.02%) | 99.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (88.68%); T1133 External Remote Services (1.46%); T1485 Data Destruction (1.13%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (74.14%); T1222 File and Directory Permissions Modification (4.81%); T1528 Steal Application Access Token (4.17%) | 0.02% | False |

## repeat_200 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1213 Data from Information Repositories (0.00%); T1610 Deploy Container (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.97%); T1036 Masquerading (0.01%); T1548 Abuse Elevation Control Mechanism (0.00%) | 99.97% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1018 Remote System Discovery (0.00%); T1053 Scheduled Task/Job (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.93%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.67%); T1059 Command and Scripting Interpreter (0.13%); T1566 Phishing (0.03%) | 99.67% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.99%); T1059 Command and Scripting Interpreter (0.00%); T1105 Ingress Tool Transfer (0.00%) | 99.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1124 System Time Discovery (0.01%); T1543 Create or Modify System Process (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.85%); T1039 Data from Network Shared Drive (0.05%); T1003 OS Credential Dumping (0.03%) | 99.85% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (30.64%); T1592 Gather Victim Host Information (17.87%); T1595 Active Scanning (12.71%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (73.23%); T1071 Application Layer Protocol (7.15%); T1033 System Owner/User Discovery (3.64%) | 0.00% | False |

## repeat_200 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1595 Active Scanning (0.00%); T1560 Archive Collected Data (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.98%); T1036 Masquerading (0.01%); T1548 Abuse Elevation Control Mechanism (0.00%) | 99.98% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1057 Process Discovery (0.00%); T1136 Create Account (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.91%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.89%); T1078 Valid Accounts (0.01%); T1083 File and Directory Discovery (0.01%) | 99.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.98%); T1591 Gather Victim Org Information (0.00%); T1059 Command and Scripting Interpreter (0.00%) | 99.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1124 System Time Discovery (0.02%); T1072 Software Deployment Tools (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.84%); T1120 Peripheral Device Discovery (0.05%); T1039 Data from Network Shared Drive (0.05%) | 99.84% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (67.75%); T1036 Masquerading (6.91%); T1222 File and Directory Permissions Modification (5.03%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1036 Masquerading (53.62%); T1219 Remote Access Tools (7.02%); T1053 Scheduled Task/Job (6.96%) | 5.09% | False |

## repeat_200 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1218 System Binary Proxy Execution (0.00%); T1003 OS Credential Dumping (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.91%); T1548 Abuse Elevation Control Mechanism (0.03%); T1082 System Information Discovery (0.01%) | 99.91% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1057 Process Discovery (0.00%); T1219 Remote Access Tools (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.94%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.01%) | 99.94% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.89%); T1057 Process Discovery (0.01%); T1018 Remote System Discovery (0.01%) | 99.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.35%); T1059 Command and Scripting Interpreter (0.60%); T1082 System Information Discovery (0.00%) | 99.35% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1018 Remote System Discovery (0.01%); T1599 Network Boundary Bridging (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.92%); T1039 Data from Network Shared Drive (0.02%); T1083 File and Directory Discovery (0.01%) | 99.92% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (73.87%); T1222 File and Directory Permissions Modification (11.05%); T1033 System Owner/User Discovery (10.59%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (94.38%); T1222 File and Directory Permissions Modification (4.04%); T1070 Indicator Removal (0.73%) | 0.01% | False |

## repeat_200 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1078 Valid Accounts (0.01%); T1557 Adversary-in-the-Middle (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.98%); T1105 Ingress Tool Transfer (0.01%); T1548 Abuse Elevation Control Mechanism (0.00%) | 99.98% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.99%); T1080 Taint Shared Content (0.00%); T1057 Process Discovery (0.00%) | 99.99% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.91%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.02%) | 99.91% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.84%); T1564 Hide Artifacts (0.02%); T1547 Boot or Logon Autostart Execution (0.02%) | 99.84% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.93%); T1059 Command and Scripting Interpreter (0.03%); T1082 System Information Discovery (0.00%) | 99.93% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1124 System Time Discovery (0.01%); T1557 Adversary-in-the-Middle (0.00%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.85%); T1003 OS Credential Dumping (0.07%); T1039 Data from Network Shared Drive (0.02%) | 99.85% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (55.67%); T1078 Valid Accounts (9.58%); T1546 Event Triggered Execution (7.13%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (30.17%); T1546 Event Triggered Execution (19.88%); T1003 OS Credential Dumping (14.89%) | 0.01% | False |

## repeat_200 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1205 Traffic Signaling (0.00%); T1190 Exploit Public-Facing Application (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.96%); T1082 System Information Discovery (0.01%); T1003 OS Credential Dumping (0.01%) | 99.96% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1057 Process Discovery (0.01%); T1003 OS Credential Dumping (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.91%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.83%); T1059 Command and Scripting Interpreter (0.03%); T1547 Boot or Logon Autostart Execution (0.01%) | 99.83% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.92%); T1033 System Owner/User Discovery (0.02%); T1083 File and Directory Discovery (0.01%) | 99.92% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1124 System Time Discovery (0.01%); T1564 Hide Artifacts (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.87%); T1003 OS Credential Dumping (0.06%); T1039 Data from Network Shared Drive (0.02%) | 99.87% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (92.75%); T1486 Data Encrypted for Impact (2.66%); T1105 Ingress Tool Transfer (1.44%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (40.70%); T1078 Valid Accounts (31.75%); T1041 Exfiltration Over C2 Channel (11.00%) | 0.00% | False |

## repeat_200 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1083 File and Directory Discovery (0.00%); T1531 Account Access Removal (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.95%); T1548 Abuse Elevation Control Mechanism (0.02%); T1105 Ingress Tool Transfer (0.01%) | 99.95% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1201 Password Policy Discovery (0.00%); T1057 Process Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.95%); T1589 Gather Victim Identity Information (0.02%); T1190 Exploit Public-Facing Application (0.01%) | 99.95% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.87%); T1105 Ingress Tool Transfer (0.02%); T1078 Valid Accounts (0.01%) | 99.87% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.99%); T1486 Data Encrypted for Impact (0.00%); T1565 Data Manipulation (0.00%) | 99.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1072 Software Deployment Tools (0.01%); T1059 Command and Scripting Interpreter (0.00%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.88%); T1039 Data from Network Shared Drive (0.07%); T1003 OS Credential Dumping (0.01%) | 99.88% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (16.14%); T1222 File and Directory Permissions Modification (15.86%); T1010 Application Window Discovery (11.88%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1083 File and Directory Discovery (12.95%); T1010 Application Window Discovery (12.80%); T1133 External Remote Services (9.50%) | 0.00% | False |

## repeat_200 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1589 Gather Victim Identity Information (0.00%); T1595 Active Scanning (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.97%); T1548 Abuse Elevation Control Mechanism (0.01%); T1566 Phishing (0.00%) | 99.97% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1057 Process Discovery (0.00%); T1528 Steal Application Access Token (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.93%); T1589 Gather Victim Identity Information (0.03%); T1190 Exploit Public-Facing Application (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.89%); T1222 File and Directory Permissions Modification (0.01%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.98%); T1018 Remote System Discovery (0.00%); T1083 File and Directory Discovery (0.00%) | 99.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.98%); T1124 System Time Discovery (0.00%); T1040 Network Sniffing (0.00%) | 99.98% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.92%); T1039 Data from Network Shared Drive (0.03%); T1120 Peripheral Device Discovery (0.01%) | 99.92% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (64.14%); T1105 Ingress Tool Transfer (28.88%); T1053 Scheduled Task/Job (2.63%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (93.99%); T1071 Application Layer Protocol (1.39%); T1595 Active Scanning (0.65%) | 0.00% | False |

## repeat_200 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1595 Active Scanning (0.00%); T1059 Command and Scripting Interpreter (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.91%); T1105 Ingress Tool Transfer (0.02%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.91% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1082 System Information Discovery (0.00%); T1003 OS Credential Dumping (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.90%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.00%) | 99.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.87%); T1548 Abuse Elevation Control Mechanism (0.01%); T1547 Boot or Logon Autostart Execution (0.01%) | 99.87% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (71.73%); T1087 Account Discovery (28.12%); T1083 File and Directory Discovery (0.03%) | 28.12% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1124 System Time Discovery (0.00%); T1615 Group Policy Discovery (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.90%); T1003 OS Credential Dumping (0.03%); T1039 Data from Network Shared Drive (0.01%) | 99.90% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (60.41%); T1059 Command and Scripting Interpreter (16.18%); T1497 Virtualization/Sandbox Evasion (13.38%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (96.27%); T1222 File and Directory Permissions Modification (1.61%); T1201 Password Policy Discovery (0.34%) | 0.00% | False |

## repeat_200 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1595 Active Scanning (0.01%); T1589 Gather Victim Identity Information (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.95%); T1548 Abuse Elevation Control Mechanism (0.02%); T1105 Ingress Tool Transfer (0.01%) | 99.95% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1201 Password Policy Discovery (0.00%); T1033 System Owner/User Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.91%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.80%); T1059 Command and Scripting Interpreter (0.03%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.80% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.97%); T1059 Command and Scripting Interpreter (0.01%); T1565 Data Manipulation (0.00%) | 99.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1110 Brute Force (0.01%); T1210 Exploitation of Remote Services (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.87%); T1039 Data from Network Shared Drive (0.05%); T1003 OS Credential Dumping (0.02%) | 99.87% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1518 Software Discovery (31.75%); T1546 Event Triggered Execution (9.89%); T1105 Ingress Tool Transfer (9.03%) | 0.13% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (22.50%); T1078 Valid Accounts (10.16%); T1057 Process Discovery (9.40%) | 0.01% | False |

## repeat_200 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.99%); T1005 Data from Local System (0.00%); T1049 System Network Connections Discovery (0.00%) | 99.99% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.95%); T1036 Masquerading (0.01%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.95% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1057 Process Discovery (0.00%); T1095 Non-Application Layer Protocol (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.92%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.02%) | 99.92% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.89%); T1548 Abuse Elevation Control Mechanism (0.02%); T1547 Boot or Logon Autostart Execution (0.01%) | 99.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.98%); T1033 System Owner/User Discovery (0.00%); T1083 File and Directory Discovery (0.00%) | 99.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.98%); T1560 Archive Collected Data (0.00%); T1124 System Time Discovery (0.00%) | 99.98% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.91%); T1039 Data from Network Shared Drive (0.02%); T1049 System Network Connections Discovery (0.01%) | 99.91% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (73.48%); T1595 Active Scanning (7.19%); T1204 User Execution (4.66%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (87.66%); T1591 Gather Victim Org Information (1.82%); T1057 Process Discovery (1.40%) | 0.00% | False |

## repeat_200 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1082 System Information Discovery (0.01%); T1595 Active Scanning (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.80%); T1548 Abuse Elevation Control Mechanism (0.09%); T1218 System Binary Proxy Execution (0.04%) | 99.80% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1543 Create or Modify System Process (0.00%); T1518 Software Discovery (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.86%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.04%) | 99.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.90%); T1219 Remote Access Tools (0.02%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.90% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.99%); T1110 Brute Force (0.00%); T1082 System Information Discovery (0.00%) | 99.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.98%); T1124 System Time Discovery (0.00%); T1115 Clipboard Data (0.00%) | 99.98% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.82%); T1039 Data from Network Shared Drive (0.04%); T1078 Valid Accounts (0.03%) | 99.82% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (95.46%); T1566 Phishing (1.23%); T1016 System Network Configuration Discovery (0.54%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (65.48%); T1614 System Location Discovery (20.00%); T1072 Software Deployment Tools (2.74%) | 0.00% | False |

## repeat_200 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1595 Active Scanning (0.00%); T1566 Phishing (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.94%); T1548 Abuse Elevation Control Mechanism (0.02%); T1105 Ingress Tool Transfer (0.01%) | 99.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1546 Event Triggered Execution (0.00%); T1083 File and Directory Discovery (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.88%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.02%) | 99.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.82%); T1547 Boot or Logon Autostart Execution (0.04%); T1595 Active Scanning (0.02%) | 99.82% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.98%); T1059 Command and Scripting Interpreter (0.00%); T1083 File and Directory Discovery (0.00%) | 99.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1124 System Time Discovery (0.01%); T1485 Data Destruction (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.92%); T1039 Data from Network Shared Drive (0.02%); T1560 Archive Collected Data (0.01%) | 99.92% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1068 Exploitation for Privilege Escalation (24.71%); T1546 Event Triggered Execution (16.20%); T1497 Virtualization/Sandbox Evasion (9.41%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (63.94%); T1548 Abuse Elevation Control Mechanism (20.42%); T1033 System Owner/User Discovery (8.13%) | 0.01% | False |

## repeat_200 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.95%); T1010 Application Window Discovery (0.01%); T1110 Brute Force (0.00%) | 99.95% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.82%); T1548 Abuse Elevation Control Mechanism (0.06%); T1036 Masquerading (0.04%) | 99.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1485 Data Destruction (0.00%); T1201 Password Policy Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.91%); T1589 Gather Victim Identity Information (0.04%); T1190 Exploit Public-Facing Application (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.80%); T1078 Valid Accounts (0.06%); T1201 Password Policy Discovery (0.02%) | 99.80% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.47%); T1059 Command and Scripting Interpreter (0.47%); T1082 System Information Discovery (0.01%) | 99.47% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1219 Remote Access Tools (0.00%); T1574 Hijack Execution Flow (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.90%); T1573 Encrypted Channel (0.03%); T1039 Data from Network Shared Drive (0.02%) | 99.90% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (85.71%); T1222 File and Directory Permissions Modification (1.91%); T1036 Masquerading (1.45%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (94.66%); T1033 System Owner/User Discovery (2.26%); T1222 File and Directory Permissions Modification (0.56%) | 0.00% | False |

## repeat_200 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1110 Brute Force (0.00%); T1133 External Remote Services (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.94%); T1548 Abuse Elevation Control Mechanism (0.02%); T1059 Command and Scripting Interpreter (0.01%) | 99.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.96%); T1057 Process Discovery (0.01%); T1543 Create or Modify System Process (0.00%) | 99.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.86%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.02%) | 99.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.79%); T1021 Remote Services (0.02%); T1059 Command and Scripting Interpreter (0.02%) | 99.79% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.83%); T1059 Command and Scripting Interpreter (0.15%); T1573 Encrypted Channel (0.00%) | 99.83% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1053 Scheduled Task/Job (0.01%); T1040 Network Sniffing (0.01%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.76%); T1003 OS Credential Dumping (0.13%); T1039 Data from Network Shared Drive (0.05%) | 99.76% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (68.94%); T1039 Data from Network Shared Drive (19.04%); T1053 Scheduled Task/Job (2.77%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (45.22%); T1053 Scheduled Task/Job (26.43%); T1059 Command and Scripting Interpreter (10.48%) | 0.02% | False |

## repeat_200 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1021 Remote Services (0.01%); T1595 Active Scanning (0.01%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.94%); T1548 Abuse Elevation Control Mechanism (0.02%); T1497 Virtualization/Sandbox Evasion (0.01%) | 99.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.99%); T1057 Process Discovery (0.00%); T1615 Group Policy Discovery (0.00%) | 99.99% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.89%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.01%) | 99.89% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.83%); T1059 Command and Scripting Interpreter (0.03%); T1105 Ingress Tool Transfer (0.03%) | 99.83% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.97%); T1040 Network Sniffing (0.00%); T1201 Password Policy Discovery (0.00%) | 99.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1016 System Network Configuration Discovery (0.00%); T1072 Software Deployment Tools (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.93%); T1039 Data from Network Shared Drive (0.03%); T1070 Indicator Removal (0.01%) | 99.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (88.81%); T1016 System Network Configuration Discovery (2.51%); T1059 Command and Scripting Interpreter (2.38%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1486 Data Encrypted for Impact (34.71%); T1546 Event Triggered Execution (8.41%); T1072 Software Deployment Tools (7.78%) | 0.05% | False |

## repeat_200 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1569 System Services (0.00%); T1057 Process Discovery (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.88%); T1110 Brute Force (0.02%); T1566 Phishing (0.02%) | 99.88% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1201 Password Policy Discovery (0.00%); T1057 Process Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.91%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.90%); T1039 Data from Network Shared Drive (0.01%); T1010 Application Window Discovery (0.01%) | 99.90% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.96%); T1016 System Network Configuration Discovery (0.00%); T1486 Data Encrypted for Impact (0.00%) | 99.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1573 Encrypted Channel (0.01%); T1124 System Time Discovery (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.91%); T1039 Data from Network Shared Drive (0.02%); T1564 Hide Artifacts (0.01%) | 99.91% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (51.09%); T1059 Command and Scripting Interpreter (13.60%); T1591 Gather Victim Org Information (8.26%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (29.20%); T1105 Ingress Tool Transfer (11.37%); T1036 Masquerading (8.18%) | 0.29% | False |

## repeat_200 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1204 User Execution (0.01%); T1213 Data from Information Repositories (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.97%); T1070 Indicator Removal (0.01%); T1548 Abuse Elevation Control Mechanism (0.00%) | 99.97% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1528 Steal Application Access Token (0.00%); T1222 File and Directory Permissions Modification (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.84%); T1589 Gather Victim Identity Information (0.10%); T1190 Exploit Public-Facing Application (0.03%) | 99.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.77%); T1059 Command and Scripting Interpreter (0.06%); T1039 Data from Network Shared Drive (0.02%) | 99.77% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.99%); T1033 System Owner/User Discovery (0.00%); T1014 Rootkit (0.00%) | 99.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1218 System Binary Proxy Execution (0.01%); T1564 Hide Artifacts (0.01%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.95%); T1039 Data from Network Shared Drive (0.01%); T1564 Hide Artifacts (0.01%) | 99.95% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1204 User Execution (33.70%); T1082 System Information Discovery (20.31%); T1018 Remote System Discovery (12.42%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (25.98%); T1531 Account Access Removal (18.00%); T1490 Inhibit System Recovery (8.45%) | 0.01% | False |

## repeat_200 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1592 Gather Victim Host Information (0.00%); T1557 Adversary-in-the-Middle (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.90%); T1548 Abuse Elevation Control Mechanism (0.04%); T1218 System Binary Proxy Execution (0.03%) | 99.90% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1190 Exploit Public-Facing Application (0.00%); T1518 Software Discovery (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.89%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.01%) | 99.89% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.90%); T1547 Boot or Logon Autostart Execution (0.03%); T1068 Exploitation for Privilege Escalation (0.01%) | 99.90% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.99%); T1068 Exploitation for Privilege Escalation (0.00%); T1041 Exfiltration Over C2 Channel (0.00%) | 99.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1059 Command and Scripting Interpreter (0.00%); T1205 Traffic Signaling (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.94%); T1003 OS Credential Dumping (0.02%); T1016 System Network Configuration Discovery (0.01%) | 99.94% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (44.27%); T1098 Account Manipulation (14.66%); T1566 Phishing (7.18%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (38.70%); T1003 OS Credential Dumping (35.12%); T1566 Phishing (9.06%) | 0.00% | False |

## repeat_200 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1072 Software Deployment Tools (0.00%); T1497 Virtualization/Sandbox Evasion (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.82%); T1548 Abuse Elevation Control Mechanism (0.12%); T1518 Software Discovery (0.01%) | 99.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.96%); T1136 Create Account (0.00%); T1531 Account Access Removal (0.00%) | 99.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.88%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.03%) | 99.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.76%); T1078 Valid Accounts (0.05%); T1547 Boot or Logon Autostart Execution (0.05%) | 99.76% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.99%); T1591 Gather Victim Org Information (0.00%); T1041 Exfiltration Over C2 Channel (0.00%) | 99.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1518 Software Discovery (0.01%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.93%); T1003 OS Credential Dumping (0.02%); T1039 Data from Network Shared Drive (0.01%) | 99.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1574 Hijack Execution Flow (35.05%); T1033 System Owner/User Discovery (34.88%); T1546 Event Triggered Execution (11.57%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (99.70%); T1574 Hijack Execution Flow (0.15%); T1059 Command and Scripting Interpreter (0.05%) | 0.00% | False |

## repeat_200 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1595 Active Scanning (0.01%); T1543 Create or Modify System Process (0.01%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.76%); T1548 Abuse Elevation Control Mechanism (0.05%); T1036 Masquerading (0.04%) | 99.76% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1057 Process Discovery (0.00%); T1110 Brute Force (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.92%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.01%) | 99.92% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.87%); T1105 Ingress Tool Transfer (0.03%); T1021 Remote Services (0.01%) | 99.87% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.97%); T1036 Masquerading (0.01%); T1550 Use Alternate Authentication Material (0.00%) | 99.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.97%); T1485 Data Destruction (0.00%); T1548 Abuse Elevation Control Mechanism (0.00%) | 99.97% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.93%); T1039 Data from Network Shared Drive (0.02%); T1033 System Owner/User Discovery (0.01%) | 99.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1074 Data Staged (12.82%); T1574 Hijack Execution Flow (12.40%); T1222 File and Directory Permissions Modification (10.03%) | 0.18% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1574 Hijack Execution Flow (33.21%); T1599 Network Boundary Bridging (14.07%); T1074 Data Staged (11.25%) | 0.02% | False |

## repeat_200 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1592 Gather Victim Host Information (0.01%); T1098 Account Manipulation (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.87%); T1548 Abuse Elevation Control Mechanism (0.07%); T1059 Command and Scripting Interpreter (0.03%) | 99.87% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.99%); T1070 Indicator Removal (0.00%); T1018 Remote System Discovery (0.00%) | 99.99% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (87.79%); T1190 Exploit Public-Facing Application (12.08%); T1589 Gather Victim Identity Information (0.07%) | 87.79% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.94%); T1078 Valid Accounts (0.02%); T1525 Implant Internal Image (0.00%) | 99.94% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (50.85%); T1087 Account Discovery (49.08%); T1486 Data Encrypted for Impact (0.02%) | 49.08% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1082 System Information Discovery (0.01%); T1614 System Location Discovery (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.90%); T1083 File and Directory Discovery (0.05%); T1039 Data from Network Shared Drive (0.01%) | 99.90% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (69.39%); T1105 Ingress Tool Transfer (24.04%); T1222 File and Directory Permissions Modification (3.41%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (77.47%); T1564 Hide Artifacts (16.19%); T1105 Ingress Tool Transfer (1.87%) | 0.08% | False |

## repeat_200 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1592 Gather Victim Host Information (0.01%); T1057 Process Discovery (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.73%); T1548 Abuse Elevation Control Mechanism (0.15%); T1036 Masquerading (0.05%) | 99.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.99%); T1082 System Information Discovery (0.00%); T1614 System Location Discovery (0.00%) | 99.99% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (82.49%); T1190 Exploit Public-Facing Application (17.40%); T1589 Gather Victim Identity Information (0.05%) | 82.49% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.89%); T1548 Abuse Elevation Control Mechanism (0.02%); T1041 Exfiltration Over C2 Channel (0.01%) | 99.89% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (71.97%); T1087 Account Discovery (27.95%); T1053 Scheduled Task/Job (0.02%) | 27.95% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.95%); T1036 Masquerading (0.01%); T1033 System Owner/User Discovery (0.01%) | 99.95% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.82%); T1049 System Network Connections Discovery (0.09%); T1573 Encrypted Channel (0.02%) | 99.82% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (37.41%); T1021 Remote Services (12.69%); T1105 Ingress Tool Transfer (12.51%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (83.62%); T1543 Create or Modify System Process (5.79%); T1560 Archive Collected Data (1.50%) | 0.00% | False |

## repeat_200 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.98%); T1592 Gather Victim Host Information (0.00%); T1021 Remote Services (0.00%) | 99.98% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.84%); T1548 Abuse Elevation Control Mechanism (0.08%); T1059 Command and Scripting Interpreter (0.01%) | 99.84% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1007 System Service Discovery (0.00%); T1083 File and Directory Discovery (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (85.90%); T1190 Exploit Public-Facing Application (14.00%); T1589 Gather Victim Identity Information (0.03%) | 85.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.93%); T1547 Boot or Logon Autostart Execution (0.02%); T1059 Command and Scripting Interpreter (0.01%) | 99.93% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (91.40%); T1087 Account Discovery (8.54%); T1105 Ingress Tool Transfer (0.01%) | 8.54% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.95%); T1485 Data Destruction (0.01%); T1003 OS Credential Dumping (0.01%) | 99.95% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.93%); T1071 Application Layer Protocol (0.01%); T1021 Remote Services (0.01%) | 99.93% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (77.32%); T1053 Scheduled Task/Job (7.34%); T1070 Indicator Removal (4.30%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (94.20%); T1574 Hijack Execution Flow (1.37%); T1564 Hide Artifacts (1.07%) | 0.03% | False |

## repeat_200 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1595 Active Scanning (0.02%); T1218 System Binary Proxy Execution (0.00%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.89%); T1548 Abuse Elevation Control Mechanism (0.06%); T1059 Command and Scripting Interpreter (0.02%) | 99.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.99%); T1560 Archive Collected Data (0.00%); T1528 Steal Application Access Token (0.00%) | 99.99% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (80.45%); T1190 Exploit Public-Facing Application (19.44%); T1589 Gather Victim Identity Information (0.04%) | 80.45% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.93%); T1547 Boot or Logon Autostart Execution (0.01%); T1041 Exfiltration Over C2 Channel (0.01%) | 99.93% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (69.93%); T1059 Command and Scripting Interpreter (29.92%); T1082 System Information Discovery (0.04%) | 69.93% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1525 Implant Internal Image (0.01%); T1518 Software Discovery (0.01%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.96%); T1120 Peripheral Device Discovery (0.01%); T1573 Encrypted Channel (0.00%) | 99.96% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (72.14%); T1190 Exploit Public-Facing Application (8.65%); T1595 Active Scanning (3.36%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (12.83%); T1016 System Network Configuration Discovery (10.01%); T1005 Data from Local System (9.40%) | 0.48% | False |

## repeat_200 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.99%); T1592 Gather Victim Host Information (0.00%); T1110 Brute Force (0.00%) | 99.99% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.94%); T1059 Command and Scripting Interpreter (0.01%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1068 Exploitation for Privilege Escalation (0.01%); T1518 Software Discovery (0.01%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.47%); T1190 Exploit Public-Facing Application (3.41%); T1589 Gather Victim Identity Information (0.07%) | 96.47% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.94%); T1218 System Binary Proxy Execution (0.01%); T1041 Exfiltration Over C2 Channel (0.01%) | 99.94% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (80.45%); T1059 Command and Scripting Interpreter (19.46%); T1053 Scheduled Task/Job (0.02%) | 80.45% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1016 System Network Configuration Discovery (0.02%); T1615 Group Policy Discovery (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.89%); T1049 System Network Connections Discovery (0.04%); T1059 Command and Scripting Interpreter (0.01%) | 99.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (41.22%); T1033 System Owner/User Discovery (32.38%); T1115 Clipboard Data (6.05%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (59.18%); T1120 Peripheral Device Discovery (10.09%); T1222 File and Directory Permissions Modification (8.01%) | 0.09% | False |

## repeat_200 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1592 Gather Victim Host Information (0.02%); T1021 Remote Services (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.92%); T1548 Abuse Elevation Control Mechanism (0.03%); T1136 Create Account (0.02%) | 99.92% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.99%); T1016 System Network Configuration Discovery (0.00%); T1083 File and Directory Discovery (0.00%) | 99.99% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (97.17%); T1190 Exploit Public-Facing Application (2.67%); T1589 Gather Victim Identity Information (0.11%) | 97.17% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.92%); T1059 Command and Scripting Interpreter (0.03%); T1547 Boot or Logon Autostart Execution (0.01%) | 99.92% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (67.37%); T1087 Account Discovery (32.55%); T1082 System Information Discovery (0.02%) | 32.55% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1614 System Location Discovery (0.01%); T1490 Inhibit System Recovery (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.98%); T1573 Encrypted Channel (0.00%); T1036 Masquerading (0.00%) | 99.98% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (45.28%); T1053 Scheduled Task/Job (33.08%); T1124 System Time Discovery (5.37%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (44.50%); T1592 Gather Victim Host Information (29.89%); T1595 Active Scanning (10.50%) | 0.02% | False |

## repeat_200 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.99%); T1110 Brute Force (0.00%); T1589 Gather Victim Identity Information (0.00%) | 99.99% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.94%); T1548 Abuse Elevation Control Mechanism (0.02%); T1120 Peripheral Device Discovery (0.01%) | 99.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.98%); T1049 System Network Connections Discovery (0.00%); T1087 Account Discovery (0.00%) | 99.98% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (96.24%); T1190 Exploit Public-Facing Application (3.62%); T1589 Gather Victim Identity Information (0.07%) | 96.24% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.93%); T1078 Valid Accounts (0.01%); T1218 System Binary Proxy Execution (0.01%) | 99.93% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (77.90%); T1087 Account Discovery (22.05%); T1053 Scheduled Task/Job (0.01%) | 22.05% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1124 System Time Discovery (0.01%); T1591 Gather Victim Org Information (0.00%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.88%); T1049 System Network Connections Discovery (0.03%); T1201 Password Policy Discovery (0.01%) | 99.88% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (39.18%); T1564 Hide Artifacts (28.49%); T1071 Application Layer Protocol (14.22%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (94.97%); T1071 Application Layer Protocol (2.32%); T1599 Network Boundary Bridging (0.93%) | 0.00% | False |

## repeat_200 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.99%); T1592 Gather Victim Host Information (0.01%); T1573 Encrypted Channel (0.00%) | 99.99% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.96%); T1105 Ingress Tool Transfer (0.02%); T1548 Abuse Elevation Control Mechanism (0.02%) | 99.96% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1518 Software Discovery (0.01%); T1087 Account Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (86.58%); T1190 Exploit Public-Facing Application (13.30%); T1589 Gather Victim Identity Information (0.05%) | 86.58% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.93%); T1105 Ingress Tool Transfer (0.04%); T1218 System Binary Proxy Execution (0.01%) | 99.93% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (50.97%); T1059 Command and Scripting Interpreter (48.93%); T1033 System Owner/User Discovery (0.02%) | 50.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.96%); T1489 Service Stop (0.01%); T1490 Inhibit System Recovery (0.00%) | 99.96% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.90%); T1105 Ingress Tool Transfer (0.03%); T1120 Peripheral Device Discovery (0.02%) | 99.90% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1486 Data Encrypted for Impact (65.87%); T1082 System Information Discovery (16.99%); T1485 Data Destruction (4.38%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (76.53%); T1219 Remote Access Tools (13.04%); T1486 Data Encrypted for Impact (3.27%) | 0.01% | False |

## repeat_200 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.96%); T1595 Active Scanning (0.01%); T1095 Non-Application Layer Protocol (0.00%) | 99.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.96%); T1548 Abuse Elevation Control Mechanism (0.03%); T1136 Create Account (0.00%) | 99.96% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.96%); T1082 System Information Discovery (0.01%); T1033 System Owner/User Discovery (0.01%) | 99.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.09%); T1190 Exploit Public-Facing Application (18.75%); T1589 Gather Victim Identity Information (0.06%) | 81.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.93%); T1033 System Owner/User Discovery (0.01%); T1547 Boot or Logon Autostart Execution (0.01%) | 99.93% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (70.08%); T1059 Command and Scripting Interpreter (29.69%); T1033 System Owner/User Discovery (0.05%) | 70.08% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.94%); T1082 System Information Discovery (0.02%); T1518 Software Discovery (0.01%) | 99.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.95%); T1120 Peripheral Device Discovery (0.01%); T1003 OS Credential Dumping (0.01%) | 99.95% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (28.84%); T1098 Account Manipulation (17.60%); T1136 Create Account (9.40%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (45.89%); T1136 Create Account (17.81%); T1033 System Owner/User Discovery (12.31%) | 0.08% | False |

## repeat_200 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.97%); T1595 Active Scanning (0.02%); T1543 Create or Modify System Process (0.00%) | 99.97% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.91%); T1548 Abuse Elevation Control Mechanism (0.04%); T1036 Masquerading (0.02%) | 99.91% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.97%); T1057 Process Discovery (0.01%); T1615 Group Policy Discovery (0.00%) | 99.97% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (76.01%); T1190 Exploit Public-Facing Application (23.88%); T1589 Gather Victim Identity Information (0.03%) | 76.01% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.92%); T1218 System Binary Proxy Execution (0.02%); T1614 System Location Discovery (0.01%) | 99.92% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (69.26%); T1059 Command and Scripting Interpreter (30.61%); T1053 Scheduled Task/Job (0.03%) | 69.26% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.90%); T1083 File and Directory Discovery (0.03%); T1057 Process Discovery (0.02%) | 99.90% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.89%); T1021 Remote Services (0.02%); T1041 Exfiltration Over C2 Channel (0.02%) | 99.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (40.58%); T1574 Hijack Execution Flow (19.42%); T1213 Data from Information Repositories (8.15%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (65.73%); T1564 Hide Artifacts (12.09%); T1557 Adversary-in-the-Middle (10.37%) | 0.05% | False |

## repeat_25 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1213 Data from Information Repositories (0.03%); T1595 Active Scanning (0.01%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.79%); T1036 Masquerading (0.07%); T1548 Abuse Elevation Control Mechanism (0.05%) | 99.79% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1018 Remote System Discovery (0.03%); T1490 Inhibit System Recovery (0.01%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.83%); T1190 Exploit Public-Facing Application (0.06%); T1589 Gather Victim Identity Information (0.03%) | 99.83% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.19%); T1059 Command and Scripting Interpreter (0.27%); T1566 Phishing (0.08%) | 99.19% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.87%); T1082 System Information Discovery (0.03%); T1059 Command and Scripting Interpreter (0.02%) | 99.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.69%); T1201 Password Policy Discovery (0.04%); T1124 System Time Discovery (0.04%) | 99.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.60%); T1039 Data from Network Shared Drive (0.28%); T1083 File and Directory Discovery (0.20%) | 98.60% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (45.01%); T1548 Abuse Elevation Control Mechanism (9.53%); T1222 File and Directory Permissions Modification (7.08%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (59.26%); T1071 Application Layer Protocol (14.83%); T1070 Indicator Removal (4.75%) | 0.00% | False |

## repeat_25 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1595 Active Scanning (0.05%); T1003 OS Credential Dumping (0.04%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.77%); T1548 Abuse Elevation Control Mechanism (0.06%); T1036 Masquerading (0.05%) | 99.77% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.81%); T1057 Process Discovery (0.02%); T1136 Create Account (0.01%) | 99.81% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.80%); T1190 Exploit Public-Facing Application (0.07%); T1589 Gather Victim Identity Information (0.03%) | 99.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.33%); T1083 File and Directory Discovery (0.10%); T1059 Command and Scripting Interpreter (0.09%) | 99.33% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.86%); T1059 Command and Scripting Interpreter (0.02%); T1053 Scheduled Task/Job (0.01%) | 99.86% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.62%); T1124 System Time Discovery (0.11%); T1072 Software Deployment Tools (0.03%) | 99.62% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.70%); T1039 Data from Network Shared Drive (0.35%); T1120 Peripheral Device Discovery (0.33%) | 98.70% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (48.04%); T1222 File and Directory Permissions Modification (38.43%); T1003 OS Credential Dumping (2.30%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (40.01%); T1218 System Binary Proxy Execution (16.86%); T1204 User Execution (4.12%) | 1.39% | False |

## repeat_25 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.83%); T1218 System Binary Proxy Execution (0.02%); T1007 System Service Discovery (0.01%) | 99.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.76%); T1548 Abuse Elevation Control Mechanism (0.08%); T1082 System Information Discovery (0.04%) | 99.76% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.78%); T1057 Process Discovery (0.05%); T1219 Remote Access Tools (0.05%) | 99.78% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.80%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.05%) | 99.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.97%); T1059 Command and Scripting Interpreter (1.32%); T1547 Boot or Logon Autostart Execution (0.07%) | 97.97% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.60%); T1059 Command and Scripting Interpreter (1.23%); T1082 System Information Discovery (0.02%) | 98.60% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.76%); T1018 Remote System Discovery (0.03%); T1124 System Time Discovery (0.02%) | 99.76% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.06%); T1083 File and Directory Discovery (0.20%); T1039 Data from Network Shared Drive (0.15%) | 99.06% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (56.63%); T1222 File and Directory Permissions Modification (32.32%); T1010 Application Window Discovery (1.67%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (41.63%); T1222 File and Directory Permissions Modification (39.97%); T1070 Indicator Removal (8.88%) | 0.09% | False |

## repeat_25 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.83%); T1557 Adversary-in-the-Middle (0.01%); T1007 System Service Discovery (0.01%) | 99.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.70%); T1548 Abuse Elevation Control Mechanism (0.09%); T1036 Masquerading (0.03%) | 99.70% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1057 Process Discovery (0.01%); T1564 Hide Artifacts (0.01%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.70%); T1589 Gather Victim Identity Information (0.11%); T1190 Exploit Public-Facing Application (0.06%) | 99.70% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (93.98%); T1059 Command and Scripting Interpreter (4.50%); T1105 Ingress Tool Transfer (0.23%) | 93.98% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.60%); T1059 Command and Scripting Interpreter (1.19%); T1082 System Information Discovery (0.03%) | 98.60% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.74%); T1124 System Time Discovery (0.05%); T1053 Scheduled Task/Job (0.02%) | 99.74% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.63%); T1039 Data from Network Shared Drive (0.24%); T1078 Valid Accounts (0.18%) | 98.63% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (48.35%); T1070 Indicator Removal (15.53%); T1003 OS Credential Dumping (6.49%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (69.16%); T1033 System Owner/User Discovery (9.16%); T1546 Event Triggered Execution (5.87%) | 0.00% | False |

## repeat_25 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.79%); T1595 Active Scanning (0.02%); T1205 Traffic Signaling (0.02%) | 99.79% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.93%); T1082 System Information Discovery (0.01%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.93% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.80%); T1057 Process Discovery (0.05%); T1201 Password Policy Discovery (0.02%) | 99.80% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.81%); T1190 Exploit Public-Facing Application (0.07%); T1589 Gather Victim Identity Information (0.04%) | 99.81% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.83%); T1059 Command and Scripting Interpreter (2.42%); T1105 Ingress Tool Transfer (0.14%) | 96.83% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.08%); T1059 Command and Scripting Interpreter (1.68%); T1083 File and Directory Discovery (0.06%) | 98.08% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.69%); T1124 System Time Discovery (0.04%); T1564 Hide Artifacts (0.04%) | 99.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.03%); T1039 Data from Network Shared Drive (0.14%); T1083 File and Directory Discovery (0.13%) | 99.03% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (54.81%); T1071 Application Layer Protocol (19.34%); T1105 Ingress Tool Transfer (3.86%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (25.91%); T1003 OS Credential Dumping (22.00%); T1105 Ingress Tool Transfer (13.54%) | 0.00% | False |

## repeat_25 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1531 Account Access Removal (0.03%); T1083 File and Directory Discovery (0.02%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.71%); T1548 Abuse Elevation Control Mechanism (0.07%); T1105 Ingress Tool Transfer (0.03%) | 99.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.77%); T1057 Process Discovery (0.03%); T1201 Password Policy Discovery (0.02%) | 99.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.80%); T1190 Exploit Public-Facing Application (0.08%); T1589 Gather Victim Identity Information (0.04%) | 99.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.95%); T1059 Command and Scripting Interpreter (1.09%); T1105 Ingress Tool Transfer (0.18%) | 97.95% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (87.56%); T1059 Command and Scripting Interpreter (12.09%); T1531 Account Access Removal (0.02%) | 87.56% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.67%); T1072 Software Deployment Tools (0.09%); T1070 Indicator Removal (0.04%) | 99.67% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.86%); T1039 Data from Network Shared Drive (0.75%); T1573 Encrypted Channel (0.19%) | 97.86% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1083 File and Directory Discovery (9.74%); T1133 External Remote Services (9.35%); T1010 Application Window Discovery (8.92%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1133 External Remote Services (14.59%); T1105 Ingress Tool Transfer (8.78%); T1574 Hijack Execution Flow (8.26%) | 0.01% | False |

## repeat_25 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1589 Gather Victim Identity Information (0.02%); T1039 Data from Network Shared Drive (0.01%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.93%); T1548 Abuse Elevation Control Mechanism (0.01%); T1566 Phishing (0.01%) | 99.93% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.82%); T1222 File and Directory Permissions Modification (0.02%); T1046 Network Service Scanning (0.01%) | 99.82% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.83%); T1070 Indicator Removal (0.03%); T1589 Gather Victim Identity Information (0.03%) | 99.83% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (95.52%); T1059 Command and Scripting Interpreter (3.30%); T1105 Ingress Tool Transfer (0.18%) | 95.52% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.59%); T1059 Command and Scripting Interpreter (0.23%); T1543 Create or Modify System Process (0.02%) | 99.59% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1124 System Time Discovery (0.01%); T1218 System Binary Proxy Execution (0.01%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.87%); T1039 Data from Network Shared Drive (0.42%); T1120 Peripheral Device Discovery (0.22%) | 98.87% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (58.60%); T1053 Scheduled Task/Job (13.76%); T1105 Ingress Tool Transfer (9.80%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (83.64%); T1595 Active Scanning (4.23%); T1059 Command and Scripting Interpreter (3.27%) | 0.00% | False |

## repeat_25 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1059 Command and Scripting Interpreter (0.03%); T1007 System Service Discovery (0.02%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.83%); T1548 Abuse Elevation Control Mechanism (0.04%); T1105 Ingress Tool Transfer (0.03%) | 99.83% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1082 System Information Discovery (0.02%); T1057 Process Discovery (0.02%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.77%); T1190 Exploit Public-Facing Application (0.09%); T1589 Gather Victim Identity Information (0.04%) | 99.77% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.32%); T1059 Command and Scripting Interpreter (0.15%); T1105 Ingress Tool Transfer (0.12%) | 99.32% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.85%); T1059 Command and Scripting Interpreter (0.02%); T1124 System Time Discovery (0.01%) | 99.85% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.63%); T1566 Phishing (0.10%); T1059 Command and Scripting Interpreter (0.04%) | 99.63% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.18%); T1120 Peripheral Device Discovery (0.23%); T1078 Valid Accounts (0.22%) | 98.18% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1497 Virtualization/Sandbox Evasion (42.49%); T1564 Hide Artifacts (26.81%); T1222 File and Directory Permissions Modification (4.07%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (55.17%); T1222 File and Directory Permissions Modification (9.02%); T1201 Password Policy Discovery (7.09%) | 0.02% | False |

## repeat_25 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.73%); T1595 Active Scanning (0.03%); T1204 User Execution (0.03%) | 99.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.68%); T1548 Abuse Elevation Control Mechanism (0.11%); T1105 Ingress Tool Transfer (0.03%) | 99.68% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.76%); T1033 System Owner/User Discovery (0.02%); T1531 Account Access Removal (0.01%) | 99.76% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.73%); T1589 Gather Victim Identity Information (0.08%); T1190 Exploit Public-Facing Application (0.07%) | 99.73% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (91.30%); T1059 Command and Scripting Interpreter (6.58%); T1547 Boot or Logon Autostart Execution (0.41%) | 91.30% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.63%); T1595 Active Scanning (0.04%); T1083 File and Directory Discovery (0.03%) | 99.63% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.57%); T1110 Brute Force (0.06%); T1210 Exploitation of Remote Services (0.04%) | 99.57% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.83%); T1039 Data from Network Shared Drive (0.38%); T1120 Peripheral Device Discovery (0.11%) | 98.83% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1204 User Execution (32.35%); T1566 Phishing (17.18%); T1222 File and Directory Permissions Modification (8.26%) | 0.13% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1566 Phishing (27.14%); T1033 System Owner/User Discovery (14.99%); T1057 Process Discovery (12.05%) | 0.02% | False |

## repeat_25 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.82%); T1218 System Binary Proxy Execution (0.01%); T1018 Remote System Discovery (0.01%) | 99.82% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.33%); T1548 Abuse Elevation Control Mechanism (0.33%); T1036 Masquerading (0.08%) | 99.33% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.75%); T1057 Process Discovery (0.05%); T1557 Adversary-in-the-Middle (0.02%) | 99.75% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.75%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.06%) | 99.75% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.21%); T1059 Command and Scripting Interpreter (0.98%); T1105 Ingress Tool Transfer (0.06%) | 98.21% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.73%); T1059 Command and Scripting Interpreter (0.11%); T1003 OS Credential Dumping (0.02%) | 99.73% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.69%); T1560 Archive Collected Data (0.02%); T1124 System Time Discovery (0.02%) | 99.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.32%); T1039 Data from Network Shared Drive (0.44%); T1049 System Network Connections Discovery (0.24%) | 98.32% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1204 User Execution (21.95%); T1564 Hide Artifacts (18.70%); T1222 File and Directory Permissions Modification (15.94%) | 0.36% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (94.08%); T1218 System Binary Proxy Execution (0.71%); T1591 Gather Victim Org Information (0.44%) | 0.00% | False |

## repeat_25 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.67%); T1595 Active Scanning (0.04%); T1528 Steal Application Access Token (0.02%) | 99.67% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.55%); T1548 Abuse Elevation Control Mechanism (0.19%); T1036 Masquerading (0.12%) | 99.55% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.82%); T1518 Software Discovery (0.02%); T1543 Create or Modify System Process (0.02%) | 99.82% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.80%); T1190 Exploit Public-Facing Application (0.07%); T1589 Gather Victim Identity Information (0.03%) | 99.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.29%); T1059 Command and Scripting Interpreter (0.19%); T1547 Boot or Logon Autostart Execution (0.05%) | 99.29% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.87%); T1083 File and Directory Discovery (0.02%); T1082 System Information Discovery (0.02%) | 99.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1124 System Time Discovery (0.03%); T1068 Exploitation for Privilege Escalation (0.01%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.49%); T1039 Data from Network Shared Drive (0.41%); T1078 Valid Accounts (0.19%) | 98.49% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (85.87%); T1016 System Network Configuration Discovery (3.36%); T1566 Phishing (1.78%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (23.02%); T1190 Exploit Public-Facing Application (6.23%); T1124 System Time Discovery (5.59%) | 0.05% | False |

## repeat_25 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.70%); T1110 Brute Force (0.04%); T1595 Active Scanning (0.03%) | 99.70% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.26%); T1548 Abuse Elevation Control Mechanism (0.21%); T1036 Masquerading (0.16%) | 99.26% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.81%); T1083 File and Directory Discovery (0.02%); T1204 User Execution (0.01%) | 99.81% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.69%); T1190 Exploit Public-Facing Application (0.12%); T1589 Gather Victim Identity Information (0.07%) | 99.69% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.78%); T1059 Command and Scripting Interpreter (1.25%); T1595 Active Scanning (0.11%) | 97.78% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.81%); T1070 Indicator Removal (0.02%); T1053 Scheduled Task/Job (0.01%) | 99.81% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1124 System Time Discovery (0.03%); T1082 System Information Discovery (0.02%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.72%); T1039 Data from Network Shared Drive (0.36%); T1078 Valid Accounts (0.08%) | 98.72% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (29.56%); T1105 Ingress Tool Transfer (22.26%); T1566 Phishing (8.24%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (92.14%); T1548 Abuse Elevation Control Mechanism (1.97%); T1033 System Owner/User Discovery (1.74%) | 0.00% | False |

## repeat_25 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.65%); T1071 Application Layer Protocol (0.03%); T1219 Remote Access Tools (0.03%) | 99.65% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.79%); T1548 Abuse Elevation Control Mechanism (0.09%); T1003 OS Credential Dumping (0.01%) | 99.79% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.80%); T1057 Process Discovery (0.03%); T1485 Data Destruction (0.02%) | 99.80% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.71%); T1190 Exploit Public-Facing Application (0.07%); T1589 Gather Victim Identity Information (0.06%) | 99.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (91.94%); T1059 Command and Scripting Interpreter (6.56%); T1078 Valid Accounts (0.23%) | 91.94% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (97.70%); T1059 Command and Scripting Interpreter (2.09%); T1124 System Time Discovery (0.02%) | 97.70% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.75%); T1110 Brute Force (0.02%); T1219 Remote Access Tools (0.02%) | 99.75% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.46%); T1039 Data from Network Shared Drive (0.29%); T1614 System Location Discovery (0.24%) | 98.46% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (43.92%); T1222 File and Directory Permissions Modification (11.14%); T1518 Software Discovery (10.10%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (37.23%); T1033 System Owner/User Discovery (19.74%); T1222 File and Directory Permissions Modification (13.94%) | 0.03% | False |

## repeat_25 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.73%); T1110 Brute Force (0.03%); T1557 Adversary-in-the-Middle (0.02%) | 99.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.69%); T1548 Abuse Elevation Control Mechanism (0.15%); T1059 Command and Scripting Interpreter (0.03%) | 99.69% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.70%); T1057 Process Discovery (0.05%); T1518 Software Discovery (0.03%) | 99.70% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.60%); T1589 Gather Victim Identity Information (0.10%); T1190 Exploit Public-Facing Application (0.07%) | 99.60% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.72%); T1059 Command and Scripting Interpreter (2.29%); T1564 Hide Artifacts (0.06%) | 96.72% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (95.78%); T1059 Command and Scripting Interpreter (3.95%); T1201 Password Policy Discovery (0.02%) | 95.78% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.71%); T1040 Network Sniffing (0.03%); T1053 Scheduled Task/Job (0.02%) | 99.71% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.65%); T1003 OS Credential Dumping (1.24%); T1039 Data from Network Shared Drive (0.32%) | 97.65% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1039 Data from Network Shared Drive (38.36%); T1222 File and Directory Permissions Modification (24.82%); T1053 Scheduled Task/Job (9.90%) | 0.15% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (54.64%); T1039 Data from Network Shared Drive (11.81%); T1053 Scheduled Task/Job (4.26%) | 0.11% | False |

## repeat_25 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.66%); T1595 Active Scanning (0.03%); T1136 Create Account (0.03%) | 99.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.01%); T1548 Abuse Elevation Control Mechanism (0.50%); T1036 Masquerading (0.15%) | 99.01% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.77%); T1057 Process Discovery (0.03%); T1615 Group Policy Discovery (0.02%) | 99.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.65%); T1190 Exploit Public-Facing Application (0.11%); T1589 Gather Victim Identity Information (0.06%) | 99.65% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (90.67%); T1059 Command and Scripting Interpreter (7.92%); T1105 Ingress Tool Transfer (0.38%) | 90.67% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (98.70%); T1087 Account Discovery (1.16%); T1574 Hijack Execution Flow (0.01%) | 1.16% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.70%); T1124 System Time Discovery (0.05%); T1059 Command and Scripting Interpreter (0.02%) | 99.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.97%); T1070 Indicator Removal (0.21%); T1039 Data from Network Shared Drive (0.18%) | 98.97% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (87.90%); T1120 Peripheral Device Discovery (2.80%); T1546 Event Triggered Execution (2.62%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (85.00%); T1546 Event Triggered Execution (4.51%); T1078 Valid Accounts (1.72%) | 0.03% | False |

## repeat_25 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1057 Process Discovery (0.02%); T1083 File and Directory Discovery (0.02%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.49%); T1548 Abuse Elevation Control Mechanism (0.80%); T1566 Phishing (0.10%) | 98.49% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.74%); T1033 System Owner/User Discovery (0.03%); T1201 Password Policy Discovery (0.02%) | 99.74% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.71%); T1190 Exploit Public-Facing Application (0.09%); T1589 Gather Victim Identity Information (0.08%) | 99.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.39%); T1059 Command and Scripting Interpreter (0.60%); T1190 Exploit Public-Facing Application (0.12%) | 98.39% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.77%); T1007 System Service Discovery (0.02%); T1016 System Network Configuration Discovery (0.02%) | 99.77% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.47%); T1573 Encrypted Channel (0.08%); T1059 Command and Scripting Interpreter (0.05%) | 99.47% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.89%); T1039 Data from Network Shared Drive (0.20%); T1564 Hide Artifacts (0.15%) | 98.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (18.34%); T1213 Data from Information Repositories (11.31%); T1059 Command and Scripting Interpreter (10.65%) | 0.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (15.83%); T1565 Data Manipulation (14.89%); T1053 Scheduled Task/Job (11.41%) | 1.79% | False |

## repeat_25 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.78%); T1213 Data from Information Repositories (0.02%); T1222 File and Directory Permissions Modification (0.02%) | 99.78% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.73%); T1548 Abuse Elevation Control Mechanism (0.05%); T1010 Application Window Discovery (0.03%) | 99.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1528 Steal Application Access Token (0.01%); T1485 Data Destruction (0.01%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.71%); T1190 Exploit Public-Facing Application (0.13%); T1589 Gather Victim Identity Information (0.06%) | 99.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.13%); T1059 Command and Scripting Interpreter (0.19%); T1039 Data from Network Shared Drive (0.12%) | 99.13% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.89%); T1059 Command and Scripting Interpreter (0.03%); T1033 System Owner/User Discovery (0.01%) | 99.89% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.83%); T1564 Hide Artifacts (0.03%); T1018 Remote System Discovery (0.01%) | 99.83% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.37%); T1039 Data from Network Shared Drive (0.15%); T1041 Exfiltration Over C2 Channel (0.06%) | 99.37% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (56.58%); T1490 Inhibit System Recovery (5.72%); T1614 System Location Discovery (5.53%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (16.75%); T1490 Inhibit System Recovery (15.03%); T1040 Network Sniffing (12.34%) | 0.02% | False |

## repeat_25 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.74%); T1592 Gather Victim Host Information (0.04%); T1557 Adversary-in-the-Middle (0.03%) | 99.74% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.36%); T1548 Abuse Elevation Control Mechanism (0.16%); T1218 System Binary Proxy Execution (0.10%) | 99.36% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1190 Exploit Public-Facing Application (0.01%); T1053 Scheduled Task/Job (0.01%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.76%); T1589 Gather Victim Identity Information (0.07%); T1190 Exploit Public-Facing Application (0.06%) | 99.76% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.82%); T1059 Command and Scripting Interpreter (1.07%); T1105 Ingress Tool Transfer (0.14%) | 97.82% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.83%); T1068 Exploitation for Privilege Escalation (0.04%); T1033 System Owner/User Discovery (0.02%) | 99.83% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.82%); T1059 Command and Scripting Interpreter (0.02%); T1039 Data from Network Shared Drive (0.02%) | 99.82% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.30%); T1039 Data from Network Shared Drive (0.16%); T1016 System Network Configuration Discovery (0.12%) | 99.30% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (55.74%); T1071 Application Layer Protocol (20.85%); T1098 Account Manipulation (3.59%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (49.17%); T1105 Ingress Tool Transfer (20.71%); T1082 System Information Discovery (10.10%) | 0.00% | False |

## repeat_25 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.73%); T1087 Account Discovery (0.03%); T1573 Encrypted Channel (0.02%) | 99.73% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.44%); T1548 Abuse Elevation Control Mechanism (0.17%); T1518 Software Discovery (0.08%) | 99.44% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.72%); T1222 File and Directory Permissions Modification (0.03%); T1057 Process Discovery (0.02%) | 99.72% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.77%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.05%) | 99.77% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (96.62%); T1059 Command and Scripting Interpreter (2.16%); T1547 Boot or Logon Autostart Execution (0.14%) | 96.62% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.87%); T1059 Command and Scripting Interpreter (0.03%); T1591 Gather Victim Org Information (0.01%) | 99.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.68%); T1518 Software Discovery (0.09%); T1033 System Owner/User Discovery (0.02%) | 99.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.97%); T1039 Data from Network Shared Drive (0.29%); T1574 Hijack Execution Flow (0.10%) | 98.97% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1574 Hijack Execution Flow (57.08%); T1041 Exfiltration Over C2 Channel (11.62%); T1003 OS Credential Dumping (6.06%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1574 Hijack Execution Flow (39.79%); T1033 System Owner/User Discovery (27.02%); T1041 Exfiltration Over C2 Channel (9.13%) | 0.04% | False |

## repeat_25 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.70%); T1005 Data from Local System (0.04%); T1595 Active Scanning (0.03%) | 99.70% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.31%); T1548 Abuse Elevation Control Mechanism (0.17%); T1036 Masquerading (0.09%) | 99.31% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1057 Process Discovery (0.05%); T1201 Password Policy Discovery (0.02%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.70%); T1589 Gather Victim Identity Information (0.08%); T1190 Exploit Public-Facing Application (0.05%) | 99.70% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.65%); T1059 Command and Scripting Interpreter (1.60%); T1547 Boot or Logon Autostart Execution (0.05%) | 97.65% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.78%); T1036 Masquerading (0.05%); T1550 Use Alternate Authentication Material (0.04%) | 99.78% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.71%); T1485 Data Destruction (0.04%); T1124 System Time Discovery (0.03%) | 99.71% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.21%); T1039 Data from Network Shared Drive (0.08%); T1003 OS Credential Dumping (0.08%) | 99.21% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (13.76%); T1591 Gather Victim Org Information (12.28%); T1016 System Network Configuration Discovery (6.55%) | 0.37% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (40.56%); T1016 System Network Configuration Discovery (8.21%); T1021 Remote Services (8.00%) | 0.04% | False |

## repeat_25 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.84%); T1614 System Location Discovery (0.01%); T1098 Account Manipulation (0.01%) | 99.84% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (96.67%); T1548 Abuse Elevation Control Mechanism (2.94%); T1136 Create Account (0.04%) | 96.67% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1543 Create or Modify System Process (0.02%); T1053 Scheduled Task/Job (0.02%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (68.03%); T1190 Exploit Public-Facing Application (31.58%); T1589 Gather Victim Identity Information (0.07%) | 68.03% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.35%); T1082 System Information Discovery (0.06%); T1078 Valid Accounts (0.06%) | 99.35% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (68.81%); T1087 Account Discovery (30.86%); T1120 Peripheral Device Discovery (0.04%) | 30.86% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.77%); T1614 System Location Discovery (0.01%); T1518 Software Discovery (0.01%) | 99.77% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.96%); T1039 Data from Network Shared Drive (0.21%); T1071 Application Layer Protocol (0.14%) | 98.96% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (57.45%); T1105 Ingress Tool Transfer (33.91%); T1082 System Information Discovery (1.13%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (42.68%); T1222 File and Directory Permissions Modification (41.04%); T1082 System Information Discovery (2.56%) | 0.04% | False |

## repeat_25 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1592 Gather Victim Host Information (0.04%); T1573 Encrypted Channel (0.02%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.73%); T1548 Abuse Elevation Control Mechanism (0.97%); T1105 Ingress Tool Transfer (0.11%) | 98.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.74%); T1040 Network Sniffing (0.03%); T1083 File and Directory Discovery (0.03%) | 99.74% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (50.41%); T1190 Exploit Public-Facing Application (49.08%); T1059 Command and Scripting Interpreter (0.09%) | 50.41% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.48%); T1059 Command and Scripting Interpreter (0.04%); T1005 Data from Local System (0.03%) | 99.48% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (59.66%); T1059 Command and Scripting Interpreter (39.79%); T1053 Scheduled Task/Job (0.21%) | 59.66% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.82%); T1072 Software Deployment Tools (0.02%); T1490 Inhibit System Recovery (0.02%) | 99.82% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.06%); T1049 System Network Connections Discovery (0.54%); T1573 Encrypted Channel (0.18%) | 98.06% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (39.70%); T1021 Remote Services (18.03%); T1105 Ingress Tool Transfer (10.78%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (32.10%); T1222 File and Directory Permissions Modification (10.61%); T1105 Ingress Tool Transfer (8.25%) | 0.12% | False |

## repeat_25 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1071 Application Layer Protocol (0.03%); T1070 Indicator Removal (0.01%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.62%); T1548 Abuse Elevation Control Mechanism (0.25%); T1059 Command and Scripting Interpreter (0.02%) | 99.62% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.81%); T1490 Inhibit System Recovery (0.01%); T1036 Masquerading (0.01%) | 99.81% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (68.94%); T1190 Exploit Public-Facing Application (30.62%); T1589 Gather Victim Identity Information (0.06%) | 68.94% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.80%); T1059 Command and Scripting Interpreter (0.54%); T1033 System Owner/User Discovery (0.11%) | 98.80% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (95.60%); T1087 Account Discovery (4.31%); T1033 System Owner/User Discovery (0.01%) | 4.31% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.35%); T1485 Data Destruction (0.12%); T1531 Account Access Removal (0.12%) | 99.35% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.82%); T1021 Remote Services (0.19%); T1573 Encrypted Channel (0.16%) | 98.82% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (49.45%); T1070 Indicator Removal (30.31%); T1098 Account Manipulation (3.43%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (93.39%); T1564 Hide Artifacts (2.35%); T1070 Indicator Removal (0.95%) | 0.03% | False |

## repeat_25 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.79%); T1098 Account Manipulation (0.02%); T1595 Active Scanning (0.01%) | 99.79% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.48%); T1548 Abuse Elevation Control Mechanism (0.34%); T1136 Create Account (0.05%) | 99.48% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1201 Password Policy Discovery (0.01%); T1082 System Information Discovery (0.01%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (77.90%); T1190 Exploit Public-Facing Application (21.69%); T1589 Gather Victim Identity Information (0.10%) | 77.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (97.79%); T1059 Command and Scripting Interpreter (1.09%); T1218 System Binary Proxy Execution (0.21%) | 97.79% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (56.71%); T1087 Account Discovery (42.78%); T1082 System Information Discovery (0.10%) | 42.78% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.68%); T1124 System Time Discovery (0.06%); T1525 Implant Internal Image (0.03%) | 99.68% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.18%); T1049 System Network Connections Discovery (0.45%); T1041 Exfiltration Over C2 Channel (0.31%) | 98.18% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1190 Exploit Public-Facing Application (14.61%); T1068 Exploitation for Privilege Escalation (8.78%); T1014 Rootkit (7.54%) | 0.15% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (48.09%); T1564 Hide Artifacts (11.83%); T1222 File and Directory Permissions Modification (9.79%) | 0.94% | False |

## repeat_25 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.82%); T1595 Active Scanning (0.03%); T1592 Gather Victim Host Information (0.02%) | 99.82% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (98.82%); T1548 Abuse Elevation Control Mechanism (0.83%); T1070 Indicator Removal (0.06%) | 98.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1068 Exploitation for Privilege Escalation (0.04%); T1486 Data Encrypted for Impact (0.02%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (70.35%); T1190 Exploit Public-Facing Application (29.21%); T1589 Gather Victim Identity Information (0.07%) | 70.35% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.18%); T1059 Command and Scripting Interpreter (0.21%); T1105 Ingress Tool Transfer (0.18%) | 99.18% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (80.32%); T1087 Account Discovery (19.49%); T1486 Data Encrypted for Impact (0.02%) | 19.49% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.26%); T1016 System Network Configuration Discovery (0.27%); T1036 Masquerading (0.05%) | 99.26% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.11%); T1083 File and Directory Discovery (0.12%); T1049 System Network Connections Discovery (0.09%) | 99.11% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (22.62%); T1105 Ingress Tool Transfer (14.96%); T1564 Hide Artifacts (14.62%) | 0.13% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (36.35%); T1033 System Owner/User Discovery (18.29%); T1564 Hide Artifacts (17.65%) | 0.16% | False |

## repeat_25 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.82%); T1592 Gather Victim Host Information (0.02%); T1021 Remote Services (0.01%) | 99.82% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (95.64%); T1548 Abuse Elevation Control Mechanism (3.36%); T1105 Ingress Tool Transfer (0.52%) | 95.64% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.80%); T1525 Implant Internal Image (0.02%); T1083 File and Directory Discovery (0.02%) | 99.80% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (85.03%); T1190 Exploit Public-Facing Application (14.56%); T1589 Gather Victim Identity Information (0.11%) | 85.03% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.36%); T1059 Command and Scripting Interpreter (0.25%); T1083 File and Directory Discovery (0.05%) | 99.36% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (84.89%); T1087 Account Discovery (14.90%); T1053 Scheduled Task/Job (0.07%) | 14.90% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.57%); T1070 Indicator Removal (0.11%); T1614 System Location Discovery (0.07%) | 99.57% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.09%); T1574 Hijack Execution Flow (0.15%); T1053 Scheduled Task/Job (0.12%) | 99.09% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1573 Encrypted Channel (13.95%); T1591 Gather Victim Org Information (13.41%); T1210 Exploitation of Remote Services (8.48%) | 0.64% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (41.42%); T1564 Hide Artifacts (13.26%); T1592 Gather Victim Host Information (7.83%) | 0.04% | False |

## repeat_25 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1610 Deploy Container (0.01%); T1569 System Services (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.56%); T1548 Abuse Elevation Control Mechanism (0.16%); T1120 Peripheral Device Discovery (0.08%) | 99.56% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1049 System Network Connections Discovery (0.02%); T1087 Account Discovery (0.01%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (70.97%); T1190 Exploit Public-Facing Application (28.60%); T1592 Gather Victim Host Information (0.12%) | 70.97% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.15%); T1059 Command and Scripting Interpreter (0.20%); T1105 Ingress Tool Transfer (0.11%) | 99.15% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (67.96%); T1059 Command and Scripting Interpreter (31.59%); T1053 Scheduled Task/Job (0.05%) | 67.96% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.77%); T1041 Exfiltration Over C2 Channel (0.04%); T1557 Adversary-in-the-Middle (0.03%) | 99.77% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.63%); T1105 Ingress Tool Transfer (0.21%); T1041 Exfiltration Over C2 Channel (0.20%) | 98.63% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (53.80%); T1071 Application Layer Protocol (10.20%); T1564 Hide Artifacts (10.10%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (57.78%); T1071 Application Layer Protocol (22.87%); T1222 File and Directory Permissions Modification (8.87%) | 0.34% | False |

## repeat_25 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1592 Gather Victim Host Information (0.06%); T1095 Non-Application Layer Protocol (0.01%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.31%); T1548 Abuse Elevation Control Mechanism (0.42%); T1059 Command and Scripting Interpreter (0.07%) | 99.31% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.73%); T1003 OS Credential Dumping (0.03%); T1016 System Network Configuration Discovery (0.03%) | 99.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (59.38%); T1190 Exploit Public-Facing Application (40.22%); T1589 Gather Victim Identity Information (0.06%) | 59.38% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.77%); T1059 Command and Scripting Interpreter (0.46%); T1564 Hide Artifacts (0.16%) | 98.77% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (51.53%); T1059 Command and Scripting Interpreter (48.23%); T1069 Permission Groups Discovery (0.03%) | 51.53% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.72%); T1489 Service Stop (0.05%); T1049 System Network Connections Discovery (0.02%) | 99.72% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.52%); T1049 System Network Connections Discovery (0.08%); T1016 System Network Configuration Discovery (0.07%) | 99.52% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1485 Data Destruction (27.75%); T1486 Data Encrypted for Impact (25.89%); T1531 Account Access Removal (9.11%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (63.08%); T1219 Remote Access Tools (15.52%); T1486 Data Encrypted for Impact (4.60%) | 0.22% | False |

## repeat_25 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.65%); T1589 Gather Victim Identity Information (0.05%); T1595 Active Scanning (0.05%) | 99.65% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (89.61%); T1548 Abuse Elevation Control Mechanism (9.24%); T1036 Masquerading (0.23%) | 89.61% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.77%); T1614 System Location Discovery (0.02%); T1120 Peripheral Device Discovery (0.02%) | 99.77% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (55.59%); T1190 Exploit Public-Facing Application (43.82%); T1589 Gather Victim Identity Information (0.09%) | 55.59% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.81%); T1564 Hide Artifacts (0.21%); T1218 System Binary Proxy Execution (0.15%) | 98.81% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (57.61%); T1087 Account Discovery (42.04%); T1053 Scheduled Task/Job (0.03%) | 42.04% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.49%); T1518 Software Discovery (0.09%); T1082 System Information Discovery (0.04%) | 99.49% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.56%); T1041 Exfiltration Over C2 Channel (0.51%); T1021 Remote Services (0.13%) | 98.56% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (76.88%); T1098 Account Manipulation (3.09%); T1136 Create Account (3.01%) | 0.05% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (30.27%); T1033 System Owner/User Discovery (15.23%); T1556 Modify Authentication Process (13.31%) | 0.27% | False |

## repeat_25 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.83%); T1543 Create or Modify System Process (0.02%); T1592 Gather Victim Host Information (0.01%) | 99.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.46%); T1548 Abuse Elevation Control Mechanism (0.38%); T1105 Ingress Tool Transfer (0.03%) | 99.46% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1057 Process Discovery (0.02%); T1557 Adversary-in-the-Middle (0.02%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (71.06%); T1190 Exploit Public-Facing Application (28.44%); T1592 Gather Victim Host Information (0.09%) | 71.06% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.22%); T1059 Command and Scripting Interpreter (0.08%); T1218 System Binary Proxy Execution (0.06%) | 99.22% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (61.49%); T1087 Account Discovery (38.02%); T1053 Scheduled Task/Job (0.10%) | 38.02% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.61%); T1072 Software Deployment Tools (0.07%); T1057 Process Discovery (0.04%) | 99.61% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.74%); T1021 Remote Services (0.44%); T1049 System Network Connections Discovery (0.13%) | 98.74% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (49.26%); T1574 Hijack Execution Flow (11.35%); T1213 Data from Information Repositories (8.12%) | 0.25% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (60.54%); T1018 Remote System Discovery (6.74%); T1528 Steal Application Access Token (6.21%) | 0.01% | False |

## repeat_50 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.89%); T1213 Data from Information Repositories (0.01%); T1120 Peripheral Device Discovery (0.01%) | 99.89% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.74%); T1036 Masquerading (0.15%); T1548 Abuse Elevation Control Mechanism (0.03%) | 99.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.91%); T1018 Remote System Discovery (0.02%); T1490 Inhibit System Recovery (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.85%); T1190 Exploit Public-Facing Application (0.06%); T1589 Gather Victim Identity Information (0.02%) | 99.85% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.53%); T1059 Command and Scripting Interpreter (0.17%); T1566 Phishing (0.04%) | 99.53% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.91%); T1082 System Information Discovery (0.02%); T1548 Abuse Elevation Control Mechanism (0.01%) | 99.91% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.84%); T1124 System Time Discovery (0.02%); T1201 Password Policy Discovery (0.02%) | 99.84% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.33%); T1003 OS Credential Dumping (0.34%); T1039 Data from Network Shared Drive (0.34%) | 98.33% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (21.62%); T1595 Active Scanning (16.64%); T1222 File and Directory Permissions Modification (11.67%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (53.05%); T1071 Application Layer Protocol (21.28%); T1595 Active Scanning (6.17%) | 0.00% | False |

## repeat_50 / GRU / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.86%); T1003 OS Credential Dumping (0.03%); T1595 Active Scanning (0.02%) | 99.86% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.73%); T1548 Abuse Elevation Control Mechanism (0.10%); T1036 Masquerading (0.07%) | 99.73% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1057 Process Discovery (0.01%); T1201 Password Policy Discovery (0.01%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.86%); T1190 Exploit Public-Facing Application (0.05%); T1589 Gather Victim Identity Information (0.03%) | 99.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.67%); T1518 Software Discovery (0.06%); T1078 Valid Accounts (0.05%) | 99.67% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.75%); T1059 Command and Scripting Interpreter (0.13%); T1591 Gather Victim Org Information (0.02%) | 99.75% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.73%); T1124 System Time Discovery (0.09%); T1072 Software Deployment Tools (0.02%) | 99.73% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.24%); T1120 Peripheral Device Discovery (0.27%); T1039 Data from Network Shared Drive (0.17%) | 99.24% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (64.44%); T1591 Gather Victim Org Information (26.95%); T1565 Data Manipulation (0.86%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (36.78%); T1218 System Binary Proxy Execution (12.70%); T1204 User Execution (7.60%) | 0.67% | False |

## repeat_50 / GRU / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1218 System Binary Proxy Execution (0.01%); T1036 Masquerading (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1548 Abuse Elevation Control Mechanism (0.04%); T1082 System Information Discovery (0.02%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1057 Process Discovery (0.02%); T1219 Remote Access Tools (0.02%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.90%); T1589 Gather Victim Identity Information (0.03%); T1190 Exploit Public-Facing Application (0.02%) | 99.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.62%); T1059 Command and Scripting Interpreter (0.12%); T1486 Data Encrypted for Impact (0.03%) | 99.62% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1083 File and Directory Discovery (0.01%); T1041 Exfiltration Over C2 Channel (0.00%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.89%); T1018 Remote System Discovery (0.01%); T1124 System Time Discovery (0.01%) | 99.89% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.16%); T1201 Password Policy Discovery (0.14%); T1039 Data from Network Shared Drive (0.13%) | 99.16% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1070 Indicator Removal (51.43%); T1222 File and Directory Permissions Modification (26.82%); T1033 System Owner/User Discovery (3.58%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (59.28%); T1222 File and Directory Permissions Modification (23.82%); T1078 Valid Accounts (3.62%) | 0.04% | False |

## repeat_50 / GRU / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.88%); T1007 System Service Discovery (0.01%); T1201 Password Policy Discovery (0.01%) | 99.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.75%); T1548 Abuse Elevation Control Mechanism (0.07%); T1105 Ingress Tool Transfer (0.04%) | 99.75% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1033 System Owner/User Discovery (0.03%); T1059 Command and Scripting Interpreter (0.01%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.35%); T1190 Exploit Public-Facing Application (0.46%); T1589 Gather Victim Identity Information (0.07%) | 99.35% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.21%); T1059 Command and Scripting Interpreter (0.27%); T1547 Boot or Logon Autostart Execution (0.08%) | 99.21% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (98.84%); T1087 Account Discovery (1.08%); T1547 Boot or Logon Autostart Execution (0.01%) | 1.08% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1124 System Time Discovery (0.03%); T1485 Data Destruction (0.01%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.89%); T1120 Peripheral Device Discovery (0.28%); T1021 Remote Services (0.09%) | 98.89% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (43.70%); T1003 OS Credential Dumping (20.22%); T1546 Event Triggered Execution (6.14%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1078 Valid Accounts (57.91%); T1003 OS Credential Dumping (10.37%); T1546 Event Triggered Execution (9.06%) | 0.00% | False |

## repeat_50 / GRU / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.88%); T1595 Active Scanning (0.01%); T1205 Traffic Signaling (0.01%) | 99.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.86%); T1548 Abuse Elevation Control Mechanism (0.04%); T1082 System Information Discovery (0.02%) | 99.86% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1057 Process Discovery (0.02%); T1083 File and Directory Discovery (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.88%); T1190 Exploit Public-Facing Application (0.04%); T1589 Gather Victim Identity Information (0.03%) | 99.88% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.71%); T1059 Command and Scripting Interpreter (0.06%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.88%); T1059 Command and Scripting Interpreter (0.06%); T1083 File and Directory Discovery (0.01%) | 99.88% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1564 Hide Artifacts (0.02%); T1124 System Time Discovery (0.02%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.38%); T1039 Data from Network Shared Drive (0.08%); T1201 Password Policy Discovery (0.06%) | 99.38% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (43.62%); T1003 OS Credential Dumping (29.42%); T1007 System Service Discovery (4.40%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (52.75%); T1078 Valid Accounts (17.00%); T1003 OS Credential Dumping (8.67%) | 0.00% | False |

## repeat_50 / GRU / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1083 File and Directory Discovery (0.02%); T1531 Account Access Removal (0.01%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.82%); T1548 Abuse Elevation Control Mechanism (0.07%); T1105 Ingress Tool Transfer (0.01%) | 99.82% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1219 Remote Access Tools (0.02%); T1057 Process Discovery (0.01%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.83%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.04%) | 99.83% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.59%); T1547 Boot or Logon Autostart Execution (0.08%); T1105 Ingress Tool Transfer (0.05%) | 99.59% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.95%); T1120 Peripheral Device Discovery (0.00%); T1486 Data Encrypted for Impact (0.00%) | 99.95% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1072 Software Deployment Tools (0.04%); T1059 Command and Scripting Interpreter (0.02%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.32%); T1039 Data from Network Shared Drive (0.23%); T1573 Encrypted Channel (0.12%) | 99.32% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1083 File and Directory Discovery (26.79%); T1222 File and Directory Permissions Modification (7.22%); T1010 Application Window Discovery (6.58%) | 0.23% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1083 File and Directory Discovery (19.73%); T1518 Software Discovery (9.46%); T1098 Account Manipulation (6.94%) | 0.01% | False |

## repeat_50 / GRU / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1595 Active Scanning (0.02%); T1589 Gather Victim Identity Information (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.88%); T1548 Abuse Elevation Control Mechanism (0.06%); T1218 System Binary Proxy Execution (0.01%) | 99.88% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1046 Network Service Scanning (0.01%); T1528 Steal Application Access Token (0.01%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.90%); T1190 Exploit Public-Facing Application (0.02%); T1589 Gather Victim Identity Information (0.02%) | 99.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.72%); T1222 File and Directory Permissions Modification (0.03%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.72% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.94%); T1059 Command and Scripting Interpreter (0.01%); T1083 File and Directory Discovery (0.01%) | 99.94% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.87%); T1124 System Time Discovery (0.01%); T1040 Network Sniffing (0.01%) | 99.87% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.74%); T1039 Data from Network Shared Drive (0.40%); T1120 Peripheral Device Discovery (0.24%) | 98.74% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (81.42%); T1105 Ingress Tool Transfer (10.69%); T1053 Scheduled Task/Job (2.98%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (83.60%); T1059 Command and Scripting Interpreter (6.56%); T1595 Active Scanning (2.07%) | 0.00% | False |

## repeat_50 / GRU / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.86%); T1059 Command and Scripting Interpreter (0.02%); T1007 System Service Discovery (0.01%) | 99.86% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.89%); T1218 System Binary Proxy Execution (0.02%); T1548 Abuse Elevation Control Mechanism (0.02%) | 99.89% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1003 OS Credential Dumping (0.01%); T1053 Scheduled Task/Job (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.90%); T1589 Gather Victim Identity Information (0.03%); T1190 Exploit Public-Facing Application (0.03%) | 99.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.38%); T1059 Command and Scripting Interpreter (0.27%); T1547 Boot or Logon Autostart Execution (0.07%) | 99.38% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.86%); T1059 Command and Scripting Interpreter (0.07%); T1222 File and Directory Permissions Modification (0.01%) | 99.86% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1566 Phishing (0.05%); T1124 System Time Discovery (0.02%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.47%); T1003 OS Credential Dumping (0.43%); T1083 File and Directory Discovery (0.16%) | 98.47% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1564 Hide Artifacts (47.27%); T1497 Virtualization/Sandbox Evasion (17.32%); T1222 File and Directory Permissions Modification (6.46%) | 0.07% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (70.69%); T1222 File and Directory Permissions Modification (8.55%); T1078 Valid Accounts (3.64%) | 0.03% | False |

## repeat_50 / GRU / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.84%); T1595 Active Scanning (0.02%); T1497 Virtualization/Sandbox Evasion (0.01%) | 99.84% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.80%); T1105 Ingress Tool Transfer (0.04%); T1548 Abuse Elevation Control Mechanism (0.04%) | 99.80% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1201 Password Policy Discovery (0.01%); T1518 Software Discovery (0.01%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.87%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.02%) | 99.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.60%); T1059 Command and Scripting Interpreter (0.07%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.60% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.79%); T1059 Command and Scripting Interpreter (0.06%); T1083 File and Directory Discovery (0.02%) | 99.79% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.75%); T1110 Brute Force (0.06%); T1518 Software Discovery (0.02%) | 99.75% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.91%); T1039 Data from Network Shared Drive (0.44%); T1003 OS Credential Dumping (0.11%) | 98.91% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (26.65%); T1033 System Owner/User Discovery (13.43%); T1546 Event Triggered Execution (8.44%) | 0.08% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (39.77%); T1078 Valid Accounts (14.80%); T1105 Ingress Tool Transfer (9.56%) | 0.01% | False |

## repeat_50 / GRU / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.89%); T1018 Remote System Discovery (0.01%); T1071 Application Layer Protocol (0.01%) | 99.89% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.76%); T1548 Abuse Elevation Control Mechanism (0.05%); T1036 Masquerading (0.05%) | 99.76% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.84%); T1057 Process Discovery (0.03%); T1003 OS Credential Dumping (0.02%) | 99.84% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.79%); T1190 Exploit Public-Facing Application (0.11%); T1589 Gather Victim Identity Information (0.03%) | 99.79% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.71%); T1059 Command and Scripting Interpreter (0.04%); T1105 Ingress Tool Transfer (0.02%) | 99.71% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.87%); T1059 Command and Scripting Interpreter (0.04%); T1083 File and Directory Discovery (0.02%) | 99.87% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.76%); T1057 Process Discovery (0.02%); T1014 Rootkit (0.01%) | 99.76% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.27%); T1039 Data from Network Shared Drive (0.16%); T1049 System Network Connections Discovery (0.10%) | 99.27% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (17.49%); T1204 User Execution (16.82%); T1564 Hide Artifacts (12.53%) | 0.36% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (93.81%); T1591 Gather Victim Org Information (0.48%); T1057 Process Discovery (0.40%) | 0.00% | False |

## repeat_50 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.81%); T1595 Active Scanning (0.03%); T1074 Data Staged (0.02%) | 99.81% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.60%); T1036 Masquerading (0.12%); T1548 Abuse Elevation Control Mechanism (0.10%) | 99.60% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1543 Create or Modify System Process (0.02%); T1518 Software Discovery (0.02%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.81%); T1190 Exploit Public-Facing Application (0.07%); T1589 Gather Victim Identity Information (0.04%) | 99.81% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.60%); T1059 Command and Scripting Interpreter (0.11%); T1219 Remote Access Tools (0.09%) | 99.60% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.85%); T1059 Command and Scripting Interpreter (0.05%); T1083 File and Directory Discovery (0.02%) | 99.85% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.87%); T1124 System Time Discovery (0.02%); T1210 Exploitation of Remote Services (0.01%) | 99.87% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.17%); T1039 Data from Network Shared Drive (0.42%); T1053 Scheduled Task/Job (0.26%) | 98.17% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (90.39%); T1105 Ingress Tool Transfer (1.93%); T1222 File and Directory Permissions Modification (0.86%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (78.96%); T1614 System Location Discovery (11.23%); T1564 Hide Artifacts (0.92%) | 0.01% | False |

## repeat_50 / LSTM / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.79%); T1595 Active Scanning (0.03%); T1566 Phishing (0.02%) | 99.79% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.66%); T1548 Abuse Elevation Control Mechanism (0.11%); T1036 Masquerading (0.08%) | 99.66% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1083 File and Directory Discovery (0.01%); T1614 System Location Discovery (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.76%); T1190 Exploit Public-Facing Application (0.10%); T1589 Gather Victim Identity Information (0.05%) | 99.76% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.50%); T1190 Exploit Public-Facing Application (0.11%); T1595 Active Scanning (0.05%) | 99.50% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.86%); T1070 Indicator Removal (0.03%); T1556 Modify Authentication Process (0.01%) | 99.86% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.83%); T1124 System Time Discovery (0.02%); T1573 Encrypted Channel (0.01%) | 99.83% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.33%); T1039 Data from Network Shared Drive (0.19%); T1120 Peripheral Device Discovery (0.05%) | 99.33% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (39.24%); T1082 System Information Discovery (10.73%); T1068 Exploitation for Privilege Escalation (8.63%) | 0.10% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (63.35%); T1033 System Owner/User Discovery (10.24%); T1548 Abuse Elevation Control Mechanism (6.77%) | 0.01% | False |

## repeat_50 / LSTM / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.82%); T1219 Remote Access Tools (0.02%); T1049 System Network Connections Discovery (0.01%) | 99.82% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.74%); T1548 Abuse Elevation Control Mechanism (0.05%); T1615 Group Policy Discovery (0.03%) | 99.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1485 Data Destruction (0.01%); T1057 Process Discovery (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.87%); T1589 Gather Victim Identity Information (0.03%); T1190 Exploit Public-Facing Application (0.03%) | 99.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.70%); T1201 Password Policy Discovery (0.03%); T1078 Valid Accounts (0.03%) | 99.70% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (98.37%); T1059 Command and Scripting Interpreter (1.32%); T1124 System Time Discovery (0.05%) | 98.37% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1110 Brute Force (0.02%); T1219 Remote Access Tools (0.02%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.13%); T1039 Data from Network Shared Drive (0.14%); T1614 System Location Discovery (0.12%) | 99.13% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1053 Scheduled Task/Job (34.21%); T1518 Software Discovery (15.26%); T1222 File and Directory Permissions Modification (10.11%) | 0.06% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1053 Scheduled Task/Job (56.85%); T1222 File and Directory Permissions Modification (15.48%); T1518 Software Discovery (7.56%) | 0.03% | False |

## repeat_50 / LSTM / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1110 Brute Force (0.04%); T1105 Ingress Tool Transfer (0.02%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.38%); T1548 Abuse Elevation Control Mechanism (0.30%); T1105 Ingress Tool Transfer (0.05%) | 99.38% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.82%); T1057 Process Discovery (0.02%); T1543 Create or Modify System Process (0.02%) | 99.82% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.71%); T1589 Gather Victim Identity Information (0.06%); T1190 Exploit Public-Facing Application (0.05%) | 99.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.03%); T1059 Command and Scripting Interpreter (0.44%); T1105 Ingress Tool Transfer (0.10%) | 99.03% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (78.01%); T1059 Command and Scripting Interpreter (21.74%); T1018 Remote System Discovery (0.02%) | 78.01% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.78%); T1040 Network Sniffing (0.03%); T1518 Software Discovery (0.02%) | 99.78% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.87%); T1039 Data from Network Shared Drive (0.21%); T1041 Exfiltration Over C2 Channel (0.12%) | 98.87% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (59.53%); T1053 Scheduled Task/Job (12.40%); T1039 Data from Network Shared Drive (6.18%) | 0.12% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (34.76%); T1059 Command and Scripting Interpreter (20.80%); T1105 Ingress Tool Transfer (15.81%) | 0.22% | False |

## repeat_50 / LSTM / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.82%); T1595 Active Scanning (0.02%); T1136 Create Account (0.02%) | 99.82% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.58%); T1548 Abuse Elevation Control Mechanism (0.20%); T1036 Masquerading (0.05%) | 99.58% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.87%); T1057 Process Discovery (0.02%); T1068 Exploitation for Privilege Escalation (0.01%) | 99.87% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.86%); T1589 Gather Victim Identity Information (0.03%); T1190 Exploit Public-Facing Application (0.03%) | 99.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (98.95%); T1059 Command and Scripting Interpreter (0.59%); T1105 Ingress Tool Transfer (0.11%) | 98.95% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.92%); T1083 File and Directory Discovery (0.01%); T1059 Command and Scripting Interpreter (0.01%) | 99.92% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.75%); T1124 System Time Discovery (0.02%); T1016 System Network Configuration Discovery (0.02%) | 99.75% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.78%); T1039 Data from Network Shared Drive (0.43%); T1070 Indicator Removal (0.12%) | 98.78% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1105 Ingress Tool Transfer (73.60%); T1059 Command and Scripting Interpreter (10.23%); T1120 Peripheral Device Discovery (3.50%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (55.62%); T1546 Event Triggered Execution (22.63%); T1547 Boot or Logon Autostart Execution (3.54%) | 0.19% | False |

## repeat_50 / LSTM / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.81%); T1083 File and Directory Discovery (0.02%); T1569 System Services (0.02%) | 99.81% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.64%); T1548 Abuse Elevation Control Mechanism (0.08%); T1485 Data Destruction (0.04%) | 99.64% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1201 Password Policy Discovery (0.02%); T1485 Data Destruction (0.01%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.71%); T1589 Gather Victim Identity Information (0.14%); T1190 Exploit Public-Facing Application (0.05%) | 99.71% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.54%); T1059 Command and Scripting Interpreter (0.05%); T1021 Remote Services (0.04%) | 99.54% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.90%); T1059 Command and Scripting Interpreter (0.01%); T1614 System Location Discovery (0.01%) | 99.90% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.80%); T1573 Encrypted Channel (0.03%); T1136 Create Account (0.02%) | 99.80% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.73%); T1039 Data from Network Shared Drive (0.30%); T1573 Encrypted Channel (0.22%) | 98.73% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (19.82%); T1082 System Information Discovery (16.22%); T1610 Deploy Container (6.19%) | 0.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (16.57%); T1083 File and Directory Discovery (14.13%); T1059 Command and Scripting Interpreter (12.26%) | 0.74% | False |

## repeat_50 / LSTM / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.85%); T1222 File and Directory Permissions Modification (0.02%); T1213 Data from Information Repositories (0.01%) | 99.85% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.63%); T1070 Indicator Removal (0.13%); T1087 Account Discovery (0.05%) | 99.63% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1222 File and Directory Permissions Modification (0.01%); T1528 Steal Application Access Token (0.01%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.84%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.04%) | 99.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.63%); T1059 Command and Scripting Interpreter (0.06%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.63% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.91%); T1033 System Owner/User Discovery (0.01%); T1014 Rootkit (0.01%) | 99.91% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.87%); T1564 Hide Artifacts (0.03%); T1124 System Time Discovery (0.01%) | 99.87% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.46%); T1039 Data from Network Shared Drive (0.16%); T1564 Hide Artifacts (0.07%) | 99.46% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (71.31%); T1105 Ingress Tool Transfer (8.64%); T1566 Phishing (3.32%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1082 System Information Discovery (43.86%); T1083 File and Directory Discovery (22.67%); T1120 Peripheral Device Discovery (6.90%) | 0.00% | False |

## repeat_50 / LSTM / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1557 Adversary-in-the-Middle (0.02%); T1592 Gather Victim Host Information (0.02%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.75%); T1218 System Binary Proxy Execution (0.08%); T1548 Abuse Elevation Control Mechanism (0.05%) | 99.75% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.88%); T1190 Exploit Public-Facing Application (0.01%); T1531 Account Access Removal (0.01%) | 99.88% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.86%); T1589 Gather Victim Identity Information (0.05%); T1190 Exploit Public-Facing Application (0.03%) | 99.86% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.64%); T1547 Boot or Logon Autostart Execution (0.05%); T1068 Exploitation for Privilege Escalation (0.04%) | 99.64% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.36%); T1059 Command and Scripting Interpreter (0.52%); T1033 System Owner/User Discovery (0.02%) | 99.36% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.88%); T1566 Phishing (0.01%); T1124 System Time Discovery (0.01%) | 99.88% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.01%); T1003 OS Credential Dumping (0.31%); T1039 Data from Network Shared Drive (0.18%) | 99.01% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1082 System Information Discovery (79.46%); T1071 Application Layer Protocol (5.02%); T1105 Ingress Tool Transfer (3.96%) | 0.01% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1105 Ingress Tool Transfer (31.95%); T1003 OS Credential Dumping (30.34%); T1082 System Information Discovery (13.58%) | 0.00% | False |

## repeat_50 / LSTM / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.82%); T1087 Account Discovery (0.02%); T1021 Remote Services (0.01%) | 99.82% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1548 Abuse Elevation Control Mechanism (0.03%); T1574 Hijack Execution Flow (0.02%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1136 Create Account (0.01%); T1201 Password Policy Discovery (0.01%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.80%); T1589 Gather Victim Identity Information (0.08%); T1190 Exploit Public-Facing Application (0.03%) | 99.80% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.19%); T1059 Command and Scripting Interpreter (0.24%); T1547 Boot or Logon Autostart Execution (0.06%) | 99.19% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.93%); T1591 Gather Victim Org Information (0.01%); T1525 Implant Internal Image (0.00%) | 99.93% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.84%); T1518 Software Discovery (0.03%); T1124 System Time Discovery (0.01%) | 99.84% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.19%); T1039 Data from Network Shared Drive (0.30%); T1574 Hijack Execution Flow (0.09%) | 99.19% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1574 Hijack Execution Flow (47.89%); T1041 Exfiltration Over C2 Channel (15.88%); T1033 System Owner/User Discovery (14.01%) | 0.03% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1033 System Owner/User Discovery (78.61%); T1574 Hijack Execution Flow (15.35%); T1041 Exfiltration Over C2 Channel (2.29%) | 0.01% | False |

## repeat_50 / LSTM / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.83%); T1005 Data from Local System (0.02%); T1589 Gather Victim Identity Information (0.01%) | 99.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.71%); T1548 Abuse Elevation Control Mechanism (0.05%); T1036 Masquerading (0.03%) | 99.71% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.83%); T1057 Process Discovery (0.03%); T1018 Remote System Discovery (0.02%) | 99.83% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (99.77%); T1190 Exploit Public-Facing Application (0.07%); T1589 Gather Victim Identity Information (0.05%) | 99.77% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.61%); T1059 Command and Scripting Interpreter (0.15%); T1105 Ingress Tool Transfer (0.03%) | 99.61% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (99.89%); T1036 Masquerading (0.02%); T1033 System Owner/User Discovery (0.02%) | 99.89% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.85%); T1485 Data Destruction (0.02%); T1124 System Time Discovery (0.01%) | 99.85% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.21%); T1039 Data from Network Shared Drive (0.11%); T1133 External Remote Services (0.10%) | 99.21% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1485 Data Destruction (20.97%); T1136 Create Account (13.23%); T1010 Application Window Discovery (9.54%) | 0.36% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1525 Implant Internal Image (30.27%); T1133 External Remote Services (10.42%); T1592 Gather Victim Host Information (6.25%) | 0.01% | False |

## repeat_50 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1592 Gather Victim Host Information (0.01%); T1595 Active Scanning (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.45%); T1548 Abuse Elevation Control Mechanism (0.42%); T1059 Command and Scripting Interpreter (0.02%) | 99.45% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1543 Create or Modify System Process (0.02%); T1083 File and Directory Discovery (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.40%); T1190 Exploit Public-Facing Application (18.38%); T1589 Gather Victim Identity Information (0.05%) | 81.40% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.73%); T1490 Inhibit System Recovery (0.02%); T1124 System Time Discovery (0.02%) | 99.73% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (63.51%); T1087 Account Discovery (36.30%); T1095 Non-Application Layer Protocol (0.03%) | 36.30% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.81%); T1016 System Network Configuration Discovery (0.03%); T1003 OS Credential Dumping (0.02%) | 99.81% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.42%); T1041 Exfiltration Over C2 Channel (0.08%); T1039 Data from Network Shared Drive (0.07%) | 99.42% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (63.28%); T1105 Ingress Tool Transfer (33.36%); T1219 Remote Access Tools (0.77%) | 0.00% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (59.23%); T1564 Hide Artifacts (24.37%); T1574 Hijack Execution Flow (10.23%) | 0.05% | False |

## repeat_50 / Transformer / seed 1

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.83%); T1595 Active Scanning (0.02%); T1573 Encrypted Channel (0.02%) | 99.83% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (97.74%); T1548 Abuse Elevation Control Mechanism (1.64%); T1036 Masquerading (0.18%) | 97.74% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1021 Remote Services (0.02%); T1083 File and Directory Discovery (0.01%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (82.87%); T1190 Exploit Public-Facing Application (16.84%); T1589 Gather Victim Identity Information (0.06%) | 82.87% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.66%); T1059 Command and Scripting Interpreter (0.06%); T1078 Valid Accounts (0.03%) | 99.66% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (67.86%); T1087 Account Discovery (31.85%); T1053 Scheduled Task/Job (0.08%) | 31.85% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.91%); T1071 Application Layer Protocol (0.01%); T1490 Inhibit System Recovery (0.01%) | 99.91% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (97.59%); T1021 Remote Services (0.90%); T1049 System Network Connections Discovery (0.60%) | 97.59% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1078 Valid Accounts (25.83%); T1021 Remote Services (16.63%); T1057 Process Discovery (13.03%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (23.36%); T1057 Process Discovery (19.96%); T1222 File and Directory Permissions Modification (13.63%) | 0.09% | False |

## repeat_50 / Transformer / seed 2

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.87%); T1071 Application Layer Protocol (0.04%); T1033 System Owner/User Discovery (0.01%) | 99.87% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.57%); T1548 Abuse Elevation Control Mechanism (0.23%); T1059 Command and Scripting Interpreter (0.09%) | 99.57% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.87%); T1083 File and Directory Discovery (0.03%); T1124 System Time Discovery (0.01%) | 99.87% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (54.50%); T1595 Active Scanning (45.17%); T1059 Command and Scripting Interpreter (0.06%) | 45.17% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.73%); T1068 Exploitation for Privilege Escalation (0.03%); T1059 Command and Scripting Interpreter (0.02%) | 99.73% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (84.62%); T1087 Account Discovery (15.24%); T1082 System Information Discovery (0.03%) | 15.24% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.21%); T1486 Data Encrypted for Impact (0.22%); T1485 Data Destruction (0.07%) | 99.21% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.64%); T1021 Remote Services (0.18%); T1573 Encrypted Channel (0.17%) | 98.64% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1222 File and Directory Permissions Modification (46.78%); T1070 Indicator Removal (28.37%); T1053 Scheduled Task/Job (12.45%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (89.44%); T1564 Hide Artifacts (5.88%); T1574 Hijack Execution Flow (1.96%) | 0.07% | False |

## repeat_50 / Transformer / seed 3

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.88%); T1595 Active Scanning (0.01%); T1098 Account Manipulation (0.01%) | 99.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.21%); T1548 Abuse Elevation Control Mechanism (0.53%); T1136 Create Account (0.07%) | 99.21% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.79%); T1083 File and Directory Discovery (0.05%); T1003 OS Credential Dumping (0.03%) | 99.79% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (62.56%); T1190 Exploit Public-Facing Application (37.00%); T1589 Gather Victim Identity Information (0.10%) | 62.56% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.49%); T1218 System Binary Proxy Execution (0.08%); T1059 Command and Scripting Interpreter (0.06%) | 99.49% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (56.43%); T1059 Command and Scripting Interpreter (43.12%); T1033 System Owner/User Discovery (0.06%) | 56.43% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.69%); T1124 System Time Discovery (0.07%); T1525 Implant Internal Image (0.03%) | 99.69% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.59%); T1041 Exfiltration Over C2 Channel (0.38%); T1049 System Network Connections Discovery (0.17%) | 98.59% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1218 System Binary Proxy Execution (35.08%); T1595 Active Scanning (12.62%); T1589 Gather Victim Identity Information (10.15%) | 0.14% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (52.36%); T1564 Hide Artifacts (8.79%); T1016 System Network Configuration Discovery (6.90%) | 0.14% | False |

## repeat_50 / Transformer / seed 4

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.90%); T1592 Gather Victim Host Information (0.03%); T1218 System Binary Proxy Execution (0.01%) | 99.90% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.40%); T1548 Abuse Elevation Control Mechanism (0.38%); T1105 Ingress Tool Transfer (0.07%) | 99.40% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.93%); T1068 Exploitation for Privilege Escalation (0.02%); T1219 Remote Access Tools (0.01%) | 99.93% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (81.16%); T1190 Exploit Public-Facing Application (18.58%); T1589 Gather Victim Identity Information (0.05%) | 81.16% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.78%); T1218 System Binary Proxy Execution (0.04%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.78% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (65.92%); T1087 Account Discovery (33.90%); T1053 Scheduled Task/Job (0.02%) | 33.90% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.43%); T1016 System Network Configuration Discovery (0.19%); T1083 File and Directory Discovery (0.04%) | 99.43% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.17%); T1041 Exfiltration Over C2 Channel (0.24%); T1573 Encrypted Channel (0.21%) | 98.17% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1543 Create or Modify System Process (17.89%); T1105 Ingress Tool Transfer (12.21%); T1115 Clipboard Data (5.30%) | 0.11% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (25.64%); T1070 Indicator Removal (24.40%); T1564 Hide Artifacts (20.47%) | 0.07% | False |

## repeat_50 / Transformer / seed 5

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.86%); T1592 Gather Victim Host Information (0.04%); T1021 Remote Services (0.01%) | 99.86% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.68%); T1548 Abuse Elevation Control Mechanism (0.15%); T1105 Ingress Tool Transfer (0.07%) | 99.68% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.89%); T1614 System Location Discovery (0.01%); T1525 Implant Internal Image (0.01%) | 99.89% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (68.17%); T1190 Exploit Public-Facing Application (31.48%); T1589 Gather Victim Identity Information (0.07%) | 68.17% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.41%); T1059 Command and Scripting Interpreter (0.34%); T1547 Boot or Logon Autostart Execution (0.03%) | 99.41% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (74.52%); T1087 Account Discovery (25.29%); T1095 Non-Application Layer Protocol (0.04%) | 25.29% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.76%); T1070 Indicator Removal (0.06%); T1614 System Location Discovery (0.03%) | 99.76% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.35%); T1021 Remote Services (0.11%); T1574 Hijack Execution Flow (0.08%) | 99.35% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1591 Gather Victim Org Information (43.00%); T1087 Account Discovery (11.14%); T1124 System Time Discovery (7.43%) | 0.42% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (49.09%); T1222 File and Directory Permissions Modification (11.48%); T1486 Data Encrypted for Impact (7.01%) | 0.14% | False |

## repeat_50 / Transformer / seed 6

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.94%); T1110 Brute Force (0.01%); T1589 Gather Victim Identity Information (0.01%) | 99.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.75%); T1548 Abuse Elevation Control Mechanism (0.09%); T1120 Peripheral Device Discovery (0.03%) | 99.75% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.91%); T1049 System Network Connections Discovery (0.02%); T1041 Exfiltration Over C2 Channel (0.01%) | 99.91% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (73.67%); T1190 Exploit Public-Facing Application (26.10%); T1589 Gather Victim Identity Information (0.06%) | 73.67% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.63%); T1105 Ingress Tool Transfer (0.08%); T1615 Group Policy Discovery (0.06%) | 99.63% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (67.97%); T1059 Command and Scripting Interpreter (31.75%); T1053 Scheduled Task/Job (0.03%) | 67.97% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.66%); T1557 Adversary-in-the-Middle (0.05%); T1201 Password Policy Discovery (0.05%) | 99.66% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.20%); T1041 Exfiltration Over C2 Channel (0.17%); T1201 Password Policy Discovery (0.10%) | 99.20% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (57.89%); T1071 Application Layer Protocol (10.63%); T1105 Ingress Tool Transfer (10.47%) | 0.02% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (37.65%); T1071 Application Layer Protocol (31.31%); T1222 File and Directory Permissions Modification (15.39%) | 0.33% | False |

## repeat_50 / Transformer / seed 7

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.91%); T1592 Gather Victim Host Information (0.03%); T1095 Non-Application Layer Protocol (0.01%) | 99.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.85%); T1548 Abuse Elevation Control Mechanism (0.09%); T1021 Remote Services (0.01%) | 99.85% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.86%); T1518 Software Discovery (0.02%); T1082 System Information Discovery (0.02%) | 99.86% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (78.13%); T1190 Exploit Public-Facing Application (21.64%); T1589 Gather Victim Identity Information (0.06%) | 78.13% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.75%); T1105 Ingress Tool Transfer (0.04%); T1218 System Binary Proxy Execution (0.02%) | 99.75% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (63.99%); T1059 Command and Scripting Interpreter (35.79%); T1033 System Owner/User Discovery (0.03%) | 63.99% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.86%); T1049 System Network Connections Discovery (0.02%); T1489 Service Stop (0.01%) | 99.86% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.62%); T1120 Peripheral Device Discovery (0.11%); T1614 System Location Discovery (0.03%) | 99.62% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1486 Data Encrypted for Impact (25.25%); T1485 Data Destruction (22.49%); T1219 Remote Access Tools (16.93%) | 0.09% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (71.66%); T1219 Remote Access Tools (10.46%); T1486 Data Encrypted for Impact (3.16%) | 0.23% | False |

## repeat_50 / Transformer / seed 8

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.76%); T1595 Active Scanning (0.06%); T1589 Gather Victim Identity Information (0.05%) | 99.76% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.66%); T1548 Abuse Elevation Control Mechanism (0.23%); T1105 Ingress Tool Transfer (0.02%) | 99.66% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.85%); T1033 System Owner/User Discovery (0.03%); T1007 System Service Discovery (0.02%) | 99.85% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1190 Exploit Public-Facing Application (54.97%); T1595 Active Scanning (44.60%); T1083 File and Directory Discovery (0.07%) | 44.60% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.56%); T1547 Boot or Logon Autostart Execution (0.14%); T1543 Create or Modify System Process (0.02%) | 99.56% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (68.24%); T1087 Account Discovery (31.51%); T1033 System Owner/User Discovery (0.04%) | 31.51% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.79%); T1518 Software Discovery (0.07%); T1082 System Information Discovery (0.01%) | 99.79% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (99.41%); T1569 System Services (0.07%); T1003 OS Credential Dumping (0.07%) | 99.41% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (76.56%); T1098 Account Manipulation (9.58%); T1556 Modify Authentication Process (3.09%) | 0.04% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1222 File and Directory Permissions Modification (45.13%); T1033 System Owner/User Discovery (14.96%); T1556 Modify Authentication Process (10.32%) | 0.32% | False |

## repeat_50 / Transformer / seed 9

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (99.80%); T1595 Active Scanning (0.04%); T1543 Create or Modify System Process (0.02%) | 99.80% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (99.72%); T1548 Abuse Elevation Control Mechanism (0.12%); T1070 Indicator Removal (0.06%) | 99.72% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (99.90%); T1007 System Service Discovery (0.01%); T1057 Process Discovery (0.01%) | 99.90% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (83.59%); T1190 Exploit Public-Facing Application (16.09%); T1592 Gather Victim Host Information (0.05%) | 83.59% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (99.72%); T1218 System Binary Proxy Execution (0.05%); T1059 Command and Scripting Interpreter (0.02%) | 99.72% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1087 Account Discovery (67.98%); T1059 Command and Scripting Interpreter (31.65%); T1082 System Information Discovery (0.07%) | 67.98% | True |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (99.66%); T1057 Process Discovery (0.07%); T1083 File and Directory Discovery (0.03%) | 99.66% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1213 Data from Information Repositories (98.53%); T1021 Remote Services (0.61%); T1201 Password Policy Discovery (0.15%) | 98.53% | True |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (59.94%); T1213 Data from Information Repositories (6.68%); T1046 Network Service Scanning (4.62%) | 0.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1564 Hide Artifacts (43.94%); T1018 Remote System Discovery (18.83%); T1222 File and Directory Permissions Modification (10.36%) | 0.02% | False |

