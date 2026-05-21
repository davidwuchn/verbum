"""FFN Circuit Probe — Find the routing and output functions in the FFN.

The FFN has two jobs:
  1. ROUTING: support the K/B/C shared rotation at L1 (store routing result)
  2. OUTPUT:  produce the answer when WHNF fires at L2 (read from store)

Find which FFN dimensions implement each function. Compare teacher vs
Q2-damaged student at those specific dimensions. The divergence points
to exactly which plate positions need fixing.

Protocol:
  1. Run K/I/B/C probes through teacher at each layer
  2. Capture FFN output at:
     a. Combinator token position → routing activation
     b. "=" token position → output activation
  3. Identify:
     - Shared routing dims (high across K/B/C at combinator pos)
     - Output dims (high at "=" pos)
     - WHNF-specific dims (high at "=" but not at combinator)
  4. Compare oracle-student vs Q2-student at those dimensions
  5. The divergence = which plate positions to fix

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/ffn_circuit_probe_exp.py 2>&1 | tee results/ffn-circuit-probe/run.log

License: MIT
"""

from __future__ import annotations

import json, sys, time
from pathlib import Path
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo_d_sweep_v2 import (
    VOCAB_SIZE, PAD_ID, EQ_ID, TOK2ID,
    Comb, Var, App,
    GDModel, HoloModel,
    masked_ce_loss, eval_model,
    generate_batch,
    _get_plates,
)
from mini_holo_crystal import write_crystal_to_model

def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "ffn-circuit-probe"
D_TEACHER = 256; D_STUDENT = 128; N_LAYERS = 3
BATCH_SIZE = 32; LR = 0.003; MAX_DEPTH = 4
COMBINATORS = ["K", "I", "B", "C"]


# ══════════════════════════════════════════════════════════════════════
# Probes
# ══════════════════════════════════════════════════════════════════════

def gen_probes(n=50, seed=42):
    rng = np.random.RandomState(seed)
    vs = ["a","b","c","d","e","x","y","z"]; fs = ["f","g","h","p","q"]
    probes = {}
    for c in COMBINATORS:
        ps = []
        for _ in range(n*5):
            if len(ps) >= n: break
            v1,v2 = Var(rng.choice(vs)),Var(rng.choice(vs))
            f1,f2 = Var(rng.choice(fs)),Var(rng.choice(fs))
            if c=="K": e = App(App(Comb("K"),v1),v2)
            elif c=="I": e = App(Comb("I"),v1)
            elif c=="B": e = App(App(App(Comb("B"),f1),f2),v1)
            elif c=="C": e = App(App(App(Comb("C"),f1),v1),v2)
            t = ["<bos>"] + e.to_tokens() + ["="]
            if not all(x in TOK2ID for x in t): continue
            ids = [TOK2ID[x] for x in t]
            ids = ids[:20] + [PAD_ID]*max(0,20-len(ids))
            ps.append(ids)
        probes[c] = ps[:n]
    return probes


def find_combinator_position(ids):
    comb_ids = {TOK2ID.get(c) for c in ["K","I","B","C"] if c in TOK2ID}
    for i, tok in enumerate(ids):
        if tok in comb_ids: return i
    return 1


def find_eq_position(ids):
    for i, tok in enumerate(ids):
        if tok == EQ_ID: return i
    return len([t for t in ids if t != PAD_ID]) - 1


# ══════════════════════════════════════════════════════════════════════
# FFN activation capture
# ══════════════════════════════════════════════════════════════════════

def capture_ffn_activations(model, input_ids, positions):
    """Run one probe, capture FFN output at specified positions for each layer.

    Returns: dict[layer_idx] → dict[pos_name] → ffn_output vector (d_model,)

    We capture:
      - The FFN output BEFORE residual add (the pure FFN contribution)
      - The attention output BEFORE residual add (the pure attn contribution)
    """
    x = model.embed(mx.array(np.array([input_ids], dtype=np.int32)))
    mx.eval(x)

    layer_activations = {}

    for li, layer in enumerate(model.layers):
        # Attention step
        attn_input = layer.attn_norm(x)
        attn_out = layer.attn(attn_input)
        mx.eval(attn_out)
        h_mid = x + attn_out

        # FFN step — handle both GDModel (layer.ffn) and HoloModel (layer.ffn_plate)
        ffn_input = layer.ffn_norm(h_mid)
        if hasattr(layer, 'ffn'):
            ffn_out = layer.ffn(ffn_input)
        elif hasattr(layer, 'ffn_plate'):
            ffn_out = layer.ffn_plate(ffn_input) * layer.ffn_scale + layer.ffn_bias
        else:
            ffn_out = mx.zeros_like(ffn_input)
        mx.eval(ffn_out)

        # Capture at each position
        layer_acts = {}
        for pos_name, pos_idx in positions.items():
            layer_acts[pos_name] = {
                "ffn": np.array(ffn_out[0, pos_idx, :]).copy(),
                "attn": np.array(attn_out[0, pos_idx, :]).copy(),
            }

        layer_activations[li] = layer_acts
        x = h_mid + ffn_out

    return layer_activations


