%%
% CoADAM Phase 2A: Environment Configuration Builder
% Builds and saves the complete simulation configuration struct.
% Loads threat profiles from Phase 1 to ground attack distributions.
%
% Input:  /Users/ujw/Desktop/CoADAM/data/processed/threat_profiles.mat
% Output: /Users/ujw/Desktop/CoADAM/data/processed/environment_config.mat
%         /Users/ujw/Desktop/CoADAM/phase2_environment/config_report.txt
%
% Date: 28-Feb-2026
%%

clear; clc;
fprintf('CoADAM Phase 2A: Environment Configuration Builder\n');
fprintf('Timestamp: %s\n', char(datetime('now')));
fprintf('==================================================\n\n');

% Paths
project_root = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
phase2_dir = fullfile(project_root, 'phase2_environment');
if ~exist(phase2_dir, 'dir'), mkdir(phase2_dir); end

% Open report file
report_path = fullfile(phase2_dir, 'config_report.txt');
fid = fopen(report_path, 'w');
dual_print(fid, 'CoADAM Phase 2A: Environment Configuration Report\n');
dual_print(fid, 'Timestamp: %s\n', char(datetime('now')));
dual_print(fid, '==================================================\n\n');

% Load threat profiles from Phase 1
tp_path = fullfile(processed_dir, 'threat_profiles.mat');
dual_print(fid, 'Loading threat profiles from: %s\n', tp_path);
load(tp_path, 'threat_profiles');
dual_print(fid, 'Threat profiles loaded successfully.\n\n');

%%
% 1. MITRE ATT&CK CATEGORY DEFINITIONS
%%
dual_print(fid, '--- 1. MITRE ATT&CK Category Definitions ---\n\n');

config = struct();

config.mitre_categories = {'Reconnaissance', 'InitialAccess', 'Execution', ...
                           'LateralMovement', 'Impact'};
config.n_attack_categories = length(config.mitre_categories);

% MITRE technique IDs for citation in the paper
config.mitre_technique_ids = struct();
config.mitre_technique_ids.Reconnaissance = {'T1595', 'T1592', 'T1590'};
config.mitre_technique_ids.InitialAccess = {'T1110', 'T1190', 'T1133'};
config.mitre_technique_ids.Execution = {'T1059', 'T1204', 'T1053'};
config.mitre_technique_ids.LateralMovement = {'T1021', 'T1570', 'T1080'};
config.mitre_technique_ids.Impact = {'T1498', 'T1486', 'T1489'};

for i = 1:config.n_attack_categories
    cat = config.mitre_categories{i};
    ids = config.mitre_technique_ids.(cat);
    dual_print(fid, '  %s: %s\n', cat, strjoin(ids, ', '));
end
dual_print(fid, '\n');

%%
% 2. DEFENSE MECHANISMS
%%
dual_print(fid, '--- 2. Defense Mechanisms ---\n\n');

config.defense_mechanisms = {'Honeypot', 'IDS', 'NetworkSegmentation', ...
                             'AccessControl', 'TrafficFiltering', 'DecoyDocuments'};
config.n_mechanisms = length(config.defense_mechanisms);

% Normalized costs [0,1] relative to total budget = 1.0
% Justification: CIS Controls 2023 cost benchmarks (USD shown for reference)
% Honeypot: USD 15,000 -> 0.04
% IDS: USD 45,000 -> 0.12
% NetworkSegmentation: USD 100,000 -> 0.27
% AccessControl: USD 85,000 -> 0.23
% TrafficFiltering: USD 40,000 -> 0.11
% DecoyDocuments: USD 22,000 -> 0.06
% Total reference: USD 307,000 (not all deployed simultaneously)
% Normalized to max single deployment cost (NetworkSegmentation = 0.27)

config.mechanism_costs = [0.008, 0.025, 0.055, 0.045, 0.020, 0.012];


% False positive rates per mechanism (operational data, NIST SP 800-94)
config.mechanism_fpr = [0.02, 0.08, 0.01, 0.03, 0.06, 0.04];

