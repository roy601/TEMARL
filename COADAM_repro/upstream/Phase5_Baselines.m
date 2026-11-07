%%
% CoADAM Phase 5: Baseline Comparison (Final)
%
% Key fix in this version:
%   TABLE B now uses a METHOD-SPECIFIC adaptive attacker for each baseline.
%   Each method's attacker is fine-tuned for 1000 episodes against that
%   specific defense before the 100 evaluation episodes.
%   This removes the artificial advantage given to Static/Heuristic/Stackelberg
%   which previously showed 0.000 infection only because the CoADAM-trained
%   attacker had never seen their action space.
%
%   Fix 3 retained: CoADAM state indices s(6)=skepticism, s(5)=momentum
%   Fix 2 retained: masking only at infection>0.60 AND skepticism>0.80
%
% Date: 01-Mar-2026 (Final)
%%

clear; clc;
fprintf('CoADAM Phase 5: Baseline Comparison (Final)\n');
fprintf('Timestamp: %s\n', char(datetime('now')));
fprintf('=====================================\n\n');

project_root  = '/Users/ujw/Desktop/CoADAM';
processed_dir = fullfile(project_root, 'data', 'processed');
phase2_dir    = fullfile(project_root, 'phase2_environment');
phase3_dir    = fullfile(project_root, 'phase3_defender');
phase5_dir    = fullfile(project_root, 'phase5_baselines');
results_dir   = fullfile(project_root, 'results');

if ~exist(phase5_dir, 'dir'), mkdir(phase5_dir); end
if ~exist(results_dir,'dir'), mkdir(results_dir); end
addpath(phase2_dir);
addpath(phase3_dir);

fprintf('Loading configuration...\n');
load(fullfile(processed_dir, 'environment_config.mat'), 'config');

fprintf('Loading trained CoADAM models...\n');
trained = load(fullfile(results_dir, 'dqn_cotraining_results.mat'), ...
    'W1','W2','W3','b1','b2','b3','atk_Q');

W1 = trained.W1; W2 = trained.W2; W3 = trained.W3;
b1 = trained.b1; b2 = trained.b2; b3 = trained.b3;
atk_Q_base = trained.atk_Q;   % kept as base; never modified directly
atk_bins   = config.attacker_state.n_bins;
atk_gamma  = config.training.attacker.gamma;

% With this block:
tab_path    = fullfile(results_dir, 'cotraining_results.mat');
has_tabular = false;
tab_Q       = [];
def_bins    = [];
if isfile(tab_path)
    tab_vars = who('-file', tab_path);
    if ismember('def_Q', tab_vars)
        tab_data    = load(tab_path, 'def_Q');
        tab_Q       = tab_data.def_Q;
        def_bins    = config.defender_state.n_bins;
        has_tabular = true;
        fprintf('Tabular Q-learning model loaded.\n');
    else
        fprintf('Tabular file found but def_Q missing, skipping.\n');
    end
else
    fprintf('Tabular Q-learning file not found, skipping.\n');
end

n_eval        = 100;
max_steps     = config.episode.max_steps;
n_def_actions = config.n_defender_actions;
n_atk_actions = config.n_attacker_actions;

fprintf('Evaluating each baseline for %d episodes.\n\n', n_eval);

%%
% DEFINE METHODS
%%

method_names = {'Static','Random','Heuristic','DQN_Individual', ...
    'Deception_Only','Stackelberg','Tabular_QL','CoADAM_DQN'};
n_methods = length(method_names);

%%
% TRAIN DQN_INDIVIDUAL BASELINE
%%

fprintf('--- Pre-training: DQN Individual Mechanisms ---\n');

indiv_input  = config.defender_state.n_features;
indiv_h1     = 128;
indiv_h2     = 64;
indiv_output = config.n_mechanisms;

rng(99);
iW1 = randn(indiv_h1, indiv_input) * sqrt(2 / indiv_input);
ib1 = zeros(indiv_h1, 1);
iW2 = randn(indiv_h2, indiv_h1)    * sqrt(2 / indiv_h1);
ib2 = zeros(indiv_h2, 1);
iW3 = randn(indiv_output, indiv_h2) * sqrt(2 / indiv_h2);
ib3 = zeros(indiv_output, 1);

iW1_t = iW1; ib1_t = ib1;
iW2_t = iW2; ib2_t = ib2;
iW3_t = iW3; ib3_t = ib3;

indiv_bundles = zeros(config.n_mechanisms, config.n_mechanisms);
for m = 1:config.n_mechanisms
    indiv_bundles(m, :) = 0.05;
    indiv_bundles(m, m) = 0.75;
end

irep_cap = 50000;
irep_s   = zeros(irep_cap, indiv_input);
irep_a   = zeros(irep_cap, 1);
irep_r   = zeros(irep_cap, 1);
irep_ns  = zeros(irep_cap, indiv_input);
irep_d   = zeros(irep_cap, 1);
irep_ptr = 0;

indiv_lr        = 0.0005;
indiv_gamma     = 0.85;
indiv_eps       = 0.15;
indiv_eps_decay = 0.999;
indiv_eps_min   = 0.05;
indiv_batch     = 64;
n_indiv_episodes = 3000;

env_indiv = iiot_environment(config);
fprintf('  Training DQN Individual (3000 episodes vs random attacker)...\n');
indiv_train_start = tic;

