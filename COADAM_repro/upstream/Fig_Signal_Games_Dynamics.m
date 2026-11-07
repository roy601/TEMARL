%% CoADAM Signaling Game Dynamics Figure
clear; clc; close all;

%% Confirmed CoADAM Parameters
sigma_max    = 0.80;
lambda_decay = 0.92;
delta_s      = 0.05;
theta_dec    = 0.15;
sigma_eq     = 0.4333;
kappa_m      = 0.30;

omega         = [0.25, 0.70, 0.10, 0.10];
profile_names = {'P_1 (Balanced)','P_2 (DeceptionHeavy)',...
                 'P_3 (Perimeter)','P_4 (AccessLockdown)'};

p_base       = [0.35, 0.30, 0.25, 0.20, 0.40];
tactic_names = {'Reconnaissance','Initial Access','Execution',...
                'Lateral Movement','Impact'};

%% Font settings
fn  = 'Times New Roman';
fsz = 14;
fw  = 'bold';

%% Colors
c_p1  = [0.40 0.65 0.85];
c_p2  = [0.85 0.33 0.10];
c_p3  = [0.47 0.67 0.19];
c_p4  = [0.49 0.18 0.56];
c_eq  = [0.85 0.10 0.10];
c_thr = [0.50 0.50 0.50];
c_max = [0.20 0.20 0.20];

tactic_colors = [
    0.00 0.45 0.74;
    0.85 0.33 0.10;
    0.93 0.69 0.13;
    0.49 0.18 0.56;
    0.47 0.67 0.19];

profile_colors = {c_p1, c_p2, c_p3, c_p4};
profile_lines  = {'-','-','--',':'};
profile_widths = [1.8, 2.4, 1.8, 1.8];
profile_start  = [0.10, 0.10, 0.50, 0.60];

%% Create figure
fig = figure('Position',[80 80 1200 520],...
             'Color','w',...
             'PaperPositionMode','auto',...
             'PaperUnits','inches',...
             'PaperSize',[12 5.2],...
             'Renderer','painters');

%% =========================================================
%% PANEL A: Skepticism Dynamics
%% =========================================================
ax1 = subplot(1,2,1);
hold on;

T     = 120;
steps = 1:T;

for p = 1:4
    sigma    = zeros(1,T);
    sigma(1) = profile_start(p);
    for t = 1:T-1
        if omega(p) > theta_dec
            inc        = delta_s*(omega(p)-theta_dec)/(1-theta_dec);
            sigma(t+1) = min(sigma_max, sigma(t)+inc);
        else
            sigma(t+1) = lambda_decay*sigma(t);
        end
    end
    plot(steps, sigma,...
         profile_lines{p},...
         'Color',     profile_colors{p},...
         'LineWidth', profile_widths(p),...
         'DisplayName', profile_names{p});
end

hl_eq       = yline(sigma_eq,'--','Color',c_eq,'LineWidth',2.0,'HandleVisibility','off');
hl_eq.Label                     = sprintf('\\sigma^*_{emp} = %.4f',sigma_eq);
hl_eq.LabelHorizontalAlignment  = 'left';
hl_eq.FontName                  = fn;
hl_eq.FontSize                  = fsz-2;
hl_eq.FontWeight                = fw;

hl_max      = yline(sigma_max,':','Color',c_max,'LineWidth',1.6,'HandleVisibility','off');
hl_max.Label                    = sprintf('\\sigma_{max} = %.2f',sigma_max);
hl_max.LabelHorizontalAlignment = 'left';
hl_max.FontName                 = fn;
hl_max.FontSize                 = fsz-2;
hl_max.FontWeight               = fw;

hl_thr      = yline(theta_dec,'-.','Color',c_thr,'LineWidth',1.6,'HandleVisibility','off');
hl_thr.Label                    = sprintf('\\theta_{dec} = %.2f',theta_dec);
hl_thr.LabelHorizontalAlignment = 'left';
hl_thr.FontName                 = fn;
hl_thr.FontSize                 = fsz-2;
hl_thr.FontWeight               = fw;

str = {sprintf('\\sigma_{max}    = %.2f', sigma_max),...
       sprintf('\\lambda_{decay} = %.2f', lambda_decay),...
       sprintf('\\delta_s        = %.2f', delta_s),...
       sprintf('\\theta_{dec}    = %.2f', theta_dec)};
text(2, 0.78, str,...
     'FontName',fn,'FontSize',fsz-3,'FontWeight',fw,...
     'BackgroundColor','w','EdgeColor',[0.7 0.7 0.7],...
     'VerticalAlignment','top','Margin',4);

text(85, 0.47,'P_1 crosses \sigma^*_{emp}',...
     'FontName',fn,'FontSize',fsz-3,'FontWeight','normal',...
     'Color',c_p1,'HorizontalAlignment','center');

text(62, 0.06,'P_3, P_4: \omega < \theta_{dec} \Rightarrow decay',...
     'FontName',fn,'FontSize',fsz-3,'FontWeight','normal',...
     'Color',c_p3,'HorizontalAlignment','center');

xlabel('Episode Step $t$','Interpreter','latex',...
       'FontName',fn,'FontSize',fsz,'FontWeight',fw);
ylabel('Skepticism $\sigma_t$','Interpreter','latex',...
       'FontName',fn,'FontSize',fsz,'FontWeight',fw);
