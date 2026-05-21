"""Quick activation-space distillation test — 50 steps.

Tests whether Procrustes-aligned teacher hidden states can guide
student training. Measures cosine similarity before and after.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/distill_v6_quick.py

License: MIT
"""
import numpy as np, json, sys, time
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent.parent / "src"))
from sklearn.utils.extmath import randomized_svd
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from verbum.v6.model import VSMLMV6

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)

# ── Load teacher features ──
log("Loading teacher features...")
with open("checkpoints/teacher-features-14b/manifest.json") as f:
    manifest = json.load(f)

teacher_means = {}
for depth in manifest["depth_indices"]:
    data = np.load(f"checkpoints/teacher-features-14b/layer_{depth:03d}_outputs.npz")
    teacher_means[depth] = np.stack([data[k].mean(axis=0) for k in sorted(data.keys())])

# ── Teacher PCA ──
# n_components <= n_probes - 1 (centered data has rank n-1)
N_PROBES = len(teacher_means[manifest["depth_indices"][0]])
K_REDUCE = min(512, N_PROBES - 1)  # 199 for 200 probes
log(f"Computing teacher PCA projections (k={K_REDUCE})...")

teacher_reduced = {}  # depth → (n_probes, K_REDUCE) float32
teacher_Vt = {}       # depth → (K_REDUCE, d_teacher) projection
for depth in manifest["depth_indices"]:
    T = teacher_means[depth]
    T_c = T - T.mean(axis=0, keepdims=True)
    _, _, Vt = randomized_svd(T_c, n_components=K_REDUCE, n_iter=4, random_state=42)
    teacher_reduced[depth] = (T_c @ Vt[:K_REDUCE, :].T).astype(np.float32)
    teacher_Vt[depth] = Vt[:K_REDUCE, :]

# ── Load student model ──
log("Loading student model...")
with open("checkpoints/vsm-lm-v6/step_032500/meta.json") as f:
    meta = json.load(f)
config = meta["config"]
model = VSMLMV6(
    vocab_size=config["vocab_size"], d_model=config["d_model"],
    d_register=config["d_register"], max_len=config["seq_len"],
    n_heads=config["n_heads"], d_ff=config["d_ff"],
    d_ff_consolidate=config["d_ff_consolidate"], window=config["window"],
    strides=tuple(config["strides"]),
)
weights = mx.load("checkpoints/vsm-lm-v6/step_032500/weights.safetensors")
model.load_weights(list(weights.items()))
mx.eval(model.parameters())

# ── Tokenize probes ──
log("Tokenizing probes...")
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-410m")
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

with open("lattice/diverse_corpus.json") as f:
    corpus = json.load(f)
probe_texts = []
for item in corpus:
    if isinstance(item, dict):
        probe_texts.append(item.get("text") or item.get("prompt") or item.get("input") or "")
    else:
        probe_texts.append(str(item))
probe_texts = probe_texts[:200]

enc = tokenizer(probe_texts, padding=True, truncation=True, max_length=40, return_tensors="np")
# Keep as numpy — we'll slice with numpy then convert to mx per batch
all_ids_np = enc["input_ids"]  # (200, seq_len) numpy
n_train, n_eval = 150, 50

DEPTHS = [8, 16, 24, 32, 40]

# ── Pad teacher targets to 512D ──
# Teacher PCA gives K_REDUCE dims. Pad to 512 so shapes match student.
# The extra dims are zero — loss only backprops through the K_REDUCE active dims.
log(f"Padding teacher targets from {K_REDUCE} to 512...")
teacher_padded = {}
for depth in manifest["depth_indices"]:
    T = teacher_reduced[depth]  # (n_probes, K_REDUCE)
    padded = np.zeros((T.shape[0], 512), dtype=np.float32)
    padded[:, :K_REDUCE] = T
    teacher_padded[depth] = padded

# ── Model forward capturing per-pass states ──
def get_pass_states(model, input_ids):
    """Run input through v6, return mean-pooled hidden states per pass."""
    B, L = input_ids.shape
    positions = mx.arange(L)
    x = model.embed_norm(model.token_embed(input_ids) + model.pos_embed(positions))
    bank_0 = model._init_bank0()
    banks = [model._fresh_bank() for _ in range(5)]
    states = []
    x, banks[0], _, _ = model._run_level_pass(x, 0, False, [bank_0], banks[0])
    states.append(mx.mean(x, axis=1))
    x, banks[1], _, _ = model._run_level_pass(x, 1, False, [bank_0, banks[0]], banks[1])
    states.append(mx.mean(x, axis=1))
    x, banks[2], _, _ = model._run_level_pass(x, 2, False, [bank_0, banks[0], banks[1]], banks[2])
    states.append(mx.mean(x, axis=1))
    x, banks[3], _, _ = model._run_level_pass(x, 3, True, [bank_0, banks[0], banks[1], banks[2]], banks[3])
    states.append(mx.mean(x, axis=1))
    x, banks[4], _, _ = model._run_level_pass(x, 4, True,
        [bank_0, banks[0], banks[1], banks[2], banks[3]], banks[4])
    states.append(mx.mean(x, axis=1))
    return states

