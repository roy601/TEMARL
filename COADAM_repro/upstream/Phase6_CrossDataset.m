%%
% CoADAM Phase 6: Cross-Domain Transfer Testing (REVISED)
% Tests trained DQN defender on all three IIoT datasets
% Two evaluation modes:
%   Table A - Each domain uses its natural attack distribution
%   Table B - All domains use the CIC source attack distribution
% This separates domain difficulty from transfer quality.
% Date: 28-Feb-2026
%%
clear; clc;
fprintf('=== CoADAM Phase 6: Cross-Domain Transfer Testing (REVISED) ===\n');
fprintf('Started: %s\n\n', char(datetime('now')));
phase6_start = tic;

%% ---- Paths -------------------------------------------------------------
project_root  = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
results_dir   = fullfile(project_root, 'results');
phase2_dir    = fullfile(project_root, 'phase2_environment');
phase6_dir    = fullfile(project_root, 'phase6_transfer');

if ~exist(phase6_dir, 'dir'), mkdir(phase6_dir); end
if ~exist(results_dir, 'dir'), mkdir(results_dir); end
addpath(phase2_dir);

%% ---- Load config -------------------------------------------------------
fprintf('[1] Loading environment config...\n');
load(fullfile(processed_dir, 'environment_config.mat'), 'config');
fprintf('    Defender actions: %d, Attacker actions: %d, Max steps: %d\n', ...
    config.n_defender_actions, config.n_attacker_actions, config.episode.max_steps);

%% ---- Load trained DQN weights and attacker Q-table ---------------------
fprintf('[2] Loading trained CoADAM DQN...\n');
trained = load(fullfile(results_dir, 'dqn_cotraining_results.mat'), ...
    'W1', 'W2', 'W3', 'b1', 'b2', 'b3', 'atk_Q', ...
    'eval_amr', 'eval_dsr', 'eval_far', 'eval_rew', 'eval_inf', ...
    'eval_mttd', 'eval_dwell', 'eval_dce', 'eval_atk_rew', 'eval_length');

W1 = trained.W1; W2 = trained.W2; W3 = trained.W3;
b1 = trained.b1; b2 = trained.b2; b3 = trained.b3;
atk_Q = trained.atk_Q;

fprintf('    DQN: [%dx%d]->[%dx%d]->[%dx%d]\n', ...
    size(W1,1),size(W1,2), size(W2,1),size(W2,2), size(W3,1),size(W3,2));
fprintf('    Attacker Q-table: [%d x %d]\n', size(atk_Q,1), size(atk_Q,2));

% Source domain baseline (from Phase 3-4 evaluation on CIC)
source_metrics = struct();
source_metrics.AMR = mean(trained.eval_amr);
source_metrics.DSR = mean(trained.eval_dsr);
source_metrics.FAR = mean(trained.eval_far);
source_metrics.Reward = mean(trained.eval_rew);
source_metrics.Infection = mean(trained.eval_inf);
source_metrics.MTTD = mean(trained.eval_mttd);
source_metrics.DwellTime = mean(trained.eval_dwell);
source_metrics.DCE = mean(trained.eval_dce);
fprintf('    Source baseline: AMR=%.4f, Reward=%.2f, Infection=%.4f\n', ...
    source_metrics.AMR, source_metrics.Reward, source_metrics.Infection);

%% ---- Load threat profiles ----------------------------------------------
fprintf('[3] Loading threat profiles...\n');
tp = load(fullfile(processed_dir, 'threat_profiles.mat'), 'threat_profiles');
threat_profiles = tp.threat_profiles;

% Extract attack-only distributions (exclude benign, normalize to sum=1)
cic_fields = [threat_profiles.cic.Reconnaissance, threat_profiles.cic.InitialAccess, ...
    threat_profiles.cic.Execution, threat_profiles.cic.LateralMovement, threat_profiles.cic.Impact];
cic_dist = cic_fields / sum(cic_fields);

wustl_fields = [threat_profiles.wustl.Reconnaissance, threat_profiles.wustl.InitialAccess, ...
    threat_profiles.wustl.Execution, threat_profiles.wustl.LateralMovement, threat_profiles.wustl.Impact];
if sum(wustl_fields) > 0
    wustl_dist = wustl_fields / sum(wustl_fields);
else
    wustl_dist = ones(1,5)/5;
end

edge_fields = [threat_profiles.edge.Reconnaissance, threat_profiles.edge.InitialAccess, ...
    threat_profiles.edge.Execution, threat_profiles.edge.LateralMovement, threat_profiles.edge.Impact];
edge_dist = edge_fields / sum(edge_fields);

dataset_info = struct();
dataset_info(1).name = 'CIC-IIoT-2025';
dataset_info(1).short = 'cic';
dataset_info(1).role = 'Source';
dataset_info(1).attack_dist = cic_dist;

dataset_info(2).name = 'WUSTL-IIoT-2021';
dataset_info(2).short = 'wustl';
dataset_info(2).role = 'Transfer';
dataset_info(2).attack_dist = wustl_dist;

