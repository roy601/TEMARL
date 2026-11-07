classdef coevolutionary_trainer < handle
%%
% CoADAM Phase 3-4: Co-Evolutionary Trainer
%
% Manages both defender (CoADAM) and attacker Q-learning agents.
% Both agents learn simultaneously through interaction in the
% IIoT defense environment, creating an arms-race dynamic.
%
% The defender selects strategy bundles (4 actions).
% The attacker selects tactic/intensity/zone combinations (45 actions).
%
% Usage:
%   trainer = coevolutionary_trainer(config, env);
%   results = trainer.train();
%
% Date: 28-Feb-2026
%%

    properties
        config
        env

        % Defender Q-table and parameters
        def_Q
        def_state_bins
        def_n_actions
        def_lr
        def_gamma
        def_epsilon
        def_epsilon_decay
        def_epsilon_min

        % Attacker Q-table and parameters
        atk_Q
        atk_state_bins
        atk_n_actions
        atk_lr
        atk_gamma
        atk_epsilon
        atk_epsilon_decay
        atk_epsilon_min

        % Training tracking
        n_episodes
        max_steps
        episode_metrics_log    % cell array of per-episode metric structs
        training_rewards_def   % vector of cumulative defender rewards
        training_rewards_atk   % vector of cumulative attacker rewards
        training_amr           % vector of AMR per episode
        training_infection     % vector of final infection per episode
        training_dsr           % vector of DSR per episode
        training_mttd          % vector of MTTD per episode
        training_dwell         % vector of dwell time per episode
        training_dce           % vector of defense cost efficiency per episode
        training_far           % vector of FAR per episode
        training_epsilon_def   % vector of defender epsilon per episode
        training_epsilon_atk   % vector of attacker epsilon per episode

        % Q-table visit counts (for analysis)
        def_visit_count
        atk_visit_count
    end

    methods

        %------------------------------------------------------------------
        % CONSTRUCTOR
        %------------------------------------------------------------------
        function obj = coevolutionary_trainer(config, env)
            obj.config = config;
            obj.env = env;

            % Defender setup
            obj.def_state_bins = config.defender_state.n_bins;
            obj.def_n_actions = config.n_defender_actions;
            def_state_size = prod(obj.def_state_bins);
            obj.def_Q = zeros(def_state_size, obj.def_n_actions);
            obj.def_visit_count = zeros(def_state_size, obj.def_n_actions);

            obj.def_lr = config.training.defender.learning_rate;
            obj.def_gamma = config.training.defender.gamma;
            obj.def_epsilon = config.training.defender.epsilon_start;
            obj.def_epsilon_decay = config.training.defender.epsilon_decay;
            obj.def_epsilon_min = config.training.defender.epsilon_min;

            % Attacker setup
            obj.atk_state_bins = config.attacker_state.n_bins;
            obj.atk_n_actions = config.n_attacker_actions;
            atk_state_size = prod(obj.atk_state_bins);
            obj.atk_Q = zeros(atk_state_size, obj.atk_n_actions);
            obj.atk_visit_count = zeros(atk_state_size, obj.atk_n_actions);

            obj.atk_lr = config.training.attacker.learning_rate;
            obj.atk_gamma = config.training.attacker.gamma;
            obj.atk_epsilon = config.training.attacker.epsilon_start;
            obj.atk_epsilon_decay = config.training.attacker.epsilon_decay;
            obj.atk_epsilon_min = config.training.attacker.epsilon_min;

            % Training parameters
            obj.n_episodes = config.training.n_episodes;
            obj.max_steps = config.training.max_steps;
        end

        %------------------------------------------------------------------
        % DISCRETIZE STATE: Convert continuous [0,1] state to linear index
        %------------------------------------------------------------------
        function idx = discretize_state(~, state, n_bins)
            n = length(state);
            sub_indices = zeros(1, n);
            for i = 1:n
                val = max(0, min(1 - 1e-10, state(i)));
                bin = floor(val * n_bins(i));
                sub_indices(i) = bin;
            end

            idx = sub_indices(1);
            multiplier = 1;
            for i = 2:n
                multiplier = multiplier * n_bins(i-1);
                idx = idx + sub_indices(i) * multiplier;
            end
            idx = idx + 1;  % MATLAB 1-indexed
        end

        %------------------------------------------------------------------
        % SELECT ACTION: Epsilon-greedy policy
        %------------------------------------------------------------------
        function action = select_action(~, Q_table, state_idx, n_actions, epsilon)
            if rand() < epsilon
                action = randi(n_actions);
            else
                q_values = Q_table(state_idx, :);
                max_q = max(q_values);
                % Break ties randomly
                best_actions = find(q_values == max_q);
                action = best_actions(randi(length(best_actions)));
            end
        end

        %------------------------------------------------------------------
        % UPDATE Q-VALUE: Standard Q-learning update
        %------------------------------------------------------------------
        function Q_table = update_q(~, Q_table, state_idx, action, reward, ...
                next_state_idx, gamma, lr)
            current_q = Q_table(state_idx, action);
            max_next_q = max(Q_table(next_state_idx, :));
            td_target = reward + gamma * max_next_q;
            Q_table(state_idx, action) = current_q + lr * (td_target - current_q);
        end

        %------------------------------------------------------------------
        % TRAIN: Main co-evolutionary training loop
        %------------------------------------------------------------------
        function results = train(obj, seed)
            if nargin < 2
                seed = 42;
            end
            rng(seed);

            % Pre-allocate tracking arrays
            obj.training_rewards_def = zeros(1, obj.n_episodes);
            obj.training_rewards_atk = zeros(1, obj.n_episodes);
            obj.training_amr = zeros(1, obj.n_episodes);
            obj.training_infection = zeros(1, obj.n_episodes);
            obj.training_dsr = zeros(1, obj.n_episodes);
            obj.training_mttd = zeros(1, obj.n_episodes);
            obj.training_dwell = zeros(1, obj.n_episodes);
            obj.training_dce = zeros(1, obj.n_episodes);
            obj.training_far = zeros(1, obj.n_episodes);
            obj.training_epsilon_def = zeros(1, obj.n_episodes);
            obj.training_epsilon_atk = zeros(1, obj.n_episodes);
            obj.episode_metrics_log = cell(1, obj.n_episodes);

            % Training timer
            train_start = tic;
            last_print_time = tic;

            for ep = 1:obj.n_episodes

                % Reset environment
                [def_state_raw, atk_state_raw] = obj.env.reset(seed + ep);

                % Discretize initial states
                def_state_idx = obj.discretize_state(def_state_raw, obj.def_state_bins);
                atk_state_idx = obj.discretize_state(atk_state_raw, obj.atk_state_bins);

                ep_def_reward = 0;
                ep_atk_reward = 0;
                done = false;

                for t = 1:obj.max_steps
                    if done
                        break;
                    end

                    % Select actions
                    def_action = obj.select_action(obj.def_Q, def_state_idx, ...
                        obj.def_n_actions, obj.def_epsilon);
                    atk_action = obj.select_action(obj.atk_Q, atk_state_idx, ...
                        obj.atk_n_actions, obj.atk_epsilon);

                    % Environment step
                    [next_def_raw, next_atk_raw, def_reward, atk_reward, done, ~] = ...
                        obj.env.step(def_action, atk_action);

                    % Discretize next states
                    next_def_idx = obj.discretize_state(next_def_raw, obj.def_state_bins);
                    next_atk_idx = obj.discretize_state(next_atk_raw, obj.atk_state_bins);

                    % Update Q-tables
                    if done
                        % Terminal state: no future reward
                        obj.def_Q(def_state_idx, def_action) = ...
                            obj.def_Q(def_state_idx, def_action) + ...
                            obj.def_lr * (def_reward - obj.def_Q(def_state_idx, def_action));
                        obj.atk_Q(atk_state_idx, atk_action) = ...
                            obj.atk_Q(atk_state_idx, atk_action) + ...
                            obj.atk_lr * (atk_reward - obj.atk_Q(atk_state_idx, atk_action));
                    else
                        obj.def_Q = obj.update_q(obj.def_Q, def_state_idx, def_action, ...
                            def_reward, next_def_idx, obj.def_gamma, obj.def_lr);
                        obj.atk_Q = obj.update_q(obj.atk_Q, atk_state_idx, atk_action, ...
                            atk_reward, next_atk_idx, obj.atk_gamma, obj.atk_lr);
                    end

                    % Update visit counts
                    obj.def_visit_count(def_state_idx, def_action) = ...
                        obj.def_visit_count(def_state_idx, def_action) + 1;
                    obj.atk_visit_count(atk_state_idx, atk_action) = ...
                        obj.atk_visit_count(atk_state_idx, atk_action) + 1;

                    % Accumulate rewards
                    ep_def_reward = ep_def_reward + def_reward;
                    ep_atk_reward = ep_atk_reward + atk_reward;

                    % Transition
                    def_state_idx = next_def_idx;
                    atk_state_idx = next_atk_idx;
                end

                % Get episode metrics
                ep_metrics = obj.env.get_episode_metrics();
                obj.episode_metrics_log{ep} = ep_metrics;

                % Store tracking data
                obj.training_rewards_def(ep) = ep_def_reward;
                obj.training_rewards_atk(ep) = ep_atk_reward;
                obj.training_amr(ep) = ep_metrics.AMR;
                obj.training_infection(ep) = ep_metrics.InfectionRate;
                obj.training_dsr(ep) = ep_metrics.DSR;
                obj.training_mttd(ep) = ep_metrics.MTTD;
                obj.training_dwell(ep) = ep_metrics.AttackerDwellTime;
                obj.training_dce(ep) = ep_metrics.DefenseCostEfficiency;
                obj.training_far(ep) = ep_metrics.FAR;
                obj.training_epsilon_def(ep) = obj.def_epsilon;
                obj.training_epsilon_atk(ep) = obj.atk_epsilon;

                % Decay epsilon
                obj.def_epsilon = max(obj.def_epsilon_min, ...
                    obj.def_epsilon * obj.def_epsilon_decay);
                obj.atk_epsilon = max(obj.atk_epsilon_min, ...
                    obj.atk_epsilon * obj.atk_epsilon_decay);

                % Progress printing every 30 seconds or at key milestones
                elapsed_since_print = toc(last_print_time);
                is_milestone = (mod(ep, 500) == 0) || (ep == 1) || (ep == obj.n_episodes);

                if elapsed_since_print > 30 || is_milestone
                    elapsed_total = toc(train_start);
                    eps_per_sec = ep / elapsed_total;
                    eta_sec = (obj.n_episodes - ep) / eps_per_sec;

                    fprintf('Ep %4d/%d | DefR=%.1f AMR=%.3f Inf=%.3f DSR=%.3f | ', ...
                        ep, obj.n_episodes, ep_def_reward, ep_metrics.AMR, ...
                        ep_metrics.InfectionRate, ep_metrics.DSR);
                    fprintf('AtkR=%.1f | eps_d=%.3f eps_a=%.3f | ', ...
                        ep_atk_reward, obj.def_epsilon, obj.atk_epsilon);
                    fprintf('%.1f ep/s ETA %.0fs\n', eps_per_sec, eta_sec);

                    last_print_time = tic;
                end
            end

            total_time = toc(train_start);

            % Compute training statistics
            results = struct();
            results.total_training_time = total_time;
            results.episodes = obj.n_episodes;
            results.final_def_epsilon = obj.def_epsilon;
            results.final_atk_epsilon = obj.atk_epsilon;

            % Per-episode data
            results.training_rewards_def = obj.training_rewards_def;
            results.training_rewards_atk = obj.training_rewards_atk;
            results.training_amr = obj.training_amr;
            results.training_infection = obj.training_infection;
            results.training_dsr = obj.training_dsr;
            results.training_mttd = obj.training_mttd;
            results.training_dwell = obj.training_dwell;
            results.training_dce = obj.training_dce;
            results.training_far = obj.training_far;
            results.training_epsilon_def = obj.training_epsilon_def;
            results.training_epsilon_atk = obj.training_epsilon_atk;
            results.episode_metrics_log = obj.episode_metrics_log;

            % Q-table statistics
            results.def_Q_nonzero = nnz(obj.def_Q);
            results.def_Q_total = numel(obj.def_Q);
            results.def_Q_utilization = results.def_Q_nonzero / results.def_Q_total;
            results.def_states_visited = sum(any(obj.def_visit_count > 0, 2));
            results.atk_Q_nonzero = nnz(obj.atk_Q);
            results.atk_Q_total = numel(obj.atk_Q);
            results.atk_Q_utilization = results.atk_Q_nonzero / results.atk_Q_total;
            results.atk_states_visited = sum(any(obj.atk_visit_count > 0, 2));

            % Convergence analysis (last 500 vs first 500 episodes)
            if obj.n_episodes >= 1000
                early = 1:500;
                late = (obj.n_episodes-499):obj.n_episodes;

                results.convergence.early_def_reward = mean(obj.training_rewards_def(early));
                results.convergence.late_def_reward = mean(obj.training_rewards_def(late));
                results.convergence.early_atk_reward = mean(obj.training_rewards_atk(early));
                results.convergence.late_atk_reward = mean(obj.training_rewards_atk(late));
                results.convergence.early_amr = mean(obj.training_amr(early));
                results.convergence.late_amr = mean(obj.training_amr(late));
                results.convergence.early_infection = mean(obj.training_infection(early));
                results.convergence.late_infection = mean(obj.training_infection(late));
                results.convergence.early_dsr = mean(obj.training_dsr(early));
                results.convergence.late_dsr = mean(obj.training_dsr(late));
                results.convergence.early_mttd = mean(obj.training_mttd(early));
                results.convergence.late_mttd = mean(obj.training_mttd(late));
                results.convergence.def_reward_improvement = ...
                    (results.convergence.late_def_reward - results.convergence.early_def_reward) / ...
                    abs(results.convergence.early_def_reward) * 100;
                results.convergence.amr_improvement = ...
                    (results.convergence.late_amr - results.convergence.early_amr) / ...
                    max(0.001, results.convergence.early_amr) * 100;
            end

            % Q-tables for saving
            results.def_Q = obj.def_Q;
            results.atk_Q = obj.atk_Q;
            results.def_visit_count = obj.def_visit_count;
            results.atk_visit_count = obj.atk_visit_count;

            fprintf('\nTraining complete. Time: %.1f seconds (%.1f minutes)\n', ...
                total_time, total_time/60);
        end

        %------------------------------------------------------------------
        % EVALUATE: Run evaluation episodes with fixed (greedy) policies
        %------------------------------------------------------------------
        function eval_results = evaluate(obj, n_eval_episodes, seed_offset)
            if nargin < 2, n_eval_episodes = 100; end
            if nargin < 3, seed_offset = 10000; end

            eval_metrics = cell(1, n_eval_episodes);

            for ep = 1:n_eval_episodes
                [def_state_raw, atk_state_raw] = obj.env.reset(seed_offset + ep);
                def_state_idx = obj.discretize_state(def_state_raw, obj.def_state_bins);
                atk_state_idx = obj.discretize_state(atk_state_raw, obj.atk_state_bins);
                done = false;

                for t = 1:obj.max_steps
                    if done, break; end

                    % Greedy actions (no exploration)
                    def_action = obj.select_action(obj.def_Q, def_state_idx, ...
                        obj.def_n_actions, 0);
                    atk_action = obj.select_action(obj.atk_Q, atk_state_idx, ...
                        obj.atk_n_actions, 0);

                    [next_def_raw, next_atk_raw, ~, ~, done, ~] = ...
                        obj.env.step(def_action, atk_action);

                    def_state_idx = obj.discretize_state(next_def_raw, obj.def_state_bins);
                    atk_state_idx = obj.discretize_state(next_atk_raw, obj.atk_state_bins);
                end

                eval_metrics{ep} = obj.env.get_episode_metrics();
            end

            % Aggregate evaluation results
            eval_results = struct();
            metric_fields = {'AMR', 'DSR', 'FAR', 'CumulativeReward', ...
                'InfectionRate', 'MTTD', 'AttackerDwellTime', ...
                'DefenseCostEfficiency', 'AttackerCumulativeReward', 'EpisodeLength'};

            for m = 1:length(metric_fields)
                fname = metric_fields{m};
                vals = cellfun(@(x) x.(fname), eval_metrics);
                eval_results.(fname).mean = mean(vals);
                eval_results.(fname).std = std(vals);
                eval_results.(fname).min = min(vals);
                eval_results.(fname).max = max(vals);
                eval_results.(fname).median = median(vals);
                eval_results.(fname).values = vals;
            end

            % CVaR at alpha=0.05 on defender cumulative reward
            reward_vals = cellfun(@(x) x.CumulativeReward, eval_metrics);
            sorted_rewards = sort(reward_vals);
            alpha = obj.config.metrics.cvar_alpha;
            n_tail = max(1, floor(alpha * n_eval_episodes));
            eval_results.CVaR_005 = mean(sorted_rewards(1:n_tail));

            % Training reliability (DR): IQR of rewards
            eval_results.TrainingReliability_DR = iqr(reward_vals);

            eval_results.raw_metrics = eval_metrics;
            eval_results.n_episodes = n_eval_episodes;
        end

        %------------------------------------------------------------------
        % GET POLICY SUMMARY: Analyze learned defender policy
        %------------------------------------------------------------------
        function summary = get_policy_summary(obj)
            summary = struct();

            % For each visited state, find the greedy action
            action_counts = zeros(1, obj.def_n_actions);
            total_visited = 0;

            n_states = size(obj.def_Q, 1);
            for s = 1:n_states
                if any(obj.def_visit_count(s, :) > 0)
                    [~, best_action] = max(obj.def_Q(s, :));
                    action_counts(best_action) = action_counts(best_action) + 1;
                    total_visited = total_visited + 1;
                end
            end

            if total_visited > 0
                summary.action_distribution = action_counts / total_visited;
            else
                summary.action_distribution = zeros(1, obj.def_n_actions);
            end
            summary.action_counts = action_counts;
            summary.total_visited_states = total_visited;
            summary.strategy_names = obj.config.strategy_names;

            % Attacker policy summary
            atk_tactic_counts = zeros(1, obj.config.n_attacker_tactics);
            atk_intensity_counts = zeros(1, obj.config.n_intensity);
            atk_zone_counts = zeros(1, obj.config.n_zones);
            atk_total_visited = 0;

            n_atk_states = size(obj.atk_Q, 1);
            for s = 1:n_atk_states
                if any(obj.atk_visit_count(s, :) > 0)
                    [~, best_action] = max(obj.atk_Q(s, :));
                    tiz = obj.config.attacker_action_table(best_action, :);
                    atk_tactic_counts(tiz(1)) = atk_tactic_counts(tiz(1)) + 1;
                    atk_intensity_counts(tiz(2)) = atk_intensity_counts(tiz(2)) + 1;
                    atk_zone_counts(tiz(3)) = atk_zone_counts(tiz(3)) + 1;
                    atk_total_visited = atk_total_visited + 1;
                end
            end

            if atk_total_visited > 0
                summary.atk_tactic_distribution = atk_tactic_counts / atk_total_visited;
                summary.atk_intensity_distribution = atk_intensity_counts / atk_total_visited;
                summary.atk_zone_distribution = atk_zone_counts / atk_total_visited;
            else
                summary.atk_tactic_distribution = zeros(1, obj.config.n_attacker_tactics);
                summary.atk_intensity_distribution = zeros(1, obj.config.n_intensity);
                summary.atk_zone_distribution = zeros(1, obj.config.n_zones);
            end
            summary.atk_total_visited_states = atk_total_visited;
        end

    end
end
