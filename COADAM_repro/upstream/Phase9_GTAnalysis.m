%% ========================================================================
%  CoADAM Phase 9: Game-Theoretic Analysis
%  Component 1: Exploitability over training (attacker pool snapshots)
%  Component 2: Nash Equilibrium Gap
%  Component 3: Skepticism-Momentum Signaling Analysis
%  Date: 02-Mar-2026
%% ========================================================================
clear; clc;
fprintf('=== CoADAM Phase 9: Game-Theoretic Analysis ===\n');
fprintf('Started: %s\n\n', char(datetime('now')));
phase9_start = tic;

%% ---- Paths -------------------------------------------------------------
project_root  = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
results_dir   = fullfile(project_root, 'results');
phase2_dir    = fullfile(project_root, 'phase2_environment');
phase9_dir    = fullfile(project_root, 'phase9_gametheory');

if ~exist(phase9_dir,  'dir'), mkdir(phase9_dir);  end
if ~exist(results_dir, 'dir'), mkdir(results_dir); end
addpath(phase2_dir);

%% ---- Load config and trained models ------------------------------------
fprintf('[1] Loading config and trained models...\n');
load(fullfile(processed_dir, 'environment_config.mat'), 'config');
trained = load(fullfile(results_dir, 'dqn_cotraining_results.mat'));

W1 = trained.W1; W2 = trained.W2; W3 = trained.W3;
b1 = trained.b1; b2 = trained.b2; b3 = trained.b3;
atk_Q        = trained.atk_Q;
atk_pool     = trained.attacker_pool;
n_pool       = length(atk_pool);
atk_bins     = config.attacker_state.n_bins;
conv_ep      = double(trained.convergence_episode);
n_episodes   = double(trained.n_episodes);
n_eval       = 200;
max_steps    = config.episode.max_steps;

fprintf('    DQN [%dx%d]->[%dx%d]->[%dx%d]\n', ...
    size(W1,1),size(W1,2), size(W2,1),size(W2,2), size(W3,1),size(W3,2));
fprintf('    Attacker Q-table: %dx%d\n', size(atk_Q,1), size(atk_Q,2));
fprintf('    Attacker pool: %d snapshots\n', n_pool);
fprintf('    Convergence episode: %d\n', conv_ep);
fprintf('    Evaluation episodes per condition: %d\n\n', n_eval);

%% ========================================================================
%  COMPONENT 1: EXPLOITABILITY OVER TRAINING
%  For each pool snapshot (representing an attacker at a training stage),
%  evaluate it against the FROZEN final defender policy.
%  Exploitability = V_BR(pi_d) - V_coevol
%  where V_BR is best-response attacker value and V_coevol is the
%  co-evolutionary attacker value at the same snapshot.
%% ========================================================================
fprintf('==============================================================\n');
fprintf('  COMPONENT 1: EXPLOITABILITY ANALYSIS\n');
fprintf('==============================================================\n\n');

% The pool snapshots are ordered from oldest to newest during training.
% Pool snapshot k approximately corresponds to episode k*(n_episodes/n_pool).
pool_episodes = round(linspace(n_episodes/n_pool, n_episodes, n_pool));

pool_atk_reward  = zeros(1, n_pool);  % attacker reward per pool snapshot
pool_def_reward  = zeros(1, n_pool);  % defender reward per pool snapshot
pool_amr         = zeros(1, n_pool);  % AMR per pool snapshot
pool_infection   = zeros(1, n_pool);  % infection per pool snapshot

fprintf('Evaluating %d pool snapshots against frozen final defender...\n\n', n_pool);