dataset_info(3).name = 'Edge-IIoTset';
dataset_info(3).short = 'edge';
dataset_info(3).role = 'Transfer';
dataset_info(3).attack_dist = edge_dist;

fprintf('    Attack distributions:\n');
for di = 1:3
    fprintf('    %s: [%.3f %.3f %.3f %.3f %.3f]\n', ...
        dataset_info(di).short, dataset_info(di).attack_dist);
end

% Source distribution (CIC) - used for Table B
source_dist = cic_dist;

%% ---- Attacker state discretization setup --------------------------------
atk_bins = config.attacker_state.n_bins;

%% ---- Evaluation settings ------------------------------------------------
n_eval = 100;
max_steps = config.episode.max_steps;
n_intensities = 3;
n_zones = 3;

fprintf('\n    Evaluation: %d episodes per domain per mode\n', n_eval);
fprintf('    Modes: (A) Natural attack dist, (B) CIC source dist\n\n');

%% ---- Helper: run evaluation on one domain with given distribution -------
% (defined as nested operations below to avoid nested function issues)

%% ---- DOMAIN DIFFICULTY CALIBRATION (Random Policy) ----------------------
fprintf('=== DOMAIN DIFFICULTY CALIBRATION (Random Policy) ===\n\n');

random_baseline = struct();

rng(42);
for di = 1:3
    fprintf('  Random policy on %s (natural distribution)...\n', dataset_info(di).short);
    
    eval_config = config;
    eval_config.attacker.frequency_weights = dataset_info(di).attack_dist;
    
    rand_metrics = zeros(n_eval, 10);
    
    for ep = 1:n_eval
        env = iiot_environment(eval_config);
        [def_state, atk_state] = env.reset();
        
        for step = 1:max_steps
            % Random defender
            def_action = randi(config.n_defender_actions);
            
            % Adaptive attacker (greedy from Q-table)
            atk_idx = env.discretize_state(atk_state, atk_bins);
            atk_q_row = atk_Q(atk_idx, :);
            for ti = 1:5
                action_range = ((ti-1)*n_intensities*n_zones + 1):(ti*n_intensities*n_zones);
                atk_q_row(action_range) = atk_q_row(action_range) * ...
                    (1 + 0.5 * (dataset_info(di).attack_dist(ti) - 0.2));
            end
            [~, atk_action] = max(atk_q_row);
            
            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env.get_episode_metrics();
        rand_metrics(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, ...
            m.DefenseCostEfficiency, m.AttackerCumulativeReward, m.EpisodeLength];
    end
    
    rb = struct();
    rb.AMR = mean(rand_metrics(:,1));
    rb.DSR = mean(rand_metrics(:,2));
    rb.FAR = mean(rand_metrics(:,3));
    rb.Reward = mean(rand_metrics(:,4));
    rb.InfectionRate = mean(rand_metrics(:,5));
    rb.MTTD = mean(rand_metrics(:,6));
    rb.DwellTime = mean(rand_metrics(:,7));
    rb.DCE = mean(rand_metrics(:,8));
    random_baseline.(dataset_info(di).short) = rb;
    
    fprintf('    AMR=%.4f, Reward=%.2f, Infection=%.4f\n', rb.AMR, rb.Reward, rb.InfectionRate);
end
fprintf('\n');

%% ---- TABLE A: NATURAL ATTACK DISTRIBUTIONS -----------------------------
fprintf('=== TABLE A: CoADAM per Domain (Natural Attack Distributions) ===\n\n');

results_A = struct();