def measure_ffn_circuits(model, probes, model_name="model"):
    """Measure FFN activation patterns for routing vs output across all probes.

    Returns per-layer, per-combinator, per-position activation profiles.
    """
    log(f"\n  Measuring FFN circuits in {model_name}...")

    # Collect activations: [combinator][layer][position] → list of activation vectors
    d_model = None
    all_acts = {}

    for c in COMBINATORS:
        all_acts[c] = {}
        for probe_ids in probes[c]:
            comb_pos = find_combinator_position(probe_ids)
            eq_pos = find_eq_position(probe_ids)

            positions = {"combinator": comb_pos, "output": eq_pos}
            layer_acts = capture_ffn_activations(model, probe_ids, positions)

            for li in layer_acts:
                if li not in all_acts[c]:
                    all_acts[c][li] = {"combinator": {"ffn": [], "attn": []},
                                       "output": {"ffn": [], "attn": []}}
                for pos_name in ["combinator", "output"]:
                    all_acts[c][li][pos_name]["ffn"].append(
                        layer_acts[li][pos_name]["ffn"])
                    all_acts[c][li][pos_name]["attn"].append(
                        layer_acts[li][pos_name]["attn"])
                if d_model is None:
                    d_model = len(layer_acts[li]["combinator"]["ffn"])

    # Aggregate: mean activation magnitude per dimension
    profiles = {}
    for c in COMBINATORS:
        profiles[c] = {}
        for li in range(N_LAYERS):
            profiles[c][li] = {}
            for pos_name in ["combinator", "output"]:
                ffn_vecs = np.array(all_acts[c][li][pos_name]["ffn"])  # (n_probes, d)
                attn_vecs = np.array(all_acts[c][li][pos_name]["attn"])
                profiles[c][li][pos_name] = {
                    "ffn_mean_mag": np.mean(np.abs(ffn_vecs), axis=0),  # (d,)
                    "ffn_mean_signed": np.mean(ffn_vecs, axis=0),  # (d,)
                    "attn_mean_mag": np.mean(np.abs(attn_vecs), axis=0),
                    "attn_mean_signed": np.mean(attn_vecs, axis=0),
                    "ffn_std": np.std(ffn_vecs, axis=0),
                    "ffn_total_energy": float(np.mean(ffn_vecs ** 2)),
                    "attn_total_energy": float(np.mean(attn_vecs ** 2)),
                }

    return profiles, d_model


# ══════════════════════════════════════════════════════════════════════
# Circuit identification
# ══════════════════════════════════════════════════════════════════════

def identify_circuits(profiles, d_model, top_k=20):
    """Identify routing and output circuits from activation profiles.

    Routing circuit: FFN dims that activate at combinator position across K/B/C
    Output circuit:  FFN dims that activate at "=" position (WHNF)
    """
    results = {}

    for li in range(N_LAYERS):
        # Shared routing activation: mean across K, B, C at combinator position
        kbc_routing = np.mean([
            profiles[c][li]["combinator"]["ffn_mean_mag"]
            for c in ["K", "B", "C"]
        ], axis=0)  # (d,)

        # I routing (for comparison)
        i_routing = profiles["I"][li]["combinator"]["ffn_mean_mag"]

        # Output activation: mean across all combinators at "=" position
        output_act = np.mean([
            profiles[c][li]["output"]["ffn_mean_mag"]
            for c in COMBINATORS
        ], axis=0)  # (d,)

        # Routing-specific dims: high at combinator, relative to output
        routing_specificity = kbc_routing / (output_act + 1e-10)

        # Output-specific dims: high at "=", relative to combinator
        output_specificity = output_act / (kbc_routing + 1e-10)

        # Top-K routing dims
        routing_dims = np.argsort(routing_specificity)[-top_k:]
        output_dims = np.argsort(output_specificity)[-top_k:]

        # Overlap: dims that are both routing and output
        overlap = set(routing_dims) & set(output_dims)

        # Energy comparison
        route_energy = {c: profiles[c][li]["combinator"]["ffn_total_energy"]
                        for c in COMBINATORS}
        output_energy = {c: profiles[c][li]["output"]["ffn_total_energy"]
                         for c in COMBINATORS}

        results[li] = {
            "routing_dims": routing_dims.tolist(),
            "output_dims": output_dims.tolist(),
            "overlap": list(overlap),
            "kbc_routing_mag": kbc_routing,
            "i_routing_mag": i_routing,
            "output_mag": output_act,
            "routing_specificity": routing_specificity,
            "output_specificity": output_specificity,
            "route_energy": route_energy,
            "output_energy": output_energy,
        }

    return results


