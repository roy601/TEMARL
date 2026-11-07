% CoADAM Phase 3-4 v3: DQN Co-Evolutionary Training
% Fix 2: Action masking only fires at infection>0.60 AND skepticism>0.80
%        (was firing 25-28% of the time, blocking CoADAM's key advantage)
% Date: 01-Mar-2026

clear; clc;
fprintf('CoADAM DQN Co-Evolutionary Training v3\n');
fprintf('Timestamp: %s\n', char(datetime('now')));
fprintf('========================================================================\n\n');

project_root  = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
phase2_dir    = fullfile(project_root, 'phase2_environment');
phase3_dir    = fullfile(project_root, 'phase3_defender');
results_dir   = fullfile(project_root, 'results');
checkpoint_dir = fullfile(results_dir, 'checkpoints');
if ~exist(phase3_dir,    'dir'), mkdir(phase3_dir);    end
if ~exist(results_dir,   'dir'), mkdir(results_dir);   end
if ~exist(checkpoint_dir,'dir'), mkdir(checkpoint_dir);end

addpath(phase2_dir);
addpath(phase3_dir);

fprintf('Loading configuration...\n');
load(fullfile(processed_dir, 'environment_config.mat'), 'config');

n_episodes = 5000;
max_steps  = config.training.max_steps;

env = iiot_environment(config);
env.intel_boost_enabled = true;
fprintf('Environment created.\n');
fprintf('  Defender: 12 continuous features -> 4 actions (DQN)\n');
fprintf('  Attacker: %d discrete states -> %d actions (Q-table + Pool)\n', ...
    prod(config.attacker_state.n_bins), config.n_attacker_actions);
fprintf('  Episodes: %d, Steps/episode: %d\n\n', n_episodes, max_steps);

% =====================================================
% DQN DEFENDER SETUP
% =====================================================

dqn_input  = config.defender_state.n_features;
dqn_h1     = 128;
dqn_h2     = 64;
dqn_output = config.n_defender_actions;

rng(42);
W1 = randn(dqn_h1, dqn_input)  * sqrt(2 / dqn_input);
b1 = zeros(dqn_h1, 1);
W2 = randn(dqn_h2, dqn_h1)     * sqrt(2 / dqn_h1);
b2 = zeros(dqn_h2, 1);
W3 = randn(dqn_output, dqn_h2) * sqrt(2 / dqn_h2);
b3 = zeros(dqn_output, 1);

W1_t = W1; b1_t = b1;
W2_t = W2; b2_t = b2;
W3_t = W3; b3_t = b3;

dqn_lr        = 0.0005;
dqn_gamma     = 0.85;
dqn_epsilon   = 0.15;
dqn_eps_decay = 0.9993;
dqn_eps_min   = 0.05;
batch_size    = 64;
target_update_freq = 100;
grad_clip     = 1.0;

replay_cap  = 100000;
replay_s    = zeros(replay_cap, dqn_input);
replay_a    = zeros(replay_cap, 1);
replay_r    = zeros(replay_cap, 1);
replay_ns   = zeros(replay_cap, dqn_input);
replay_d    = zeros(replay_cap, 1);
replay_ptr  = 0;
replay_full = false;

n_params = dqn_input*dqn_h1 + dqn_h1 + dqn_h1*dqn_h2 + dqn_h2 + ...
           dqn_h2*dqn_output + dqn_output;
fprintf('DQN network: %d -> %d -> %d -> %d (%d parameters)\n', ...
    dqn_input, dqn_h1, dqn_h2, dqn_output, n_params);

% =====================================================
% ATTACKER SETUP WITH POOL
% =====================================================

atk_bins       = config.attacker_state.n_bins;
atk_state_size = prod(atk_bins);
atk_n_actions  = config.n_attacker_actions;

atk_Q      = zeros(atk_state_size, atk_n_actions);
atk_visits = zeros(atk_state_size, atk_n_actions);
atk_lr     = config.training.attacker.learning_rate;
atk_gamma  = config.training.attacker.gamma;
atk_epsilon   = 0.20;
atk_eps_decay = 0.9993;
atk_eps_min   = 0.05;

attacker_pool_size  = 10;
attacker_pool       = cell(1, attacker_pool_size);
pool_count          = 0;
pool_save_interval  = 500;
pool_usage_prob     = 0.3;

fprintf('Attacker Q-table: %d x %d\n', atk_state_size, atk_n_actions);

% =====================================================
% FIX 2: ACTION MASKING — only fires at catastrophic state
% Old thresholds (infection>0.10, skepticism>0.50, momentum>0.60,
% combined>0.35) were firing 25-28% of the time and blocking
% CoADAM's primary differentiating mechanism (deception).
% New: only mask when infection>0.60 AND skepticism>0.80 simultaneously.
% =====================================================

DECEPTION_HEAVY_IDX = 2;

fprintf('Action Masking: DeceptionHeavy masked only when infection>0.60 AND skepticism>0.80\n\n');

% =====================================================
% TRACKING ARRAYS
% =====================================================

trk_def_reward  = zeros(1, n_episodes);
trk_atk_reward  = zeros(1, n_episodes);
trk_amr         = zeros(1, n_episodes);
trk_infection   = zeros(1, n_episodes);
trk_dsr         = zeros(1, n_episodes);
trk_far         = zeros(1, n_episodes);
trk_mttd        = zeros(1, n_episodes);
trk_dwell       = zeros(1, n_episodes);
trk_dce         = zeros(1, n_episodes);
trk_eps_def     = zeros(1, n_episodes);
trk_eps_atk     = zeros(1, n_episodes);
trk_ep_length   = zeros(1, n_episodes);
trk_momentum    = zeros(1, n_episodes);
trk_skepticism  = zeros(1, n_episodes);
trk_budget      = zeros(1, n_episodes);
trk_loss        = zeros(1, n_episodes);
trk_mask_count  = zeros(1, n_episodes);
trk_pool_used   = zeros(1, n_episodes);

episode_metrics_log = cell(1, n_episodes);

convergence_window    = 500;
convergence_threshold = 0.02;
convergence_episode   = NaN;

checkpoint_eps = [1000, 2000, 3000, 4000, 5000];

def_action_counts      = zeros(1, dqn_output);
mask_trigger_total     = 0;
total_action_selections = 0;

% =====================================================
% TRAINING LOOP
% =====================================================

fprintf('Starting training...\n');
fprintf('========================================================================\n');

train_start = tic;
last_print  = tic;
total_steps = 0;

for ep = 1:n_episodes

    [def_raw, atk_raw] = env.reset(42 + ep);
    atk_idx = discretize_state_fn(atk_raw, atk_bins);

    use_pool = (rand() < pool_usage_prob) && (pool_count > 0);
    if use_pool
        pool_idx       = randi(pool_count);
        episode_atk_Q  = attacker_pool{pool_idx};
    else
        episode_atk_Q  = atk_Q;
    end
    trk_pool_used(ep) = use_pool;

    ep_def_r   = 0;
    ep_atk_r   = 0;
    ep_loss    = 0;
    ep_updates = 0;
    ep_mask_count = 0;
    done = false;

    for t = 1:max_steps
        if done, break; end
        total_steps = total_steps + 1;
        total_action_selections = total_action_selections + 1;

        % ------------------------------------------------------------------
        % FIX 2: Masking condition — only catastrophic state
        % ------------------------------------------------------------------
        current_infection  = def_raw(1);
        current_skepticism = def_raw(6);   % FIX 3: correct index (was 4 in Phase 5)

        mask_deception = (current_infection > 0.60) && (current_skepticism > 0.80);

        % ---- DEFENDER ACTION ----
        if rand() < dqn_epsilon
            if mask_deception
                valid_actions = setdiff(1:dqn_output, DECEPTION_HEAVY_IDX);
                def_a = valid_actions(randi(length(valid_actions)));
            else
                def_a = randi(dqn_output);
            end
        else
            q_vals = forward_pass(def_raw, W1, b1, W2, b2, W3, b3);
            if mask_deception
                q_vals(DECEPTION_HEAVY_IDX) = -inf;
                ep_mask_count  = ep_mask_count + 1;
                mask_trigger_total = mask_trigger_total + 1;
            end
            temperature = max(0.25, 1.0 * 0.9995^ep);
            q_shifted = q_vals - max(q_vals);
            q_probs   = exp(q_shifted / temperature) / ...
                        sum(exp(q_shifted / temperature));
            cum_probs = cumsum(q_probs);
            def_a = find(cum_probs >= rand(), 1, 'first');
        end
        def_action_counts(def_a) = def_action_counts(def_a) + 1;

        % ---- ATTACKER ACTION ----
        if rand() < atk_epsilon
            atk_a = randi(atk_n_actions);
        else
            qv    = episode_atk_Q(atk_idx, :);
            mx    = max(qv);
            cands = find(qv == mx);
            atk_a = cands(randi(length(cands)));
        end

        % ---- ENVIRONMENT STEP ----
        [next_def_raw, next_atk_raw, def_r, atk_r, done, ~] = ...
            env.step(def_a, atk_a);
        next_atk_idx = discretize_state_fn(next_atk_raw, atk_bins);

        % ---- STORE IN REPLAY BUFFER ----
        buf_idx = mod(replay_ptr, replay_cap) + 1;
        replay_s(buf_idx, :)  = def_raw;
        replay_a(buf_idx)     = def_a;
        replay_r(buf_idx)     = def_r;
        replay_ns(buf_idx, :) = next_def_raw;
        replay_d(buf_idx)     = done;
        replay_ptr = replay_ptr + 1;
        if replay_ptr >= replay_cap, replay_full = true; end

        % ---- ATTACKER Q-UPDATE ----
        if done
            atk_Q(atk_idx, atk_a) = atk_Q(atk_idx, atk_a) + ...
                atk_lr * (atk_r - atk_Q(atk_idx, atk_a));
        else
            atk_Q(atk_idx, atk_a) = atk_Q(atk_idx, atk_a) + ...
                atk_lr * (atk_r + atk_gamma * max(atk_Q(next_atk_idx, :)) ...
                - atk_Q(atk_idx, atk_a));
        end
        atk_visits(atk_idx, atk_a) = atk_visits(atk_idx, atk_a) + 1;

        % ---- DQN MINI-BATCH UPDATE ----
        buf_size = min(replay_ptr, replay_cap);
        if buf_size >= batch_size
            samp = randperm(buf_size, batch_size);

            gW1 = zeros(size(W1)); gb1 = zeros(size(b1));
            gW2 = zeros(size(W2)); gb2 = zeros(size(b2));
            gW3 = zeros(size(W3)); gb3 = zeros(size(b3));
            batch_loss = 0;

            for b = 1:batch_size
                si     = samp(b);
                cur_q  = forward_pass(replay_s(si,:),  W1,   b1,   W2,   b2,   W3,   b3);
                nxt_q  = forward_pass(replay_ns(si,:), W1_t, b1_t, W2_t, b2_t, W3_t, b3_t);

                if replay_d(si)
                    tgt = replay_r(si);
                else
                    tgt = replay_r(si) + dqn_gamma * max(nxt_q);
                end

                td_err = tgt - cur_q(replay_a(si));
                td_err = max(-grad_clip, min(grad_clip, td_err));
                batch_loss = batch_loss + td_err^2;

                [dW1, db1_, dW2, db2_, dW3, db3_] = backprop(...
                    replay_s(si,:), replay_a(si), td_err, ...
                    W1, b1, W2, b2, W3, b3);

                gW1 = gW1 + dW1; gb1 = gb1 + db1_;
                gW2 = gW2 + dW2; gb2 = gb2 + db2_;
                gW3 = gW3 + dW3; gb3 = gb3 + db3_;
            end

            scale = dqn_lr / batch_size;
            W1 = W1 + scale * gW1; b1 = b1 + scale * gb1;
            W2 = W2 + scale * gW2; b2 = b2 + scale * gb2;
            W3 = W3 + scale * gW3; b3 = b3 + scale * gb3;

            ep_loss    = ep_loss + batch_loss / batch_size;
            ep_updates = ep_updates + 1;
        end

        ep_def_r = ep_def_r + def_r;
        ep_atk_r = ep_atk_r + atk_r;

        def_raw  = next_def_raw;
        atk_idx  = next_atk_idx;
    end

    % ---- TARGET NETWORK UPDATE ----
    if mod(ep, target_update_freq) == 0
        W1_t = W1; b1_t = b1;
        W2_t = W2; b2_t = b2;
        W3_t = W3; b3_t = b3;
    end

    % ---- SAVE ATTACKER SNAPSHOT TO POOL ----
    if mod(ep, pool_save_interval) == 0
        pool_count = min(pool_count + 1, attacker_pool_size);
        slot = mod(floor(ep / pool_save_interval) - 1, attacker_pool_size) + 1;
        attacker_pool{slot} = atk_Q;
        fprintf('  >> Attacker snapshot saved to pool slot %d (pool size: %d)\n', ...
            slot, pool_count);
    end

    % ---- COLLECT EPISODE METRICS ----
    ep_metrics = env.get_episode_metrics();
    episode_metrics_log{ep} = ep_metrics;

    trk_def_reward(ep) = ep_def_r;
    trk_atk_reward(ep) = ep_atk_r;
    trk_amr(ep)        = ep_metrics.AMR;
    trk_infection(ep)  = ep_metrics.InfectionRate;
    trk_dsr(ep)        = ep_metrics.DSR;
    trk_far(ep)        = ep_metrics.FAR;
    trk_mttd(ep)       = ep_metrics.MTTD;
    trk_dwell(ep)      = ep_metrics.AttackerDwellTime;
    trk_dce(ep)        = ep_metrics.DefenseCostEfficiency;
    trk_eps_def(ep)    = dqn_epsilon;
    trk_eps_atk(ep)    = atk_epsilon;
    trk_ep_length(ep)  = ep_metrics.EpisodeLength;
    trk_momentum(ep)   = ep_metrics.FinalMomentum;
    trk_skepticism(ep) = ep_metrics.FinalSkepticism;
    trk_budget(ep)     = ep_metrics.BudgetRemaining;
    trk_mask_count(ep) = ep_mask_count;
    if ep_updates > 0
        trk_loss(ep) = ep_loss / ep_updates;
    end

    % ---- EPSILON DECAY ----
    dqn_epsilon = max(dqn_eps_min, dqn_epsilon * dqn_eps_decay);
    atk_epsilon = max(atk_eps_min, atk_epsilon * atk_eps_decay);

    % ---- CONVERGENCE DETECTION ----
    if ep > 2 * convergence_window && isnan(convergence_episode)
        recent  = mean(trk_def_reward(ep-convergence_window+1:ep));
        earlier = mean(trk_def_reward(ep-2*convergence_window+1:ep-convergence_window));
        if earlier ~= 0
            pct_change = abs(recent - earlier) / abs(earlier);
            if pct_change < convergence_threshold
                convergence_episode = ep;
                fprintf('  >> Convergence detected at episode %d (%.1f%% change)\n', ...
                    ep, pct_change*100);
            end
        end
    end

    % ---- CHECKPOINTS ----
    if ismember(ep, checkpoint_eps)
        ckpt_path = fullfile(checkpoint_dir, sprintf('checkpoint_ep%d.mat', ep));
        save(ckpt_path, 'W1', 'b1', 'W2', 'b2', 'W3', 'b3', ...
            'W1_t', 'b1_t', 'W2_t', 'b2_t', 'W3_t', 'b3_t', ...
            'atk_Q', 'atk_visits', 'attacker_pool', 'pool_count', ...
            'ep', 'dqn_epsilon', 'atk_epsilon');
        fprintf('  >> Checkpoint saved at episode %d\n', ep);
    end

    % ---- PROGRESS PRINTING ----
    if toc(last_print) > 30 || ismember(ep, [1,500,1000,1500,2000,2500,3000,3500,4000,4500,5000])
        elapsed     = toc(train_start);
        eps_per_sec = ep / elapsed;
        eta         = (n_episodes - ep) / eps_per_sec;
        mask_pct    = 0;
        if total_action_selections > 0
            mask_pct = mask_trigger_total / total_action_selections * 100;
        end
        fprintf('Ep %4d/%d | DefR=%6.1f AMR=%.3f Inf=%.3f DSR=%.3f | ', ...
            ep, n_episodes, ep_def_r, ep_metrics.AMR, ...
            ep_metrics.InfectionRate, ep_metrics.DSR);
        fprintf('AtkR=%6.1f | eps=%.3f/%.3f | mask=%.1f%% pool=%d | %.1f ep/s ETA %.0fs\n', ...
            ep_atk_r, dqn_epsilon, atk_epsilon, mask_pct, use_pool, ...
            eps_per_sec, eta);
        last_print = tic;
    end
end

total_time = toc(train_start);
fprintf('========================================================================\n');
fprintf('Training complete. Time: %.1f seconds (%.1f minutes)\n', ...
    total_time, total_time/60);
fprintf('Action masking triggered: %.2f%% of selections\n', ...
    mask_trigger_total / total_action_selections * 100);
fprintf('Pool episodes: %.1f%%\n\n', sum(trk_pool_used) / n_episodes * 100);

% =====================================================
% EVALUATION (100 episodes, greedy)
% =====================================================

fprintf('Running evaluation (100 episodes, greedy)...\n');
n_eval = 100;
eval_metrics_all  = cell(1, n_eval);
eval_action_counts = zeros(1, dqn_output);
eval_mask_total   = 0;
eval_step_total   = 0;

for ep = 1:n_eval
    [def_raw, atk_raw] = env.reset(10000 + ep);
    atk_idx = discretize_state_fn(atk_raw, atk_bins);
    done = false;

    for t = 1:max_steps
        if done, break; end
        eval_step_total = eval_step_total + 1;

        % FIX 2: same corrected masking condition
        current_infection  = def_raw(1);
        current_skepticism = def_raw(6);
        mask_deception = (current_infection > 0.60) && (current_skepticism > 0.80);

        q_vals = forward_pass(def_raw, W1, b1, W2, b2, W3, b3);
        if mask_deception
            q_vals(DECEPTION_HEAVY_IDX) = -inf;
            eval_mask_total = eval_mask_total + 1;
        end

        eval_temp = 0.2;
        q_shifted = q_vals - max(q_vals);
        q_probs   = exp(q_shifted / eval_temp) / sum(exp(q_shifted / eval_temp));
        cum_probs = cumsum(q_probs);
        def_a     = find(cum_probs >= rand(), 1, 'first');
        eval_action_counts(def_a) = eval_action_counts(def_a) + 1;

        qv    = atk_Q(atk_idx, :);
        mx    = max(qv);
        cands = find(qv == mx);
        atk_a = cands(randi(length(cands)));

        [next_def_raw, next_atk_raw, ~, ~, done, ~] = env.step(def_a, atk_a);
        def_raw = next_def_raw;
        atk_idx = discretize_state_fn(next_atk_raw, atk_bins);
    end
    eval_metrics_all{ep} = env.get_episode_metrics();
end

eval_amr  = cellfun(@(x) x.AMR,                    eval_metrics_all);
eval_inf  = cellfun(@(x) x.InfectionRate,           eval_metrics_all);
eval_rew  = cellfun(@(x) x.CumulativeReward,        eval_metrics_all);
eval_dsr  = cellfun(@(x) x.DSR,                     eval_metrics_all);
eval_far  = cellfun(@(x) x.FAR,                     eval_metrics_all);
eval_mttd = cellfun(@(x) x.MTTD,                    eval_metrics_all);
eval_dwell = cellfun(@(x) x.AttackerDwellTime,      eval_metrics_all);
eval_dce  = cellfun(@(x) x.DefenseCostEfficiency,   eval_metrics_all);
eval_atk_rew = cellfun(@(x) x.AttackerCumulativeReward, eval_metrics_all);
eval_length  = cellfun(@(x) x.EpisodeLength,        eval_metrics_all);

sorted_rew = sort(eval_rew);
n_tail     = max(1, floor(0.05 * n_eval));
eval_cvar  = mean(sorted_rew(1:n_tail));
eval_dr    = iqr(eval_rew);

fprintf('Evaluation complete.\n');
fprintf('  Eval masking rate: %.2f%%\n', eval_mask_total / eval_step_total * 100);
fprintf('  Eval action dist: ');
eval_pct = eval_action_counts / sum(eval_action_counts) * 100;
for a = 1:dqn_output
    fprintf('%s=%.1f%% ', config.strategy_names{a}, eval_pct(a));
end
fprintf('\n\n');

% =====================================================
% REPORT
% =====================================================

report_path = fullfile(phase3_dir, 'dqn_cotraining_report_v3.txt');
fid = fopen(report_path, 'w');

dual_print(fid, 'CoADAM DQN Co-Evolutionary Training Report v3\n');
dual_print(fid, 'Timestamp: %s\n', char(datetime('now')));
dual_print(fid, 'Fixes applied: (1) diversity reward removed, (2) masking threshold corrected\n');
dual_print(fid, '====================================================\n\n');

dual_print(fid, '--- Training Configuration ---\n\n');
dual_print(fid, '  Episodes: %d\n', n_episodes);
dual_print(fid, '  Steps per episode: %d\n', max_steps);
dual_print(fid, '  Total interactions: %d\n', total_steps);
dual_print(fid, '  Training time: %.1f seconds (%.1f minutes)\n', ...
    total_time, total_time/60);
dual_print(fid, '  DQN: lr=%.4f, gamma=%.2f, eps=[0.15->%.4f, decay=%.4f]\n', ...
    dqn_lr, dqn_gamma, dqn_epsilon, dqn_eps_decay);
dual_print(fid, '  DQN: batch=%d, replay=%d, target_update=%d, grad_clip=%.1f\n', ...
    batch_size, replay_cap, target_update_freq, grad_clip);
dual_print(fid, '  Masking rate (training): %.2f%%\n', ...
    mask_trigger_total / total_action_selections * 100);
dual_print(fid, '  Convergence detected: ');
if ~isnan(convergence_episode)
    dual_print(fid, 'Episode %d\n', convergence_episode);
else
    dual_print(fid, 'Not reached\n');
end
dual_print(fid, '\n');

dual_print(fid, '--- Convergence Analysis ---\n\n');
windows = {1:500, 501:1000, 1001:2000, 2001:3000, 3001:4000, 4001:5000};
window_labels = {'Ep1-500','Ep501-1k','Ep1k-2k','Ep2k-3k','Ep3k-4k','Ep4k-5k'};
conv_metrics = {'DefReward','AMR','Infection','DSR','MTTD','MaskRate'};
conv_data    = {trk_def_reward, trk_amr, trk_infection, trk_dsr, trk_mttd, trk_mask_count};

dual_print(fid, '  %-12s', 'Metric');
for w = 1:length(windows)
    dual_print(fid, ' %10s', window_labels{w});
end
dual_print(fid, '\n  %s\n', repmat('-', 1, 75));
for m = 1:length(conv_metrics)
    dual_print(fid, '  %-12s', conv_metrics{m});
    for w = 1:length(windows)
        idx = windows{w};
        if max(idx) <= n_episodes
            dual_print(fid, ' %10.3f', mean(conv_data{m}(idx)));
        end
    end
    dual_print(fid, '\n');
end
dual_print(fid, '\n');

dual_print(fid, '--- Defender Action Distribution (Training) ---\n\n');
action_pct = def_action_counts / sum(def_action_counts) * 100;
for i = 1:dqn_output
    dual_print(fid, '  %-20s %6.1f%%\n', config.strategy_names{i}, action_pct(i));
end
dual_print(fid, '\n');

dual_print(fid, '--- Defender Action Distribution (Evaluation) ---\n\n');
for i = 1:dqn_output
    dual_print(fid, '  %-20s %6.1f%%\n', config.strategy_names{i}, eval_pct(i));
end
dual_print(fid, '\n');

dual_print(fid, '--- Evaluation Results (100 episodes) ---\n\n');
eval_names  = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
    'MTTD','AttackerDwellTime','DefenseCostEfficiency', ...
    'AttackerCumulativeReward','EpisodeLength'};