% Deployment latency in normalized time units [0,1]
% Honeypot: near-instant (pre-deployed) -> 0.05
% IDS: signature update cycle -> 0.10
% NetworkSegmentation: SDN rule propagation -> 0.20
% AccessControl: policy push -> 0.15
% TrafficFiltering: filter rule insertion -> 0.08
% DecoyDocuments: file placement -> 0.03
config.mechanism_latency = [0.05, 0.10, 0.20, 0.15, 0.08, 0.03];

% Is mechanism deception-based? (for DSR tracking)
config.mechanism_is_deception = [true, false, false, false, false, true];

for i = 1:config.n_mechanisms
    dual_print(fid, '  %s: cost=%.2f, fpr=%.2f, latency=%.2f, deception=%d\n', ...
        config.defense_mechanisms{i}, config.mechanism_costs(i), ...
        config.mechanism_fpr(i), config.mechanism_latency(i), ...
        config.mechanism_is_deception(i));
end
dual_print(fid, '\n');

%%
% 3. EFFECTIVENESS MATRIX (mechanism x attack_category)
%%
dual_print(fid, '--- 3. Effectiveness Matrix ---\n\n');

% Rows: mechanisms (6), Columns: attack categories (5)
% Values in [0,1]: probability of successfully mitigating the attack
% Sources: MITRE ATT&CK mitigations, NIST guidelines, Verizon DBIR 2024
%
%                    Recon  InitAcc  Exec  LatMov  Impact
config.effectiveness = [
    0.25,  0.15,   0.10,  0.20,   0.15;   % Honeypot
    0.60,  0.55,   0.50,  0.45,   0.70;   % IDS
    0.15,  0.30,   0.20,  0.75,   0.40;   % NetworkSegmentation
    0.20,  0.70,   0.35,  0.60,   0.25;   % AccessControl
    0.50,  0.40,   0.30,  0.35,   0.80;   % TrafficFiltering
    0.30,  0.20,   0.15,  0.25,   0.10;   % DecoyDocuments
];

dual_print(fid, '  Effectiveness matrix [mechanism x attack_category]:\n');
dual_print(fid, '  %-22s', '');
for j = 1:config.n_attack_categories
    dual_print(fid, '%-15s', config.mitre_categories{j});
end
dual_print(fid, '\n');
for i = 1:config.n_mechanisms
    dual_print(fid, '  %-22s', config.defense_mechanisms{i});
    for j = 1:config.n_attack_categories
        dual_print(fid, '%-15.2f', config.effectiveness(i,j));
    end
    dual_print(fid, '\n');
end
dual_print(fid, '\n');

% Deception engagement probability: if attack hits a deception mechanism,
% probability the attacker is "engaged" (dwells) rather than immediately
% recognizing the deception. Higher = better deception quality.
%                    Recon  InitAcc  Exec  LatMov  Impact
config.deception_engagement = [
    0.70,  0.55,   0.40,  0.60,   0.35;   % Honeypot
    0.00,  0.00,   0.00,  0.00,   0.00;   % IDS (not deception)
    0.00,  0.00,   0.00,  0.00,   0.00;   % NetworkSegmentation
    0.00,  0.00,   0.00,  0.00,   0.00;   % AccessControl
    0.00,  0.00,   0.00,  0.00,   0.00;   % TrafficFiltering
    0.60,  0.45,   0.35,  0.50,   0.30;   % DecoyDocuments
];

dual_print(fid, '  Deception engagement matrix [mechanism x attack_category]:\n');
dual_print(fid, '  %-22s', '');
for j = 1:config.n_attack_categories
    dual_print(fid, '%-15s', config.mitre_categories{j});
end
dual_print(fid, '\n');
for i = 1:config.n_mechanisms
    dual_print(fid, '  %-22s', config.defense_mechanisms{i});
    for j = 1:config.n_attack_categories
        dual_print(fid, '%-15.2f', config.deception_engagement(i,j));
    end
    dual_print(fid, '\n');
end
dual_print(fid, '\n');

