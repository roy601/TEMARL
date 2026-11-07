function repro_initialize()
root = getenv('COADAM_CELL');
package = getenv('COADAM_PACKAGE');
settings = jsondecode(fileread(fullfile(root, 'settings.json')));
load(fullfile(settings.config_source, 'environment_config.mat'), 'config');
config.training.max_steps = settings.max_steps;
config.episode.max_steps = settings.max_steps;
config.training.n_episodes = settings.tabular_episodes;
if strcmp(settings.track, 'paper_aligned')
    config.training.attacker.learning_rate = 0.01;
    config.training.attacker.gamma = 0.90;
    config.training.attacker.epsilon_start = 0.30;
end
folder = fullfile(root, 'data', 'processed');
if ~isfolder(folder), mkdir(folder); end
save(fullfile(folder, 'environment_config.mat'), 'config');
copyfile(fullfile(settings.config_source, 'threat_profiles.mat'), folder);
addpath(fullfile(root, 'code'));
addpath(fullfile(package, 'matlab'));
fprintf('Configured %s seed %d, %d training and %d evaluation episodes.\n', ...
    settings.track, settings.seed, settings.train_episodes, settings.eval_episodes);
end