def compare_circuits(teacher_profiles, oracle_profiles, q2_profiles,
                     circuits, d_teacher, d_student):
    """Compare teacher vs oracle-student vs Q2-student at circuit dimensions.

    Since teacher (d=256) and students (d=128) have different dims,
    we compare the two students directly and use the teacher's circuit
    structure as the reference pattern.
    """
    log("\n  Comparing oracle-student vs Q2-student at circuit dimensions...")

    comparisons = {}
    for li in range(N_LAYERS):
        routing_dims = circuits[li]["routing_dims"]
        output_dims = circuits[li]["output_dims"]

        # Compare oracle vs Q2 at routing dims
        for pos_name, dims, label in [
            ("combinator", routing_dims, "routing"),
            ("output", output_dims, "output"),
        ]:
            oracle_act = np.mean([
                oracle_profiles[c][li][pos_name]["ffn_mean_signed"]
                for c in COMBINATORS
            ], axis=0)

            q2_act = np.mean([
                q2_profiles[c][li][pos_name]["ffn_mean_signed"]
                for c in COMBINATORS
            ], axis=0)

            # Divergence at circuit dims
            if len(dims) > 0:
                oracle_circuit = oracle_act[dims]
                q2_circuit = q2_act[dims]
                divergence = np.abs(oracle_circuit - q2_circuit)
                cos_sim = (np.dot(oracle_circuit, q2_circuit) /
                           (np.linalg.norm(oracle_circuit) *
                            np.linalg.norm(q2_circuit) + 1e-10))

                # Full divergence for comparison
                full_divergence = np.abs(oracle_act - q2_act)

                comparisons[f"L{li}_{label}"] = {
                    "circuit_divergence_mean": float(np.mean(divergence)),
                    "circuit_divergence_max": float(np.max(divergence)),
                    "full_divergence_mean": float(np.mean(full_divergence)),
                    "circuit_cos_sim": float(cos_sim),
                    "circuit_dims_with_sign_flip": int(
                        np.sum(np.sign(oracle_circuit) != np.sign(q2_circuit))),
                    "n_circuit_dims": len(dims),
                    "most_divergent_dims": [
                        int(dims[i]) for i in np.argsort(divergence)[-5:]
                    ],
                }

                log(f"    L{li} {label:7s}: circuit cos_sim={cos_sim:.4f}  "
                    f"div={np.mean(divergence):.4f} (full={np.mean(full_divergence):.4f})  "
                    f"sign_flips={comparisons[f'L{li}_{label}']['circuit_dims_with_sign_flip']}"
                    f"/{len(dims)}")

    return comparisons


# ══════════════════════════════════════════════════════════════════════
# Extraction helpers
# ══════════════════════════════════════════════════════════════════════

def q2_simulate_weights(W, n_bits=2, block_size=32):
    W_flat=W.flatten(); n=len(W_flat)
    pad=(block_size-n%block_size)%block_size
    W_padded=np.concatenate([W_flat,np.zeros(pad)])
    W_blocks=W_padded.reshape(-1,block_size)
    n_levels=2**(n_bits-1)
    scales=np.maximum(np.max(np.abs(W_blocks),axis=1,keepdims=True),1e-10)
    W_norm=W_blocks/scales
    W_quant=np.round(W_norm*n_levels).clip(-n_levels,n_levels)
    W_dequant=(W_quant/n_levels)*scales
    signs=np.sign(W_dequant.flatten()[:n].reshape(W.shape)).astype(np.float32)
    zeros=signs==0
    if zeros.any(): signs[zeros]=np.random.RandomState(42).choice([-1.,1.],size=int(zeros.sum()))
    return signs

def extract_oracle_crystal(teacher, ds):
    crystal=[]
    for layer in teacher.layers:
        ls={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]; W_proj=P@W@P.T
            signs=np.sign(W_proj).astype(np.float32)
            zeros=signs==0
            if zeros.any(): signs[zeros]=np.random.RandomState(42).choice([-1.,1.],size=int(zeros.sum()))
            ls[nm]=signs
        crystal.append(ls)
    return crystal