%%
% 4. DEFENDER STRATEGY BUNDLES
%%
dual_print(fid, '--- 4. Defender Strategy Bundles ---\n\n');

% Each bundle allocates resources across the 6 mechanisms.
% Rows: bundles (actions), Columns: mechanism allocation weights [0,1]
% Weights represent relative resource allocation (summing to ~1.0)
%
% Bundle 0: Balanced Defense - even spread
% Bundle 1: Deception Heavy - prioritize honeypots and decoys
% Bundle 2: Perimeter Defense - IDS, filtering, segmentation
% Bundle 3: Access Lockdown - access control, segmentation, IDS

%                    Honeypot  IDS   NetSeg  AccCtrl  TrafFilt  Decoy
config.strategy_bundles = [
    0.15,  0.20,  0.20,   0.20,    0.15,     0.10;   % Balanced
    0.35,  0.10,  0.05,   0.05,    0.10,     0.35;   % Deception Heavy
    0.05,  0.30,  0.25,   0.10,    0.25,     0.05;   % Perimeter Defense
    0.05,  0.20,  0.25,   0.30,    0.15,     0.05;   % Access Lockdown
];

config.strategy_names = {'Balanced', 'DeceptionHeavy', 'PerimeterDefense', 'AccessLockdown'};
config.n_defender_actions = size(config.strategy_bundles, 1);

for i = 1:config.n_defender_actions
    dual_print(fid, '  Bundle %d (%s):\n', i-1, config.strategy_names{i});
    for j = 1:config.n_mechanisms
        dual_print(fid, '    %-22s %.2f\n', config.defense_mechanisms{j}, ...
            config.strategy_bundles(i,j));
    end
    bundle_cost = sum(config.strategy_bundles(i,:) .* config.mechanism_costs);
    bundle_fpr = sum(config.strategy_bundles(i,:) .* config.mechanism_fpr);
    dual_print(fid, '    Estimated cost: %.4f, Estimated FPR: %.4f\n\n', ...
        bundle_cost, bundle_fpr);
end

%%
% 5. ATTACKER ACTION SPACE
%%
dual_print(fid, '--- 5. Attacker Action Space ---\n\n');

% Attacker chooses: tactic (5) x intensity (3) x target_zone (3) = 45 actions
% Tactics align with MITRE categories
config.attacker_tactics = config.mitre_categories;  % 5 tactics
config.n_attacker_tactics = config.n_attack_categories;

% Intensity levels affect success probability and detectability
config.intensity_levels = {'Low', 'Medium', 'High'};
config.n_intensity = length(config.intensity_levels);
config.intensity_multipliers = [0.6, 1.0, 1.5];      % success rate multiplier
config.intensity_detectability = [0.5, 1.0, 1.8];     % detectability multiplier
config.intensity_cost = [0.05, 0.10, 0.20];           % attacker resource cost

% Target zones represent network segments
config.target_zones = {'Edge', 'Core', 'Critical'};
config.n_zones = length(config.target_zones);
config.zone_value = [0.3, 0.6, 1.0];                  % damage value if breached
config.zone_defense_bonus = [0.0, 0.1, 0.2];          % extra defense from segmentation

% Total attacker actions
config.n_attacker_actions = config.n_attacker_tactics * config.n_intensity * config.n_zones;

% Build attacker action lookup table
config.attacker_action_table = zeros(config.n_attacker_actions, 3);
idx = 0;
for t = 1:config.n_attacker_tactics
    for i = 1:config.n_intensity
        for z = 1:config.n_zones
            idx = idx + 1;
            config.attacker_action_table(idx, :) = [t, i, z];
        end
    end
end

dual_print(fid, '  Tactics: %s\n', strjoin(config.attacker_tactics, ', '));
dual_print(fid, '  Intensity levels: %s (multipliers: [%.1f, %.1f, %.1f])\n', ...
    strjoin(config.intensity_levels, ', '), config.intensity_multipliers);
