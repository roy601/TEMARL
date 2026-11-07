classdef iiot_environment < handle
%%
% CoADAM Phase 2B: IIoT Defense Simulation Environment (REVISED)
%
% Changes from original:
%   - Infection penalty uses delta (change) not absolute level
%   - Critical zone bonus penalty added
%   - MTTD tracking fixed (per-attack detection delay)
%   - Skepticism has ceiling relative to deception density
%   - Deception engagement scales with dwell reward properly
%   - Budget constraint creates real tradeoffs
%
% Fix 1: Removed both diversity reward components (were teaching uniform
%         action selection — proven by ~25% each action in output)
% Fix 2: Action masking threshold raised to only fire at catastrophic
%         infection (>0.60) AND near-max skepticism (>0.80) simultaneously
%
% Date: 01-Mar-2026 (Fixed)
%%

    properties
        config
        current_step
        max_steps

        % Network state
        infection_rate
        zone_infection
        budget_remaining
        prev_infection_rate

        % Dynamic state
        skepticism
        momentum
        recent_fp_rate
        deception_density

        % History tracking
        attack_history
        success_history
        defense_history
        deception_encounters
        dwell_accumulator
        recent_actions
        intel_boost
        intel_decay_steps
        intel_boost_enabled

        % Per-step metric accumulators
        episode_attacks
        episode_mitigated
        episode_deceptions
        episode_deception_successes
        episode_false_positives
        episode_total_alerts
        episode_damage_prevented
        episode_cost_spent
        episode_defender_reward
        episode_attacker_reward
        episode_dwell_times

        % Per-attack detection tracking
        pending_attacks
        resolved_detection_delays

        history_window
        n_devices

        % Scale factors
        spread_scale
        detection_scale
        recovery_scale
    end


    methods

        %------------------------------------------------------------------
        % CONSTRUCTOR
        %------------------------------------------------------------------
        function obj = iiot_environment(config, varargin)
            obj.config = config;
            obj.max_steps = config.episode.max_steps;
            obj.history_window = 10;

            if nargin > 1 && ~isempty(varargin{1})
                obj.n_devices = varargin{1};
            else
                obj.n_devices = config.network.default_n_devices;
            end

            ref = 100;
            ratio = obj.n_devices / ref;
            obj.spread_scale    = sqrt(ratio);
            obj.detection_scale = 1 / sqrt(ratio);
            obj.recovery_scale  = ratio ^ (-0.3);
        end

        %------------------------------------------------------------------
        % RESET
        %------------------------------------------------------------------
        function [def_state, atk_state] = reset(obj, varargin)
            if nargin > 1 && ~isempty(varargin{1})
                rng(varargin{1});
            end

            obj.current_step = 0;

            obj.infection_rate  = obj.config.episode.initial_infection;
            obj.zone_infection  = obj.config.episode.initial_infection * ones(1, 3);
            obj.zone_infection  = obj.zone_infection + 0.02 * (rand(1,3) - 0.5);
            obj.zone_infection  = max(0, min(1, obj.zone_infection));
            obj.budget_remaining = obj.config.episode.initial_budget_remaining;
            obj.prev_infection_rate = obj.infection_rate;

            obj.skepticism      = obj.config.skepticism.initial;
            obj.momentum        = obj.config.momentum.initial;
            obj.recent_fp_rate  = 0;
            obj.deception_density = 0;

            obj.attack_history      = zeros(1, obj.history_window);
            obj.success_history     = zeros(1, obj.history_window);
            obj.defense_history     = zeros(1, obj.history_window);
            obj.deception_encounters = zeros(1, obj.history_window);
            obj.dwell_accumulator   = 0;
            obj.recent_actions      = [];
            obj.intel_boost         = 0;
            obj.intel_decay_steps   = 0;

            obj.episode_attacks            = 0;
            obj.episode_mitigated          = 0;
            obj.episode_deceptions         = 0;
            obj.episode_deception_successes = 0;
            obj.episode_false_positives    = 0;
            obj.episode_total_alerts       = 0;
            obj.episode_damage_prevented   = 0;
            obj.episode_cost_spent         = 0;
            obj.episode_defender_reward    = 0;
            obj.episode_attacker_reward    = 0;
            obj.episode_dwell_times        = [];

            obj.pending_attacks           = [];
            obj.resolved_detection_delays = [];

            def_state = obj.get_defender_state();
            atk_state = obj.get_attacker_state();
        end

        %------------------------------------------------------------------
        % STEP
        %------------------------------------------------------------------
        function [def_state, atk_state, def_reward, atk_reward, done, info] = ...
                step(obj, def_action, atk_action)

            obj.current_step = obj.current_step + 1;
            info = struct();

            obj.prev_infection_rate = obj.infection_rate;

            %--------------------------------------------------------------
            % 1. Decode actions
            %--------------------------------------------------------------
            def_action = max(1, min(obj.config.n_defender_actions, def_action));
            bundle     = obj.config.strategy_bundles(def_action, :);
            bundle_cost = sum(bundle .* obj.config.mechanism_costs);

            atk_action    = max(1, min(obj.config.n_attacker_actions, atk_action));
            atk_tactic    = obj.config.attacker_action_table(atk_action, 1);
            atk_intensity = obj.config.attacker_action_table(atk_action, 2);
            atk_zone      = obj.config.attacker_action_table(atk_action, 3);

            info.defender_bundle  = def_action;
            info.attacker_tactic  = atk_tactic;
            info.attacker_intensity = atk_intensity;
            info.attacker_zone    = atk_zone;

            %--------------------------------------------------------------
            % 2. Defense effectiveness
            %--------------------------------------------------------------
            defense_eff = sum(bundle .* obj.config.effectiveness(:, atk_tactic)');
            zone_bonus  = obj.config.zone_defense_bonus(atk_zone) * bundle(3);
            defense_eff = defense_eff + zone_bonus;

            if obj.intel_boost_enabled
                defense_eff = defense_eff + obj.intel_boost;
                if obj.intel_decay_steps > 0
                    obj.intel_boost = obj.intel_boost * ...
                        (obj.intel_decay_steps - 1) / obj.intel_decay_steps;
                    obj.intel_decay_steps = obj.intel_decay_steps - 1;
                end
            end

            defense_eff = min(defense_eff, 0.95);

            %--------------------------------------------------------------
            % 3. Attack success probability
            %--------------------------------------------------------------
            base_success   = obj.config.attack_base_success(atk_tactic);
            intensity_mult = obj.config.intensity_multipliers(atk_intensity);
            momentum_bonus = obj.momentum * obj.config.momentum.effect_on_success;

            attack_prob      = base_success * intensity_mult + momentum_bonus;
            attack_prob      = min(attack_prob, 0.95);
            net_success_prob = attack_prob * (1 - defense_eff);
            net_success_prob = max(0, min(1, net_success_prob));

            attack_succeeded = rand() < net_success_prob;

            info.defense_effectiveness = defense_eff;
            info.attack_probability    = attack_prob;
            info.net_success_prob      = net_success_prob;
            info.attack_succeeded      = attack_succeeded;

            %--------------------------------------------------------------
            % 4. Deception interaction
            %--------------------------------------------------------------
            deception_attempted = false;
            deception_succeeded = false;
            dwell_this_step     = 0;

            deception_weight      = bundle(1) + bundle(6);
            obj.deception_density = deception_weight;

            if deception_weight > 0.05
                deception_attempted = true;
                obj.episode_deceptions = obj.episode_deceptions + 1;

                engage_hp  = bundle(1) * obj.config.deception_engagement(1, atk_tactic);
                engage_dd  = bundle(6) * obj.config.deception_engagement(6, atk_tactic);
                engage_prob = engage_hp + engage_dd;

                skepticism_reduction = obj.skepticism * ...
                    obj.config.skepticism.effect_on_deception;
                skepticism_reduction = min(skepticism_reduction, 0.80);
                engage_prob = engage_prob * (1 - skepticism_reduction);

                if rand() < engage_prob
                    deception_succeeded = true;
                    obj.episode_deception_successes = ...
                        obj.episode_deception_successes + 1;

                    base_dwell    = 1 + randi(4);
                    dwell_this_step = max(1, round(base_dwell * ...
                        (1 - 0.5 * obj.skepticism)));
                    obj.dwell_accumulator = obj.dwell_accumulator + dwell_this_step;
                    obj.episode_dwell_times = [obj.episode_dwell_times, dwell_this_step];

                    if obj.intel_boost_enabled
                        obj.intel_boost       = 0.15;
                        obj.intel_decay_steps = 8;
                    end

                    if attack_succeeded
                        attack_succeeded      = false;
                        info.attack_succeeded = false;
                        info.trapped_by_deception = true;
                    end
                end
            end

            if deception_weight > 0.15
                normalized_deception = (deception_weight - 0.15) / 0.55;
                skep_inc  = obj.config.skepticism.increment * normalized_deception;
                obj.skepticism = min(obj.config.skepticism.max, ...
                    obj.skepticism + skep_inc);
            else
                obj.skepticism = obj.skepticism * obj.config.skepticism.decay;
            end

            info.deception_attempted = deception_attempted;
            info.deception_succeeded = deception_succeeded;
            info.dwell_this_step     = dwell_this_step;

            %--------------------------------------------------------------
            % 5. Update infection state
            %--------------------------------------------------------------
            obj.episode_attacks = obj.episode_attacks + 1;

            new_attack = struct('start_step', obj.current_step, ...
                                'tactic',     atk_tactic, ...
                                'zone',       atk_zone);

            if attack_succeeded
                damage = obj.config.breach_damage(atk_tactic) * ...
                         obj.config.zone_value(atk_zone) * ...
                         obj.config.intensity_multipliers(atk_intensity);
                damage = damage * 0.15;

                obj.zone_infection(atk_zone) = min(1, ...
                    obj.zone_infection(atk_zone) + damage);

                spread = obj.config.network.infection_spread_rate * ...
                         obj.zone_infection(atk_zone) * obj.spread_scale;
                for z = 1:3
                    if z ~= atk_zone
                        obj.zone_infection(z) = min(1, ...
                            obj.zone_infection(z) + spread * 0.5);
                    end
                end

                obj.momentum = min(obj.config.momentum.max, ...
                    obj.momentum + obj.config.momentum.increment);

                obj.pending_attacks = [obj.pending_attacks, new_attack];
            else
                obj.episode_mitigated = obj.episode_mitigated + 1;

                obj.resolved_detection_delays = ...
                    [obj.resolved_detection_delays, 0];

                potential_damage = obj.config.breach_damage(atk_tactic) * ...
                                   obj.config.zone_value(atk_zone) * ...
                                   obj.config.intensity_multipliers(atk_intensity);
                obj.episode_damage_prevented = ...
                    obj.episode_damage_prevented + potential_damage;

                obj.momentum = max(0, obj.momentum - ...
                    obj.config.momentum.decay_rate);
            end

            if ~isempty(obj.pending_attacks)
                detection_capability = (bundle(2) * 0.15 + bundle(5) * 0.08) * ...
                    obj.detection_scale;
                remaining = [];
                for pi = 1:length(obj.pending_attacks)
                    pa  = obj.pending_attacks(pi);
                    age = obj.current_step - pa.start_step;
                    detect_prob = detection_capability * (1 + 0.1 * age);
                    detect_prob = min(detect_prob, 0.5);
                    if rand() < detect_prob
                        delay = obj.current_step - pa.start_step;
                        obj.resolved_detection_delays = ...
                            [obj.resolved_detection_delays, delay];
                        obj.zone_infection(pa.zone) = max(0, ...
                            obj.zone_infection(pa.zone) - 0.02);
                    else
                        remaining = [remaining, pa];
                    end
                end
                obj.pending_attacks = remaining;
            end

            obj.zone_infection = max(0, obj.zone_infection - ...
                obj.config.network.recovery_rate * obj.recovery_scale);

            obj.infection_rate = sum(obj.zone_infection .* ...
                obj.config.network.zone_distribution);
            obj.infection_rate = max(0, min(1, obj.infection_rate));

            info.infection_rate  = obj.infection_rate;
            info.zone_infection  = obj.zone_infection;

            %--------------------------------------------------------------
            % 6. False positive generation
            %--------------------------------------------------------------
            bundle_fpr  = sum(bundle .* obj.config.mechanism_fpr);
            fp_occurred = rand() < bundle_fpr;
            if fp_occurred
                obj.episode_false_positives = obj.episode_false_positives + 1;
            end
            obj.episode_total_alerts = obj.episode_total_alerts + 1;
            if ~attack_succeeded
                obj.episode_total_alerts = obj.episode_total_alerts + 1;
            end

            alpha_fp = 0.1;
            obj.recent_fp_rate = (1 - alpha_fp) * obj.recent_fp_rate + ...
                                  alpha_fp * double(fp_occurred);

            info.false_positive = fp_occurred;

            %--------------------------------------------------------------
            % 7. Budget update
            %--------------------------------------------------------------
            obj.budget_remaining = obj.budget_remaining - bundle_cost;
            obj.budget_remaining = max(0, obj.budget_remaining);
            obj.episode_cost_spent = obj.episode_cost_spent + bundle_cost;

            info.step_cost        = bundle_cost;
            info.budget_remaining = obj.budget_remaining;

            %--------------------------------------------------------------
            % 8. Update histories
            %--------------------------------------------------------------
            obj.attack_history = [obj.attack_history(2:end), atk_tactic];
            obj.success_history = [obj.success_history(2:end), ...
                double(attack_succeeded)];
            obj.defense_history = [obj.defense_history(2:end), def_action];
            obj.deception_encounters = [obj.deception_encounters(2:end), ...
                double(deception_attempted)];

            %--------------------------------------------------------------
            % 9. Compute defender reward
            % FIX 1: Both diversity reward components removed.
            %         They proved to teach uniform ~25% action selection
            %         rather than threat-contingent behaviour.
            %         recent_actions tracking kept for state bookkeeping only.
            %--------------------------------------------------------------
            rw = obj.config.reward;
            def_reward = 0;

            % Mitigation reward
            if ~attack_succeeded
                def_reward = def_reward + rw.w_mitigation;
            end

            % Deception reward
            if deception_succeeded
                def_reward = def_reward + rw.w_deception;
            end

            % False positive penalty
            if fp_occurred
                def_reward = def_reward + rw.w_false_positive;
            end

            % Cost penalty
            def_reward = def_reward + rw.w_cost * bundle_cost;

            % Infection level penalty
            def_reward = def_reward + rw.w_infection * obj.infection_rate;

            % Infection delta reward
            infection_delta = obj.prev_infection_rate - obj.infection_rate;
            if isfield(rw, 'w_infection_delta')
                def_reward = def_reward + rw.w_infection_delta * infection_delta;
            end

            % Critical zone penalty
            if isfield(rw, 'w_critical_zone')
                def_reward = def_reward + rw.w_critical_zone * obj.zone_infection(3);
            end

            % Dwell time reward
            if dwell_this_step > 0
                def_reward = def_reward + rw.w_dwell * (dwell_this_step / 5);
            end

            % Momentum penalty
            def_reward = def_reward + rw.w_momentum_penalty * obj.momentum;

            % FIX 1: Only keep recent_actions for bookkeeping — no reward from it
            obj.recent_actions = [obj.recent_actions, def_action];
            if length(obj.recent_actions) > 10
                obj.recent_actions = obj.recent_actions(end-9:end);
            end

            obj.episode_defender_reward = obj.episode_defender_reward + def_reward;

            %--------------------------------------------------------------
            % 10. Compute attacker reward
            %--------------------------------------------------------------
            arw = obj.config.reward;
            atk_reward = 0;

            if attack_succeeded
                atk_reward = atk_reward + arw.attacker_w_success;
                atk_reward = atk_reward + arw.attacker_w_damage * ...
                    obj.config.breach_damage(atk_tactic) * ...
                    obj.config.zone_value(atk_zone);
            end

            if ~attack_succeeded && ~deception_succeeded
                atk_reward = atk_reward + arw.attacker_w_detection;
            end

            if deception_succeeded
                atk_reward = atk_reward + arw.attacker_w_trapped;
            end

            atk_reward = atk_reward + arw.attacker_w_cost * ...
                obj.config.intensity_cost(atk_intensity);
            atk_reward = atk_reward + arw.attacker_w_momentum * obj.momentum;

            obj.episode_attacker_reward = obj.episode_attacker_reward + atk_reward;

            info.defender_reward = def_reward;
            info.attacker_reward = atk_reward;

            %--------------------------------------------------------------
            % 11. Termination
            %--------------------------------------------------------------
            done = false;
            if obj.current_step >= obj.max_steps
                done = true;
                info.termination_reason = 'max_steps';
            elseif obj.config.episode.early_termination && ...
                    obj.infection_rate >= obj.config.episode.termination_threshold
                done = true;
                info.termination_reason = 'infection_threshold';
            elseif obj.budget_remaining <= 0
                done = true;
                info.termination_reason = 'budget_exhausted';
            end

            if ~done
                info.termination_reason = 'ongoing';
            end

            %--------------------------------------------------------------
            % 12. Build observations
            %--------------------------------------------------------------
            def_state = obj.get_defender_state();
            atk_state = obj.get_attacker_state();
        end

        %------------------------------------------------------------------
        % GET DEFENDER STATE
        %------------------------------------------------------------------
        function state = get_defender_state(obj)
            state = zeros(1, obj.config.defender_state.n_features);

            state(1) = obj.infection_rate;
            state(2) = obj.deception_density;

            last_atk = obj.attack_history(end);
            if last_atk == 0
                state(3) = 0;
            else
                state(3) = (last_atk - 1) / (obj.config.n_attack_categories - 1);
            end

            state(4) = mean(obj.success_history);
            state(5) = obj.momentum / obj.config.momentum.max;
            state(6) = obj.skepticism / obj.config.skepticism.max;
            state(7) = obj.budget_remaining / obj.config.episode.initial_budget_remaining;
            state(8) = obj.recent_fp_rate;
            state(9) = obj.current_step / obj.max_steps;
            state(10) = obj.zone_infection(1);
            state(11) = obj.zone_infection(2);
            state(12) = obj.zone_infection(3);
        end

        %------------------------------------------------------------------
        % GET ATTACKER STATE
        %------------------------------------------------------------------
        function state = get_attacker_state(obj)
            state = zeros(1, obj.config.attacker_state.n_features);

            last_def = obj.defense_history(end);
            if last_def == 0
                state(1) = 0;
            else
                state(1) = (last_def - 1) / (obj.config.n_defender_actions - 1);
            end

            state(2) = mean(obj.success_history);
            state(3) = obj.skepticism / obj.config.skepticism.max;
            state(4) = obj.momentum / obj.config.momentum.max;
            state(5) = mean(obj.deception_encounters);
            state(6) = mean(obj.zone_infection);
            state(7) = obj.current_step / obj.max_steps;

            recent_def = obj.defense_history(obj.defense_history > 0);
            if length(recent_def) < 2
                state(8) = 0;
            else
                changes  = sum(diff(recent_def) ~= 0);
                state(8) = changes / (length(recent_def) - 1);
            end
        end

        %------------------------------------------------------------------
        % DISCRETIZE STATE
        %------------------------------------------------------------------
        function idx = discretize_state(~, state, n_bins)
            n = length(state);
            sub_indices = zeros(1, n);
            for i = 1:n
                val = max(0, min(1, state(i)));
                bin = floor(val * n_bins(i));
                bin = min(bin, n_bins(i) - 1);
                sub_indices(i) = bin;
            end

            idx = sub_indices(1);
            multiplier = 1;
            for i = 2:n
                multiplier = multiplier * n_bins(i-1);
                idx = idx + sub_indices(i) * multiplier;
            end
            idx = idx + 1;
        end

        %------------------------------------------------------------------
        % GET EPISODE METRICS
        %------------------------------------------------------------------
        function metrics = get_episode_metrics(obj)
            metrics = struct();

            if obj.episode_attacks > 0
                metrics.AMR = obj.episode_mitigated / obj.episode_attacks;
            else
                metrics.AMR = 1.0;
            end

            if obj.episode_deceptions > 0
                metrics.DSR = obj.episode_deception_successes / ...
                    obj.episode_deceptions;
            else
                metrics.DSR = 0;
            end

            if obj.episode_total_alerts > 0
                metrics.FAR = obj.episode_false_positives / ...
                    obj.episode_total_alerts;
            else
                metrics.FAR = 0;
            end

            metrics.CumulativeReward = obj.episode_defender_reward;
            metrics.InfectionRate    = obj.infection_rate;

            if ~isempty(obj.resolved_detection_delays)
                metrics.MTTD = mean(obj.resolved_detection_delays);
            else
                metrics.MTTD = obj.max_steps;
            end

            if ~isempty(obj.episode_dwell_times)
                metrics.AttackerDwellTime = mean(obj.episode_dwell_times);
            else
                metrics.AttackerDwellTime = 0;
            end

            if obj.episode_cost_spent > 0
                metrics.DefenseCostEfficiency = ...
                    obj.episode_damage_prevented / obj.episode_cost_spent;
            else
                metrics.DefenseCostEfficiency = 0;
            end

            metrics.CVaR_005               = NaN;
            metrics.TrainingReliability_DR  = NaN;
            metrics.CrossDomainRetention    = NaN;
            metrics.AblationDegradation     = NaN;
            metrics.AttackerAdaptationRate  = NaN;
            metrics.NashConvergenceGap      = NaN;

            metrics.AttackerCumulativeReward = obj.episode_attacker_reward;
            metrics.EpisodeLength            = obj.current_step;
            metrics.FinalMomentum            = obj.momentum;
            metrics.FinalSkepticism          = obj.skepticism;
            metrics.BudgetRemaining          = obj.budget_remaining;
            metrics.PendingUndetected        = length(obj.pending_attacks);
        end

        %------------------------------------------------------------------
        % GET STATE SPACE SIZES
        %------------------------------------------------------------------
        function [def_size, atk_size] = get_state_space_sizes(obj)
            def_size = prod(obj.config.defender_state.n_bins);
            atk_size = prod(obj.config.attacker_state.n_bins);
        end

    end
end
