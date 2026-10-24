```
CAM-LDS extraction
  repo : C:\Users\User\thesis_project_pev_V2\thesis_project_pev\thesis_project
  out  : C:\Users\User\thesis_project_pev_V2\thesis_project_pev\thesis_project\camlds_real\out
  source: C:\Users\User\thesis_project_pev_V2\thesis_project_pev\thesis_project\camlds_real\attack_times.csv  (904 rows)

==============================================================================
DECLARED DECISIONS
==============================================================================
  D1 ORDER = ascending `start` timestamp.
     event_id is non-monotonic in 27/34 runs and sorting by it breaks
     timestamp order in 28/34. Row order is wrong in 4 runs. Only the
     timestamp is reliable, so it is the sole ordering key.
  D2 EVERY SOURCE ROW IS KEPT. 904 rows over 883 distinct
     (run, event_id) keys; the 18 repeated keys all have distinct
     timestamps, so they are separate executions. Each row carries an
     `occurrence` index. Nothing is merged here.
  D3 VOCABULARY IS REBUILT from the release. Both sub-technique and
     parent forms are emitted; no prior vocabulary is imposed.
  D4 ZONES/GOALS ARE NOT DERIVED. They are carried from the hand-typed
     grounding and labelled as such. Log volume, where available, is
     recorded as CORROBORATING evidence only -- it is confounded by
     per-service logging verbosity and collection settings, and
     agreeing with an annotation does not validate that annotation.
  D5 NO WINDOWS, NO SPLITS, NO COLLAPSING. Those are modelling
     choices and are made downstream where they can be varied.

==============================================================================
RECONCILIATION — every source row accounted for
==============================================================================
  source rows            : 904
  emitted steps          : 904
  distinct source rows   : 904
  dropped                : 0
  merged                 : 0  (D2: nothing is merged here)
  LOSSLESS               : YES

  runs                   : 34
  technique instances    : 1351
  sub-techniques         : 97
  parent techniques      : 81
  multi-technique steps  : 203 (22.5%)

==============================================================================
ORDERING — how far time order moved rows from file order (D1)
==============================================================================
  runs where sorting by time changed row order: 4/34
      6_macro_binary                   2 of 23 positions
      6_macro_cron                     2 of 21 positions
      6_screensharing_binary           2 of 42 positions
      6_screensharing_cron             2 of 36 positions

  If this is empty, file order already was execution order -- but it is
  the timestamp that guarantees it, which is why D1 sorts explicitly.

==============================================================================
REPEATED EXECUTIONS KEPT (D2)
==============================================================================
  rows belonging to a repeated (run, event_id): 39
  distinct repeated keys: 18
      1_pwnkit_localaccount          ev 40   x3  cmd=rm               gaps=[32.7, 16.4]s
      1_pwnkit_pam                   ev 40   x3  cmd=rm               gaps=[32.7, 16.3]s
      1_pwnkit_sshkey                ev 40   x3  cmd=rm               gaps=[32.7, 16.4]s
      1_sudo_localaccount            ev 40   x2  cmd=rm               gaps=[32.7]s
      1_sudo_pam                     ev 40   x2  cmd=rm               gaps=[32.6]s
      1_sudo_sshkey                  ev 40   x2  cmd=rm               gaps=[32.6]s
      1_validaccount_localaccount    ev 40   x2  cmd=rm               gaps=[16.2]s
      1_validaccount_pam             ev 40   x2  cmd=rm               gaps=[16.2]s
      1_validaccount_sshkey          ev 40   x2  cmd=rm               gaps=[16.2]s
      3_vnc_apt                      ev 54   x2  cmd=key              gaps=[60.0]s
      3_vnc_puppet                   ev 59   x2  cmd=sudo__i          gaps=[33.0]s
      6_plugin                       ev 26   x2  cmd=key              gaps=[53.0]s

  Non-zero gaps confirm separate executions rather than duplicate rows.

==============================================================================
SCENARIO BALANCE — read before choosing a split
==============================================================================
  scenario    runs   steps    share
  S1            18     522    57.7%
  S2             2      47     5.2%
  S3             6     160    17.7%
  S4             1      22     2.4%
  S5             1       3     0.3%
  S6             5     137    15.2%
  S7             1      13     1.4%

  >> S1 is 58% of all steps across 18 variants.
     Split by BASE SCENARIO. A variant-level split leaks the same
     campaign into train and test.

==============================================================================
ZONES — carried, not derived (D4)
==============================================================================
  S1  entry=Internet     target=DMZ          host=VideoServer    goal=Persistence
  S2  entry=DMZ          target=DMZ          host=VideoServer    goal=Exfiltration
  S3  entry=Internet     target=LAN          host=FileShare      goal=Impact
  S4  entry=DMZ          target=Firewall     host=Firewall       goal=Network Boundary Bridging (Defense Evasion)
  S5  entry=LAN          target=DMZ          host=VideoServer    goal=Credential Access
  S6  entry=User         target=User         host=Client         goal=Exfiltration
  S7  entry=Internet     target=DMZ          host=DockerServer   goal=Credential Access / Exfiltration

  no volume cross-check (pass --data to enable it).

==============================================================================
WHAT IS DELIBERATELY NOT DONE HERE
==============================================================================
  - no windows, no train/test split, no collapsing of repeats (D5)
  - zones and goals are NOT derived from the release (D4)
  - execution success is not inferred: the release records none
```
