function repro_training_export()
root = getenv('COADAM_CELL');
path = fullfile(root, 'results', 'dqn_cotraining_results.mat');
names = {'trk_def_reward','trk_atk_reward','trk_amr','trk_infection', ...
    'trk_dsr','trk_far','trk_mttd','trk_dwell','trk_dce','trk_loss', ...
    'trk_ep_length','trk_eps_def','trk_eps_atk','trk_mask_count','trk_pool_used'};
result = load(path, names{:});
n = numel(result.trk_amr);
data = zeros(n, numel(names));
for index = 1:numel(names), data(:, index) = result.(names{index})(:); end
assert(all(isfinite(data(:))), 'Nonfinite training curve');
writetable(array2table([(1:n)' data], 'VariableNames', [{'episode'} names]), ...
    fullfile(root, 'results', 'training.csv'));
end
