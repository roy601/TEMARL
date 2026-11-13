# Deterministic human-readable prediction examples

Same evenly spaced test-window indices for each model. No selection based on correctness. These are examples, not extra independent evaluations.

## markov_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (12.88%); T1595 Active Scanning (6.00%); T1213 Data from Information Repositories (3.05%) | 12.88% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (19.08%); T1548 Abuse Elevation Control Mechanism (6.08%); T1615 Group Policy Discovery (2.93%) | 19.08% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (16.96%); T1201 Password Policy Discovery (6.15%); T1057 Process Discovery (5.98%) | 16.96% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (43.31%); T1592 Gather Victim Host Information (4.09%); T1190 Exploit Public-Facing Application (3.73%) | 43.31% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (46.05%); T1033 System Owner/User Discovery (3.92%); T1219 Remote Access Tools (2.60%) | 46.05% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (61.99%); T1087 Account Discovery (3.55%); T1105 Ingress Tool Transfer (2.30%) | 3.55% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (13.08%); T1120 Peripheral Device Discovery (7.28%); T1124 System Time Discovery (5.52%) | 13.08% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (9.50%); T1497 Virtualization/Sandbox Evasion (2.96%); T1591 Gather Victim Org Information (2.84%) | 2.10% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (5.79%); T1049 System Network Connections Discovery (4.21%); T1018 Remote System Discovery (4.11%) | 0.54% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (10.84%); T1003 OS Credential Dumping (4.71%); T1018 Remote System Discovery (3.56%) | 0.43% | False |

## markov_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (5.55%); T1595 Active Scanning (5.53%); T1033 System Owner/User Discovery (3.74%) | 5.55% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (15.03%); T1049 System Network Connections Discovery (3.22%); T1059 Command and Scripting Interpreter (2.87%) | 15.03% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (13.26%); T1201 Password Policy Discovery (6.56%); T1057 Process Discovery (4.87%) | 13.26% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (27.40%); T1592 Gather Victim Host Information (4.42%); T1059 Command and Scripting Interpreter (4.27%) | 27.40% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (38.48%); T1219 Remote Access Tools (2.49%); T1120 Peripheral Device Discovery (2.44%) | 38.48% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (57.11%); T1087 Account Discovery (4.41%); T1486 Data Encrypted for Impact (1.58%) | 4.41% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (14.64%); T1595 Active Scanning (3.50%); T1124 System Time Discovery (3.26%) | 14.64% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (6.71%); T1105 Ingress Tool Transfer (4.51%); T1059 Command and Scripting Interpreter (4.24%) | 1.99% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (6.45%); T1033 System Owner/User Discovery (6.10%); T1219 Remote Access Tools (5.23%) | 0.41% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (6.05%); T1033 System Owner/User Discovery (4.77%); T1219 Remote Access Tools (3.50%) | 0.46% | False |

## markov_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (14.94%); T1595 Active Scanning (5.12%); T1033 System Owner/User Discovery (2.69%) | 14.94% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (6.55%); T1059 Command and Scripting Interpreter (4.15%); T1548 Abuse Elevation Control Mechanism (3.55%) | 6.55% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1059 Command and Scripting Interpreter (9.26%); T1069 Permission Groups Discovery (6.04%); T1105 Ingress Tool Transfer (4.42%) | 6.04% | False |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (19.93%); T1059 Command and Scripting Interpreter (6.19%); T1592 Gather Victim Host Information (4.55%) | 19.93% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (23.12%); T1033 System Owner/User Discovery (5.03%); T1136 Create Account (2.58%) | 23.12% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (57.71%); T1087 Account Discovery (2.52%); T1105 Ingress Tool Transfer (1.70%) | 2.52% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1059 Command and Scripting Interpreter (10.79%); T1497 Virtualization/Sandbox Evasion (6.22%); T1120 Peripheral Device Discovery (4.25%) | 6.22% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1059 Command and Scripting Interpreter (7.49%); T1120 Peripheral Device Discovery (4.90%); T1219 Remote Access Tools (4.33%) | 1.26% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (12.43%); T1566 Phishing (7.26%); T1105 Ingress Tool Transfer (6.80%) | 0.20% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (4.26%); T1105 Ingress Tool Transfer (4.02%); T1595 Active Scanning (3.92%) | 0.97% | False |