eval_arrays = {eval_amr, eval_dsr, eval_far, eval_rew, eval_inf, ...
    eval_mttd, eval_dwell, eval_dce, eval_atk_rew, eval_length};

dual_print(fid, '  %-28s %10s %10s %10s %10s %10s\n', ...
    'Metric','Mean','Std','Min','Max','Median');
dual_print(fid, '  %s\n', repmat('-', 1, 78));
for m = 1:length(eval_names)
    v = eval_arrays{m};
    dual_print(fid, '  %-28s %10.4f %10.4f %10.4f %10.4f %10.4f\n', ...
        eval_names{m}, mean(v), std(v), min(v), max(v), median(v));
end
dual_print(fid, '\n  CVaR (alpha=0.05): %.4f\n', eval_cvar);
dual_print(fid, '  Training Reliability (DR): %.4f\n', eval_dr);
dual_print(fid, '\n');

% Compare with tabular if available
dual_print(fid, '--- Comparison with Tabular Q-Learning ---\n\n');
try
    tab_res  = load(fullfile(results_dir, 'cotraining_results.mat'), 'eval_results');
    tab_eval = tab_res.eval_results;
    comp_names   = {'AMR','InfectionRate','DSR','CumulativeReward','MTTD','FAR'};
    tab_vals     = [tab_eval.AMR.mean, tab_eval.InfectionRate.mean, ...
        tab_eval.DSR.mean, tab_eval.CumulativeReward.mean, ...
        tab_eval.MTTD.mean, tab_eval.FAR.mean];
    dqn_vals     = [mean(eval_amr), mean(eval_inf), mean(eval_dsr), ...
        mean(eval_rew), mean(eval_mttd), mean(eval_far)];
    better_higher = [true, false, true, true, false, false];

    dual_print(fid, '  %-25s %12s %12s %12s\n', 'Metric','Tabular','DQN_v3','Improvement');
    dual_print(fid, '  %s\n', repmat('-', 1, 61));
    for m = 1:length(comp_names)
        diff_val = dqn_vals(m) - tab_vals(m);
        if tab_vals(m) ~= 0
            pct = diff_val / abs(tab_vals(m)) * 100;
        else
            pct = 0;
        end
        if better_higher(m)
            direction = ternary_str(diff_val >= 0, 'better', 'worse');
        else
            direction = ternary_str(diff_val <= 0, 'better', 'worse');
        end
        dual_print(fid, '  %-25s %12.4f %12.4f %+10.1f%% (%s)\n', ...
            comp_names{m}, tab_vals(m), dqn_vals(m), pct, direction);
    end