def extract_q2_crystal(teacher, ds, n_bits=2):
    crystal=[]
    for layer in teacher.layers:
        ls={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]; W_proj=P@W@P.T
            ls[nm]=q2_simulate_weights(W_proj,n_bits=n_bits)
        crystal.append(ls)
    return crystal

def extract_mag(teacher, ds):
    t=[]
    for layer in teacher.layers:
        lm={}
        for nm,proj in [("k",layer.attn.k_proj),("v",layer.attn.v_proj),
                        ("o",layer.attn.o_proj),("ffn",layer.ffn)]:
            W=np.array(proj.weight); _,S,Vt=np.linalg.svd(W,full_matrices=False)
            P=Vt[:ds,:]
            lm[nm]=np.sqrt(np.mean((P@W@P.T)**2,axis=1)).astype(np.float32)
        t.append(lm)
    return t

def make_model(crystal, mag):
    m=HoloModel(d_model=D_STUDENT,n_layers=N_LAYERS); mx.eval(m.parameters())
    write_crystal_to_model(m,crystal)
    for i,l in enumerate(m.layers):
        l.attn.k_scale=mx.array(mag[i]["k"]); l.attn.v_scale=mx.array(mag[i]["v"])
        l.attn.o_scale=mx.array(mag[i]["o"]); l.ffn_scale=mx.array(mag[i]["ffn"])
    mx.eval(m.parameters()); return m

