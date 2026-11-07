%%
% CoADAM Manuscript Figures - Batch 2 (Figures 6-10)
% Adversarial adaptation, cross-domain transfer, ablation study,
% sensitivity & robustness, multi-scale scalability
%
% Style: Times New Roman 15pt Bold, no pie charts, realistic variance
% Date: 01-Mar-2026
%%

clear; clc;
fprintf('=== CoADAM Manuscript Figures: Batch 2 ===\n');
fprintf('Generating Figures 6-10...\n\n');

project_root = '/Users/ujw/Desktop/CoADAM';
results_dir = fullfile(project_root, 'results');
fig_dir = fullfile(project_root, 'figures');
if ~exist(fig_dir, 'dir'), mkdir(fig_dir); end

% Load all data
baseline   = load(fullfile(results_dir, 'baseline_results_final.mat'));
transfer   = load(fullfile(results_dir, 'transfer_results.mat'));
ablation   = load(fullfile(results_dir, 'ablation_results.mat'));
scalability = load(fullfile(results_dir, 'scalability_results.mat'));

% Global style settings
set(0, 'DefaultAxesFontName', 'Times New Roman');
set(0, 'DefaultAxesFontSize', 15);
set(0, 'DefaultAxesFontWeight', 'bold');
set(0, 'DefaultTextFontName', 'Times New Roman');
set(0, 'DefaultTextFontSize', 15);
set(0, 'DefaultTextFontWeight', 'bold');
set(0, 'DefaultLineLineWidth', 1.5);

% Color scheme
c_coadam = [0.00 0.45 0.74];
c_atk    = [0.85 0.33 0.10];
c_green  = [0.47 0.67 0.19];
c_purple = [0.49 0.18 0.56];
c_gold   = [0.93 0.69 0.13];
c_cyan   = [0.30 0.75 0.93];
c_gray   = [0.50 0.50 0.50];

method_colors = [
    0.50 0.50 0.50;
    0.60 0.60 0.60;
    0.70 0.55 0.40;
    0.30 0.75 0.93;
    0.93 0.69 0.13;
    0.47 0.67 0.19;
    0.49 0.18 0.56;
    0.00 0.45 0.74;
];

short_names = {'Static','Random','Heuris.','DQN-Ind','Dec-Only','Stack.','Tab-QL','CoADAM'};
n_methods   = length(baseline.method_names);

%%
% FIGURE 6: Adversarial Adaptation Analysis
% (a) AMR across 3 attacker modes
% (b) Infection across 3 attacker modes
% (c) Reward across 3 attacker modes
% (d) Degradation score ranking
%%

fprintf('Figure 6: Adversarial Adaptation...\n');
fig6 = figure('Position', [50 50 1200 900], 'Color', 'w');

amr_3mode = zeros(n_methods, 3);
inf_3mode = zeros(n_methods, 3);
rew_3mode = zeros(n_methods, 3);

for i = 1:n_methods
    r1 = baseline.results_tableA{i};
    amr_3mode(i,1) = r1.AMR.mean;
    inf_3mode(i,1) = r1.InfectionRate.mean;
    rew_3mode(i,1) = r1.CumulativeReward.mean;

    r2 = baseline.results_tableB{i};
    amr_3mode(i,2) = r2.AMR.mean;
    inf_3mode(i,2) = r2.InfectionRate.mean;
    rew_3mode(i,2) = r2.CumulativeReward.mean;

    ra = baseline.adapt_results{i};
    amr_3mode(i,3) = ra.AMR.mean;
    inf_3mode(i,3) = ra.InfectionRate.mean;
    rew_3mode(i,3) = ra.CumulativeReward.mean;
end

mode_colors = [0.30 0.70 0.90; 0.85 0.33 0.10; 0.60 0.10 0.10];
mode_labels = {'Random Attacker','Adaptive Attacker','Adapted Attacker'};

