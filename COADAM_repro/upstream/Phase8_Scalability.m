%% ========================================================================
%  CoADAM Phase 8: Multi-Scale Evaluation Engine
%  Tests CoADAM performance across network scales
%  Evaluates scalability of learned defense policy
%  Four evaluation combos per scale:
%    1. CoADAM vs Adaptive attacker
%    2. CoADAM vs Random attacker
%    3. Random defender vs Adaptive attacker
%    4. Random defender vs Random attacker
%  Date: 28-Feb-2026
%  ========================================================================
clear; clc;
fprintf('=== CoADAM Phase 8: Multi-Scale Evaluation ===\n');
fprintf('Started: %s\n\n', char(datetime('now')));
phase8_start = tic;

%% ---- Paths -------------------------------------------------------------
project_root  = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
results_dir   = fullfile(project_root, 'results');
phase2_dir    = fullfile(project_root, 'phase2_environment');
phase8_dir    = fullfile(project_root, 'phase8_scalability');

if ~exist(phase8_dir, 'dir'), mkdir(phase8_dir); end
if ~exist(results_dir, 'dir'), mkdir(results_dir); end
addpath(phase2_dir);

%% ---- Load config and trained models ------------------------------------
fprintf('[1] Loading config and trained models...\n');
load(fullfile(processed_dir, 'environment_config.mat'), 'config');

trained = load(fullfile(results_dir, 'dqn_cotraining_results.mat'), ...
    'W1', 'W2', 'W3', 'b1', 'b2', 'b3', 'atk_Q');

W1 = trained.W1; W2 = trained.W2; W3 = trained.W3;
b1 = trained.b1; b2 = trained.b2; b3 = trained.b3;
atk_Q = trained.atk_Q;

atk_bins = config.attacker_state.n_bins;
n_eval = 200;
max_steps = config.episode.max_steps;

fprintf('    DQN [%dx%d]->[%dx%d]->[%dx%d]\n', ...
    size(W1,1),size(W1,2), size(W2,1),size(W2,2), size(W3,1),size(W3,2));
fprintf('    Training scale: %d devices\n\n', config.network.default_n_devices);

%% ---- Define scale levels ------------------------------------------------
scale_levels = [50, 100, 200, 500, 1000];
n_scales = length(scale_levels);
training_scale = config.network.default_n_devices;  % 100

fprintf('[2] Scale levels: ');
for si = 1:n_scales
    if scale_levels(si) == training_scale
        fprintf('%d (trained) ', scale_levels(si));
    else
        fprintf('%d ', scale_levels(si));
    end
end
fprintf('\n');
fprintf('    Evaluation: %d episodes per combo per scale\n\n', n_eval);

%% ---- Multi-scale evaluation (4 combos per scale) -----------------------
fprintf('[3] Running multi-scale evaluation...\n\n');

scale_results      = struct();  % CoADAM vs Adaptive
random_results     = struct();  % Random def vs Adaptive
coadam_vs_rand_atk = struct();  % CoADAM vs Random atk
random_vs_rand     = struct();  % Random def vs Random atk

