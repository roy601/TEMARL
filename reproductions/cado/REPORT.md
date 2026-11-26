# CADO (Huang et al., Future Internet 18(10), 552, 2026): reproduction from Supplementary Material S1

**Paper verdict: reproduced (every primary target MATCH).**

- Targets: 333 printed numbers; MATCH 326, CLOSE 0, NO MATCH 0, NOT ATTEMPTED 7. Primary (208): MATCH 208, CLOSE 0, NO MATCH 0, NOT ATTEMPTED 0.
- The authors' code ran unchanged (DECISIONS 5, 6, 15): `code/reproduce_submitted.py` exit 0; `code/revision_analysis.py` exit 0; `prototype/run_poc.py` exit 0. `reproduce_submitted.py` ends with its own comparison of every scientific value with the authors' archived outputs (1e-12); exit 0 means it passed.
- Our fresh outputs against the authors' archived ones, timing columns excluded: 17 of 17 files equal within 1e-12.
- Host timings (decision and parsing latency, throughput) are NOT ATTEMPTED (DECISIONS 7).
- Scope (DECISIONS 14): a match shows that the released code produces the published numbers. The alerts, attackers and outcomes are synthetic; nothing here tests the simulator's realism.

## Every target

| id | table or section | quantity | published | ours | difference | verdict |
|---|---|---|---|---|---|---|
| T2.Static.utility.mean | Table 2 | primary, Static, defensive utility, mean (primary) | 0.6853 | 0.685326 | +2.62e-05 | MATCH |
| T2.Static.utility.ci_low | Table 2 | primary, Static, defensive utility, ci_low | 0.6831 | 0.683137 | +3.65e-05 | MATCH |
| T2.Static.utility.ci_high | Table 2 | primary, Static, defensive utility, ci_high | 0.6875 | 0.687516 | +1.64e-05 | MATCH |
| T2.Adaptive.utility.mean | Table 2 | primary, Adaptive, defensive utility, mean (primary) | 0.6213 | 0.621327 | +2.73e-05 | MATCH |
| T2.Adaptive.utility.ci_low | Table 2 | primary, Adaptive, defensive utility, ci_low | 0.6192 | 0.619166 | -3.43e-05 | MATCH |
| T2.Adaptive.utility.ci_high | Table 2 | primary, Adaptive, defensive utility, ci_high | 0.6234 | 0.623379 | -2.13e-05 | MATCH |
| T2.Consensus.utility.mean | Table 2 | primary, Consensus, defensive utility, mean (primary) | 0.6953 | 0.695279 | -2.11e-05 | MATCH |
| T2.Consensus.utility.ci_low | Table 2 | primary, Consensus, defensive utility, ci_low | 0.6933 | 0.693337 | +3.73e-05 | MATCH |
| T2.Consensus.utility.ci_high | Table 2 | primary, Consensus, defensive utility, ci_high | 0.6973 | 0.697287 | -1.33e-05 | MATCH |
| T2.CADO.utility.mean | Table 2 | primary, CADO, defensive utility, mean (primary) | 0.7020 | 0.702014 | +1.37e-05 | MATCH |
| T2.CADO.utility.ci_low | Table 2 | primary, CADO, defensive utility, ci_low | 0.7003 | 0.700260 | -4.05e-05 | MATCH |
| T2.CADO.utility.ci_high | Table 2 | primary, CADO, defensive utility, ci_high | 0.7038 | 0.703816 | +1.64e-05 | MATCH |
| T2.Static.redirection_precision.mean | Table 2 | primary, Static, redirection precision, mean (primary) | 0.6847 | 0.684678 | -2.22e-05 | MATCH |
| T2.Static.redirection_precision.ci_low | Table 2 | primary, Static, redirection precision, ci_low | 0.6753 | 0.675319 | +1.92e-05 | MATCH |
| T2.Static.redirection_precision.ci_high | Table 2 | primary, Static, redirection precision, ci_high | 0.6940 | 0.694046 | +4.58e-05 | MATCH |
| T2.Adaptive.redirection_precision.mean | Table 2 | primary, Adaptive, redirection precision, mean (primary) | 0.5908 | 0.590794 | -5.79e-06 | MATCH |
| T2.Adaptive.redirection_precision.ci_low | Table 2 | primary, Adaptive, redirection precision, ci_low | 0.5823 | 0.582332 | +3.21e-05 | MATCH |
| T2.Adaptive.redirection_precision.ci_high | Table 2 | primary, Adaptive, redirection precision, ci_high | 0.5994 | 0.599397 | -2.63e-06 | MATCH |
| T2.Consensus.redirection_precision.mean | Table 2 | primary, Consensus, redirection precision, mean (primary) | 0.6978 | 0.697814 | +1.36e-05 | MATCH |
| T2.Consensus.redirection_precision.ci_low | Table 2 | primary, Consensus, redirection precision, ci_low | 0.6890 | 0.689046 | +4.58e-05 | MATCH |
| T2.Consensus.redirection_precision.ci_high | Table 2 | primary, Consensus, redirection precision, ci_high | 0.7069 | 0.706929 | +2.89e-05 | MATCH |
| T2.CADO.redirection_precision.mean | Table 2 | primary, CADO, redirection precision, mean (primary) | 0.7282 | 0.728191 | -9.05e-06 | MATCH |
| T2.CADO.redirection_precision.ci_low | Table 2 | primary, CADO, redirection precision, ci_low | 0.7191 | 0.719103 | +3.31e-06 | MATCH |
| T2.CADO.redirection_precision.ci_high | Table 2 | primary, CADO, redirection precision, ci_high | 0.7376 | 0.737636 | +3.62e-05 | MATCH |
| T2.Static.engagement_rate.mean | Table 2 | primary, Static, engagement rate, mean (primary) | 0.9416 | 0.941562 | -3.83e-05 | MATCH |
| T2.Static.engagement_rate.ci_low | Table 2 | primary, Static, engagement rate, ci_low | 0.9378 | 0.937764 | -3.61e-05 | MATCH |
| T2.Static.engagement_rate.ci_high | Table 2 | primary, Static, engagement rate, ci_high | 0.9452 | 0.945239 | +3.86e-05 | MATCH |
| T2.Adaptive.engagement_rate.mean | Table 2 | primary, Adaptive, engagement rate, mean (primary) | 0.9993 | 0.999268 | -3.16e-05 | MATCH |
| T2.Adaptive.engagement_rate.ci_low | Table 2 | primary, Adaptive, engagement rate, ci_low | 0.9988 | 0.998764 | -3.61e-05 | MATCH |
| T2.Adaptive.engagement_rate.ci_high | Table 2 | primary, Adaptive, engagement rate, ci_high | 0.9997 | 0.999693 | -7.38e-06 | MATCH |
| T2.Consensus.engagement_rate.mean | Table 2 | primary, Consensus, engagement rate, mean (primary) | 0.9999 | 0.999913 | +1.32e-05 | MATCH |
| T2.Consensus.engagement_rate.ci_low | Table 2 | primary, Consensus, engagement rate, ci_low | 0.9997 | 0.999740 | +3.96e-05 | MATCH |
| T2.Consensus.engagement_rate.ci_high | Table 2 | primary, Consensus, engagement rate, ci_high | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T2.CADO.engagement_rate.mean | Table 2 | primary, CADO, engagement rate, mean (primary) | 0.9999 | 0.999913 | +1.32e-05 | MATCH |
| T2.CADO.engagement_rate.ci_low | Table 2 | primary, CADO, engagement rate, ci_low | 0.9997 | 0.999740 | +3.96e-05 | MATCH |
| T2.CADO.engagement_rate.ci_high | Table 2 | primary, CADO, engagement rate, ci_high | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T2.Static.benign_false_redirect_rate.mean | Table 2 | primary, Static, benign false redirects, mean (primary) | 0.002897 | 0.00289695 | -4.59e-08 | MATCH |
| T2.Static.benign_false_redirect_rate.ci_low | Table 2 | primary, Static, benign false redirects, ci_low | 0.002347 | 0.00234658 | -4.21e-07 | MATCH |
| T2.Static.benign_false_redirect_rate.ci_high | Table 2 | primary, Static, benign false redirects, ci_high | 0.003480 | 0.00348033 | +3.26e-07 | MATCH |
| T2.Adaptive.benign_false_redirect_rate.mean | Table 2 | primary, Adaptive, benign false redirects, mean (primary) | 0.105962 | 0.10596246 | +4.56e-07 | MATCH |
| T2.Adaptive.benign_false_redirect_rate.ci_low | Table 2 | primary, Adaptive, benign false redirects, ci_low | 0.100999 | 0.10099857 | -4.28e-07 | MATCH |
| T2.Adaptive.benign_false_redirect_rate.ci_high | Table 2 | primary, Adaptive, benign false redirects, ci_high | 0.110944 | 0.11094362 | -3.78e-07 | MATCH |
| T2.Consensus.benign_false_redirect_rate.mean | Table 2 | primary, Consensus, benign false redirects, mean (primary) | 0.000082 | 0.00008172 | -2.83e-07 | MATCH |
| T2.Consensus.benign_false_redirect_rate.ci_low | Table 2 | primary, Consensus, benign false redirects, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T2.Consensus.benign_false_redirect_rate.ci_high | Table 2 | primary, Consensus, benign false redirects, ci_high | 0.000205 | 0.00020489 | -1.07e-07 | MATCH |
| T2.CADO.benign_false_redirect_rate.mean | Table 2 | primary, CADO, benign false redirects, mean (primary) | 0.000082 | 0.00008172 | -2.83e-07 | MATCH |
| T2.CADO.benign_false_redirect_rate.ci_low | Table 2 | primary, CADO, benign false redirects, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T2.CADO.benign_false_redirect_rate.ci_high | Table 2 | primary, CADO, benign false redirects, ci_high | 0.000205 | 0.00020489 | -1.07e-07 | MATCH |
| T2.Static.unsafe_action_rate.mean | Table 2 | primary, Static, unsafe actions, mean (primary) | 0.001944 | 0.00194444 | +4.44e-07 | MATCH |
| T2.Static.unsafe_action_rate.ci_low | Table 2 | primary, Static, unsafe actions, ci_low | 0.001574 | 0.00157407 | +7.41e-08 | MATCH |
| T2.Static.unsafe_action_rate.ci_high | Table 2 | primary, Static, unsafe actions, ci_high | 0.002315 | 0.00231539 | +3.94e-07 | MATCH |
| T2.Adaptive.unsafe_action_rate.mean | Table 2 | primary, Adaptive, unsafe actions, mean (primary) | 0.065000 | 0.06500000 | +0.00e+00 | MATCH |
| T2.Adaptive.unsafe_action_rate.ci_low | Table 2 | primary, Adaptive, unsafe actions, ci_low | 0.061991 | 0.06199074 | -2.59e-07 | MATCH |
| T2.Adaptive.unsafe_action_rate.ci_high | Table 2 | primary, Adaptive, unsafe actions, ci_high | 0.068009 | 0.06800926 | +2.59e-07 | MATCH |
| T2.Consensus.unsafe_action_rate.mean | Table 2 | primary, Consensus, unsafe actions, mean (primary) | 0.000046 | 0.00004630 | +2.96e-07 | MATCH |
| T2.Consensus.unsafe_action_rate.ci_low | Table 2 | primary, Consensus, unsafe actions, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T2.Consensus.unsafe_action_rate.ci_high | Table 2 | primary, Consensus, unsafe actions, ci_high | 0.000116 | 0.00011574 | -2.59e-07 | MATCH |
| T2.CADO.unsafe_action_rate.mean | Table 2 | primary, CADO, unsafe actions, mean (primary) | 0.000046 | 0.00004630 | +2.96e-07 | MATCH |
| T2.CADO.unsafe_action_rate.ci_low | Table 2 | primary, CADO, unsafe actions, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T2.CADO.unsafe_action_rate.ci_high | Table 2 | primary, CADO, unsafe actions, ci_high | 0.000116 | 0.00011574 | -2.59e-07 | MATCH |
| T2.Static.normalized_cost.mean | Table 2 | primary, Static, normalized cost, mean (primary) | 0.05788 | 0.0578816 | +1.56e-06 | MATCH |
| T2.Static.normalized_cost.ci_low | Table 2 | primary, Static, normalized cost, ci_low | 0.05707 | 0.0570656 | -4.36e-06 | MATCH |
| T2.Static.normalized_cost.ci_high | Table 2 | primary, Static, normalized cost, ci_high | 0.05872 | 0.0587228 | +2.83e-06 | MATCH |
| T2.Adaptive.normalized_cost.mean | Table 2 | primary, Adaptive, normalized cost, mean (primary) | 0.09618 | 0.0961758 | -4.21e-06 | MATCH |
| T2.Adaptive.normalized_cost.ci_low | Table 2 | primary, Adaptive, normalized cost, ci_low | 0.09548 | 0.0954815 | +1.53e-06 | MATCH |
| T2.Adaptive.normalized_cost.ci_high | Table 2 | primary, Adaptive, normalized cost, ci_high | 0.09688 | 0.0968816 | +1.64e-06 | MATCH |
| T2.Consensus.normalized_cost.mean | Table 2 | primary, Consensus, normalized cost, mean (primary) | 0.07573 | 0.0757263 | -3.67e-06 | MATCH |
| T2.Consensus.normalized_cost.ci_low | Table 2 | primary, Consensus, normalized cost, ci_low | 0.07491 | 0.0749082 | -1.81e-06 | MATCH |
| T2.Consensus.normalized_cost.ci_high | Table 2 | primary, Consensus, normalized cost, ci_high | 0.07655 | 0.0765542 | +4.22e-06 | MATCH |
| T2.CADO.normalized_cost.mean | Table 2 | primary, CADO, normalized cost, mean (primary) | 0.07538 | 0.0753812 | +1.22e-06 | MATCH |
| T2.CADO.normalized_cost.ci_low | Table 2 | primary, CADO, normalized cost, ci_low | 0.07447 | 0.0744670 | -3.03e-06 | MATCH |
| T2.CADO.normalized_cost.ci_high | Table 2 | primary, CADO, normalized cost, ci_high | 0.07629 | 0.0762928 | +2.81e-06 | MATCH |
| T3.primary.Consensus.utility | Table 3 | primary, Consensus, utility (primary) | 0.6953 | 0.695279 | -2.11e-05 | MATCH |
| T3.primary.Consensus.redirection_precision | Table 3 | primary, Consensus, redirection_precision (primary) | 0.6978 | 0.697814 | +1.36e-05 | MATCH |
| T3.primary.Consensus.benign_false_redirect_rate | Table 3 | primary, Consensus, benign_false_redirect_rate (primary) | 0.000082 | 0.00008172 | -2.83e-07 | MATCH |
| T3.primary.Consensus.unsafe_action_rate | Table 3 | primary, Consensus, unsafe_action_rate (primary) | 0.000046 | 0.00004630 | +2.96e-07 | MATCH |
| T3.primary.CADO.utility | Table 3 | primary, Full CADO, utility (primary) | 0.7020 | 0.702014 | +1.37e-05 | MATCH |
| T3.primary.CADO.redirection_precision | Table 3 | primary, Full CADO, redirection_precision (primary) | 0.7282 | 0.728191 | -9.05e-06 | MATCH |
| T3.primary.CADO.benign_false_redirect_rate | Table 3 | primary, Full CADO, benign_false_redirect_rate (primary) | 0.000082 | 0.00008172 | -2.83e-07 | MATCH |
| T3.primary.CADO.unsafe_action_rate | Table 3 | primary, Full CADO, unsafe_action_rate (primary) | 0.000046 | 0.00004630 | +2.96e-07 | MATCH |
| T3.primary.CADO.fallback_rate | Table 3 | primary, Full CADO, fallback_rate (primary) | 0.9633 | 0.963333 | +3.33e-05 | MATCH |
| T3.primary.CADO-NoEvidence.utility | Table 3 | primary, No evidence gate, utility (primary) | 0.7024 | 0.702429 | +2.87e-05 | MATCH |
| T3.primary.CADO-NoEvidence.redirection_precision | Table 3 | primary, No evidence gate, redirection_precision (primary) | 0.7289 | 0.728878 | -2.20e-05 | MATCH |
| T3.primary.CADO-NoEvidence.benign_false_redirect_rate | Table 3 | primary, No evidence gate, benign_false_redirect_rate (primary) | 0.000082 | 0.00008172 | -2.83e-07 | MATCH |
| T3.primary.CADO-NoEvidence.unsafe_action_rate | Table 3 | primary, No evidence gate, unsafe_action_rate (primary) | 0.000046 | 0.00004630 | +2.96e-07 | MATCH |
| T3.primary.CADO-NoEvidence.fallback_rate | Table 3 | primary, No evidence gate, fallback_rate (primary) | 0.9610 | 0.960995 | -4.63e-06 | MATCH |
| T3.primary.CADO-NoNoninferiority.utility | Table 3 | primary, No confidence/value gates, utility (primary) | 0.7163 | 0.716337 | +3.68e-05 | MATCH |
| T3.primary.CADO-NoNoninferiority.redirection_precision | Table 3 | primary, No confidence/value gates, redirection_precision (primary) | 0.7717 | 0.771655 | -4.53e-05 | MATCH |
| T3.primary.CADO-NoNoninferiority.benign_false_redirect_rate | Table 3 | primary, No confidence/value gates, benign_false_redirect_rate (primary) | 0.000377 | 0.00037670 | -3.00e-07 | MATCH |
| T3.primary.CADO-NoNoninferiority.unsafe_action_rate | Table 3 | primary, No confidence/value gates, unsafe_action_rate (primary) | 0.006042 | 0.00604167 | -3.33e-07 | MATCH |
| T3.primary.CADO-NoNoninferiority.fallback_rate | Table 3 | primary, No confidence/value gates, fallback_rate (primary) | 0.2050 | 0.204977 | -2.31e-05 | MATCH |
| T3.primary.CADO-BoundedOnly.utility | Table 3 | primary, Bounded residual only, utility (primary) | 0.7208 | 0.720797 | -2.66e-06 | MATCH |
| T3.primary.CADO-BoundedOnly.redirection_precision | Table 3 | primary, Bounded residual only, redirection_precision (primary) | 0.7895 | 0.789455 | -4.48e-05 | MATCH |
| T3.primary.CADO-BoundedOnly.benign_false_redirect_rate | Table 3 | primary, Bounded residual only, benign_false_redirect_rate (primary) | 0.000409 | 0.00040938 | +3.80e-07 | MATCH |
| T3.primary.CADO-BoundedOnly.unsafe_action_rate | Table 3 | primary, Bounded residual only, unsafe_action_rate (primary) | 0.007731 | 0.00773148 | +4.81e-07 | MATCH |
| T3.primary.CADO-BoundedOnly.fallback_rate | Table 3 | primary, Bounded residual only, fallback_rate (primary) | 0.0000 | 0.000000 | +0.00e+00 | MATCH |
| T3.ood.Consensus.utility | Table 3 | held-out, Consensus, utility (primary) | 0.6572 | 0.657196 | -3.99e-06 | MATCH |
| T3.ood.Consensus.redirection_precision | Table 3 | held-out, Consensus, redirection_precision (primary) | 0.5549 | 0.554868 | -3.16e-05 | MATCH |
| T3.ood.Consensus.benign_false_redirect_rate | Table 3 | held-out, Consensus, benign_false_redirect_rate (primary) | 0.000299 | 0.00029938 | +3.77e-07 | MATCH |
| T3.ood.Consensus.unsafe_action_rate | Table 3 | held-out, Consensus, unsafe_action_rate (primary) | 0.000185 | 0.00018519 | +1.85e-07 | MATCH |
| T3.ood.CADO.utility | Table 3 | held-out, Full CADO, utility (primary) | 0.6590 | 0.658988 | -1.23e-05 | MATCH |
| T3.ood.CADO.redirection_precision | Table 3 | held-out, Full CADO, redirection_precision (primary) | 0.5745 | 0.574508 | +8.17e-06 | MATCH |
| T3.ood.CADO.benign_false_redirect_rate | Table 3 | held-out, Full CADO, benign_false_redirect_rate (primary) | 0.000299 | 0.00029938 | +3.77e-07 | MATCH |
| T3.ood.CADO.unsafe_action_rate | Table 3 | held-out, Full CADO, unsafe_action_rate (primary) | 0.000185 | 0.00018519 | +1.85e-07 | MATCH |
| T3.ood.CADO.fallback_rate | Table 3 | held-out, Full CADO, fallback_rate (primary) | 0.9868 | 0.986759 | -4.07e-05 | MATCH |
| T3.ood.CADO-NoOOD.utility | Table 3 | held-out, No OOD gate, utility (primary) | 0.6611 | 0.661128 | +2.84e-05 | MATCH |
| T3.ood.CADO-NoOOD.redirection_precision | Table 3 | held-out, No OOD gate, redirection_precision (primary) | 0.5970 | 0.597008 | +8.44e-06 | MATCH |
| T3.ood.CADO-NoOOD.benign_false_redirect_rate | Table 3 | held-out, No OOD gate, benign_false_redirect_rate (primary) | 0.000299 | 0.00029938 | +3.77e-07 | MATCH |
| T3.ood.CADO-NoOOD.unsafe_action_rate | Table 3 | held-out, No OOD gate, unsafe_action_rate (primary) | 0.000185 | 0.00018519 | +1.85e-07 | MATCH |
| T3.ood.CADO-NoOOD.fallback_rate | Table 3 | held-out, No OOD gate, fallback_rate (primary) | 0.9746 | 0.974630 | +2.96e-05 | MATCH |
| T3.ood.CADO-BoundedOnly.utility | Table 3 | held-out, Bounded residual only, utility (primary) | 0.6966 | 0.696636 | +3.60e-05 | MATCH |
| T3.ood.CADO-BoundedOnly.redirection_precision | Table 3 | held-out, Bounded residual only, redirection_precision (primary) | 0.8117 | 0.811703 | +3.41e-06 | MATCH |
| T3.ood.CADO-BoundedOnly.benign_false_redirect_rate | Table 3 | held-out, Bounded residual only, benign_false_redirect_rate (primary) | 0.000579 | 0.00057944 | +4.45e-07 | MATCH |
| T3.ood.CADO-BoundedOnly.unsafe_action_rate | Table 3 | held-out, Bounded residual only, unsafe_action_rate (primary) | 0.040093 | 0.04009259 | -4.07e-07 | MATCH |
| T3.ood.CADO-BoundedOnly.fallback_rate | Table 3 | held-out, Bounded residual only, fallback_rate (primary) | 0.0000 | 0.000000 | +0.00e+00 | MATCH |
| T4.Consensus.utility.mean | Table 4 | held-out, Consensus, defensive utility, mean (primary) | 0.6572 | 0.657196 | -3.99e-06 | MATCH |
| T4.Consensus.utility.ci_low | Table 4 | held-out, Consensus, defensive utility, ci_low | 0.6523 | 0.652265 | -3.51e-05 | MATCH |
| T4.Consensus.utility.ci_high | Table 4 | held-out, Consensus, defensive utility, ci_high | 0.6620 | 0.662040 | +4.05e-05 | MATCH |
| T4.CADO.utility.mean | Table 4 | held-out, CADO, defensive utility, mean (primary) | 0.6590 | 0.658988 | -1.23e-05 | MATCH |
| T4.CADO.utility.ci_low | Table 4 | held-out, CADO, defensive utility, ci_low | 0.6542 | 0.654152 | -4.83e-05 | MATCH |
| T4.CADO.utility.ci_high | Table 4 | held-out, CADO, defensive utility, ci_high | 0.6639 | 0.663894 | -5.80e-06 | MATCH |
| T4.diff.utility.mean_difference | Table 4 | held-out, CADO minus Consensus, defensive utility, mean_difference (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T4.diff.utility.ci_low | Table 4 | held-out, CADO minus Consensus, defensive utility, ci_low | 0.001137 | 0.00113699 | -5.60e-09 | MATCH |
| T4.diff.utility.ci_high | Table 4 | held-out, CADO minus Consensus, defensive utility, ci_high | 0.002500 | 0.00250035 | +3.50e-07 | MATCH |
| T4.diff.utility.p_holm | Table 4 | held-out, CADO minus Consensus, defensive utility, Holm p (primary) | 0.000505 | 0.00050505 | +5.13e-08 | MATCH |
| T4.diff.utility.effect_size_dz | Table 4 | held-out, CADO minus Consensus, defensive utility, d_z | 0.932 | 0.93161 | -3.94e-04 | MATCH |
| T4.Consensus.redirection_precision.mean | Table 4 | held-out, Consensus, redirection precision, mean (primary) | 0.5549 | 0.554868 | -3.16e-05 | MATCH |
| T4.Consensus.redirection_precision.ci_low | Table 4 | held-out, Consensus, redirection precision, ci_low | 0.5401 | 0.540127 | +2.68e-05 | MATCH |
| T4.Consensus.redirection_precision.ci_high | Table 4 | held-out, Consensus, redirection precision, ci_high | 0.5688 | 0.568839 | +3.89e-05 | MATCH |
| T4.CADO.redirection_precision.mean | Table 4 | held-out, CADO, redirection precision, mean (primary) | 0.5745 | 0.574508 | +8.17e-06 | MATCH |
| T4.CADO.redirection_precision.ci_low | Table 4 | held-out, CADO, redirection precision, ci_low | 0.5588 | 0.558774 | -2.59e-05 | MATCH |
| T4.CADO.redirection_precision.ci_high | Table 4 | held-out, CADO, redirection precision, ci_high | 0.5900 | 0.589988 | -1.19e-05 | MATCH |
| T4.diff.redirection_precision.mean_difference | Table 4 | held-out, CADO minus Consensus, redirection precision, mean_difference (primary) | 0.019640 | 0.01963981 | -1.92e-07 | MATCH |
| T4.diff.redirection_precision.ci_low | Table 4 | held-out, CADO minus Consensus, redirection precision, ci_low | 0.012773 | 0.01277297 | -3.20e-08 | MATCH |
| T4.diff.redirection_precision.ci_high | Table 4 | held-out, CADO minus Consensus, redirection precision, ci_high | 0.026782 | 0.02678227 | +2.68e-07 | MATCH |
| T4.diff.redirection_precision.p_holm | Table 4 | held-out, CADO minus Consensus, redirection precision, Holm p (primary) | 0.001571 | 0.00157149 | +4.94e-07 | MATCH |
| T4.diff.redirection_precision.effect_size_dz | Table 4 | held-out, CADO minus Consensus, redirection precision, d_z | 0.973 | 0.97336 | +3.63e-04 | MATCH |
| T4.Consensus.engagement_rate.mean | Table 4 | held-out, Consensus, engagement rate, mean (primary) | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T4.Consensus.engagement_rate.ci_low | Table 4 | held-out, Consensus, engagement rate, ci_low | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T4.Consensus.engagement_rate.ci_high | Table 4 | held-out, Consensus, engagement rate, ci_high | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T4.CADO.engagement_rate.mean | Table 4 | held-out, CADO, engagement rate, mean (primary) | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T4.CADO.engagement_rate.ci_low | Table 4 | held-out, CADO, engagement rate, ci_low | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T4.CADO.engagement_rate.ci_high | Table 4 | held-out, CADO, engagement rate, ci_high | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| T4.diff.engagement_rate.mean_difference | Table 4 | held-out, CADO minus Consensus, engagement rate, mean_difference (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.engagement_rate.ci_low | Table 4 | held-out, CADO minus Consensus, engagement rate, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.engagement_rate.ci_high | Table 4 | held-out, CADO minus Consensus, engagement rate, ci_high | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.engagement_rate.p_holm | Table 4 | held-out, CADO minus Consensus, engagement rate, Holm p (primary) | 1.000 | 1.00000 | +0.00e+00 | MATCH |
| T4.diff.engagement_rate.effect_size_dz | Table 4 | held-out, CADO minus Consensus, engagement rate, d_z | 0.000 | 0.00000 | +0.00e+00 | MATCH |
| T4.Consensus.benign_false_redirect_rate.mean | Table 4 | held-out, Consensus, benign false redirects, mean (primary) | 0.000299 | 0.00029938 | +3.77e-07 | MATCH |
| T4.Consensus.benign_false_redirect_rate.ci_low | Table 4 | held-out, Consensus, benign false redirects, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.Consensus.benign_false_redirect_rate.ci_high | Table 4 | held-out, Consensus, benign false redirects, ci_high | 0.000757 | 0.00075748 | +4.84e-07 | MATCH |
| T4.CADO.benign_false_redirect_rate.mean | Table 4 | held-out, CADO, benign false redirects, mean (primary) | 0.000299 | 0.00029938 | +3.77e-07 | MATCH |
| T4.CADO.benign_false_redirect_rate.ci_low | Table 4 | held-out, CADO, benign false redirects, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.CADO.benign_false_redirect_rate.ci_high | Table 4 | held-out, CADO, benign false redirects, ci_high | 0.000757 | 0.00075748 | +4.84e-07 | MATCH |
| T4.diff.benign_false_redirect_rate.mean_difference | Table 4 | held-out, CADO minus Consensus, benign false redirects, mean_difference (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.benign_false_redirect_rate.ci_low | Table 4 | held-out, CADO minus Consensus, benign false redirects, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.benign_false_redirect_rate.ci_high | Table 4 | held-out, CADO minus Consensus, benign false redirects, ci_high | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.benign_false_redirect_rate.p_holm | Table 4 | held-out, CADO minus Consensus, benign false redirects, Holm p (primary) | 1.000 | 1.00000 | +0.00e+00 | MATCH |
| T4.diff.benign_false_redirect_rate.effect_size_dz | Table 4 | held-out, CADO minus Consensus, benign false redirects, d_z | 0.000 | 0.00000 | +0.00e+00 | MATCH |
| T4.Consensus.unsafe_action_rate.mean | Table 4 | held-out, Consensus, unsafe actions, mean (primary) | 0.000185 | 0.00018519 | +1.85e-07 | MATCH |
| T4.Consensus.unsafe_action_rate.ci_low | Table 4 | held-out, Consensus, unsafe actions, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.Consensus.unsafe_action_rate.ci_high | Table 4 | held-out, Consensus, unsafe actions, ci_high | 0.000463 | 0.00046296 | -3.70e-08 | MATCH |
| T4.CADO.unsafe_action_rate.mean | Table 4 | held-out, CADO, unsafe actions, mean (primary) | 0.000185 | 0.00018519 | +1.85e-07 | MATCH |
| T4.CADO.unsafe_action_rate.ci_low | Table 4 | held-out, CADO, unsafe actions, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.CADO.unsafe_action_rate.ci_high | Table 4 | held-out, CADO, unsafe actions, ci_high | 0.000463 | 0.00046296 | -3.70e-08 | MATCH |
| T4.diff.unsafe_action_rate.mean_difference | Table 4 | held-out, CADO minus Consensus, unsafe actions, mean_difference (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.unsafe_action_rate.ci_low | Table 4 | held-out, CADO minus Consensus, unsafe actions, ci_low | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.unsafe_action_rate.ci_high | Table 4 | held-out, CADO minus Consensus, unsafe actions, ci_high | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T4.diff.unsafe_action_rate.p_holm | Table 4 | held-out, CADO minus Consensus, unsafe actions, Holm p (primary) | 1.000 | 1.00000 | +0.00e+00 | MATCH |
| T4.diff.unsafe_action_rate.effect_size_dz | Table 4 | held-out, CADO minus Consensus, unsafe actions, d_z | 0.000 | 0.00000 | +0.00e+00 | MATCH |
| T4.Consensus.normalized_cost.mean | Table 4 | held-out, Consensus, normalized cost, mean (primary) | 0.07108 | 0.0710827 | +2.69e-06 | MATCH |
| T4.Consensus.normalized_cost.ci_low | Table 4 | held-out, Consensus, normalized cost, ci_low | 0.06967 | 0.0696734 | +3.38e-06 | MATCH |
| T4.Consensus.normalized_cost.ci_high | Table 4 | held-out, Consensus, normalized cost, ci_high | 0.07253 | 0.0725274 | -2.57e-06 | MATCH |
| T4.CADO.normalized_cost.mean | Table 4 | held-out, CADO, normalized cost, mean (primary) | 0.07288 | 0.0728827 | +2.66e-06 | MATCH |
| T4.CADO.normalized_cost.ci_low | Table 4 | held-out, CADO, normalized cost, ci_low | 0.07122 | 0.0712203 | +2.65e-07 | MATCH |
| T4.CADO.normalized_cost.ci_high | Table 4 | held-out, CADO, normalized cost, ci_high | 0.07447 | 0.0744698 | -2.18e-07 | MATCH |
| T4.diff.normalized_cost.mean_difference | Table 4 | held-out, CADO minus Consensus, normalized cost, mean_difference (primary) | 0.001800 | 0.00179997 | -3.00e-08 | MATCH |
| T4.diff.normalized_cost.ci_low | Table 4 | held-out, CADO minus Consensus, normalized cost, ci_low | 0.001293 | 0.00129284 | -1.64e-07 | MATCH |
| T4.diff.normalized_cost.ci_high | Table 4 | held-out, CADO minus Consensus, normalized cost, ci_high | 0.002321 | 0.00232074 | -2.62e-07 | MATCH |
| T4.diff.normalized_cost.p_holm | Table 4 | held-out, CADO minus Consensus, normalized cost, Holm p (primary) | 0.000182 | 0.00018197 | -2.61e-08 | MATCH |
| T4.diff.normalized_cost.effect_size_dz | Table 4 | held-out, CADO minus Consensus, normalized cost, d_z | 1.236 | 1.23649 | +4.85e-04 | MATCH |
| T5.default.settings.n | Table 5 | default: number of settings | 1 | 1.00 | +0.00e+00 | MATCH |
| T5.default.primary_utility.min | Table 5 | default: CADO-minus-Consensus primary_utility across settings, min (printed as one value) (primary) | 0.006735 | 0.00673481 | -1.90e-07 | MATCH |
| T5.default.primary_utility.max | Table 5 | default: CADO-minus-Consensus primary_utility across settings, max (printed as one value) (primary) | 0.006735 | 0.00673481 | -1.90e-07 | MATCH |
| T5.default.ood_utility.min | Table 5 | default: CADO-minus-Consensus ood_utility across settings, min (printed as one value) (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T5.default.ood_utility.max | Table 5 | default: CADO-minus-Consensus ood_utility across settings, max (printed as one value) (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T5.default.primary_unsafe.min | Table 5 | default: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.default.primary_unsafe.max | Table 5 | default: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.risk_weights.settings.n | Table 5 | risk weights: number of settings | 3 | 3.00 | +0.00e+00 | MATCH |
| T5.risk_weights.primary_utility.min | Table 5 | risk weights: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.007468 | 0.00746765 | -3.45e-07 | MATCH |
| T5.risk_weights.primary_utility.max | Table 5 | risk weights: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.009931 | 0.00993148 | +4.80e-07 | MATCH |
| T5.risk_weights.ood_utility.min | Table 5 | risk weights: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.001042 | 0.00104151 | -4.87e-07 | MATCH |
| T5.risk_weights.ood_utility.max | Table 5 | risk weights: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.001841 | 0.00184079 | -2.11e-07 | MATCH |
| T5.risk_weights.primary_unsafe.min | Table 5 | risk weights: CADO-minus-Consensus primary_unsafe across settings, min (primary) | -0.000208 | -0.00020833 | -3.33e-07 | MATCH |
| T5.risk_weights.primary_unsafe.max | Table 5 | risk weights: CADO-minus-Consensus primary_unsafe across settings, max (primary) | -0.000023 | -0.00002315 | -1.48e-07 | MATCH |
| T5.action_thresholds.settings.n | Table 5 | action thresholds: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.action_thresholds.primary_utility.min | Table 5 | action thresholds: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.006415 | 0.00641497 | -3.29e-08 | MATCH |
| T5.action_thresholds.primary_utility.max | Table 5 | action thresholds: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.011622 | 0.01162180 | -2.01e-07 | MATCH |
| T5.action_thresholds.ood_utility.min | Table 5 | action thresholds: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.001170 | 0.00116997 | -3.45e-08 | MATCH |
| T5.action_thresholds.ood_utility.max | Table 5 | action thresholds: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.002134 | 0.00213426 | +2.63e-07 | MATCH |
| T5.action_thresholds.primary_unsafe.min | Table 5 | action thresholds: CADO-minus-Consensus primary_unsafe across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.action_thresholds.primary_unsafe.max | Table 5 | action thresholds: CADO-minus-Consensus primary_unsafe across settings, max (primary) | 0.000023 | 0.00002315 | +1.48e-07 | MATCH |
| T5.evidence_gate.settings.n | Table 5 | evidence gate: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.evidence_gate.primary_utility.min | Table 5 | evidence gate: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.005962 | 0.00596195 | -4.85e-08 | MATCH |
| T5.evidence_gate.primary_utility.max | Table 5 | evidence gate: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.007050 | 0.00704997 | -3.17e-08 | MATCH |
| T5.evidence_gate.ood_utility.min | Table 5 | evidence gate: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.001622 | 0.00162225 | +2.52e-07 | MATCH |
| T5.evidence_gate.ood_utility.max | Table 5 | evidence gate: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T5.evidence_gate.primary_unsafe.min | Table 5 | evidence gate: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.evidence_gate.primary_unsafe.max | Table 5 | evidence gate: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.OOD_gate.settings.n | Table 5 | OOD gate: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.OOD_gate.primary_utility.min | Table 5 | OOD gate: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.004378 | 0.00437844 | +4.42e-07 | MATCH |
| T5.OOD_gate.primary_utility.max | Table 5 | OOD gate: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.006978 | 0.00697754 | -4.63e-07 | MATCH |
| T5.OOD_gate.ood_utility.min | Table 5 | OOD gate: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.OOD_gate.ood_utility.max | Table 5 | OOD gate: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.003932 | 0.00393237 | +3.74e-07 | MATCH |
| T5.OOD_gate.primary_unsafe.min | Table 5 | OOD gate: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.OOD_gate.primary_unsafe.max | Table 5 | OOD gate: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.confidence_gate.settings.n | Table 5 | confidence gate: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.confidence_gate.primary_utility.min | Table 5 | confidence gate: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.006043 | 0.00604325 | +2.46e-07 | MATCH |
| T5.confidence_gate.primary_utility.max | Table 5 | confidence gate: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.007092 | 0.00709222 | +2.22e-07 | MATCH |
| T5.confidence_gate.ood_utility.min | Table 5 | confidence gate: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.001413 | 0.00141287 | -1.31e-07 | MATCH |
| T5.confidence_gate.ood_utility.max | Table 5 | confidence gate: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.002441 | 0.00244121 | +2.09e-07 | MATCH |
| T5.confidence_gate.primary_unsafe.min | Table 5 | confidence gate: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.confidence_gate.primary_unsafe.max | Table 5 | confidence gate: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.uncertainty_margin.settings.n | Table 5 | uncertainty margin: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.uncertainty_margin.primary_utility.min | Table 5 | uncertainty margin: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.004713 | 0.00471264 | -3.62e-07 | MATCH |
| T5.uncertainty_margin.primary_utility.max | Table 5 | uncertainty margin: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.009343 | 0.00934314 | +1.42e-07 | MATCH |
| T5.uncertainty_margin.ood_utility.min | Table 5 | uncertainty margin: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.uncertainty_margin.ood_utility.max | Table 5 | uncertainty margin: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.003078 | 0.00307825 | +2.50e-07 | MATCH |
| T5.uncertainty_margin.primary_unsafe.min | Table 5 | uncertainty margin: CADO-minus-Consensus primary_unsafe across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.uncertainty_margin.primary_unsafe.max | Table 5 | uncertainty margin: CADO-minus-Consensus primary_unsafe across settings, max (primary) | 0.000023 | 0.00002315 | +1.48e-07 | MATCH |
| T5.residual_bound.settings.n | Table 5 | residual bound: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.residual_bound.primary_utility.min | Table 5 | residual bound: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.residual_bound.primary_utility.max | Table 5 | residual bound: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.006735 | 0.00673481 | -1.90e-07 | MATCH |
| T5.residual_bound.ood_utility.min | Table 5 | residual bound: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.residual_bound.ood_utility.max | Table 5 | residual bound: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T5.residual_bound.primary_unsafe.min | Table 5 | residual bound: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.residual_bound.primary_unsafe.max | Table 5 | residual bound: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.outcome_capture.settings.n | Table 5 | outcome capture: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.outcome_capture.primary_utility.min | Table 5 | outcome capture: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.006221 | 0.00622138 | +3.84e-07 | MATCH |
| T5.outcome_capture.primary_utility.max | Table 5 | outcome capture: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.006835 | 0.00683481 | -1.90e-07 | MATCH |
| T5.outcome_capture.ood_utility.min | Table 5 | outcome capture: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.001651 | 0.00165096 | -4.41e-08 | MATCH |
| T5.outcome_capture.ood_utility.max | Table 5 | outcome capture: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.001758 | 0.00175836 | +3.63e-07 | MATCH |
| T5.outcome_capture.primary_unsafe.min | Table 5 | outcome capture: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.outcome_capture.primary_unsafe.max | Table 5 | outcome capture: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.outcome_resource_cost.settings.n | Table 5 | outcome resource cost: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.outcome_resource_cost.primary_utility.min | Table 5 | outcome resource cost: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.006562 | 0.00656225 | +2.55e-07 | MATCH |
| T5.outcome_resource_cost.primary_utility.max | Table 5 | outcome resource cost: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.006761 | 0.00676112 | +1.20e-07 | MATCH |
| T5.outcome_resource_cost.ood_utility.min | Table 5 | outcome resource cost: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.000892 | 0.00089171 | -2.88e-07 | MATCH |
| T5.outcome_resource_cost.ood_utility.max | Table 5 | outcome resource cost: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.002692 | 0.00269168 | -3.18e-07 | MATCH |
| T5.outcome_resource_cost.primary_unsafe.min | Table 5 | outcome resource cost: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.outcome_resource_cost.primary_unsafe.max | Table 5 | outcome resource cost: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.outcome_benign_harm.settings.n | Table 5 | outcome benign harm: number of settings | 2 | 2.00 | +0.00e+00 | MATCH |
| T5.outcome_benign_harm.primary_utility.min | Table 5 | outcome benign harm: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.006735 | 0.00673481 | -1.90e-07 | MATCH |
| T5.outcome_benign_harm.primary_utility.max | Table 5 | outcome benign harm: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.006735 | 0.00673481 | -1.90e-07 | MATCH |
| T5.outcome_benign_harm.ood_utility.min | Table 5 | outcome benign harm: CADO-minus-Consensus ood_utility across settings, min (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T5.outcome_benign_harm.ood_utility.max | Table 5 | outcome benign harm: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.001792 | 0.00179170 | -3.03e-07 | MATCH |
| T5.outcome_benign_harm.primary_unsafe.min | Table 5 | outcome benign harm: CADO-minus-Consensus primary_unsafe across settings, min (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.outcome_benign_harm.primary_unsafe.max | Table 5 | outcome benign harm: CADO-minus-Consensus primary_unsafe across settings, max (printed as one value) (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.joint_threshold_and_margin.settings.n | Table 5 | joint threshold and margin: number of settings | 4 | 4.00 | +0.00e+00 | MATCH |
| T5.joint_threshold_and_margin.primary_utility.min | Table 5 | joint threshold and margin: CADO-minus-Consensus primary_utility across settings, min (primary) | 0.002012 | 0.00201204 | +3.63e-08 | MATCH |
| T5.joint_threshold_and_margin.primary_utility.max | Table 5 | joint threshold and margin: CADO-minus-Consensus primary_utility across settings, max (primary) | 0.018683 | 0.01868335 | +3.52e-07 | MATCH |
| T5.joint_threshold_and_margin.ood_utility.min | Table 5 | joint threshold and margin: CADO-minus-Consensus ood_utility across settings, min (primary) | -0.000032 | -0.00003179 | +2.07e-07 | MATCH |
| T5.joint_threshold_and_margin.ood_utility.max | Table 5 | joint threshold and margin: CADO-minus-Consensus ood_utility across settings, max (primary) | 0.004233 | 0.00423269 | -3.05e-07 | MATCH |
| T5.joint_threshold_and_margin.primary_unsafe.min | Table 5 | joint threshold and margin: CADO-minus-Consensus primary_unsafe across settings, min (primary) | 0.000000 | 0.00000000 | +0.00e+00 | MATCH |
| T5.joint_threshold_and_margin.primary_unsafe.max | Table 5 | joint threshold and margin: CADO-minus-Consensus primary_unsafe across settings, max (primary) | 0.000046 | 0.00004630 | +2.96e-07 | MATCH |
| T6.verified_expiry.passed | Table 6 | prototype, verified_expiry: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.verified_expiry.restored | Table 6 | prototype, verified_expiry: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.duplicate_apply.passed | Table 6 | prototype, duplicate_apply: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.duplicate_apply.restored | Table 6 | prototype, duplicate_apply: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.ack_lost.passed | Table 6 | prototype, ack_lost: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.ack_lost.restored | Table 6 | prototype, ack_lost: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.state_divergence.passed | Table 6 | prototype, state_divergence: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.state_divergence.restored | Table 6 | prototype, state_divergence: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.telemetry_unavailable.passed | Table 6 | prototype, telemetry_unavailable: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.telemetry_unavailable.restored | Table 6 | prototype, telemetry_unavailable: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.stale_ttl.passed | Table 6 | prototype, stale_ttl: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.stale_ttl.restored | Table 6 | prototype, stale_ttl: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.rollback_transient.passed | Table 6 | prototype, rollback_transient: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.rollback_transient.restored | Table 6 | prototype, rollback_transient: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.rollback_persistent.passed | Table 6 | prototype, rollback_persistent: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.rollback_persistent.restored | Table 6 | prototype, rollback_persistent: path restored (of 30) (primary) | 0 | 0.00 | +0.00e+00 | MATCH |
| T6.unauthorized_scope.passed | Table 6 | prototype, unauthorized_scope: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.idempotency_conflict.passed | Table 6 | prototype, idempotency_conflict: trials meeting the expected outcome (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| T6.idempotency_conflict.restored | Table 6 | prototype, idempotency_conflict: path restored (of 30) (primary) | 30 | 30.00 | +0.00e+00 | MATCH |
| S51.utility.mean_difference | Section 5.1 | primary, CADO minus Consensus, defensive utility, mean_difference (primary) | 0.006735 | 0.00673481 | -1.90e-07 | MATCH |
| S51.utility.ci_low | Section 5.1 | primary, CADO minus Consensus, defensive utility, ci_low | 0.006284 | 0.00628353 | -4.68e-07 | MATCH |
| S51.utility.ci_high | Section 5.1 | primary, CADO minus Consensus, defensive utility, ci_high | 0.007222 | 0.00722204 | +4.00e-08 | MATCH |
| S51.utility.p_holm | Section 5.1 | primary, CADO minus Consensus, defensive utility, p_holm (primary) | 3.35e-8 | 3.353e-08 | +2.76e-11 | MATCH |
| S51.redirection_precision.mean_difference | Section 5.1 | primary, CADO minus Consensus, redirection precision, mean_difference (primary) | 0.03038 | 0.0303774 | -2.63e-06 | MATCH |
| S51.redirection_precision.ci_low | Section 5.1 | primary, CADO minus Consensus, redirection precision, ci_low | 0.02663 | 0.0266318 | +1.78e-06 | MATCH |
| S51.redirection_precision.ci_high | Section 5.1 | primary, CADO minus Consensus, redirection precision, ci_high | 0.03440 | 0.0344010 | +1.05e-06 | MATCH |
| S51.redirection_precision.p_holm | Section 5.1 | primary, CADO minus Consensus, redirection precision, p_holm (primary) | 3.35e-8 | 3.353e-08 | +2.76e-11 | MATCH |
| S51.normalized_cost.mean_difference | Section 5.1 | primary, CADO minus Consensus, normalized cost, mean_difference (primary) | -0.000345 | -0.00034511 | -1.11e-07 | MATCH |
| S51.normalized_cost.ci_low | Section 5.1 | primary, CADO minus Consensus, normalized cost, ci_low | -0.000647 | -0.00064679 | +2.08e-07 | MATCH |
| S51.normalized_cost.ci_high | Section 5.1 | primary, CADO minus Consensus, normalized cost, ci_high | -0.000047 | -0.00004739 | -3.94e-07 | MATCH |
| S51.normalized_cost.p_holm | Section 5.1 | primary, CADO minus Consensus, normalized cost, p_holm (primary) | 0.249 | 0.24855 | -4.49e-04 | MATCH |
| S52.gate.gate_insufficient | Section 5.2 | primary, CADO decisions routed: gate_insufficient (printed as a percentage) (primary) | 0.1398 | 0.139769 | -3.15e-05 | MATCH |
| S52.gate.gate_ood | Section 5.2 | primary, CADO decisions routed: gate_ood (printed as a percentage) (primary) | 0.0652 | 0.065208 | +8.33e-06 | MATCH |
| S52.gate.gate_noninferiority | Section 5.2 | primary, CADO decisions routed: gate_noninferiority (printed as a percentage) (primary) | 0.7584 | 0.758356 | -4.35e-05 | MATCH |
| S52.gate.personalized_rate | Section 5.2 | primary, CADO decisions routed: personalized_rate (printed as a percentage) (primary) | 0.0367 | 0.036667 | -3.33e-05 | MATCH |
| S52.ood_fallback.mean | Section 5.2 | held-out, CADO consensus fallback, mean (printed as a percentage) (primary) | 0.9868 | 0.986759 | -4.07e-05 | MATCH |
| S52.ood_fallback.ci_low | Section 5.2 | held-out, CADO consensus fallback, ci_low (printed as a percentage) | 0.9831 | 0.983056 | -4.44e-05 | MATCH |
| S52.ood_fallback.ci_high | Section 5.2 | held-out, CADO consensus fallback, ci_high (printed as a percentage) | 0.9904 | 0.990370 | -2.96e-05 | MATCH |
| S52.ood_unsafe.Adaptive | Section 5.2 | held-out, Adaptive unsafe-action rate (primary) | 0.4079 | 0.407870 | -2.96e-05 | MATCH |
| S54.ood_fallback.min | Section 5.4 | held-out CADO fallback across the 26 settings, min (printed as a percentage) (primary) | 0.9669 | 0.966852 | -4.81e-05 | MATCH |
| S54.ood_fallback.max | Section 5.4 | held-out CADO fallback across the 26 settings, max (printed as a percentage) (primary) | 1.0000 | 1.000000 | +0.00e+00 | MATCH |
| S55.rollback.Static | Section 5.5 | fault simulation, modeled rollback-success rate, Static configuration (primary) | 0.2158 | 0.215833 | +3.33e-05 | MATCH |
| S55.rollback.Adaptive | Section 5.5 | fault simulation, modeled rollback-success rate, Adaptive configuration (primary) | 0.4467 | 0.446667 | -3.33e-05 | MATCH |
| S55.rollback.Consensus | Section 5.5 | fault simulation, modeled rollback-success rate, Consensus configuration (primary) | 0.7242 | 0.724167 | -3.33e-05 | MATCH |
| S55.rollback.CADO | Section 5.5 | fault simulation, modeled rollback-success rate, CADO configuration (primary) | 0.9804 | 0.980417 | +1.67e-05 | MATCH |
| S55.persistence.CADO | Section 5.5 | fault simulation, mean persistence (steps), CADO configuration (primary) | 1.22 | 1.2154 | -4.58e-03 | MATCH |
| S55.persistence.Consensus | Section 5.5 | fault simulation, mean persistence (steps), Consensus configuration (primary) | 4.03 | 4.0342 | +4.17e-03 | MATCH |
| S55.prototype.trials | Section 5.5 | prototype: trials | 300 | 300.00 | +0.00e+00 | MATCH |
| S55.prototype.passed_criteria | Section 5.5 | prototype: passed_criteria (primary) | 300 | 300.00 | +0.00e+00 | MATCH |
| S55.prototype.installed_routes | Section 5.5 | prototype: installed_routes | 270 | 270.00 | +0.00e+00 | MATCH |
| S55.prototype.restored_installed_routes | Section 5.5 | prototype: restored_installed_routes (primary) | 240 | 240.00 | +0.00e+00 | MATCH |
| S55.prototype.persistent_rollback_failures | Section 5.5 | prototype: persistent_rollback_failures | 30 | 30.00 | +0.00e+00 | MATCH |
| S55.prototype.requests | Section 5.5 | prototype: requests | 4170 | 4170.00 | +0.00e+00 | MATCH |
| S55.prototype.journal_entries | Section 5.5 | prototype: journal_entries | 1770 | 1770.00 | +0.00e+00 | MATCH |
| S56.records.total | Section 5.6 | format replay: records parsed (4 x 5000) | 20000 | 20000.00 | +0.00e+00 | MATCH |
| S56.recovery.syslog | Section 5.6 | format replay, syslog: fraction of records with all six fields exact ('all') (primary) | 1 | 1.00 | +0.00e+00 | MATCH |
| S56.recovery.cef | Section 5.6 | format replay, cef: fraction of records with all six fields exact ('all') (primary) | 1 | 1.00 | +0.00e+00 | MATCH |
| S56.recovery.json | Section 5.6 | format replay, json: fraction of records with all six fields exact ('all') (primary) | 1 | 1.00 | +0.00e+00 | MATCH |
| S56.recovery.kv | Section 5.6 | format replay, kv: fraction of records with all six fields exact ('all') (primary) | 1 | 1.00 | +0.00e+00 | MATCH |
| TIME.throughput_min_records_s | Section 5.6 | host timing: throughput_min_records_s | 263000 | - | - | NOT ATTEMPTED |
| TIME.throughput_max_records_s | Section 5.6 | host timing: throughput_max_records_s | 327000 | - | - | NOT ATTEMPTED |
| TIME.parse_p95_latency_max_us | Section 5.6 | host timing: parse_p95_latency_max_us | 7.31 | - | - | NOT ATTEMPTED |
| TIME.policy_p95_latency_Static_us | Section 5.6 | host timing: policy_p95_latency_Static_us | 0.60 | - | - | NOT ATTEMPTED |
| TIME.policy_p95_latency_Consensus_us | Section 5.6 | host timing: policy_p95_latency_Consensus_us | 0.70 | - | - | NOT ATTEMPTED |
| TIME.policy_p95_latency_Adaptive_us | Section 5.6 | host timing: policy_p95_latency_Adaptive_us | 42.56 | - | - | NOT ATTEMPTED |
| TIME.policy_p95_latency_CADO_us | Section 5.6 | host timing: policy_p95_latency_CADO_us | 104.44 | - | - | NOT ATTEMPTED |
| S44.validation.episode_rows | Section 4.4 | CADO/Consensus episode rows checked by the vectorized evaluator | 900 | 900.00 | +0.00e+00 | MATCH |
| S44.validation.scalar_decisions | Section 4.4 | scalar policy decisions checked | 4200 | 4200.00 | +0.00e+00 | MATCH |

## Printed claims that the targets missed (added 2026-11-25, after the results; not targets)

A second reading of the paper against `TARGETS.csv`, after the results, found printed claims that the targets did not cover (DECISIONS 19). They cannot become targets after the results (STANDARD requirement 1), so they are checked here on our outputs and reported separately. Figures are not compared: they plot the tabled values, except Figure 4 (host timings).

| check | where | claim | holds on our outputs | detail |
|---|---|---|---|---|
| A1 | Section 3.6 | worked example: R' = 0.786433, consensus level 2, residual rejected by the value-margin check, action stays 2 | yes | risk 0.786433, consensus 2, selected 2, path noninferiority |
| A2 | Table 5 note | held-out unsafe-rate difference is zero in every one of the 26 configurations | yes | 26 settings, max |difference| 0 |
| A3 | Section 5.4 | thresholds +0.05, or the uncertainty penalty halved, raise CADO's primary unsafe rate over Consensus by 0.000023; both together by 0.000046 | yes | threshold_shift_0.05 +0.000023, uncertainty_scale_0.5 +0.000023, joint_0.05_0.5 +0.000046 |
| A4 | Section 5.4 | the only negative held-out utility difference is thresholds -0.05 with penalty x1.5, and its paired 95% interval includes zero | yes | joint_-0.05_1.5 -0.000032 [-0.000107, +0.000008] |
| A5 | Section 5.4 | an OOD limit of 1.65, or a penalty of x1.5, applied alone, suppresses held-out personalization completely | yes | ood_limit_1.65: held-out fallback 1.0000, uncertainty_scale_1.5: held-out fallback 1.0000 |
| A6 | Section 5.4 | radius zero reproduces Consensus exactly; radius two gives the same results as the default | yes | radius 0: all differences zero True; radius 2: means, differences and tests identical to the default True (bootstrap intervals differ by construction: seeded by setting name) |
| A7 | Section 5.5 | the state journal's hash chain is consistent | yes | journal_hash_chain_valid True |
| A8 | Section 4.2 | 43,200 primary decisions per policy (172,800 over four) and 10,800 held-out per policy | yes | ood Adaptive 10800, ood CADO 10800, ood Consensus 10800, ood Static 10800, primary Adaptive 43200, primary CADO 43200, primary Consensus 43200, primary Static 43200 |
| A9 | S1 `code/verify_claims.py` | the authors' own claim checks (benign actions unchanged, radius 0 and 2, one-level bound, the negative held-out setting, prototype counts) pass on our outputs | yes | exit 0 (`out/claims/claim_verification.json`) |

## Checklist (STANDARD.md, Section 2)

| # | requirement | met? | where |
|---|---|---|---|
| 1 | targets committed before any result | yes | 4b34e1d2 before the first result 8dbeec2d; `audit.py` ORDER |
| 2 | gaps decided before the run | yes: decisions 1-18 before the run; decision 19 is marked as made after the results | `DECISIONS.md` |
| 3 | authors asked about every gap | **not yet**: the two questions are drafted, to be sent by the user | `AUTHOR_CONTACT.md` |
| 4 | exact sources and licence | yes | `SOURCES.md`; S1 SHA-256 and the authors' manifest checked by `fetch.py` |
| 5 | variance: two machines identical (deterministic method) | yes: identical scientific outputs on a second machine (DESKTOP-JV86IM7) | `out/RECHECK_*.json`, DECISIONS 10 |
| 6 | every target reported | yes | table above, `audit.py` |
| 7 | environment recorded | yes | `out/ENVIRONMENT.json` |
| 8 | one command from public inputs, outputs hashed | yes: a fixed sequence of commands (`README.md`); every output's SHA-256 in `out/HASHES.txt` | `fetch.py`, `run.py` |
| 9 | unit tests for each rule | yes: comparison, verdict, hashing, lookups, S1 check | `tests/test_cado.py` |
| 10 | comparison only after this report; adaptations declared | not started | DECISIONS 1 |

## Environment

- Python 3.13.5, Windows-11-10.0.26100-SP0, machine DESKTOP-Q1DMJ51; matplotlib==3.10.0, numpy==2.1.3, pandas==2.2.3, scipy==1.15.3 (the authors' pins); full list in `out/ENVIRONMENT.json`.
- Rechecks on another machine: DESKTOP-JV86IM7: IDENTICAL.
- Every output's SHA-256 (LF line endings): `out/HASHES.txt`; scientific CSVs without timing columns: `out/SCIENTIFIC_SHA256.json`.
