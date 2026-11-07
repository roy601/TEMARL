%%
% CoADAM Manuscript Figures - Batch 1 (Figures 1-5)
% Training convergence, training dynamics, defense behavior,
% baseline comparison (random attacker), baseline comparison (adaptive)
%
% Style: Times New Roman 15pt Bold, no pie charts, realistic variance
% Date: 01-Mar-2026
%%

clear; clc;
fprintf('=== CoADAM Manuscript Figures: Batch 1 ===\n');
fprintf('Generating Figures 1-5...\n\n');

project_root = '/Users/ujw/Desktop/CoADAM';
results_dir = fullfile(project_root, 'results');
fig_dir = fullfile(project_root, 'figures');
if ~exist(fig_dir, 'dir'), mkdir(fig_dir); 
end

% Load all data
training = load(fullfile(results_dir, 'dqn_cotraining_results.mat'));
baseline = load(fullfile(results_dir, 'baseline_results_final.mat'));

% Global style settings
set(0, 'DefaultAxesFontName', 'Times New Roman');
set(0, 'DefaultAxesFontSize', 15);
set(0, 'DefaultAxesFontWeight', 'bold');
set(0, 'DefaultTextFontName', 'Times New Roman');
set(0, 'DefaultTextFontSize', 15);
set(0, 'DefaultTextFontWeight', 'bold');
set(0, 'DefaultLineLineWidth', 1.5);

% Color scheme
c_coadam  = [0.00 0.45 0.74];  % blue
c_atk     = [0.85 0.33 0.10];  % red-orange
c_raw     = [0.80 0.80 0.80];  % light gray for raw data
c_smooth  = [0.00 0.45 0.74];  % blue for smoothed
c_conv    = [0.47 0.67 0.19];  % green for convergence marker

% Smoothing function (moving average)
smooth_fn = @(x, w) movmean(x, w);
win = 100;  % smoothing window

n_episodes = double(training.n_episodes);
episodes = 1:n_episodes;
conv_ep = double(training.convergence_episode);

%%
% FIGURE 1: Training Convergence
% (a) Defender reward  (b) Attacker reward  (c) AMR  (d) Training loss
%%

fprintf('Figure 1: Training Convergence...\n');
fig1 = figure('Position', [50 50 1200 900], 'Color', 'w');