for ep = 1:n_indiv_episodes
    [def_raw, ~] = env_indiv.reset(200 + ep);

    for t = 1:max_steps
        if rand() < indiv_eps
            def_a = randi(indiv_output);
        else
            q = forward_pass_fn(def_raw, iW1, ib1, iW2, ib2, iW3, ib3);
            [~, def_a] = max(q);
        end

        atk_a = randi(n_atk_actions);

        orig_bundles = config.strategy_bundles;
        config.strategy_bundles   = indiv_bundles;
        config.n_defender_actions = config.n_mechanisms;
        env_indiv.config = config;

        [next_def_raw, ~, def_r, ~, done, ~] = env_indiv.step(def_a, atk_a);

        config.strategy_bundles   = orig_bundles;
        config.n_defender_actions = n_def_actions;
        env_indiv.config = config;

        buf_idx = mod(irep_ptr, irep_cap) + 1;
        irep_s(buf_idx,:)  = def_raw;
        irep_a(buf_idx)    = def_a;
        irep_r(buf_idx)    = def_r;
        irep_ns(buf_idx,:) = next_def_raw;
        irep_d(buf_idx)    = done;
        irep_ptr = irep_ptr + 1;

        buf_size = min(irep_ptr, irep_cap);
        if buf_size >= indiv_batch
            samp = randperm(buf_size, indiv_batch);
            gW1=zeros(size(iW1)); gb1_=zeros(size(ib1));
            gW2=zeros(size(iW2)); gb2_=zeros(size(ib2));
            gW3=zeros(size(iW3)); gb3_=zeros(size(ib3));
            for b = 1:indiv_batch
                si    = samp(b);
                cur_q = forward_pass_fn(irep_s(si,:),  iW1,   ib1,   iW2,   ib2,   iW3,   ib3);
                nxt_q = forward_pass_fn(irep_ns(si,:), iW1_t, ib1_t, iW2_t, ib2_t, iW3_t, ib3_t);
                if irep_d(si), tgt = irep_r(si);
                else, tgt = irep_r(si) + indiv_gamma * max(nxt_q); end
                td_err = max(-1, min(1, tgt - cur_q(irep_a(si))));
                [dW1_,db1__,dW2_,db2__,dW3_,db3__] = backprop_fn(...
                    irep_s(si,:), irep_a(si), td_err, ...
                    iW1, ib1, iW2, ib2, iW3, ib3);
                gW1=gW1+dW1_; gb1_=gb1_+db1__;
                gW2=gW2+dW2_; gb2_=gb2_+db2__;
                gW3=gW3+dW3_; gb3_=gb3_+db3__;
            end
            scale = indiv_lr / indiv_batch;
            iW1=iW1+scale*gW1; ib1=ib1+scale*gb1_;
            iW2=iW2+scale*gW2; ib2=ib2+scale*gb2_;
            iW3=iW3+scale*gW3; ib3=ib3+scale*gb3_;
        end

        def_raw = next_def_raw;
        if done, break; end
    end

    if mod(ep,100)==0
        iW1_t=iW1; ib1_t=ib1;
        iW2_t=iW2; ib2_t=ib2;
        iW3_t=iW3; ib3_t=ib3;
    end
    indiv_eps = max(indiv_eps_min, indiv_eps * indiv_eps_decay);
    if mod(ep,500)==0 || ep==1
        fprintf('  Ep %4d/%d | eps=%.3f | %.1f ep/s\n', ...
            ep, n_indiv_episodes, indiv_eps, ep/toc(indiv_train_start));
    end
end
indiv_train_time = toc(indiv_train_start);
fprintf('  DQN Individual training complete (%.1f s)\n\n', indiv_train_time);

%%
% TRAIN DECEPTION-ONLY BASELINE
%%

fprintf('--- Pre-training: Deception-Only RL ---\n');

dec_bundles = [
    0.50, 0.05, 0.05, 0.05, 0.05, 0.30;
    0.30, 0.05, 0.05, 0.05, 0.05, 0.50;
];
n_dec_actions  = size(dec_bundles, 1);
dec_bins       = config.defender_state.n_bins;
dec_state_size = prod(dec_bins);
dec_Q          = zeros(dec_state_size, n_dec_actions);
dec_lr         = 0.001;
dec_gamma      = 0.80;
dec_eps        = 0.20;
dec_eps_decay  = 0.999;
dec_eps_min    = 0.05;
n_dec_episodes = 3000;

env_dec = iiot_environment(config);
dec_train_start = tic;

for ep = 1:n_dec_episodes
    [def_raw, ~] = env_dec.reset(300 + ep);

    orig_bundles = config.strategy_bundles;
    orig_n       = config.n_defender_actions;
    config.strategy_bundles   = dec_bundles;
    config.n_defender_actions = n_dec_actions;
    env_dec.config = config;

    def_idx = discretize_state_fn(def_raw, dec_bins);

    for t = 1:max_steps
        if rand() < dec_eps
            def_a = randi(n_dec_actions);
        else
            [~, def_a] = max(dec_Q(def_idx,:));
        end
        atk_a = randi(n_atk_actions);
        [next_def_raw, ~, def_r, ~, done, ~] = env_dec.step(def_a, atk_a);
        next_def_idx = discretize_state_fn(next_def_raw, dec_bins);
        if done
            dec_Q(def_idx,def_a) = dec_Q(def_idx,def_a) + ...
                dec_lr*(def_r - dec_Q(def_idx,def_a));
        else
            dec_Q(def_idx,def_a) = dec_Q(def_idx,def_a) + ...
                dec_lr*(def_r + dec_gamma*max(dec_Q(next_def_idx,:)) ...
                - dec_Q(def_idx,def_a));
        end
        def_raw = next_def_raw;
        def_idx = next_def_idx;
        if done, break; end
    end

    config.strategy_bundles   = orig_bundles;
    config.n_defender_actions = orig_n;
    env_dec.config = config;

    dec_eps = max(dec_eps_min, dec_eps * dec_eps_decay);
    if mod(ep,500)==0 || ep==1
        fprintf('  Ep %4d/%d | eps=%.3f | %.1f ep/s\n', ...
            ep, n_dec_episodes, dec_eps, ep/toc(dec_train_start));
    end
