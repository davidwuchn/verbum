"""XM Sampled-Teacher — port 3 etch. §XM-SAMPLED-TEACHER (FROZEN s298).

The last XM lever. s296-297 closed the DETERMINISTIC-teacher arc (no
multimodality to explore). Port 3 breaks that hinge with a genuinely multimodal
source: Qwen3-4B SAMPLED at temp 1.3 reducing combinator expressions. Design 1
(Michael-approved): keep the toy 26-token KIBC task + mini_holo student
UNCHANGED; the teacher's sampled token outputs (mapped back into the vocab) are
the distillation targets.

Etch signal (necessary change): a sampled LLM emits TOKENS, not commensurable
activations, so the etch switches from activation-MSE (s296-297) to the
output-CE sign-vote (`etch_plates`: accumulate sign(grad masked_ce_loss), flip
plates where confidence > 0.6). Internally controlled (all arms use it).

The paper's core contrast, instantiated (equal K-pair budget per input; only
target CONTENT differs):
  baseline   the K distinct Qwen samples (the mode MIXTURE = M=1 blur)
  xm         [best] x K, best = min token-distance to ground truth (mode-commit)
  xm_rand    [random] x K (random mode-commit; load-bearing selection null)

Student learns ONLY from teacher targets (etch + beam-fit both use the arm's
targets; NO ground-truth GD). Ground truth is used ONLY by the selector and the
eval. Recovery = student true-task acc / true-task GDModel-oracle acc.

Gates (frozen §XM-SAMPLED-TEACHER):
  G1  xm > baseline                    (mode-commit beats blur)
  G2  xm > xm_rand   [lambda yardstick] (selection-toward-truth, load-bearing)
  G3  (xm-xm_rand) gain GREATER in depth 2-3 (spread~1.8) than depth 1 (spread~1.0)
Verdicts: SAMPLED-TEACHER-UNBLOCKS / SELECTION-HELPS-UNSTRUCTURED /
          MIXTURE-ARTIFACT / STILL-BLOCKED.

Two stages:
  --gen   : load Qwen3-4B (torch), sample K reductions/expr, cache targets.
  (etch)  : consume cache, run arms x probes x seeds (MLX), score frozen gates.

License: MIT
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "v12"))

import mlx.core as mx  # noqa: E402
import mlx.nn as nn  # noqa: E402
import mlx.optimizers as optim  # noqa: E402
import numpy as np  # noqa: E402
from mini_holo_d_sweep_v2 import (  # noqa: E402
    EOS_ID,
    EQ_ID,
    PAD_ID,
    TOK2ID,
    GDModel,
    HoloModel,
    _extract_plate_grad,
    _get_plates,
    eval_by_depth,
    eval_model,
    generate_batch,
    masked_ce_loss,
)
from xm_sampled_teacher_probe import (  # noqa: E402
    build_messages,
    canonical,
    extract_answer,
    make_examples,
    parse_expr,
    to_chat,
)

PLATE_NAMES = ["attn.k_plate", "attn.v_plate", "attn.o_plate", "ffn_plate"]
MAX_LEN = 40
ARMS = ["baseline", "xm", "xm_rand"]


# ══════════════════════════════════════════════════════════════════════
# Token utilities
# ══════════════════════════════════════════════════════════════════════

def tok_dist(a: list[str], b: list[str]) -> int:
    """Token-level Levenshtein distance (graded selection score)."""
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[lb]


def build_batch_from_pairs(pairs: list[tuple[list[str], list[str]]]):
    """(inp_toks, out_toks) pairs -> (input_ids, targets, mask) mirroring
    generate_batch exactly (mask covers '=' + output toks, not EOS/PAD)."""
    all_ids, all_tgt, all_msk = [], [], []
    for inp_toks, out_toks in pairs:
        seq = ["<bos>", *inp_toks, "=", *out_toks, "<eos>"]
        ids = [TOK2ID[t] for t in seq]
        n = min(len(ids), MAX_LEN)
        ids = ids[:MAX_LEN] + [PAD_ID] * (MAX_LEN - n)
        target = [*ids[1:], PAD_ID]
        mask = [0] * MAX_LEN
        eq_pos = None
        for i, tid in enumerate(ids):
            if tid == EQ_ID:
                eq_pos = i
                mask[i] = 1
            elif eq_pos is not None and tid != PAD_ID and tid != EOS_ID:
                mask[i] = 1
        all_ids.append(ids)
        all_tgt.append(target)
        all_msk.append(mask)
    return (mx.array(np.array(all_ids, dtype=np.int32)),
            mx.array(np.array(all_tgt, dtype=np.int32)),
            mx.array(np.array(all_msk, dtype=np.float32)))


# ══════════════════════════════════════════════════════════════════════
# Arm target construction (baseline mixture / xm best / xm_rand random)
# ══════════════════════════════════════════════════════════════════════

def arm_pairs(items: list[dict], arm: str, K: int,
              rng: np.random.RandomState) -> list[tuple]:
    """Build the arm's (inp_toks, out_toks) pairs — K per input, equal budget."""
    pairs = []
    for it in items:
        inp = it["inp_toks"]
        samples = it["samples"]           # K reduced-canonical toklists
        if arm == "baseline":
            for s in samples:
                pairs.append((inp, s))
        elif arm == "xm":
            gt = it["gt_toks"]
            best = min(samples, key=lambda s: tok_dist(s, gt))
            pairs.extend([(inp, best)] * K)
        elif arm == "xm_rand":
            r = int(rng.randint(0, len(samples)))
            pairs.extend([(inp, samples[r])] * K)
        else:
            raise ValueError(arm)
    return pairs


