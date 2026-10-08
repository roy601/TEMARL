# Deterministic human-readable prediction examples

Same evenly spaced test-window indices for each model. No selection based on correctness. These are examples, not extra independent evaluations.

## markov_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (13.10%); T1595 Active Scanning (5.62%); T1213 Data from Information Repositories (2.99%) | 13.10% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (19.69%); T1548 Abuse Elevation Control Mechanism (5.89%); T1049 System Network Connections Discovery (2.98%) | 19.69% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (18.81%); T1201 Password Policy Discovery (6.02%); T1057 Process Discovery (5.64%) | 18.81% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (43.32%); T1592 Gather Victim Host Information (3.89%); T1190 Exploit Public-Facing Application (3.61%) | 43.32% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (45.76%); T1033 System Owner/User Discovery (3.86%); T1219 Remote Access Tools (2.56%) | 45.76% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (61.53%); T1087 Account Discovery (3.61%); T1105 Ingress Tool Transfer (2.36%) | 3.61% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (13.58%); T1120 Peripheral Device Discovery (7.55%); T1124 System Time Discovery (5.04%) | 13.58% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (8.96%); T1497 Virtualization/Sandbox Evasion (2.97%); T1105 Ingress Tool Transfer (2.71%) | 2.12% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (5.87%); T1049 System Network Connections Discovery (4.21%); T1003 OS Credential Dumping (4.05%) | 0.54% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (11.00%); T1003 OS Credential Dumping (4.83%); T1018 Remote System Discovery (3.60%) | 0.41% | False |

## markov_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (5.66%); T1595 Active Scanning (5.36%); T1033 System Owner/User Discovery (3.71%) | 5.66% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (16.00%); T1049 System Network Connections Discovery (3.29%); T1548 Abuse Elevation Control Mechanism (2.79%) | 16.00% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (13.43%); T1201 Password Policy Discovery (6.63%); T1057 Process Discovery (4.83%) | 13.43% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (27.09%); T1059 Command and Scripting Interpreter (4.58%); T1592 Gather Victim Host Information (4.55%) | 27.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (39.50%); T1219 Remote Access Tools (2.35%); T1120 Peripheral Device Discovery (2.30%) | 39.50% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (56.78%); T1087 Account Discovery (4.50%); T1486 Data Encrypted for Impact (1.64%) | 4.50% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (13.94%); T1595 Active Scanning (3.84%); T1124 System Time Discovery (3.36%) | 13.94% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (7.28%); T1059 Command and Scripting Interpreter (4.95%); T1105 Ingress Tool Transfer (4.21%) | 1.97% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (6.44%); T1033 System Owner/User Discovery (5.68%); T1219 Remote Access Tools (5.23%) | 0.38% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (6.73%); T1033 System Owner/User Discovery (4.07%); T1069 Permission Groups Discovery (3.28%) | 0.47% | False |

## markov_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (15.60%); T1595 Active Scanning (4.90%); T1082 System Information Discovery (2.79%) | 15.60% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (5.79%); T1059 Command and Scripting Interpreter (4.67%); T1548 Abuse Elevation Control Mechanism (3.62%) | 5.79% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1059 Command and Scripting Interpreter (10.87%); T1069 Permission Groups Discovery (5.59%); T1105 Ingress Tool Transfer (4.19%) | 5.59% | False |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (16.01%); T1059 Command and Scripting Interpreter (6.74%); T1592 Gather Victim Host Information (4.63%) | 16.01% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (25.83%); T1033 System Owner/User Discovery (5.23%); T1136 Create Account (2.28%) | 25.83% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (60.21%); T1087 Account Discovery (2.47%); T1105 Ingress Tool Transfer (1.45%) | 2.47% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1059 Command and Scripting Interpreter (11.11%); T1497 Virtualization/Sandbox Evasion (5.98%); T1120 Peripheral Device Discovery (4.11%) | 5.98% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1059 Command and Scripting Interpreter (7.48%); T1120 Peripheral Device Discovery (5.16%); T1219 Remote Access Tools (4.13%) | 1.22% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (13.97%); T1566 Phishing (6.87%); T1105 Ingress Tool Transfer (6.72%) | 0.21% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (4.26%); T1003 OS Credential Dumping (3.89%); T1105 Ingress Tool Transfer (3.61%) | 1.06% | False |

