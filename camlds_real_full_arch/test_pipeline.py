import unittest
import copy
import numpy as np
import torch
import pipeline as p

class IntegrationTests(unittest.TestCase):
    def test_all_folds_and_vocabulary(self):
        a = p.audit()
        self.assertEqual((a['steps'],a['runs'],a['labels'],a['folds']), (904,34,81,32))
        import d3fend_payoff
        for i,t in enumerate(p.port.LABELS):
            np.testing.assert_array_equal(p.env.PAYOFF[i], d3fend_payoff.PAYOFF[p.env.TECHNIQUES[t]['id']])

    def test_execution_order_and_source_labels(self):
        f = p.ordered_folds('execution')[0]
        source = {s['source_row']: s for s in p.data.steps_for('main')}
        for s in f['_steps']:
            self.assertEqual(s['techniques_parent'],source[s['source_row']]['techniques_parent'])
        for name in {s['run'] for s in f['_steps']}:
            seq = sorted([s for s in f['_steps'] if s['run']==name], key=lambda s:s['exec_index'])
            self.assertEqual([s['exec_index'] for s in seq], list(range(len(seq))))

    def test_replay_every_supported_run(self):
        all_steps = p.ordered_folds('execution')[0]['_steps']
        f = {'_steps':all_steps,'train_runs':sorted({s['run'] for s in all_steps})}
        replay_runs = p.runs(f, 'train')
        self.assertIn('S4', {r['scenario'] for r in replay_runs})
        for spec in p.specs(replay_runs,3,1):
            e = p.env.CommandEngagementEnv().reset(spec)
            self.assertEqual(e.local_obs().shape, (4,p.env.LOCAL_DIM))
            self.assertEqual(e.global_state().shape, (p.env.GLOBAL_DIM,))
            consumed=[]
            while not e.done:
                _,_,info=e.step([0]*4)
                consumed.append(info['labels'])
            self.assertEqual(tuple(consumed), spec.commands[:len(consumed)])
            self.assertLessEqual(e.t,spec.horizon)
            with self.assertRaises(RuntimeError): e.step([0]*4)

    def test_history_has_no_future_and_encoder_is_frozen(self):
        f = p.ordered_folds('execution')[0]
        spec = p.specs(p.runs(f,'train'),1,1)[0]
        changed = copy.deepcopy(spec)
        changed.run_id += '_changed'
        changed.commands = spec.commands[:3] + ((0,),)*(len(spec.commands)-3)
        for variant in ('baseline','allpos','gru_allpos','lstm_allpos'):
            model=p.variants.build_variant(variant,16)
            bank=p.marl.HistoryBank(model,16)
            a,b=bank.table(spec),bank.table(changed)
            np.testing.assert_allclose(a[:4],b[:4], atol=1e-6)
            self.assertTrue(all(not x.requires_grad for x in model.parameters()))
            self.assertEqual(a.shape,(spec.horizon+1,64))
            np.testing.assert_array_equal(a[0],np.zeros(64))

    def test_common_random_numbers(self):
        f=p.ordered_folds('execution')[0]
        a=p.specs(p.runs(f,'test'),200000,2)
        b=p.specs(p.runs(f,'test'),200000,2)
        for x,y in zip(a,b): np.testing.assert_array_equal(x.u,y.u)

if __name__=='__main__':
    torch.set_num_threads(2)
    unittest.main()