rng(42);  % Set once before the loop
for si = 1:n_scales
    scale = scale_levels(si);
    ...
    fprintf('--- Scale: %d devices ---\n', scale);
    scale_start = tic;   
    
    % Modify config for this scale
    scale_config = config;
    scale_config.network.default_n_devices = scale;
    
    % Scale is handled inside iiot_environment via n_devices
    fprintf('    Scale factors: spread=%.2f, detect=%.2f, recovery=%.2f\n', ...
        sqrt(scale / training_scale), ...
        1 / sqrt(scale / training_scale), ...
        (scale / training_scale) ^ (-0.3));
    
    metric_names = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
        'MTTD','AttackerDwellTime','DefenseCostEfficiency'};
    
    % ============ Combo 1: CoADAM vs ADAPTIVE attacker ============
    ep_metrics_adapt = zeros(n_eval, 8);
    ep_times = zeros(n_eval, 1);
    
    for ep = 1:n_eval
        ep_start = tic;
        env = iiot_environment(scale_config);
        [def_state, atk_state] = env.reset();
        
        for step = 1:max_steps
            s = def_state(:);
            h1 = max(0, W1 * s + b1);
            h2 = max(0, W2 * h1 + b2);
            q_vals = W3 * h2 + b3;
            [~, def_action] = max(q_vals);
            
            atk_idx = env.discretize_state(atk_state, atk_bins);
            [~, atk_action] = max(atk_Q(atk_idx, :));
            
            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env.get_episode_metrics();
        ep_metrics_adapt(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, m.DefenseCostEfficiency];
        ep_times(ep) = toc(ep_start);
    end
    
    % ============ Combo 2: CoADAM vs RANDOM attacker ============
    ep_metrics_rand_atk = zeros(n_eval, 8);
    
    for ep = 1:n_eval
        env = iiot_environment(scale_config);
        [def_state, atk_state] = env.reset();
        
        for step = 1:max_steps
            s = def_state(:);
            h1 = max(0, W1 * s + b1);
            h2 = max(0, W2 * h1 + b2);
            q_vals = W3 * h2 + b3;
            [~, def_action] = max(q_vals);
            
            atk_action = randi(config.n_attacker_actions);
            
            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env.get_episode_metrics();
        ep_metrics_rand_atk(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, m.DefenseCostEfficiency];
    end
    
    % ============ Combo 3: RANDOM defender vs ADAPTIVE attacker ============
    rand_metrics_adapt = zeros(n_eval, 8);
    
    for ep = 1:n_eval
        env_r = iiot_environment(scale_config);
        [def_state, atk_state] = env_r.reset();
        
        for step = 1:max_steps
            def_action = randi(config.n_defender_actions);
            
            atk_idx = env_r.discretize_state(atk_state, atk_bins);
            [~, atk_action] = max(atk_Q(atk_idx, :));
            
            [def_state, atk_state, ~, ~, done, ~] = env_r.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env_r.get_episode_metrics();
        rand_metrics_adapt(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, m.DefenseCostEfficiency];
    end
    
    % ============ Combo 4: RANDOM defender vs RANDOM attacker ============
    rand_metrics_rand = zeros(n_eval, 8);
    
    for ep = 1:n_eval
        env_r = iiot_environment(scale_config);
        [def_state, atk_state] = env_r.reset();
        
        for step = 1:max_steps
            def_action = randi(config.n_defender_actions);
            atk_action = randi(config.n_attacker_actions);
            
            [def_state, atk_state, ~, ~, done, ~] = env_r.step(def_action, atk_action);
            if done, break; end
        end
        
        m = env_r.get_episode_metrics();
        rand_metrics_rand(ep,:) = [m.AMR, m.DSR, m.FAR, m.CumulativeReward, ...
            m.InfectionRate, m.MTTD, m.AttackerDwellTime, m.DefenseCostEfficiency];
    end
    
    % ============ Aggregate ============
    
    % CoADAM vs Adaptive
    sr = struct();
    sr.scale = scale;
    sr.spread_rate = scale_config.network.infection_spread_rate;
    sr.budget = scale_config.episode.initial_budget_remaining;
    for mi = 1:length(metric_names)
        arr = ep_metrics_adapt(:, mi);
        sr.(metric_names{mi}) = struct( ...
            'mean', mean(arr), 'std', std(arr), ...
            'min', min(arr), 'max', max(arr), ...
            'median', median(arr), 'raw', arr);
    end
    sorted_rew = sort(ep_metrics_adapt(:,4), 'ascend');
    n_tail = max(1, floor(0.05 * n_eval));
    sr.CVaR_005 = mean(sorted_rew(1:n_tail));
    sr.DR = iqr(ep_metrics_adapt(:,4));
    sr.mean_ep_time = mean(ep_times);
    sr.total_time = toc(scale_start);
    scale_results.(sprintf('s%d', scale)) = sr;
    
    % CoADAM vs Random attacker
    sr_rand_atk = struct();
    sr_rand_atk.scale = scale;
    for mi = 1:length(metric_names)
        arr = ep_metrics_rand_atk(:, mi);
        sr_rand_atk.(metric_names{mi}) = struct( ...
            'mean', mean(arr), 'std', std(arr), 'raw', arr);
    end
    coadam_vs_rand_atk.(sprintf('s%d', scale)) = sr_rand_atk;
    
    % Random def vs Adaptive
    rr_adapt = struct();
    rr_adapt.scale = scale;
    for mi = 1:length(metric_names)
        rr_adapt.(metric_names{mi}) = struct('mean', mean(rand_metrics_adapt(:,mi)), ...
            'std', std(rand_metrics_adapt(:,mi)), 'raw', rand_metrics_adapt(:,mi));
    end
    random_results.(sprintf('s%d', scale)) = rr_adapt;
    
    % Random def vs Random atk
    rr_rand = struct();
    rr_rand.scale = scale;
    for mi = 1:length(metric_names)
        rr_rand.(metric_names{mi}) = struct('mean', mean(rand_metrics_rand(:,mi)), ...
            'std', std(rand_metrics_rand(:,mi)), 'raw', rand_metrics_rand(:,mi));
    end
    random_vs_rand.(sprintf('s%d', scale)) = rr_rand;
    
    fprintf('    CoADAM vs Adaptive:  AMR=%.4f, Reward=%.2f, Inf=%.4f\n', ...
        sr.AMR.mean, sr.CumulativeReward.mean, sr.InfectionRate.mean);
    fprintf('    CoADAM vs Random:    AMR=%.4f, Reward=%.2f, Inf=%.4f\n', ...
        sr_rand_atk.AMR.mean, sr_rand_atk.CumulativeReward.mean, sr_rand_atk.InfectionRate.mean);
    fprintf('    Random vs Adaptive:  AMR=%.4f, Reward=%.2f, Inf=%.4f\n', ...
        rr_adapt.AMR.mean, rr_adapt.CumulativeReward.mean, rr_adapt.InfectionRate.mean);
    fprintf('    Random vs Random:    AMR=%.4f, Reward=%.2f, Inf=%.4f\n', ...
        rr_rand.AMR.mean, rr_rand.CumulativeReward.mean, rr_rand.InfectionRate.mean);
    fprintf('    Ep time: %.4f s | Total: %.1f s\n\n', sr.mean_ep_time, sr.total_time);
