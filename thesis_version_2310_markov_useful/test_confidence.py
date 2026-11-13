"""Equation and leakage checks for the confidence-aware policy intervention."""
import copy
import unittest
import numpy as np
import torch
from torch.nn import functional as F

from confidence_ablation import (ConfidenceHistoryBank, entropy, fit_temperature,
                                 calibration_metrics, NT)
from encoders_marl import build_encoder
from mappo import Actor, compute_gae, clipped_policy_loss, critic_input
from env_marl import LOCAL_DIM, GLOBAL_DIM, N_AGENTS, EpisodeSource


class ConfidenceTests(unittest.TestCase):
    def test_entropy_extremes(self):
        np.testing.assert_allclose(entropy(np.ones((2,NT))/NT),1)
        p=np.zeros((1,NT)); p[0,0]=1
        np.testing.assert_allclose(entropy(p),0)

    def test_temperature_positive_preserves_ranking_and_fits_nll(self):
        logits=np.zeros((12,NT)); logits[:,0]=9
        targets=np.array([0,1]*6)
        t=fit_temperature(logits,targets)
        self.assertGreater(t,0)
        a=calibration_metrics(logits,targets,1)
        b=calibration_metrics(logits,targets,t)
        self.assertLessEqual(b['nll'],a['nll']+1e-8)
        self.assertEqual(a['top1'],b['top1'])

    def test_baseline_ignores_entropy_and_capacity_is_equal(self):
        torch.manual_seed(1); a=Actor(); b=Actor(True); b.load_state_dict(a.state_dict())
        local=torch.randn(8,LOCAL_DIM); h=torch.randn(8,64)
        low=torch.cat([h,torch.zeros(8,1)],-1)
        high=torch.cat([h,torch.ones(8,1)],-1)
        torch.testing.assert_close(a(local,low)[0],a(local,high)[0])
        torch.testing.assert_close(a(local,h)[0],a(local,low)[0])
        self.assertFalse(torch.equal(b(local,low)[0],b(local,high)[0]))
        self.assertEqual(sum(p.numel() for p in a.parameters()),sum(p.numel() for p in b.parameters()))
        b.eval(); old=b(local,high)[0]; b.train()
        torch.testing.assert_close(old,b(local,high)[0])

    def test_critic_ignores_confidence_in_both_modes(self):
        l=np.zeros((2,N_AGENTS,LOCAL_DIM),np.float32)
        g=np.zeros((2,GLOBAL_DIM),np.float32)
        h=np.zeros((2,65),np.float32); other=h.copy(); other[:,-1]=1
        for central in (False,True):
            np.testing.assert_array_equal(critic_input(central,l,h,g),critic_input(central,l,other,g))

    def test_confidence_bank_never_reads_future_and_preserves_embedding(self):
        from pretrain_marl import HistoryBank
        sp=EpisodeSource(7).next(); altered=copy.deepcopy(sp)
        altered.tau[3:] = (altered.tau[3:]+1)%NT
        for name in ('Transformer','GRU','LSTM'):
            enc=build_encoder(name).freeze()
            bank=ConfidenceHistoryBank(enc,1.3)
            x,y=bank.tables([sp,altered])
            np.testing.assert_allclose(x[:4],y[:4],atol=1e-6)
            np.testing.assert_allclose(x[:,:64],HistoryBank(enc).tables([sp])[0],atol=1e-5)
            self.assertTrue(np.all((x[:,-1]>=0)&(x[:,-1]<=1)))
            self.assertEqual(x[0,-1],1.)

    def test_gae_terminal_and_bootstrap(self):
        r=np.array([[1.],[2.]],np.float32)
        v=np.array([[[.5]],[[.8]]],np.float32)
        done=np.array([[0.],[1.]],np.float32)
        a,ret=compute_gae(r,done,v,np.array([[100.]],np.float32),.9,.8)
        np.testing.assert_allclose(a[:,0,0],[1+.9*.8-.5+.9*.8*1.2,1.2],rtol=1e-6)
        np.testing.assert_allclose(ret,a+v)
        a,_=compute_gae(r[:1],done[:1],v[:1],np.array([[2.]],np.float32),.9,.8)
        np.testing.assert_allclose(a,2.3,rtol=1e-6)

    def test_ppo_clipping_both_advantage_signs(self):
        ratio=torch.tensor([1.5,.5,1.5,.5],requires_grad=True)
        adv=torch.tensor([1.,1.,-1.,-1.])
        loss=clipped_policy_loss(ratio.log(),torch.zeros(4),adv,torch.ones(4)*.4,.2,.01)
        expected=-torch.tensor([1.2,.5,-1.5,-.8]).mean()-.004
        torch.testing.assert_close(loss,expected)
        loss.backward(); self.assertTrue(torch.isfinite(ratio.grad).all())

    def test_transformer_attention_matches_explicit_equation(self):
        enc=build_encoder('Transformer').double().eval()
        layer=enc.enc.layers[0]; attn=layer.self_attn
        x=torch.randn(2,4,64,dtype=torch.double)
        mask=torch.tensor([[False,False,False,True],[False,False,True,True]])
        q,k,v=F.linear(x,attn.in_proj_weight,attn.in_proj_bias).chunk(3,-1)
        q,k,v=[a.reshape(2,4,4,16).transpose(1,2) for a in (q,k,v)]
        scores=(q@k.transpose(-2,-1))/4
        scores=scores.masked_fill(mask[:,None,None,:],float('-inf'))
        manual=(scores.softmax(-1)@v).transpose(1,2).reshape(2,4,64)
        manual=F.linear(manual,attn.out_proj.weight,attn.out_proj.bias)
        actual=attn(x,x,x,key_padding_mask=mask,need_weights=False)[0]
        torch.testing.assert_close(actual,manual)
        a=layer.norm1(x+manual)
        expected=layer.norm2(a+layer.linear2(F.relu(layer.linear1(a))))
        torch.testing.assert_close(layer(x,src_key_padding_mask=mask),expected)


if __name__ == '__main__':
    torch.set_num_threads(2)
    unittest.main(verbosity=2)