subplot(2,2,1);
b1 = bar(1:n_methods, amr_3mode, 0.85);
for m = 1:3, b1(m).FaceColor = mode_colors(m,:); end
set(gca,'XTick',1:n_methods,'XTickLabel',short_names,'XTickLabelRotation',30);
ylabel('AMR'); title('(a) AMR Across Attacker Modes');
ylim([0.4 1.0]);
legend(mode_labels,'Location','southwest','FontSize',9);
grid on; box on;

subplot(2,2,2);
b2 = bar(1:n_methods, inf_3mode, 0.85);
for m = 1:3, b2(m).FaceColor = mode_colors(m,:); end
set(gca,'XTick',1:n_methods,'XTickLabel',short_names,'XTickLabelRotation',30);
ylabel('Infection Rate'); title('(b) Infection Across Attacker Modes');
legend(mode_labels,'Location','northwest','FontSize',9);
grid on; box on;

subplot(2,2,3);
b3 = bar(1:n_methods, rew_3mode, 0.85);
for m = 1:3, b3(m).FaceColor = mode_colors(m,:); end
set(gca,'XTick',1:n_methods,'XTickLabel',short_names,'XTickLabelRotation',30);
ylabel('Cumulative Reward'); title('(c) Reward Across Attacker Modes');
legend(mode_labels,'Location','southwest','FontSize',9);
grid on; box on;

subplot(2,2,4);
degrad = baseline.adapt_robustness;
[sorted_deg, sort_idx] = sort(degrad,'ascend');
sorted_names  = short_names(sort_idx);
sorted_colors = method_colors(sort_idx,:);
bh = barh(1:n_methods, sorted_deg, 0.7);
bh.FaceColor = 'flat';
for i = 1:n_methods, bh.CData(i,:) = sorted_colors(i,:); end
set(gca,'YTick',1:n_methods,'YTickLabel',sorted_names);
xlabel('Degradation Score');
title('(d) Adaptation Robustness (lower = better)');
grid on; box on;

sgtitle('Figure 6: Adversarial Adaptation Analysis','FontName','Times New Roman',...
    'FontSize',18,'FontWeight','bold');
exportgraphics(fig6, fullfile(fig_dir,'fig6_adversarial_adaptation.png'),'Resolution',300);
exportgraphics(fig6, fullfile(fig_dir,'fig6_adversarial_adaptation.pdf'),'ContentType','vector');
fprintf('  Saved.\n');

%%
% FIGURE 7: Cross-Domain Transfer
% (a) AMR Table A vs B  (b) Infection  (c) Reward  (d) Composite scores
%%

fprintf('Figure 7: Cross-Domain Transfer...\n');
fig7 = figure('Position', [50 50 1200 900], 'Color', 'w');

domain_keys  = {'cic','wustl','edge'};
domain_names = {'CIC (Source)','WUSTL','Edge'};
n_domains    = length(domain_keys);

amr_A = zeros(1,n_domains); amr_A_std = zeros(1,n_domains);
amr_B = zeros(1,n_domains); amr_B_std = zeros(1,n_domains);
inf_A = zeros(1,n_domains); inf_A_std = zeros(1,n_domains);
inf_B = zeros(1,n_domains); inf_B_std = zeros(1,n_domains);
rew_A = zeros(1,n_domains); rew_A_std = zeros(1,n_domains);
rew_B = zeros(1,n_domains); rew_B_std = zeros(1,n_domains);
comp  = zeros(1,n_domains);

for d = 1:n_domains
    rA = transfer.results_A.(domain_keys{d});
    rB = transfer.results_B.(domain_keys{d});
    amr_A(d) = rA.AMR.mean;  amr_A_std(d) = rA.AMR.std;
    amr_B(d) = rB.AMR.mean;  amr_B_std(d) = rB.AMR.std;
    inf_A(d) = rA.InfectionRate.mean; inf_A_std(d) = rA.InfectionRate.std;
    inf_B(d) = rB.InfectionRate.mean; inf_B_std(d) = rB.InfectionRate.std;
    rew_A(d) = rA.CumulativeReward.mean; rew_A_std(d) = rA.CumulativeReward.std;
    rew_B(d) = rB.CumulativeReward.mean; rew_B_std(d) = rB.CumulativeReward.std;
    comp(d) = transfer.composite_scores(d);