def pairs_to_batches(pairs: list[tuple], batch_size: int,
                     rng: np.random.RandomState) -> list[tuple]:
    idx = rng.permutation(len(pairs))
    batches = []
    for i in range(0, len(pairs), batch_size):
        chunk = [pairs[j] for j in idx[i:i + batch_size]]
        batches.append(build_batch_from_pairs(chunk))
    return batches


# ══════════════════════════════════════════════════════════════════════
# Output-CE sign-vote etch over teacher-target batches
# ══════════════════════════════════════════════════════════════════════

def etch_from_batches(model, batches, n_rounds, confidence_threshold=0.6):
    """Pure multi-round output-CE sign-vote etch (DETERMINISTIC).

    Each round accumulates sign(grad masked_ce_loss) over the teacher-target
    batches on the current (plate) config and flips where confidence > 0.6.
    NO interleaved Adam — continuous beams are fit once in the post-etch GD
    phase (run_arm). Keeping the etch beam-free makes the plate signs
    bit-reproducible within-process and removes MPS-Adam plate-structure noise
    (the graded recovery is handled by >=5 seeds + internal paired deltas)."""
    n_layers = len(model.layers)
    plates = _get_plates(model)
    plate_paths = [(i, p) for i in range(n_layers) for p in PLATE_NAMES]
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    log = []
    for r in range(n_rounds):
        accs = [np.zeros((pl.out_features, pl.in_features), dtype=np.float64)
                for _, pl in plates]
        for ids, tgt, msk in batches:
            lv, gr = loss_and_grad(model, ids, tgt, msk)
            mx.eval(lv, gr)
            for pidx, (li, pn) in enumerate(plate_paths):
                g = _extract_plate_grad(gr, li, pn)
                mx.eval(g)
                accs[pidx] += np.sign(np.array(g))
            del lv, gr
        nb = len(batches)
        flips = 0
        for pidx, (_, pl) in enumerate(plates):
            conf = np.abs(accs[pidx]) / nb
            ts = np.sign(accs[pidx])
            cur = np.sign(np.array(pl.weight)).astype(np.int8)
            sf = (conf > confidence_threshold) & (ts != 0) & (ts != cur)
            pl.weight = mx.array(np.where(sf, ts, cur).astype(np.float32))
            mx.eval(pl.weight)
            flips += int(sf.sum())
        ev = eval_model(model, np.random.RandomState(999))
        log.append({"round": r + 1, "flips": flips, **ev})
        mx.clear_cache()
    return log


# ══════════════════════════════════════════════════════════════════════
# Oracle (true-task yardstick) — identical to xm_latent train_oracle
# ══════════════════════════════════════════════════════════════════════

def train_oracle(gd_steps, d_model=48, n_layers=3, max_depth=4):
    np.random.seed(42)
    mx.random.seed(42)
    oracle = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(oracle.parameters())
    opt = optim.Adam(learning_rate=0.003)
    lg = nn.value_and_grad(oracle, masked_ce_loss)
    rng = np.random.RandomState(42)
    for step in range(gd_steps):
        ids, tgt, msk = generate_batch(32, rng, max_depth=max_depth)
        lv, gr = lg(oracle, ids, tgt, msk)
        mx.eval(lv, gr)
        oracle.update(opt.apply_gradients(gr, oracle))
        mx.eval(oracle.parameters())
        del lv, gr
        if (step + 1) % 50 == 0:
            mx.clear_cache()
    return oracle


