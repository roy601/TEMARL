function [parameters, state] = repro_adam(parameters, directions, state, rate)
% Directions supplied by upstream backprop are NEGATIVE gradients of half MSE.
% Average over the batch before calling. Clip the combined gradient norm to 2.
% Adam defaults are a declared assumption, not recovered author settings.
if isempty(state)
    state.step = 0;
    state.first = cellfun(@(x) zeros(size(x)), parameters, 'UniformOutput', false);
    state.second = state.first;
end
norm_squared = sum(cellfun(@(x) sum(x(:).^2), directions));
factor = min(1, 2 / max(sqrt(norm_squared), eps));
state.step = state.step + 1;
for index = 1:numel(parameters)
    direction = directions{index} * factor;
    assert(all(isfinite(direction(:))), 'Nonfinite Adam direction');
    state.first{index} = 0.9 * state.first{index} + 0.1 * direction;
    state.second{index} = 0.999 * state.second{index} + 0.001 * direction.^2;
    first = state.first{index} / (1 - 0.9^state.step);
    second = state.second{index} / (1 - 0.999^state.step);
    parameters{index} = parameters{index} + rate * first ./ (sqrt(second) + 1e-8);
    assert(all(isfinite(parameters{index}(:))), 'Nonfinite Adam parameter');
end
end
