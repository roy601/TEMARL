"""Data and environment checks only; these tests do not train models."""
import unittest
import numpy as np
from replay_data import audit, records, run_ids
from env_marl import EpisodeSource, EngagementEnv, EnvConfig, N_AGENTS
from pretrain_marl import windows


class ReplayTests(unittest.TestCase):
    def test_source_and_splits(self):
        result = audit()
        self.assertTrue(result['source_verified'])
        self.assertEqual(result['runs'], 36)
        self.assertEqual(result['labelled_steps'], 1347)

    def test_exact_replay_and_exhaustion(self):
        for split in ('train','validation','test'):
            specs = EpisodeSource(2310, split=split).take(len(run_ids(split)))
            self.assertEqual({s.run_id for s in specs}, set(run_ids(split)))
            for s in specs:
                r = records()[s.run_id]
                self.assertEqual(s.source_labels, r['labels'])
                np.testing.assert_array_equal(s.tau, r['ids'])
                self.assertEqual(s.horizon, len(r['labels']))
                env = EngagementEnv(EnvConfig(goal_steps=s.horizon+1)).reset(s)
                observed = []
                while not env.done:
                    _, _, info = env.step([0]*N_AGENTS)
                    observed.append(info['tau'])
                self.assertEqual(observed, list(r['ids']))
                with self.assertRaises(RuntimeError):
                    env.step([0]*N_AGENTS)
                x, lengths, y = windows([s])
                np.testing.assert_array_equal(y, s.tau[1:])
                for t in range(1, s.horizon):
                    np.testing.assert_array_equal(x[t-1,:lengths[t-1]], s.tau[max(0,t-16):t])

    def test_policy_cannot_change_sequence(self):
        for s in EpisodeSource(9).take(8):
            for action in ([0]*N_AGENTS, [1]*N_AGENTS, [3,4,1,2]):
                env = EngagementEnv().reset(s)
                observed = []
                while not env.done:
                    observed.append(env.step(action)[2]['tau'])
                self.assertEqual(observed, list(s.tau[:len(observed)]))

    def test_shared_specs(self):
        a = EpisodeSource(123, split='test').take(20)
        b = EpisodeSource(123, split='test').take(20)
        for x,y in zip(a,b):
            self.assertEqual(x.run_id,y.run_id)
            np.testing.assert_array_equal(x.tau,y.tau)
            np.testing.assert_array_equal(x.u,y.u)

    def test_prediction_test_uses_test_runs_without_training(self):
        from encoders_marl import build_encoder
        from pretrain_marl import test_prediction
        from scripts_marl import script_ids
        result = test_prediction(build_encoder('GRU').freeze(), script_ids())
        self.assertEqual(set(result['run_ids']), set(run_ids('test')))
        self.assertEqual(result['n_windows'], sum(len(records()[k]['ids'])-1 for k in run_ids('test')))
        self.assertLessEqual(result['top1'], result['top3'])
        self.assertEqual(len(result['examples']), result['n_windows'])
        for row in result['examples']:
            record = records()[row['run_id']]
            self.assertEqual(row['actual_source'], record['labels'][row['next_step']-1])
            self.assertEqual(row['actual_id'], record['ids'][row['next_step']-1])
            self.assertEqual(row['correct'], row['top3_ids'][0] == row['actual_id'])
            self.assertEqual(len(row['top3_ids']), 3)
            self.assertTrue(all(0 <= p <= 1 for p in row['top3_probabilities']))
            self.assertLessEqual(sum(row['top3_probabilities']), 1.000001)

    def test_readable_report_fixed_examples(self):
        from report_results import readable_predictions
        rows = []
        for encoder in ('Transformer', 'GRU', 'LSTM'):
            examples = [dict(run_id='example', next_step=step, history_ids=[0,1],
                             source_history=['T1190','T1566'], actual_id=0, actual_source='T1190',
                             top3_ids=[0,1,2], top3_probabilities=[.6,.2,.1], correct=True)
                        for step in range(2,7)]
            rows.append(dict(cell=dict(encoder=encoder, learner='MAPPO', seed=0),
                             prediction_test=dict(examples=examples)))
        text = '\n'.join(readable_predictions(rows))
        self.assertIn('60.00%', text)
        self.assertIn('Exploit Public-Facing Application', text)
        self.assertEqual(text.count('### example:'),3)
        self.assertIn('predict step 2',text)
        self.assertIn('predict step 4',text)
        self.assertIn('predict step 6',text)
        self.assertNotIn('predict step 3',text)
        self.assertIn('Pending', '\n'.join(readable_predictions([])))


if __name__ == '__main__':
    unittest.main(verbosity=2)
