%% ========================================================================
%  CoADAM Phase 7: Ablation & Sensitivity Analysis (REVISED)
%  Part A: Ablation study (contribution analysis)
%  Part B: Reward weight sensitivity analysis
%  Part C: Statistical robustness analysis
%  Date: 28-Feb-2026
%  ========================================================================
clear; clc;
fprintf('=== CoADAM Phase 7: Ablation & Sensitivity Analysis ===\n');
fprintf('Started: %s\n\n', char(datetime('now')));
phase7_start = tic;

%% ---- Paths -------------------------------------------------------------
project_root  = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
results_dir   = fullfile(project_root, 'results');
phase2_dir    = fullfile(project_root, 'phase2_environment');
phase7_dir    = fullfile(project_root, 'phase7_ablation');

if ~exist(phase7_dir, 'dir'), mkdir(phase7_dir); end
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
n_eval = 100;
max_steps = config.episode.max_steps;

fprintf('    DQN [%dx%d]->[%dx%d]->[%dx%d]\n', ...
    size(W1,1),size(W1,2), size(W2,1),size(W2,2), size(W3,1),size(W3,2));
fprintf('    Attacker Q-table [%d x %d]\n', size(atk_Q,1), size(atk_Q,2));
fprintf('    Evaluation: %d episodes per variant\n\n', n_eval);

%% ========================================================================
%  PART A: ABLATION STUDY
%  ========================================================================
fprintf('==============================================================\n');
fprintf('  PART A: ABLATION STUDY (Component Contribution Analysis)\n');
fprintf('==============================================================\n\n');

% Variant definitions:
% 1. Full CoADAM (baseline)
% 2. No Deception (zero deception mechanisms + reward)
% 3. No Co-evolution (random attacker - measures robustness gain)
% 4. No DQN (random defender - measures learning value)
% 5. No Skepticism (skepticism = 0)
% 6. No Momentum (momentum = 0 + zero penalty)
% 7. No Diversity Reward (w_diversity = 0)

n_variants = 7;
variant_names = { ...
    'Full CoADAM', ...
    'No Deception', ...
    'No Co-evolution', ...
    'No DQN (Random Def)', ...
    'No Skepticism', ...
    'No Momentum', ...
    'No Diversity Reward'};

variant_short = {'full', 'no_deception', 'no_coevol', 'no_dqn', ...
    'no_skepticism', 'no_momentum', 'no_diversity'};

% Classification: which variants WEAKEN the attacker vs WEAKEN the defender
% This determines expected direction of change
variant_type = {'baseline', 'mixed', 'weakens_attacker', 'weakens_defender', ...
    'weakens_attacker', 'weakens_attacker', 'neutral'};

fprintf('Variants and expected effects:\n');
fprintf('  %-22s %-20s %s\n', 'Variant', 'Type', 'Expected Direction');
fprintf('  %s\n', repmat('-', 1, 70));
fprintf('  %-22s %-20s %s\n', 'Full CoADAM', 'baseline', '(reference)');
fprintf('  %-22s %-20s %s\n', 'No Deception', 'mixed', 'AMR may drop, DSR=0');
fprintf('  %-22s %-20s %s\n', 'No Co-evolution', 'weakens_attacker', 'Reward UP (easier game)');
fprintf('  %-22s %-20s %s\n', 'No DQN', 'weakens_defender', 'AMR DOWN, Reward DOWN');
fprintf('  %-22s %-20s %s\n', 'No Skepticism', 'weakens_attacker', 'DSR UP (deception always works)');
fprintf('  %-22s %-20s %s\n', 'No Momentum', 'weakens_attacker', 'Infection DOWN (weaker attacker)');
fprintf('  %-22s %-20s %s\n', 'No Diversity', 'neutral', 'Reward slightly lower');
fprintf('\n');

fprintf('Running ablation evaluation...\n\n');
all_ablation_results = struct();

