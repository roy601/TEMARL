"""Auditable, count-checked portability patches; upstream is never modified."""
import difflib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one patch anchor: {old[:100]!r}')
    return text.replace(old, new, 1)

def prepare(cell, settings):
    cell = Path(cell)
    for folder in ('code', 'patches', 'results', 'logs', 'phase3_defender', 'phase5_baselines'):
        (cell / folder).mkdir(parents=True, exist_ok=True)
    (cell / 'settings.json').write_text(json.dumps(settings, indent=2), encoding='utf-8')
    for source in (ROOT / 'upstream').glob('*.m'):
        if source.name not in ('iiot_environment.m', 'coevolutionary_trainer.m', 'Phase_3and4.m', 'Phase5_Baselines.m'):
            continue
        original = source.read_text(encoding='utf-8-sig')
        code = original
        if source.name.startswith('Phase'):
            code = replace(code, "project_root  = '/Users/ujw/Desktop/CoADAM';",
                "project_root = getenv('COADAM_CELL');\nrc = jsondecode(fileread(fullfile(project_root,'settings.json')));")
            # reset() seeds MATLAB's global stream; shifting only rng() is insufficient.
            code = re.sub(r'\.reset\((\d+)', r'.reset(rc.seed_offset + \1', code)
            code = re.sub(r'rng\((\d+)\)', r'rng(rc.seed_offset + \1)', code)
        if source.name == 'Phase_3and4.m':
            code = replace(code, 'n_episodes = 5000;', 'n_episodes = rc.train_episodes;')
            code = replace(code, 'n_eval = 100;', 'n_eval = rc.eval_episodes;')
            if settings['track'] == 'paper_aligned':
                code = replace(code, 'atk_epsilon   = 0.20;', 'atk_epsilon   = 0.30;')
                code = replace(code, 'grad_clip     = 1.0;', 'grad_clip     = 2.0;\nadam_state = [];')
                code = replace(code, 'td_err = max(-grad_clip, min(grad_clip, td_err));', '% Global gradient norm clipping is applied by repro_adam.')
                old = '''            scale = dqn_lr / batch_size;
            W1 = W1 + scale * gW1; b1 = b1 + scale * gb1;
            W2 = W2 + scale * gW2; b2 = b2 + scale * gb2;
            W3 = W3 + scale * gW3; b3 = b3 + scale * gb3;'''
                new = '''            gradients = {gW1/batch_size,gb1/batch_size,gW2/batch_size,gb2/batch_size,gW3/batch_size,gb3/batch_size};
            [parameters,adam_state] = repro_adam({W1,b1,W2,b2,W3,b3}, gradients, adam_state, dqn_lr);
            [W1,b1,W2,b2,W3,b3] = parameters{:};'''
                code = replace(code, old, new)
                old = '''    if mod(ep, target_update_freq) == 0
        W1_t = W1; b1_t = b1;
        W2_t = W2; b2_t = b2;
        W3_t = W3; b3_t = b3;
    end'''
                code = replace(code, old, '% Target network updated on environment steps above.')
                code = replace(code, '        ep_def_r = ep_def_r + def_r;', '''        if mod(total_steps, target_update_freq) == 0
            W1_t=W1; b1_t=b1; W2_t=W2; b2_t=b2; W3_t=W3; b3_t=b3;
        end
        ep_def_r = ep_def_r + def_r;''')
                start = code.index('            temperature = max(0.25,')
                end = code.index("            def_a = find(cum_probs >= rand(), 1, 'first');", start)
                end += len("            def_a = find(cum_probs >= rand(), 1, 'first');")
                code = code[:start] + '            [~, def_a] = max(q_vals); % epsilon-greedy assumption' + code[end:]
        if source.name == 'Phase5_Baselines.m':
            code = replace(code, 'n_eval        = 100;', "assert(has_tabular, 'Required Tabular_QL model is missing; refusing static fallback');\nn_eval = rc.eval_episodes;")
            code = replace(code, 'n_indiv_episodes = 3000;', 'n_indiv_episodes = rc.baseline_episodes;')
            code = replace(code, 'n_dec_episodes = 3000;', 'n_dec_episodes = rc.baseline_episodes;')
            code = replace(code, 'n_stack_sim  = 50;', 'n_stack_sim = rc.stack_simulations;')
            code = replace(code, 'n_finetune = 1000;', 'n_finetune = rc.finetune_episodes;')
            if settings['track'] == 'paper_aligned':
                code = replace(code, 'rc.seed_offset + 5000 + mi*100 + ep', 'rc.seed_offset + 100000 + ep')
                code = replace(code, 'rc.seed_offset + 8000 + mi*100 + ep', 'rc.seed_offset + 200000 + ep')
            start = code.index('% ADVERSARIAL ADAPTATION TEST (500 eps, same as before)')
            end = code.index('% LOCAL FUNCTIONS', start)
            code = code[:start] + '''% Scope: Tables 5/6 only. Later adaptation study is not run.
save(fullfile(results_dir,'baseline_results_final.mat'), ...
    'results_tableA','results_tableB','method_names','n_eval','n_finetune','-v7');
fprintf('Tables 5/6 raw episode results saved.\\n');
%%
''' + code[end:]
        (cell / 'code' / source.name).write_text(code, encoding='utf-8')
        diff = ''.join(difflib.unified_diff(original.splitlines(True), code.splitlines(True),
            fromfile='upstream/' + source.name, tofile='generated/' + source.name))
        (cell / 'patches' / (source.name + '.diff')).write_text(diff, encoding='utf-8')
