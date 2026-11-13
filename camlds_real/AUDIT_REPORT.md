```
CAM-LDS release audit
  data : C:\Users\user5\Downloads\DATASET 01
  repo : C:\Users\user5\TEMARL

==============================================================================
Q1  INVENTORY — what is actually on this machine
==============================================================================
  37 archives under C:\Users\user5\Downloads\DATASET 01

  file                                                  MB  
  attack-manifestations-interpretation-main.zip        9.4  
  manifestations_filtered.zip                        213.7  
  manifestations_raw.zip                             535.9  
  scenario_1_autostart_localaccount.zip              178.0  
  scenario_1_autostart_pam.zip                       177.4  
  scenario_1_autostart_sshkey.zip                    176.6  
  scenario_1_cron_localaccount.zip                   173.9  
  scenario_1_cron_pam.zip                            173.7  
  scenario_1_cron_sshkey.zip                         173.6  
  scenario_1_pwnkit_localaccount.zip                 174.0  
  scenario_1_pwnkit_pam.zip                          173.4  
  scenario_1_pwnkit_sshkey.zip                       175.7  
  scenario_1_racecondition_localaccount.zip          176.2  
  scenario_1_racecondition_pam.zip                   174.3  
  scenario_1_racecondition_sshkey.zip                174.7  
  scenario_1_sudo_localaccount.zip                   178.0  
  scenario_1_sudo_pam.zip                            175.3  
  scenario_1_sudo_sshkey.zip                         173.5  
  scenario_1_validaccount_localaccount.zip           173.0  
  scenario_1_validaccount_pam.zip                    172.9  
  scenario_1_validaccount_sshkey.zip                 173.1  
  scenario_2_cron.zip                                160.5  
  scenario_2_rootkit.zip                             161.0  
  scenario_3_ssh_apt.zip                             206.8  
  scenario_3_ssh_healthcheck.zip                     203.4  
  scenario_3_ssh_puppet.zip                          197.8  
  scenario_3_vnc_apt.zip                             206.6  
  scenario_3_vnc_healthcheck.zip                     202.7  
  scenario_3_vnc_puppet.zip                          198.8  
  scenario_4.zip                                     201.5  
  scenario_5.zip                                     202.8  
  scenario_6_macro_binary.zip                        202.3  
  scenario_6_macro_cron.zip                          198.6  
  scenario_6_plugin.zip                              199.7  
  scenario_6_screensharing_binary.zip                364.3  
  scenario_6_screensharing_cron.zip                  447.1  
  scenario_7.zip                                     160.1  

  TOTAL 7.42 GB  (37 distinct archives)

  Looks like the full LOGS release (~7.41 GB, 36 files).
  manifestations_filtered.zip      PRESENT
  manifestations_raw.zip           PRESENT

  Freeze one Zenodo version and record it. Published:
    logs_v1   10.5281/zenodo.18390561  2026-01-27  36 files  7.41 GB
    logs_v2   10.5281/zenodo.18861762  2026-03-04  36 files  7.41 GB
    pcaps     10.5281/zenodo.18701095  2026-02-19  34 files  182.07 GB
  v2 (18861762) adds `runc init` audit events for Scenario 7. Prefer v2.

==============================================================================
Q2  Does `attacker/logs/attackmate.json` exist in the scenario zips?
==============================================================================
  An external plan said to download all 7.41 GB for this file.
  Verifying against the archives themselves.

  scenario_1_autostart_localaccount.zip  (10508 entries)
      attackmate matches : 6
         scenario_1_autostart_localaccount/attacker/logs/attackmate.json
         scenario_1_autostart_localaccount/attacker/logs/attackmate.log
         scenario_1_autostart_localaccount/attacker/configs/etc/attackmate.yml.3575.2025-09-22@18:16:50~
         scenario_1_autostart_localaccount/attacker/configs/etc/attackmate/
      attacker/ entries  : 2730
         scenario_1_autostart_localaccount/attacker/
         scenario_1_autostart_localaccount/attacker/facts.json
         scenario_1_autostart_localaccount/attacker/logs/
         scenario_1_autostart_localaccount/attacker/logs/attackmate.json

  scenario_1_autostart_pam.zip  (10508 entries)
      attackmate matches : 6
         scenario_1_autostart_pam/attacker/logs/attackmate.json
         scenario_1_autostart_pam/attacker/logs/attackmate.log
         scenario_1_autostart_pam/attacker/configs/etc/attackmate/
         scenario_1_autostart_pam/attacker/configs/etc/attackmate/playbooks/
      attacker/ entries  : 2730
         scenario_1_autostart_pam/attacker/
         scenario_1_autostart_pam/attacker/facts.json
         scenario_1_autostart_pam/attacker/logs/
         scenario_1_autostart_pam/attacker/logs/attackmate.json

  scenario_1_autostart_sshkey.zip  (10507 entries)
      attackmate matches : 6
         scenario_1_autostart_sshkey/attacker/logs/attackmate.json
         scenario_1_autostart_sshkey/attacker/logs/attackmate.log
         scenario_1_autostart_sshkey/attacker/configs/etc/attackmate/
         scenario_1_autostart_sshkey/attacker/configs/etc/attackmate/playbooks/
      attacker/ entries  : 2731
         scenario_1_autostart_sshkey/attacker/
         scenario_1_autostart_sshkey/attacker/facts.json
         scenario_1_autostart_sshkey/attacker/logs/
         scenario_1_autostart_sshkey/attacker/logs/attackmate.json

  scenario_1_cron_localaccount.zip  (10505 entries)
      attackmate matches : 6
         scenario_1_cron_localaccount/attacker/logs/attackmate.json
         scenario_1_cron_localaccount/attacker/logs/attackmate.log
         scenario_1_cron_localaccount/attacker/configs/etc/attackmate/
         scenario_1_cron_localaccount/attacker/configs/etc/attackmate/playbooks/
      attacker/ entries  : 2730
         scenario_1_cron_localaccount/attacker/
         scenario_1_cron_localaccount/attacker/facts.json
         scenario_1_cron_localaccount/attacker/logs/
         scenario_1_cron_localaccount/attacker/logs/attackmate.json

  scenario_1_cron_pam.zip  (10504 entries)
      attackmate matches : 6
         scenario_1_cron_pam/attacker/logs/attackmate.json
         scenario_1_cron_pam/attacker/logs/attackmate.log
         scenario_1_cron_pam/attacker/configs/etc/attackmate.yml.3774.2025-09-24@08:48:14~
         scenario_1_cron_pam/attacker/configs/etc/attackmate/
      attacker/ entries  : 2730
         scenario_1_cron_pam/attacker/
         scenario_1_cron_pam/attacker/facts.json
         scenario_1_cron_pam/attacker/logs/
         scenario_1_cron_pam/attacker/logs/attackmate.json

  VERDICT:
    attackmate logs EXIST. The execution-record route is available, and
    is better than attack_times.csv alone because it records what actually
    ran (including failures/retries) rather than what was specified.

==============================================================================
Q3  `manifestations_filtered.zip` layout  +  Q4  ZONE DERIVATION
==============================================================================
  note: no attackbed clone at C:\Users\user5\TEMARL\attackbed\ansible\hosts.example
        using the transcribed inventory instead (commit 4d43354).
        `git clone https://github.com/ait-testbed/attackbed` to use the source.
  AttackBed inventory [transcribed fallback table]: 15 hosts in 8 subnets

    10.12.0.0/24       adminpc1, adminpc2
    172.17.100.0/24    docker, reposerver, videoserver, webcam
    192.168.100.0/24   inetfw, lanturtle, linuxshare, wazuh
    192.168.50.0/24    client
    192.42.0.0/24      corpdns
    192.42.1.0/24      attacker
    192.42.2.0/24      inetdns
    57.128.7.0/24      mgmt

  >> 8 subnets, but our topology is a 5-ZONE star. The mapping
     is not one-to-one, so a grouping rule must be DECLARED and written
     down before the zones below mean anything.

  42596 entries in manifestations_filtered.zip
  groupings present: {'techniques': 21741, 'steps': 11946, 'sequences': 8908}
  (the analysis repo recommends `steps`; sequences/techniques duplicate logs)

  using grouping: steps
    sequences      401 (scenario, step) pairs
    steps          883 (scenario, step) pairs
    techniques      97 (scenario, step) pairs

  matched 883 (scenario, step) pairs across 34 scenario-variants
  published expectation: 34 runs, 904 steps

  DECLARED: hosts excluded from zone derivation = attacker, mgmt, wazuh
            (attacker = origin, wazuh = SIEM, mgmt = out-of-band admin)

  scenario-variant               steps  entry            target           victim-host path
  1_autostart_localaccount          28  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_autostart_pam                   28  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_autostart_sshkey                28  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_cron_localaccount               30  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_cron_pam                        30  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_cron_sshkey                     30  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_pwnkit_localaccount             26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_pwnkit_pam                      26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_pwnkit_sshkey                   26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_racecondition_localaccount      34  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_racecondition_pam               34  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_racecondition_sshkey            34  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_sudo_localaccount               26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_sudo_pam                        26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_sudo_sshkey                     26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_validaccount_localaccount       26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_validaccount_pam                26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  1_validaccount_sshkey             26  192.42.0.0/24    172.17.100.0/24  corpdns -> inetfw -> videoserver
  2_cron                            21  192.42.0.0/24    192.168.100.0/24 corpdns -> videoserver -> inetfw
  2_rootkit                         26  172.17.100.0/24  192.42.0.0/24    videoserver -> inetfw -> corpdns
  3_ssh_apt                         32  192.42.0.0/24    192.168.100.0/24 corpdns -> inetfw -> reposerver -> linuxshare
  3_ssh_healthcheck                 26  192.42.0.0/24    192.168.100.0/24 corpdns -> inetfw -> reposerver -> linuxshare
  3_ssh_puppet                      25  192.42.0.0/24    192.168.100.0/24 corpdns -> inetfw -> reposerver -> linuxshare
  3_vnc_apt                         28  192.168.100.0/24 172.17.100.0/24  linuxshare -> inetfw -> corpdns -> reposerver
  3_vnc_healthcheck                 25  192.168.100.0/24 192.42.0.0/24    linuxshare -> reposerver -> inetfw -> corpdns
  3_vnc_puppet                      22  192.168.100.0/24 192.42.0.0/24    linuxshare -> reposerver -> inetfw -> corpdns
  4                                 22  192.42.0.0/24    192.168.100.0/24 corpdns -> inetfw -> reposerver -> linuxshare
  5                                  3  10.12.0.0/24     172.17.100.0/24  adminpc -> inetfw -> videoserver
  6_macro_binary                    23  192.168.50.0/24  172.17.100.0/24  client -> inetfw -> videoserver
  6_macro_cron                      21  192.168.100.0/24 192.42.0.0/24    inetfw -> client -> videoserver -> corpdns
  6_plugin                          13  192.168.50.0/24  172.17.100.0/24  client -> inetfw -> videoserver
  6_screensharing_binary            39  192.168.50.0/24  192.42.0.0/24    client -> inetfw -> videoserver -> corpdns
  6_screensharing_cron              34  192.168.50.0/24  172.17.100.0/24  client -> inetfw -> videoserver
  7                                 13  192.42.0.0/24    192.168.100.0/24 corpdns -> docker -> inetfw

  all host folders seen (10): adminpc, attacker, client, corpdns, docker, inetfw, linuxshare, reposerver, videoserver, wazuh

  distinct ENTRY zones across 34 runs: {'192.42.0.0/24': 24, '172.17.100.0/24': 1, '192.168.100.0/24': 4, '10.12.0.0/24': 1, '192.168.50.0/24': 4}
  distinct TARGET zones across 34 runs: {'172.17.100.0/24': 23, '192.168.100.0/24': 6, '192.42.0.0/24': 5}

  --- Does this AGREE with the hand-typed camlds_grounding.json? ---
  hand-typed file: thesis_system\data\camlds_grounding.json
  it declares 7 scenarios; the release has 34 scenario-variants.
  Hand-typed entry/target per scenario:
    S1                           entry=Internet         target=DMZ              goal=Persistence
    S2                           entry=DMZ              target=DMZ              goal=Exfiltration
    S3                           entry=Internet         target=LAN              goal=Impact
    S4                           entry=DMZ              target=Firewall         goal=Network Boundary Bridging (Defense Evasion)
    S5                           entry=LAN              target=DMZ              goal=Credential Access
    S6                           entry=User             target=User             goal=Exfiltration
    S7                           entry=Internet         target=DMZ              goal=Credential Access / Exfiltration

  --- subnet <-> symbolic-zone mapping, recovered from target_host ---
  scenario hand target_host   -> subnet          hand calls it derived target host(s)
  S1     VideoServer        172.17.100.0/24    DMZ          videoserver  <= MATCH
  S2     VideoServer        172.17.100.0/24    DMZ          corpdns, inetfw  <= DIFFERS
  S3     FileShare          None               LAN          corpdns, linuxshare, reposerver  <= DIFFERS
  S4     Firewall           None               Firewall     linuxshare  <= DIFFERS
  S5     VideoServer        172.17.100.0/24    DMZ          videoserver  <= MATCH
  S6     Client             192.168.50.0/24    User         corpdns, videoserver  <= DIFFERS
  S7     DockerServer       172.17.100.0/24    DMZ          inetfw  <= DIFFERS

    172.17.100.0/24    = DMZ
    192.168.50.0/24    = User

  >> This recovers the grouping rule from the existing annotation rather
     than inventing one. Any subnet with no row here was never named by
     the hand-typed file and still needs a declared decision.

  >> The release names scenario VARIANTS (e.g. 1_autostart_localaccount)
     while the hand-typed file names base scenarios. Decide, and WRITE DOWN,
     whether all 18 variants of scenario 1 share one zone pair. If they do,
     they are one campaign and must never be split across train and test.

  wrote derived_zones.json

