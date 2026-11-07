function repro_tabular()
root = getenv('COADAM_CELL');
settings = jsondecode(fileread(fullfile(root, 'settings.json')));
load(fullfile(root, 'data', 'processed', 'environment_config.mat'), 'config');
env = iiot_environment(config);
env.intel_boost_enabled = false;
trainer = coevolutionary_trainer(config, env);
fprintf('Training missing Tab-QL model using released tabular trainer.\n');
result = trainer.train(settings.seed_offset + 300000);
assert(any(result.def_Q(:) ~= 0), 'Tabular training produced an empty policy');
def_Q = result.def_Q;
atk_Q = result.atk_Q;
save(fullfile(root, 'results', 'cotraining_results.mat'), 'def_Q', 'atk_Q', '-v7.3');
metrics = {'training_rewards_def','training_rewards_atk','training_amr', ...
    'training_infection','training_dsr','training_far'};
data = zeros(settings.tabular_episodes, numel(metrics));
for index = 1:numel(metrics), data(:, index) = result.(metrics{index})(:); end
writetable(array2table(data, 'VariableNames', metrics), ...
    fullfile(root, 'results', 'tabular_training.csv'));
end