% (a) Defender Reward
subplot(2,2,1);
plot(episodes, training.trk_def_reward, 'Color', [c_raw 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_def_reward, win), 'Color', c_coadam, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', c_conv, 'LineWidth', 1.5);
xlabel('Episode'); ylabel('Cumulative Reward');
title('(a) Defender Reward');
legend({'Raw', 'Moving Avg (100)', sprintf('Convergence (Ep %d)', conv_ep)}, ...
    'Location', 'southeast', 'FontSize', 10);
grid on; box on;

% (b) Attacker Reward
subplot(2,2,2);
plot(episodes, training.trk_atk_reward, 'Color', [c_atk 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_atk_reward, win), 'Color', c_atk, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', c_conv, 'LineWidth', 1.5);
xlabel('Episode'); ylabel('Cumulative Reward');
title('(b) Attacker Reward');
legend({'Raw', 'Moving Avg (100)', sprintf('Convergence (Ep %d)', conv_ep)}, ...
    'Location', 'northeast', 'FontSize', 10);
grid on; box on;

% (c) Attack Mitigation Rate
subplot(2,2,3);
plot(episodes, training.trk_amr, 'Color', [c_raw 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_amr, win), 'Color', c_coadam, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', c_conv, 'LineWidth', 1.5);
xlabel('Episode'); ylabel('AMR');
title('(c) Attack Mitigation Rate');
ylim([0.4 1.0]);
legend({'Raw', 'Moving Avg (100)', sprintf('Convergence (Ep %d)', conv_ep)}, ...
    'Location', 'southeast', 'FontSize', 10);
grid on; box on;

% (d) Training Loss
subplot(2,2,4);
loss_valid = training.trk_loss;
loss_valid(loss_valid == 0) = NaN;
plot(episodes, loss_valid, 'Color', [c_raw 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_loss, win), 'Color', [0.49 0.18 0.56], 'LineWidth', 2);
xline(conv_ep, '--', 'Color', c_conv, 'LineWidth', 1.5);
xlabel('Episode'); ylabel('TD Loss');
title('(d) Training Loss');
legend({'Raw', 'Moving Avg (100)', sprintf('Convergence (Ep %d)', conv_ep)}, ...
    'Location', 'northeast', 'FontSize', 10);
grid on; box on;

sgtitle('Figure 1: CoADAM Training Convergence', 'FontName', 'Times New Roman', ...
    'FontSize', 18, 'FontWeight', 'bold');

exportgraphics(fig1, fullfile(fig_dir, 'fig1_training_convergence.png'), 'Resolution', 300);
exportgraphics(fig1, fullfile(fig_dir, 'fig1_training_convergence.pdf'), 'ContentType', 'vector');
fprintf('  Saved.\n');

%%
% FIGURE 2: Training Dynamics
% (a) Infection rate  (b) Momentum  (c) Exploration rates  (d) Budget
%%

fprintf('Figure 2: Training Dynamics...\n');
fig2 = figure('Position', [50 50 1200 900], 'Color', 'w');

% (a) Infection Rate
subplot(2,2,1);
plot(episodes, training.trk_infection, 'Color', [c_atk 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_infection, win), 'Color', c_atk, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('Infection Rate');
title('(a) Infection Rate');
legend({'Raw', 'Moving Avg (100)', 'Convergence (Ep 1377)'}, ...
    'Location', 'northwest', 'FontSize', 10);
grid on; box on;

% (b) Momentum
subplot(2,2,2);
plot(episodes, training.trk_momentum, 'Color', [0.93 0.69 0.13 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_momentum, win), 'Color', [0.93 0.69 0.13], 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('Momentum');
title('(b) Attacker Momentum');
legend({'Raw', 'Moving Avg (100)'}, 'Location', 'northeast', 'FontSize', 10);
grid on; box on;

% (c) Exploration Rates (Defender & Attacker epsilon)
subplot(2,2,3);
plot(episodes, training.trk_eps_def, 'Color', c_coadam, 'LineWidth', 2); hold on;
plot(episodes, training.trk_eps_atk, 'Color', c_atk, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('Epsilon');
title('(c) Exploration Rates');
legend({'Defender \epsilon', 'Attacker \epsilon'}, 'Location', 'northeast', 'FontSize', 10);
ylim([0 0.25]);
grid on; box on;

% (d) Budget Remaining
subplot(2,2,4);
plot(episodes, training.trk_budget, 'Color', [c_conv 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_budget, win), 'Color', c_conv, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('Budget Remaining');
title('(d) Budget Utilization');
legend({'Raw', 'Moving Avg (100)'}, 'Location', 'northeast', 'FontSize', 10);
grid on; box on;

sgtitle('Figure 2: Co-Evolutionary Training Dynamics', 'FontName', 'Times New Roman', ...
    'FontSize', 18, 'FontWeight', 'bold');

exportgraphics(fig2, fullfile(fig_dir, 'fig2_training_dynamics.png'), 'Resolution', 300);
exportgraphics(fig2, fullfile(fig_dir, 'fig2_training_dynamics.pdf'), 'ContentType', 'vector');
fprintf('  Saved.\n');

%%
% FIGURE 3: Defense Behavior
% (a) DSR  (b) FAR  (c) MTTD  (d) Defense Cost Efficiency
%%

fprintf('Figure 3: Defense Behavior...\n');
fig3 = figure('Position', [50 50 1200 900], 'Color', 'w');

% (a) Deception Success Rate
subplot(2,2,1);
plot(episodes, training.trk_dsr, 'Color', [c_coadam 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_dsr, win), 'Color', c_coadam, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('DSR');
title('(a) Deception Success Rate');
legend({'Raw', 'Moving Avg (100)'}, 'Location', 'northeast', 'FontSize', 10);
grid on; box on;

% (b) False Alarm Rate
subplot(2,2,2);
plot(episodes, training.trk_far, 'Color', [0.85 0.33 0.10 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_far, win), 'Color', [0.85 0.33 0.10], 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('FAR');
title('(b) False Alarm Rate');
legend({'Raw', 'Moving Avg (100)'}, 'Location', 'northeast', 'FontSize', 10);
grid on; box on;

% (c) Mean Time to Detect
subplot(2,2,3);
plot(episodes, training.trk_mttd, 'Color', [0.49 0.18 0.56 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_mttd, win), 'Color', [0.49 0.18 0.56], 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('MTTD (steps)');
title('(c) Mean Time to Detect');
legend({'Raw', 'Moving Avg (100)'}, 'Location', 'northeast', 'FontSize', 10);
grid on; box on;

% (d) Defense Cost Efficiency
subplot(2,2,4);
plot(episodes, training.trk_dce, 'Color', [c_conv 0.3], 'LineWidth', 0.5); hold on;
plot(episodes, smooth_fn(training.trk_dce, win), 'Color', c_conv, 'LineWidth', 2);
xline(conv_ep, '--', 'Color', [0.4 0.6 0.2], 'LineWidth', 1.5, ...
    'Label', sprintf('Convergence (Ep %d)', conv_ep), ...
    'LabelOrientation', 'horizontal', 'FontName', 'Times New Roman', ...
    'FontSize', 9, 'FontWeight', 'bold');
xlabel('Episode'); ylabel('DCE');
title('(d) Defense Cost Efficiency');
legend({'Raw', 'Moving Avg (100)'}, 'Location', 'northeast', 'FontSize', 10);
grid on; box on;

sgtitle('Figure 3: Defense Behavior During Training', 'FontName', 'Times New Roman', ...
    'FontSize', 18, 'FontWeight', 'bold');

exportgraphics(fig3, fullfile(fig_dir, 'fig3_defense_behavior.png'), 'Resolution', 300);
exportgraphics(fig3, fullfile(fig_dir, 'fig3_defense_behavior.pdf'), 'ContentType', 'vector');
fprintf('  Saved.\n');

%%
% FIGURE 4: Baseline Comparison - Random Attacker (Table A)
% (a) AMR  (b) Infection  (c) Reward  (d) DSR
%%

fprintf('Figure 4: Baseline Comparison (Random Attacker)...\n');
fig4 = figure('Position', [50 50 1200 900], 'Color', 'w');

method_names = baseline.method_names;
n_methods = length(method_names);

% Color map for methods
method_colors = [
    0.50 0.50 0.50;   % Static - gray
    0.60 0.60 0.60;   % Random - lighter gray
    0.70 0.55 0.40;   % Heuristic - brown
    0.30 0.75 0.93;   % DQN_Individual - light blue
    0.93 0.69 0.13;   % Deception_Only - gold
    0.47 0.67 0.19;   % Stackelberg - green
    0.49 0.18 0.56;   % Tabular_QL - purple
    0.00 0.45 0.74;   % CoADAM_DQN - blue
];

% Short labels for x-axis
short_names = {'Static', 'Random', 'Heuris.', 'DQN-Ind', 'Dec-Only', 'Stack.', 'Tab-QL', 'CoADAM'};

% Extract Table A data (random attacker = mode 1)
amr_mean = zeros(1, n_methods);
amr_std = zeros(1, n_methods);
inf_mean = zeros(1, n_methods);
inf_std = zeros(1, n_methods);
rew_mean = zeros(1, n_methods);
rew_std = zeros(1, n_methods);
dsr_mean = zeros(1, n_methods);
dsr_std = zeros(1, n_methods);

for i = 1:n_methods
    r = baseline.results_tableA{i};
    amr_mean(i) = r.AMR.mean;           amr_std(i) = r.AMR.std;
    inf_mean(i) = r.InfectionRate.mean;  inf_std(i) = r.InfectionRate.std;
    rew_mean(i) = r.CumulativeReward.mean; rew_std(i) = r.CumulativeReward.std;
    dsr_mean(i) = r.DSR.mean;           dsr_std(i) = r.DSR.std;
end

% (a) AMR
subplot(2,2,1);
b1 = bar(1:n_methods, amr_mean, 0.7); hold on;
b1.FaceColor = 'flat';
for i = 1:n_methods
    b1.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, amr_mean, amr_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('AMR');
title('(a) Attack Mitigation Rate');
ylim([0.6 1.0]);
grid on; box on;

% (b) Infection Rate
subplot(2,2,2);
b2 = bar(1:n_methods, inf_mean, 0.7); hold on;
b2.FaceColor = 'flat';
for i = 1:n_methods
    b2.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, inf_mean, inf_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('Infection Rate');
title('(b) Infection Rate');
grid on; box on;

% (c) Cumulative Reward
subplot(2,2,3);
b3 = bar(1:n_methods, rew_mean, 0.7); hold on;
b3.FaceColor = 'flat';
for i = 1:n_methods
    b3.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, rew_mean, rew_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('Cumulative Reward');
title('(c) Cumulative Reward');
grid on; box on;

% (d) DSR
subplot(2,2,4);
b4 = bar(1:n_methods, dsr_mean, 0.7); hold on;
b4.FaceColor = 'flat';
for i = 1:n_methods
    b4.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, dsr_mean, dsr_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('DSR');
title('(d) Deception Success Rate');
grid on; box on;

sgtitle('Figure 4: Baseline Comparison — Random Attacker', 'FontName', 'Times New Roman', ...
    'FontSize', 18, 'FontWeight', 'bold');

exportgraphics(fig4, fullfile(fig_dir, 'fig4_baseline_random_attacker.png'), 'Resolution', 300);
exportgraphics(fig4, fullfile(fig_dir, 'fig4_baseline_random_attacker.pdf'), 'ContentType', 'vector');
fprintf('  Saved.\n');

fprintf('Figure 5: Baseline Comparison (Adapted Attacker)...\n');
fig5 = figure('Position', [50 50 1200 900], 'Color', 'w');

% Extract adapted attacker data (per-method attacker fine-tuned 500 episodes)
amr_ad = zeros(1, n_methods);
amr_ad_std = zeros(1, n_methods);
inf_ad = zeros(1, n_methods);
inf_ad_std = zeros(1, n_methods);
rew_ad = zeros(1, n_methods);
rew_ad_std = zeros(1, n_methods);

for i = 1:n_methods
    r = baseline.results_tableB{i};
    amr_ad(i) = r.AMR.mean;           amr_ad_std(i) = r.AMR.std;
    inf_ad(i) = r.InfectionRate.mean;  inf_ad_std(i) = r.InfectionRate.std;
    rew_ad(i) = r.CumulativeReward.mean; rew_ad_std(i) = r.CumulativeReward.std;
end

% (a) AMR
subplot(2,2,1);
b5 = bar(1:n_methods, amr_ad, 0.7); hold on;
b5.FaceColor = 'flat';
for i = 1:n_methods
    b5.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, amr_ad, amr_ad_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('AMR');
title('(a) Attack Mitigation Rate');
ylim([0.3 1.0]);
grid on; box on;

% (b) Infection Rate
subplot(2,2,2);
b6 = bar(1:n_methods, inf_ad, 0.7); hold on;
b6.FaceColor = 'flat';
for i = 1:n_methods
    b6.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, inf_ad, inf_ad_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('Infection Rate');
title('(b) Infection Rate');
grid on; box on;

% (c) Cumulative Reward
subplot(2,2,3);
b7 = bar(1:n_methods, rew_ad, 0.7); hold on;
b7.FaceColor = 'flat';
for i = 1:n_methods
    b7.CData(i,:) = method_colors(i,:);
end
errorbar(1:n_methods, rew_ad, rew_ad_std, 'k.', 'LineWidth', 1.2, 'CapSize', 6);
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('Cumulative Reward');
title('(c) Cumulative Reward');
grid on; box on;

% (d) Adaptation Robustness (degradation from random to adapted attacker)
subplot(2,2,4);
degrad = baseline.adapt_robustness;
b8 = bar(1:n_methods, degrad, 0.7); hold on;
b8.FaceColor = 'flat';
for i = 1:n_methods
    b8.CData(i,:) = method_colors(i,:);
end
set(gca, 'XTick', 1:n_methods, 'XTickLabel', short_names, 'XTickLabelRotation', 30);
ylabel('Degradation Score');
title('(d) Robustness: Random → Adapted Attacker (lower = better)');
grid on; box on;

sgtitle('Figure 5: Baseline Comparison — Adapted Attacker (Per-Method)', ...
    'FontName', 'Times New Roman', 'FontSize', 18, 'FontWeight', 'bold');

exportgraphics(fig5, fullfile(fig_dir, 'fig5_baseline_adapted_attacker.png'), 'Resolution', 300);
exportgraphics(fig5, fullfile(fig_dir, 'fig5_baseline_adapted_attacker.pdf'), 'ContentType', 'vector');
fprintf('  Saved.\n');

fprintf('\n=== Batch 1 Complete ===\n');
fprintf('Figures saved to: %s\n', fig_dir);
fprintf('Files: fig1-fig5 (.png 300dpi + .pdf vector)\n');
