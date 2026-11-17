# Check of decisions D1 (zones) and D3 (goals), 2026-11-17, before any run

Sources: the AttackBed repository at commit 4d43354 (`attackbed/`, the testbed CAM-LDS was recorded on):
`docs/development/firewall.md`, `docs/development/dns.md`, `ansible/hosts.example`,
`docs/scenarios/*.md`. Read-only checks of the corpus through `pipeline.py` (no training, no test data
scored).

## D1. Subnet -> zone: fully defined by the source

`firewall.md` names the firewall zones; they are exactly the environment's five zones:

| subnet | AttackBed zone | our zone | hosts (`hosts.example`) |
|---|---|---|---|
| 192.42.0.0/16 (fake internet, `dns.md`) | inet | Internet | attacker, corpdns, inetdns, firewall public IP |
| 172.17.100.0/24 | dmz | DMZ | videoserver, reposerver, docker, webcam |
| 192.168.100.0/24 | lan | LAN | linuxshare, lanturtle, wazuh, firewall LAN IP |
| 10.12.0.0/24 | admin | Admin | adminpc1, adminpc2 |
| 192.168.50.0/24 | user | User | client |

No mapping choice is left to us. (57.128.7.0/24 = mgmt, out of band, not part of any scenario.)

## D1. `derived_zones.json` is NOT a valid source of attacker zones

Its host path is the order in which hosts first show manifestations in the logs, not where the attacker
is:

- `corpdns` and `inetfw` appear in almost every run because every DNS query and every crossing of zones
  passes through them (`dns.md`, `firewall.md`). 24 of 34 runs therefore "start" at corpdns.
- The two scenario 2 runs give opposite paths (corpdns -> videoserver -> inetfw and
  videoserver -> inetfw -> corpdns) for the same attack.
- Scenario 5 "starts" at adminpc, which is the victim of the ARP spoofing; the attacker is the LAN
  Turtle, placed inside the LAN (`lanturtle.md`).

## D1. The hand-typed zones agree with AttackBed's own scenario descriptions

| scenario | AttackBed description | entry / target | hand-typed | agrees |
|---|---|---|---|---|
| S1 Videoserver | attacker (inet) exploits ZoneMinder on videoserver (dmz) | Internet / DMZ | Internet / DMZ | yes |
| S2 Linux malware | malware on videoserver (dmz), "same infrastructure as videoserver" | DMZ / DMZ | DMZ / DMZ | yes |
| S3 Lateral movement | brute force reposerver (dmz from inet), then lateral to linuxshare (lan), impact | Internet / LAN | Internet / LAN | yes |
| S4 Network | already on reposerver (dmz), takes the firewall, opens dmz -> lan, connects to linuxshare (lan) | DMZ / firewall, then LAN | DMZ / "Firewall" (mapped by rule to DMZ) | **open** (1 run) |
| S5 LAN Turtle | attacker machine inside the lan, steals an auth hash, uses it against the dmz server | LAN / DMZ | LAN / DMZ | yes |
| S6 Client | client (user) exploited, attacker persists on it | User / User | User / User | yes |
| S7 Docker | attacker (inet) exploits nextcloud container on docker host (dmz), escapes, dumps /etc/shadow | Internet / DMZ | Internet / DMZ | yes |

## D3. The 8 "unreachable" runs come from two goal errors, both fixable from sources

1. **S6 goal.** The hand-typed goal is Exfiltration, but `client.md` lists no exfiltration technique;
   its stated aim is "Attacker persists" (T1554, T1546, T1053; the plugin variant installs a browser
   extension, T1176, Persistence). With goal = Persistence, all 5 S6 runs contain goal commands
   (4, 4, 8, 6, 4).
2. **S1 pam variants.** `videoserver.md` step 10 lists "modifies pam (T1556.003)" as the backdoor (the
   Persistence goal of S1). Our vocabulary gives each technique one tactic and assigns T1556 to Credential
   Access only. MITRE ATT&CK lists T1556 under Credential Access, Defense Evasion and Persistence. With
   the goal mask built from ATT&CK's full tactic membership, the 3 pam runs without goal commands now have
   2 each.

With both fixes, **all 34 runs contain at least one goal command**; no run has to be dropped.

Resolved in code (2026-11-17, `d1_data.py`): instead of an external ATT&CK file, a goal command is a
command whose own released tactic labels (`tactics_raw`) contain the goal tactic. The dataset labels
T1556.003 as credential-access, defense-evasion and persistence, so the result above holds with the
dataset's own labels. S4's target is settled by the D2 check below.

## D2. Movement: the environment's random-walk model does NOT match the recorded runs

Check: `checks/movement_check.py` (read-only) -> `checks/MOVEMENT_CHECK.txt`. Each of the 904 commands is
linked to its AttackMate execution record (all 904 matched; records from the 34 md5-verified scenario
archives, not from the mismatched `manifestations_filtered.zip`). Its zone is the zone of the host it
executes on, by documented rules (DNAT ports and reverse shells from `firewall.md`, implant and handler
hosts from the scenario pages, ssh hops inside a session). The model is env_cmd's own `_move`
(p_goal 0.7, p_stay 0.8), no defence, 20 draws per run.

| | recorded | model |
|---|---|---|
| zone changes per run (mean) | **1.50** | **9.27** |
| stay in the target zone, next command | **0.967** | **0.781** |
| share of commands in the target zone | 0.737 | 0.767 |
| share of commands in undefended zones (Internet, firewall) | **0.159** | **0.000** |

Recorded paths are short and fixed by the scenario (e.g. S1: Internet x5 -> DMZ x23; S3: Internet -> DMZ ->
LAN; S6 macro: User only). The model adds about 8 random moves per run into zones the attack never
touches, and it cannot place the attacker on the attacker machine or the firewall at all. The similar
"share in target" is a coincidence of averages.

Consequences:
1. Primary environment: the attacker's zone is the **recorded zone of each command**. The defence can
   still change it only through lures (a lure engagement sends the next command to the partner zone;
   then the replay continues on its recorded path). Commands that execute in Internet or on the firewall
   cannot be engaged (no agent defends them); they are counted and reported. The old movement model is a
   sensitivity analysis.
2. Goal zones under recorded positions: 32 of 34 runs have goal commands in their hand-typed target zone.
   **S5**: the credential theft executes on the LAN Turtle, in LAN (hand-typed DMZ is where the stolen
   hash is used) -> target LAN. **S4**: its goal commands execute on the firewall, which no agent defends
   -> S4 cannot be protected in this environment; it is excluded from P1 and reported as such (P1 on 33
   runs). This replaces the S4 "LAN vs DMZ" question above.
3. This changes `env_cmd.py`; the change is written, tested and committed before the protocol is frozen.