end

%% ---- Scale comparison tables --------------------------------------------
fprintf('==============================================================\n');
fprintf('  SCALABILITY RESULTS\n');
fprintf('==============================================================\n\n');

show_labels = {'AMR','DSR','FAR','Reward','Infection','MTTD','Dwell','CostEff'};

fprintf('TABLE 1: CoADAM vs Adaptive Attacker (hardest scenario)\n\n');
fprintf('%-8s', 'Scale');
for mi = 1:length(show_labels)
    fprintf(' %10s', show_labels{mi});
end
fprintf(' %10s\n', 'Ep_Time');
fprintf('%s\n', repmat('-', 1, 8 + 10*length(show_labels) + 10));

for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    if scale_levels(si) == training_scale
        label = sprintf('%d*', scale_levels(si));
    else
        label = sprintf('%d', scale_levels(si));
    end
    fprintf('%-8s', label);
    fprintf(' %10.4f', sr.AMR.mean);
    fprintf(' %10.4f', sr.DSR.mean);
    fprintf(' %10.4f', sr.FAR.mean);
    fprintf(' %10.2f', sr.CumulativeReward.mean);
    fprintf(' %10.4f', sr.InfectionRate.mean);
    fprintf(' %10.2f', sr.MTTD.mean);
    fprintf(' %10.2f', sr.AttackerDwellTime.mean);
    fprintf(' %10.2f', sr.DefenseCostEfficiency.mean);
    fprintf(' %10.4f', sr.mean_ep_time);
    fprintf('\n');
end
fprintf('(* = training scale)\n\n');

fprintf('TABLE 2: CoADAM vs Random Attacker (fair comparison)\n\n');
fprintf('%-8s %10s %10s %10s %10s\n', 'Scale', 'AMR', 'Reward', 'Infection', 'DSR');
fprintf('%s\n', repmat('-', 1, 48));
for si = 1:n_scales
    cr = coadam_vs_rand_atk.(sprintf('s%d', scale_levels(si)));
    fprintf('%-8d %10.4f %10.2f %10.4f %10.4f\n', ...
        scale_levels(si), cr.AMR.mean, cr.CumulativeReward.mean, ...
        cr.InfectionRate.mean, cr.DSR.mean);
end
fprintf('\n');

fprintf('TABLE 3: Random Defender vs Random Attacker (baseline)\n\n');
fprintf('%-8s %10s %10s %10s\n', 'Scale', 'AMR', 'Reward', 'Infection');
fprintf('%s\n', repmat('-', 1, 40));
for si = 1:n_scales
    rr = random_vs_rand.(sprintf('s%d', scale_levels(si)));
    fprintf('%-8d %10.4f %10.2f %10.4f\n', ...
        scale_levels(si), rr.AMR.mean, rr.CumulativeReward.mean, rr.InfectionRate.mean);
