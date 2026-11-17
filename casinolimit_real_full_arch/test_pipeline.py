import unittest
import numpy as np
import pipeline as p

class Checks(unittest.TestCase):
    def test_replay(self):
        r=p.runs(p.D.folds()[0],'test')[0]
        sp=p.make_spec(r,np.random.default_rng(1))
        e=p.CommandEngagementEnv(p.EnvConfig(fog=1)); e.reset(sp)
        for i,c in enumerate(sp.commands):
            _,done,info=e.step([0,0,0,0])
            self.assertEqual(info['labels'],c)
            self.assertEqual(info['machine'],r['machines'][i])
            self.assertEqual(done,i==len(sp.commands)-1)
            self.assertEqual(e.local_obs()[:,7:74].sum(),0)
        self.assertEqual(e.dwell,0)
        with self.assertRaises(RuntimeError): e.step([0]*4)
    def test_splits(self):
        for f in p.D.folds():
            a,b,c=[set(f[k+'_runs']) for k in ('train','val','test')]
            self.assertFalse(a&b or a&c or b&c)
            self.assertEqual(len(a|b|c),114)
    def test_past_only(self):
        class Recorder(p.nn.Module):
            def history(self,x,m): return x.sum((1,2))[:,None].repeat(1,64)
        r=p.runs(p.D.folds()[0],'test')[0]; sp=p.make_spec(r,np.random.default_rng(3))
        p.Bank.fog=0; bank=p.Bank(Recorder(),16)
        table=bank.table(sp); self.assertEqual(table[0].sum(),0)
        self.assertEqual(table[1,0],len(sp.commands[0]))
        p.Bank.fog=1; self.assertEqual(bank.table(sp).sum(),0)

if __name__=='__main__': unittest.main()