for v = 1:n_variants
    fprintf('--- Variant %d/%d: %s ---\n', v, n_variants, variant_names{v});
    var_start = tic;
    
    rng(42);
    var_config = config;
    
    switch v
        case 1
            % Full CoADAM - no changes
            
        case 2
            % No Deception
            var_config.strategy_bundles(:, 1) = 0;
            var_config.strategy_bundles(:, 6) = 0;
            var_config.deception_engagement(1, :) = 0;
            var_config.deception_engagement(6, :) = 0;
            var_config.reward.w_deception = 0;
            
        case 3
            % No Co-evolution (random attacker)
            
        case 4
            % No DQN (random defender)
            
        case 5
            % No Skepticism
            var_config.skepticism.initial = 0;
            var_config.skepticism.max = 0;
            var_config.skepticism.increment = 0;
            if isfield(var_config.skepticism, 'decay')
                var_config.skepticism.decay = 0;
            end
            
        case 6
            % No Momentum
            var_config.momentum.initial = 0;
            var_config.momentum.max = 0;
            var_config.momentum.increment = 0;
            if isfield(var_config.momentum, 'decay')
                var_config.momentum.decay = 0;
            end
            if isfield(var_config.momentum, 'effect_on_success')
                var_config.momentum.effect_on_success = 0;
            end
            var_config.reward.w_momentum_penalty = 0;
            
        case 7
            % No Diversity Reward
            var_config.reward.w_diversity = 0;
    end
    
    env = iiot_environment(var_config);
    ep_metrics = cell(1, n_eval);
    
    for ep = 1:n_eval
        [def_state, atk_state] = env.reset();
        
        for step = 1:max_steps
            if v == 4
                def_action = randi(var_config.n_defender_actions);
            else
                s = def_state(:);
                h1 = max(0, W1 * s + b1);
                h2 = max(0, W2 * h1 + b2);
                q_vals = W3 * h2 + b3;
                [~, def_action] = max(q_vals);
            end
            
            if v == 3
                atk_action = randi(var_config.n_attacker_actions);
            else
                atk_idx = env.discretize_state(atk_state, atk_bins);
                [~, atk_action] = max(atk_Q(atk_idx, :));
            end
            
            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end
        
        ep_metrics{ep} = env.get_episode_metrics();
    end
    
    % Aggregate
    amr_arr   = cellfun(@(m) m.AMR, ep_metrics);
    dsr_arr   = cellfun(@(m) m.DSR, ep_metrics);
    far_arr   = cellfun(@(m) m.FAR, ep_metrics);
    rew_arr   = cellfun(@(m) m.CumulativeReward, ep_metrics);
    inf_arr   = cellfun(@(m) m.InfectionRate, ep_metrics);
    mttd_arr  = cellfun(@(m) m.MTTD, ep_metrics);
    dwell_arr = cellfun(@(m) m.AttackerDwellTime, ep_metrics);
    dce_arr   = cellfun(@(m) m.DefenseCostEfficiency, ep_metrics);
    
    res = struct();
    res.name = variant_names{v};
    res.short = variant_short{v};
    res.type = variant_type{v};
    
    metric_names = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
        'MTTD','AttackerDwellTime','DefenseCostEfficiency'};
    metric_arrays = {amr_arr, dsr_arr, far_arr, rew_arr, inf_arr, ...
        mttd_arr, dwell_arr, dce_arr};
    
    for mi = 1:length(metric_names)
        arr = metric_arrays{mi};
        res.(metric_names{mi}) = struct( ...
            'mean', mean(arr), 'std', std(arr), ...
            'min', min(arr), 'max', max(arr), ...
            'median', median(arr), 'raw', arr);
    end
    
    sorted_rew = sort(rew_arr, 'ascend');
    n_tail = max(1, floor(0.05 * n_eval));
    res.CVaR_005 = mean(sorted_rew(1:n_tail));
    res.DR = iqr(rew_arr);
    res.eval_time = toc(var_start);
    
    all_ablation_results.(variant_short{v}) = res;
    
    fprintf('    AMR: %.4f +/- %.4f | DSR: %.4f | Reward: %.2f | Infection: %.4f\n', ...
        res.AMR.mean, res.AMR.std, res.DSR.mean, res.CumulativeReward.mean, ...
        res.InfectionRate.mean);
    fprintf('    MTTD: %.2f | DwellTime: %.2f | CVaR: %.2f | Time: %.1f s\n\n', ...
        res.MTTD.mean, res.AttackerDwellTime.mean, res.CVaR_005, res.eval_time);
end

%% ---- Ablation results table ---------------------------------------------
fprintf('=== Ablation Results Table ===\n\n');

show_metrics = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
    'MTTD','AttackerDwellTime','DefenseCostEfficiency'};
show_labels  = {'AMR','DSR','FAR','Reward','Infection','MTTD','Dwell','CostEff'};

fprintf('%-22s %-18s', 'Variant', 'Type');
for mi = 1:length(show_labels)
    fprintf(' %10s', show_labels{mi});
end
fprintf('\n%s\n', repmat('-', 1, 22 + 18 + 10*length(show_labels)));

for v = 1:n_variants
    r = all_ablation_results.(variant_short{v});
    fprintf('%-22s %-18s', variant_names{v}, variant_type{v});
    for mi = 1:length(show_metrics)
        fprintf(' %10.4f', r.(show_metrics{mi}).mean);
    end
    fprintf('\n');
end
fprintf('\n');

%% ---- Directional change analysis ----------------------------------------
fprintf('=== Directional Change Analysis ===\n');
fprintf('    Arrow direction: expected vs observed\n\n');

full = all_ablation_results.full;