==============================================================================
Q5  Does `attack_times.csv` line up with our parsed corpus?
==============================================================================
  C:\Users\user5\TEMARL\camlds_real\attack_times.csv  ->  904 rows

  quantity                             released       ours  published
  steps / commands                          904        889        904
  technique instances                      1351       1347       1351
  runs                                       34         36         34
  parent-level techniques                    81          -         81

  multi-technique steps : 203 (22.5%)
  mean techniques/step  : 1.494

  runs per base scenario: {'1': 18, '2': 2, '3': 6, '4': 1, '5': 1, '6': 5, '7': 1}
  published expectation : {'1': 18, '2': 2, '3': 6, '4': 1, '5': 1, '6': 5, '7': 1}

  >> SCENARIO 1 IS 522 OF 904 STEPS (58%), across 18 variants.
     This is R7. It is identical in the released data and in ours, so this
     download does NOT fix it. Split by base scenario, never by variant, and
     say so explicitly in the paper.

  >> We parsed 36 playbooks; the release has 34 runs. Find the 2 extra before
     reconciling — they are likely playbooks never executed into the release.

==============================================================================
Q6  Schema of `attacker/logs/attackmate.json` (one scenario)
==============================================================================
  scenario_1_autostart_localaccount.zip :: scenario_1_autostart_localaccount/attacker/logs/attackmate.json   (28.8 KB)
  playbooks shipped in this archive: 0

  not one JSON document — looks like JSON Lines (53 lines)
  all lines parse individually
  records: 53
  keys seen across records:
      start-datetime               in 53/53
      type                         in 53/53
      cmd                          in 53/53
      parameters                   in 53/53

  FIRST RECORD:
    {
      "start-datetime": "2025-09-22T18:29:33.376943",
      "type": "shell",
      "cmd": "echo \"Target:  ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDduw+tvTUXiUk9Zt0BGcA2QfzZEnKgRpluo8UljNhVkDg5xtRUcXahasR+wWebG+QVs4MOk3Gp21SREsxDEtunPctSrgJN0eeu8d/Z//fYQN1bNQd7VEXv7lMnbSHnumFGsjRxZo/ncwSxLMIzlCOLr3jW4wnrZ7vGq3CEO+hf84+mLyTmYCUBGq5riCjG8Sz/GIKPZwZrD0YSn9RbhxKNhZX5IFvl4eYJ5qzgX54v0jn+1A9PPd+8KvVkrlTD8iCMfYMRH0OXYv7CyWZ554wrtpZqGjtmv0PPdUtLsF5k3cphft/oDNwZOXXn/tNivFD4kumZDtbq7zZiR3+0kNHumlyn8VqmHm4D7qpWymIJ29tH2x0+Gw5Ah6uoX53aAqHrP+GrrIzCs9Tjpa+jLYB8ouh947353CarsRXs+5YcowHc70f1+WnFaMCp9Fc2HQfbQzFRIGFbsSEiwgNE3cguxCdGcLEJnBorApj9bVCOj/EYu+Hz3p0fAGNPS1foQFUac+GtR1oiQPCLDZjpedPjC2o/77V4IFvAn6apA3JUxNbqNCDLadGmqx3+YSVsJ4+NWKPiAhxpk5JDYZkojpRSVYIJ2iOvo9ZbG1AabQThNUd7atkikcTt3se2TDz9vg06hALv/+urmJfKtxj98vabw1AGIpOLLiyWTVfsPFp+nw==\"",
      "parameters": {
        "only_if": null,
        "error_if": null,
        "error_if_not": null,
        "loop_if": null,
        "loop_if_not": null,
        "loop_count": "3",
        "exit_on_error": true,
        "save": null,
        "background": false,
        "kill_on_exit": true,
        "metadata": null,
        "interactive": false,
        "creates_session": null,
        "session": null,
        "command_timeout": "

  LAST RECORD:
    {
      "start-datetime": "2025-09-22T18:59:47.284543",
      "type": "sleep",
      "cmd": "sleep",
      "parameters": {
        "only_if": null,
        "error_if": null,
        "error_if_not": null,
        "loop_if": null,
        "loop_if_not": null,
        "loop_count": "3",
        "exit_on_error": true,
        "save": null,
        "background": false,
        "kill_on_exit": true,
        "metadata": null,
        "min_sec": "0",
        "seconds": "30",
        "random": false
      }
    }

  >> The extractor needs, per record: an ordering key, the command that
     ran, its technique label(s) if present, and an execution status so
     failed or retried steps can be handled explicitly rather than
     silently becoming attack transitions.

==============================================================================
WHAT TO DO NEXT
==============================================================================
  1. If Q4 produced zones, diff them against the hand-typed ones by hand and
     record the decision. That converts R4/R5 from typed to derived.
  2. If Q2 found attackmate logs, prefer them over attack_times.csv: they
     record what RAN, including failures and retries, not what was specified.
  3. Do NOT reuse the old 84-label vocabulary blindly — rebuild it from the
     release and document any sub-technique -> parent collapse.
  4. Group scenario variants BEFORE splitting. 58% of the corpus is one
     campaign; a variant-level split silently leaks it.
  5. Only then build windows (16 steps -> next step) and retrain.
```