rng(42);
for di = 1:3
    fprintf('  Evaluating %s (%s, natural dist)...\n', dataset_info(di).name, dataset_info(di).role);
    ds_start = tic;
    
    eval_config = config;
    eval_config.attacker.frequency_weights = dataset_info(di).attack_dist;
    
    ep_metrics = zeros(n_eval, 10);
    
    for ep = 1:n_eval
        env = iiot_environment(eval_config);
        [def_state, atk_state] = env.reset();
        
        for step = 1:max_steps
            % CoADAM DQN defender
            s = def_state(:);
            h1 = max(0, W1 * s + b1);
            h2 = max(0, W2 * h1 + b2);
            q_vals = W3 * h2 + b3;
            [~, def_action] = max(q_vals);
            
            % Adaptive attacker with dataset bias
            atk_idx = env.discretize_state(atk_state, atk_bins);
            atk_q_row = atk_Q(atk_idx, :);
            for ti = 1:5
                action_range = ((ti-1)*n_intensities*n_zones + 1):(ti*n_intensities*n_zones);
                atk_q_row(action_range) = atk_q_row(action_range) * ...
                    (1 + 0.5 * (dataset_info(di).attack_dist(ti) - 0.2));
            end
            [~, atk_action] = max(atk_q_row);
            
            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env.get_episode_metrics();
        ep_metrics(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, ...
            m.DefenseCostEfficiency, m.AttackerCumulativeReward, m.EpisodeLength];
    end
    
    ds_results = struct();
    ds_results.name = dataset_info(di).name;
    ds_results.role = dataset_info(di).role;
    ds_results.attack_dist = dataset_info(di).attack_dist;
    ds_results.raw = ep_metrics;
    ds_results.eval_time = toc(ds_start);
    
    metric_names = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
        'MTTD','AttackerDwellTime','DefenseCostEfficiency', ...
        'AttackerCumulativeReward','EpisodeLength'};
    
    for mi = 1:length(metric_names)
        arr = ep_metrics(:, mi);
        ds_results.(metric_names{mi}) = struct( ...
            'mean', mean(arr), 'std', std(arr), ...
            'min', min(arr), 'max', max(arr), ...
            'median', median(arr));
    end
    
    % CVaR
    sorted_rew = sort(ep_metrics(:,4), 'ascend');
    n_tail = max(1, floor(0.05 * n_eval));
    ds_results.CVaR_005 = mean(sorted_rew(1:n_tail));
    ds_results.DR = iqr(ep_metrics(:,4));
    
    results_A.(dataset_info(di).short) = ds_results;
    
    fprintf('    AMR: %.4f +/- %.4f | Reward: %.2f +/- %.2f | Infection: %.4f\n', ...
        ds_results.AMR.mean, ds_results.AMR.std, ...
        ds_results.CumulativeReward.mean, ds_results.CumulativeReward.std, ...
        ds_results.InfectionRate.mean);
    fprintf('    DSR: %.4f | MTTD: %.2f | DwellTime: %.2f | CVaR: %.2f\n', ...
        ds_results.DSR.mean, ds_results.MTTD.mean, ...
        ds_results.AttackerDwellTime.mean, ds_results.CVaR_005);
    fprintf('    Time: %.1f s\n\n', ds_results.eval_time);
end

%% ---- TABLE B: SOURCE (CIC) DISTRIBUTION ON ALL DOMAINS -----------------
fprintf('=== TABLE B: CoADAM per Domain (CIC Source Distribution) ===\n');
fprintf('    Isolates domain effect from attacker distribution effect\n\n');

results_B = struct();

rng(42);
for di = 1:3
    fprintf('  Evaluating %s (CIC source dist)...\n', dataset_info(di).name);
    ds_start = tic;
    
    eval_config = config;
    % Force CIC source distribution on all domains
    eval_config.attacker.frequency_weights = source_dist;
    
    ep_metrics = zeros(n_eval, 10);
    
    for ep = 1:n_eval
        env = iiot_environment(eval_config);
        [def_state, atk_state] = env.reset();
        
        for step = 1:max_steps
            % CoADAM DQN defender
            s = def_state(:);
            h1 = max(0, W1 * s + b1);
            h2 = max(0, W2 * h1 + b2);
            q_vals = W3 * h2 + b3;
            [~, def_action] = max(q_vals);
            
            % Adaptive attacker with SOURCE (CIC) bias
            atk_idx = env.discretize_state(atk_state, atk_bins);
            atk_q_row = atk_Q(atk_idx, :);
            for ti = 1:5
                action_range = ((ti-1)*n_intensities*n_zones + 1):(ti*n_intensities*n_zones);
                atk_q_row(action_range) = atk_q_row(action_range) * ...
                    (1 + 0.5 * (source_dist(ti) - 0.2));
            end
            [~, atk_action] = max(atk_q_row);
            
            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env.get_episode_metrics();
        ep_metrics(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, ...
            m.DefenseCostEfficiency, m.AttackerCumulativeReward, m.EpisodeLength];
    end
    
    ds_results = struct();
    ds_results.name = dataset_info(di).name;
    ds_results.role = dataset_info(di).role;
    ds_results.attack_dist = source_dist;
    ds_results.raw = ep_metrics;
    ds_results.eval_time = toc(ds_start);
    
    metric_names = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
        'MTTD','AttackerDwellTime','DefenseCostEfficiency', ...
        'AttackerCumulativeReward','EpisodeLength'};
    
    for mi = 1:length(metric_names)
        arr = ep_metrics(:, mi);
        ds_results.(metric_names{mi}) = struct( ...
            'mean', mean(arr), 'std', std(arr), ...
            'min', min(arr), 'max', max(arr), ...
            'median', median(arr));
    end
    
    sorted_rew = sort(ep_metrics(:,4), 'ascend');
    n_tail = max(1, floor(0.05 * n_eval));
    ds_results.CVaR_005 = mean(sorted_rew(1:n_tail));
    ds_results.DR = iqr(ep_metrics(:,4));
    
    results_B.(dataset_info(di).short) = ds_results;
    
    fprintf('    AMR: %.4f +/- %.4f | Reward: %.2f +/- %.2f | Infection: %.4f\n', ...
        ds_results.AMR.mean, ds_results.AMR.std, ...
        ds_results.CumulativeReward.mean, ds_results.CumulativeReward.std, ...
        ds_results.InfectionRate.mean);
    fprintf('    DSR: %.4f | MTTD: %.2f | DwellTime: %.2f | CVaR: %.2f\n', ...
        ds_results.DSR.mean, ds_results.MTTD.mean, ...
        ds_results.AttackerDwellTime.mean, ds_results.CVaR_005);
    fprintf('    Time: %.1f s\n\n', ds_results.eval_time);