end
fprintf('\n');

%% ---- Advantage: CoADAM vs Random (both against random attacker) ---------
fprintf('=== CoADAM Advantage Over Random (both vs Random Attacker) ===\n');
fprintf('    (FAIR comparison - same attacker for both defenders)\n\n');

fprintf('%-8s %10s %10s %10s %10s\n', 'Scale', 'AMR_adv', 'Rew_adv', 'Inf_red', 'DSR_adv');
fprintf('%s\n', repmat('-', 1, 48));

advantage_fair = zeros(n_scales, 4);

for si = 1:n_scales
    cr = coadam_vs_rand_atk.(sprintf('s%d', scale_levels(si)));
    rr = random_vs_rand.(sprintf('s%d', scale_levels(si)));
    
    advantage_fair(si,1) = cr.AMR.mean - rr.AMR.mean;
    advantage_fair(si,2) = cr.CumulativeReward.mean - rr.CumulativeReward.mean;
    advantage_fair(si,3) = rr.InfectionRate.mean - cr.InfectionRate.mean;  % positive = CoADAM better
    advantage_fair(si,4) = cr.DSR.mean - rr.DSR.mean;
    
    fprintf('%-8d %+10.4f %+10.2f %+10.4f %+10.4f\n', ...
        scale_levels(si), advantage_fair(si,1), advantage_fair(si,2), ...
        advantage_fair(si,3), advantage_fair(si,4));
end
fprintf('\n');

%% ---- Advantage: CoADAM vs Random (both against adaptive attacker) -------
fprintf('=== CoADAM Advantage Over Random (both vs Adaptive Attacker) ===\n');
fprintf('    (ADVERSARIAL comparison - adaptive attacker exploits weaknesses)\n\n');

fprintf('%-8s %10s %10s %10s %10s\n', 'Scale', 'AMR_adv', 'Rew_adv', 'Inf_red', 'DSR_adv');
fprintf('%s\n', repmat('-', 1, 48));

advantage_adapt = zeros(n_scales, 4);

for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    rr = random_results.(sprintf('s%d', scale_levels(si)));
    
    advantage_adapt(si,1) = sr.AMR.mean - rr.AMR.mean;
    advantage_adapt(si,2) = sr.CumulativeReward.mean - rr.CumulativeReward.mean;
    advantage_adapt(si,3) = rr.InfectionRate.mean - sr.InfectionRate.mean;
    advantage_adapt(si,4) = sr.DSR.mean - rr.DSR.mean;
    
    fprintf('%-8d %+10.4f %+10.2f %+10.4f %+10.4f\n', ...
        scale_levels(si), advantage_adapt(si,1), advantage_adapt(si,2), ...
        advantage_adapt(si,3), advantage_adapt(si,4));
end
fprintf('\n');

%% ---- Performance relative to training scale -----------------------------
fprintf('=== Performance Relative to Training Scale (%d devices) ===\n\n', training_scale);

train_idx = find(scale_levels == training_scale);
train_sr = scale_results.(sprintf('s%d', training_scale));

fprintf('%-8s %10s %10s %10s %10s %10s\n', ...
    'Scale', 'AMR_ret%', 'Rew_chg', 'Inf_ret%', 'DSR_ret%', 'MTTD_ret%');
fprintf('%s\n', repmat('-', 1, 58));

retention = zeros(n_scales, 4);

for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    
    amr_ret = sr.AMR.mean / max(train_sr.AMR.mean, 0.001) * 100;
    inf_ret = train_sr.InfectionRate.mean / max(sr.InfectionRate.mean, 0.001) * 100;
    dsr_ret = sr.DSR.mean / max(train_sr.DSR.mean, 0.001) * 100;
    mttd_ret = train_sr.MTTD.mean / max(sr.MTTD.mean, 0.001) * 100;
    
    rew_chg = sr.CumulativeReward.mean - train_sr.CumulativeReward.mean;
    
    retention(si,:) = [amr_ret, inf_ret, dsr_ret, mttd_ret];
    
    fprintf('%-8d %9.1f%% %+10.2f %9.1f%% %9.1f%% %9.1f%%\n', ...
        scale_levels(si), amr_ret, rew_chg, inf_ret, dsr_ret, mttd_ret);