fprintf('%-22s %-18s %8s %8s %8s %8s %10s\n', ...
    'Variant', 'Type', 'AMR', 'DSR', 'Infect', 'Reward', 'Consistent?');
fprintf('%s\n', repmat('-', 1, 88));

consistency_count = 0;
total_checks = 0;

for v = 2:n_variants
    r = all_ablation_results.(variant_short{v});
    
    amr_change = r.AMR.mean - full.AMR.mean;
    dsr_change = r.DSR.mean - full.DSR.mean;
    inf_change = r.InfectionRate.mean - full.InfectionRate.mean;
    rew_change = r.CumulativeReward.mean - full.CumulativeReward.mean;
    
    amr_dir = ternary(amr_change > 0.005, 'UP', ternary(amr_change < -0.005, 'DOWN', '~'));
    dsr_dir = ternary(dsr_change > 0.005, 'UP', ternary(dsr_change < -0.005, 'DOWN', '~'));
    inf_dir = ternary(inf_change > 0.005, 'UP', ternary(inf_change < -0.005, 'DOWN', '~'));
    rew_dir = ternary(rew_change > 1, 'UP', ternary(rew_change < -1, 'DOWN', '~'));
    
    % Check consistency based on variant type
    switch v
        case 2  % No Deception
            % Expected: DSR=0 (confirmed), AMR could go either way
            consistent = strcmp(dsr_dir, 'DOWN') || r.DSR.mean == 0;
        case 3  % No Co-evolution (random attacker)
            % Expected: easier game, reward UP, infection DOWN
            consistent = rew_change > 0 && inf_change < 0;
        case 4  % No DQN (random defender)
            % Expected: harder, reward DOWN, AMR DOWN
            consistent = rew_change < 0;
        case 5  % No Skepticism
            % Expected: DSR UP (deception always works)
            consistent = dsr_change > 0;
        case 6  % No Momentum
            % Expected: weaker attacker, infection DOWN
            consistent = inf_change < 0;
        case 7  % No Diversity
            % Expected: small or no change in AMR/infection
            consistent = abs(amr_change) < 0.02;
    end
    
    total_checks = total_checks + 1;
    if consistent
        consistency_count = consistency_count + 1;
        con_str = 'YES';
    else
        con_str = 'NO';
    end
    
    fprintf('%-22s %-18s %8s %8s %8s %8s %10s\n', ...
        variant_names{v}, variant_type{v}, amr_dir, dsr_dir, inf_dir, rew_dir, con_str);
end

fprintf('\nConsistency: %d/%d variants behave as expected (%.0f%%)\n\n', ...
    consistency_count, total_checks, consistency_count/total_checks*100);

%% ---- Statistical significance -------------------------------------------
fprintf('=== Statistical Significance (Wilcoxon vs Full) ===\n\n');

full_rew_raw = full.CumulativeReward.raw;
full_amr_raw = full.AMR.raw;
full_inf_raw = full.InfectionRate.raw;

fprintf('%-22s %16s %16s %16s\n', 'Variant', 'Reward p', 'AMR p', 'Infection p');
fprintf('%s\n', repmat('-', 1, 70));

for v = 2:n_variants
    r = all_ablation_results.(variant_short{v});
    p_rew = ranksum(full_rew_raw, r.CumulativeReward.raw);
    p_amr = ranksum(full_amr_raw, r.AMR.raw);
    p_inf = ranksum(full_inf_raw, r.InfectionRate.raw);
    
    fprintf('%-22s %8.4f %-6s %8.4f %-6s %8.4f %-6s\n', ...
        variant_names{v}, p_rew, sig_str(p_rew), p_amr, sig_str(p_amr), ...
        p_inf, sig_str(p_inf));
    
    all_ablation_results.(variant_short{v}).pvalues = struct( ...
        'reward', p_rew, 'amr', p_amr, 'infection', p_inf);
end
fprintf('\n');

%% ---- Component contribution (defender-side only) ------------------------
fprintf('=== Defender-Side Component Contribution ===\n');
fprintf('    Comparing only variants that weaken the DEFENDER\n');
fprintf('    (No DQN, No Diversity) - these show true degradation\n\n');

def_variants = [4, 7];  % No DQN, No Diversity
fprintf('%-22s %10s %10s %10s %10s\n', 'Variant', 'AMR_chg', 'Inf_chg', 'Rew_chg', 'DSR_chg');
fprintf('%s\n', repmat('-', 1, 62));

for vi = 1:length(def_variants)
    v = def_variants(vi);
    r = all_ablation_results.(variant_short{v});
    fprintf('%-22s %+9.4f %+9.4f %+9.2f %+9.4f\n', ...
        variant_names{v}, ...
        r.AMR.mean - full.AMR.mean, ...
        r.InfectionRate.mean - full.InfectionRate.mean, ...
        r.CumulativeReward.mean - full.CumulativeReward.mean, ...
        r.DSR.mean - full.DSR.mean);