end
dec_train_time = toc(dec_train_start);
fprintf('  Deception-Only training complete (%.1f s)\n\n', dec_train_time);

%%
% COMPUTE STACKELBERG EQUILIBRIUM
%%

fprintf('--- Computing Stackelberg Equilibrium ---\n');

n_stack_sim  = 50;
stack_payoff = zeros(n_def_actions, config.n_attacker_tactics);
env_stack    = iiot_environment(config);

for da = 1:n_def_actions
    for at = 1:config.n_attacker_tactics
        rewards_tmp = zeros(1, n_stack_sim);
        for sim = 1:n_stack_sim
            env_stack.reset(400 + da*100 + at*10 + sim);
            for t = 1:max_steps
                atk_a_idx = (at-1)*config.n_intensity*config.n_zones + ...
                    (2-1)*config.n_zones + randi(config.n_zones);
                [~,~,def_r,~,done,~] = env_stack.step(da, atk_a_idx);
                rewards_tmp(sim) = rewards_tmp(sim) + def_r;
                if done, break; end
            end
        end
        stack_payoff(da,at) = mean(rewards_tmp);
    end
end
stack_br_payoff = zeros(1, n_def_actions);
for da = 1:n_def_actions
    stack_br_payoff(da) = min(stack_payoff(da,:));
end
[~, stack_action] = max(stack_br_payoff);
fprintf('  Stackelberg equilibrium action: %d (%s)\n\n', ...
    stack_action, config.strategy_names{stack_action});

%%
% HELPER: GET DEFENDER ACTION FOR A GIVEN METHOD
%%
% Extracted as inline logic below to avoid nested function issues in MATLAB.
% Called identically in Table A, Table B, and adaptation sections.

%%
% TABLE A: RANDOM ATTACKER
%%

fprintf('========================================\n');
fprintf('TABLE A: Random Attacker\n');
fprintf('========================================\n\n');

results_tableA = cell(n_methods, 1);

for mi = 1:n_methods
    method = method_names{mi};
    fprintf('--- %s ---\n', method);

    env_eval = iiot_environment(config);
    if strcmp(method,'CoADAM_DQN')
        env_eval.intel_boost_enabled = true;
    else
        env_eval.intel_boost_enabled = false;
    end

    ep_metrics = cell(1, n_eval);

    for ep = 1:n_eval
        [def_raw, atk_raw] = env_eval.reset(5000 + mi*100 + ep);

        switch method
            case 'DQN_Individual'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = indiv_bundles;
                config.n_defender_actions = config.n_mechanisms;
                env_eval.config = config;
            case 'Deception_Only'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = dec_bundles;
                config.n_defender_actions = n_dec_actions;
                env_eval.config = config;
        end

        for t = 1:max_steps
            def_a = get_def_action(method, def_raw, n_def_actions, ...
                iW1,ib1,iW2,ib2,iW3,ib3, dec_Q,dec_bins, ...
                tab_Q,def_bins,has_tabular, stack_action, ...
                W1,b1,W2,b2,W3,b3);

            atk_a = randi(n_atk_actions);  % random attacker

            [def_raw, atk_raw, ~, ~, done, ~] = env_eval.step(def_a, atk_a);
            if done, break; end
        end

        switch method
            case {'DQN_Individual','Deception_Only'}
                config.strategy_bundles   = orig_bundles;
                config.n_defender_actions = orig_n;
                env_eval.config = config;
        end

        ep_metrics{ep} = env_eval.get_episode_metrics();
    end

    results_tableA{mi} = aggregate_metrics(ep_metrics, n_eval, method);
    fprintf('  AMR=%.4f, Inf=%.4f, DSR=%.4f, Reward=%.2f\n\n', ...
        results_tableA{mi}.AMR.mean, results_tableA{mi}.InfectionRate.mean, ...
        results_tableA{mi}.DSR.mean, results_tableA{mi}.CumulativeReward.mean);
end

%%
% TABLE B: METHOD-SPECIFIC ADAPTIVE ATTACKER
% For each method: fine-tune attacker for 1000 episodes against that
% specific defense, then evaluate for 100 episodes.
% This is the fair comparison — each method faces an attacker that has
% actually learned to exploit *that* method's weaknesses.
%%

fprintf('========================================\n');
fprintf('TABLE B: Method-Specific Adaptive Attacker\n');
fprintf('(Each method faces attacker fine-tuned 1000 eps against it)\n');
fprintf('========================================\n\n');

results_tableB = cell(n_methods, 1);
n_finetune = 1000;   % fine-tune episodes per method