end
fprintf('\n');

%% ---- Statistical significance across scales -----------------------------
fprintf('=== Statistical Significance (vs Training Scale) ===\n\n');

train_raw = scale_results.(sprintf('s%d', training_scale));

fprintf('%-8s %16s %16s %16s\n', 'Scale', 'Reward p', 'AMR p', 'Infection p');
fprintf('%s\n', repmat('-', 1, 56));

for si = 1:n_scales
    if scale_levels(si) == training_scale
        fprintf('%-8d %16s %16s %16s\n', scale_levels(si), '(baseline)', '(baseline)', '(baseline)');
        continue;
    end
    
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    p_rew = ranksum(train_raw.CumulativeReward.raw, sr.CumulativeReward.raw);
    p_amr = ranksum(train_raw.AMR.raw, sr.AMR.raw);
    p_inf = ranksum(train_raw.InfectionRate.raw, sr.InfectionRate.raw);
    
    fprintf('%-8d %8.4f %-6s %8.4f %-6s %8.4f %-6s\n', ...
        scale_levels(si), p_rew, sig_str(p_rew), p_amr, sig_str(p_amr), ...
        p_inf, sig_str(p_inf));
end
fprintf('\n');

%% ---- Statistical significance: Fair comparison --------------------------
fprintf('=== Statistical Significance (Fair: CoADAM vs Random, both vs Random Atk) ===\n\n');

fprintf('%-8s %16s %16s %16s\n', 'Scale', 'Reward p', 'AMR p', 'Infection p');
fprintf('%s\n', repmat('-', 1, 56));

for si = 1:n_scales
    cr = coadam_vs_rand_atk.(sprintf('s%d', scale_levels(si)));
    rvr = random_vs_rand.(sprintf('s%d', scale_levels(si)));
    
    p_rew = ranksum(cr.CumulativeReward.raw, rvr.CumulativeReward.raw);
    p_amr = ranksum(cr.AMR.raw, rvr.AMR.raw);
    p_inf = ranksum(cr.InfectionRate.raw, rvr.InfectionRate.raw);
    
    fprintf('%-8d %8.4f %-6s %8.4f %-6s %8.4f %-6s\n', ...
        scale_levels(si), p_rew, sig_str(p_rew), p_amr, sig_str(p_amr), ...
        p_inf, sig_str(p_inf));
end
fprintf('\n');

%% ---- Risk across scales -------------------------------------------------
fprintf('=== Risk Analysis Across Scales ===\n\n');

fprintf('%-8s %12s %12s %12s %12s\n', 'Scale', 'CVaR_005', 'Rew_IQR', 'Rew_Std', 'AMR_Std');
fprintf('%s\n', repmat('-', 1, 56));

for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    fprintf('%-8d %12.2f %12.2f %12.2f %12.4f\n', ...
        scale_levels(si), sr.CVaR_005, sr.DR, sr.CumulativeReward.std, sr.AMR.std);
end
fprintf('\n');

%% ---- Computational scalability ------------------------------------------
fprintf('=== Computational Scalability ===\n\n');

fprintf('%-8s %12s %12s %12s\n', 'Scale', 'Ep_Time(s)', 'Relative', 'Throughput');
fprintf('%s\n', repmat('-', 1, 44));

train_time = scale_results.(sprintf('s%d', training_scale)).mean_ep_time;

for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    relative = sr.mean_ep_time / max(train_time, 0.0001);
    throughput = 1 / max(sr.mean_ep_time, 0.0001);
    fprintf('%-8d %12.4f %11.2fx %10.1f ep/s\n', ...
        scale_levels(si), sr.mean_ep_time, relative, throughput);
end
fprintf('\n');

%% ---- Scalability score --------------------------------------------------
fprintf('=== Scalability Score ===\n\n');

fprintf('%-8s %10s %10s %10s %10s %12s %10s\n', ...
    'Scale', 'AMR_ret', 'Inf_ret', 'DSR_ret', 'MTTD_ret', 'Composite', 'Quality');
fprintf('%s\n', repmat('-', 1, 70));

composite_weights = [0.40, 0.30, 0.20, 0.10];
scalability_scores = zeros(n_scales, 1);