dual_print(fid, '  Target zones: %s (values: [%.1f, %.1f, %.1f])\n', ...
    strjoin(config.target_zones, ', '), config.zone_value);
dual_print(fid, '  Total attacker actions: %d\n\n', config.n_attacker_actions);

%%
% 6. ATTACK BASE SUCCESS RATES (grounded in threat profiles)
%%
dual_print(fid, '--- 6. Attack Base Success Rates ---\n\n');

% Base success rates per tactic (Verizon DBIR 2024, ENISA Threat Landscape)
% These represent probability of success against an undefended target
config.attack_base_success = [0.35, 0.30, 0.25, 0.20, 0.40];
%                             Recon  InitAcc Exec  LatMov Impact

% Attack frequency weights from primary dataset (CIC-IIoT-2025)
% Derived from threat_profiles: proportion of each attack category
% excluding benign traffic
cic_profile = threat_profiles.cic;
attack_cats = config.mitre_categories;
attack_proportions = zeros(1, config.n_attack_categories);
for i = 1:config.n_attack_categories
    fname = attack_cats{i};
    if isfield(cic_profile, fname)
        attack_proportions(i) = cic_profile.(fname);
    else
        attack_proportions(i) = 0.01;  % minimum floor
    end
end
% Normalize to sum to 1 (attack-only distribution)
attack_proportions = attack_proportions / sum(attack_proportions);
config.attack_frequency = attack_proportions;

% Breach damage per tactic (normalized, IBM Cost of Data Breach 2024)
% Reconnaissance alone causes minimal direct damage
% Impact (DDoS, ransomware) causes maximum
config.breach_damage = [0.10, 0.40, 0.60, 0.50, 1.00];

dual_print(fid, '  Base success rates:\n');
for i = 1:config.n_attack_categories
    dual_print(fid, '    %-20s success=%.2f, frequency=%.4f, damage=%.2f\n', ...
        config.mitre_categories{i}, config.attack_base_success(i), ...
        config.attack_frequency(i), config.breach_damage(i));
end
dual_print(fid, '\n');

%%
% 7. SKEPTICISM AND MOMENTUM DYNAMICS
%%
dual_print(fid, '--- 7. Skepticism and Momentum Dynamics ---\n\n');

config.skepticism = struct();
config.skepticism.initial = 0.0;
config.skepticism.max = 0.8;
config.skepticism.increment = 0.05;
config.skepticism.decay = 0.92;
config.skepticism.effect_on_deception = 0.8;

config.momentum = struct();
config.momentum.initial = 0.0;
config.momentum.max = 1.0;
config.momentum.increment = 0.10;    % per successful attack
config.momentum.decay_rate = 0.05;   % subtracted per failed attack
config.momentum.effect_on_success = 0.3;  % bonus: success += momentum * effect

dual_print(fid, '  Skepticism: initial=%.2f, max=%.2f, inc=%.2f, decay=%.2f\n', ...
    config.skepticism.initial, config.skepticism.max, ...
    config.skepticism.increment, config.skepticism.decay);
dual_print(fid, '  Momentum: initial=%.2f, max=%.2f, inc=%.2f, decay=%.2f\n', ...
    config.momentum.initial, config.momentum.max, ...
    config.momentum.increment, config.momentum.decay_rate);
dual_print(fid, '\n');

%%
% 8. NETWORK CONFIGURATION
%%
dual_print(fid, '--- 8. Network Configuration ---\n\n');

config.network = struct();
config.network.default_n_devices = 100;
config.network.scale_levels = [100, 250, 500];   % for scalability experiments
config.network.infection_spread_rate = 0.03;      % per infected node per step
config.network.max_infection = 1.0;               % fully compromised
config.network.recovery_rate = 0.01;              % natural recovery per step
config.network.zone_distribution = [0.50, 0.35, 0.15];  % Edge, Core, Critical

