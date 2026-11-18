# Deception literature notes for the CAM-LDS deception study

Written 2026-11-17, before any protocol, code change or run. Every statement below was checked
against the paper's PDF in `PDF/`. These notes feed the pre-registered protocol; they are not results.

Main claim to test (simulation only): *deception agents that know the attacker's history keep
attackers engaged longer and protect assets better than agents without history and than published
deception methods.*

## Papers and what each one gives the study

| paper | DOI | what it did (from the PDF) | use in our study |
|---|---|---|---|
| Dowling, Schukat & Barrett 2018, ECML PKDD (LNAI 11053, 341-355) | 10.1007/978-3-030-10997-4_21 | Live Cowrie SSH honeypot; SARSA; actions allow / block / substitute; reward 1 per attacker command (bash, custom or compound), else 0; 4x more command transitions than a standard high-interaction honeypot. Code: github.com/sosdow/RLHPot | Precedent for our reward (1 per engaged command). Their attackers were real and reacted; ours are simulated. |
| Huang & Zhu 2019, GameSec (LNCS 11836) | 10.1007/978-3-030-32430-8_13 (web record; not printed in the arXiv copy) | SMDP over a 13-node honeynet; per-node actions eject / record / low / high engagement; metrics: occupancy in honeynet (91%), attraction efficiency (0.63), mean first passage time to the normal zone; engagement vs penetration trade-off; Q-learning. Transition parameters not published, no baselines. | Closest model to ours (zones + moving attacker). Borrow metrics: time until the attacker reaches the target zone. Not reproducible (parameters missing). |
| Wang et al. 2020, IEEE Access 8 | 10.1109/ACCESS.2020.2974786 | Q-learning redeploys deception resources on a threat penetration graph; Definition 9 defense success probability (dsp) = successful defense experiments / all experiments (attacker enters a decoy before the database); dsp ~80%, better than three other deployment policies. Parameters in its Table 3. | Origin of the DSR/DSP metric used by Li 2025 and Hawkeyes. Our `protected` uses the same ratio, with an adapted success criterion (PROTOCOL_D1.0.md). Possibly replicable. |
| Anwar, Kamhoua, Leslie & Kiekintveld 2022, IEEE TNSM 19(3):3438 | 10.1109/TNSM.2022.3179965 | Honeypot allocation on attack graphs (entry / intermediate / target nodes); reactive phase as a POMDP solved with Monte-Carlo tree search; defender only partly observes the attacker; 48% better than random and 45% better than greedy (50-node graph); beats fixed, random and less sophisticated policies. | Baselines our reference ladder must include: fixed, random, greedy. A POMDP policy acts on observation history: method support for the history arm. |
| Ferguson-Walter, Major, Johnson & Muhleman 2021, USENIX Security (pp. 1127-1144) | none (USENIX) | 130+ professional red teamers (Tularosa data); decoys absent/present x informed/uninformed. Decoys present: fewer real machines targeted (22.78 vs 31.98, p < .01); 710 commands (52% of commands containing IPs) went to decoys; fewer bytes to real machines (p = .022); fewer EternalBlue IDS alerts (p = .014). p = .004 is Present-Informed vs Present-Uninformed (decoys targeted), NOT decoys vs none. Admin account p = .003 is Present-Informed vs Absent-Uninformed. | The only real-human evidence that decoys absorb attacker effort and protect real hosts. The 52% may justify the range of the efficacy sensitivity check; it is not a calibration (static decoys, ~50 of them, humans). |
| Ferguson-Walter et al. 2019, HICSS (Tularosa design) | 10.24251/HICSS.2019.874 (web record; our PDF is the appendix only) | Experimental design and questionnaires. | Cite for the design only. |
| He, Boyd-Graber, Kwok & Daume 2016, ICML | none | Encoding observations of the opponent into a DQN (DRON) beats DQN on soccer and quiz-bowl. | Method support: our encoder output h is the opponent model; NoHistory is the plain baseline. |
| Hausknecht & Stone 2015, arXiv 1507.06527 (DRQN) | none (arXiv) | Recurrent memory helps under partial observability. | Method support for giving agents history. |
| Pauna, Iacob & Bica 2018, QRASSH (IEEE conference) | not printed | Deep Q-learning SSH honeypot rewarded for downloads; under 20 real episodes; reports loss curves only. | Cite as an idea only; no engagement evidence. |

## Consequences for the study design (to be fixed in the protocol before any run)

1. Reward: keep 1 per engaged command (Dowling precedent).
2. Protection: report defense success probability as the ratio of Wang 2020 Definition 9 (our success
   criterion is adapted: the goal is never reached; see PROTOCOL_D1.0.md); also time until the
   attacker reaches the target zone (Huang & Zhu). Engagement and protection are reported together
   because they trade off (Huang & Zhu).
3. Reference ladder before any learned agent: none, random, fixed (static), greedy, plus a
   clairvoyant ceiling (Anwar's baselines; Wang's static policy).
4. History claim: no deception paper tests history vs no history. Support is general (He 2016, DRQN,
   POMDP in Anwar). State it as the gap our study fills.
5. Every result is labelled "in simulation": the replayed attacker reacts only through the simulated
   movement model, unlike the real attackers in Dowling and Ferguson-Walter.
6. Efficacy sensitivity: report results over a range of efficacy values; Ferguson-Walter's 52% may be
   cited for the range, never as a calibration.