for si = 1:n_scales
    ret = retention(si,:) / 100;
    composite = sum([ret(1), ret(2), ret(3), ret(4)] .* composite_weights);
    scalability_scores(si) = composite;
    
    if composite >= 0.95,     quality = 'Excellent';
    elseif composite >= 0.85, quality = 'Good';
    elseif composite >= 0.70, quality = 'Moderate';
    elseif composite >= 0.50, quality = 'Poor';
    else,                     quality = 'Failed';
    end
    
    fprintf('%-8d %9.1f%% %9.1f%% %9.1f%% %9.1f%% %12.4f %10s\n', ...
        scale_levels(si), retention(si,1), retention(si,2), ...
        retention(si,3), retention(si,4), composite, quality);
end
fprintf('\n');

%% ---- Key findings -------------------------------------------------------
fprintf('=== KEY FINDINGS ===\n\n');

non_train = setdiff(1:n_scales, train_idx);
[worst_composite, worst_idx] = min(scalability_scores(non_train));
worst_scale = scale_levels(non_train(worst_idx));
[best_composite, best_idx] = max(scalability_scores(non_train));
best_scale = scale_levels(non_train(best_idx));

fprintf('1. SCALE RANGE: Tested %d to %d devices (%.0fx range)\n', ...
    min(scale_levels), max(scale_levels), max(scale_levels)/min(scale_levels));
fprintf('   Training scale: %d devices\n\n', training_scale);

fprintf('2. BEST TRANSFER: %d devices (composite=%.4f)\n', best_scale, best_composite);
fprintf('   WORST TRANSFER: %d devices (composite=%.4f)\n\n', worst_scale, worst_composite);

amr_vals = zeros(1, n_scales);
for si = 1:n_scales
    amr_vals(si) = scale_results.(sprintf('s%d', scale_levels(si))).AMR.mean;
end
fprintf('3. AMR TREND: ');
for si = 1:n_scales
    if si > 1, fprintf(' -> '); end
    fprintf('%.3f(%d)', amr_vals(si), scale_levels(si));
end
fprintf('\n');
amr_range = max(amr_vals) - min(amr_vals);
fprintf('   AMR range: %.4f (%.1f%% variation)\n\n', amr_range, ...
    amr_range / mean(amr_vals) * 100);

fprintf('4. FAIR ADVANTAGE (both vs Random Attacker):\n');
n_amr_wins_fair = 0;
n_inf_wins_fair = 0;
for si = 1:n_scales
    fprintf('   %d devices: AMR %+.4f, Reward %+.2f, InfReduct %+.4f, DSR %+.4f\n', ...
        scale_levels(si), advantage_fair(si,1), advantage_fair(si,2), ...
        advantage_fair(si,3), advantage_fair(si,4));
    if advantage_fair(si,1) > 0, n_amr_wins_fair = n_amr_wins_fair + 1; end
    if advantage_fair(si,3) > 0, n_inf_wins_fair = n_inf_wins_fair + 1; end
end
fprintf('   CoADAM beats random: AMR at %d/%d scales, Infection at %d/%d scales\n\n', ...
    n_amr_wins_fair, n_scales, n_inf_wins_fair, n_scales);

fprintf('5. ADVERSARIAL ADVANTAGE (both vs Adaptive Attacker):\n');
n_amr_wins_adv = 0;
n_inf_wins_adv = 0;
for si = 1:n_scales
    fprintf('   %d devices: AMR %+.4f, Reward %+.2f, InfReduct %+.4f, DSR %+.4f\n', ...
        scale_levels(si), advantage_adapt(si,1), advantage_adapt(si,2), ...
        advantage_adapt(si,3), advantage_adapt(si,4));
    if advantage_adapt(si,1) > 0, n_amr_wins_adv = n_amr_wins_adv + 1; end
    if advantage_adapt(si,3) > 0, n_inf_wins_adv = n_inf_wins_adv + 1; end
end
fprintf('   CoADAM beats random: AMR at %d/%d scales, Infection at %d/%d scales\n\n', ...
    n_amr_wins_adv, n_scales, n_inf_wins_adv, n_scales);

fprintf('6. COMPUTATIONAL SCALING:\n');
first_time = scale_results.(sprintf('s%d', scale_levels(1))).mean_ep_time;
last_time = scale_results.(sprintf('s%d', scale_levels(end))).mean_ep_time;
fprintf('   Episode time range: %.4f s (%d devices) to %.4f s (%d devices)\n', ...
    first_time, scale_levels(1), last_time, scale_levels(end));
