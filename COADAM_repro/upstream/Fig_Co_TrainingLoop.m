clear; clc;
fprintf('=== CoADAM Figure: Co-Evolutionary Training Loop ===\n');

project_root = '/Users/ujw/Desktop/CoADAM';
fig_dir      = fullfile(project_root, 'figures');
if ~exist(fig_dir, 'dir'), mkdir(fig_dir); end

%% ---- Load verified values ----
trained = load(fullfile(project_root, 'results', 'dqn_cotraining_results.mat'));
config  = load(fullfile(project_root, 'data', 'processed', 'environment_config.mat'));

n_episodes    = double(trained.n_episodes);
conv_ep       = double(trained.convergence_episode);
pool_size     = numel(trained.attacker_pool);
T             = 100;
p_pool        = 0.30;
snap_interval = 500;
tgt_interval  = 100;

fprintf('Verified: N=%d, conv=%d, K=%d, T=%d\n', ...
    n_episodes, conv_ep, pool_size, T);

fig = figure('Position', [30 20 1100 1500], 'Color', 'w');
ax  = axes('Position', [0.04 0.02 0.92 0.96], 'Visible', 'off');
hold on;
xlim([0 12]); ylim([0 15.5]);
axis off;

%% ---- Colors ----
c_blue   = [0.20 0.56 0.84];
c_red    = [0.88 0.30 0.25];
c_green  = [0.25 0.65 0.32];
c_purple = [0.58 0.30 0.65];
c_orange = [0.93 0.62 0.20];
c_gray   = [0.55 0.55 0.55];

c_blue_e   = c_blue   * 0.75;
c_red_e    = c_red    * 0.75;
c_green_e  = c_green  * 0.70;
c_purple_e = c_purple * 0.70;
c_orange_e = c_orange * 0.75;
c_gray_e   = c_gray   * 0.70;

aw = 0.10; ah = 0.13;

%% ---- Consistent spacing ----
% All blocks use uniform vertical gap of 0.55 between bottom of one and top of next
bx   = 5.5;        % center x for main flow
bw   = 5.5;        % main box width
gap  = 0.40;       % uniform gap between blocks
bh_s = 0.55;       % small box height (single line)
bh_m = 0.75;       % medium box height (two lines)