for mi = 1:n_methods
    method = method_names{mi};
    fprintf('--- %s: fine-tuning attacker (%d eps) ---\n', method, n_finetune);

    % Start from CoADAM-trained attacker base
    ft_atk_Q      = atk_Q_base;
    ft_lr         = 0.002;
    ft_eps        = 0.20;
    ft_eps_decay  = 0.995;
    ft_eps_min    = 0.05;

    env_ft = iiot_environment(config);
    if strcmp(method,'CoADAM_DQN')
        env_ft.intel_boost_enabled = true;
    else
        env_ft.intel_boost_enabled = false;
    end

    ft_start = tic;

    for ep = 1:n_finetune
        [def_raw, atk_raw] = env_ft.reset(7000 + mi*1000 + ep);

        switch method
            case 'DQN_Individual'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = indiv_bundles;
                config.n_defender_actions = config.n_mechanisms;
                env_ft.config = config;
            case 'Deception_Only'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = dec_bundles;
                config.n_defender_actions = n_dec_actions;
                env_ft.config = config;
        end

        atk_idx = discretize_state_fn(atk_raw, atk_bins);

        for t = 1:max_steps
            def_a = get_def_action(method, def_raw, n_def_actions, ...
                iW1,ib1,iW2,ib2,iW3,ib3, dec_Q,dec_bins, ...
                tab_Q,def_bins,has_tabular, stack_action, ...
                W1,b1,W2,b2,W3,b3);

            if rand() < ft_eps
                atk_a = randi(n_atk_actions);
            else
                qv    = ft_atk_Q(atk_idx,:);
                mx    = max(qv);
                cands = find(qv==mx);
                atk_a = cands(randi(length(cands)));
            end

            [next_def_raw, next_atk_raw, ~, atk_r, done, ~] = ...
                env_ft.step(def_a, atk_a);
            next_atk_idx = discretize_state_fn(next_atk_raw, atk_bins);

            if done
                ft_atk_Q(atk_idx,atk_a) = ft_atk_Q(atk_idx,atk_a) + ...
                    ft_lr*(atk_r - ft_atk_Q(atk_idx,atk_a));
            else
                ft_atk_Q(atk_idx,atk_a) = ft_atk_Q(atk_idx,atk_a) + ...
                    ft_lr*(atk_r + atk_gamma*max(ft_atk_Q(next_atk_idx,:)) ...
                    - ft_atk_Q(atk_idx,atk_a));
            end

            def_raw = next_def_raw;
            atk_raw = next_atk_raw;
            atk_idx = next_atk_idx;
            if done, break; end
        end

        switch method
            case {'DQN_Individual','Deception_Only'}
                config.strategy_bundles   = orig_bundles;
                config.n_defender_actions = orig_n;
                env_ft.config = config;
        end

        ft_eps = max(ft_eps_min, ft_eps * ft_eps_decay);
    end

    fprintf('  Fine-tuning complete (%.1f s). Now evaluating...\n', toc(ft_start));

    % Evaluate against fine-tuned attacker
    ep_metrics = cell(1, n_eval);

    env_eval = iiot_environment(config);
    if strcmp(method,'CoADAM_DQN')
        env_eval.intel_boost_enabled = true;
    else
        env_eval.intel_boost_enabled = false;
    end

    for ep = 1:n_eval
        [def_raw, atk_raw] = env_eval.reset(8000 + mi*100 + ep);

        switch method
            case 'DQN_Individual'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = indiv_bundles;
                config.n_defender_actions = config.n_mechanisms;
                env_eval.config = config;
            case 'Deception_Only'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = dec_bundles;
                config.n_defender_actions = n_dec_actions;
                env_eval.config = config;
        end

        atk_idx = discretize_state_fn(atk_raw, atk_bins);

        for t = 1:max_steps
            def_a = get_def_action(method, def_raw, n_def_actions, ...
                iW1,ib1,iW2,ib2,iW3,ib3, dec_Q,dec_bins, ...
                tab_Q,def_bins,has_tabular, stack_action, ...
                W1,b1,W2,b2,W3,b3);

            atk_idx = discretize_state_fn(atk_raw, atk_bins);
            qv    = ft_atk_Q(atk_idx,:);
            mx    = max(qv);
            cands = find(qv==mx);
            atk_a = cands(randi(length(cands)));

            [def_raw, atk_raw, ~, ~, done, ~] = env_eval.step(def_a, atk_a);
            if done, break; end
        end

        switch method
            case {'DQN_Individual','Deception_Only'}
                config.strategy_bundles   = orig_bundles;
                config.n_defender_actions = orig_n;
                env_eval.config = config;
        end

        ep_metrics{ep} = env_eval.get_episode_metrics();
    end

    results_tableB{mi} = aggregate_metrics(ep_metrics, n_eval, method);
    fprintf('  AMR=%.4f, Inf=%.4f, DSR=%.4f, Reward=%.2f\n\n', ...
        results_tableB{mi}.AMR.mean, results_tableB{mi}.InfectionRate.mean, ...
        results_tableB{mi}.DSR.mean, results_tableB{mi}.CumulativeReward.mean);
end

%%
% ADVERSARIAL ADAPTATION TEST (500 eps, same as before)
%%

fprintf('========================================\n');
fprintf('ADVERSARIAL ADAPTATION TEST (500 eps)\n');
fprintf('========================================\n\n');

n_adapt_episodes = 500;
adapt_results    = cell(1, n_methods);