title('(A) Skepticism Dynamics per Defense Profile',...
      'FontName',fn,'FontSize',fsz,'FontWeight',fw);
legend('Location','east','FontName',fn,'FontSize',fsz-2,'FontWeight',fw,'Box','on');

ylim([0 sigma_max+0.08]);
xlim([1 T]);
grid on; box on;

set(ax1,'FontName',fn,'FontSize',fsz,'FontWeight',fw,'LineWidth',1.0,'TickDir','out');

%% =========================================================
%% PANEL B: Attack Success Modulation
%% =========================================================
ax2 = subplot(1,2,2);
hold on;

%% --- Step 1: Draw shading patches FIRST ---
patch([-0.01 0.33 0.33 -0.01],[-0.02 -0.02 1.04 1.04],[0.78 0.95 0.78],...
      'FaceAlpha',0.30,'EdgeColor','none','HandleVisibility','off');
patch([0.33 0.67 0.67 0.33],[-0.02 -0.02 1.04 1.04],[0.99 0.99 0.70],...
      'FaceAlpha',0.30,'EdgeColor','none','HandleVisibility','off');
patch([0.67 0.97 0.97 0.67],[-0.02 -0.02 1.04 1.04],[0.99 0.78 0.78],...
      'FaceAlpha',0.30,'EdgeColor','none','HandleVisibility','off');

%% --- Step 2: Draw boundary lines using plot instead of xline ---
plot([0.33 0.33],[0 1.02],'k-','LineWidth',0.8,'HandleVisibility','off');
plot([0.67 0.67],[0 1.02],'k-','LineWidth',0.8,'HandleVisibility','off');

%% --- Step 3: Draw data lines on top ---
eta_range = linspace(0,0.95,300);
m_vals    = [0.0, 0.5, 1.0];
m_styles  = {'-','--',':'};
m_lw      = [2.2, 1.8, 1.8];

impact_idx = 5;
for mi = 1:3
    m     = m_vals(mi);
    p_net = min(p_base(impact_idx).*(1+kappa_m*m).*(1-eta_range), 0.95);
    plot(eta_range, p_net,...
         m_styles{mi},...
         'Color',    tactic_colors(impact_idx,:),...
         'LineWidth',m_lw(mi),...
         'DisplayName',sprintf('Impact (m_t=%.1f, base 40%%)',m));
end

for k = 1:5
    if k == impact_idx; continue; end
    p_net = min(p_base(k).*(1-eta_range), 0.95);
    plot(eta_range, p_net,'-',...
         'Color',    tactic_colors(k,:),...
         'LineWidth',1.8,...
         'DisplayName',sprintf('%s (base %.0f%%)',tactic_names{k},p_base(k)*100));
end

m_eq  = 0.1068;
eta_v = 0.50;
p_v   = min(p_base(impact_idx).*(1+kappa_m*m_eq).*(1-eta_v), 0.95);
plot(eta_v, p_v,'kp','MarkerSize',12,'MarkerFaceColor','k','HandleVisibility','off');
text(eta_v+0.01, p_v+0.03,sprintf('m_{eq}=%.4f',m_eq),...
     'FontName',fn,'FontSize',fsz-3,'FontWeight',fw);

plot(nan, nan,'kp','MarkerSize',10,'MarkerFaceColor','k',...
     'DisplayName',sprintf('m_{eq} = %.4f',m_eq));

%% --- Step 4: Region labels LAST so they sit on top ---
text(0.02, 0.97,'Low Defense',...
     'FontName',fn,'FontSize',fsz-2,'FontWeight',fw,...
     'Color',[0.10 0.40 0.10],'VerticalAlignment','top',...
     'BackgroundColor','none');
text(0.34, 0.97,'Moderate',...
     'FontName',fn,'FontSize',fsz-2,'FontWeight',fw,...
     'Color',[0.50 0.40 0.00],'VerticalAlignment','top',...
     'BackgroundColor','none');
text(0.68, 0.97,'High Defense',...
     'FontName',fn,'FontSize',fsz-2,'FontWeight',fw,...
     'Color',[0.50 0.05 0.05],'VerticalAlignment','top',...
     'BackgroundColor','none');

xlabel('Defense Effectiveness $\eta_t$','Interpreter','latex',...
       'FontName',fn,'FontSize',fsz,'FontWeight',fw);
ylabel('Net Attack Success $p_t^{net}$','Interpreter','latex',...
       'FontName',fn,'FontSize',fsz,'FontWeight',fw);
title('(B) Attack Success Modulation by Defense and Momentum',...
      'FontName',fn,'FontSize',fsz,'FontWeight',fw);

legend('Location','northeast','FontName',fn,'FontSize',fsz-3,'FontWeight',fw,'Box','on');

ylim([0 1.02]);
xlim([0 0.95]);
grid on; box on;

set(ax2,'FontName',fn,'FontSize',fsz,'FontWeight',fw,'LineWidth',1.0,'TickDir','out');

%% Main title
sgtitle('CoADAM Signaling Game: Skepticism and Attack Success Dynamics',...
        'FontName',fn,'FontSize',fsz+1,'FontWeight',fw);

%% =========================================================
%% Export
%% =========================================================
savefig(fig,'SG.fig');
exportgraphics(fig,'SG.pdf','ContentType','vector');
exportgraphics(fig,'SG.png','ContentType','image','Resolution',300);
fprintf('Saved: SG.fig  SG.pdf  SG.png\n');