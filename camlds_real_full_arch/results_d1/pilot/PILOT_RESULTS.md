# D1.0 pilot (validation only, before the freeze)

Validation runs only; seeds 101-103; 200k environment steps; means over seeds.
E1 = engaged commands per episode; P1 = defense success; depth = distinct techniques engaged; exposed = share of episodes where the deception was exposed.

## fold 1_cron_sshkey (validation run: 1_autostart_localaccount)

| policy | E1 | P1 | depth | exposed |
|---|---|---|---|---|
| none | 0.00 | 0.00 | 0.00 | 0.00 |
| random | 2.40 | 0.00 | 4.10 | 0.10 |
| static | 2.40 | 0.00 | 0.90 | 0.20 |
| fixed | 7.20 | 0.10 | 2.30 | 0.40 |
| greedy | 5.00 | 0.00 | 1.80 | 0.20 |
| planner | 8.60 | 0.20 | 3.60 | 0.40 |
| clairvoyant | 14.50 | 0.50 | 15.60 | 0.40 |
| **allpos, engagement reward** | 13.77 | 0.50 | 15.70 | 0.33 |
| **allpos, proposal reward** | 13.60 | 0.50 | 15.73 | 0.33 |
| **NoHistory, engagement reward** | 12.23 | 0.67 | 5.57 | 0.23 |
| **NoHistory, proposal reward** | 12.23 | 0.67 | 5.70 | 0.27 |
| **lstm_allpos, engagement reward** | 13.77 | 0.50 | 13.83 | 0.30 |
| **lstm_allpos, proposal reward** | 13.83 | 0.47 | 15.70 | 0.27 |

## fold 3_vnc_puppet (validation run: 3_ssh_apt)

| policy | E1 | P1 | depth | exposed |
|---|---|---|---|---|
| none | 0.00 | 0.00 | 0.00 | 0.00 |
| random | 2.60 | 0.00 | 2.70 | 0.60 |
| static | 4.10 | 0.00 | 3.00 | 0.60 |
| fixed | 8.60 | 0.00 | 4.90 | 0.60 |
| greedy | 7.50 | 0.00 | 6.20 | 0.60 |
| planner | 5.40 | 0.00 | 4.30 | 0.80 |
| clairvoyant | 20.40 | 0.50 | 14.80 | 0.40 |
| **allpos, engagement reward** | 11.43 | 0.07 | 8.23 | 0.67 |
| **allpos, proposal reward** | 10.80 | 0.07 | 8.30 | 0.70 |
| **NoHistory, engagement reward** | 9.83 | 0.00 | 6.60 | 0.53 |
| **NoHistory, proposal reward** | 11.57 | 0.10 | 9.80 | 0.53 |
| **lstm_allpos, engagement reward** | 12.97 | 0.17 | 10.10 | 0.60 |
| **lstm_allpos, proposal reward** | 11.27 | 0.07 | 8.87 | 0.67 |

## fold 6_macro_cron (validation run: 6_macro_binary)

| policy | E1 | P1 | depth | exposed |
|---|---|---|---|---|
| none | 0.00 | 0.00 | 0.00 | 0.00 |
| random | 2.10 | 0.00 | 2.10 | 0.10 |
| static | 4.20 | 0.00 | 4.00 | 0.20 |
| fixed | 12.70 | 0.60 | 8.10 | 0.20 |
| greedy | 9.20 | 0.00 | 5.70 | 0.20 |
| planner | 11.20 | 0.50 | 6.70 | 0.10 |
| clairvoyant | 18.50 | 0.70 | 10.70 | 0.10 |
| **allpos, engagement reward** | 14.57 | 0.53 | 7.50 | 0.17 |
| **allpos, proposal reward** | 15.20 | 0.57 | 7.87 | 0.13 |
| **NoHistory, engagement reward** | 12.80 | 0.43 | 6.53 | 0.17 |
| **NoHistory, proposal reward** | 13.60 | 0.57 | 7.53 | 0.17 |
| **lstm_allpos, engagement reward** | 15.13 | 0.53 | 7.60 | 0.17 |
| **lstm_allpos, proposal reward** | 15.03 | 0.57 | 7.70 | 0.13 |

## Decisions (rules declared before the pilot)

- R1 works: **PASS** {"1_cron_sshkey": {"allpos": true, "NoHistory": true, "lstm_allpos": true}, "3_vnc_puppet": {"allpos": true, "NoHistory": true, "lstm_allpos": true}, "6_macro_cron": {"allpos": true, "NoHistory": true, "lstm_allpos": true}}
- R2 reward means: {"engagement": {"E1": 12.944444444444443, "depth": 9.074074074074074, "P1": 0.3777777777777777}, "proposal": {"E1": 13.014814814814812, "depth": 9.68888888888889, "P1": 0.39629629629629626}}
- R2 reward for the main study: **proposal**
- R3: history differences above are reported only; they decide nothing.