catch
    dual_print(fid, '  (Tabular results not available)\n');
end

dual_print(fid, '\n====================================================\n');
dual_print(fid, 'Phase 3-4 v3 complete.\n');

save_path = fullfile(results_dir, 'dqn_cotraining_results.mat');
save(save_path, ...
    'W1','b1','W2','b2','W3','b3', ...
    'W1_t','b1_t','W2_t','b2_t','W3_t','b3_t', ...
    'atk_Q','atk_visits','attacker_pool','pool_count', ...
    'trk_def_reward','trk_atk_reward','trk_amr','trk_infection', ...
    'trk_dsr','trk_far','trk_mttd','trk_dwell','trk_dce', ...
    'trk_eps_def','trk_eps_atk','trk_ep_length', ...
    'trk_momentum','trk_skepticism','trk_budget','trk_loss', ...
    'trk_mask_count','trk_pool_used', ...
    'episode_metrics_log','eval_metrics_all', ...
    'eval_amr','eval_inf','eval_rew','eval_dsr','eval_far', ...
    'eval_mttd','eval_dwell','eval_dce','eval_atk_rew','eval_length', ...
    'eval_cvar','eval_dr', ...
    'def_action_counts','eval_action_counts', ...
    'convergence_episode','mask_trigger_total','total_action_selections', ...
    'n_episodes','total_time','total_steps', ...
    'dqn_lr','dqn_gamma','dqn_eps_decay','batch_size', ...
    'replay_cap','target_update_freq','grad_clip','n_params', ...
    '-v7.3');