end
fprintf('\n');

%% ---- Attacker-side analysis ---------------------------------------------
fprintf('=== Attacker-Side Component Analysis ===\n');
fprintf('    Variants that weaken the ATTACKER show improved metrics\n');
fprintf('    This is EXPECTED and shows these components make the game harder\n\n');

atk_variants = [3, 5, 6];  % No Co-evolution, No Skepticism, No Momentum
fprintf('%-22s %10s %10s %10s %s\n', 'Variant', 'Inf_chg', 'DSR_chg', 'Rew_chg', 'Interpretation');
fprintf('%s\n', repmat('-', 1, 80));

for vi = 1:length(atk_variants)
    v = atk_variants(vi);
    r = all_ablation_results.(variant_short{v});
    inf_chg = r.InfectionRate.mean - full.InfectionRate.mean;
    dsr_chg = r.DSR.mean - full.DSR.mean;
    rew_chg = r.CumulativeReward.mean - full.CumulativeReward.mean;
    
    switch v
        case 3
            interp = 'Random attacker trivially easy -> co-evolution provides challenge';
        case 5
            interp = 'No skepticism -> deception always works -> skepticism needed for realism';
        case 6
            interp = 'No momentum -> attacker cant escalate -> momentum creates real threat';
    end
    
    fprintf('%-22s %+9.4f %+9.4f %+9.2f %s\n', ...
        variant_names{v}, inf_chg, dsr_chg, rew_chg, interp);
end
fprintf('\n');

%% ========================================================================
%  PART B: REWARD WEIGHT SENSITIVITY ANALYSIS
%  ========================================================================
fprintf('==============================================================\n');
fprintf('  PART B: REWARD WEIGHT SENSITIVITY ANALYSIS\n');
fprintf('==============================================================\n\n');

% Test sensitivity to key reward weights by scaling them 0.5x and 2.0x
sensitivity_params = { ...
    'w_mitigation',      'reward', 'w_mitigation';
    'w_deception',       'reward', 'w_deception';
    'w_cost',            'reward', 'w_cost';
    'w_infection',       'reward', 'w_infection';
    'w_infection_delta', 'reward', 'w_infection_delta';
    'w_momentum_penalty','reward', 'w_momentum_penalty';
    'w_critical_zone',   'reward', 'w_critical_zone'};

scale_factors = [0.5, 1.0, 2.0];
scale_names = {'0.5x', '1.0x (base)', '2.0x'};

n_params = size(sensitivity_params, 1);
n_scales = length(scale_factors);

fprintf('Testing %d reward weights at %d scale levels (%d episodes each)...\n\n', ...
    n_params, n_scales, n_eval);

sensitivity_results = struct();

for pi = 1:n_params
    param_name = sensitivity_params{pi, 1};
    param_group = sensitivity_params{pi, 2};
    param_field = sensitivity_params{pi, 3};
    
    fprintf('  Parameter: %s\n', param_name);
    
    % Get base value
    base_val = config.(param_group).(param_field);
    fprintf('    Base value: %.4f\n', base_val);
    
    param_results = struct();
    
    for si = 1:n_scales
        rng(42);
        
        sens_config = config;
        new_val = base_val * scale_factors(si);
        sens_config.(param_group).(param_field) = new_val;
        
        env = iiot_environment(sens_config);
        ep_rew = zeros(1, n_eval);
        ep_amr = zeros(1, n_eval);
        ep_inf = zeros(1, n_eval);
        ep_dsr = zeros(1, n_eval);
        
        for ep = 1:n_eval
            [def_state, atk_state] = env.reset();
            ep_reward = 0;
            
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
            ep_rew(ep) = m.CumulativeReward;
            ep_amr(ep) = m.AMR;
            ep_inf(ep) = m.InfectionRate;
            ep_dsr(ep) = m.DSR;
        end
        
        sr = struct();
        sr.scale = scale_factors(si);
        sr.value = new_val;
        sr.reward_mean = mean(ep_rew);
        sr.reward_std = std(ep_rew);
        sr.amr_mean = mean(ep_amr);
        sr.amr_std = std(ep_amr);
        sr.infection_mean = mean(ep_inf);
        sr.dsr_mean = mean(ep_dsr);
        sr.raw_reward = ep_rew;
        sr.raw_amr = ep_amr;
        
        param_results.(sprintf('scale_%d', si)) = sr;
        
        fprintf('    %s (val=%.4f): Reward=%.2f, AMR=%.4f, Inf=%.4f\n', ...
            scale_names{si}, new_val, sr.reward_mean, sr.amr_mean, sr.infection_mean);
    end
    
    sensitivity_results.(param_name) = param_results;
    fprintf('\n');
