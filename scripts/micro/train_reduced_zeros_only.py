#!/usr/bin/env python3
"""β-reduce with zeros only (flips disabled). Sweep zero_threshold."""

from __future__ import annotations
import json, sys, time
from pathlib import Path
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from micro_model import MicroModel, MicroConfig
from reduce import reduce_attention, measure_mspace

def load_ex(p):
    return [json.loads(l) for l in open(p) if l.strip()]

def tok(exs, tokenizer, cfg):
    seqs = []
    for ex in exs:
        ids = tokenizer.encode(f"{ex['input']}\n{ex['output']}", add_special_tokens=False)
        ids.append(cfg.eod_id)
        seqs.append(np.array(ids[:cfg.max_seq_len], dtype=np.int32))
    return seqs

class DL:
    def __init__(self, seqs, bs, sl, seed=42):
        self.seqs, self.bs, self.sl = seqs, bs, sl
        self.rng = np.random.RandomState(seed)
        self._build()
    def _build(self):
        idx = self.rng.permutation(len(self.seqs))
        self.stream = np.concatenate([self.seqs[i] for i in idx])
        self.pos = 0
    def next_batch(self):
        n = self.bs * (self.sl + 1)
        if self.pos + n > len(self.stream): self._build()
        buf = self.stream[self.pos:self.pos+n].reshape(self.bs, self.sl+1)
        self.pos += n
        return mx.array(buf[:,:self.sl]), mx.array(buf[:,1:self.sl+1])

def train_5k(model, cfg, train_seqs, ev_in, ev_tgt):
    lr_sched = optim.cosine_decay(3e-4, 5000, 3e-6)
    warmup = optim.linear_schedule(1e-7, 3e-4, 100)
    def lr_fn(s): return warmup(s) if s < 100 else lr_sched(s)
    opt = optim.AdamW(learning_rate=lr_fn, weight_decay=0.01)
    def lfn(m, x, t):
        _, l = m(x, t)
        return l
    lag = nn.value_and_grad(model, lfn)
    loader = DL(train_seqs, cfg.batch_size, cfg.max_seq_len, seed=42)
    t0 = time.time()
    for step in range(1, 5001):
        model._training_step = step
        inp, tgt = loader.next_batch()
        lv, g = lag(model, inp, tgt)
        g, gn = optim.clip_grad_norm(g, 1.0)
        opt.update(model, g)
        mx.eval(model.parameters(), opt.state, lv, gn)
        if step % 1000 == 0 or step == 1:
            _, el = model(ev_in, ev_tgt)
            mx.eval(el)
            print(f'    step {step:>5}: train={float(lv.item()):.4f}, '
                  f'eval={float(el.item()):.4f}, {time.time()-t0:.0f}s', flush=True)
    _, fl = model(ev_in, ev_tgt)
    mx.eval(fl)
    return float(fl.item())

def main():
    t0 = time.time()
    print("=" * 70, flush=True)
    print("β-REDUCE: ZEROS ONLY (no flips)", flush=True)
    print("=" * 70, flush=True)

    cfg = MicroConfig()
    trained_model = MicroModel(cfg)
    w = mx.load('checkpoints/micro/final/model.npz')
    trained_model.load_weights(list(w.items()))
    mx.eval(trained_model.parameters())

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B')
    train_seqs = tok(load_ex(cfg.train_file), tokenizer, cfg)
    eval_seqs = tok(load_ex(cfg.eval_file), tokenizer, cfg)
    stream = np.concatenate(eval_seqs)
    T = min(cfg.max_seq_len, len(stream)-1)
    ev_in = mx.array(stream[:T].reshape(1,T))
    ev_tgt = mx.array(stream[1:T+1].reshape(1,T))

    results = []
    for zt in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]:
        print(f'\n{"─"*70}', flush=True)
        print(f'  zero_thresh={zt} (flips disabled)', flush=True)
        print(f'{"─"*70}', flush=True)

        model = MicroModel(cfg)
        mx.eval(model.parameters())

        for li in range(cfg.n_layers):
            Wq = np.array(trained_model.blocks[li].attn.q_proj.weight)
            Wk = np.array(trained_model.blocks[li].attn.k_proj.weight)
            r = reduce_attention(Wq, Wk, zero_threshold=zt, flip_threshold=999.0)
            block = model.blocks[li]
            block.attn.q_proj.weight = mx.array(r['W_q_ternary'] * r['gamma_q'])
            block.attn.k_proj.weight = mx.array(r['W_k_ternary'] * r['gamma_k'])
            block.attn.q_proj.freeze(keys=['weight'])
            block.attn.k_proj.freeze(keys=['weight'])
        mx.eval(model.parameters())

        # Layer 2 stats
        Wq2 = np.array(trained_model.blocks[2].attn.q_proj.weight)
        Wk2 = np.array(trained_model.blocks[2].attn.k_proj.weight)
        r2 = reduce_attention(Wq2, Wk2, zero_threshold=zt, flip_threshold=999.0)
        zf = r2['stats']['q']['zero_frac']
        ms_init = measure_mspace(r2['W_q_ternary'], r2['W_k_ternary'])
        print(f'  L2: {zf:.0%} zeros, K={r2["stats"]["K"]}, '
              f'rank90={ms_init["rank90"]}, top1={ms_init["top1_pct"]:.1f}%', flush=True)

        final_loss = train_5k(model, cfg, train_seqs, ev_in, ev_tgt)
        ms_final = measure_mspace(
            np.array(model.blocks[2].attn.q_proj.weight),
            np.array(model.blocks[2].attn.k_proj.weight))
        print(f'  Final: loss={final_loss:.4f}, L2 rank90={ms_final["rank90"]}, '
              f'top1={ms_final["top1_pct"]:.1f}%', flush=True)

        results.append({'zt': zt, 'zero_frac': zf, 'loss': final_loss,
                        'rank90': ms_final['rank90'], 'top1': ms_final['top1_pct']})

    print(f'\n{"="*70}', flush=True)
    print('COMPARISON (zeros-only vs prior variants)', flush=True)
    print(f'{"="*70}', flush=True)
    ref = [('A. Float32', 6.7412, 6, 80.5, '—'),
           ('B. Sign-only', 6.8625, 32, 45.5, '0%'),
           ('C. M-noise 30%', 6.6972, 25, 56.1, '30%')]
    for r in results:
        ref.append((f'I. SNR-zeros zt={r["zt"]}', r['loss'], r['rank90'],
                     r['top1'], f'{r["zero_frac"]:.0%}'))
    best = min(v[1] for v in ref)
    print(f'\n{"Variant":>28} | {"Loss":>8} | {"r90":>4} | {"top1":>6} | {"zeros":>5}', flush=True)
    print('-'*62, flush=True)
    for n,l,r,t,z in ref:
        m = ' ★' if l == best else ''
        print(f'{n:>28} | {l:>8.4f} | {r:>4} | {t:>5.1f}% | {z:>5}{m}', flush=True)

    print(f'\nElapsed: {time.time()-t0:.0f}s', flush=True)
    Path('results/reduced-zeros-only').mkdir(parents=True, exist_ok=True)
    with open('results/reduced-zeros-only/summary.json','w') as f:
        json.dump(results, f, indent=2)
    print('Saved to results/reduced-zeros-only/summary.json', flush=True)

if __name__ == '__main__':
    main()