if first_time > 0
    fprintf('   Scaling factor: %.2fx for %.0fx network growth\n\n', ...
        last_time / first_time, scale_levels(end) / scale_levels(1));
else
    fprintf('   Scaling factor: N/A\n\n');
end

avg_non_train = mean(scalability_scores(non_train));
fprintf('7. OVERALL SCALABILITY: Average composite = %.4f\n', avg_non_train);
if avg_non_train >= 0.95
    fprintf('   CONCLUSION: Excellent scalability across all tested scales.\n');
elseif avg_non_train >= 0.90
    fprintf('   CONCLUSION: Good scalability with graceful degradation at larger scales.\n');
elseif avg_non_train >= 0.80
    fprintf('   CONCLUSION: Good scalability with minor degradation at extreme scales.\n');
elseif avg_non_train >= 0.65
    fprintf('   CONCLUSION: Moderate scalability. Performance degrades at larger scales.\n');
else
    fprintf('   CONCLUSION: Poor scalability. Retraining recommended for different scales.\n');
end
fprintf('\n');

%% ---- Save results -------------------------------------------------------
total_time = toc(phase8_start);

scalability_results = struct();
scalability_results.scale_levels = scale_levels;
scalability_results.training_scale = training_scale;
scalability_results.scale_results = scale_results;
scalability_results.random_results = random_results;
scalability_results.coadam_vs_rand_atk = coadam_vs_rand_atk;
scalability_results.random_vs_rand = random_vs_rand;
scalability_results.advantage_fair = advantage_fair;
scalability_results.advantage_adapt = advantage_adapt;
scalability_results.retention = retention;
scalability_results.scalability_scores = scalability_scores;
scalability_results.n_eval = n_eval;
scalability_results.total_time = total_time;
scalability_results.timestamp = char(datetime('now'));

save(fullfile(results_dir, 'scalability_results.mat'), '-struct', 'scalability_results');
fprintf('Results saved: %s\n', fullfile(results_dir, 'scalability_results.mat'));

%% ---- Write report -------------------------------------------------------
fid = fopen(fullfile(phase8_dir, 'scalability_report.txt'), 'w');

fprintf(fid, '================================================================\n');
fprintf(fid, '  CoADAM Phase 8: Multi-Scale Evaluation Report\n');
fprintf(fid, '  Generated: %s\n', char(datetime('now')));
fprintf(fid, '  Total time: %.1f s (%.1f min)\n', total_time, total_time/60);
fprintf(fid, '================================================================\n\n');

fprintf(fid, '1. CONFIGURATION\n');
fprintf(fid, '   Scale levels: ');
for si = 1:n_scales
    fprintf(fid, '%d ', scale_levels(si));
end
fprintf(fid, '\n');
fprintf(fid, '   Training scale: %d devices\n', training_scale);
fprintf(fid, '   Episodes per combo: %d\n', n_eval);
fprintf(fid, '   Combos: 4 (CoADAM/Random x Adaptive/Random attacker)\n');
fprintf(fid, '   Infection spread scaling: power law (exponent -0.3)\n');
fprintf(fid, '   Budget scaling: power law (exponent 0.3)\n\n');

fprintf(fid, '2. CoADAM vs ADAPTIVE ATTACKER (Table 1)\n\n');
fprintf(fid, '   %-8s', 'Scale');
for mi = 1:length(show_labels)
    fprintf(fid, ' %10s', show_labels{mi});
end
fprintf(fid, '\n   %s\n', repmat('-', 1, 6 + 10*length(show_labels)));
for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    fprintf(fid, '   %-8d', scale_levels(si));
    fprintf(fid, ' %10.4f', sr.AMR.mean);
    fprintf(fid, ' %10.4f', sr.DSR.mean);
    fprintf(fid, ' %10.4f', sr.FAR.mean);
    fprintf(fid, ' %10.2f', sr.CumulativeReward.mean);
    fprintf(fid, ' %10.4f', sr.InfectionRate.mean);
    fprintf(fid, ' %10.2f', sr.MTTD.mean);
    fprintf(fid, ' %10.2f', sr.AttackerDwellTime.mean);
    fprintf(fid, ' %10.2f', sr.DefenseCostEfficiency.mean);
    fprintf(fid, '\n');