%% ================================================================
%%  TITLE
%% ================================================================
text(ax, bx, 15.6, 'CoADAM: Co-Evolutionary Training Loop', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',17,'FontWeight','bold','Color','k');

%% ================================================================
%%  BLOCK 1 — START EPISODE
%% ================================================================
y1 = 14.9;

rectangle('Parent',ax,'Position',[bx-bw/2, y1-bh_s/2, bw, bh_s], ...
    'Curvature',0.15,'FaceColor',c_blue,'EdgeColor',c_blue_e,'LineWidth',2.2);
text(ax, bx, y1, sprintf('Start Episode  e = 1, 2, ..., %d', n_episodes), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',11,'FontWeight','bold','Color',[1 1 1]);

y1_bot = y1 - bh_s/2;

%% ================================================================
%%  BLOCK 2 — SAMPLE ATTACKER
%% ================================================================
y2 = y1_bot - gap - bh_m/2;

% Arrow from block 1 to block 2
plot([bx bx],[y1_bot y2+bh_m/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y2+bh_m/2+ah y2+bh_m/2 y2+bh_m/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y2-bh_m/2, bw, bh_m], ...
    'Curvature',0.15,'FaceColor',c_red,'EdgeColor',c_red_e,'LineWidth',2.2);
text(ax, bx, y2+0.13, 'Sample Attacker  \pi_a', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',11,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, bx, y2-0.15, sprintf('Pool (p=%.2f) or Current (p=%.2f)', p_pool, 1-p_pool), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 0.92 0.92]);

y2_bot = y2 - bh_m/2;

%% ================================================================
%%  BLOCK 3 — RESET ENVIRONMENT
%% ================================================================
y3 = y2_bot - gap - bh_s/2;

plot([bx bx],[y2_bot y3+bh_s/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y3+bh_s/2+ah y3+bh_s/2 y3+bh_s/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y3-bh_s/2, bw, bh_s], ...
    'Curvature',0.15,'FaceColor',c_green,'EdgeColor',c_green_e,'LineWidth',2.2);
text(ax, bx, y3, 'Reset Environment;  Observe  s_1 \in R^{12}', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',11,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');

y3_bot = y3 - bh_s/2;

%% ================================================================
%%  BLOCK 4 — INNER LOOP HEADER
%% ================================================================
y4 = y3_bot - gap - bh_s/2;

plot([bx bx],[y3_bot y4+bh_s/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y4+bh_s/2+ah y4+bh_s/2 y4+bh_s/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y4-bh_s/2, bw, bh_s], ...
    'Curvature',0.15,'FaceColor',c_gray,'EdgeColor',c_gray_e,'LineWidth',2.2);
text(ax, bx, y4, sprintf('For  t = 1, 2, ..., %d  (inner loop)', T), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1]);

y4_bot = y4 - bh_s/2;

%% ================================================================
%%  BLOCK 5 — ACTIONS
%% ================================================================
y5 = y4_bot - gap - bh_m/2;

plot([bx bx],[y4_bot y5+bh_m/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y5+bh_m/2+ah y5+bh_m/2 y5+bh_m/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y5-bh_m/2, bw, bh_m], ...
    'Curvature',0.15,'FaceColor',c_blue,'EdgeColor',c_blue_e,'LineWidth',2.2);
text(ax, bx, y5+0.13, 'Defender: select  a_t  via  \epsilon-greedy + masking', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, bx, y5-0.13, 'Attacker: select  b_t  via  \epsilon-greedy on  Q_a', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[0.9 0.95 1],'Interpreter','tex');

y5_bot = y5 - bh_m/2;

%% ================================================================
%%  BLOCK 6 — ENVIRONMENT STEP
%% ================================================================
y6 = y5_bot - gap - bh_m/2;

plot([bx bx],[y5_bot y6+bh_m/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y6+bh_m/2+ah y6+bh_m/2 y6+bh_m/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y6-bh_m/2, bw, bh_m], ...
    'Curvature',0.15,'FaceColor',c_green,'EdgeColor',c_green_e,'LineWidth',2.2);
text(ax, bx, y6+0.13, 'Compute  p_t^{net}  (Eq. 5),   \eta_t  (Eq. 6)', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, bx, y6-0.13, 'Update  \sigma_{t+1}  (Eq. 8);   Observe  s_{t+1}', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[0.9 1 0.9],'Interpreter','tex');

y6_bot = y6 - bh_m/2;

%% ================================================================
%%  BLOCK 7 — REWARDS
%% ================================================================
y7 = y6_bot - gap - bh_m/2;

plot([bx bx],[y6_bot y7+bh_m/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y7+bh_m/2+ah y7+bh_m/2 y7+bh_m/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y7-bh_m/2, bw, bh_m], ...
    'Curvature',0.15,'FaceColor',c_orange,'EdgeColor',c_orange_e,'LineWidth',2.2);
text(ax, bx, y7+0.13, 'Compute  r_d  (Eq. 11),   r_a  (Eq. 12)', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, bx, y7-0.13, 'Store  (s_t, a_t, b_t, r_d, s_{t+1})  in replay buffer  D', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 0.97 0.9],'Interpreter','tex');

y7_bot = y7 - bh_m/2;

%% ================================================================
%%  BLOCK 8 — END INNER LOOP
%% ================================================================
y8 = y7_bot - gap - bh_s/2;

plot([bx bx],[y7_bot y8+bh_s/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y8+bh_s/2+ah y8+bh_s/2 y8+bh_s/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y8-bh_s/2, bw, bh_s], ...
    'Curvature',0.15,'FaceColor',c_gray,'EdgeColor',c_gray_e,'LineWidth',2.2);
text(ax, bx, y8, 'End inner loop  (t = T)', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1]);