dual_print(fid, 'Results saved to: %s\n', save_path);
dual_print(fid, 'Report saved to: %s\n', report_path);
fclose(fid);
fprintf('\nDone. Report saved to: %s\n', report_path);

% =====================================================
% HELPER FUNCTIONS
% =====================================================

function idx = discretize_state_fn(state, n_bins)
    n = length(state);
    idx = 0;
    multiplier = 1;
    for i = 1:n
        val = max(0, min(1 - 1e-10, state(i)));
        bin = floor(val * n_bins(i));
        idx = idx + bin * multiplier;
        multiplier = multiplier * n_bins(i);
    end
    idx = idx + 1;
end

function q = forward_pass(state, W1, b1, W2, b2, W3, b3)
    x  = state(:);
    h1 = max(0, W1 * x + b1);
    h2 = max(0, W2 * h1 + b2);
    q  = (W3 * h2 + b3)';
end

function [dW1, db1, dW2, db2, dW3, db3] = backprop(state, action, td_error, ...
        W1, b1, W2, b2, W3, b3)
    x  = state(:);
    z1 = W1 * x + b1;
    h1 = max(0, z1);
    z2 = W2 * h1 + b2;
    h2 = max(0, z2);

    dq = zeros(size(W3, 1), 1);
    dq(action) = td_error;

    dW3 = dq * h2';
    db3 = dq;
    dh2 = W3' * dq;

    dz2 = dh2 .* (z2 > 0);
    dW2 = dz2 * h1';
    db2 = dz2;
    dh1 = W2' * dz2;

    dz1 = dh1 .* (z1 > 0);
    dW1 = dz1 * x';
    db1 = dz1;
end

function s = ternary_str(cond, a, b)
    if cond, s = a; else, s = b; end
end

function dual_print(fid, varargin)
    fprintf(varargin{:});
    if fid > 0
        fprintf(fid, varargin{:});
    end
end