end

tab_colors = [c_coadam; c_atk];
tab_labels = {'Natural Distribution (Table A)','CIC Source Distribution (Table B)'};

subplot(2,2,1);
grp = [amr_A; amr_B]';
grp_std = [amr_A_std; amr_B_std]';
b1 = bar(1:n_domains, grp, 0.8); hold on;
b1(1).FaceColor = tab_colors(1,:);
b1(2).FaceColor = tab_colors(2,:);
for k = 1:2
    errorbar(b1(k).XEndPoints, grp(:,k), grp_std(:,k), 'k.','LineWidth',1.2,'CapSize',6);
end
set(gca,'XTick',1:n_domains,'XTickLabel',domain_names);
ylabel('AMR'); title('(a) Attack Mitigation Rate');
ylim([0.6 1.0]);
legend(tab_labels,'Location','southwest','FontSize',9);
grid on; box on;

subplot(2,2,2);
grp = [inf_A; inf_B]';
grp_std = [inf_A_std; inf_B_std]';
b2 = bar(1:n_domains, grp, 0.8); hold on;
b2(1).FaceColor = tab_colors(1,:);
b2(2).FaceColor = tab_colors(2,:);
for k = 1:2
    errorbar(b2(k).XEndPoints, grp(:,k), grp_std(:,k), 'k.','LineWidth',1.2,'CapSize',6);
end
set(gca,'XTick',1:n_domains,'XTickLabel',domain_names);
ylabel('Infection Rate'); title('(b) Infection Rate');
legend(tab_labels,'Location','northwest','FontSize',9);
grid on; box on;

subplot(2,2,3);
grp = [rew_A; rew_B]';
grp_std = [rew_A_std; rew_B_std]';
b3 = bar(1:n_domains, grp, 0.8); hold on;
b3(1).FaceColor = tab_colors(1,:);
b3(2).FaceColor = tab_colors(2,:);
for k = 1:2
    errorbar(b3(k).XEndPoints, grp(:,k), grp_std(:,k), 'k.','LineWidth',1.2,'CapSize',6);
end
set(gca,'XTick',1:n_domains,'XTickLabel',domain_names);
ylabel('Cumulative Reward'); title('(c) Cumulative Reward');
legend(tab_labels,'Location','southwest','FontSize',9);
grid on; box on;

subplot(2,2,4);
bar_colors = [c_coadam; c_green; c_gold];
bh = bar(1:n_domains, comp, 0.6); hold on;
bh.FaceColor = 'flat';
for i = 1:n_domains, bh.CData(i,:) = bar_colors(i,:); end
yline(0.95,'r--','LineWidth',1.5);
yline(1.0,'k-','LineWidth',1);
text(n_domains+0.3, 0.95, 'Excellent threshold','FontSize',10,'Color','r',...
    'FontName','Times New Roman');
set(gca,'XTick',1:n_domains,'XTickLabel',domain_names);
ylabel('Composite Score'); title('(d) Transfer Quality Score');
ylim([0.8 1.2]);
grid on; box on;

sgtitle('Figure 7: Cross-Domain Transfer Performance','FontName','Times New Roman',...
    'FontSize',18,'FontWeight','bold');
exportgraphics(fig7, fullfile(fig_dir,'fig7_cross_domain_transfer.png'),'Resolution',300);
exportgraphics(fig7, fullfile(fig_dir,'fig7_cross_domain_transfer.pdf'),'ContentType','vector');
fprintf('  Saved.\n');

%%
% FIGURE 8: Ablation Study
% (a) AMR  (b) Reward  (c) Infection  (d) Cohen's d heatmap
%%

fprintf('Figure 8: Ablation Study...\n');
fig8 = figure('Position', [50 50 1200 900], 'Color', 'w');

n_variants = ablation.n_variants;
var_short  = ablation.variant_short;

abl_amr     = zeros(1,n_variants);
abl_amr_std = zeros(1,n_variants);
abl_rew     = zeros(1,n_variants);
abl_rew_std = zeros(1,n_variants);
abl_inf     = zeros(1,n_variants);
abl_inf_std = zeros(1,n_variants);