y8_bot = y8 - bh_s/2;

%% ================================================================
%%  BLOCK 9 — POLICY UPDATES
%% ================================================================
y9 = y8_bot - gap - bh_m/2;

plot([bx bx],[y8_bot y9+bh_m/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y9+bh_m/2+ah y9+bh_m/2 y9+bh_m/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y9-bh_m/2, bw, bh_m], ...
    'Curvature',0.15,'FaceColor',c_blue,'EdgeColor',c_blue_e,'LineWidth',2.2);
text(ax, bx, y9+0.13, 'Update DQN  \theta  via Adam (mini-batch from D)', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, bx, y9-0.13, 'Update  Q_a  via Q-learning  (\eta_a=0.01,  \gamma_a=0.90)', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[0.9 0.95 1],'Interpreter','tex');

y9_bot = y9 - bh_m/2;

%% ================================================================
%%  BLOCK 10 — SNAPSHOT CONDITION
%% ================================================================
bw10 = 5.0;
y10 = y9_bot - gap - bh_s/2;

plot([bx bx],[y9_bot y10+bh_s/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y10+bh_s/2+ah y10+bh_s/2 y10+bh_s/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw10/2, y10-bh_s/2, bw10, bh_s], ...
    'Curvature',0.15,'FaceColor',c_purple,'EdgeColor',c_purple_e,'LineWidth',2.2);
text(ax, bx, y10, sprintf('e  mod  %d  =  0 ?  (Pool Snapshot)', snap_interval), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1]);

% Yes -> right to pool box
x_side_start = bx + bw10/2;
x_side_box   = 10.5;
side_bw      = 2.2;
side_bh      = 0.65;

plot([x_side_start x_side_box-side_bw/2-ah],[y10 y10],'-','Color',c_purple,'LineWidth',2);
patch([x_side_box-side_bw/2-ah x_side_box-side_bw/2 x_side_box-side_bw/2-ah], ...
    [y10+aw y10 y10-aw],c_purple,'EdgeColor','none');
text(ax, (x_side_start+x_side_box-side_bw/2)/2, y10+0.25, 'Yes', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_purple);

rectangle('Parent',ax,'Position',[x_side_box-side_bw/2, y10-side_bh/2, side_bw, side_bh], ...
    'Curvature',0.15,'FaceColor',c_red,'EdgeColor',c_red_e,'LineWidth',2);
text(ax, x_side_box, y10+0.10, 'Append  Q_a', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, x_side_box, y10-0.13, sprintf('to Pool (K=%d)', pool_size), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',9,'FontWeight','bold','Color',[1 0.9 0.9]);

% No -> down
y10_bot = y10 - bh_s/2;
text(ax, bx-0.50, y10_bot-gap/2+0.05, 'No', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_gray);

%% ================================================================
%%  BLOCK 11 — TARGET UPDATE CONDITION
%% ================================================================
y11 = y10_bot - gap - bh_s/2;

plot([bx bx],[y10_bot y11+bh_s/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y11+bh_s/2+ah y11+bh_s/2 y11+bh_s/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw10/2, y11-bh_s/2, bw10, bh_s], ...
    'Curvature',0.15,'FaceColor',c_purple,'EdgeColor',c_purple_e,'LineWidth',2.2);
text(ax, bx, y11, sprintf('t  mod  %d  =  0 ?  (Target Update)', tgt_interval), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1]);

% Yes -> right to target box
plot([x_side_start x_side_box-side_bw/2-ah],[y11 y11],'-','Color',c_purple,'LineWidth',2);
patch([x_side_box-side_bw/2-ah x_side_box-side_bw/2 x_side_box-side_bw/2-ah], ...
    [y11+aw y11 y11-aw],c_purple,'EdgeColor','none');
text(ax, (x_side_start+x_side_box-side_bw/2)/2, y11+0.25, 'Yes', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_purple);

rectangle('Parent',ax,'Position',[x_side_box-side_bw/2, y11-side_bh/2, side_bw, side_bh], ...
    'Curvature',0.15,'FaceColor',c_blue,'EdgeColor',c_blue_e,'LineWidth',2);