for mi = 1:n_methods
    method = method_names{mi};
    fprintf('--- Adapting attacker against: %s ---\n', method);

    adapted_Q       = atk_Q_base;
    adapt_lr        = 0.002;
    adapt_eps       = 0.20;
    adapt_eps_decay = 0.995;
    adapt_eps_min   = 0.05;

    env_adapt = iiot_environment(config);
    if strcmp(method,'CoADAM_DQN')
        env_adapt.intel_boost_enabled = true;
    else
        env_adapt.intel_boost_enabled = false;
    end

    for ep = 1:n_adapt_episodes
        [def_raw, atk_raw] = env_adapt.reset(20000 + mi*1000 + ep);

        switch method
            case 'DQN_Individual'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = indiv_bundles;
                config.n_defender_actions = config.n_mechanisms;
                env_adapt.config = config;
            case 'Deception_Only'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = dec_bundles;
                config.n_defender_actions = n_dec_actions;
                env_adapt.config = config;
        end

        adapt_atk_idx = discretize_state_fn(atk_raw, atk_bins);

        for t = 1:max_steps
            def_a = get_def_action(method, def_raw, n_def_actions, ...
                iW1,ib1,iW2,ib2,iW3,ib3, dec_Q,dec_bins, ...
                tab_Q,def_bins,has_tabular, stack_action, ...
                W1,b1,W2,b2,W3,b3);

            if rand() < adapt_eps
                atk_a = randi(n_atk_actions);
            else
                qv    = adapted_Q(adapt_atk_idx,:);
                mx    = max(qv);
                cands = find(qv==mx);
                atk_a = cands(randi(length(cands)));
            end

            [next_def_raw, next_atk_raw, ~, atk_r, done, ~] = ...
                env_adapt.step(def_a, atk_a);
            next_adapt_atk_idx = discretize_state_fn(next_atk_raw, atk_bins);

            if done
                adapted_Q(adapt_atk_idx,atk_a) = adapted_Q(adapt_atk_idx,atk_a) + ...
                    adapt_lr*(atk_r - adapted_Q(adapt_atk_idx,atk_a));
            else
                adapted_Q(adapt_atk_idx,atk_a) = adapted_Q(adapt_atk_idx,atk_a) + ...
                    adapt_lr*(atk_r + atk_gamma*max(adapted_Q(next_adapt_atk_idx,:)) ...
                    - adapted_Q(adapt_atk_idx,atk_a));
            end

            def_raw = next_def_raw;
            atk_raw = next_atk_raw;
            adapt_atk_idx = next_adapt_atk_idx;
            if done, break; end
        end

        switch method
            case {'DQN_Individual','Deception_Only'}
                config.strategy_bundles   = orig_bundles;
                config.n_defender_actions = orig_n;
                env_adapt.config = config;
        end

        adapt_eps = max(adapt_eps_min, adapt_eps * adapt_eps_decay);
    end

    % Evaluate against adapted attacker
    ep_metrics = cell(1, n_adapt_episodes);
    env_adapt2 = iiot_environment(config);
    if strcmp(method,'CoADAM_DQN')
        env_adapt2.intel_boost_enabled = true;
    else
        env_adapt2.intel_boost_enabled = false;
    end

    for ep = 1:n_adapt_episodes
        [def_raw, atk_raw] = env_adapt2.reset(30000 + mi*1000 + ep);

        switch method
            case 'DQN_Individual'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = indiv_bundles;
                config.n_defender_actions = config.n_mechanisms;
                env_adapt2.config = config;
            case 'Deception_Only'
                orig_bundles = config.strategy_bundles;
                orig_n = config.n_defender_actions;
                config.strategy_bundles   = dec_bundles;
                config.n_defender_actions = n_dec_actions;
                env_adapt2.config = config;
        end

        adapt_atk_idx = discretize_state_fn(atk_raw, atk_bins);

        for t = 1:max_steps
            def_a = get_def_action(method, def_raw, n_def_actions, ...
                iW1,ib1,iW2,ib2,iW3,ib3, dec_Q,dec_bins, ...
                tab_Q,def_bins,has_tabular, stack_action, ...
                W1,b1,W2,b2,W3,b3);

            adapt_atk_idx = discretize_state_fn(atk_raw, atk_bins);
            qv    = adapted_Q(adapt_atk_idx,:);
            mx    = max(qv);
            cands = find(qv==mx);
            atk_a = cands(randi(length(cands)));

            [def_raw, atk_raw, ~, ~, done, ~] = env_adapt2.step(def_a, atk_a);
            if done, break; end
        end

        switch method
            case {'DQN_Individual','Deception_Only'}
                config.strategy_bundles   = orig_bundles;
                config.n_defender_actions = orig_n;
                env_adapt2.config = config;
        end

        ep_metrics{ep} = env_adapt2.get_episode_metrics();
    end

    adapt_results{mi} = aggregate_metrics(ep_metrics, n_adapt_episodes, method);
    fprintf('  After adaptation: AMR=%.4f, Inf=%.4f, Reward=%.2f\n\n', ...
        adapt_results{mi}.AMR.mean, adapt_results{mi}.InfectionRate.mean, ...
        adapt_results{mi}.CumulativeReward.mean);
end

%%
% REPORT
%%

report_path = fullfile(phase5_dir, 'baseline_report_final.txt');
fid = fopen(report_path, 'w');

dual_print(fid, 'CoADAM Phase 5: Baseline Comparison Report (Final)\n');
dual_print(fid, 'Timestamp: %s\n', char(datetime('now')));
dual_print(fid, 'Table B uses method-specific adaptive attacker (1000 fine-tune eps)\n');
dual_print(fid, '=============================================\n\n');

show_metrics = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
    'MTTD','AttackerDwellTime','DefenseCostEfficiency'};
show_labels  = {'AMR','DSR','FAR','Reward','Infection','MTTD','DwellTime','CostEff'};

%--- TABLE A ---
dual_print(fid, '========================================\n');
dual_print(fid, 'TABLE A: Random Attacker\n');
dual_print(fid, '========================================\n\n');
print_comparison_table(fid, results_tableA, method_names, n_methods, ...
    show_metrics, show_labels);
print_improvement_table(fid, results_tableA, method_names, n_methods);
print_risk_table(fid, results_tableA, method_names, n_methods);
print_significance_table(fid, results_tableA, method_names, n_methods);

%--- TABLE B ---
dual_print(fid, '========================================\n');
dual_print(fid, 'TABLE B: Method-Specific Adaptive Attacker\n');
dual_print(fid, '(Each method faces attacker fine-tuned 1000 eps against it)\n');
dual_print(fid, '========================================\n\n');
print_comparison_table(fid, results_tableB, method_names, n_methods, ...
    show_metrics, show_labels);
print_improvement_table(fid, results_tableB, method_names, n_methods);
print_risk_table(fid, results_tableB, method_names, n_methods);
print_significance_table(fid, results_tableB, method_names, n_methods);

%--- ROBUSTNESS: A -> B ---
dual_print(fid, '========================================\n');
dual_print(fid, 'ROBUSTNESS ANALYSIS: Random -> Method-Specific Adaptive\n');
dual_print(fid, '========================================\n\n');

dual_print(fid, '%-18s %10s %10s %10s %10s %10s\n', ...
    'Method','AMR drop','Inf rise','DSR drop','Rew drop','Robust?');
dual_print(fid, '%s\n', repmat('-',1,68));