end

%% ---- PRINT COMPARISON TABLES -------------------------------------------
domains = {'cic', 'wustl', 'edge'};
disp_names = {'CIC (Source)', 'WUSTL (Transfer)', 'Edge (Transfer)'};
show_metrics = {'AMR','DSR','FAR','CumulativeReward','InfectionRate','MTTD','AttackerDwellTime','DefenseCostEfficiency'};
show_labels  = {'AMR','DSR','FAR','Reward','Infection','MTTD','DwellTime','CostEff'};

fprintf('\n=== TABLE A: Natural Attack Distributions ===\n\n');
fprintf('%-12s', 'Metric');
for di = 1:3, fprintf('  %-26s', disp_names{di}); end
fprintf('\n%s\n', repmat('-', 1, 92));
for mi = 1:length(show_metrics)
    fprintf('%-12s', show_labels{mi});
    for di = 1:3
        m = results_A.(domains{di}).(show_metrics{mi});
        fprintf('  %-26s', sprintf('%.4f +/- %.4f', m.mean, m.std));
    end
    fprintf('\n');
end
fprintf('\n');

fprintf('=== TABLE B: CIC Source Distribution (Controlled) ===\n\n');
fprintf('%-12s', 'Metric');
for di = 1:3, fprintf('  %-26s', disp_names{di}); end
fprintf('\n%s\n', repmat('-', 1, 92));
for mi = 1:length(show_metrics)
    fprintf('%-12s', show_labels{mi});
    for di = 1:3
        m = results_B.(domains{di}).(show_metrics{mi});
        fprintf('  %-26s', sprintf('%.4f +/- %.4f', m.mean, m.std));
    end
    fprintf('\n');
end
fprintf('\n');

%% ---- TRANSFER GAP ANALYSIS (from Table B) ------------------------------
fprintf('=== TRANSFER GAP ANALYSIS (Table B - Controlled) ===\n');
fprintf('    Positive = degradation, Negative = improvement\n\n');

src_B = results_B.cic;

% Metrics where higher is better
higher_better_map = containers.Map( ...
    {'AMR','DSR','FAR','CumulativeReward','InfectionRate','MTTD','AttackerDwellTime','DefenseCostEfficiency'}, ...
    {true, true, false, true, false, false, true, true});

fprintf('%-12s', 'Domain');
for mi = 1:length(show_metrics)
    fprintf(' %14s', show_labels{mi});
end
fprintf('\n%s\n', repmat('-', 1, 12 + 14*length(show_metrics)));

% Source row
fprintf('%-12s', 'CIC (src)');
for mi = 1:length(show_metrics)
    fprintf(' %14.4f', src_B.(show_metrics{mi}).mean);
end
fprintf('\n');

transfer_gaps = struct();

for di = 2:3
    tgt_B = results_B.(domains{di});
    fprintf('%-12s', dataset_info(di).short);
    gaps = zeros(1, length(show_metrics));
    for mi = 1:length(show_metrics)
        src_val = src_B.(show_metrics{mi}).mean;
        tgt_val = tgt_B.(show_metrics{mi}).mean;
        if higher_better_map(show_metrics{mi})
            gaps(mi) = src_val - tgt_val;
        else
            gaps(mi) = tgt_val - src_val;
        end
        fprintf(' %14.4f', tgt_val);
    end
    fprintf('\n');
    transfer_gaps.(domains{di}) = gaps;
end

fprintf('\nGaps (positive = degradation):\n');
fprintf('%-12s', 'Domain');
for mi = 1:length(show_metrics)
    fprintf(' %14s', show_labels{mi});
end
fprintf('\n%s\n', repmat('-', 1, 12 + 14*length(show_metrics)));

for di = 2:3
    gaps = transfer_gaps.(domains{di});
    fprintf('%-12s', dataset_info(di).short);
    for mi = 1:length(show_metrics)
        fprintf(' %+14.4f', gaps(mi));
    end
    fprintf('\n');
end

% Percentage gaps
fprintf('\nGaps (%% of source):\n');
fprintf('%-12s', 'Domain');
for mi = 1:length(show_metrics)
    fprintf(' %14s', show_labels{mi});
end
fprintf('\n%s\n', repmat('-', 1, 12 + 14*length(show_metrics)));

for di = 2:3
    gaps = transfer_gaps.(domains{di});
    fprintf('%-12s', dataset_info(di).short);
    for mi = 1:length(show_metrics)
        src_val = src_B.(show_metrics{mi}).mean;
        if abs(src_val) > 1e-6
            pct = (gaps(mi) / abs(src_val)) * 100;
        else
            pct = 0;
        end
        fprintf(' %+13.1f%%', pct);
    end
    fprintf('\n');