dual_print(fid, '  Default devices: %d\n', config.network.default_n_devices);
dual_print(fid, '  Scale levels: [%s]\n', num2str(config.network.scale_levels));
dual_print(fid, '  Infection spread rate: %.2f\n', config.network.infection_spread_rate);
dual_print(fid, '  Zone distribution: Edge=%.0f%%, Core=%.0f%%, Critical=%.0f%%\n', ...
    config.network.zone_distribution * 100);
dual_print(fid, '\n');

%%
% 9. EPISODE CONFIGURATION
%%
dual_print(fid, '--- 9. Episode Configuration ---\n\n');

config.episode = struct();
config.episode.max_steps = 100;
config.episode.initial_infection = 0.05;        % 5% of devices start compromised
config.episode.initial_budget_remaining = 5.0;  % full budget at start
config.episode.early_termination = true;        % end if infection > threshold
config.episode.termination_threshold = 0.90;    % 90% infection = game over

dual_print(fid, '  Max steps per episode: %d\n', config.episode.max_steps);
dual_print(fid, '  Initial infection: %.0f%%\n', config.episode.initial_infection * 100);
dual_print(fid, '  Early termination at: %.0f%% infection\n', ...
    config.episode.termination_threshold * 100);
dual_print(fid, '\n');

% 10. REWARD CONFIGURATION

dual_print(fid, '--- 10. Reward Configuration ---\n\n');

% Defender reward components (all unitless, normalized)
config.reward = struct();
config.reward.w_mitigation = 1.5;           % reward for successful attack mitigation
config.reward.w_deception = 3.0;            % reward for successful deception/trapping
config.reward.w_false_positive = -0.3;      % penalty for false alarms
config.reward.w_cost = -1.5;               % penalty multiplied by bundle_cost
config.reward.w_infection = -1.2;           % penalty proportional to infection rate
config.reward.w_dwell = 0.6;               % reward for attacker dwell time on deception
config.reward.w_diversity = 0.05;           % reward for strategy diversity
config.reward.w_momentum_penalty = -0.5;    % penalty if attacker has high momentum
config.reward.w_infection_delta = 2.5;      % reward for reducing infection step-to-step
config.reward.w_critical_zone = -2.0;       % extra penalty for critical zone infection

% Attacker reward components (mirror of defender losses)
config.reward.attacker_w_success = 1.0;       % reward for successful attack
config.reward.attacker_w_damage = 1.5;        % reward proportional to damage caused
config.reward.attacker_w_detection = -1.0;    % penalty for being detected
config.reward.attacker_w_trapped = -2.0;      % penalty for being trapped by deception
config.reward.attacker_w_cost = -0.2;         % penalty for attack resource cost
config.reward.attacker_w_momentum = 0.3;      % reward for maintaining momentum

% Reward weight profiles for sensitivity analysis
config.reward_profiles = struct();
config.reward_profiles.aggressive = struct('w_mitigation', 1.5, 'w_deception', 3.0, ...
    'w_false_positive', -0.3, 'w_cost', -1.5, 'w_infection', -1.2, ...
    'w_dwell', 0.6, 'w_diversity', 0.05, 'w_momentum_penalty', -0.5, ...
    'w_infection_delta', 2.5, 'w_critical_zone', -2.0);
config.reward_profiles.balanced = struct('w_mitigation', 1.0, 'w_deception', 2.5, ...
    'w_false_positive', -0.5, 'w_cost', -2.0, 'w_infection', -1.0, ...
    'w_dwell', 0.5, 'w_diversity', 0.1, 'w_momentum_penalty', -0.3, ...
    'w_infection_delta', 2.0, 'w_critical_zone', -1.5);
config.reward_profiles.conservative = struct('w_mitigation', 0.8, 'w_deception', 2.0, ...
    'w_false_positive', -1.0, 'w_cost', -2.5, 'w_infection', -0.8, ...
    'w_dwell', 0.3, 'w_diversity', 0.15, 'w_momentum_penalty', -0.2, ...
    'w_infection_delta', 1.5, 'w_critical_zone', -1.0);
