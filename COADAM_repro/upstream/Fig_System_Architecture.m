clear; clc;
fprintf('=== CoADAM Figure: System Architecture ===\n');

project_root = '/Users/ujw/Desktop/CoADAM';
fig_dir      = fullfile(project_root, 'figures');
if ~exist(fig_dir, 'dir'), mkdir(fig_dir); end

fig = figure('Position', [30 30 1600 1050], 'Color', 'w');
ax  = axes('Position', [0.03 0.03 0.94 0.94], 'Visible', 'off');
hold on;
xlim([0 16]); ylim([0 11.5]);
axis off;

%% ---- Colors (LIGHTER / more readable) ----
c_blue   = [0.20 0.56 0.84];
c_orange = [0.93 0.62 0.20];
c_green  = [0.25 0.65 0.32];
c_red    = [0.88 0.30 0.25];
c_purple = [0.58 0.30 0.65];
c_gray   = [0.55 0.55 0.55];
c_gold   = [0.90 0.70 0.10];
c_white  = [1 1 1];

% Darker versions for edges
c_blue_e   = c_blue * 0.75;
c_orange_e = c_orange * 0.75;
c_green_e  = c_green * 0.70;
c_red_e    = c_red * 0.75;
c_purple_e = c_purple * 0.70;
c_gray_e   = c_gray * 0.70;

%% ---- Arrowhead size ----
ah = 0.14; aw = 0.11;
line_col = [0.50 0.50 0.50];