## real_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1595 Active Scanning (4.21%); T1548 Abuse Elevation Control Mechanism (3.71%); T1591 Gather Victim Org Information (3.57%) | 3.57% | False |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (17.70%); T1546 Event Triggered Execution (3.43%); T1548 Abuse Elevation Control Mechanism (2.79%) | 17.70% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (8.73%); T1490 Inhibit System Recovery (3.23%); T1201 Password Policy Discovery (2.93%) | 8.73% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (25.92%); T1059 Command and Scripting Interpreter (2.73%); T1190 Exploit Public-Facing Application (2.62%) | 25.92% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (12.91%); T1033 System Owner/User Discovery (10.15%); T1219 Remote Access Tools (2.95%) | 12.91% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (46.12%); T1087 Account Discovery (2.75%); T1566 Phishing (1.99%) | 2.75% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1055 Process Injection (6.09%); T1120 Peripheral Device Discovery (5.57%); T1497 Virtualization/Sandbox Evasion (5.37%) | 5.37% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (6.51%); T1068 Exploitation for Privilege Escalation (2.48%); T1055 Process Injection (2.39%) | 1.39% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (4.62%); T1003 OS Credential Dumping (4.51%); T1016 System Network Configuration Discovery (3.51%) | 0.70% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (6.28%); T1003 OS Credential Dumping (4.95%); T1018 Remote System Discovery (3.22%) | 0.47% | False |

## real_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1078 Valid Accounts (3.69%); T1033 System Owner/User Discovery (3.55%); T1595 Active Scanning (2.98%) | 2.74% | False |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (8.42%); T1553 Subvert Trust Controls (2.65%); T1204 User Execution (2.62%) | 8.42% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (5.25%); T1083 File and Directory Discovery (4.82%); T1201 Password Policy Discovery (3.88%) | 5.25% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (6.90%); T1059 Command and Scripting Interpreter (6.11%); T1486 Data Encrypted for Impact (2.84%) | 6.90% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1059 Command and Scripting Interpreter (6.39%); T1546 Event Triggered Execution (5.80%); T1087 Account Discovery (3.90%) | 5.80% | False |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (30.65%); T1087 Account Discovery (5.35%); T1566 Phishing (3.40%) | 5.35% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (5.50%); T1595 Active Scanning (2.99%); T1033 System Owner/User Discovery (2.72%) | 5.50% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (4.08%); T1059 Command and Scripting Interpreter (4.06%); T1486 Data Encrypted for Impact (3.13%) | 1.24% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (5.13%); T1219 Remote Access Tools (5.09%); T1033 System Owner/User Discovery (4.71%) | 0.66% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (4.65%); T1033 System Owner/User Discovery (3.71%); T1219 Remote Access Tools (3.27%) | 0.70% | False |

## real_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (6.91%); T1033 System Owner/User Discovery (3.45%); T1557 Adversary-in-the-Middle (3.17%) | 6.91% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (4.94%); T1059 Command and Scripting Interpreter (4.53%); T1213 Data from Information Repositories (2.99%) | 4.94% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1059 Command and Scripting Interpreter (8.73%); T1105 Ingress Tool Transfer (3.85%); T1120 Peripheral Device Discovery (3.64%) | 2.36% | False |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1059 Command and Scripting Interpreter (9.84%); T1595 Active Scanning (5.59%); T1120 Peripheral Device Discovery (3.28%) | 5.59% | False |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (4.76%); T1033 System Owner/User Discovery (3.61%); T1615 Group Policy Discovery (2.59%) | 4.76% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (39.43%); T1486 Data Encrypted for Impact (2.04%); T1087 Account Discovery (1.98%) | 1.98% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1059 Command and Scripting Interpreter (8.86%); T1566 Phishing (4.16%); T1120 Peripheral Device Discovery (4.13%) | 3.31% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1059 Command and Scripting Interpreter (6.73%); T1219 Remote Access Tools (3.84%); T1083 File and Directory Discovery (3.33%) | 1.14% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (11.10%); T1566 Phishing (8.45%); T1105 Ingress Tool Transfer (4.74%) | 0.28% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1003 OS Credential Dumping (3.83%); T1120 Peripheral Device Discovery (3.83%); T1007 System Service Discovery (3.43%) | 1.59% | False |

## repeat_100 / GRU / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (12.00%); T1595 Active Scanning (6.32%); T1213 Data from Information Repositories (3.21%) | 12.00% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (22.54%); T1548 Abuse Elevation Control Mechanism (4.03%); T1546 Event Triggered Execution (2.65%) | 22.54% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (19.95%); T1201 Password Policy Discovery (6.07%); T1057 Process Discovery (5.68%) | 19.95% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (38.73%); T1190 Exploit Public-Facing Application (5.85%); T1592 Gather Victim Host Information (2.26%) | 38.73% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (21.19%); T1033 System Owner/User Discovery (5.81%); T1219 Remote Access Tools (3.92%) | 21.19% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (57.32%); T1087 Account Discovery (5.57%); T1105 Ingress Tool Transfer (2.35%) | 5.57% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (16.40%); T1120 Peripheral Device Discovery (7.73%); T1124 System Time Discovery (6.53%) | 16.40% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (13.93%); T1591 Gather Victim Org Information (2.88%); T1497 Virtualization/Sandbox Evasion (2.72%) | 1.77% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1595 Active Scanning (6.39%); T1003 OS Credential Dumping (6.02%); T1018 Remote System Discovery (3.87%) | 0.54% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1595 Active Scanning (9.00%); T1003 OS Credential Dumping (6.15%); T1070 Indicator Removal (3.92%) | 0.37% | False |