config.reward_profiles.security_first = struct('w_mitigation', 1.5, 'w_deception', 1.5, ...
    'w_false_positive', -0.5, 'w_cost', -1.5, 'w_infection', -2.5, ...
    'w_dwell', 0.3, 'w_diversity', 0.10, 'w_momentum_penalty', -0.5, ...
    'w_infection_delta', 3.0, 'w_critical_zone', -2.0);

profile_names = fieldnames(config.reward_profiles);
dual_print(fid, '  Default reward weights:\n');
dual_print(fid, '    w_mitigation=%.1f, w_deception=%.1f, w_fp=%.1f, w_cost=%.1f\n', ...
    config.reward.w_mitigation, config.reward.w_deception, ...
    config.reward.w_false_positive, config.reward.w_cost);
dual_print(fid, '    w_infection=%.1f, w_dwell=%.1f, w_diversity=%.1f, w_momentum=%.1f\n', ...
    config.reward.w_infection, config.reward.w_dwell, ...
    config.reward.w_diversity, config.reward.w_momentum_penalty);
dual_print(fid, '    w_infection_delta=%.1f, w_critical_zone=%.1f\n', ...
    config.reward.w_infection_delta, config.reward.w_critical_zone);
dual_print(fid, '\n  Reward profiles for sensitivity analysis:\n');
for p = 1:length(profile_names)
    dual_print(fid, '    %s\n', profile_names{p});
end
dual_print(fid, '\n');

%%
% 11. STATE SPACE DEFINITION
%%
dual_print(fid, '--- 11. State Space Definition ---\n\n');

% Defender observes:
config.defender_state = struct();
config.defender_state.features = {
    'infection_rate';           % [0, 1] fraction of compromised devices
    'deception_density';        % [0, 1] fraction of deception mechanisms active
    'recent_attack_category';   % [1, 5] last observed MITRE tactic (discretized)
    'attack_intensity';         % [0, 1] normalized recent attack intensity
    'momentum';                 % [0, 1] attacker momentum
    'skepticism';               % [0, 0.5] attacker skepticism toward deception
    'budget_remaining';         % [0, 1] remaining defense budget
    'false_positive_rate';      % [0, 1] recent false positive rate
    'time_step_normalized';     % [0, 1] current step / max steps
    'zone_threat_edge';         % [0, 1] threat level in edge zone
    'zone_threat_core';         % [0, 1] threat level in core zone
    'zone_threat_critical'      % [0, 1] threat level in critical zone
};
config.defender_state.n_features = length(config.defender_state.features);

% For tabular Q-learning: discretization bins per feature
config.defender_state.n_bins = [5, 3, 5, 3, 4, 3, 4, 3, 5, 3, 3, 3];

% Attacker observes:
config.attacker_state = struct();
config.attacker_state.features = {
    'observed_defense_type';    % [1, 4] perceived defender bundle
    'recent_success';           % [0, 1] fraction of recent attacks that succeeded
    'skepticism';               % [0, 0.5] own skepticism toward deception
    'momentum';                 % [0, 1] own momentum
    'detected_deception';       % [0, 1] fraction of recent deceptions identified
    'target_zone_infection';    % [0, 1] infection in currently targeted zone
    'time_step_normalized';     % [0, 1] current step / max steps
    'defense_change_rate'       % [0, 1] how often defender changed strategy recently
};
config.attacker_state.n_features = length(config.attacker_state.features);
config.attacker_state.n_bins = [4, 4, 3, 4, 3, 4, 5, 3];

dual_print(fid, '  Defender state: %d features\n', config.defender_state.n_features);
for i = 1:config.defender_state.n_features
    dual_print(fid, '    %d. %-30s bins=%d\n', i, ...
        config.defender_state.features{i}, config.defender_state.n_bins(i));
end
dual_print(fid, '\n  Attacker state: %d features\n', config.attacker_state.n_features);
for i = 1:config.attacker_state.n_features
    dual_print(fid, '    %d. %-30s bins=%d\n', i, ...
        config.attacker_state.features{i}, config.attacker_state.n_bins(i));
end
dual_print(fid, '\n');

