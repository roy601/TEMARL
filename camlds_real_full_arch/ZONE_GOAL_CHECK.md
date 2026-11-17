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

Two things still to do before the protocol is frozen: (a) pin the ATT&CK release used for the tactic
membership (a STIX file with its hash), because the full-membership mask can also add goal commands in
other runs; the new counts are reported per run; (b) decide S4's target (LAN, where the attack ends,
recommended; DMZ by the old rule as a sensitivity run).