for i = 1:n_variants
    v = ablation.ablation.(var_short{i});
    abl_amr(i)     = v.AMR.mean;
    abl_amr_std(i) = v.AMR.std;
    abl_rew(i)     = v.CumulativeReward.mean;
    abl_rew_std(i) = v.CumulativeReward.std;
    abl_inf(i)     = v.InfectionRate.mean;
    abl_inf_std(i) = v.InfectionRate.std;
end

abl_colors = [
    c_coadam;
    c_gray;
    c_atk;
    0.70 0.55 0.40;
    c_gold;
    c_purple;
    c_cyan;
];

subplot(2,2,1);
bh = bar(1:n_variants, abl_amr, 0.7); hold on;
bh.FaceColor = 'flat';
for i = 1:n_variants, bh.CData(i,:) = abl_colors(i,:); end
errorbar(1:n_variants, abl_amr, abl_amr_std,'k.','LineWidth',1.2,'CapSize',6);
yline(abl_amr(1),'b--','LineWidth',1.2);
set(gca,'XTick',1:n_variants,'XTickLabel',var_short,'XTickLabelRotation',35);
ylabel('AMR'); title('(a) Attack Mitigation Rate');
ylim([0.5 1.0]);
grid on; box on;

subplot(2,2,2);
bh = bar(1:n_variants, abl_rew, 0.7); hold on;
bh.FaceColor = 'flat';
for i = 1:n_variants, bh.CData(i,:) = abl_colors(i,:); end
errorbar(1:n_variants, abl_rew, abl_rew_std,'k.','LineWidth',1.2,'CapSize',6);
yline(abl_rew(1),'b--','LineWidth',1.2);
set(gca,'XTick',1:n_variants,'XTickLabel',var_short,'XTickLabelRotation',35);
ylabel('Cumulative Reward'); title('(b) Cumulative Reward');
grid on; box on;

subplot(2,2,3);
bh = bar(1:n_variants, abl_inf, 0.7); hold on;
bh.FaceColor = 'flat';
for i = 1:n_variants, bh.CData(i,:) = abl_colors(i,:); end
errorbar(1:n_variants, abl_inf, abl_inf_std,'k.','LineWidth',1.2,'CapSize',6);
yline(abl_inf(1),'b--','LineWidth',1.2);
set(gca,'XTick',1:n_variants,'XTickLabel',var_short,'XTickLabelRotation',35);
ylabel('Infection Rate'); title('(c) Infection Rate');
grid on; box on;

subplot(2,2,4);
metrics_for_d = {'AMR','CumulativeReward','InfectionRate'};
metric_labels_d = {'AMR','Reward','Infection'};
d_matrix = zeros(n_variants-1, length(metrics_for_d));
full_data = ablation.ablation.(var_short{1});

for vi = 2:n_variants
    var_data = ablation.ablation.(var_short{vi});
    for m = 1:length(metrics_for_d)
        mn = metrics_for_d{m};
        full_raw = full_data.(mn).raw;
        var_raw  = var_data.(mn).raw;
        pooled_std = sqrt((std(full_raw)^2 + std(var_raw)^2) / 2);
        if pooled_std > 0
            d_matrix(vi-1,m) = abs(mean(full_raw) - mean(var_raw)) / pooled_std;
        end
    end
end

imagesc(d_matrix);
colormap(subplot(2,2,4), flipud(hot));
colorbar;
set(gca,'XTick',1:length(metric_labels_d),'XTickLabel',metric_labels_d);
set(gca,'YTick',1:(n_variants-1),'YTickLabel',var_short(2:end));
title('(d) Effect Size (|Cohen''s d|)');
for r = 1:size(d_matrix,1)
    for c = 1:size(d_matrix,2)
        val = d_matrix(r,c);
        txt_color = 'k';
        if val > 2, txt_color = 'w'; end
        text(c, r, sprintf('%.2f',val),'HorizontalAlignment','center',...
            'FontSize',11,'FontWeight','bold','Color',txt_color,...
            'FontName','Times New Roman');
    end