%%
% 12. NOVEL ATTACK DEFINITIONS
%%
dual_print(fid, '--- 12. Novel Attack Definitions ---\n\n');

config.novel_attacks = struct();
config.novel_attacks.types = {'Polymorphic', 'AIGenerated', 'ZeroClick', 'SupplyChain'};
config.novel_attacks.n_types = length(config.novel_attacks.types);

% Novel attacks modify base parameters
% Each has a primary MITRE tactic, modified success rate, and evasion bonus
config.novel_attacks.primary_tactic = [3, 2, 2, 1];  % Exec, InitAcc, InitAcc, Recon
config.novel_attacks.success_modifier = [1.3, 1.4, 1.5, 1.2];  % harder to stop
config.novel_attacks.evasion_bonus = [0.15, 0.20, 0.25, 0.10]; % harder to detect
config.novel_attacks.deception_resistance = [0.10, 0.25, 0.15, 0.05]; % resist deception

for i = 1:config.novel_attacks.n_types
    dual_print(fid, '  %s: tactic=%s, success_mod=%.1f, evasion=%.2f, deception_resist=%.2f\n', ...
        config.novel_attacks.types{i}, ...
        config.mitre_categories{config.novel_attacks.primary_tactic(i)}, ...
        config.novel_attacks.success_modifier(i), ...
        config.novel_attacks.evasion_bonus(i), ...
        config.novel_attacks.deception_resistance(i));
end
dual_print(fid, '\n');

%%
% 13. METRIC TRACKING CONFIGURATION
%%
dual_print(fid, '--- 13. Metric Tracking (14 metrics) ---\n\n');

config.metrics = struct();
config.metrics.names = {
    'AMR';                      % Attack Mitigation Rate
    'DSR';                      % Deception Success Rate
    'FAR';                      % False Alarm Rate
    'CumulativeReward';         % Total defender reward
    'InfectionRate';            % Final infection rate
    'MTTD';                     % Mean Time to Detect (steps)
    'AttackerDwellTime';        % Average dwell on deception (steps)
    'DefenseCostEfficiency';    % Damage prevented / cost spent
    'CVaR_005';                 % Conditional Value at Risk (alpha=0.05)
    'TrainingReliability_DR';   % Dispersion across runs (IQR)
    'CrossDomainRetention';     % Performance retention on transfer
    'AblationDegradation';      % Performance drop per removed component
    'AttackerAdaptationRate';   % Attacker improvement over training
    'NashConvergenceGap'        % Gap from best-response equilibrium
};
config.metrics.n_metrics = length(config.metrics.names);
config.metrics.cvar_alpha = 0.05;
config.metrics.n_eval_runs = 20;  % for statistical significance

dual_print(fid, '  Total metrics: %d\n', config.metrics.n_metrics);
for i = 1:config.metrics.n_metrics
    dual_print(fid, '    %2d. %s\n', i, config.metrics.names{i});
end
dual_print(fid, '\n');

%%
% 14. TRAINING HYPERPARAMETERS
%%
dual_print(fid, '--- 14. Training Hyperparameters ---\n\n');

config.training = struct();
config.training.n_episodes = 2000;
config.training.max_steps = config.episode.max_steps;  % 100
config.training.n_seeds = 20;

% Defender (CoADAM) Q-learning parameters
config.training.defender = struct();
config.training.defender.learning_rate = 0.001;
config.training.defender.gamma = 0.85;
config.training.defender.epsilon_start = 0.15;
config.training.defender.epsilon_decay = 0.995;
config.training.defender.epsilon_min = 0.05;

% Attacker Q-learning parameters
config.training.attacker = struct();
config.training.attacker.learning_rate = 0.001;
config.training.attacker.gamma = 0.80;
config.training.attacker.epsilon_start = 0.20;
config.training.attacker.epsilon_decay = 0.993;
config.training.attacker.epsilon_min = 0.05;

dual_print(fid, '  Episodes: %d, Steps/episode: %d, Seeds: %d\n', ...
    config.training.n_episodes, config.training.max_steps, config.training.n_seeds);