end
fprintf('\n');

%% ---- TRANSFER QUALITY SUMMARY (Table B direct comparison) ---------------
fprintf('=== TRANSFER QUALITY SUMMARY (Table B) ===\n');
fprintf('    Direct comparison: transfer domain vs source (same attack dist)\n\n');

fprintf('%-12s %10s %10s %10s %10s %10s %10s\n', ...
    'Domain', 'AMR', 'Reward', 'Infect', 'DSR', 'MTTD', 'CostEff');
fprintf('%s\n', repmat('-', 1, 72));

src_B = results_B.cic;
fprintf('%-12s %10.4f %10.2f %10.4f %10.4f %10.2f %10.2f\n', ...
    'CIC (src)', src_B.AMR.mean, src_B.CumulativeReward.mean, ...
    src_B.InfectionRate.mean, src_B.DSR.mean, src_B.MTTD.mean, ...
    src_B.DefenseCostEfficiency.mean);

for di = 2:3
    tgt = results_B.(domains{di});
    fprintf('%-12s %10.4f %10.2f %10.4f %10.4f %10.2f %10.2f\n', ...
        dataset_info(di).short, tgt.AMR.mean, tgt.CumulativeReward.mean, ...
        tgt.InfectionRate.mean, tgt.DSR.mean, tgt.MTTD.mean, ...
        tgt.DefenseCostEfficiency.mean);
end
fprintf('\n');

% Retention as percentage of source value (not improvement-over-random)
fprintf('%-12s %10s %10s %10s %10s\n', 'Domain', 'AMR_ret%', 'DSR_ret%', 'Inf_ret%', 'MTTD_ret%');
fprintf('%s\n', repmat('-', 1, 50));

retention_pct = zeros(3, 4);  % AMR, DSR, Infection, MTTD

for di = 1:3
    tgt = results_B.(domains{di});
    % AMR retention (higher is better, so tgt/src * 100)
    retention_pct(di,1) = tgt.AMR.mean / max(src_B.AMR.mean, 1e-6) * 100;
    % DSR retention (higher is better)
    retention_pct(di,2) = tgt.DSR.mean / max(src_B.DSR.mean, 1e-6) * 100;
    % Infection retention (lower is better, so src/tgt * 100)
    retention_pct(di,3) = src_B.InfectionRate.mean / max(tgt.InfectionRate.mean, 1e-6) * 100;
    % MTTD retention (lower is better, so src/tgt * 100)
    retention_pct(di,4) = src_B.MTTD.mean / max(tgt.MTTD.mean, 1e-6) * 100;
    
    fprintf('%-12s %9.1f%% %9.1f%% %9.1f%% %9.1f%%\n', ...
        dataset_info(di).short, retention_pct(di,1), retention_pct(di,2), ...
        retention_pct(di,3), retention_pct(di,4));
end
fprintf('\n');


%% ---- ATTACK DISTRIBUTION EFFECT ----------------------------------------
fprintf('=== ATTACK DISTRIBUTION EFFECT ===\n');
fprintf('    Table A (natural) minus Table B (source dist) per domain\n');
fprintf('    CIC should be ~0. Large values = distribution drives the difference.\n\n');

fprintf('%-12s %16s %16s %16s\n', 'Domain', 'AMR_A - AMR_B', 'Rew_A - Rew_B', 'Inf_A - Inf_B');
fprintf('%s\n', repmat('-', 1, 60));

for di = 1:3
    nat = results_A.(domains{di});
    src = results_B.(domains{di});
    amr_diff = nat.AMR.mean - src.AMR.mean;
    rew_diff = nat.CumulativeReward.mean - src.CumulativeReward.mean;
    inf_diff = nat.InfectionRate.mean - src.InfectionRate.mean;
    fprintf('%-12s %+16.4f %+16.2f %+16.4f\n', ...
        dataset_info(di).short, amr_diff, rew_diff, inf_diff);
end
fprintf('\n');

%% ---- STATISTICAL SIGNIFICANCE -------------------------------------------
fprintf('=== STATISTICAL SIGNIFICANCE ===\n\n');

fprintf('Table B (Controlled - CIC dist on all domains):\n');
fprintf('  Wilcoxon rank-sum: CIC vs each transfer domain\n\n');

src_raw_B = results_B.cic.raw;

col_labels = {'AMR','DSR','FAR','Reward','InfRate','MTTD','Dwell','CostEff'};
fprintf('%-12s', 'Domain');
for mi = 1:length(col_labels)
    fprintf('  %12s', col_labels{mi});
end
fprintf('\n%s\n', repmat('-', 1, 12 + 14*length(col_labels)));