end

sgtitle('Figure 8: Ablation Study — Component Contributions','FontName','Times New Roman',...
    'FontSize',18,'FontWeight','bold');
exportgraphics(fig8, fullfile(fig_dir,'fig8_ablation_study.png'),'Resolution',300);
exportgraphics(fig8, fullfile(fig_dir,'fig8_ablation_study.pdf'),'ContentType','vector');
fprintf('  Saved.\n');

%%
% FIGURE 9: Sensitivity & Robustness
% (a) Reward sensitivity  (b) Cross-seed AMR  (c) Cross-seed Reward  (d) 95% CI
%%

fprintf('Figure 9: Sensitivity & Robustness...\n');
fig9 = figure('Position', [50 50 1200 900], 'Color', 'w');

% Build sensitivity arrays from struct fields
sens        = ablation.sensitivity;
param_keys  = {'w_mitigation','w_deception','w_cost','w_infection',...
               'w_infection_delta','w_momentum_penalty','w_critical_zone'};
param_short = {'w\_mit','w\_dec','w\_cost','w\_inf','w\_inf\_d','w\_mom','w\_crit'};
n_params_s  = length(param_keys);

rew_05x = zeros(1,n_params_s);
rew_1x  = zeros(1,n_params_s);
rew_2x  = zeros(1,n_params_s);

for pi = 1:n_params_s
    pr = sens.(param_keys{pi});
    rew_05x(pi) = pr.scale_1.reward_mean;
    rew_1x(pi)  = pr.scale_2.reward_mean;
    rew_2x(pi)  = pr.scale_3.reward_mean;
end

subplot(2,2,1);
x = 1:n_params_s;
plot(x, rew_05x,'s-','Color',c_coadam,'MarkerFaceColor',c_coadam,'MarkerSize',8,'LineWidth',2); hold on;
plot(x, rew_1x, 'o-','Color',c_green, 'MarkerFaceColor',c_green, 'MarkerSize',8,'LineWidth',2);
plot(x, rew_2x, 'd-','Color',c_atk,  'MarkerFaceColor',c_atk,   'MarkerSize',8,'LineWidth',2);
set(gca,'XTick',x,'XTickLabel',param_short,'XTickLabelRotation',35);
ylabel('Cumulative Reward'); title('(a) Reward Sensitivity to Weights');
legend({'0.5x','1.0x (base)','2.0x'},'Location','best','FontSize',10);
grid on; box on;

% Cross-seed data from per_seed_means matrix [n_seeds x 4]: AMR, Reward, Infection, DSR
seed_means  = ablation.seed_analysis.per_seed_means;
seed_values = ablation.seed_analysis.seed_values;
n_seeds     = ablation.seed_analysis.n_seeds;
n_seed_eval = ablation.seed_analysis.n_seed_eval;
seed_labels = arrayfun(@(x) sprintf('S%d',x), seed_values,'UniformOutput',false);

% per_seed_means is [n_seeds x 4] — columns: AMR, Reward, Infection, DSR
% For box plots we need episode-level raw data which is not stored per seed.
% We simulate the distribution using mean and std from per_seed_means
% and plot per-seed means as a bar chart instead.

subplot(2,2,2);
bar(1:n_seeds, seed_means(:,1), 0.7,'FaceColor',c_coadam);
hold on;
yline(mean(seed_means(:,1)),'k--','LineWidth',1.5);
set(gca,'XTick',1:n_seeds,'XTickLabel',seed_labels,'XTickLabelRotation',30);
ylabel('AMR'); title('(b) Per-Seed AMR Means');
grid on; box on;

subplot(2,2,3);
bar(1:n_seeds, seed_means(:,2), 0.7,'FaceColor',c_green);
hold on;
yline(mean(seed_means(:,2)),'k--','LineWidth',1.5);
set(gca,'XTick',1:n_seeds,'XTickLabel',seed_labels,'XTickLabelRotation',30);
ylabel('Cumulative Reward'); title('(c) Per-Seed Reward Means');
grid on; box on;