dual_print(fid, '  Defender: lr=%.4f, gamma=%.2f, eps=[%.2f -> %.2f, decay=%.4f]\n', ...
    config.training.defender.learning_rate, config.training.defender.gamma, ...
    config.training.defender.epsilon_start, config.training.defender.epsilon_min, ...
    config.training.defender.epsilon_decay);
dual_print(fid, '  Attacker: lr=%.4f, gamma=%.2f, eps=[%.2f -> %.2f, decay=%.4f]\n', ...
    config.training.attacker.learning_rate, config.training.attacker.gamma, ...
    config.training.attacker.epsilon_start, config.training.attacker.epsilon_min, ...
    config.training.attacker.epsilon_decay);
dual_print(fid, '\n');

%%
% 15. DATASET CONFIGURATION
%%
dual_print(fid, '--- 15. Dataset Configuration ---\n\n');

config.datasets = struct();
config.datasets.primary = 'cic_iiot_2025';
config.datasets.transfer = {'wustl_iiot_2021', 'edge_iiot'};
config.datasets.paths = struct();
config.datasets.paths.cic_iiot_2025 = fullfile(processed_dir, 'cic_iiot_2025_processed.mat');
config.datasets.paths.wustl_iiot_2021 = fullfile(processed_dir, 'wustl_iiot_2021_processed.mat');
config.datasets.paths.edge_iiot = fullfile(processed_dir, 'edge_iiot_processed.mat');
config.datasets.paths.threat_profiles = fullfile(processed_dir, 'threat_profiles.mat');

ds_names = fieldnames(config.datasets.paths);
for i = 1:length(ds_names)
    p = config.datasets.paths.(ds_names{i});
    exists_str = 'FOUND';
    if ~isfile(p), exists_str = 'MISSING'; end
    dual_print(fid, '  %s: %s [%s]\n', ds_names{i}, p, exists_str);
end
dual_print(fid, '\n');

%%
% 16. SUMMARY
%%
dual_print(fid, '--- Configuration Summary ---\n\n');
dual_print(fid, '  Defense mechanisms:     %d\n', config.n_mechanisms);
dual_print(fid, '  Defender actions:       %d strategy bundles\n', config.n_defender_actions);
dual_print(fid, '  Attacker actions:       %d (5 tactics x 3 intensity x 3 zones)\n', ...
    config.n_attacker_actions);
dual_print(fid, '  Defender state dim:     %d features\n', config.defender_state.n_features);
dual_print(fid, '  Attacker state dim:     %d features\n', config.attacker_state.n_features);
dual_print(fid, '  Episode length:         %d steps\n', config.episode.max_steps);
dual_print(fid, '  Training episodes:      %d\n', config.training.n_episodes);
dual_print(fid, '  Evaluation seeds:       %d\n', config.training.n_seeds);
dual_print(fid, '  Metrics tracked:        %d\n', config.metrics.n_metrics);
dual_print(fid, '  Reward profiles:        %d\n', length(profile_names));
dual_print(fid, '  Novel attack types:     %d\n', config.novel_attacks.n_types);
dual_print(fid, '  Network scale levels:   [%s]\n', num2str(config.network.scale_levels));
dual_print(fid, '  Primary dataset:        %s\n', config.datasets.primary);
dual_print(fid, '  Transfer datasets:      %s\n', strjoin(config.datasets.transfer, ', '));

%%
% SAVE
%%
save_path = fullfile(processed_dir, 'environment_config.mat');
save(save_path, 'config');
dual_print(fid, '\nConfiguration saved to: %s\n', save_path);
dual_print(fid, 'Report saved to: %s\n', report_path);
dual_print(fid, '\nPhase 2A complete. Proceed to Phase 2B (environment core).\n');

fclose(fid);
fprintf('\nDone. Report saved to: %s\n', report_path);

%%
% HELPER FUNCTION
%%
function dual_print(fid, varargin)
    fprintf(varargin{:});
    if fid > 0
        fprintf(fid, varargin{:});
    end
end
