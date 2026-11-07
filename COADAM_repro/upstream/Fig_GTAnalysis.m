%%
% CoADAM Figure 11: Game-Theoretic Analysis
%%

clear; clc;
fprintf('=== CoADAM Figure 11: Game-Theoretic Analysis ===\n');

project_root = '/Users/ujw/Desktop/CoADAM';
results_dir  = fullfile(project_root, 'results');
fig_dir      = fullfile(project_root, 'figures');
if ~exist(fig_dir, 'dir'), mkdir(fig_dir); end

% Load data
p9      = load(fullfile(results_dir, 'phase9_results.mat'));
trained = load(fullfile(results_dir, 'dqn_cotraining_results.mat'));
config  = load('/Users/ujw/Desktop/CoADAM/data/processed/environment_config.mat');

% Global style
set(0, 'DefaultAxesFontName',   'Times New Roman');
set(0, 'DefaultAxesFontSize',   13);
set(0, 'DefaultAxesFontWeight', 'bold');
set(0, 'DefaultTextFontName',   'Times New Roman');
set(0, 'DefaultTextFontSize',   13);
set(0, 'DefaultTextFontWeight', 'bold');
set(0, 'DefaultLineLineWidth',  1.5);

% Colors
c_coadam = [0.00 0.45 0.74];
c_atk    = [0.85 0.33 0.10];
c_green  = [0.47 0.67 0.19];
c_purple = [0.49 0.18 0.56];
c_gold   = [0.93 0.69 0.13];
c_theory = [0.85 0.10 0.10];

%% ---- Extract parameters ------------------------------------------------
cfg         = config.config;
lambda_d    = cfg.skepticism.decay;
delta_s     = cfg.skepticism.increment;
sigma_max   = cfg.skepticism.max;
T           = 100;

bundles     = cfg.strategy_bundles;
dec_weights = bundles(:,1) + bundles(:,6);

action_dist = double(trained.eval_action_counts) / ...
              sum(double(trained.eval_action_counts));
action_dist = action_dist(:);

% Per-action skepticism dynamics
skep_inc = zeros(4,1);
skep_dec = zeros(4,1);
theta_dec = 0.15;
for i = 1:4
    if dec_weights(i) > theta_dec
        skep_inc(i) = delta_s * (dec_weights(i) - theta_dec) / (1 - theta_dec);
        skep_dec(i) = 1.0;
    else
        skep_inc(i) = 0.0;
        skep_dec(i) = lambda_d;
    end
end

% Scalar alpha and beta
alpha = 0; beta = 0;
for i = 1:4
    alpha = alpha + action_dist(i) * skep_dec(i);
    beta  = beta  + action_dist(i) * skep_inc(i);
end

% Theoretical upper bound
sigma_upper = beta / (1 - alpha);
sigma_upper = min(sigma_upper, sigma_max);

% Empirical equilibrium
conv_ep     = double(trained.convergence_episode);
ep_log      = trained.episode_metrics_log;
post_skep   = cellfun(@(x) x.FinalSkepticism, ep_log(conv_ep:end));
sigma_emp   = mean(post_skep);
sigma_std   = std(post_skep);

% Decay rate
decay_rate  = p9.signaling.decay_rate;

% DQN action probabilities at different sigma levels
W1 = trained.W1; W2 = trained.W2; W3 = trained.W3;
b1 = trained.b1; b2 = trained.b2; b3 = trained.b3;

sigma_levels = linspace(0, sigma_max, 50);
dh_probs     = zeros(1, 50);

for si = 1:50
    sigma_norm = sigma_levels(si) / sigma_max;
    s = [0.0887; 0.3376; 1.0; 0.21; 0.1068; sigma_norm; ...
         0.5; 0.0232; 0.5; 0.08; 0.08; 0.09];
    h1_ = max(0, W1*s + b1);
    h2_ = max(0, W2*h1_ + b2);
    q   = W3*h2_ + b3;
    q_exp = exp(q - max(q));
    probs = q_exp / sum(q_exp);
    dh_probs(si) = probs(2);