% 95% CI from ci_results struct
ci      = ablation.seed_analysis.ci_results;
ci_keys = {'AMR','Reward','Infection','DSR'};
ci_labels_plot = {'AMR','Reward','Infection','DSR'};
ci_means  = zeros(1,4);
ci_lo     = zeros(1,4);
ci_hi     = zeros(1,4);

for m = 1:4
    ci_means(m) = ci.(ci_keys{m}).mean;
    ci_lo(m)    = ci.(ci_keys{m}).ci_lower;
    ci_hi(m)    = ci.(ci_keys{m}).ci_upper;
end

subplot(2,2,4);
for m = 1:4
    errorbar(m, ci_means(m), ci_means(m)-ci_lo(m), ci_hi(m)-ci_means(m),...
        'o','Color',c_coadam,'MarkerFaceColor',c_coadam,...
        'MarkerSize',10,'LineWidth',2,'CapSize',10); hold on;
end

% Annotate small-valued metrics so they are not invisible on the y-axis scale
text(3, ci_means(3) + (max(ci_means)*0.05), ...
    sprintf('%.4f', ci_means(3)), ...
    'HorizontalAlignment','center','FontName','Times New Roman',...
    'FontSize',9,'FontWeight','bold','Color','k');
text(4, ci_means(4) + (max(ci_means)*0.05), ...
    sprintf('%.4f', ci_means(4)), ...
    'HorizontalAlignment','center','FontName','Times New Roman',...
    'FontSize',9,'FontWeight','bold','Color','k');

set(gca,'XTick',1:4,'XTickLabel',ci_labels_plot);
ylabel('Value'); title('(d) 95% Bootstrap Confidence Intervals');
grid on; box on;

sgtitle('Figure 9: Sensitivity & Statistical Robustness','FontName','Times New Roman',...
    'FontSize',18,'FontWeight','bold');
exportgraphics(fig9, fullfile(fig_dir,'fig9_sensitivity_robustness.png'),'Resolution',300);
exportgraphics(fig9, fullfile(fig_dir,'fig9_sensitivity_robustness.pdf'),'ContentType','vector');
fprintf('  Saved.\n');

%%
% FIGURE 10: Multi-Scale Scalability
% (a) AMR & Infection vs scale  (b) Advantage vs scale
% (c) Composite score  (d) Risk analysis
%%

fprintf('Figure 10: Multi-Scale Scalability...\n');
fig10 = figure('Position', [50 50 1200 900], 'Color', 'w');

scales      = scalability.scale_levels;
n_scales    = length(scales);
train_scale = scalability.training_scale;
scale_keys  = {'s50','s100','s200','s500','s1000'};

amr_scale     = zeros(1,n_scales);
inf_scale     = zeros(1,n_scales);
cvar_scale    = zeros(1,n_scales);
rew_std_scale = zeros(1,n_scales);

for si = 1:n_scales
    sr = scalability.scale_results.(scale_keys{si});
    amr_scale(si)     = sr.AMR.mean;
    inf_scale(si)     = sr.InfectionRate.mean;
    cvar_scale(si)    = sr.CVaR_005;
    rew_std_scale(si) = sr.CumulativeReward.std;
end

subplot(2,2,1);
yyaxis left;
plot(1:n_scales, amr_scale,'o-','Color',c_coadam,'MarkerFaceColor',c_coadam,...
    'MarkerSize',10,'LineWidth',2);
ylabel('AMR'); ylim([0.7 0.85]);
yyaxis right;
plot(1:n_scales, inf_scale,'s-','Color',c_atk,'MarkerFaceColor',c_atk,...
    'MarkerSize',10,'LineWidth',2);
ylabel('Infection Rate');
set(gca,'XTick',1:n_scales,'XTickLabel',arrayfun(@num2str,scales,'UniformOutput',false));
xlabel('Network Scale (devices)'); title('(a) AMR & Infection vs Scale');
hold on;
train_idx = find(scales == train_scale);
yyaxis left;
plot(train_idx, amr_scale(train_idx),'p','Color',c_green,...
    'MarkerFaceColor',c_green,'MarkerSize',18);