## repeat_100 / LSTM / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1595 Active Scanning (5.82%); T1591 Gather Victim Org Information (5.29%); T1078 Valid Accounts (5.09%) | 5.29% | False |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (19.87%); T1548 Abuse Elevation Control Mechanism (2.92%); T1078 Valid Accounts (2.89%) | 19.87% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1069 Permission Groups Discovery (16.57%); T1201 Password Policy Discovery (6.78%); T1057 Process Discovery (5.27%) | 16.57% | True |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (22.47%); T1059 Command and Scripting Interpreter (5.69%); T1592 Gather Victim Host Information (3.52%) | 22.47% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (9.07%); T1059 Command and Scripting Interpreter (7.63%); T1219 Remote Access Tools (5.60%) | 9.07% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (55.85%); T1087 Account Discovery (5.56%); T1566 Phishing (1.78%) | 5.56% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1497 Virtualization/Sandbox Evasion (19.59%); T1124 System Time Discovery (4.14%); T1595 Active Scanning (3.38%) | 19.59% | True |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1021 Remote Services (9.43%); T1105 Ingress Tool Transfer (4.48%); T1053 Scheduled Task/Job (4.07%) | 2.11% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (6.38%); T1219 Remote Access Tools (6.09%); T1033 System Owner/User Discovery (5.40%) | 0.33% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1059 Command and Scripting Interpreter (5.53%); T1033 System Owner/User Discovery (4.55%); T1219 Remote Access Tools (3.53%) | 0.54% | False |

## repeat_100 / Transformer / seed 0

| Run / window | Recent history | Actual next | Top-3 predictions and probabilities | Actual probability | Correct Top-1 |
|---|---|---|---|---|---|
| scenario_1_b_c.j2 / 0 | T1590 | T1591 Gather Victim Org Information | T1591 Gather Victim Org Information (15.96%); T1595 Active Scanning (5.28%); T1033 System Owner/User Discovery (2.70%) | 15.96% | True |
| scenario_1_b_c.j2 / 30 | T1007 -> T1615 -> T1033 -> T1548 -> T1548 | T1033 System Owner/User Discovery | T1033 System Owner/User Discovery (10.33%); T1548 Abuse Elevation Control Mechanism (3.88%); T1049 System Network Connections Discovery (2.81%) | 10.33% | True |
| scenario_1_c_c.j2 / 60 | T1059 -> T1059 -> T1087 -> T1083 -> T1201 | T1069 Permission Groups Discovery | T1059 Command and Scripting Interpreter (8.56%); T1069 Permission Groups Discovery (7.47%); T1105 Ingress Tool Transfer (4.33%) | 7.47% | False |
| scenario_1_d_a.j2 / 90 | T1590 -> T1591 -> T1595 -> T1592 -> T1595 | T1595 Active Scanning | T1595 Active Scanning (15.09%); T1059 Command and Scripting Interpreter (7.81%); T1592 Gather Victim Host Information (4.13%) | 15.09% | True |
| scenario_1_d_a.j2 / 120 | T1033 -> T1546 -> T1546 -> T1546 -> T1546 | T1546 Event Triggered Execution | T1546 Event Triggered Execution (7.40%); T1033 System Owner/User Discovery (5.96%); T1136 Create Account (2.72%) | 7.40% | True |
| scenario_1_e_a.j2 / 150 | T1059 -> T1059 -> T1059 -> T1059 -> T1059 | T1087 Account Discovery | T1059 Command and Scripting Interpreter (60.36%); T1087 Account Discovery (2.59%); T1105 Ingress Tool Transfer (2.05%) | 2.59% | False |
| scenario_1_e_a.j2 / 180 | T1033 -> T1003 -> T1120 -> T1120 -> T1124 | T1497 Virtualization/Sandbox Evasion | T1059 Command and Scripting Interpreter (8.49%); T1497 Virtualization/Sandbox Evasion (8.08%); T1120 Peripheral Device Discovery (4.36%) | 8.08% | False |
| scenario_3_b_b.j2 / 210 | T1021 -> T1021 -> T1021 -> T1021 -> T1003 | T1213 Data from Information Repositories | T1059 Command and Scripting Interpreter (6.38%); T1120 Peripheral Device Discovery (5.34%); T1219 Remote Access Tools (4.45%) | 1.43% | False |
| scenario_6_c.j2 / 240 | T1176 -> T1056 -> T1056 -> T1115 -> T1176 | T1056 Input Capture | T1059 Command and Scripting Interpreter (15.14%); T1566 Phishing (7.98%); T1105 Ingress Tool Transfer (7.73%) | 0.16% | False |
| scenario_6_c.j2 / 271 | T1056 -> T1056 -> T1056 -> T1056 -> T1115 | T1115 Clipboard Data | T1219 Remote Access Tools (4.49%); T1003 OS Credential Dumping (4.44%); T1120 Peripheral Device Discovery (3.59%) | 1.06% | False |

