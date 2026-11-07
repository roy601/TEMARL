function repro_check()
assert(~verLessThan('matlab','25.2'), 'Use MATLAB R2025b or newer.');
assert(exist('ranksum','file') == 2 && exist('iqr','file') == 2, ...
    'Statistics and Machine Learning Toolbox is required.');
root = getenv('COADAM_CELL');
load(fullfile(root, 'data', 'processed', 'environment_config.mat'), 'config');
assert(config.defender_state.n_features == 12);
assert(config.n_defender_actions == 4 && config.n_attacker_actions == 45);
env = iiot_environment(config);
env.intel_boost_enabled = true;
[first, ~] = env.reset(123456);
[next1, ~, reward1] = env.step(1, 1);
env.reset(123456);
[next2, ~, reward2] = env.step(1, 1);
assert(isequal(next1,next2) && reward1 == reward2, 'Seed replay failed');
assert(numel(first) == 12 && all(isfinite(next1)));
[value, state] = repro_adam({[1;2]}, {[1;-1]}, [], 0.001);
assert(state.step == 1 && abs(value{1}(1)-1.001) < 1e-8);
assert(abs(value{1}(2)-1.999) < 1e-8);
runtime.matlab_version = version;
runtime.computer = computer;
runtime.toolboxes = ver;
runtime.timestamp = char(datetime('now','Format','yyyy-MM-dd HH:mm:ss'));
fid = fopen(fullfile(root,'runtime.json'),'w');
assert(fid >= 0, 'Cannot save runtime metadata');
fprintf(fid,'%s',jsonencode(runtime));
fclose(fid);
fprintf('MATLAB, environment dimensions, deterministic reset, and Adam checks passed.\n');
end