end
fprintf(fid, '\n');

fprintf(fid, '3. RETENTION RELATIVE TO TRAINING SCALE\n\n');
fprintf(fid, '   %-8s %10s %10s %10s %10s %12s\n', ...
    'Scale', 'AMR', 'Infection', 'DSR', 'MTTD', 'Composite');
fprintf(fid, '   %s\n', repmat('-', 1, 60));
for si = 1:n_scales
    fprintf(fid, '   %-8d %9.1f%% %9.1f%% %9.1f%% %9.1f%% %12.4f\n', ...
        scale_levels(si), retention(si,1), retention(si,2), ...
        retention(si,3), retention(si,4), scalability_scores(si));
end
fprintf(fid, '\n');

fprintf(fid, '4. ADVANTAGE OVER RANDOM (Fair: both vs Random Attacker)\n\n');
fprintf(fid, '   %-8s %10s %10s %10s %10s\n', 'Scale', 'AMR', 'Reward', 'Infection', 'DSR');
fprintf(fid, '   %s\n', repmat('-', 1, 48));
for si = 1:n_scales
    fprintf(fid, '   %-8d %+10.4f %+10.2f %+10.4f %+10.4f\n', ...
        scale_levels(si), advantage_fair(si,1), advantage_fair(si,2), ...
        advantage_fair(si,3), advantage_fair(si,4));
end
fprintf(fid, '\n');

fprintf(fid, '   ADVANTAGE OVER RANDOM (Adversarial: both vs Adaptive Attacker)\n\n');
fprintf(fid, '   %-8s %10s %10s %10s %10s\n', 'Scale', 'AMR', 'Reward', 'Infection', 'DSR');
fprintf(fid, '   %s\n', repmat('-', 1, 48));
for si = 1:n_scales
    fprintf(fid, '   %-8d %+10.4f %+10.2f %+10.4f %+10.4f\n', ...
        scale_levels(si), advantage_adapt(si,1), advantage_adapt(si,2), ...
        advantage_adapt(si,3), advantage_adapt(si,4));
end
fprintf(fid, '\n');

fprintf(fid, '5. COMPUTATIONAL PERFORMANCE\n\n');
fprintf(fid, '   %-8s %12s %12s\n', 'Scale', 'Ep_Time(s)', 'Relative');
fprintf(fid, '   %s\n', repmat('-', 1, 34));
for si = 1:n_scales
    sr = scale_results.(sprintf('s%d', scale_levels(si)));
    fprintf(fid, '   %-8d %12.4f %11.2fx\n', ...
        scale_levels(si), sr.mean_ep_time, sr.mean_ep_time / max(train_time, 0.0001));
end
fprintf(fid, '\n');

fprintf(fid, '6. KEY FINDINGS\n\n');
fprintf(fid, '   Average scalability composite: %.4f\n', avg_non_train);
fprintf(fid, '   AMR range across scales: %.4f (%.1f%% variation)\n', ...
    amr_range, amr_range / mean(amr_vals) * 100);
fprintf(fid, '   Fair advantage: CoADAM beats random on AMR at %d/%d scales\n', ...
    n_amr_wins_fair, n_scales);
fprintf(fid, '   Fair advantage: CoADAM beats random on Infection at %d/%d scales\n', ...
    n_inf_wins_fair, n_scales);
if avg_non_train >= 0.90
    fprintf(fid, '   CONCLUSION: Excellent scalability.\n');
elseif avg_non_train >= 0.80
    fprintf(fid, '   CONCLUSION: Good scalability with minor degradation.\n');
elseif avg_non_train >= 0.65
    fprintf(fid, '   CONCLUSION: Moderate scalability.\n');
else
    fprintf(fid, '   CONCLUSION: Poor scalability. Retraining recommended.\n');
end

fclose(fid);
fprintf('Report saved: %s\n', fullfile(phase8_dir, 'scalability_report.txt'));
fprintf('\n=== Phase 8 Complete (%.1f s) ===\n', total_time);

%% ---- Helper function ----------------------------------------------------
function s = sig_str(p)
    if p < 0.001, s = '(***)';
    elseif p < 0.01, s = '(**)';
    elseif p < 0.05, s = '(*)';
    else, s = '(n.s.)';
    end
end