for pi = 1:n_pool
    rng(42);
    snap_Q = atk_pool{pi};
    env    = iiot_environment(config);

    ep_atk_rew = zeros(1, n_eval);
    ep_def_rew = zeros(1, n_eval);
    ep_amr     = zeros(1, n_eval);
    ep_inf     = zeros(1, n_eval);

    for ep = 1:n_eval
        [def_state, atk_state] = env.reset();

        for step = 1:max_steps
            % Frozen final defender policy
            s    = def_state(:);
            h1_  = max(0, W1*s + b1);
            h2_  = max(0, W2*h1_ + b2);
            q_d  = W3*h2_ + b3;

            % Action masking (Fix 2)
            infection_level = s(1);
            skepticism_val  = s(6);
            if (infection_level > 0.60) && (skepticism_val > 0.80)
                q_d(2) = -inf;
            end
            [~, def_action] = max(q_d);

            % Pool snapshot attacker policy
            atk_idx = env.discretize_state(atk_state, atk_bins);
            atk_idx = min(atk_idx, size(snap_Q, 1));
            [~, atk_action] = max(snap_Q(atk_idx, :));

            [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
            if done, break; end
        end

        m = env.get_episode_metrics();
        ep_atk_rew(ep) = m.AttackerCumulativeReward;
        ep_def_rew(ep) = m.CumulativeReward;
        ep_amr(ep)     = m.AMR;
        ep_inf(ep)     = m.InfectionRate;
    end

    pool_atk_reward(pi) = mean(ep_atk_rew);
    pool_def_reward(pi) = mean(ep_def_rew);
    pool_amr(pi)        = mean(ep_amr);
    pool_infection(pi)  = mean(ep_inf);

    fprintf('  Snapshot %2d (ep ~%4d): AtkRew=%.2f | DefRew=%.2f | AMR=%.4f | Inf=%.4f\n', ...
        pi, pool_episodes(pi), pool_atk_reward(pi), pool_def_reward(pi), ...
        pool_amr(pi), pool_infection(pi));
end

% Exploitability = max attacker reward across pool - final co-evol attacker reward
% Final co-evol attacker reward is from training evaluation
coevol_atk_reward = mean(trained.eval_atk_rew);
coevol_def_reward = mean(trained.eval_rew);

exploitability = max(pool_atk_reward) - coevol_atk_reward;
best_response_value = max(pool_atk_reward);

fprintf('\n--- Exploitability Summary ---\n');
fprintf('  Co-evolutionary attacker reward (final): %.4f\n', coevol_atk_reward);
fprintf('  Best-response attacker reward (max pool): %.4f\n', best_response_value);
fprintf('  Exploitability: %.4f\n', exploitability);
fprintf('  Exploitability normalized: %.4f%%\n\n', ...
    exploitability / abs(coevol_def_reward) * 100);

%% ========================================================================
%  COMPONENT 2: NASH EQUILIBRIUM GAP
%  Nash gap = exploitability of defender + exploitability of attacker
%  Defender exploitability = how much defender can improve against
%  the frozen final attacker (using random defender as lower bound
%  and trained DQN as upper bound).
%% ========================================================================
fprintf('==============================================================\n');
fprintf('  COMPONENT 2: NASH EQUILIBRIUM GAP\n');
fprintf('==============================================================\n\n');

% Evaluate best-response DEFENDER against frozen final attacker
% (random defender as lower bound, DQN as best available)
rng(42);
env = iiot_environment(config);

br_def_rew_dqn  = zeros(1, n_eval);
br_def_rew_rand = zeros(1, n_eval);
br_atk_rew_dqn  = zeros(1, n_eval);
br_atk_rew_rand = zeros(1, n_eval);

for ep = 1:n_eval
    [def_state, atk_state] = env.reset();

    for step = 1:max_steps
        % DQN defender
        s   = def_state(:);
        h1_ = max(0, W1*s + b1);
        h2_ = max(0, W2*h1_ + b2);
        q_d = W3*h2_ + b3;
        infection_level = s(1);
        skepticism_val  = s(6);
        if (infection_level > 0.60) && (skepticism_val > 0.80)
            q_d(2) = -inf;
        end
        [~, def_action] = max(q_d);

        % Frozen final attacker
        atk_idx = env.discretize_state(atk_state, atk_bins);
        atk_idx = min(atk_idx, size(atk_Q, 1));
        [~, atk_action] = max(atk_Q(atk_idx, :));

        [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
        if done, break; end
    end

    m = env.get_episode_metrics();
    br_def_rew_dqn(ep)  = m.CumulativeReward;
    br_atk_rew_dqn(ep)  = m.AttackerCumulativeReward;
end

% Random defender against frozen final attacker
rng(42);
env = iiot_environment(config);
for ep = 1:n_eval
    [def_state, atk_state] = env.reset();

    for step = 1:max_steps
        def_action = randi(config.n_defender_actions);

        atk_idx = env.discretize_state(atk_state, atk_bins);
        atk_idx = min(atk_idx, size(atk_Q, 1));
        [~, atk_action] = max(atk_Q(atk_idx, :));

        [def_state, atk_state, ~, ~, done, ~] = env.step(def_action, atk_action);
        if done, break; end
    end

    m = env.get_episode_metrics();
    br_def_rew_rand(ep) = m.CumulativeReward;
    br_atk_rew_rand(ep) = m.AttackerCumulativeReward;
end

% Nash gap components
V_def_dqn   = mean(br_def_rew_dqn);   % DQN defender value
V_def_rand  = mean(br_def_rew_rand);  % Random defender value
V_atk_final = mean(br_atk_rew_dqn);  % Attacker value against DQN defender

% Defender exploitability: how much better than random
def_exploitability = V_def_dqn - V_def_rand;

% Attacker exploitability: best-response minus co-evol
atk_exploitability = exploitability;

% Nash gap = sum of both exploitabilities normalized
nash_gap = (abs(atk_exploitability) + abs(def_exploitability)) / ...
           (abs(coevol_def_reward) + abs(coevol_atk_reward));

fprintf('--- Nash Equilibrium Gap ---\n');
fprintf('  Defender value (DQN vs frozen atk):    %.4f\n', V_def_dqn);
fprintf('  Defender value (Random vs frozen atk): %.4f\n', V_def_rand);
fprintf('  Defender exploitability:               %.4f\n', def_exploitability);
fprintf('  Attacker exploitability:               %.4f\n', atk_exploitability);
fprintf('  Nash Gap (normalized):                 %.4f\n\n', nash_gap);

%% ========================================================================
%  COMPONENT 3: SKEPTICISM-MOMENTUM SIGNALING ANALYSIS
%  Uses trk_skepticism and trk_momentum from training history.
%  Shows the coupled dynamic converges to a stable equilibrium.
%  Computes: correlation, equilibrium point, convergence rate.
%% ========================================================================
fprintf('==============================================================\n');
fprintf('  COMPONENT 3: SKEPTICISM-MOMENTUM SIGNALING ANALYSIS\n');
fprintf('==============================================================\n\n');

trk_skep = trained.trk_skepticism;
trk_mom  = trained.trk_momentum;
trk_inf  = trained.trk_infection;

win = 100;  % smoothing window

skep_smooth = movmean(trk_skep, win);
mom_smooth  = movmean(trk_mom,  win);
inf_smooth  = movmean(trk_inf,  win);

% Equilibrium point: mean of last 500 episodes (post-convergence)
post_conv_start = max(conv_ep, n_episodes - 500);
skep_eq = mean(trk_skep(post_conv_start:end));
mom_eq  = mean(trk_mom(post_conv_start:end));
inf_eq  = mean(trk_inf(post_conv_start:end));

% Correlation between skepticism and momentum
[rho_sm, p_sm] = corr(trk_skep(:), trk_mom(:), 'Type', 'Spearman');

% Correlation between skepticism and infection
[rho_si, p_si] = corr(trk_skep(:), trk_inf(:), 'Type', 'Spearman');

% Correlation between momentum and infection
[rho_mi, p_mi] = corr(trk_mom(:), trk_inf(:), 'Type', 'Spearman');

% Convergence rate: fit exponential decay to |skepticism - skep_eq|
% from convergence episode onward
post_ep   = (conv_ep:n_episodes)';
skep_dev  = abs(trk_skep(conv_ep:end)' - skep_eq);
skep_dev  = max(skep_dev, 1e-6);

% Fit log-linear model to get decay rate
log_dev = log(skep_dev);
p_fit   = polyfit(post_ep - conv_ep, log_dev, 1);
decay_rate = -p_fit(1);

% Phase space analysis: divide into pre/post convergence
pre_skep  = trk_skep(1:conv_ep);
post_skep = trk_skep(conv_ep:end);
pre_mom   = trk_mom(1:conv_ep);
post_mom  = trk_mom(conv_ep:end);

pre_var_skep  = var(pre_skep);
post_var_skep = var(post_skep);
pre_var_mom   = var(pre_mom);
post_var_mom  = var(post_mom);

variance_reduction_skep = (pre_var_skep - post_var_skep) / pre_var_skep * 100;
variance_reduction_mom  = (pre_var_mom  - post_var_mom)  / pre_var_mom  * 100;

fprintf('--- Signaling Dynamic Analysis ---\n');
fprintf('  Equilibrium skepticism:    %.4f\n', skep_eq);
fprintf('  Equilibrium momentum:      %.4f\n', mom_eq);
fprintf('  Equilibrium infection:     %.4f\n\n', inf_eq);

fprintf('  Spearman correlations:\n');
fprintf('    Skepticism-Momentum:  rho=%.4f, p=%.6f\n', rho_sm, p_sm);
fprintf('    Skepticism-Infection: rho=%.4f, p=%.6f\n', rho_si, p_si);
fprintf('    Momentum-Infection:   rho=%.4f, p=%.6f\n\n', rho_mi, p_mi);

fprintf('  Convergence decay rate (skepticism): %.6f per episode\n', decay_rate);
fprintf('  Variance reduction post-convergence:\n');
fprintf('    Skepticism: %.1f%%\n', variance_reduction_skep);
fprintf('    Momentum:   %.1f%%\n\n', variance_reduction_mom);

%% ---- Save results ------------------------------------------------------
phase9_results = struct();

% Component 1
phase9_results.exploitability.pool_episodes    = pool_episodes;
phase9_results.exploitability.pool_atk_reward  = pool_atk_reward;
phase9_results.exploitability.pool_def_reward  = pool_def_reward;
phase9_results.exploitability.pool_amr         = pool_amr;
phase9_results.exploitability.pool_infection   = pool_infection;
phase9_results.exploitability.coevol_atk_reward = coevol_atk_reward;
phase9_results.exploitability.best_response_value = best_response_value;
phase9_results.exploitability.exploitability   = exploitability;

% Component 2
phase9_results.nash_gap.V_def_dqn          = V_def_dqn;
phase9_results.nash_gap.V_def_rand         = V_def_rand;
phase9_results.nash_gap.V_atk_final        = V_atk_final;
phase9_results.nash_gap.def_exploitability = def_exploitability;
phase9_results.nash_gap.atk_exploitability = atk_exploitability;
phase9_results.nash_gap.nash_gap           = nash_gap;

% Component 3
phase9_results.signaling.skep_eq               = skep_eq;
phase9_results.signaling.mom_eq                = mom_eq;
phase9_results.signaling.inf_eq                = inf_eq;
phase9_results.signaling.rho_skep_mom          = rho_sm;
phase9_results.signaling.p_skep_mom            = p_sm;
phase9_results.signaling.rho_skep_inf          = rho_si;
phase9_results.signaling.p_skep_inf            = p_si;
phase9_results.signaling.rho_mom_inf           = rho_mi;
phase9_results.signaling.p_mom_inf             = p_mi;
phase9_results.signaling.decay_rate            = decay_rate;
phase9_results.signaling.variance_red_skep     = variance_reduction_skep;
phase9_results.signaling.variance_red_mom      = variance_reduction_mom;
phase9_results.signaling.skep_smooth           = skep_smooth;
phase9_results.signaling.mom_smooth            = mom_smooth;
phase9_results.signaling.inf_smooth            = inf_smooth;

phase9_results.total_time = toc(phase9_start);
phase9_results.timestamp  = char(datetime('now'));

save(fullfile(results_dir, 'phase9_results.mat'), '-struct', 'phase9_results');
fprintf('Results saved: %s\n', fullfile(results_dir, 'phase9_results.mat'));

%% ---- Write report ------------------------------------------------------
fid = fopen(fullfile(phase9_dir, 'phase9_report.txt'), 'w');

fprintf(fid, '================================================================\n');
fprintf(fid, '  CoADAM Phase 9: Game-Theoretic Analysis Report\n');
fprintf(fid, '  Generated: %s\n', char(datetime('now')));
fprintf(fid, '  Total time: %.1f s\n', phase9_results.total_time);
fprintf(fid, '================================================================\n\n');

fprintf(fid, '1. EXPLOITABILITY ANALYSIS\n\n');
fprintf(fid, '   Pool snapshots evaluated against frozen final defender:\n\n');
fprintf(fid, '   %-10s %-12s %-12s %-10s %-10s\n', ...
    'Snapshot', 'Episode', 'Atk_Reward', 'Def_Reward', 'AMR');
fprintf(fid, '   %s\n', repmat('-', 1, 54));
for pi = 1:n_pool
    fprintf(fid, '   %-10d %-12d %-12.4f %-10.4f %-10.4f\n', ...
        pi, pool_episodes(pi), pool_atk_reward(pi), ...
        pool_def_reward(pi), pool_amr(pi));
end
fprintf(fid, '\n');
fprintf(fid, '   Co-evolutionary attacker reward: %.4f\n', coevol_atk_reward);
fprintf(fid, '   Best-response attacker reward:   %.4f\n', best_response_value);
fprintf(fid, '   Exploitability:                  %.4f\n\n', exploitability);

fprintf(fid, '2. NASH EQUILIBRIUM GAP\n\n');
fprintf(fid, '   Defender value (DQN):    %.4f\n', V_def_dqn);
fprintf(fid, '   Defender value (Random): %.4f\n', V_def_rand);
fprintf(fid, '   Defender exploitability: %.4f\n', def_exploitability);
fprintf(fid, '   Attacker exploitability: %.4f\n', atk_exploitability);
fprintf(fid, '   Nash Gap (normalized):   %.4f\n\n', nash_gap);

fprintf(fid, '3. SKEPTICISM-MOMENTUM SIGNALING ANALYSIS\n\n');
fprintf(fid, '   Equilibrium point: skep=%.4f, mom=%.4f, inf=%.4f\n', ...
    skep_eq, mom_eq, inf_eq);
fprintf(fid, '   Skepticism-Momentum correlation: rho=%.4f (p=%.6f)\n', rho_sm, p_sm);
fprintf(fid, '   Skepticism-Infection correlation: rho=%.4f (p=%.6f)\n', rho_si, p_si);
fprintf(fid, '   Momentum-Infection correlation:  rho=%.4f (p=%.6f)\n', rho_mi, p_mi);
fprintf(fid, '   Convergence decay rate:          %.6f per episode\n', decay_rate);
fprintf(fid, '   Variance reduction (skepticism): %.1f%%\n', variance_reduction_skep);
fprintf(fid, '   Variance reduction (momentum):   %.1f%%\n\n', variance_reduction_mom);

fclose(fid);
fprintf('Report saved: %s\n', fullfile(phase9_dir, 'phase9_report.txt'));
fprintf('\n=== Phase 9 Complete (%.1f s) ===\n', toc(phase9_start));