for di = 2:3
    tgt_raw = results_B.(domains{di}).raw;
    fprintf('%-12s', dataset_info(di).short);
    for mi = 1:8
        p = ranksum(src_raw_B(:, mi), tgt_raw(:, mi));
        fprintf('  %7.4f %4s', p, sig_str(p));
    end
    fprintf('\n');
end

fprintf('\nTable A (Natural distributions):\n');
src_raw_A = results_A.cic.raw;
fprintf('%-12s', 'Domain');
for mi = 1:length(col_labels)
    fprintf('  %12s', col_labels{mi});
end
fprintf('\n%s\n', repmat('-', 1, 12 + 14*length(col_labels)));

for di = 2:3
    tgt_raw = results_A.(domains{di}).raw;
    fprintf('%-12s', dataset_info(di).short);
    for mi = 1:8
        p = ranksum(src_raw_A(:, mi), tgt_raw(:, mi));
        fprintf('  %7.4f %4s', p, sig_str(p));
    end
    fprintf('\n');
end
fprintf('\n');

%% ---- RISK ANALYSIS ------------------------------------------------------
fprintf('=== RISK ANALYSIS (CVaR, Dispersion) ===\n\n');

fprintf('Table A (Natural):\n');
fprintf('%-12s %12s %12s %12s %12s\n', 'Domain', 'CVaR_005', 'Rew_IQR', 'AMR_IQR', 'Inf_IQR');
fprintf('%s\n', repmat('-', 1, 60));
for di = 1:3
    r = results_A.(domains{di});
    fprintf('%-12s %12.2f %12.2f %12.4f %12.4f\n', ...
        dataset_info(di).short, r.CVaR_005, r.DR, ...
        iqr(r.raw(:,1)), iqr(r.raw(:,5)));
end

fprintf('\nTable B (Source dist):\n');
fprintf('%-12s %12s %12s %12s %12s\n', 'Domain', 'CVaR_005', 'Rew_IQR', 'AMR_IQR', 'Inf_IQR');
fprintf('%s\n', repmat('-', 1, 60));
for di = 1:3
    r = results_B.(domains{di});
    fprintf('%-12s %12.2f %12.2f %12.4f %12.4f\n', ...
        dataset_info(di).short, r.CVaR_005, r.DR, ...
        iqr(r.raw(:,1)), iqr(r.raw(:,5)));
end
fprintf('\n');

%% ---- COMPOSITE TRANSFER SCORE ------------------------------------------
fprintf('=== COMPOSITE TRANSFER SCORE ===\n\n');

% Weights: AMR 40%, Infection 30%, DSR 20%, MTTD 10%
composite_weights = [0.40, 0.20, 0.30, 0.10];

fprintf('%-12s %10s %10s %10s %10s %12s %10s\n', ...
    'Domain', 'AMR_ret', 'DSR_ret', 'Inf_ret', 'MTTD_ret', 'Composite', 'Quality');
fprintf('%s\n', repmat('-', 1, 74));

composite_scores = zeros(3,1);

for di = 1:3
    ret = retention_pct(di,:) / 100;  % Convert to fraction
    composite = sum(ret .* composite_weights);
    composite_scores(di) = composite;
    
    if composite >= 0.95,     quality = 'Excellent';
    elseif composite >= 0.85, quality = 'Good';
    elseif composite >= 0.70, quality = 'Moderate';
    elseif composite >= 0.50, quality = 'Poor';
    else,                     quality = 'Failed';
    end
    
    fprintf('%-12s %9.1f%% %9.1f%% %9.1f%% %9.1f%% %12.4f %10s\n', ...
        dataset_info(di).short, retention_pct(di,1), retention_pct(di,2), ...
        retention_pct(di,3), retention_pct(di,4), composite, quality);
end
fprintf('\n');

%% ---- KEY FINDINGS -------------------------------------------------------
fprintf('=== KEY FINDINGS ===\n\n');

fprintf('1. CONTROLLED TRANSFER (Table B - same CIC attack distribution):\n');
for di = 2:3
    gaps = transfer_gaps.(domains{di});
    amr_gap_pct = 0;
    src_amr_val = src_B.AMR.mean;
    if abs(src_amr_val) > 1e-6
        amr_gap_pct = (gaps(1) / src_amr_val) * 100;
    end
    if gaps(1) > 0
        fprintf('   %s: AMR degrades by %.4f (%.1f%%) - expected transfer cost.\n', ...
            dataset_info(di).short, gaps(1), amr_gap_pct);
    else
        fprintf('   %s: AMR improves by %.4f (%.1f%%) on transfer domain.\n', ...
            dataset_info(di).short, abs(gaps(1)), abs(amr_gap_pct));
    end
end
fprintf('\n');