end

% Episode trajectory from sigma=0
sigma_traj = zeros(1, T+1);
sigma_traj(1) = 0;
for t = 1:T
    sigma_traj(t+1) = min(sigma_max, alpha*sigma_traj(t) + beta);
end

fprintf('=== Equilibrium Analysis ===\n');
fprintf('alpha:          %.6f\n', alpha);
fprintf('beta:           %.6f\n', beta);
fprintf('sigma* upper:   %.4f\n', sigma_upper);
fprintf('sigma* empirical: %.4f +/- %.4f\n', sigma_emp, sigma_std);
fprintf('Decay rate: %.6f per episode\n', decay_rate);

%% ---- Build Figure 11 ---------------------------------------------------
fig11 = figure('Position', [30 30 1400 1050], 'Color', 'w');

%% ================================================================
%% Subplot (a): Equilibrium — manually positioned for more room
%% ================================================================
ax_a = axes('Position', [0.06 0.56 0.42 0.36]);

steps = 0:T;
plot(steps, sigma_traj, '-', 'Color', c_theory, 'LineWidth', 2.5); hold on;

% Upper bound
yline(sigma_upper, '--', 'Color', c_theory, 'LineWidth', 1.5);

% Empirical equilibrium
yline(sigma_emp, '-', 'Color', c_coadam, 'LineWidth', 2);

% Std band
fill([0 T T 0], ...
    [sigma_emp-sigma_std sigma_emp-sigma_std ...
     sigma_emp+sigma_std sigma_emp+sigma_std], ...
    c_coadam, 'FaceAlpha', 0.12, 'EdgeColor', 'none');

% Convergence point
[~, t_conv] = min(abs(sigma_traj - sigma_emp));
plot(t_conv, sigma_traj(t_conv), 'o', 'Color', c_green, ...
    'MarkerFaceColor', c_green, 'MarkerSize', 10);

% Annotations — placed to avoid overlap
text(t_conv+3, sigma_traj(t_conv)+0.04, ...
    sprintf('t^*=%d', t_conv), ...
    'FontSize', 10, 'Color', c_green);

xlabel('Episode Step');
ylabel('Skepticism \sigma', 'Interpreter', 'tex');
title({'(a) Deception Equilibrium:', ...
    sprintf('Unique Stable Point (\\alpha=%.4f<1)', alpha)}, 'FontSize', 13);

lgd_a = legend({'Trajectory (\sigma_0=0)', ...
    sprintf('\\sigma^*_{upper}=%.4f', sigma_upper), ...
    sprintf('\\sigma^*_{emp}=%.4f', sigma_emp), ...
    '\sigma^* \pm 1 std', '', 'Convergence'}, ...
    'Location', 'east', 'FontSize', 8);