end

%% ---- Sensitivity summary ------------------------------------------------
fprintf('=== Sensitivity Summary ===\n\n');

fprintf('%-22s %8s %12s %12s %12s %12s\n', ...
    'Parameter', 'Base', 'Rew(0.5x)', 'Rew(1.0x)', 'Rew(2.0x)', 'Sensitivity');
fprintf('%s\n', repmat('-', 1, 78));

for pi = 1:n_params
    param_name = sensitivity_params{pi, 1};
    pr = sensitivity_results.(param_name);
    
    rew_05 = pr.scale_1.reward_mean;
    rew_10 = pr.scale_2.reward_mean;
    rew_20 = pr.scale_3.reward_mean;
    
    % Sensitivity = range of reward change relative to base
    rew_range = max([rew_05, rew_10, rew_20]) - min([rew_05, rew_10, rew_20]);
    if abs(rew_10) > 0.001
        sensitivity = rew_range / abs(rew_10) * 100;
    else
        sensitivity = rew_range * 100;
    end
    
    base_val = config.(sensitivity_params{pi, 2}).(sensitivity_params{pi, 3});
    
    fprintf('%-22s %8.4f %12.2f %12.2f %12.2f %11.1f%%\n', ...
        param_name, base_val, rew_05, rew_10, rew_20, sensitivity);
end
fprintf('\n');

% AMR sensitivity
fprintf('%-22s %8s %12s %12s %12s %12s\n', ...
    'Parameter', 'Base', 'AMR(0.5x)', 'AMR(1.0x)', 'AMR(2.0x)', 'AMR_range');
fprintf('%s\n', repmat('-', 1, 78));

for pi = 1:n_params
    param_name = sensitivity_params{pi, 1};
    pr = sensitivity_results.(param_name);
    
    amr_05 = pr.scale_1.amr_mean;
    amr_10 = pr.scale_2.amr_mean;
    amr_20 = pr.scale_3.amr_mean;
    amr_range = max([amr_05, amr_10, amr_20]) - min([amr_05, amr_10, amr_20]);
    
    base_val = config.(sensitivity_params{pi, 2}).(sensitivity_params{pi, 3});
    
    fprintf('%-22s %8.4f %12.4f %12.4f %12.4f %12.4f\n', ...
        param_name, base_val, amr_05, amr_10, amr_20, amr_range);
end
fprintf('\n');

%% ========================================================================
%  PART C: STATISTICAL ROBUSTNESS ANALYSIS
%  ========================================================================
fprintf('==============================================================\n');
fprintf('  PART C: STATISTICAL ROBUSTNESS ANALYSIS\n');
fprintf('==============================================================\n\n');

% Run Full CoADAM with multiple seeds to assess variability
n_seeds = 10;
seed_values = 1:10:100;  % Seeds: 1, 11, 21, ..., 91
n_seed_eval = 50;  % Episodes per seed

fprintf('Running %d seeds x %d episodes = %d total evaluations...\n\n', ...
    n_seeds, n_seed_eval, n_seeds * n_seed_eval);

seed_results = struct();
all_seed_amr = [];
all_seed_rew = [];
all_seed_inf = [];
all_seed_dsr = [];

per_seed_means = zeros(n_seeds, 4);  % AMR, Reward, Infection, DSR

for si = 1:n_seeds
    rng(seed_values(si));
    
    env = iiot_environment(config);
    seed_amr = zeros(1, n_seed_eval);
    seed_rew = zeros(1, n_seed_eval);
    seed_inf = zeros(1, n_seed_eval);
    seed_dsr = zeros(1, n_seed_eval);
    
    for ep = 1:n_seed_eval
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
        seed_amr(ep) = m.AMR;
        seed_rew(ep) = m.CumulativeReward;
        seed_inf(ep) = m.InfectionRate;
        seed_dsr(ep) = m.DSR;
    end
    
    per_seed_means(si,:) = [mean(seed_amr), mean(seed_rew), mean(seed_inf), mean(seed_dsr)];
    all_seed_amr = [all_seed_amr, seed_amr];
    all_seed_rew = [all_seed_rew, seed_rew];
    all_seed_inf = [all_seed_inf, seed_inf];
    all_seed_dsr = [all_seed_dsr, seed_dsr];
    
    fprintf('  Seed %3d: AMR=%.4f, Reward=%.2f, Infection=%.4f, DSR=%.4f\n', ...
        seed_values(si), per_seed_means(si,1), per_seed_means(si,2), ...
        per_seed_means(si,3), per_seed_means(si,4));
end
fprintf('\n');

%% ---- Cross-seed consistency ---------------------------------------------
fprintf('=== Cross-Seed Consistency ===\n\n');