## real_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1595 Active Scanning (4.42%); T1548 Abuse Elevation Control Mechanism (3.86%); T1591 Gather Victim Org Information (3.62%) | 3.62% | False |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (17.04%); T1546 Event Triggered Execution (3.57%); T1219 Remote Access Tools (2.80%) | 17.04% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (9.32%); T1490 Inhibit System Recovery (3.19%); T1083 File and Directory Discovery (2.96%) | 9.32% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (25.84%); T1190 Exploit Public-Facing Application (2.77%); T1059 Command and Scripting Interpreter (2.60%) | 25.84% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (12.65%); T1033 System Owner/User Discovery (10.18%); T1219 Remote Access Tools (3.14%) | 12.65% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (45.41%); T1087 Account Discovery (2.88%); T1566 Phishing (2.08%) | 2.88% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1055 Process Injection (6.12%); T1120 Peripheral Device Discovery (5.80%); T1497 Virtualization/Sandbox Evasion (5.60%) | 5.60% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (7.23%); T1055 Process Injection (2.50%); T1590 Gather Victim Network Information (2.40%) | 1.36% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1003 OS Credential Dumping (4.41%); T1595 Active Scanning (4.30%); T1016 System Network Configuration Discovery (3.57%) | 0.72% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (6.03%); T1003 OS Credential Dumping (4.83%); T1018 Remote System Discovery (3.12%) | 0.48% | False |

## real_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1078 Valid Accounts (3.68%); T1033 System Owner/User Discovery (3.50%); T1595 Active Scanning (2.92%) | 2.72% | False |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (8.27%); T1059 Command and Scripting Interpreter (2.77%); T1553 Subvert Trust Controls (2.61%) | 8.27% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (5.08%); T1083 File and Directory Discovery (4.63%); T1201 Password Policy Discovery (3.79%) | 5.08% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (7.22%); T1059 Command and Scripting Interpreter (6.88%); T1486 Data Encrypted for Impact (2.92%) | 7.22% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1059 Command and Scripting Interpreter (7.17%); T1546 Event Triggered Execution (5.42%); T1219 Remote Access Tools (4.67%) | 5.42% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (30.48%); T1087 Account Discovery (5.22%); T1566 Phishing (3.33%) | 5.22% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (5.56%); T1595 Active Scanning (3.03%); T1033 System Owner/User Discovery (2.67%) | 5.56% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1059 Command and Scripting Interpreter (4.31%); T1021 Remote Services (4.09%); T1486 Data Encrypted for Impact (3.24%) | 1.23% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1033 System Owner/User Discovery (5.07%); T1219 Remote Access Tools (5.06%); T1059 Command and Scripting Interpreter (4.70%) | 0.68% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (4.16%); T1033 System Owner/User Discovery (3.99%); T1219 Remote Access Tools (3.26%) | 0.64% | False |

## real_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (6.51%); T1033 System Owner/User Discovery (3.41%); T1557 Adversary-in-the-Middle (3.20%) | 6.51% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1059 Command and Scripting Interpreter (4.82%); T1033 System Owner/User Discovery (4.61%); T1213 Data from Information Repositories (3.05%) | 4.61% | False |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1059 Command and Scripting Interpreter (8.91%); T1105 Ingress Tool Transfer (3.91%); T1120 Peripheral Device Discovery (3.66%) | 2.15% | False |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1059 Command and Scripting Interpreter (9.21%); T1595 Active Scanning (5.13%); T1105 Ingress Tool Transfer (2.96%) | 5.13% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (4.45%); T1033 System Owner/User Discovery (3.36%); T1590 Gather Victim Network Information (2.77%) | 4.45% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (39.21%); T1486 Data Encrypted for Impact (2.04%); T1105 Ingress Tool Transfer (1.99%) | 1.76% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1059 Command and Scripting Interpreter (9.62%); T1566 Phishing (4.27%); T1120 Peripheral Device Discovery (3.92%) | 3.25% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1059 Command and Scripting Interpreter (6.67%); T1083 File and Directory Discovery (3.30%); T1120 Peripheral Device Discovery (3.29%) | 1.22% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (11.52%); T1566 Phishing (7.86%); T1105 Ingress Tool Transfer (4.61%) | 0.29% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1120 Peripheral Device Discovery (3.84%); T1003 OS Credential Dumping (3.75%); T1007 System Service Discovery (3.61%) | 1.59% | False |