fprintf('2. ATTACK DISTRIBUTION EFFECT:\n');
for di = 2:3
    nat_amr = results_A.(domains{di}).AMR.mean;
    src_amr_B = results_B.(domains{di}).AMR.mean;
    diff = nat_amr - src_amr_B;
    total_diff = results_A.(domains{di}).AMR.mean - results_A.cic.AMR.mean;
    if abs(total_diff) > 1e-6
        pct_explained = abs(diff) / abs(total_diff) * 100;
    else
        pct_explained = 0;
    end
    if abs(diff) > 0.01
        fprintf('   %s: Attack distribution accounts for %.4f AMR difference (%.1f%% of total).\n', ...
            dataset_info(di).short, abs(diff), min(pct_explained, 100));
    else
        fprintf('   %s: Attack distribution has minimal effect (%.4f AMR).\n', ...
            dataset_info(di).short, abs(diff));
    end
end
fprintf('\n');

fprintf('3. TRANSFER RETENTION (Table B, direct):\n');
for di = 2:3
    avg_ret = mean(retention_pct(di,:));
    fprintf('   %s: Average metric retention %.1f%%\n', dataset_info(di).short, avg_ret);
end
fprintf('\n');

fprintf('4. RISK CONSISTENCY:\n');
for di = 1:3
    r = results_B.(domains{di});
    fprintf('   %s: CVaR(0.05) = %.2f, Reward std = %.2f\n', ...
        dataset_info(di).short, r.CVaR_005, r.CumulativeReward.std);
end
fprintf('\n');

avg_composite = mean(composite_scores(2:3));
fprintf('5. OVERALL TRANSFER QUALITY:\n');
fprintf('   Average composite (transfer domains): %.4f\n', avg_composite);
if avg_composite >= 0.95
    fprintf('   CONCLUSION: Excellent cross-domain transfer (>95%% retention).\n');
elseif avg_composite >= 0.85
    fprintf('   CONCLUSION: Good cross-domain transfer (85-95%% retention).\n');
elseif avg_composite >= 0.70
    fprintf('   CONCLUSION: Moderate transfer (70-85%%). Fine-tuning may help.\n');
else
    fprintf('   CONCLUSION: Significant degradation. Domain-specific tuning needed.\n');
end
fprintf('\n');

%% ---- SAVE RESULTS -------------------------------------------------------
total_time = toc(phase6_start);

transfer_results = struct();
transfer_results.results_A = results_A;
transfer_results.results_B = results_B;
transfer_results.random_baseline = random_baseline;
transfer_results.transfer_gaps = transfer_gaps;
transfer_results.retention_pct = retention_pct;
transfer_results.composite_scores = composite_scores;
transfer_results.source_metrics = source_metrics;
transfer_results.dataset_info = dataset_info;
transfer_results.attack_distributions = [cic_dist; wustl_dist; edge_dist];
transfer_results.n_eval = n_eval;
transfer_results.total_time = total_time;
transfer_results.timestamp = char(datetime('now'));

save(fullfile(results_dir, 'transfer_results.mat'), '-struct', 'transfer_results');
fprintf('Results saved: %s\n', fullfile(results_dir, 'transfer_results.mat'));

%% ---- WRITE REPORT FILE -------------------------------------------------
fid = fopen(fullfile(phase6_dir, 'transfer_report.txt'), 'w');
fprintf(fid, '================================================================\n');
fprintf(fid, '  CoADAM Phase 6: Cross-Domain Transfer Report (REVISED)\n');
fprintf(fid, '  Generated: %s\n', char(datetime('now')));
fprintf(fid, '  Total time: %.1f s (%.1f min)\n', total_time, total_time/60);
fprintf(fid, '================================================================\n\n');

fprintf(fid, '1. CONFIGURATION\n');
fprintf(fid, '   Episodes per dataset per mode: %d\n', n_eval);
fprintf(fid, '   Max steps: %d\n', max_steps);
fprintf(fid, '   Defender: CoADAM DQN (12-128-64-4)\n');
fprintf(fid, '   Attacker: Trained Q-table (%d x %d)\n', size(atk_Q,1), size(atk_Q,2));
fprintf(fid, '   Modes: (A) Natural attack dist, (B) CIC source dist\n\n');

fprintf(fid, '2. ATTACK DISTRIBUTIONS\n');
fprintf(fid, '   %-12s  Recon   InitAcc  Exec    LatMov  Impact\n', 'Dataset');
fprintf(fid, '   %s\n', repmat('-', 1, 65));
for di = 1:3
    fprintf(fid, '   %-12s  %.3f   %.3f    %.3f   %.3f   %.3f\n', ...
        dataset_info(di).short, dataset_info(di).attack_dist);
end
fprintf(fid, '\n');

fprintf(fid, '3. RANDOM BASELINE (difficulty calibration)\n');
for di = 1:3
    rb = random_baseline.(domains{di});
    fprintf(fid, '   %-12s: AMR=%.4f, Reward=%.2f, Infection=%.4f\n', ...
        dataset_info(di).short, rb.AMR, rb.Reward, rb.InfectionRate);
end
fprintf(fid, '\n');