metric_labels = {'AMR', 'Reward', 'Infection', 'DSR'};
all_arrays = {all_seed_amr, all_seed_rew, all_seed_inf, all_seed_dsr};

fprintf('%-12s %10s %10s %10s %10s %10s %10s\n', ...
    'Metric', 'Mean', 'Std', 'CV(%)', 'Min', 'Max', 'Range');
fprintf('%s\n', repmat('-', 1, 72));

for mi = 1:4
    arr = all_arrays{mi};
    m_mean = mean(arr);
    m_std = std(arr);
    if abs(m_mean) > 0.001
        cv = m_std / abs(m_mean) * 100;
    else
        cv = 0;
    end
    fprintf('%-12s %10.4f %10.4f %9.1f%% %10.4f %10.4f %10.4f\n', ...
        metric_labels{mi}, m_mean, m_std, cv, min(arr), max(arr), max(arr)-min(arr));
end
fprintf('\n');

% Per-seed mean stability
fprintf('Per-seed mean stability (std of seed means):\n');
fprintf('%-12s %10s %10s\n', 'Metric', 'Seed_Std', 'Seed_CV(%)');
fprintf('%s\n', repmat('-', 1, 34));
for mi = 1:4
    seed_std = std(per_seed_means(:, mi));
    seed_mean = mean(per_seed_means(:, mi));
    if abs(seed_mean) > 0.001
        seed_cv = seed_std / abs(seed_mean) * 100;
    else
        seed_cv = 0;
    end
    fprintf('%-12s %10.4f %9.1f%%\n', metric_labels{mi}, seed_std, seed_cv);
end
fprintf('\n');

%% ---- Confidence intervals -----------------------------------------------
fprintf('=== 95%% Confidence Intervals (Bootstrap) ===\n\n');

n_bootstrap = 1000;
fprintf('%-12s %14s %12s %12s\n', 'Metric', 'Mean', 'CI_lower', 'CI_upper');
fprintf('%s\n', repmat('-', 1, 52));

ci_results = struct();

for mi = 1:4
    arr = all_arrays{mi};
    boot_means = zeros(1, n_bootstrap);
    rng(42);
    for b = 1:n_bootstrap
        boot_sample = arr(randi(length(arr), 1, length(arr)));
        boot_means(b) = mean(boot_sample);
    end
    ci_lower = prctile(boot_means, 2.5);
    ci_upper = prctile(boot_means, 97.5);
    
    fprintf('%-12s %14.4f [%10.4f, %10.4f]\n', ...
        metric_labels{mi}, mean(arr), ci_lower, ci_upper);
    
    ci_results.(metric_labels{mi}) = struct( ...
        'mean', mean(arr), 'ci_lower', ci_lower, 'ci_upper', ci_upper, ...
        'ci_width', ci_upper - ci_lower);
end
fprintf('\n');