def train_teacher(d, n=5000):
    m=GDModel(d_model=d,n_layers=N_LAYERS); mx.eval(m.parameters())
    opt=optim.Adam(learning_rate=LR); lag=nn.value_and_grad(m,masked_ce_loss)
    rng=np.random.RandomState(42)
    for s in range(n):
        ids,tgt,msk=generate_batch(BATCH_SIZE,rng,max_depth=MAX_DEPTH)
        lv,gr=lag(m,ids,tgt,msk); mx.eval(lv,gr)
        m.update(opt.apply_gradients(gr,m)); mx.eval(m.parameters()); del lv,gr
        if (s+1)%100==0: mx.clear_cache()
        if (s+1)%1000==0:
            ev=eval_model(m,np.random.RandomState(999),max_depth=MAX_DEPTH)
            log(f"    Step {s+1}: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}")
    ev=eval_model(m,np.random.RandomState(999),max_depth=MAX_DEPTH)
    log(f"  Final: loss={ev['loss']:.4f}, acc={ev['accuracy']:.4f}"); return m


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # Train teacher
    log(f"{'═'*60}")
    log(f"Training teacher d={D_TEACHER}...")
    teacher = train_teacher(D_TEACHER, 5000)

    # Generate probes
    probes = gen_probes(n=50)

    # Extract crystals
    oracle_crystal = extract_oracle_crystal(teacher, D_STUDENT)
    q2_crystal = extract_q2_crystal(teacher, D_STUDENT, n_bits=2)
    mag = extract_mag(teacher, D_STUDENT)

    from mini_holo_crystal import crystal_similarity
    q2_sim = crystal_similarity(oracle_crystal, q2_crystal)
    log(f"  Q2 sign agreement with oracle: {q2_sim:.4f}")

    # ══════════════════════════════════════════════════════════════
    # Measure FFN circuits in teacher
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    teacher_profiles, d_t = measure_ffn_circuits(teacher, probes, "teacher")

    # Print energy comparison: routing vs output
    log(f"\n  Teacher FFN energy: routing (combinator pos) vs output (= pos)")
    log(f"  {'Comb':>4s}  {'Layer':>5s}  {'Route FFN':>10s}  {'Output FFN':>10s}  "
        f"{'Route Attn':>10s}  {'Output Attn':>10s}  {'Ratio':>6s}")
    for c in COMBINATORS:
        for li in range(N_LAYERS):
            re = teacher_profiles[c][li]["combinator"]["ffn_total_energy"]
            oe = teacher_profiles[c][li]["output"]["ffn_total_energy"]
            ra = teacher_profiles[c][li]["combinator"]["attn_total_energy"]
            oa = teacher_profiles[c][li]["output"]["attn_total_energy"]
            ratio = oe / max(re, 1e-10)
            log(f"  {c:>4s}  L{li:>4d}  {re:10.4f}  {oe:10.4f}  "
                f"{ra:10.4f}  {oa:10.4f}  {ratio:5.1f}×")
        log("")

    # Identify circuits
    log(f"{'═'*60}")
    log("Identifying routing and output circuits...")
    teacher_circuits = identify_circuits(teacher_profiles, d_t, top_k=20)

    for li in range(N_LAYERS):
        c = teacher_circuits[li]
        log(f"\n  Layer {li}:")
        log(f"    Routing dims (top-20): {sorted(c['routing_dims'][:10])}...")
        log(f"    Output dims  (top-20): {sorted(c['output_dims'][:10])}...")
        log(f"    Overlap: {len(c['overlap'])} dims shared")

        # Energy at circuit dims
        route_at_route = np.mean(c['kbc_routing_mag'][c['routing_dims']])
        route_at_output = np.mean(c['output_mag'][c['routing_dims']])
        output_at_output = np.mean(c['output_mag'][c['output_dims']])
        output_at_route = np.mean(c['kbc_routing_mag'][c['output_dims']])

        log(f"    Routing dims: route_mag={route_at_route:.4f} output_mag={route_at_output:.4f}")
        log(f"    Output dims:  route_mag={output_at_route:.4f} output_mag={output_at_output:.4f}")

        # I vs K/B/C at routing dims
        i_at_route = np.mean(c['i_routing_mag'][c['routing_dims']])
        log(f"    I at routing dims: {i_at_route:.4f} (K/B/C: {route_at_route:.4f}) "
            f"{'← I differs!' if abs(i_at_route - route_at_route) / max(route_at_route, 1e-10) > 0.3 else ''}")

    # ══════════════════════════════════════════════════════════════
    # Compare oracle-student vs Q2-student at circuit dimensions
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("Building oracle and Q2 student models...")

    oracle_model = make_model(oracle_crystal, mag)
    q2_model = make_model(q2_crystal, mag)

    oracle_profiles, d_s = measure_ffn_circuits(oracle_model, probes, "oracle-student")
    q2_profiles, _ = measure_ffn_circuits(q2_model, probes, "q2-student")

    # Use oracle circuits for student comparison (same d_model)
    student_circuits = identify_circuits(oracle_profiles, d_s, top_k=20)
    comparisons = compare_circuits(
        teacher_profiles, oracle_profiles, q2_profiles,
        student_circuits, d_t, d_s)

    # ══════════════════════════════════════════════════════════════
    # Key findings
    # ══════════════════════════════════════════════════════════════
    log(f"\n{'═'*60}")
    log("KEY FINDINGS:")

    # Is FFN more active at output than routing?
    for li in range(N_LAYERS):
        route_e = np.mean([teacher_profiles[c][li]["combinator"]["ffn_total_energy"]
                           for c in ["K","B","C"]])
        output_e = np.mean([teacher_profiles[c][li]["output"]["ffn_total_energy"]
                            for c in COMBINATORS])
        log(f"  L{li} FFN energy: routing={route_e:.4f} output={output_e:.4f} "
            f"ratio={output_e/max(route_e,1e-10):.1f}× "
            f"{'← FFN activates for output!' if output_e > route_e * 1.5 else ''}")

    # Where does Q2 damage concentrate?
    log(f"\n  Q2 damage concentration in circuits:")
    for key in sorted(comparisons.keys()):
        c = comparisons[key]
        log(f"    {key}: circuit_div={c['circuit_divergence_mean']:.4f} "
            f"full_div={c['full_divergence_mean']:.4f} "
            f"cos_sim={c['circuit_cos_sim']:.4f} "
            f"sign_flips={c['circuit_dims_with_sign_flip']}/{c['n_circuit_dims']}")

    # Save
    elapsed = time.time() - t_start

    save_results = {
        "comparisons": comparisons,
        "teacher_circuits": {
            li: {
                "routing_dims": teacher_circuits[li]["routing_dims"],
                "output_dims": teacher_circuits[li]["output_dims"],
                "overlap": teacher_circuits[li]["overlap"],
                "route_energy": teacher_circuits[li]["route_energy"],
                "output_energy": teacher_circuits[li]["output_energy"],
            }
            for li in range(N_LAYERS)
        },
        "meta": {"elapsed_seconds": elapsed, "d_teacher": D_TEACHER,
                 "d_student": D_STUDENT},
    }

    out_path = RESULTS_DIR / "results.json"
    with open(out_path, "w") as f:
        json.dump(save_results, f, indent=2)

    log(f"\n{'═'*60}")
    log(f"Results saved to {out_path} ({elapsed:.0f}s)")

    del teacher, oracle_model, q2_model
    mx.clear_cache()


if __name__ == "__main__":
    main()