# ══════════════════════════════════════════════════════════════════════
# Per-arm pipeline
# ══════════════════════════════════════════════════════════════════════

def seed_all(seed: int):
    np.random.seed(seed)
    mx.random.seed(seed)


def run_arm(items, arm, K, init_seed, n_probes, gd_steps, n_rounds,
            batch_size=32, lr=0.003, max_depth=4):
    seed_all(init_seed)
    model = HoloModel(d_model=48, n_layers=3)
    mx.eval(model.parameters())

    arm_rng = np.random.RandomState(init_seed + 12345)
    pairs = arm_pairs(items, arm, K, arm_rng)
    batch_rng = np.random.RandomState(init_seed + 999)
    batches = pairs_to_batches(pairs, batch_size, batch_rng)

    etch_log = etch_from_batches(model, batches, n_rounds)

    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()

    opt = optim.Adam(learning_rate=lr)
    lg = nn.value_and_grad(model, masked_ce_loss)
    gd_rng = np.random.RandomState(init_seed + 77)
    npairs = len(pairs)
    gd_log = []
    for step in range(gd_steps):
        pick = gd_rng.randint(0, npairs, size=batch_size)
        ids, tgt, msk = build_batch_from_pairs([pairs[j] for j in pick])
        lv, gr = lg(model, ids, tgt, msk)
        mx.eval(lv, gr)
        model.update(opt.apply_gradients(gr, model))
        mx.eval(model.parameters())
        del lv, gr
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0:
            gd_log.append({"step": step + 1,
                           **eval_model(model, np.random.RandomState(999))})

    final = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
    depth = eval_by_depth(model, np.random.RandomState(999), max_depth=max_depth)
    all_acc = ([e["accuracy"] for e in etch_log]
               + [e["accuracy"] for e in gd_log] + [final["accuracy"]])
    return {
        "arm": arm, "init_seed": init_seed, "n_probes": n_probes,
        "final_acc": final["accuracy"], "best_acc": max(all_acc),
        "depth_acc": {str(d): v["accuracy"] for d, v in depth.items()},
        "n_pairs": npairs, "etch_log": etch_log, "gd_log": gd_log,
    }


# ══════════════════════════════════════════════════════════════════════
# Statistics
# ══════════════════════════════════════════════════════════════════════

def paired_delta(a, b):
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    d = a - b
    n = len(d)
    mean = float(d.mean())
    std = float(d.std(ddof=1)) if n > 1 else 0.0
    se = std / np.sqrt(n) if n > 1 else 0.0
    return {"mean_delta": mean, "std": std,
            "t": float(mean / se) if se > 0 else 0.0,
            "n": n, "wins": int((d > 0).sum()), "per_seed": d.tolist()}


# ══════════════════════════════════════════════════════════════════════
# Stage --gen : Qwen3-4B teacher target cache
# ══════════════════════════════════════════════════════════════════════