%% ================================================================
%%  TITLE
%% ================================================================
text(8.0, 11.15, 'CoADAM: System Architecture', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',18,'FontWeight','bold','Color','k');

%% ================================================================
%%  ROW 1 — DATASETS  (y = 10.2)
%% ================================================================
y1 = 10.2;  bw1 = 2.8;  bh1 = 0.75;

% Group label
text(8.0, y1+0.60, 'Dataset Layer', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',12,'FontWeight','bold','Color',c_blue_e);

% CIC
rectangle('Position', [2.5-bw1/2, y1-bh1/2, bw1, bh1], 'Curvature', 0.18, ...
    'FaceColor', c_blue, 'EdgeColor', c_blue_e, 'LineWidth', 2);
text(2.5, y1+0.10, 'CIC-IIoT-2025', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white);
text(2.5, y1-0.15, '(Primary)', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9.5,'FontWeight','bold','Color',[0.9 0.95 1]);

% WUSTL
rectangle('Position', [8.0-bw1/2, y1-bh1/2, bw1, bh1], 'Curvature', 0.18, ...
    'FaceColor', c_blue, 'EdgeColor', c_blue_e, 'LineWidth', 2);
text(8.0, y1+0.10, 'WUSTL-IIoT-2021', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white);
text(8.0, y1-0.15, '(Transfer)', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9.5,'FontWeight','bold','Color',[0.9 0.95 1]);

% Edge
rectangle('Position', [13.5-bw1/2, y1-bh1/2, bw1, bh1], 'Curvature', 0.18, ...
    'FaceColor', c_blue, 'EdgeColor', c_blue_e, 'LineWidth', 2);
text(13.5, y1+0.10, 'Edge-IIoTset', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white);
text(13.5, y1-0.15, '(Transfer)', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9.5,'FontWeight','bold','Color',[0.9 0.95 1]);

%% ---- Arrows: Datasets -> Preprocessing ----
y_a1_top = y1 - bh1/2;
y_a1_bot = 9.0 + 0.40;

plot([2.5 6.2], [y_a1_top y_a1_bot], '-', 'Color', line_col, 'LineWidth', 1.6);
plot([8.0 8.0], [y_a1_top y_a1_bot], '-', 'Color', line_col, 'LineWidth', 1.6);
plot([13.5 9.8], [y_a1_top y_a1_bot], '-', 'Color', line_col, 'LineWidth', 1.6);
patch([6.2-aw 6.2 6.2+aw], [y_a1_bot+ah y_a1_bot y_a1_bot+ah], line_col, 'EdgeColor','none');
patch([8.0-aw 8.0 8.0+aw], [y_a1_bot+ah y_a1_bot y_a1_bot+ah], line_col, 'EdgeColor','none');
patch([9.8-aw 9.8 9.8+aw], [y_a1_bot+ah y_a1_bot y_a1_bot+ah], line_col, 'EdgeColor','none');

%% ================================================================
%%  ROW 2 — PREPROCESSING  (y = 9.0)
%% ================================================================
y2 = 9.0;  bw2 = 6.8;  bh2 = 0.75;

rectangle('Position', [8.0-bw2/2, y2-bh2/2, bw2, bh2], 'Curvature', 0.15, ...
    'FaceColor', c_orange, 'EdgeColor', c_orange_e, 'LineWidth', 2);
text(8.0, y2+0.12, 'Phase 1: Data Preprocessing', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white);
text(8.0, y2-0.14, 'MITRE ATT&CK Mapping | Min-Max Norm [0,1] | 80/20 Split', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',[1 0.97 0.9]);

% Arrow down
y_a2_bot = 8.0 + 0.40;
plot([8.0 8.0], [y2-bh2/2 y_a2_bot], '-', 'Color', line_col, 'LineWidth', 1.6);
patch([8.0-aw 8.0 8.0+aw], [y_a2_bot+ah y_a2_bot y_a2_bot+ah], line_col, 'EdgeColor','none');

%% ================================================================
%%  ROW 3 — ENVIRONMENT CONFIG  (y = 8.0)
%% ================================================================
y3 = 8.0;  bw3 = 6.8;  bh3 = 0.75;

rectangle('Position', [8.0-bw3/2, y3-bh3/2, bw3, bh3], 'Curvature', 0.15, ...
    'FaceColor', c_orange, 'EdgeColor', c_orange_e, 'LineWidth', 2);
text(8.0, y3+0.12, 'Phase 2: Environment Configuration', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white);
text(8.0, y3-0.14, 'Threat Profiles | Attack Rates | Zone Values | Matrix E', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',[1 0.97 0.9]);

% Arrow down
y_a3_bot = 6.25 + 0.50;
plot([8.0 8.0], [y3-bh3/2 y_a3_bot], '-', 'Color', line_col, 'LineWidth', 1.6);
patch([8.0-aw 8.0 8.0+aw], [y_a3_bot+ah y_a3_bot y_a3_bot+ah], line_col, 'EdgeColor','none');

%% ================================================================
%%  ROW 4 — SIMULATION ENVIRONMENT  (y = 6.25)
%% ================================================================
y4 = 6.25;  bw4 = 6.8;  bh4 = 0.95;

rectangle('Position', [8.0-bw4/2, y4-bh4/2, bw4, bh4], 'Curvature', 0.15, ...
    'FaceColor', c_green, 'EdgeColor', c_green_e, 'LineWidth', 2.5);
text(8.0, y4+0.25, 'IIoT Simulation Environment', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',12,'FontWeight','bold','Color',c_white);
text(8.0, y4, 'M = (S, A_d, A_a, P, R_d, R_a, \gamma, C)', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',10, ...
    'FontWeight','bold','Color',[0.9 1 0.9],'Interpreter','tex');
text(8.0, y4-0.25, '|S| = 12 continuous     T = 100 steps/episode', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9, ...
    'FontWeight','bold','Color',[0.9 1 0.9]);

%% ================================================================
%%  DEFENDER (left)
%% ================================================================
xd = 2.3;  bwd = 3.0;  bhd = 1.55;

rectangle('Position', [xd-bwd/2, y4-bhd/2, bwd, bhd], 'Curvature', 0.15, ...
    'FaceColor', c_blue, 'EdgeColor', c_blue_e, 'LineWidth', 2.5);
text(xd, y4+0.45, 'DQN Defender  \pi_d', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white,'Interpreter','tex');
text(xd, y4+0.15, '12 \rightarrow 128 \rightarrow 64 \rightarrow 4', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',[0.9 0.95 1],'Interpreter','tex');
text(xd, y4-0.12, '|\theta| = 10,180', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',[0.9 0.95 1],'Interpreter','tex');
text(xd, y4-0.40, 'Adam    \gamma = 0.85', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',[0.9 0.95 1],'Interpreter','tex');

%% ---- Defender <-> Environment arrows ----
x_def_right = xd + bwd/2;
x_env_left  = 8.0 - bw4/2;
x_mid = (x_def_right + x_env_left) / 2;

% Top arrow: env -> defender (reward, state)
ya_top = y4 + 0.20;
plot([x_env_left x_def_right], [ya_top ya_top], '-', 'Color', c_blue, 'LineWidth', 2);
patch([x_def_right+0.12 x_def_right x_def_right+0.12], [ya_top+0.09 ya_top ya_top-0.09], c_blue, 'EdgeColor','none');
text(x_mid, ya_top+0.18, 'r_d ,  s_{t+1}', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',c_blue_e,'Interpreter','tex');

% Bottom arrow: defender -> env (action)
ya_bot = y4 - 0.20;
plot([x_def_right x_env_left], [ya_bot ya_bot], '-', 'Color', c_blue, 'LineWidth', 2);
patch([x_env_left-0.12 x_env_left x_env_left-0.12], [ya_bot+0.09 ya_bot ya_bot-0.09], c_blue, 'EdgeColor','none');
text(x_mid, ya_bot-0.18, 'a_t  \in  A_d', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',c_blue_e,'Interpreter','tex');

%% ================================================================
%%  ATTACKER (right)
%% ================================================================
xa = 13.7;  bwa = 3.0;  bha = 1.55;

rectangle('Position', [xa-bwa/2, y4-bha/2, bwa, bha], 'Curvature', 0.15, ...
    'FaceColor', c_red, 'EdgeColor', c_red_e, 'LineWidth', 2.5);
text(xa, y4+0.45, 'Tabular Attacker  \pi_a', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white,'Interpreter','tex');
text(xa, y4+0.15, 'Q_a \in R^{34560 x 45}', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',[1 0.9 0.9],'Interpreter','tex');
text(xa, y4-0.12, '|A_a| = 45 actions', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',[1 0.9 0.9]);
text(xa, y4-0.40, '\eta = 0.01    \gamma = 0.90', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',[1 0.9 0.9],'Interpreter','tex');

%% ---- Attacker <-> Environment arrows ----
x_env_right = 8.0 + bw4/2;
x_atk_left  = xa - bwa/2;
x_mid_r = (x_env_right + x_atk_left) / 2;

% Top arrow: env -> attacker
plot([x_env_right x_atk_left], [ya_top ya_top], '-', 'Color', c_red, 'LineWidth', 2);
patch([x_atk_left-0.12 x_atk_left x_atk_left-0.12], [ya_top+0.09 ya_top ya_top-0.09], c_red, 'EdgeColor','none');
text(x_mid_r, ya_top+0.18, 'r_a ,  s_{t+1}', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',c_red_e,'Interpreter','tex');

% Bottom arrow: attacker -> env
plot([x_atk_left x_env_right], [ya_bot ya_bot], '-', 'Color', c_red, 'LineWidth', 2);
patch([x_env_right+0.12 x_env_right x_env_right+0.12], [ya_bot+0.09 ya_bot ya_bot-0.09], c_red, 'EdgeColor','none');
text(x_mid_r, ya_bot-0.18, 'b_t  \in  A_a', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',10,'FontWeight','bold','Color',c_red_e,'Interpreter','tex');

%% ================================================================
%%  ATTACKER POOL (above attacker, right side)
%% ================================================================
yp = 8.0;  bwp = 3.0;  bhp = 0.75;

rectangle('Position', [xa-bwp/2, yp-bhp/2, bwp, bhp], 'Curvature', 0.15, ...
    'FaceColor', c_red, 'EdgeColor', c_red_e, 'LineWidth', 2);
text(xa, yp+0.12, 'Attacker Pool  \Pi_a', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white,'Interpreter','tex');
text(xa, yp-0.14, 'K=10 snapshots    p_{pool}=0.30', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',[1 0.9 0.9],'Interpreter','tex');

% Attacker -> Pool (solid upward)
plot([xa xa], [y4+bha/2 yp-bhp/2], '-', 'Color', c_red, 'LineWidth', 1.8);
patch([xa-aw xa xa+aw], [yp-bhp/2+ah yp-bhp/2 yp-bhp/2+ah], c_red, 'EdgeColor','none');
text(xa+0.45, (y4+bha/2 + yp-bhp/2)/2, 'every 500 ep.', ...
    'HorizontalAlignment','left','FontName','Times New Roman','FontSize',8.5, ...
    'FontWeight','bold','Color',c_red,'Rotation',90);

% Pool -> Environment (dashed diagonal)
plot([xa-bwp/2  x_env_right], [yp-bhp/2  y4+bh4/2], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.5);
text((xa-bwp/2 + x_env_right)/2 + 0.3, (yp-bhp/2 + y4+bh4/2)/2 + 0.2, 'sample', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9, ...
    'FontWeight','bold','Color',[0.5 0.5 0.5]);

%% ================================================================
%%  SKEPTICISM EQUATION  (below environment)
%% ================================================================
y_sk = y4 - bh4/2 - 0.40;

% Use plain text to avoid rendering issues
text(8.0, y_sk, ...
    'Skepticism:   \sigma_{t+1} = min(\sigma_{max},  \sigma_t + \Delta(\omega_t))   if  \omega_t > \theta_{dec}  ;   else   \lambda_{decay} \cdot \sigma_t', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9.5, ...
    'FontWeight','bold','Color',c_green_e,'Interpreter','tex');

%% ---- Arrows to Evaluation ----
y_eval = 3.65;
plot([8.0 8.0], [y_sk-0.25 y_eval+bh2/2], '-', 'Color', line_col, 'LineWidth', 1.6);
patch([8.0-aw 8.0 8.0+aw], [y_eval+bh2/2+ah y_eval+bh2/2 y_eval+bh2/2+ah], line_col, 'EdgeColor','none');

% Defender diagonal to evaluation
plot([xd  8.0-bw2/2+0.5], [y4-bhd/2  y_eval+bh2/2], '-', 'Color', line_col*0.85, 'LineWidth', 1.3);

%% ================================================================
%%  ROW 5 — EVALUATION  (y = 3.65)
%% ================================================================
y5 = y_eval;  bw5 = 6.8;  bh5 = 0.75;

rectangle('Position', [8.0-bw5/2, y5-bh5/2, bw5, bh5], 'Curvature', 0.15, ...
    'FaceColor', c_purple, 'EdgeColor', c_purple_e, 'LineWidth', 2);
text(8.0, y5+0.12, 'Evaluation:  Phases 5  \rightarrow  9', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',11,'FontWeight','bold','Color',c_white,'Interpreter','tex');
text(8.0, y5-0.14, 'Baseline | Transfer | Ablation | Scalability | Game-Theoretic', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',[0.92 0.88 1]);

% Arrow down to metrics
y6 = 2.5;
plot([8.0 8.0], [y5-bh5/2 y6+0.35], '-', 'Color', line_col, 'LineWidth', 1.6);
patch([8.0-aw 8.0 8.0+aw], [y6+0.35+ah y6+0.35 y6+0.35+ah], line_col, 'EdgeColor','none');

%% ================================================================
%%  ROW 6 — OUTPUT METRICS  (y = 2.5)
%% ================================================================
bw6 = 10.5;  bh6 = 0.65;

rectangle('Position', [8.0-bw6/2, y6-bh6/2, bw6, bh6], 'Curvature', 0.12, ...
    'FaceColor', c_gray, 'EdgeColor', c_gray_e, 'LineWidth', 2);
text(8.0, y6, ...
    'Output:   AMR  |  DSR  |  FAR  |  MTTD  |  CVaR_{0.05}  |  Transfer Score  |  Robustness', ...
    'HorizontalAlignment','center','FontName','Times New Roman','FontSize',10, ...
    'FontWeight','bold','Color',c_white,'Interpreter','tex');

%% ================================================================
%%  ANNOTATIONS (below defender and attacker)
%% ================================================================

% --- Action Masking + Intel Boost (below defender) ---
y_ann_d = y4 - bhd/2 - 0.35;

% Background box for annotations
ann_bw = 2.8; ann_bh = 1.1;
rectangle('Position', [xd-ann_bw/2, y_ann_d-ann_bh+0.15, ann_bw, ann_bh], ...
    'Curvature', 0.1, 'FaceColor', [0.95 0.97 1], 'EdgeColor', c_blue*0.8, ...
    'LineWidth', 1, 'LineStyle', ':');

text(xd, y_ann_d, 'Action Masking:', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',c_blue_e);
text(xd, y_ann_d-0.28, 'Suppress P_2 if \rho_t > 0.60', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',c_blue_e,'Interpreter','tex');
text(xd, y_ann_d-0.54, 'and \sigma_t > 0.80  (<2\% of steps)', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',c_blue_e,'Interpreter','tex');

% --- Co-evolution (below attacker) ---
y_ann_a = y4 - bha/2 - 0.35;

rectangle('Position', [xa-ann_bw/2, y_ann_a-ann_bh+0.35, ann_bw, ann_bh-0.2], ...
    'Curvature', 0.1, 'FaceColor', [1 0.96 0.96], 'EdgeColor', c_red*0.8, ...
    'LineWidth', 1, 'LineStyle', ':');

text(xa, y_ann_a, 'Co-evolutionary Loop:', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',c_red_e);
text(xa, y_ann_a-0.25, '5000 episodes', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',c_red_e);
text(xa, y_ann_a-0.50, 'Simultaneous Updates', 'HorizontalAlignment','center', ...
    'FontName','Times New Roman','FontSize',9,'FontWeight','bold','Color',c_red_e);

%% ================================================================
%%  SAVE
%% ================================================================
exportgraphics(fig, fullfile(fig_dir, 'fig_architecture.pdf'), 'ContentType', 'vector');
exportgraphics(fig, fullfile(fig_dir, 'fig_architecture.png'), 'Resolution', 300);
fprintf('Figure saved to: %s\n', fig_dir);
fprintf('=== Done ===\n');