## repeat_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (11.32%); T1595 Active Scanning (6.58%); T1592 Gather Victim Host Information (3.32%) | 11.32% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (22.00%); T1548 Abuse Elevation Control Mechanism (4.36%); T1546 Event Triggered Execution (2.42%) | 22.00% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (18.94%); T1201 Password Policy Discovery (6.03%); T1057 Process Discovery (5.84%) | 18.94% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (40.58%); T1190 Exploit Public-Facing Application (5.66%); T1592 Gather Victim Host Information (2.34%) | 40.58% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (21.20%); T1033 System Owner/User Discovery (5.84%); T1219 Remote Access Tools (4.26%) | 21.20% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (57.13%); T1087 Account Discovery (5.67%); T1105 Ingress Tool Transfer (2.40%) | 5.67% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (16.48%); T1120 Peripheral Device Discovery (7.55%); T1124 System Time Discovery (6.74%) | 16.48% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (14.28%); T1591 Gather Victim Org Information (2.80%); T1497 Virtualization/Sandbox Evasion (2.68%) | 1.75% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (6.77%); T1003 OS Credential Dumping (5.78%); T1049 System Network Connections Discovery (3.72%) | 0.56% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (9.04%); T1003 OS Credential Dumping (5.95%); T1070 Indicator Removal (3.95%) | 0.37% | False |

## repeat_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1595 Active Scanning (5.96%); T1591 Gather Victim Org Information (5.11%); T1078 Valid Accounts (4.93%) | 5.11% | False |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (19.65%); T1548 Abuse Elevation Control Mechanism (3.07%); T1049 System Network Connections Discovery (2.84%) | 19.65% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (17.44%); T1201 Password Policy Discovery (6.32%); T1057 Process Discovery (5.40%) | 17.44% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (22.09%); T1059 Command and Scripting Interpreter (5.58%); T1592 Gather Victim Host Information (3.40%) | 22.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (9.05%); T1059 Command and Scripting Interpreter (7.32%); T1219 Remote Access Tools (5.14%) | 9.05% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (56.31%); T1087 Account Discovery (5.40%); T1566 Phishing (1.74%) | 5.40% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (19.70%); T1124 System Time Discovery (4.05%); T1595 Active Scanning (3.38%) | 19.70% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (9.19%); T1105 Ingress Tool Transfer (4.76%); T1053 Scheduled Task/Job (4.04%) | 2.02% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (6.28%); T1219 Remote Access Tools (5.99%); T1033 System Owner/User Discovery (5.65%) | 0.35% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (5.36%); T1033 System Owner/User Discovery (4.85%); T1219 Remote Access Tools (3.72%) | 0.53% | False |

## repeat_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (14.66%); T1595 Active Scanning (5.61%); T1033 System Owner/User Discovery (2.47%) | 14.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (10.62%); T1548 Abuse Elevation Control Mechanism (3.79%); T1049 System Network Connections Discovery (3.12%) | 10.62% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1059 Command and Scripting Interpreter (8.51%); T1069 Permission Groups Discovery (8.14%); T1105 Ingress Tool Transfer (4.27%) | 8.14% | False |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (14.37%); T1059 Command and Scripting Interpreter (8.20%); T1592 Gather Victim Host Information (3.87%) | 14.37% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (6.80%); T1033 System Owner/User Discovery (6.53%); T1136 Create Account (2.75%) | 6.80% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (60.18%); T1087 Account Discovery (2.70%); T1105 Ingress Tool Transfer (1.89%) | 2.70% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1059 Command and Scripting Interpreter (8.41%); T1497 Virtualization/Sandbox Evasion (8.13%); T1120 Peripheral Device Discovery (4.19%) | 8.13% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1219 Remote Access Tools (4.99%); T1059 Command and Scripting Interpreter (4.89%); T1120 Peripheral Device Discovery (4.75%) | 1.48% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (14.39%); T1566 Phishing (8.27%); T1105 Ingress Tool Transfer (7.69%) | 0.17% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (4.82%); T1105 Ingress Tool Transfer (3.94%); T1219 Remote Access Tools (3.82%) | 1.02% | False |