lgd_a.BoxFace.ColorType = 'truecoloralpha';
lgd_a.BoxFace.ColorData = uint8([255 255 255 220]');

ylim([0 sigma_max + 0.05]);
xlim([0 T]);
grid on; box on;

% Inset: DH Policy — positioned inside top-left of subplot (a)
axes('Position', [0.08 0.80 0.10 0.09]);
plot(sigma_levels, dh_probs*100, '-', 'Color', c_purple, 'LineWidth', 1.5);
xlabel('\sigma', 'FontSize', 8, 'Interpreter', 'tex');
ylabel('P(DH)%', 'FontSize', 8);
title('DH Policy', 'FontSize', 8);
xline(sigma_emp, '--', 'Color', c_coadam, 'LineWidth', 1);
set(gca, 'FontSize', 8);
grid on;

%% ================================================================
%% Subplot (b): Exploitability — manually positioned
%% ================================================================
ax_b = axes('Position', [0.56 0.56 0.40 0.36]);

pool_ep  = p9.exploitability.pool_episodes;
pool_atk = p9.exploitability.pool_atk_reward;
pool_def = p9.exploitability.pool_def_reward;
coevol_v = p9.exploitability.coevol_atk_reward;
expl     = p9.exploitability.exploitability;

yyaxis left;
plot(pool_ep, pool_atk, 'o-', 'Color', c_atk, ...
    'MarkerFaceColor', c_atk, 'MarkerSize', 7, 'LineWidth', 2); hold on;
yline(coevol_v, '--', 'Color', [c_atk 0.6], 'LineWidth', 1.5);
ylabel('Attacker Reward');
set(gca, 'YColor', c_atk);

yyaxis right;
plot(pool_ep, pool_def, 's-', 'Color', c_coadam, ...
    'MarkerFaceColor', c_coadam, 'MarkerSize', 7, 'LineWidth', 2);
ylabel('Defender Reward');
set(gca, 'YColor', c_coadam);

xline(conv_ep, '--', 'Color', c_green, 'LineWidth', 1.5);

% Exploitability annotation — top left, away from data
yyaxis left;
ax_ylim = ylim;
text(pool_ep(1)+50, ax_ylim(2)*0.95, ...
    sprintf('Exploitability = %.2f (%.1f%%)', expl, ...
    expl/abs(coevol_v)*100), ...
    'FontSize', 10, 'Color', c_atk, ...
    'BackgroundColor', [1 1 1 0.85], 'EdgeColor', c_atk, ...
    'Margin', 3);

set(gca, 'XTick', pool_ep(1:2:end));
xlabel('Training Episode (Pool Snapshot)');
title({'(b) Exploitability Across Training:', ...
    sprintf('\\epsilon = %.2f (%.1f%% Normalized)', expl, ...
    expl/abs(coevol_v)*100)}, 'FontSize', 13, 'Interpreter', 'tex');

lgd_b = legend({'Atk Reward (pool)', 'Co-evol Atk Reward', ...
    'Def Reward (pool)', ...
    sprintf('Convergence (Ep %d)', conv_ep)}, ...
    'Location', 'south', 'FontSize', 8, 'NumColumns', 2);
lgd_b.BoxFace.ColorType = 'truecoloralpha';
lgd_b.BoxFace.ColorData = uint8([255 255 255 220]');
grid on; box on;

%% ================================================================
%% Subplot (c): Nash gap — manually positioned with extra bottom margin
%% ================================================================
ax_c = axes('Position', [0.06 0.08 0.40 0.36]);

V_def_dqn  = p9.nash_gap.V_def_dqn;
V_def_rand = p9.nash_gap.V_def_rand;
V_atk_fin  = p9.nash_gap.V_atk_final;
def_expl   = p9.nash_gap.def_exploitability;
atk_expl   = p9.nash_gap.atk_exploitability;
nash_g     = p9.nash_gap.nash_gap;

values     = [V_def_dqn, V_def_rand, V_atk_fin];
bar_colors = [c_coadam; c_purple; c_atk];

bh = bar(1:3, values, 0.55); hold on;
bh.FaceColor = 'flat';
for i = 1:3
    bh.CData(i,:) = bar_colors(i,:);
end

% Value labels on top of bars
for i = 1:3
    if values(i) >= 0
        va = 'bottom'; yoff = 2;
    else
        va = 'top'; yoff = -2;
    end
    text(i, values(i) + yoff, sprintf('%.1f', values(i)), ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', va, ...
        'FontSize', 10, 'FontWeight', 'bold');
end

% Nash gap annotation box — centered, below bars
y_range = max(values) - min(values);
text(2, min(values) - y_range*0.15, ...
    sprintf('Nash Gap = %.4f', nash_g), ...
    'HorizontalAlignment', 'center', 'FontSize', 11, ...
    'Color', c_atk, 'FontWeight', 'bold', ...
    'BackgroundColor', 'w', 'EdgeColor', c_atk, 'Margin', 4);

% Short category labels — no overlap
short_labels = {'Def (DQN)', 'Def (Random)', 'Atk (Final)'};
set(gca, 'XTick', 1:3, 'XTickLabel', short_labels, 'XTickLabelRotation', 0);
ylabel('Cumulative Reward');
title({'(c) Nash Equilibrium Gap:', ...
    sprintf('Gap=%.4f (Atk.Expl.=%.1f%%)', nash_g, ...
    atk_expl/abs(V_def_dqn)*100)}, 'FontSize', 13);

% Extend y limits to fit annotation
ylim([min(values)-y_range*0.35 max(values)*1.15]);
grid on; box on;

%% ================================================================
%% Subplot (d): Signaling dynamics — manually positioned
%% ================================================================
ax_d = axes('Position', [0.56 0.08 0.40 0.36]);

n_ep_total = double(trained.n_episodes);
episodes   = 1:n_ep_total;

skep_smooth = p9.signaling.skep_smooth;
mom_smooth  = p9.signaling.mom_smooth;
inf_smooth  = p9.signaling.inf_smooth;

% Normalize
skep_norm = skep_smooth / sigma_max;
mom_norm  = mom_smooth  / cfg.momentum.max;

yyaxis left;
plot(episodes, skep_norm, '-', 'Color', c_purple, 'LineWidth', 1.8); hold on;
plot(episodes, mom_norm,  '-', 'Color', c_gold,   'LineWidth', 1.8);
ylabel('Norm. Skepticism / Momentum');
ylim([0 1.15]);
set(gca, 'YColor', 'k');

yyaxis right;
plot(episodes, inf_smooth, '--', 'Color', c_atk, 'LineWidth', 1.8);
ylabel('Infection Rate');
ylim([0 0.5]);
set(gca, 'YColor', c_atk);

% Convergence line
xline(conv_ep, '--', 'Color', c_green, 'LineWidth', 1.5);

% Equilibrium reference
yyaxis left;
yline(sigma_emp/sigma_max, '-.', 'Color', [c_purple 0.5], 'LineWidth', 1.2);

xlabel('Training Episode');
title({'(d) Signaling Dynamics:', ...
    'Skepticism-Momentum-Infection Coupling'}, 'FontSize', 13);

lgd_d = legend({'Skepticism (norm.)', 'Momentum (norm.)', ...
    'Infection Rate', ...
    sprintf('Convergence (Ep %d)', conv_ep), ...
    '\sigma^* equilibrium'}, ...
    'Location', 'northeast', 'FontSize', 8);
lgd_d.BoxFace.ColorType = 'truecoloralpha';
lgd_d.BoxFace.ColorData = uint8([255 255 255 200]');
grid on; box on;

%% ---- Supertitle and save -----------------------------------------------
sgtitle({'Figure 11: Game-Theoretic Analysis', ...
    'Deception Signaling Equilibrium & Nash Convergence'}, ...
    'FontName', 'Times New Roman', 'FontSize', 14, 'FontWeight', 'bold');

exportgraphics(fig11, fullfile(fig_dir,'fig11_game_theoretic.png'), ...
    'Resolution', 300);
exportgraphics(fig11, fullfile(fig_dir,'fig11_game_theoretic.pdf'), ...
    'ContentType', 'vector');
fprintf('Figure 11 saved.\n');

% Reset defaults
set(0, 'DefaultAxesFontName',   'Helvetica');
set(0, 'DefaultAxesFontSize',   10);
set(0, 'DefaultAxesFontWeight', 'normal');
set(0, 'DefaultTextFontName',   'Helvetica');
set(0, 'DefaultTextFontSize',   10);
set(0, 'DefaultTextFontWeight', 'normal');

fprintf('=== Figure 11 Complete ===\n');