robustness_scores = zeros(1, n_methods);
for mi = 1:n_methods
    rA = results_tableA{mi};
    rB = results_tableB{mi};
    amr_drop = rA.AMR.mean - rB.AMR.mean;
    inf_rise = rB.InfectionRate.mean - rA.InfectionRate.mean;
    dsr_drop = rA.DSR.mean - rB.DSR.mean;
    rew_drop = rA.CumulativeReward.mean - rB.CumulativeReward.mean;
    robustness_scores(mi) = amr_drop + inf_rise + abs(dsr_drop)*0.5;
    if robustness_scores(mi) < 0.05,     rl = 'HIGH';
    elseif robustness_scores(mi) < 0.15, rl = 'MEDIUM';
    else,                                 rl = 'LOW';   
    end
    dual_print(fid, '%-18s %+9.4f %+9.4f %+9.4f %+9.2f %10s\n', ...
        method_names{mi}, amr_drop, inf_rise, dsr_drop, rew_drop, rl);
end
dual_print(fid, '\n');
[~, rob_rank] = sort(robustness_scores, 'ascend');
dual_print(fid, 'Robustness ranking (best to worst):\n');
for i = 1:n_methods
    dual_print(fid, '  %d. %s (score: %.4f)\n', ...
        i, method_names{rob_rank(i)}, robustness_scores(rob_rank(i)));
end
dual_print(fid, '\n');

%--- ADVERSARIAL ADAPTATION TABLE ---
dual_print(fid, '========================================\n');
dual_print(fid, 'ADVERSARIAL ADAPTATION (500 eps)\n');
dual_print(fid, '========================================\n\n');

dual_print(fid, '%-18s %8s %8s %8s %8s %8s %8s\n', ...
    'Method','AMR(R)','AMR(B)','AMR(Aa)','Inf(R)','Inf(B)','Inf(Aa)');
dual_print(fid, '%s\n', repmat('-',1,74));
for mi = 1:n_methods
    rA  = results_tableA{mi};
    rB  = results_tableB{mi};
    rAa = adapt_results{mi};
    dual_print(fid, '%-18s %8.4f %8.4f %8.4f %8.4f %8.4f %8.4f\n', ...
        method_names{mi}, ...
        rA.AMR.mean,  rB.AMR.mean,  rAa.AMR.mean, ...
        rA.InfectionRate.mean, rB.InfectionRate.mean, rAa.InfectionRate.mean);
end
dual_print(fid, '\n');

dual_print(fid, '--- Degradation: Random -> Adapted (500 eps) ---\n\n');
dual_print(fid, '%-18s %10s %10s %10s %10s\n', ...
    'Method','AMR drop','Inf rise','Rew drop','Robust?');
dual_print(fid, '%s\n', repmat('-',1,58));
adapt_robustness = zeros(1, n_methods);
for mi = 1:n_methods
    rA  = results_tableA{mi};
    rAa = adapt_results{mi};
    amr_drop = rA.AMR.mean - rAa.AMR.mean;
    inf_rise = rAa.InfectionRate.mean - rA.InfectionRate.mean;
    rew_drop = rA.CumulativeReward.mean - rAa.CumulativeReward.mean;
    adapt_robustness(mi) = amr_drop + inf_rise;
    if adapt_robustness(mi) < 0.05,     rl = 'HIGH';
    elseif adapt_robustness(mi) < 0.15, rl = 'MEDIUM';
    else,                                rl = 'LOW';   
    end
    dual_print(fid, '%-18s %+9.4f %+9.4f %+9.2f %10s\n', ...
        method_names{mi}, amr_drop, inf_rise, rew_drop, rl);
end
dual_print(fid, '\n');
[~, adapt_rank] = sort(adapt_robustness, 'ascend');
dual_print(fid, 'Adaptation robustness ranking:\n');
for i = 1:n_methods
    dual_print(fid, '  %d. %s (degradation: %.4f)\n', ...
        i, method_names{adapt_rank(i)}, adapt_robustness(adapt_rank(i)));
end
dual_print(fid, '\n');

dual_print(fid, '--- Statistical Significance (Adapted, CoADAM vs each) ---\n\n');
dual_print(fid, '%-18s %10s %10s %10s %10s\n', ...
    'Baseline','Reward p','Rew sig','AMR p','AMR sig');
dual_print(fid, '%s\n', repmat('-',1,58));
coadam_aa_rew = adapt_results{n_methods}.CumulativeReward.raw;
coadam_aa_amr = adapt_results{n_methods}.AMR.raw;
for mi = 1:n_methods-1
    rAa   = adapt_results{mi};
    p_rew = ranksum(coadam_aa_rew, rAa.CumulativeReward.raw);
    p_amr = ranksum(coadam_aa_amr, rAa.AMR.raw);
    dual_print(fid, '%-18s %10.6f %10s %10.6f %10s\n', ...
        method_names{mi}, p_rew, sig_str(p_rew), p_amr, sig_str(p_amr));
end
dual_print(fid, '\n');

%--- KEY FINDINGS ---
dual_print(fid, '========================================\n');
dual_print(fid, 'KEY FINDINGS\n');
dual_print(fid, '========================================\n\n');

% Table A ranks
[~, tA_amr_rank] = sort(cellfun(@(r) r.AMR.mean, results_tableA), 'descend');
coadam_tA_amr = find(tA_amr_rank == n_methods);
[~, tA_rew_rank] = sort(cellfun(@(r) r.CumulativeReward.mean, results_tableA), 'descend');
coadam_tA_rew = find(tA_rew_rank == n_methods);

% Table B ranks
[~, tB_amr_rank] = sort(cellfun(@(r) r.AMR.mean, results_tableB), 'descend');
coadam_tB_amr = find(tB_amr_rank == n_methods);
[~, tB_rew_rank] = sort(cellfun(@(r) r.CumulativeReward.mean, results_tableB), 'descend');
coadam_tB_rew = find(tB_rew_rank == n_methods);