% Legend moved here AFTER all three plot calls
legend({'AMR','Infection','Training Scale'},'Location','west','FontSize',10);
grid on; box on;

subplot(2,2,2);
% advantage_fair and advantage_adapt are plain numeric matrices
adv_fair  = scalability.advantage_fair;
adv_adapt = scalability.advantage_adapt;
plot(1:n_scales, adv_fair(:,1),'o-','Color',c_coadam,'MarkerFaceColor',c_coadam,...
    'MarkerSize',8,'LineWidth',2); hold on;
plot(1:n_scales, adv_adapt(:,1),'s-','Color',c_atk,'MarkerFaceColor',c_atk,...
    'MarkerSize',8,'LineWidth',2);
yline(0,'k--','LineWidth',1);
set(gca,'XTick',1:n_scales,'XTickLabel',arrayfun(@num2str,scales,'UniformOutput',false));
xlabel('Network Scale (devices)'); ylabel('AMR Advantage');
title('(b) CoADAM AMR Advantage Over Random');
legend({'vs Random Atk (Fair)','vs Adaptive Atk'},'Location','best','FontSize',10);
grid on; box on;

subplot(2,2,3);
comp = scalability.scalability_scores;
scale_colors = [c_cyan; c_coadam; c_green; c_gold; c_atk];
bh = bar(1:n_scales, comp, 0.6); hold on;
bh.FaceColor = 'flat';
for i = 1:n_scales, bh.CData(i,:) = scale_colors(i,:); end
yline(0.95,'g--','LineWidth',1.5);
yline(0.85,'Color',c_gold,'LineStyle','--','LineWidth',1.5);
yline(0.70,'r--','LineWidth',1.5);
text(n_scales+0.2, 0.96,'Excellent','FontSize',9,'Color',c_green,'FontName','Times New Roman');
text(n_scales+0.2, 0.86,'Good','FontSize',9,'Color',c_gold,'FontName','Times New Roman');
text(n_scales+0.2, 0.71,'Moderate','FontSize',9,'Color','r','FontName','Times New Roman');
set(gca,'XTick',1:n_scales,'XTickLabel',arrayfun(@num2str,scales,'UniformOutput',false));
xlabel('Network Scale (devices)'); ylabel('Composite Score');
title('(c) Scalability Score'); ylim([0.5 1.2]);
grid on; box on;

subplot(2,2,4);
yyaxis left;
plot(1:n_scales, cvar_scale,'o-','Color',c_purple,'MarkerFaceColor',c_purple,...
    'MarkerSize',10,'LineWidth',2);
ylabel('CVaR (0.05)');
yyaxis right;
plot(1:n_scales, rew_std_scale,'s-','Color',c_gold,'MarkerFaceColor',c_gold,...
    'MarkerSize',10,'LineWidth',2);
ylabel('Reward Std');
set(gca,'XTick',1:n_scales,'XTickLabel',arrayfun(@num2str,scales,'UniformOutput',false));
xlabel('Network Scale (devices)'); title('(d) Risk Analysis Across Scales');
legend({'CVaR (5%)','Reward Std'},'Location','best','FontSize',10);
grid on; box on;

sgtitle('Figure 10: Multi-Scale Scalability Analysis','FontName','Times New Roman',...
    'FontSize',18,'FontWeight','bold');
exportgraphics(fig10, fullfile(fig_dir,'fig10_scalability.png'),'Resolution',300);
exportgraphics(fig10, fullfile(fig_dir,'fig10_scalability.pdf'),'ContentType','vector');
fprintf('  Saved.\n');

% Reset defaults
set(0,'DefaultAxesFontName','Helvetica');
set(0,'DefaultAxesFontSize',10);
set(0,'DefaultAxesFontWeight','normal');
set(0,'DefaultTextFontName','Helvetica');
set(0,'DefaultTextFontSize',10);
set(0,'DefaultTextFontWeight','normal');

fprintf('\n=== Batch 2 Complete ===\n');
fprintf('Figures saved to: %s\n', fig_dir);
fprintf('Files: fig6-fig10 (.png 300dpi + .pdf vector)\n');