# ── Distillation loss ──
def distill_loss(model, input_ids, target_list):
    states = get_pass_states(model, input_ids)
    total = mx.array(0.0)
    for i in range(5):
        diff = states[i] - target_list[i]  # both (B, 512)
        total = total + mx.mean(diff * diff)
    return total / 5.0

# ── Procrustes alignment measurement ──
def measure_alignment(model, all_ids_np, teacher_reduced):
    """Measure cosine similarity between Procrustes-aligned student and teacher."""
    input_ids = mx.array(all_ids_np)
    states = get_pass_states(model, input_ids)
    results = {}
    for i, depth in enumerate(DEPTHS):
        S = np.array(states[i])
        T_red = teacher_reduced[depth]
        S_c = S - S.mean(axis=0, keepdims=True)
        T_c = T_red - T_red.mean(axis=0, keepdims=True)
        M = S_c.T @ T_c
        Um, _, Vtm = np.linalg.svd(M, full_matrices=False)
        R = Um @ Vtm
        S_al = S_c @ R
        s_n = np.linalg.norm(S_al, axis=1, keepdims=True) + 1e-8
        t_n = np.linalg.norm(T_c, axis=1, keepdims=True) + 1e-8
        cos = np.sum((S_al / s_n) * (T_c / t_n), axis=1)
        results[depth] = float(cos.mean())
    return results

# ── Pre-training measurement ──
log("\nPre-training alignment:")
pre_align = measure_alignment(model, all_ids_np, teacher_reduced)
for depth, cos in pre_align.items():
    log(f"  Depth {depth}: cos={cos:.3f}")

# ── Training loop ──
log(f"\nDistillation training (50 steps, batch=30)...")
opt = optim.Adam(learning_rate=1e-4)
loss_grad = nn.value_and_grad(model, distill_loss)
rng = np.random.RandomState(42)

t0 = time.time()
for step in range(50):
    # Sample batch indices with numpy, slice numpy arrays, then convert
    idx = rng.choice(n_train, size=30, replace=False)
    batch_np = all_ids_np[idx]  # numpy slice
    batch = mx.array(batch_np)
    targets = [mx.array(teacher_padded[d][idx]) for d in DEPTHS]

    lv, gr = loss_grad(model, batch, targets)
    mx.eval(lv, gr)
    model.update(opt.apply_gradients(gr, model))
    mx.eval(model.parameters())
    del gr

    if (step + 1) % 10 == 0:
        # Eval on held-out
        eval_np = all_ids_np[n_train:n_train + n_eval]
        eval_batch = mx.array(eval_np)
        eval_targets = [mx.array(teacher_padded[d][n_train:n_train + n_eval]) for d in DEPTHS]
        eval_states = get_pass_states(model, eval_batch)
        eval_mse = 0
        for i in range(5):
            diff = eval_states[i] - eval_targets[i]
            eval_mse += float(mx.mean(diff * diff).item())
        eval_mse /= 5.0
        log(f"  Step {step+1}: train={lv.item():.6f} eval={eval_mse:.6f}")
        mx.clear_cache()

dt = time.time() - t0
log(f"  Training: {dt:.1f}s")

# ── Post-training measurement ──
log("\nPost-training alignment:")
post_align = measure_alignment(model, all_ids_np, teacher_reduced)
for depth, cos in post_align.items():
    log(f"  Depth {depth}: cos={cos:.3f}")

# ── Summary ──
log(f"\n{'='*60}")
log(f"  {'Depth':>5s}  {'Before':>8s}  {'After':>8s}  {'Delta':>8s}")
log(f"  {'-'*5}  {'-'*8}  {'-'*8}  {'-'*8}")
for depth in DEPTHS:
    pre = pre_align[depth]
    post = post_align[depth]
    delta = post - pre
    log(f"  {depth:5d}  {pre:8.3f}  {post:8.3f}  {delta:+8.3f}")
log(f"{'='*60}")
