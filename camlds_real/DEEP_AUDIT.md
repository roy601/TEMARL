```
CAM-LDS DEEP AUDIT
  data    : C:\Users\user5\Downloads\DATASET 01
  archives: 37
  mode    : exhaustive
  per-class examples: 3

==============================================================================
PASS 1 — EVERY ENTRY IN EVERY ARCHIVE
==============================================================================
  No sampling. Each row is written to FULL_INVENTORY.csv.

  archive                                          files   dirs   uncompressed  hosts
  attack-manifestations-interpretation-main.zip       36      2         50.1MB      0
  manifestations_filtered.zip                     17,242 25,354      4,441.8MB     10
  manifestations_raw.zip                          44,473 63,230      9,384.1MB     10
  scenario_1_autostart_localaccount.zip            9,073  1,435      1,059.1MB      5
  scenario_1_autostart_pam.zip                     9,073  1,435      1,060.4MB      5
  scenario_1_autostart_sshkey.zip                  9,072  1,435      1,046.6MB      5
  scenario_1_cron_localaccount.zip                 9,070  1,435      1,005.9MB      5
  scenario_1_cron_pam.zip                          9,069  1,435      1,017.1MB      5
  scenario_1_cron_sshkey.zip                       9,071  1,435      1,014.3MB      5
  scenario_1_pwnkit_localaccount.zip               9,071  1,435      1,010.2MB      5
  scenario_1_pwnkit_pam.zip                        9,070  1,435      1,025.2MB      5
  scenario_1_pwnkit_sshkey.zip                     9,059  1,435      1,071.0MB      5
  scenario_1_racecondition_localaccount.zip        9,065  1,435      1,034.5MB      5
  scenario_1_racecondition_pam.zip                 9,065  1,435      1,024.5MB      5
  scenario_1_racecondition_sshkey.zip              9,067  1,435      1,030.2MB      5
  scenario_1_sudo_localaccount.zip                 9,070  1,435      1,063.9MB      5
  scenario_1_sudo_pam.zip                          9,070  1,435      1,040.3MB      5
  scenario_1_sudo_sshkey.zip                       9,071  1,435      1,004.8MB      5
  scenario_1_validaccount_localaccount.zip         9,071  1,435      1,009.6MB      5
  scenario_1_validaccount_pam.zip                  9,070  1,435      1,006.7MB      5
  scenario_1_validaccount_sshkey.zip               9,069  1,435      1,000.7MB      5
  scenario_2_cron.zip                              9,024  1,435        697.2MB      5
  scenario_2_rootkit.zip                           9,024  1,435        700.6MB      5
  scenario_3_ssh_apt.zip                          12,545  1,864        882.8MB      6
  scenario_3_ssh_healthcheck.zip                  12,526  1,864        863.1MB      6
  scenario_3_ssh_puppet.zip                       12,523  1,864        832.4MB      6
  scenario_3_vnc_apt.zip                          12,538  1,864        897.1MB      6
  scenario_3_vnc_healthcheck.zip                  12,534  1,864        852.4MB      6
  scenario_3_vnc_puppet.zip                       12,531  1,864        833.1MB      6
  scenario_4.zip                                  12,534  1,864        870.6MB      6
  scenario_5.zip                                  11,136  1,803        803.7MB      6
  scenario_6_macro_binary.zip                     11,214  1,819        967.0MB      6
  scenario_6_macro_cron.zip                       11,205  1,819        921.0MB      6
  scenario_6_plugin.zip                           11,209  1,819        918.8MB      6
  scenario_6_screensharing_binary.zip             11,227  1,820      2,332.3MB      6
  scenario_6_screensharing_cron.zip               11,225  1,820      3,042.9MB      6
  scenario_7.zip                                   8,923  1,476        629.8MB      5

  TOTAL entries      : 549,625
  TOTAL uncompressed : 49.45 GB
  TOTAL compressed   : 7.27 GB
  distinct file kinds: 6,157
  full inventory     : C:\Users\user5\TEMARL\camlds_real\audit_out\FULL_INVENTORY.csv

==============================================================================
PASS 2 — HOSTS PRESENT
==============================================================================
  host                  appears in N archives
  attacker                                 36
  corpdns                                  36
  inetfw                                   36
  wazuh                                    36
  videoserver                              28
  linuxshare                                9
  reposerver                                9
  client                                    7
  adminpc                                   3
  docker                                    3

==============================================================================
PASS 3 — EVERY DISTINCT KIND OF FILE, OPENED AND READ
==============================================================================
  6157 distinct kinds. Each is opened and characterised.
  Full detail in FILE_CLASSES.md; the biggest are summarised here.

  kind of file                                               files         MB
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l   3,934   6,225.2
  <scenario>/<host>/logs/log/journal/<hash>/system.journal     149   3,623.9
  <scenario>/<host>/configs/suricata/rules/suricata.rules       68   2,717.3
  <scenario>/<host>/logs/log/audit/audit.log                   114   1,754.4
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l   2,525   1,467.8
  <scenario>/<host>/logs/log/journal/<hash>/user-1001.jour     149   1,249.9
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l   4,390     986.3
  MANIFEST/sequences/<run-step>/<host>/logs/log/audit/audi   1,703     865.1
  MANIFEST/steps/<run-step>/<host>/logs/log/audit/audit.lo   2,358     865.1
  <scenario>/<host>/logs/log/collectd/collectd.log             115     793.6
  <scenario>/<host>/logs/log/suricata/eve.json                  68     717.9
  <scenario>/<host>/configs/etc/alternatives/view              183     699.5
  <scenario>/<host>/configs/etc/alternatives/rvim              183     699.5
  <scenario>/<host>/configs/etc/alternatives/vi                183     699.5
  <scenario>/<host>/configs/etc/alternatives/rview             183     699.5
  <scenario>/<host>/configs/etc/alternatives/ex                183     699.5
  <scenario>/<host>/configs/etc/alternatives/vimdiff           183     699.5
  <scenario>/<host>/configs/etc/alternatives/vim               183     699.5
  <scenario>/<host>/logs/log/journal/<hash>/system@0000000      33     578.8
  <scenario>/<host>/logs/log/journal/<hash>/system@0000000      30     503.3
  MANIFEST/sequences/<run-step>/<host>/logs/log/suricata/e   1,073     476.9
  MANIFEST/steps/<run-step>/<host>/logs/log/suricata/eve.j   1,655     476.9
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/a   1,046     473.5
  <scenario>/<host>/configs/etc/alternatives/liblapack.so.      66     473.3
  MANIFEST/sequences/<run-step>/<host>/logs/alerts/alerts.     434     454.1
  MANIFEST/steps/<run-step>/<host>/logs/alerts/alerts.json     495     454.1
  <scenario>/<host>/configs/etc/filebeat/fields.yml             94     355.5
  <scenario>/<host>/configs/suricata/update/cache/3159a4b0      68     346.9
  <scenario>/<host>/logs/alerts/alerts.json                     34     284.1
  <scenario>/<host>/logs/log/journal/<hash>/user-1000@0000      33     276.8
  MANIFEST/sequences/<run-step>/<host>/logs/log/collectd/c   1,869     259.0
  MANIFEST/steps/<run-step>/<host>/logs/log/collectd/colle   2,962     259.0
  <scenario>/<host>/logs/log/journal/<hash>/user-1000@0000      30     251.7
  <scenario>/<host>/logs/alerts/alerts.log                      34     244.1
  <scenario>/<host>/logs/log/journal/<hash>/user-1001@2b17      26     218.1
  <scenario>/<host>/logs/log/journal/<hash>/system@62f1bab      26     218.1
  <scenario>/<host>/logs/log/journal/<hash>/user-1001@a5f6      26     218.1
  <scenario>/<host>/logs/log/journal/<hash>/system@000635c      26     218.1
  <scenario>/<host>/logs/log/journal/<hash>/system@2b175b2      26     218.1
  <scenario>/<host>/logs/log/journal/<hash>/user-1000@a5f6      26     218.1
  ... 6117 further kinds, all in FILE_CLASSES.md

  formats detected across the opened examples:
      yaml-or-conf             7545
      binary                   4733
      text                     3096
      empty                    942
      iso-timestamped          109
      jsonl                    84
      syslog                   76
      csv-comma                44
      apache-clf               32
      json-object              31
      csv-semicolon            23
      tsv                      15
      auditd                   12
      blank                    12

==============================================================================
PASS 4 — THE FILES THAT MATTER, READ IN FULL
==============================================================================
  attacker/logs/attackmate.json — every record of every run

  archive                                         records types
  manifestations_filtered.zip                           1 {'shell': 1}
  manifestations_raw.zip                                1 {'shell': 1}
  scenario_1_autostart_localaccount.zip                53 {'msf-session': 31, 'sleep': 7, 'ssh': 7, 'shell': 6}
  scenario_1_autostart_pam.zip                         53 {'msf-session': 31, 'sleep': 7, 'ssh': 7, 'shell': 6}
  scenario_1_autostart_sshkey.zip                      53 {'msf-session': 31, 'sleep': 7, 'ssh': 7, 'shell': 6}
  scenario_1_cron_localaccount.zip                     49 {'msf-session': 29, 'ssh': 7, 'sleep': 6, 'shell': 5}
  scenario_1_cron_pam.zip                              49 {'msf-session': 29, 'ssh': 7, 'sleep': 6, 'shell': 5}
  scenario_1_cron_sshkey.zip                           49 {'msf-session': 29, 'ssh': 7, 'sleep': 6, 'shell': 5}
  scenario_1_pwnkit_localaccount.zip                   39 {'msf-session': 21, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_pwnkit_pam.zip                            39 {'msf-session': 21, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_pwnkit_sshkey.zip                         39 {'msf-session': 21, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_racecondition_localaccount.zip            53 {'msf-session': 31, 'sleep': 7, 'ssh': 7, 'shell': 6}
  scenario_1_racecondition_pam.zip                     53 {'msf-session': 31, 'sleep': 7, 'ssh': 7, 'shell': 6}
  scenario_1_racecondition_sshkey.zip                  54 {'msf-session': 32, 'sleep': 7, 'ssh': 7, 'shell': 6}
  scenario_1_sudo_localaccount.zip                     38 {'msf-session': 20, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_sudo_pam.zip                              38 {'msf-session': 20, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_sudo_sshkey.zip                           38 {'msf-session': 20, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_validaccount_localaccount.zip             38 {'msf-session': 20, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_validaccount_pam.zip                      38 {'msf-session': 20, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_1_validaccount_sshkey.zip                   38 {'msf-session': 20, 'ssh': 7, 'shell': 5, 'sleep': 5}
  scenario_2_cron.zip                                  29 {'sliver-session': 16, 'mktemp': 4, 'ssh': 2, 'sliver': 2}
  scenario_2_rootkit.zip                               43 {'sliver-session': 16, 'ssh': 11, 'mktemp': 5, 'shell': 3}
  scenario_3_ssh_apt.zip                               55 {'ssh': 28, 'msf-session': 15, 'sleep': 4, 'shell': 2}
  scenario_3_ssh_healthcheck.zip                       41 {'msf-session': 17, 'ssh': 15, 'sleep': 2, 'shell': 1}
  scenario_3_ssh_puppet.zip                            39 {'ssh': 15, 'msf-session': 15, 'sleep': 2, 'shell': 1}
  scenario_3_vnc_apt.zip                               77 {'vnc': 38, 'sleep': 16, 'msf-session': 15, 'mktemp': 1}
  scenario_3_vnc_healthcheck.zip                       64 {'vnc': 24, 'msf-session': 17, 'sleep': 16, 'mktemp': 1}
  scenario_3_vnc_puppet.zip                            67 {'vnc': 27, 'sleep': 18, 'msf-session': 15, 'mktemp': 1}
  scenario_4.zip                                       46 {'ssh': 24, 'sleep': 15, 'sliver': 2, 'shell': 2}
  scenario_5.zip                                        7 {'shell': 3, 'setvar': 1, 'debug': 1, 'sleep': 1}
  scenario_6_macro_binary.zip                          51 {'msf-session': 25, 'vnc': 11, 'sleep': 10, 'shell': 1}
  scenario_6_macro_cron.zip                            51 {'msf-session': 25, 'vnc': 11, 'sleep': 10, 'shell': 1}
  scenario_6_plugin.zip                                56 {'vnc': 29, 'sleep': 26, 'shell': 1}
  scenario_6_screensharing_binary.zip                 178 {'vnc': 80, 'sleep': 66, 'msf-session': 21, 'shell': 3}
  scenario_6_screensharing_cron.zip                   165 {'vnc': 73, 'sleep': 59, 'msf-session': 24, 'shell': 3}
  scenario_7.zip                                       26 {'sleep': 9, 'shell': 6, 'sliver-session': 3, 'sliver': 2}

  runs read: 36 | total records: 1,808
  EVERY top-level key seen: {'start-datetime': 1808, 'type': 1808, 'cmd': 1808, 'parameters': 1808}
  every `type` value: {'msf-session': 648, 'sleep': 361, 'vnc': 293, 'ssh': 221, 'shell': 127, 'sliver-session': 37, 'msf-module': 34, 'mktemp': 20, 'setvar': 15, 'msf-payload': 10, 'include': 10, 'sliver': 8, 'webserv': 8, 'debug': 5, 'sftp': 3, 'loop': 3, 'regex': 2, 'http-client': 2, 'father': 1}

  attacker/facts.json — what it describes

==============================================================================
PASS 5 — EXHAUSTIVE: EVERY TEXT FILE DECOMPRESSED AND COUNTED
==============================================================================
  No estimates. Every text file is decompressed and its lines counted.

  files counted: 386,504 | bytes: 48.96 GB
  TOTAL LINES  : 213,373,457

  kind of file                                                      lines
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l     28,873,373
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l     24,420,301
  <scenario>/<host>/logs/log/collectd/collectd.log             22,511,771
  <scenario>/<host>/configs/etc/filebeat/fields.yml             9,651,168
  MANIFEST/sequences/<run-step>/<host>/logs/log/collectd/c      7,558,817
  MANIFEST/steps/<run-step>/<host>/logs/log/collectd/colle      7,558,817
  <scenario>/<host>/logs/log/audit/audit.log                    6,981,674
  <scenario>/<host>/configs/etc/dictionaries-common/words       4,903,698
  <scenario>/<host>/facts.json                                  4,781,325
  <scenario>/<host>/logs/log/journal/<hash>/system.journal      4,347,642
  <scenario>/<host>/configs/suricata/rules/suricata.rules       4,195,236
  MANIFEST/sequences/<run-step>/<host>/logs/log/audit/audi      3,375,964
  MANIFEST/steps/<run-step>/<host>/logs/log/audit/audit.lo      3,375,964
  <scenario>/<host>/logs/alerts/alerts.log                      2,951,429
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l      2,563,044
  <scenario>/<host>/configs/etc/alternatives/view               2,266,314
  <scenario>/<host>/configs/etc/alternatives/rvim               2,266,314
  <scenario>/<host>/configs/etc/alternatives/vi                 2,266,314
  <scenario>/<host>/configs/etc/alternatives/rview              2,266,314
  <scenario>/<host>/configs/etc/alternatives/ex                 2,266,314
  <scenario>/<host>/configs/etc/alternatives/vimdiff            2,266,314
  <scenario>/<host>/configs/etc/alternatives/vim                2,266,314
  <scenario>/<host>/logs/.msf4/store/modules_metadata.json      2,003,897
  <scenario>/<host>/logs/log/suricata/stats.log                 1,801,359
  <scenario>/<host>/logs/log/journal/<hash>/system@0000000      1,606,060
  <scenario>/<host>/logs/log/suricata/eve.json                  1,062,074
  <scenario>/<host>/configs/etc/alternatives/shimx64.efi.s        998,565
  <scenario>/<host>/logs/alerts/2025/Sep/ossec-alerts-22.l        985,781
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/l        928,333
  <scenario>/<host>/logs/alerts/2025/Sep/ossec-alerts-24.l        824,988
  MANIFEST/sequences/<run-step>/<host>/logs/log/suricata/e        803,560
  MANIFEST/steps/<run-step>/<host>/logs/log/suricata/eve.j        803,560
  MANIFEST/techniques/<technique>/<run-step>/<host>/logs/a        746,538
  MANIFEST/sequences/<run-step>/<host>/logs/access.log.N          746,370
  MANIFEST/steps/<run-step>/<host>/logs/access.log.N              746,370
  <scenario>/<host>/configs/html/donotcry                         658,172
  <scenario>/<host>/configs/etc/ssl/certs/ca-certificates.        637,238
  <scenario>/<host>/configs/etc/alternatives/nawk                 609,899
  <scenario>/<host>/configs/etc/alternatives/awk                  609,899
  <scenario>/<host>/logs/log/syslog                               575,644

==============================================================================
VERDICT
==============================================================================
  Read the numbers above before this section; it is an interpretation,
  and the tables are the evidence.

  - 549,625 entries across 37 archives, 49.45 GB uncompressed, in 6,157 distinct kinds of file.
  - Full per-file inventory in FULL_INVENTORY.csv; every distinct kind
    opened and sampled in FILE_CLASSES.md.
  - attackmate.json: 1,808 records across 36 runs. Keys seen: ['cmd', 'parameters', 'start-datetime', 'type'].
    >> NO technique label in ANY record of ANY run. Confirmed by
       full read, not by sampling.
  - facts.json describes the ATTACKER host, so it cannot identify targets.

  Use FILE_CLASSES.md to decide what else is worth reading. Anything
  this audit did not open is in FULL_INVENTORY.csv with its size and
  CRC, so nothing is hidden -- only unread, and nameable.
```