% Adaptation ranks
adapt_amrs = zeros(1, n_methods);
for mi = 1:n_methods
    adapt_amrs(mi) = adapt_results{mi}.AMR.mean;
end
[~, aa_amr_rank]  = sort(adapt_amrs, 'descend');
coadam_aa_rank    = find(aa_amr_rank == n_methods);
coadam_adapt_rank = find(adapt_rank  == n_methods);

dual_print(fid, 'Table A (random attacker):\n');
dual_print(fid, '  CoADAM AMR rank:    %d/%d (AMR=%.4f)\n', ...
    coadam_tA_amr, n_methods, results_tableA{n_methods}.AMR.mean);
dual_print(fid, '  CoADAM Reward rank: %d/%d (Rew=%.2f)\n', ...
    coadam_tA_rew, n_methods, results_tableA{n_methods}.CumulativeReward.mean);
dual_print(fid, '  CoADAM CVaR rank:   #1 = %.2f\n', ...
    results_tableA{n_methods}.CVaR_005);
dual_print(fid, '\nTable B (method-specific adaptive attacker):\n');
dual_print(fid, '  CoADAM AMR rank:    %d/%d (AMR=%.4f)\n', ...
    coadam_tB_amr, n_methods, results_tableB{n_methods}.AMR.mean);
dual_print(fid, '  CoADAM Reward rank: %d/%d (Rew=%.2f)\n', ...
    coadam_tB_rew, n_methods, results_tableB{n_methods}.CumulativeReward.mean);
dual_print(fid, '\nAdversarial Adaptation Test:\n');
dual_print(fid, '  CoADAM AMR rank:        %d/%d (AMR=%.4f)\n', ...
    coadam_aa_rank, n_methods, adapt_results{n_methods}.AMR.mean);
dual_print(fid, '  CoADAM Robustness rank: %d/%d (score=%.4f)\n', ...
    coadam_adapt_rank, n_methods, adapt_robustness(n_methods));
dual_print(fid, '\nDeception effectiveness (adapted attacker):\n');
dual_print(fid, '  CoADAM DSR: %.4f\n', adapt_results{n_methods}.DSR.mean);
dual_print(fid, '  Static DSR: %.4f\n',  adapt_results{1}.DSR.mean);
dual_print(fid, '  Stackelberg DSR: %.4f\n', adapt_results{6}.DSR.mean);

dual_print(fid, '\n=============================================\n');
dual_print(fid, 'Phase 5 (Final) complete.\n');

% Save
baseline_results = struct();
baseline_results.results_tableA    = results_tableA;
baseline_results.results_tableB    = results_tableB;
baseline_results.adapt_results     = adapt_results;
baseline_results.method_names      = method_names;
baseline_results.robustness_scores = robustness_scores;
baseline_results.adapt_robustness  = adapt_robustness;
baseline_results.stack_payoff      = stack_payoff;
baseline_results.stack_action      = stack_action;
baseline_results.n_finetune        = n_finetune;
baseline_results.n_adapt_episodes  = n_adapt_episodes;
baseline_results.timestamp         = char(datetime('now'));

save(fullfile(results_dir,'baseline_results_final.mat'), '-struct', 'baseline_results');
dual_print(fid, 'Saved: %s\n', fullfile(results_dir,'baseline_results_final.mat'));
dual_print(fid, 'Report: %s\n', report_path);
fclose(fid);
fprintf('\nDone. Report: %s\n', report_path);

%%
% LOCAL FUNCTIONS
%%

function def_a = get_def_action(method, def_raw, n_def_actions, ...
        iW1,ib1,iW2,ib2,iW3,ib3, dec_Q,dec_bins, ...
        tab_Q,def_bins,has_tabular, stack_action, ...
        W1,b1,W2,b2,W3,b3)
    switch method
        case 'Static'
            def_a = 1;
        case 'Random'
            def_a = randi(n_def_actions);
        case 'Heuristic'
            if def_raw(1) > 0.5,     def_a = 3;
            elseif def_raw(5) > 0.6, def_a = 4;
            elseif def_raw(2) < 0.2, def_a = 2;
            else,                     def_a = 1; 
            end
        case 'DQN_Individual'
            q = forward_pass_fn(def_raw, iW1, ib1, iW2, ib2, iW3, ib3);
            [~, def_a] = max(q);
        case 'Deception_Only'
            def_idx = discretize_state_fn(def_raw, dec_bins);
            [~, def_a] = max(dec_Q(def_idx,:));
        case 'Stackelberg'
            def_a = stack_action;
        case 'Tabular_QL'
            if has_tabular
                def_idx = discretize_state_fn(def_raw, def_bins);
                [~, def_a] = max(tab_Q(def_idx,:));
            else
                def_a = 1;
            end
        case 'CoADAM_DQN'
            % Fix 3: s(6)=skepticism, s(5)=momentum
            % Fix 2: mask only at infection>0.60 AND skepticism>0.80
            s      = def_raw(:);
            h1_    = max(0, W1*s + b1);
            h2_    = max(0, W2*h1_ + b2);
            q_vals = W3*h2_ + b3;
            if (s(1) > 0.60) && (s(6) > 0.80)
                q_vals(2) = -inf;
            end
            [~, def_a] = max(q_vals);
        otherwise
            def_a = 1;
    end
end

