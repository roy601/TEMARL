"""Focused integrity tests; full training belongs on the lab PC."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

import _frozen
from markov_data import (load_runs,split_runs,subset,generate,windows,repeat_windows,
                         grams,quality,metrics,evaluation_specs,ReplaySource,digest,NT)
from scripts_marl import estimate_chain
from markov_training import train_encoder,predict,load_encoder


class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runs=load_runs(); cls.split,_=split_runs(cls.runs)

    def test_source_integrity_and_counts(self):
        self.assertTrue(all(_frozen.verify().values()))
        self.assertEqual(len(self.runs),36)
        self.assertEqual(sum(len(r["seq"]) for r in self.runs),1347)

    def test_split_disjoint_complete_and_before_windows(self):
        ids=[{r["id"] for r in rs} for rs in self.split.values()]
        self.assertEqual(len(set.union(*ids)),36)
        self.assertEqual(sum(map(len,ids)),36)
        groups=[{r["group"] for r in rs} for rs in self.split.values()]
        for i in range(3):
            for j in range(i):
                self.assertFalse(groups[i]&groups[j])
        for part,rs in self.split.items():
            X,L,Y,owners=windows(rs)
            self.assertEqual(len(Y),sum(len(r["seq"])-1 for r in rs))
            self.assertEqual(set(owners),{r["id"] for r in rs})

    def test_duplicates_cannot_cross_splits(self):
        extra=dict(self.runs[0],id="copied_playbook")
        split,_=split_runs(self.runs+[extra])
        locations=[part for part,rs in split.items() if any(r["group"]==extra["group"] for r in rs)]
        self.assertEqual(len(locations),1)

    def test_loso_has_no_heldout_training_scenario(self):
        for sid in sorted({r["scenario"] for r in self.runs}):
            sp,_=split_runs(self.runs,held_out=sid)
            self.assertFalse(any(r["scenario"]==sid for r in sp["train"]+sp["validation"]))
            self.assertTrue(all(r["scenario"]==sid for r in sp["test"]))

    def test_nested_subsets_and_generation(self):
        prev=set()
        for f in (.25,.5,.75,1.):
            ids={r["id"] for r in subset(self.split["train"],f,0)}
            self.assertTrue(prev <= ids); prev=ids
        a=generate(self.split["train"],.5,123)
        b=generate(self.split["train"],2.,123)
        self.assertEqual(a,b[:len(a)])

    def test_generator_only_fits_supplied_training(self):
        import markov_data
        with patch.object(markov_data,"estimate_chain",wraps=estimate_chain) as estimator:
            gen=generate(self.split["train"],1.,11)
        fitted=[seq for call in estimator.call_args_list for seq in call.args[0]]
        self.assertEqual(sorted(fitted),sorted(r["seq"] for r in self.split["train"]))
        train_ids={r["id"] for r in self.split["train"]}
        self.assertTrue(all(r["length_source"] in train_ids for r in gen))
        for r in gen:
            lengths={len(x["seq"]) for x in self.split["train"] if x["scenario"]==r["scenario"]}
            self.assertIn(len(r["seq"]),lengths)

    def test_transition_formula_and_no_cross_run_edges(self):
        T,init=estimate_chain([[0,1],[2,3]])
        self.assertAlmostEqual(T[0,1],4.02/(NT*.02+4.))
        self.assertAlmostEqual(T[1,2],1/NT)
        self.assertAlmostEqual(init[0],2.02/(NT*.02+4.))
        self.assertTrue(np.allclose(T.sum(1),1))

    def test_exact_window_match_for_repeat_control(self):
        tr=self.split["train"]; syn=generate(tr,2.,0)
        original=windows(tr); augmented=windows(tr+syn)
        repeat=repeat_windows(original,len(augmented[2]))
        self.assertEqual(len(repeat[2]),len(augmented[2]))
        old={(tuple(x),int(l),int(y)) for x,l,y in zip(*original[:3])}
        self.assertTrue(all((tuple(x),int(l),int(y)) in old for x,l,y in zip(*repeat[:3])))

    def test_replay_keeps_exact_sequence_and_matched_uniforms(self):
        a,labels=evaluation_specs(self.split["test"],2,7)
        b,_=evaluation_specs(self.split["test"],2,7)
        lookup={r["id"]:r for r in self.split["test"]}
        for sp,other,label in zip(a,b,labels):
            self.assertEqual(sp.tau.tolist(),lookup[label["run"]]["seq"])
            self.assertTrue(np.array_equal(sp.u,other.u))
            self.assertEqual(sp.horizon,len(sp.tau))

    def test_metrics_and_quality_do_not_claim_causal_validity(self):
        p=np.array([[.7,.2,.1],[.1,.2,.7]])
        result=metrics(p,np.array([0,1]),["a","b"])
        self.assertEqual(result["top1"],.5)
        self.assertEqual(result["top3"],1.)
        self.assertAlmostEqual(result["nll"],-np.log(.14)/2)
        q=quality(generate(self.split["train"],1.,0),self.split["train"])
        self.assertIsNone(q["aep_valid_pct"])

    def test_real_epochs_and_checkpoint_round_trip(self):
        torch.set_num_threads(2)
        tiny=windows([self.split["train"][0]])
        with tempfile.TemporaryDirectory() as folder:
            enc,info=train_encoder("GRU",0,tiny,tiny,2,"cpu",Path(folder))
            self.assertEqual(info["epochs_completed"],2)
            self.assertEqual([r["epoch"] for r in info["curve"]],[1,2])
            a,_=predict(enc,tiny,"cpu")
            b,_=predict(load_encoder(folder,"cpu"),tiny,"cpu")
            self.assertEqual(a,b)
            ck=torch.load(Path(folder)/"encoder.pt",weights_only=True)
            self.assertEqual(ck["selected_epoch"],2)
            self.assertTrue((Path(folder)/"encoder_best.pt").exists())

    def test_pilot_selects_one_shared_budget_without_test(self):
        import argparse
        from run_markov_study import choose_epochs
        args=argparse.Namespace(smoke=False,epochs="auto",pilot_seeds=[101],pilot_cap=10,device="cpu")
        epochs=iter([3,7,5])
        def fake_train(arm,seed,training,validation,cap,device,folder):
            self.assertEqual(set(training[3]),{r["id"] for r in self.split["train"]})
            self.assertEqual(set(validation[3]),{r["id"] for r in self.split["validation"]})
            folder.mkdir(parents=True,exist_ok=True)
            torch.save({},folder/"encoder.pt")
            return None,dict(selected_epoch=next(epochs))
        with tempfile.TemporaryDirectory() as d, patch("run_markov_study.train_encoder",side_effect=fake_train):
            self.assertEqual(choose_epochs(args,self.split,Path(d),{"fingerprint":"test"}),7)

    def test_rl_uses_explicit_sources_not_old_markov(self):
        from mappo import train,HP
        from env_marl import EnvConfig
        val,_=evaluation_specs(self.split["validation"][:1],1,2)
        test,_=evaluation_specs(self.split["test"][:1],1,3)
        with patch.dict(HP,dict(n_envs=1,rollout_len=2,ppo_epochs=1,n_evals=1)), \
             patch("mappo.EpisodeSource",side_effect=AssertionError("Legacy source leaked into controlled study")):
            result=train(None,EnvConfig(),["S1"],0,2,device="cpu",
                         train_source=ReplaySource(self.split["train"][:1],1),validation_specs=val,evaluation_specs=test)
        self.assertEqual(result["env_steps"],2)
        self.assertEqual(len(result["test_rows"]),1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