text(ax, x_side_box, y11, '\theta^{-} \leftarrow \theta', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',12,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');

% No -> down
y11_bot = y11 - bh_s/2;
text(ax, bx-0.50, y11_bot-gap/2+0.05, 'No', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_gray);

%% ================================================================
%%  BLOCK 12 — CONTINUE?
%% ================================================================
y12 = y11_bot - gap - bh_s/2;

plot([bx bx],[y11_bot y12+bh_s/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y12+bh_s/2+ah y12+bh_s/2 y12+bh_s/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw10/2, y12-bh_s/2, bw10, bh_s], ...
    'Curvature',0.15,'FaceColor',c_orange,'EdgeColor',c_orange_e,'LineWidth',2.2);
text(ax, bx, y12, sprintf('e  <  %d ?  (Continue Training)', n_episodes), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[1 1 1]);

% Yes -> loop back left
x_loop = 1.5;
y12_bot = y12 - bh_s/2;

plot([bx-bw10/2 x_loop x_loop bx-bw/2], ...
     [y12        y12    y1     y1], ...
     '-','Color',c_green,'LineWidth',2.2);
patch([bx-bw/2+ah bx-bw/2 bx-bw/2+ah],[y1+aw y1 y1-aw],c_green,'EdgeColor','none');
text(ax, x_loop-0.50, (y12+y1)/2, 'e \leftarrow e + 1', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_green,'Rotation',90,'Interpreter','tex');

% No -> down
text(ax, bx-0.50, y12_bot-gap/2+0.05, 'No', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_gray);

%% ================================================================
%%  BLOCK 13 — OUTPUT
%% ================================================================
y13 = y12_bot - gap - bh_m/2;

plot([bx bx],[y12_bot y13+bh_m/2+ah],'-','Color',c_gray,'LineWidth',2);
patch([bx-aw bx bx+aw],[y13+bh_m/2+ah y13+bh_m/2 y13+bh_m/2+ah],c_gray,'EdgeColor','none');

rectangle('Parent',ax,'Position',[bx-bw/2, y13-bh_m/2, bw, bh_m], ...
    'Curvature',0.15,'FaceColor',c_green,'EdgeColor',c_green_e,'LineWidth',2.2);
text(ax, bx, y13+0.12, 'Return  \pi_d^*  \leftarrow  \theta', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',11,'FontWeight','bold','Color',[1 1 1],'Interpreter','tex');
text(ax, bx, y13-0.14, sprintf('Return  Pool  (K=%d snapshots)', pool_size), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',[0.9 1 0.9]);

%% ================================================================
%%  CONVERGENCE ANNOTATION
%% ================================================================
cx_conv = 9.8;  cy_conv = y13 - bh_m/2 - 0.55;
cw_conv = 2.8;  ch_conv = 0.65;

rectangle('Parent',ax, ...
    'Position',[cx_conv-cw_conv/2, cy_conv-ch_conv/2, cw_conv, ch_conv], ...
    'Curvature',0.12,'FaceColor',[0.95 1.00 0.95], ...
    'EdgeColor',c_green_e,'LineWidth',1.5,'LineStyle','--');
text(ax, cx_conv, cy_conv+0.12, 'Convergence:', ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_green_e);
text(ax, cx_conv, cy_conv-0.12, sprintf('Episode %d', conv_ep), ...
    'HorizontalAlignment','center','FontName','Times New Roman', ...
    'FontSize',10,'FontWeight','bold','Color',c_green_e);

%% ================================================================
%%  SAVE
%% ================================================================
exportgraphics(fig, fullfile(fig_dir, 'fig_training_loop.pdf'), ...
    'ContentType','vector');
exportgraphics(fig, fullfile(fig_dir, 'fig_training_loop.png'), ...
    'Resolution',300);
fprintf('Figure saved: fig_training_loop.pdf and fig_training_loop.png\n');
fprintf('=== Done ===\n');