function res = aggregate_metrics(ep_metrics, n_eval, name)
    res      = struct();
    res.name = name;
    metric_names = {'AMR','DSR','FAR','CumulativeReward','InfectionRate', ...
        'MTTD','AttackerDwellTime','DefenseCostEfficiency', ...
        'AttackerCumulativeReward','EpisodeLength'};
    for mi = 1:length(metric_names)
        mn  = metric_names{mi};
        arr = cellfun(@(m) m.(mn), ep_metrics);
        res.(mn) = struct('mean',mean(arr),'std',std(arr), ...
            'min',min(arr),'max',max(arr),'median',median(arr),'raw',arr);
    end
    sorted_rew   = sort(res.CumulativeReward.raw,'ascend');
    n_tail       = max(1, floor(0.05*n_eval));
    res.CVaR_005 = mean(sorted_rew(1:n_tail));
    res.DR       = iqr(res.CumulativeReward.raw);
end

function print_comparison_table(fid, results, method_names, n_methods, ...
        show_metrics, show_labels)
    dual_print(fid, '--- Main Comparison Table ---\n\n');
    dual_print(fid, '%-18s', 'Method');
    for si = 1:length(show_labels)
        dual_print(fid, ' %18s', show_labels{si});
    end
    dual_print(fid, '\n%s\n', repmat('-', 1, 18+18*length(show_labels)));
    for mi = 1:n_methods
        r = results{mi};
        dual_print(fid, '%-18s', method_names{mi});
        for si = 1:length(show_metrics)
            m = r.(show_metrics{si});
            dual_print(fid, ' %8.3f+/-%-7.3f', m.mean, m.std);
        end
        dual_print(fid, '\n');
    end
    dual_print(fid, '\n');
end

function print_improvement_table(fid, results, method_names, n_methods)
    coadam = results{n_methods};
    dual_print(fid, '--- CoADAM Improvement Over Baselines ---\n\n');
    dual_print(fid, '%-18s %8s %8s %8s %8s\n','Baseline','AMR%','Inf%','DSR%','Reward%');
    dual_print(fid, '%s\n', repmat('-',1,52));
    for mi = 1:n_methods-1
        r     = results{mi};
        d_amr = (coadam.AMR.mean - r.AMR.mean) / max(0.001,r.AMR.mean)*100;
        d_inf = (coadam.InfectionRate.mean - r.InfectionRate.mean) / ...
            max(0.001,r.InfectionRate.mean)*100;
        d_dsr = (coadam.DSR.mean - r.DSR.mean) / max(0.001,r.DSR.mean)*100;
        if abs(r.CumulativeReward.mean) > 0.001
            d_rew = (coadam.CumulativeReward.mean - r.CumulativeReward.mean) / ...
                abs(r.CumulativeReward.mean)*100;
        else
            d_rew = 0;
        end
        dual_print(fid, '%-18s %+7.1f%% %+7.1f%% %+7.1f%% %+7.1f%%\n', ...
            method_names{mi}, d_amr, d_inf, d_dsr, d_rew);
    end
    dual_print(fid, '\n');
end

function print_risk_table(fid, results, method_names, n_methods)
    dual_print(fid, '--- Risk Analysis (CVaR alpha=0.05) ---\n\n');
    dual_print(fid, '%-18s %12s %12s\n','Method','CVaR(0.05)','DR (IQR)');
    dual_print(fid, '%s\n', repmat('-',1,42));
    for mi = 1:n_methods
        r = results{mi};
        dual_print(fid, '%-18s %12.2f %12.2f\n', method_names{mi}, r.CVaR_005, r.DR);
    end
    dual_print(fid, '\n');
end

function print_significance_table(fid, results, method_names, n_methods)
    coadam_rew = results{n_methods}.CumulativeReward.raw;
    coadam_amr = results{n_methods}.AMR.raw;
    dual_print(fid, '--- Statistical Significance (Wilcoxon, CoADAM vs each) ---\n\n');
    dual_print(fid, '%-18s %10s %10s %10s %10s\n', ...
        'Baseline','Reward p','Rew sig','AMR p','AMR sig');
    dual_print(fid, '%s\n', repmat('-',1,58));
    for mi = 1:n_methods-1
        r     = results{mi};
        p_rew = ranksum(coadam_rew, r.CumulativeReward.raw);
        p_amr = ranksum(coadam_amr, r.AMR.raw);
        dual_print(fid, '%-18s %10.6f %10s %10.6f %10s\n', ...
            method_names{mi}, p_rew, sig_str(p_rew), p_amr, sig_str(p_amr));
    end
    dual_print(fid, '\n');
end

function idx = discretize_state_fn(state, n_bins)
    n   = length(state);
    idx = 0;
    multiplier = 1;
    for i = 1:n
        val = max(0, min(1-1e-10, state(i)));
        bin = floor(val * n_bins(i));
        idx = idx + bin * multiplier;
        multiplier = multiplier * n_bins(i);
    end
    idx = idx + 1;
end

function q = forward_pass_fn(state, W1, b1, W2, b2, W3, b3)
    x  = state(:);
    h1 = max(0, W1*x + b1);
    h2 = max(0, W2*h1 + b2);
    q  = (W3*h2 + b3)';
end

function [dW1,db1,dW2,db2,dW3,db3] = backprop_fn(state, action, td_error, ...
        W1, b1, W2, b2, W3, b3)
    x  = state(:);
    z1 = W1*x + b1;  h1 = max(0,z1);
    z2 = W2*h1 + b2; h2 = max(0,z2);
    dq = zeros(size(W3,1),1); dq(action) = td_error;
    dW3=dq*h2'; db3=dq; dh2=W3'*dq;
    dz2=dh2.*(z2>0); dW2=dz2*h1'; db2=dz2; dh1=W2'*dz2;
    dz1=dh1.*(z1>0); dW1=dz1*x';  db1=dz1;
end

function s = sig_str(p)
    if p<0.001, s='(***)'; elseif p<0.01, s='(**)';
    elseif p<0.05, s='(*)'; else, s='(n.s.)'; end
end

function dual_print(fid, varargin)
    fprintf(varargin{:});
    if fid > 0, fprintf(fid, varargin{:}); end
end