def generate_cache(args, out_dir: Path):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    rng = np.random.RandomState(args.gen_seed)
    fs_rng = np.random.RandomState(args.gen_seed + 7)
    fs_bank = make_examples(args.n_fewshot, fs_rng, args.max_depth)
    fewshot = [(e["expr_str"], " ".join(e["gt_toks"])) for e in fs_bank]
    fs_strs = {e["expr_str"] for e in fs_bank}
    exprs = [e for e in make_examples(args.n_exprs + args.n_fewshot, rng,
                                      args.max_depth)
             if e["expr_str"] not in fs_strs][:args.n_exprs]

    dtype = {"float32": torch.float32, "float16": torch.float16,
             "bfloat16": torch.bfloat16}[args.dtype]
    torch.manual_seed(args.gen_seed)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    print(f"  [gen] model loaded {time.time()-t0:.1f}s; "
          f"n_exprs={len(exprs)} K={args.K} temp={args.temp}", flush=True)

    items = []
    n_drop = 0
    for idx, e in enumerate(exprs):
        prompt = to_chat(tok, build_messages(fewshot, e["expr_str"]))
        enc = tok(prompt, return_tensors="pt").to(args.device)
        with torch.no_grad():
            out = model.generate(
                **enc, max_new_tokens=args.max_new_tokens, do_sample=True,
                temperature=args.temp, top_p=args.top_p,
                num_return_sequences=args.K,
                pad_token_id=tok.pad_token_id or tok.eos_token_id)
        plen = enc["input_ids"].shape[1]
        raws = [tok.decode(out[j][plen:], skip_special_tokens=True)
                for j in range(args.K)]
        parsed = []
        for raw in raws:
            ans = extract_answer(raw)
            if ans is None:
                continue
            try:
                parsed.append(canonical(parse_expr(ans)).split())
            except Exception:
                continue
        if not parsed:
            n_drop += 1
            continue
        # pad to K by seeded resample from parsed (keeps equal budget)
        pad_rng = np.random.RandomState(args.gen_seed + idx)
        while len(parsed) < args.K:
            parsed.append(parsed[int(pad_rng.randint(0, len(parsed)))])
        parsed = parsed[:args.K]
        distinct = len({" ".join(s) for s in parsed})
        items.append({
            "inp_toks": e["inp_toks"], "gt_toks": e["gt_canon"].split(),
            "depth": e["depth"], "samples": parsed, "distinct": distinct,
        })
        if (idx + 1) % 25 == 0:
            print(f"    [gen] {idx+1}/{len(exprs)} drop={n_drop} "
                  f"[{time.time()-t0:.0f}s]", flush=True)

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_sha = "unknown"
    cache = {"meta": {
        "run_id": "xm-sampled-teacher-gen",
        "timestamp": datetime.now(UTC).isoformat(), "git_sha": git_sha,
        "model": args.model, "dtype": args.dtype, "temp": args.temp,
        "top_p": args.top_p, "K": args.K, "max_new_tokens": args.max_new_tokens,
        "max_depth": args.max_depth, "gen_seed": args.gen_seed,
        "n_exprs": len(items), "n_dropped": n_drop, "fewshot": fewshot,
        "python": platform.python_version(), "torch": torch.__version__,
    }, "items": items}
    cache_path = out_dir / "etch_cache.json"
    with open(cache_path, "w") as f:
        json.dump(cache, f, default=str)
    md = float(np.mean([it["distinct"] for it in items]))
    print(f"  [gen] saved {len(items)} items (dropped {n_drop}), "
          f"mean distinct={md:.2f} -> {cache_path} "
          f"[{time.time()-t0:.0f}s]", flush=True)
    return cache_path


# ══════════════════════════════════════════════════════════════════════
# --validate (mechanics + within-process bit-repro)
# ══════════════════════════════════════════════════════════════════════

def _synthetic_items(n=40, K=8, seed=0):
    """Build a synthetic multimodal cache WITHOUT Qwen (mechanics check)."""
    rng = np.random.RandomState(seed)
    exprs = make_examples(n, rng, 4)
    items = []
    for e in exprs:
        gt = e["gt_canon"].split()
        samples = [gt]  # one correct mode
        # add distinct wrong modes proportional to depth (mimic Qwen spread)
        for j in range(min(e["depth"], 3)):
            samples.append([*gt, ["a", "b", "c"][j]])  # distinct wrong mode
        while len(samples) < K:
            samples.append(samples[int(rng.randint(0, len(samples)))])
        items.append({"inp_toks": e["inp_toks"], "gt_toks": gt,
                      "depth": e["depth"], "samples": samples[:K],
                      "distinct": len({" ".join(s) for s in samples[:K]})})
    return items


