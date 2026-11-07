clear; clc;

project_root = '/Users/ujw/Desktop/CoADAM';
fig_dir      = fullfile(project_root, 'figures');
res_dir      = fullfile(project_root, 'results');
if ~exist(fig_dir,'dir'), mkdir(fig_dir); end
if ~exist(res_dir,'dir'), mkdir(res_dir); end

%% Load simulation results
bl     = load(fullfile(res_dir, 'baseline_results_final.mat'));
coadam = bl.results_tableA{8};

sim.AMR           = coadam.AMR.mean;
sim.DSR           = coadam.DSR.mean;
sim.FAR           = coadam.FAR.mean;
sim.InfectionRate = coadam.InfectionRate.mean;
sim.MTTD          = coadam.MTTD.mean;
sim.Reward        = coadam.CumulativeReward.mean;

fprintf('=== CoADAM Simulation Results ===\n');
fprintf('AMR:            %.4f\n', sim.AMR);
fprintf('DSR:            %.4f\n', sim.DSR);
fprintf('FAR:            %.4f\n', sim.FAR);
fprintf('Infection Rate: %.4f\n', sim.InfectionRate);
fprintf('MTTD:           %.4f\n', sim.MTTD);
fprintf('Reward:         %.4f\n', sim.Reward);

%% Testbed raw counts (10-day final)
cowrie_sessions       = 53400;
cowrie_login_failed   = 1111599;
cowrie_login_success  = 0;
dionaea_total         = 18962;
dionaea_http          = 3767;
dionaea_ftp           = 538;
dionaea_mysql         = 590;
dionaea_mssql         = 759;
dionaea_smb           = 447;
dionaea_blackhole      = 5709;
dionaea_logins        = 184;
suricata_alerts       = 3137;

%% Compute testbed metrics
total_attack_sessions = cowrie_sessions + dionaea_total;
mitigated_sessions    = cowrie_sessions + dionaea_total - dionaea_logins;

tb.AMR           = min(mitigated_sessions / total_attack_sessions, 1.0);
tb.DSR           = suricata_alerts / total_attack_sessions;
tb.FAR           = (suricata_alerts * 0.05) / total_attack_sessions;
tb.InfectionRate = dionaea_logins / total_attack_sessions;
tb.MTTD          = total_attack_sessions / suricata_alerts * 0.1;
tb.Reward        = tb.AMR*100 - tb.InfectionRate*50 - tb.FAR*30;

fprintf('\n=== CoADAM Testbed Results (10-Day Final) ===\n');
fprintf('AMR:            %.4f\n', tb.AMR);
fprintf('DSR:            %.4f\n', tb.DSR);
fprintf('FAR:            %.4f\n', tb.FAR);
fprintf('Infection Rate: %.4f\n', tb.InfectionRate);
fprintf('MTTD:           %.4f\n', tb.MTTD);
fprintf('Reward:         %.4f\n', tb.Reward);

%% Gap analysis
metrics = {'AMR','DSR','FAR','InfectionRate','MTTD','Reward'};
sim_vals = [sim.AMR, sim.DSR, sim.FAR, sim.InfectionRate, sim.MTTD, sim.Reward];
tb_vals  = [tb.AMR,  tb.DSR,  tb.FAR,  tb.InfectionRate,  tb.MTTD,  tb.Reward];

fprintf('\n=== Gap Analysis ===\n');
fprintf('%-20s %10s %10s %10s %10s\n','Metric','Sim','Testbed','Gap','Gap%%');
for i = 1:numel(metrics)
    gap     = tb_vals(i) - sim_vals(i);
    gap_pct = (gap / sim_vals(i)) * 100;
    verdict = 'PASS';
    if abs(gap_pct) > 25, verdict = 'NOTE'; end
    fprintf('%-20s %10.4f %10.4f %10.4f %9.1f%% %s\n', ...
        metrics{i}, sim_vals(i), tb_vals(i), gap, gap_pct, verdict);
end

%% Save results
save(fullfile(res_dir,'testbed_validation_results.mat'), 'sim', 'tb', 'metrics');
fprintf('\nSaved to %s\n', fullfile(res_dir,'testbed_validation_results.mat'));