fprintf(fid, '4. TABLE A: NATURAL ATTACK DISTRIBUTIONS\n\n');
fprintf(fid, '   %-12s', 'Metric');
for di = 1:3, fprintf(fid, '  %-26s', disp_names{di}); end
fprintf(fid, '\n   %s\n', repmat('-', 1, 90));
for mi = 1:length(show_metrics)
    fprintf(fid, '   %-12s', show_labels{mi});
    for di = 1:3
        m = results_A.(domains{di}).(show_metrics{mi});
        fprintf(fid, '  %-26s', sprintf('%.4f+/-%.4f', m.mean, m.std));
    end
    fprintf(fid, '\n');
end
fprintf(fid, '\n');

fprintf(fid, '5. TABLE B: CIC SOURCE DISTRIBUTION (CONTROLLED)\n\n');
fprintf(fid, '   %-12s', 'Metric');
for di = 1:3, fprintf(fid, '  %-26s', disp_names{di}); end
fprintf(fid, '\n   %s\n', repmat('-', 1, 90));
for mi = 1:length(show_metrics)
    fprintf(fid, '   %-12s', show_labels{mi});
    for di = 1:3
        m = results_B.(domains{di}).(show_metrics{mi});
        fprintf(fid, '  %-26s', sprintf('%.4f+/-%.4f', m.mean, m.std));
    end
    fprintf(fid, '\n');
end
fprintf(fid, '\n');

fprintf(fid, '6. TRANSFER GAP (Table B, positive = degradation)\n\n');
fprintf(fid, '   %-12s', 'Domain');
for mi = 1:length(show_labels)
    fprintf(fid, ' %14s', show_labels{mi});
end
fprintf(fid, '\n   %s\n', repmat('-', 1, 12 + 14*length(show_labels)));
for di = 2:3
    gaps = transfer_gaps.(domains{di});
    fprintf(fid, '   %-12s', dataset_info(di).short);
    for mi = 1:length(gaps)
        fprintf(fid, ' %+14.4f', gaps(mi));
    end
    fprintf(fid, '\n');
end
fprintf(fid, '\n');

fprintf(fid, '7. TRANSFER RETENTION (Table B, direct comparison)\n\n');
fprintf(fid, '   %-12s %10s %10s %10s %10s %10s\n', ...
    'Domain', 'AMR', 'DSR', 'Infect', 'MTTD', 'Average');
fprintf(fid, '   %s\n', repmat('-', 1, 62));
for di = 1:3
    avg_ret = mean(retention_pct(di,:));
    fprintf(fid, '   %-12s %9.1f%% %9.1f%% %9.1f%% %9.1f%% %9.1f%%\n', ...
        dataset_info(di).short, retention_pct(di,1), retention_pct(di,2), ...
        retention_pct(di,3), retention_pct(di,4), avg_ret);
end
fprintf(fid, '\n');

fprintf(fid, '8. COMPOSITE TRANSFER SCORE\n\n');
for di = 1:3
    ret = retention_pct(di,:) / 100;
    composite = sum(ret .* composite_weights);
    if composite >= 0.90,     quality = 'Excellent';
    elseif composite >= 0.75, quality = 'Good';
    elseif composite >= 0.60, quality = 'Moderate';
    elseif composite >= 0.40, quality = 'Poor';
    else,                     quality = 'Failed';
    end
    fprintf(fid, '   %-12s: Composite=%.4f (%s)\n', dataset_info(di).short, composite, quality);
end
fprintf(fid, '\n');

fprintf(fid, '9. STATISTICAL SIGNIFICANCE (Wilcoxon, Table B)\n\n');
for di = 2:3
    tgt_raw = results_B.(domains{di}).raw;
    p_rew = ranksum(src_raw_B(:,4), tgt_raw(:,4));
    p_amr = ranksum(src_raw_B(:,1), tgt_raw(:,1));
    fprintf(fid, '   CIC vs %s:\n', dataset_info(di).short);
    fprintf(fid, '     Reward: p=%.6f %s\n', p_rew, sig_str(p_rew));
    fprintf(fid, '     AMR:    p=%.6f %s\n\n', p_amr, sig_str(p_amr));
end

fprintf(fid, '10. KEY FINDINGS\n\n');
fprintf(fid, '   Average composite retention (transfer): %.4f\n', avg_composite);
if avg_composite >= 0.80
    fprintf(fid, '   CONCLUSION: Strong cross-domain transfer.\n');
elseif avg_composite >= 0.65
    fprintf(fid, '   CONCLUSION: Moderate transfer. Fine-tuning recommended.\n');
else
    fprintf(fid, '   CONCLUSION: Significant degradation. Domain-specific tuning needed.\n');
end

fclose(fid);
fprintf('Report saved: %s\n', fullfile(phase6_dir, 'transfer_report.txt'));
fprintf('\n=== Phase 6 Complete (%.1f s) ===\n', total_time);

%% ---- HELPER FUNCTIONS ---------------------------------------------------
function s = sig_str(p)
    if p < 0.001, s = '(***)';
    elseif p < 0.01, s = '(**)';
    elseif p < 0.05, s = '(*)';
    else, s = '(n.s.)';
    end
end