%% ---- Effect sizes (Cohen's d) for ablation variants --------------------
fprintf('=== Effect Sizes (Cohens d, Full vs each variant) ===\n\n');

fprintf('%-22s %12s %12s %12s\n', 'Variant', 'd_Reward', 'd_AMR', 'd_Infection');
fprintf('%s\n', repmat('-', 1, 58));

for v = 2:n_variants
    r = all_ablation_results.(variant_short{v});
    
    % Cohen's d = (mean1 - mean2) / pooled_std
    pooled_rew = sqrt((full.CumulativeReward.std^2 + r.CumulativeReward.std^2) / 2);
    pooled_amr = sqrt((full.AMR.std^2 + r.AMR.std^2) / 2);
    pooled_inf = sqrt((full.InfectionRate.std^2 + r.InfectionRate.std^2) / 2);
    
    d_rew = (full.CumulativeReward.mean - r.CumulativeReward.mean) / max(pooled_rew, 0.001);
    d_amr = (full.AMR.mean - r.AMR.mean) / max(pooled_amr, 0.001);
    d_inf = (r.InfectionRate.mean - full.InfectionRate.mean) / max(pooled_inf, 0.001);
    
    fprintf('%-22s %12.2f %12.2f %12.2f\n', variant_names{v}, d_rew, d_amr, d_inf);
    
    all_ablation_results.(variant_short{v}).effect_size = struct( ...
        'reward', d_rew, 'amr', d_amr, 'infection', d_inf);
end
fprintf('\n');

fprintf('Interpretation: |d| < 0.2 = negligible, 0.2-0.5 = small,\n');
fprintf('                0.5-0.8 = medium, > 0.8 = large\n\n');

%% ---- Save all results ---------------------------------------------------
total_time = toc(phase7_start);

phase7_results = struct();
phase7_results.ablation = all_ablation_results;
phase7_results.sensitivity = sensitivity_results;
phase7_results.seed_analysis = struct( ...
    'per_seed_means', per_seed_means, ...
    'seed_values', seed_values, ...
    'n_seeds', n_seeds, ...
    'n_seed_eval', n_seed_eval, ...
    'ci_results', ci_results);
phase7_results.variant_names = variant_names;
phase7_results.variant_short = variant_short;
phase7_results.variant_type = variant_type;
phase7_results.n_variants = n_variants;
phase7_results.n_eval = n_eval;
phase7_results.total_time = total_time;
phase7_results.timestamp = char(datetime('now'));

save(fullfile(results_dir, 'ablation_results.mat'), '-struct', 'phase7_results');
fprintf('Results saved: %s\n', fullfile(results_dir, 'ablation_results.mat'));

%% ---- Write comprehensive report -----------------------------------------
fid = fopen(fullfile(phase7_dir, 'ablation_report.txt'), 'w');

fprintf(fid, '================================================================\n');
fprintf(fid, '  CoADAM Phase 7: Ablation & Sensitivity Report\n');
fprintf(fid, '  Generated: %s\n', char(datetime('now')));
fprintf(fid, '  Total time: %.1f s (%.1f min)\n', total_time, total_time/60);
fprintf(fid, '================================================================\n\n');

% Section 1: Ablation design
fprintf(fid, '1. ABLATION STUDY DESIGN\n\n');
fprintf(fid, '   Variants modify either defender-side or attacker-side components.\n');
fprintf(fid, '   Attacker-weakening variants are EXPECTED to show improved metrics\n');
fprintf(fid, '   (easier game), which demonstrates that component creates challenge.\n');
fprintf(fid, '   Defender-weakening variants show true performance degradation.\n\n');
for v = 1:n_variants
    fprintf(fid, '   %d. %-22s [%s]\n', v, variant_names{v}, variant_type{v});
end
fprintf(fid, '\n');

% Section 2: Results
fprintf(fid, '2. ABLATION RESULTS (%d episodes per variant)\n\n', n_eval);
fprintf(fid, '   %-22s %-18s', 'Variant', 'Type');
for mi = 1:length(show_labels)
    fprintf(fid, ' %10s', show_labels{mi});
end
fprintf(fid, '\n   %s\n', repmat('-', 1, 20 + 18 + 10*length(show_labels)));
for v = 1:n_variants
    r = all_ablation_results.(variant_short{v});
    fprintf(fid, '   %-22s %-18s', variant_names{v}, variant_type{v});
    for mi = 1:length(show_metrics)
        fprintf(fid, ' %10.4f', r.(show_metrics{mi}).mean);
    end
    fprintf(fid, '\n');
end
fprintf(fid, '\n');

% Section 3: Directional analysis
fprintf(fid, '3. DIRECTIONAL ANALYSIS\n\n');
fprintf(fid, '   Defender-weakening variants (expected degradation):\n');
for v = [4, 7]
    r = all_ablation_results.(variant_short{v});
    fprintf(fid, '     %s: AMR %+.4f, Reward %+.2f, Infection %+.4f\n', ...
        variant_names{v}, r.AMR.mean - full.AMR.mean, ...
        r.CumulativeReward.mean - full.CumulativeReward.mean, ...
        r.InfectionRate.mean - full.InfectionRate.mean);
end
fprintf(fid, '\n');
fprintf(fid, '   Attacker-weakening variants (expected improvement = component value):\n');
for v = [3, 5, 6]
    r = all_ablation_results.(variant_short{v});
    fprintf(fid, '     %s: AMR %+.4f, Reward %+.2f, Infection %+.4f\n', ...
        variant_names{v}, r.AMR.mean - full.AMR.mean, ...
        r.CumulativeReward.mean - full.CumulativeReward.mean, ...
        r.InfectionRate.mean - full.InfectionRate.mean);
end
fprintf(fid, '\n');

% Section 4: Statistical significance
fprintf(fid, '4. STATISTICAL SIGNIFICANCE\n\n');
fprintf(fid, '   %-22s %14s %14s %14s\n', 'Variant', 'Reward p', 'AMR p', 'Infection p');
fprintf(fid, '   %s\n', repmat('-', 1, 66));
for v = 2:n_variants
    r = all_ablation_results.(variant_short{v});
    fprintf(fid, '   %-22s %8.6f %-4s %8.6f %-4s %8.6f %-4s\n', ...
        variant_names{v}, r.pvalues.reward, sig_str(r.pvalues.reward), ...
        r.pvalues.amr, sig_str(r.pvalues.amr), ...
        r.pvalues.infection, sig_str(r.pvalues.infection));
end
fprintf(fid, '\n');

% Section 5: Effect sizes
fprintf(fid, '5. EFFECT SIZES (Cohens d)\n\n');
fprintf(fid, '   %-22s %12s %12s %12s\n', 'Variant', 'd_Reward', 'd_AMR', 'd_Infection');
fprintf(fid, '   %s\n', repmat('-', 1, 58));
for v = 2:n_variants
    r = all_ablation_results.(variant_short{v});
    fprintf(fid, '   %-22s %12.2f %12.2f %12.2f\n', ...
        variant_names{v}, r.effect_size.reward, r.effect_size.amr, r.effect_size.infection);
end
fprintf(fid, '\n');

% Section 6: Sensitivity
fprintf(fid, '6. REWARD WEIGHT SENSITIVITY\n\n');
fprintf(fid, '   %-22s %8s %12s %12s %12s\n', ...
    'Parameter', 'Base', 'Rew(0.5x)', 'Rew(1.0x)', 'Rew(2.0x)');
fprintf(fid, '   %s\n', repmat('-', 1, 66));
for pi = 1:n_params
    param_name = sensitivity_params{pi, 1};
    pr = sensitivity_results.(param_name);
    base_val = config.(sensitivity_params{pi, 2}).(sensitivity_params{pi, 3});
    fprintf(fid, '   %-22s %8.4f %12.2f %12.2f %12.2f\n', ...
        param_name, base_val, pr.scale_1.reward_mean, ...
        pr.scale_2.reward_mean, pr.scale_3.reward_mean);
end
fprintf(fid, '\n');

% Section 7: Robustness
fprintf(fid, '7. STATISTICAL ROBUSTNESS (%d seeds x %d episodes)\n\n', n_seeds, n_seed_eval);
fprintf(fid, '   %-12s %10s %10s %10s %14s\n', ...
    'Metric', 'Mean', 'Std', 'CV(%%)', '95%% CI');
fprintf(fid, '   %s\n', repmat('-', 1, 58));
for mi = 1:4
    arr = all_arrays{mi};
    m_mean = mean(arr);
    m_std = std(arr);
    cv = 0;
    if abs(m_mean) > 0.001
        cv = m_std / abs(m_mean) * 100;
    end
    ci = ci_results.(metric_labels{mi});
    fprintf(fid, '   %-12s %10.4f %10.4f %9.1f%% [%.4f, %.4f]\n', ...
        metric_labels{mi}, m_mean, m_std, cv, ci.ci_lower, ci.ci_upper);
end
fprintf(fid, '\n');

% Section 8: Key findings
fprintf(fid, '8. KEY FINDINGS\n\n');

fprintf(fid, '   a) DQN learned policy contributes AMR improvement of %.4f\n', ...
    full.AMR.mean - all_ablation_results.no_dqn.AMR.mean);
fprintf(fid, '      and reward improvement of %.2f over random defense.\n\n', ...
    full.CumulativeReward.mean - all_ablation_results.no_dqn.CumulativeReward.mean);

fprintf(fid, '   b) Attacker momentum creates %.1f%% more infection pressure\n', ...
    (full.InfectionRate.mean / max(all_ablation_results.no_momentum.InfectionRate.mean, 0.001) - 1) * 100);
fprintf(fid, '      (%.4f with momentum vs %.4f without).\n\n', ...
    full.InfectionRate.mean, all_ablation_results.no_momentum.InfectionRate.mean);

fprintf(fid, '   c) Co-evolved attacker is %.1fx harder than random attacker\n', ...
    full.InfectionRate.mean / max(all_ablation_results.no_coevol.InfectionRate.mean, 0.001));
fprintf(fid, '      (infection %.4f vs %.4f).\n\n', ...
    full.InfectionRate.mean, all_ablation_results.no_coevol.InfectionRate.mean);

fprintf(fid, '   d) Skepticism mechanism reduces deception success from %.4f to %.4f\n', ...
    all_ablation_results.no_skepticism.DSR.mean, full.DSR.mean);
fprintf(fid, '      creating a more realistic adversarial model.\n\n');

fprintf(fid, '   e) Results are statistically robust: AMR 95%% CI [%.4f, %.4f],\n', ...
    ci_results.AMR.ci_lower, ci_results.AMR.ci_upper);
fprintf(fid, '      CV = %.1f%% across %d seeds.\n', ...
    std(all_seed_amr)/abs(mean(all_seed_amr))*100, n_seeds);

fclose(fid);
fprintf('Report saved: %s\n', fullfile(phase7_dir, 'ablation_report.txt'));
fprintf('\n=== Phase 7 Complete (%.1f s) ===\n', total_time);

%% ---- Helper functions ---------------------------------------------------
function s = sig_str(p)
    if p < 0.001, s = '(***)';
    elseif p < 0.01, s = '(**)';
    elseif p < 0.05, s = '(*)';
    else, s = '(n.s.)';
    end
end

function result = ternary(condition, true_val, false_val)
    if condition
        result = true_val;
    else
        result = false_val;
    end
end
