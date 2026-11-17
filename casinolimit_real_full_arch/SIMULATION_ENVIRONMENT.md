# CasinoLimit replay environment

This is a resource-allocation simulation grounded in recorded CasinoLimit
commands. It is not a reconstructed live honeynet and does not measure real
human responses to decoys. No attacks or data splits are generated.

## Data and episodes

The runner imports casinolimit_encoder/cl_port.py, including its corpus hash
check, and cl_data.folds(). It uses the same 8,201 command steps and five
whole-instance splits as prediction. Every episode preserves command label
sets and recorded machine order and ends at trace exhaustion. Replaying an
instance does not create an independent campaign. The machines are start,
bastion, meet and intranet. Consecutive machine changes are not asserted to
be proven lateral movement. No fabricated topology or target tactic is used.

## Defender design (explicit modelling assumptions)

Four parameter-sharing agents each control a decoy on one recorded machine.
Actions are off/on. Capacity is two decoys. For n active decoys, an action on
an enabled machine is intercepted with probability .5 * min(1, 2/n).
The .5 efficacy is an uncalibrated assumption. It is not estimated from the
paper. Replay continues after interception; this cannot model how a human
would change subsequent commands. Shared reward is intercepted-command
indicator minus .01 per active decoy. This simplified environment deliberately
does not inherit CAM-LDS's technique-dependent payoff and synthetic movement.
Its outcomes require sensitivity analysis before publication.

Local actors receive their identity, own allocation, shared resource load,
elapsed steps and previous local sightings/techniques plus a frozen history
representation. MAPPO has a training-only global critic; IPPO uses local
critic inputs. PPO clipping, GAE, value normalization and optimiser settings
reuse camlds_real_full_arch/mappo_cmd.py. See that file's HP dictionary.

## Encoders

allpos (causal Transformer), baseline (original Transformer), gru_allpos and
lstm_allpos use existing CasinoLimit checkpoints. Missing checkpoints require
--train-missing and reuse the saved CasinoLimit budget.json and validation
stopping procedure. NoHistory supplies zeros. Kuwano uses recommend_limit
from kuwano_repro, ATT&CK v11 group data and k=60. Similarity-one handling is
the already documented limit adaptation. Uncovered labels have zero support.
Scores s become s/(1+s), or 1 for an identical neighbour, and pass through a
fixed seed-2310 Gaussian 66-by-64 projection (std=1/8). This is a declared
feature adapter, not a reproduction of Kuwano's original evaluation task.

## Fog

Each arm is trained AND evaluated separately at 0%, 50%, 90% masking.
These are matched-fog experiments, not clean-training robustness results.
An episode's pre-drawn visibility uniform hides both local sighting/technique
telemetry and the corresponding shared history labels. History retains empty
time slots, so event timing/count remains observable. Critic state remains
privileged during centralized training. Random episode uniforms match across
arms and learners at equal seed. History never includes the pending command.

## Metrics and limitations

Dwell: count of intercepted recorded commands (not seconds).
Depth: distinct technique labels on intercepted commands.
Interception rate: intercepted commands / consumed commands. The reused
internal JSON key `protected` means THIS rate, not asset protection. The MD
report labels it correctly. Exposure, lures and dead ends are zero placeholders
in the inherited schema; these mechanisms are not implemented or measured.
Per-episode records and training curves are in result.json. No claims of
statistical significance are made by the report.

One challenge, sparse intranet observations, oracle technique annotations,
and unmeasured intervention responses limit external validity. This is an
operational replay allocation benchmark, not evidence of real deception.

## Execution

Run from the full repository (sibling folders are required):

    python -m pip install -r casinolimit_real_full_arch/requirements.txt
    python casinolimit_real_full_arch/test_pipeline.py
    python casinolimit_real_full_arch/pipeline.py --smoke --train-missing
    python casinolimit_real_full_arch/pipeline.py --device cuda --train-missing

Full defaults: five folds, ten seeds, six arms, two learners, three fog levels
= 1,800 RL cells. Completed result.json cells are skipped on restart. Interrupted
cells restart training; there is no mid-cell optimizer resume. Do not launch
two processes into the same output directory. Copy the entire repository to
the lab, including Kuwano data and CasinoLimit budget/checkpoints.