def validate():
    print("=" * 60)
    print("  --validate : sampled-teacher etch mechanics")
    print("=" * 60)
    ok = True
    items = _synthetic_items(40, 8, seed=0)

    # 1. arm budgets equal (K pairs per input)
    for arm in ARMS:
        p = arm_pairs(items, arm, 8, np.random.RandomState(1))
        assert len(p) == 8 * len(items), f"{arm} budget {len(p)}"
    print("  [pass] all arms have equal K-pair budget")

    # 2. xm picks a target at least as close to gt as xm_rand (mean dist)
    xm = arm_pairs(items, "xm", 8, np.random.RandomState(1))
    xr = arm_pairs(items, "xm_rand", 8, np.random.RandomState(1))
    gtmap = {tuple(it["inp_toks"]): it["gt_toks"] for it in items}
    dxm = np.mean([tok_dist(o, gtmap[tuple(i)]) for i, o in xm])
    dxr = np.mean([tok_dist(o, gtmap[tuple(i)]) for i, o in xr])
    assert dxm <= dxr + 1e-9, f"xm dist {dxm} > xm_rand {dxr}"
    print(f"  [pass] xm target-dist {dxm:.3f} <= xm_rand {dxr:.3f}")

    # 3. batch construction shapes + mask sanity
    ids, tgt, msk = build_batch_from_pairs([(items[0]["inp_toks"],
                                             items[0]["gt_toks"])])
    assert ids.shape == (1, MAX_LEN) and tgt.shape == (1, MAX_LEN)
    assert float(msk.sum()) >= 1, "mask must cover output"
    print(f"  [pass] batch shapes ok; mask covers {int(msk.sum().item())} toks")

    # 4. within-process bit-repro of the DISCRETE etch (plate signs).
    # (Continuous eval after Adam is MPS float-nondeterministic — bit-repro
    #  holds only for the sign-vote plates, exactly as xm_latent/xm_reverse.
    #  The graded recovery is handled by >=5 seeds + internal paired deltas.)
    def plate_fp(seed):
        seed_all(seed)
        m = HoloModel(d_model=48, n_layers=3)
        mx.eval(m.parameters())
        br = np.random.RandomState(seed + 999)
        b = pairs_to_batches(arm_pairs(items, "xm", 8,
                             np.random.RandomState(seed + 12345)), 32, br)
        etch_from_batches(m, b, n_rounds=2)
        return np.concatenate([np.sign(np.array(pl.weight)).ravel()
                               for _, pl in _get_plates(m)])
    if not np.array_equal(plate_fp(11), plate_fp(11)):
        ok = False
        print("  [FAIL] etch plate signs not bit-reproducible")
    else:
        print("  [pass] etch plate signs bit-reproducible within process")

    print("=" * 60)
    print("  --validate ALL PASS" if ok else "  --validate FAILED")
    print("=" * 60)
    if not ok:
        raise SystemExit(1)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--gen", action="store_true", help="generate Qwen cache")
    ap.add_argument("--smoke", action="store_true")
    # gen args
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--n-exprs", type=int, default=800)
    ap.add_argument("--K", type=int, default=8)
    ap.add_argument("--temp", type=float, default=1.3)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-new-tokens", type=int, default=32)
    ap.add_argument("--n-fewshot", type=int, default=4)
    ap.add_argument("--max-depth", type=int, default=4)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--gen-seed", type=int, default=1234)
    # etch args
    ap.add_argument("--cache", default="results/xm-sampled-teacher/etch_cache.json")
    ap.add_argument("--gd-steps", type=int, default=3000)
    ap.add_argument("--n-rounds", type=int, default=8)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--checkpoint-dir", default="results/xm-sampled-teacher")
    args = ap.parse_args()

    if args.validate:
        validate()
        return

    out_dir = ROOT / args.checkpoint_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.gen:
        if args.smoke:
            args.n_exprs, args.K = 24, 8
        generate_cache(args, out_dir)
        return

    # ── etch stage ──
    cache_path = ROOT / args.cache
    cache = json.load(open(cache_path))
    items_all = cache["items"]
    K = cache["meta"]["K"]
    probe_counts = [50] if args.smoke else [50, 800]
    n_seeds = 2 if args.smoke else args.seeds
    gd_steps = 200 if args.smoke else args.gd_steps
    n_rounds = 2 if args.smoke else args.n_rounds
    seeds = [3000 + i for i in range(n_seeds)]

    try:
        git_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_sha = "unknown"

    meta = {
        "run_id": f"xm-sampled-teacher-{'smoke' if args.smoke else 'full'}",
        "timestamp": datetime.now(UTC).isoformat(), "git_sha": git_sha,
        "teacher_cache": str(cache_path), "teacher_meta": cache["meta"],
        "d_model": 48, "n_layers": 3, "K": K, "gd_steps": gd_steps,
        "n_rounds": n_rounds,
        "probe_counts": probe_counts, "arms": ARMS, "init_seeds": seeds,
        "preregistered": {
            "G1": "xm > baseline (mode-commit beats blur)",
            "G2": "xm > xm_rand [yardstick, selection]",
            "G3": "(xm-xm_rand) gain depth2-3 > depth1",
            "verdicts": ["SAMPLED-TEACHER-UNBLOCKS", "SELECTION-HELPS-UNSTRUCTURED",
                         "MIXTURE-ARTIFACT", "STILL-BLOCKED"]},
    }
    results = {"meta": meta}

    print("=" * 70)
    print(f"  XM SAMPLED-TEACHER ETCH  ({meta['run_id']})  K={K}")
    print(f"  arms={ARMS} probes={probe_counts} seeds={seeds} "
          f"rounds={n_rounds} gd={gd_steps}")
    print(f"  teacher: {cache['meta']['model']} temp={cache['meta']['temp']} "
          f"({cache['meta']['n_exprs']} exprs cached)")
    print("=" * 70, flush=True)

    print(f"\n  [oracle] training true-task GD teacher ({gd_steps} steps)...",
          flush=True)
    t0 = time.time()
    oracle = train_oracle(gd_steps)
    oe = eval_model(oracle, np.random.RandomState(999))
    od = eval_by_depth(oracle, np.random.RandomState(999))
    print(f"    oracle acc={oe['accuracy']:.1%} ({time.time()-t0:.1f}s)",
          flush=True)
    results["oracle"] = {"acc": oe["accuracy"],
                         "depth_acc": {str(d): v["accuracy"]
                                       for d, v in od.items()}}

    for n_probes in probe_counts:
        items = items_all[:n_probes]
        print(f"\n  probes={n_probes}: {len(items)} exprs", flush=True)
        for arm in ARMS:
            for s in seeds:
                key = f"{arm}_p{n_probes}_s{s}"
                t0 = time.time()
                r = run_arm(items, arm, K, s, n_probes, gd_steps, n_rounds)
                r["seconds"] = time.time() - t0
                results[key] = r
                rec = r["best_acc"] / oe["accuracy"] if oe["accuracy"] else 0
                print(f"    [{key}] acc={r['best_acc']:.1%} "
                      f"({rec*100:.1f}%orc) depth={r['depth_acc']} "
                      f"[{r['seconds']:.0f}s]", flush=True)
                with open(out_dir / "results.json", "w") as f:
                    json.dump(results, f, indent=2, default=str)

    # ── gate scoring ──
    print(f"\n{'═'*70}\n  GATE SCORING (oracle={oe['accuracy']:.1%})")
    scoring = {}
    for n_probes in probe_counts:
        def rec(arm, n_probes=n_probes):
            return [results[f"{arm}_p{n_probes}_s{s}"]["best_acc"]
                    / oe["accuracy"] for s in seeds]

        def depth_rec(arm, d, n_probes=n_probes):
            od_d = results["oracle"]["depth_acc"].get(str(d), 1.0) or 1.0
            return [results[f"{arm}_p{n_probes}_s{s}"]["depth_acc"].get(str(d), 0.0)
                    / od_d for s in seeds]

        g1 = paired_delta(rec("xm"), rec("baseline"))
        g2 = paired_delta(rec("xm"), rec("xm_rand"))
        # G3: (xm-xm_rand) gain in depth 2-3 vs depth 1
        gain_d1 = np.array(depth_rec("xm", 1)) - np.array(depth_rec("xm_rand", 1))
        gain_d2 = np.array(depth_rec("xm", 2)) - np.array(depth_rec("xm_rand", 2))
        gain_d3 = np.array(depth_rec("xm", 3)) - np.array(depth_rec("xm_rand", 3))
        gain_d23 = (gain_d2 + gain_d3) / 2
        g3 = paired_delta(gain_d23.tolist(), gain_d1.tolist())
        scoring[f"p{n_probes}"] = {"G1": g1, "G2": g2, "G3_depth23_vs_1": g3,
                                   "gain_d1_mean": float(gain_d1.mean()),
                                   "gain_d23_mean": float(gain_d23.mean())}
        print(f"\n  probes={n_probes}:")
        print(f"    G1 xm-baseline : Δ={g1['mean_delta']:+.4f} ±{g1['std']:.4f} "
              f"t={g1['t']:+.2f} wins={g1['wins']}/{g1['n']}")
        print(f"    G2 xm-xm_rand  : Δ={g2['mean_delta']:+.4f} ±{g2['std']:.4f} "
              f"t={g2['t']:+.2f} wins={g2['wins']}/{g2['n']}")
        print(f"    G3 gain d23>d1 : Δ={g3['mean_delta']:+.4f} t={g3['t']:+.2f} "
              f"(gain_d1={gain_d1.mean():+.3f} gain_d23={gain_d23.mean():+.3f})")
    results["scoring"] = scoring
    with open(out_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  saved -> {out_dir}/results.json", flush=True)


if __name__ == "__main__":
    main()
