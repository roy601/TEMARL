# CoADAM: A Co-Evolutionary Signaling Game Framework for Equilibrium Cyber Deception in Industrial IoT

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19556576.svg)](https://doi.org/10.5281/zenodo.19556576)

## Overview

CoADAM is a co-evolutionary deep reinforcement learning framework that models 
cyber deception in Industrial Internet of Things (IIoT) as a Constrained Markov 
Decision Process (CMDP) with an embedded signaling game. The framework trains a 
DQN defender against an adaptive attacker pool to achieve an ε-Nash deception 
equilibrium under explicit attacker skepticism dynamics.

**Key Results:**
- Attack Mitigation Rate (AMR): 0.8363 (random attacker), 0.8033 (adaptive attacker)
- ε-Nash exploitability: ε = 2.4523 (4.43% normalized)
- Cross-domain transfer retention: 99.61% across three IIoT datasets
- Physical testbed AMR: 0.9975 (Dell D660 honeypot, 10-day campaign)
- Converges at episode 1,377 across 5,000 training episodes

## Repository Structure

CoADAM/
│
├── README.md
├── .gitignore
│
├── core/
│   ├── iiot_environment.m            (IIoT simulation environment)
│   └── coevolutionary_trainer.m      (co-evolutionary training loop)
│
├── phases/
│   ├── Phase1_Preprocessing.m        (data preprocessing)
│   ├── Phase2A.m                     (environment configuration)
│   ├── Phase_3and4.m                 (DQN defender + co-evolutionary training)
│   ├── Phase5_Baselines.m            (baseline comparison)
│   ├── Phase6_CrossDataset.m         (cross-domain transfer)
│   ├── Phase7_Ablation.m             (ablation study)
│   ├── Phase8_Scalability.m          (scalability evaluation)
│   └── Phase9_GTAnalysis.m           (game-theoretic convergence)
│
├── figures/
│   ├── Fig_Co_TrainingLoop.m         (co-evolutionary training loop figure)
│   ├── Fig_GTAnalysis.m              (game-theoretic analysis figure)
│   ├── Fig_Mitre_Attack_Profile.m    (MITRE ATT&CK threat profile figure)
│   ├── Fig_Signal_Games_Dynamics.m   (signaling game dynamics figure)
│   ├── Fig_System_Architecture.m     (system architecture figure)
│   ├── Figure_Batch1.m               (results figures batch 1)
│   └── Figure_Batch2.m               (results figures batch 2)
│
├── testbed/
│   └── FinalTestBed_Validation.m     (physical testbed validation)
│
└── data/
    └── processed/
        ├── environment_config.mat    (tiny - upload)
        └── threat_profiles.mat       (0.1MB - upload)


## Requirements

- MATLAB R2025b
- Deep Learning Toolbox
- Statistics and Machine Learning Toolbox

## Datasets

The following publicly available datasets are used:

- **CIC-IIoT-2025**: https://www.unb.ca/cic/datasets/iiot-dataset-2025.html
- **WUSTL-IIoT-2021**: https://www.cse.wustl.edu/~jain/iiot2/index.html
- **Edge-IIoTset**: https://ieee-dataport.org/documents/edge-iiotset-new-comprehensive-realistic-cyber-security-dataset-iot-and-iiot-applications

Download and place processed files in `data/processed/` before running.

## How to Run

Step 1 — Preprocess datasets:
```matlab
run('phases/Phase1_Preprocessing.m')

Step 2 — Configure environment:
run('phases/Phase2A.m')

Step 3 — Train CoADAM (DQN defender + co-evolutionary attacker):
run('phases/Phase_3and4.m')

Step 4 — Run baseline comparison:
run('phases/Phase5_Baselines.m')

Step 5 — Cross-domain transfer evaluation:
run('phases/Phase6_CrossDataset.m')

Step 6 — Ablation study:
run('phases/Phase7_Ablation.m')

Step 7 — Scalability evaluation:
run('phases/Phase8_Scalability.m')

Step 8 — Game-theoretic convergence analysis:
run('phases/Phase9_GTAnalysis.m')

Step 9 — Physical testbed validation:
run('testbed/FinalTestBed_Validation.m')

Citation
If you use this code please cite:

Wushishi, U. (2026). CoADAM: A Co-Evolutionary Signaling Game Framework 
for Equilibrium Cyber Deception in Industrial IoT. Scientific Reports.

License
This project is licensed under the MIT License.

Contact
Usman Wushishi — wushi09@outlook.com
School of Computer Science and Technology
Chongqing University of Posts and Telecommunications


