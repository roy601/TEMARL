```
CAM-LDS verification pass
  data : C:\Users\user5\Downloads\DATASET 01
  repo : C:\Users\user5\TEMARL
  37 distinct archives

==============================================================================
V1  INTEGRITY — published MD5 vs the bytes on disk
==============================================================================
  checksums from Zenodo record 18861762 (36 files)

  attack-manifestations-interpretation-main.zip  (GitHub zip, not in the Zenodo record)
  manifestations_filtered.zip                    MISMATCH
      size  disk 213728643  published 213771977
      md5   disk e9d17ad99897b952abddb25838a56a7b
            published cfc14140b2e396a60989b8379eafca1f

  verified OK : 35
  MISMATCHED  : 1
  not in record: 0
  !! Re-download any mismatched archive before using it.

==============================================================================
V2  SEQUENCE EQUIVALENCE — per run and per step, not totals
==============================================================================
  The audit compared totals and called it agreement. Totals can match
  while sequences differ completely. This compares the actual content.

  ours    : thesis_system\data\camlds_grounding_verified.json
  released: attack_times.csv (904 rows)

  our runs: 36   released runs: 34
  Names do not correspond (ours: scenario_1_a_a.j2, release:
  1_autostart_localaccount), so alignment is by CONTENT, not by name.

  released run                    rel  ours     J  verdict     best-matching playbook
  1_autostart_localaccount         44    44  1.00  IDENTICAL   scenario_1_c_b.j2
  1_autostart_pam                  44    44  1.00  same set    scenario_1_c_c.j2
  1_autostart_sshkey               44    44  1.00  same set    scenario_1_c_a.j2
  1_cron_localaccount              46    46  1.00  same set    scenario_1_e_b.j2
  1_cron_pam                       46    46  1.00  same set    scenario_1_e_c.j2
  1_cron_sshkey                    46    46  1.00  same set    scenario_1_e_a.j2
  1_pwnkit_localaccount            45    45  1.00  same set    scenario_1_a_b.j2
  1_pwnkit_pam                     45    45  1.00  same set    scenario_1_a_c.j2
  1_pwnkit_sshkey                  45    45  1.00  same set    scenario_1_a_a.j2
  1_racecondition_localaccount     50    51  1.00  same set    scenario_1_d_b.j2
  1_racecondition_pam              50    51  1.00  same set    scenario_1_d_c.j2
  1_racecondition_sshkey           50    51  1.00  same set    scenario_1_d_a.j2
  1_sudo_localaccount              44    44  1.00  same set    scenario_1_b_b.j2
  1_sudo_pam                       44    44  1.00  same set    scenario_1_b_c.j2
  1_sudo_sshkey                    44    44  1.00  same set    scenario_1_b_a.j2
  1_validaccount_localaccount      44    44  1.00  same set    scenario_1_f_b.j2
  1_validaccount_pam               44    44  1.00  same set    scenario_1_f_c.j2
  1_validaccount_sshkey            44    44  1.00  same set    scenario_1_f_a.j2
  2_cron                           29    29  1.00  IDENTICAL   scenario_2_a_a.j2
  2_rootkit                        35    35  1.00  same set    scenario_2_a_c.j2
  3_ssh_apt                        43    37  1.00  same set    scenario_3_a_c.j2
  3_ssh_healthcheck                30    24  0.95  differs     scenario_3_a_a.j2
  3_ssh_puppet                     35    29  0.95  differs     scenario_3_a_d.j2
  3_vnc_apt                        36    30  1.00  same set    scenario_3_b_c.j2
  3_vnc_healthcheck                32    26  0.95  differs     scenario_3_b_a.j2
  3_vnc_puppet                     28    22  0.94  differs     scenario_3_b_d.j2
  4                                27    27  1.00  IDENTICAL   scenario_4.j2
  5                                 5     5  1.00  IDENTICAL   scenario_5.j2
  6_macro_binary                   25    19  0.92  differs     scenario_6_a_a.j2
  6_macro_cron                     22    16  0.90  differs     scenario_6_a_b.j2
  6_plugin                         41    45  1.00  same set    scenario_6_c.j2
  6_screensharing_binary           67    61  1.00  same set    scenario_6_b_a.j2
  6_screensharing_cron             54    48  1.00  same set    scenario_6_b_b.j2
  7                                23    23  1.00  IDENTICAL   scenario_7.j2

  >> 5 of 34 released runs are ORDER-IDENTICAL to a
     playbook of ours. 'J' is set overlap: J=1.00 with verdict 'same set'
     means identical techniques in a DIFFERENT order or multiplicity.

  >> our playbooks never chosen as a best match (2): scenario_3_a_b.j2, scenario_3_b_b.j2
     With 36 ours against 34 released, at least 2 must be unmatched.
     These are the candidates for the 36-vs-34 discrepancy.

  This per-run comparison, NOT the agreement of totals, is what the
  claim 'our corpus matches the published ground truth' has to rest on.

==============================================================================
V3  THE MISSING STEPS — name them
==============================================================================
  label rows            : 883
  steps/ folders        : 883
  labelled, NO folder   : 0
  folder, NO label row  : 0


==============================================================================
V4  attackmate SCHEMA — every run, not one
==============================================================================
  runs read: 34 / 34
  total records across all runs: 1806

  top-level keys (count across all records):
      start-datetime               1806
      type                         1806
      cmd                          1806
      parameters                   1806

  `type` values:
      msf-session                  648
      sleep                        361
      vnc                          293
      ssh                          221
      shell                        125
      sliver-session               37
      msf-module                   34
      mktemp                       20
      setvar                       15
      msf-payload                  10
      include                      10
      sliver                       8
      webserv                      8
      debug                        5
      sftp                         3

  parameters.* keys:
      only_if                      1806
      error_if                     1806
      error_if_not                 1806
      loop_if                      1806
      loop_if_not                  1806
      loop_count                   1806
      exit_on_error                1806
      save                         1806
      background                   1806
      kill_on_exit                 1806
      metadata                     1806
      session                      1361
      read                         773
      creates_session              676
      stdapi                       648
      write                        648
      end_str                      648
      port                         529
      hostname                     517
      password                     517
      min_sec                      361
      seconds                      361
      random                       361
      interactive                  346
      command_timeout              346

  fields that could be a TECHNIQUE LABEL : NONE
  fields that could be EXECUTION STATUS  : ['parameters.arch', 'parameters.enforce_otp', 'parameters.exit', 'parameters.exit_on_error', 'parameters.force', 'parameters.force_encode', 'parameters.kill_on_exit', 'parameters.srcport']

  >> Confirmed across every run: attackmate.json carries no technique
     label. attack_times.csv stays the label source.
  >> A status-like field EXISTS. Inspect it: if it records outcomes,
     failed steps can be handled explicitly after all.

  run                                      records
  scenario_1_autostart_localaccount.zip    53
  scenario_1_autostart_pam.zip             53
  scenario_1_autostart_sshkey.zip          53
  scenario_1_cron_localaccount.zip         49
  scenario_1_cron_pam.zip                  49
  scenario_1_cron_sshkey.zip               49
  scenario_1_pwnkit_localaccount.zip       39
  scenario_1_pwnkit_pam.zip                39
  scenario_1_pwnkit_sshkey.zip             39
  scenario_1_racecondition_localaccount.zip 53
  scenario_1_racecondition_pam.zip         53
  scenario_1_racecondition_sshkey.zip      54
  scenario_1_sudo_localaccount.zip         38
  scenario_1_sudo_pam.zip                  38
  scenario_1_sudo_sshkey.zip               38
  scenario_1_validaccount_localaccount.zip 38
  scenario_1_validaccount_pam.zip          38
  scenario_1_validaccount_sshkey.zip       38
  scenario_2_cron.zip                      29
  scenario_2_rootkit.zip                   43
  scenario_3_ssh_apt.zip                   55
  scenario_3_ssh_healthcheck.zip           41
  scenario_3_ssh_puppet.zip                39
  scenario_3_vnc_apt.zip                   77
  scenario_3_vnc_healthcheck.zip           64
  scenario_3_vnc_puppet.zip                67
  scenario_4.zip                           46
  scenario_5.zip                           7
  scenario_6_macro_binary.zip              51
  scenario_6_macro_cron.zip                51
  scenario_6_plugin.zip                    56
  scenario_6_screensharing_binary.zip      178
  scenario_6_screensharing_cron.zip        165
  scenario_7.zip                           26

==============================================================================
V5  ZONE EVIDENCE NOT YET TRIED
==============================================================================
  Derivation from log PRESENCE failed (2 of 7). That rules out one
  heuristic, not every route. These sources were never opened.

  (a) attacker/facts.json  — from scenario_1_autostart_localaccount.zip
      1221789 bytes
      keys: ['ansible_all_ipv4_addresses', 'ansible_all_ipv6_addresses', 'ansible_apparmor', 'ansible_architecture', 'ansible_bios_date', 'ansible_bios_vendor', 'ansible_bios_version', 'ansible_board_asset_tag', 'ansible_board_name', 'ansible_board_serial', 'ansible_board_vendor', 'ansible_board_version', 'ansible_chassis_asset_tag', 'ansible_chassis_serial', 'ansible_chassis_vendor', 'ansible_chassis_version', 'ansible_check_mode', 'ansible_cmdline', 'ansible_date_time', 'ansible_default_ipv4', 'ansible_default_ipv6', 'ansible_device_links', 'ansible_devices', 'ansible_diff_mode', 'ansible_distribution', 'ansible_distribution_file_parsed', 'ansible_distribution_file_path', 'ansible_distribution_file_variety', 'ansible_distribution_major_version', 'ansible_distribution_release']
        ansible_all_ipv4_addresses = ['192.42.1.174']
        ansible_all_ipv6_addresses = ['fe80::f816:3eff:fe8f:661f']
        ansible_apparmor = {'status': 'enabled'}
        ansible_architecture = x86_64
        ansible_bios_date = 04/01/2014
        ansible_bios_vendor = SeaBIOS
        ansible_bios_version = 1.15.0-1
        ansible_board_asset_tag = NA
        ansible_board_name = NA
        ansible_board_serial = NA
        ansible_board_vendor = NA
        ansible_board_version = NA

  (b) per-host log VOLUME per run — the objective should attract more
      logging than a host that merely resolved a DNS name.

      run                            hosts by log bytes (top 4)
      1_autostart_localaccount       videoserver:16339KB  wazuh:12344KB  corpdns:842KB  inetfw:283KB
      1_autostart_pam                videoserver:16387KB  wazuh:10501KB  corpdns:845KB  inetfw:358KB
      1_autostart_sshkey             videoserver:16228KB  wazuh:12912KB  corpdns:907KB  inetfw:285KB
      1_cron_localaccount            videoserver:15809KB  wazuh:11370KB  corpdns:842KB  inetfw:313KB
      1_cron_pam                     videoserver:15784KB  wazuh:12553KB  corpdns:845KB  inetfw:266KB
      1_cron_sshkey                  videoserver:15805KB  wazuh:12386KB  corpdns:842KB  inetfw:288KB
      1_pwnkit_localaccount          videoserver:15613KB  wazuh:12672KB  corpdns:842KB  inetfw:363KB
      1_pwnkit_pam                   videoserver:15537KB  wazuh:12176KB  corpdns:842KB  inetfw:309KB
      1_pwnkit_sshkey                videoserver:15792KB  wazuh:12278KB  corpdns:842KB  inetfw:316KB
      1_racecondition_localaccount   videoserver:12580KB  wazuh:12139KB  corpdns:842KB  inetfw:324KB
      1_racecondition_pam            videoserver:12602KB  wazuh:11583KB  corpdns:845KB  inetfw:292KB
      1_racecondition_sshkey         videoserver:12485KB  wazuh:12169KB  corpdns:842KB  inetfw:312KB
      1_sudo_localaccount            videoserver:15691KB  wazuh:12427KB  corpdns:845KB  inetfw:305KB
      1_sudo_pam                     videoserver:15749KB  wazuh:12978KB  corpdns:842KB  inetfw:275KB
      1_sudo_sshkey                  videoserver:15842KB  wazuh:12185KB  corpdns:845KB  inetfw:292KB
      1_validaccount_localaccount    videoserver:15697KB  wazuh:12956KB  corpdns:842KB  inetfw:289KB
      1_validaccount_pam             videoserver:15885KB  wazuh:12088KB  corpdns:842KB  inetfw:278KB
      1_validaccount_sshkey          videoserver:15895KB  wazuh:12432KB  corpdns:842KB  inetfw:276KB
      2_cron                         videoserver:198KB  inetfw:80KB  attacker:36KB  wazuh:7KB
      2_rootkit                      videoserver:371KB  wazuh:75KB  attacker:42KB  inetfw:14KB
      3_ssh_apt                      linuxshare:11153KB  reposerver:2788KB  attacker:413KB  inetfw:70KB
      3_ssh_healthcheck              linuxshare:10488KB  reposerver:1524KB  attacker:396KB  wazuh:9KB
      3_ssh_puppet                   reposerver:1548KB  attacker:398KB  linuxshare:207KB  wazuh:9KB
      3_vnc_apt                      linuxshare:11336KB  reposerver:714KB  attacker:399KB  inetfw:19KB
      3_vnc_healthcheck              linuxshare:10694KB  attacker:397KB  reposerver:168KB  wazuh:5KB
      3_vnc_puppet                   linuxshare:429KB  attacker:396KB  reposerver:157KB  wazuh:5KB
      4                              reposerver:1669KB  inetfw:969KB  linuxshare:129KB  wazuh:55KB
      5                              videoserver:79KB  wazuh:9KB  attacker:7KB  adminpc:2KB
      6_macro_binary                 client:1528KB  attacker:31KB  videoserver:19KB  wazuh:6KB
      6_macro_cron                   client:985KB  videoserver:88KB  attacker:30KB  wazuh:5KB
      6_plugin                       client:9108KB  videoserver:129KB  attacker:28KB  inetfw:21KB
      6_screensharing_binary         client:6609KB  videoserver:100KB  attacker:84KB  wazuh:49KB
      6_screensharing_cron           client:2790KB  videoserver:123KB  attacker:75KB  wazuh:46KB
      7                              corpdns:845KB  docker:492KB  attacker:35KB  inetfw:22KB

      >> Compare the heaviest NON-infrastructure host against the
         hand-typed target_host. If they agree, volume is the better
         signal and the zones become source-supported after all.

  (c) the techniques/ grouping — never inspected; it may key steps to
      techniques directly, which presence-ordering does not.
      97 distinct technique-group folders; first 20:
      ['T1003-000', 'T1003-008', 'T1005-000', 'T1007-000', 'T1010-000', 'T1014-000', 'T1016-000', 'T1018-000', 'T1021-000', 'T1021-004', 'T1021-005', 'T1033-000', 'T1036-005', 'T1039-000', 'T1040-000', 'T1041-000', 'T1046-000', 'T1049-000', 'T1053-000', 'T1053-003']

  (d) NOT machine-checkable here: the CAM-LDS paper's own scenario
      descriptions (Sec 3.4, Figs 5-11) are where the hand-typed zones
      came from. 'Source-supported' via the paper is achievable even
      though 'derivable from logs alone' is not.

==============================================================================
WHAT THIS SETTLES
==============================================================================
  V1 whether the download is intact, by published MD5.
  V2 whether our corpus matches the release in CONTENT, not just totals.
  V3 exactly which labelled steps produced no filtered log.
  V4 whether attackmate.json carries labels or status in ANY run.
  V5 whether zones are recoverable by a route other than log presence.
```
