"""
v10 — Training Script

Self-similar compressor + tree of shared-weight VSM nodes, trained with:
  • Cross-entropy on per-node op classification (tree-aware loss)
  • Ternary topology evolved via tournament selection (gradient-informed)
  • Adam on continuous parameters (gamma, norms, VSMNode weights)
  • Cosine LR with linear warmup

Architecture synopsis:
  tokens → [SelfSimilarCompressor] → h (B, L, d_model)
  For each example in batch:
    tree traversal bottom-up through shared VSMNode
    each internal node: VSMNode(context=h[b,pos], child_vals, child_types) → op_logits
  CE loss over all internal node logits vs ground-truth op labels

Evolution loop (every gen_interval steps):
  champion topology saved → 4 mutant strategies evaluated on held-out batch
  → tournament select → accept if loss improves, else restore champion

Usage:
    uv run python scripts/v10/train.py
    uv run python scripts/v10/train.py --total-steps 5000 --d-model 128
    uv run python scripts/v10/train.py --seq-len 128 --batch-size 64
    uv run python scripts/v10/train.py --resume --checkpoint-dir checkpoints/v10

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

# ── Self-contained: only imports from scripts/v10/ ───────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import generate_batch, InfiniteDataLoader, Batch, SExprTree, SExprNode
from kernel import evaluate_tree as kernel_evaluate_tree, Node as KernelNode
from model import V10Model, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    bios_mutation_budget,
    save_topology,
    load_topology,
    mutate_topology,
    _walk_ternary_modules,
    TernaryLinear,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Batch preparation — extract tree info and token positions
# ══════════════════════════════════════════════════════════════════════════════

def _token_positions_for_tree(tree: SExprTree) -> list[int]:
    """
    Compute the token sequence position of each tree node (DFS pre-order).

    The S-expression tokenizer produces tokens by a simple left-to-right
    scan of the source string.  The tree nodes are in DFS pre-order, and
    each compound node starts with '(' then its operator token.

    We recover positions by re-scanning the token stream in DFS pre-order:
      • Compound node: consumes '(' at current cursor, then operator token
                       — the operator sits at cursor+1.
      • Leaf node:     consumes one token at the current cursor.

    Returns a list of length len(tree.nodes) where entry i gives the
    0-based position of node i's *representative token* in the flat token
    sequence (the operator token for compound nodes, the literal token for
    leaves).
    """
    n = len(tree.nodes)
    positions: list[int] = [0] * n

    cursor = [0]  # mutable via list so nested function can mutate

    def _walk(node_idx: int) -> None:
        node = tree.nodes[node_idx]
        if node.is_leaf:
            positions[node_idx] = cursor[0]
            cursor[0] += 1
        else:
            # '(' at cursor[0], operator at cursor[0]+1
            positions[node_idx] = cursor[0] + 1   # operator token
            cursor[0] += 2                          # skip '(' and operator
            for child_idx in node.children:
                _walk(child_idx)
            cursor[0] += 1                          # skip ')'

    _walk(tree.root)
    return positions


# Type alias for the per-example tree info passed to loss_fn / evaluate.
# Each entry is (tree_nodes, node_positions, op_labels_per_node) where:
#   tree_nodes        — list[SExprNode] in DFS pre-order
#   node_positions    — list[int] token positions (one per node)
#   op_labels_per_node — list[int] ground-truth op idx (one per node; -1 for leaves)
ExampleTreeInfo = tuple[list[SExprNode], list[int], list[int]]


def prepare_batch(
    batch: Batch,
    cfg: V10Config,
) -> tuple[mx.array, list[ExampleTreeInfo]]:
    """
    Convert a raw Batch into MLX token tensor + per-example tree info.

    Returns
    -------
    tokens          (B, L)  int32  — padded token sequences (to cfg.max_seq_len)
    batch_tree_info list[ExampleTreeInfo] — per-example tree structure
    """
    # ── Token ids (pad to cfg.max_seq_len) ──────────────────────────────────
    # batch.token_ids is already padded by data.py to max_seq_len at generation
    # time, but we may have overridden seq_len via CLI, so re-pad here.
    B, raw_L = batch.token_ids.shape
    L = cfg.max_seq_len
    if raw_L < L:
        # Pad with zeros (PAD_ID=0)
        padded = np.zeros((B, L), dtype=np.int32)
        padded[:, :raw_L] = batch.token_ids
        tokens_np = padded
    else:
        tokens_np = batch.token_ids[:, :L]
    tokens = mx.array(tokens_np, dtype=mx.int32)

    # ── Per-example tree info ────────────────────────────────────────────────
    batch_tree_info: list[ExampleTreeInfo] = []
    for ex in batch.examples:
        tree = ex.tree
        tok_positions = _token_positions_for_tree(tree)

        # Clamp positions to valid range
        clamped_positions = [
            min(pos, cfg.max_seq_len - 1) for pos in tok_positions
        ]

        op_labels_per_node: list[int] = [
            node.op_idx for node in tree.nodes  # -1 for leaves
        ]

        batch_tree_info.append((tree.nodes, clamped_positions, op_labels_per_node))

    return tokens, batch_tree_info


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Loss function — tree-aware, stays in MLX computation graph
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(
    model: V10Model,
    tokens: mx.array,
    batch_tree_info: list[ExampleTreeInfo],
) -> mx.array:
    """
    Cross-entropy loss on per-node op classification via tree traversal.

    The model processes each example sequentially (trees are ragged).
    All VSMNode forward passes remain inside the MLX computation graph
    so gradients flow back to both the compressor AND the vsm_node weights.

    Algorithm per example:
      1. Get compressed context: h[b] = compressed[b]  (L, d_model)
      2. Walk tree bottom-up (reverse DFS pre-order = reverse index order)
         - Leaves: cache their literal value and type
         - Internal nodes:
             • Call model.vsm_node(context, child_vals, child_types) directly.
               VSMNode accepts (*, d_model) inputs; passing 1D tensors is fine
               and avoids the reshape(1,-1)/[0] round-trip that confuses MLX's
               gradient tracer when stacking gradients across multiple calls.
             • Compute CE vs ground-truth op label; append to all_ce list.
             • Run pure-Python kernel (detached) to propagate value/type.
      3. Stack all CE scalars; return their mean.
    """
    from kernel import kernel_eval

    # ── Step 1: compress the full batch ─────────────────────────────────────
    h = model.compress(tokens)   # (B, L, d_model)

    B = len(batch_tree_info)
    all_ce: list[mx.array] = []

    for b in range(B):
        tree_nodes, node_positions, op_labels_per_node = batch_tree_info[b]
        n_nodes = len(tree_nodes)

        # Storage for computed values and types (plain Python — not in graph)
        values: list[float] = [0.0] * n_nodes
        types: list[int] = [0] * n_nodes   # 0 = INT

        # Process in reverse DFS pre-order so children come before parents.
        # (DFS pre-order: root first, children after → reverse gives leaves first)
        for i in range(n_nodes - 1, -1, -1):
            node = tree_nodes[i]

            if node.is_leaf:
                # Propagate literal value and type upward
                if node.value is None:
                    values[i] = 0.0
                    types[i] = 0
                elif isinstance(node.value, bool):
                    values[i] = float(int(node.value))
                    types[i] = 1   # BOOL
                else:
                    values[i] = float(node.value)
                    types[i] = 0   # INT
                continue

            # ── Internal node ──────────────────────────────────────────────
            children = node.children  # list of node indices

            # Build child value/type arrays (pad to max_children=3)
            child_vals_list = [0.0] * 3
            child_typs_list = [0] * 3
            for ci, child_idx in enumerate(children[:3]):
                child_vals_list[ci] = values[child_idx]
                child_typs_list[ci] = types[child_idx]

            # Shape: (3,) — VSMNode handles (*, d_model) / (*, max_children)
            child_vals = mx.array(child_vals_list, dtype=mx.float32)
            child_typs = mx.array(child_typs_list, dtype=mx.int32)

            # Context from compressor at this node's token position  →  (d_model,)
            pos = node_positions[i]
            context = h[b, pos]

            # VSMNode forward — call the module directly to stay in the graph.
            # Passing 1D arrays: context=(d_model,), child_vals=(3,), child_typs=(3,).
            # The (*, ...) semantics in VSMNode work correctly with 1D inputs.
            logits = model.vsm_node(context, child_vals, child_typs)  # (n_ops,)

            # Ground-truth label → CE loss
            gt_op = op_labels_per_node[i]
            if gt_op >= 0:
                label = mx.array([gt_op], dtype=mx.int32)   # (1,)
                ce = nn.losses.cross_entropy(
                    logits.reshape(1, -1), label, reduction="none"
                )  # (1,)
                all_ce.append(ce[0])

            # Propagate value/type for child→parent chain.
            # mx.eval here detaches the scalar from the graph — intentional,
            # since the kernel result is only needed as a Python float for the
            # next node's child_vals, not for gradient computation.
            mx.eval(logits)
            pred_op_idx = int(mx.argmax(logits).item())

            try:
                result_val, _aux, result_type = kernel_eval(
                    pred_op_idx,
                    [int(v) for v in [values[ci] for ci in children]],
                    [0] * len(children),
                    [types[ci] for ci in children],
                )
                values[i] = float(result_val)
                types[i] = result_type
            except Exception:
                values[i] = 0.0
                types[i] = 4   # ERROR

    if not all_ce:
        # Degenerate batch (all leaves) — return zero loss
        return mx.array(0.0)

    # Mean CE over all internal nodes across the batch
    return mx.mean(mx.stack(all_ce))


# ══════════════════════════════════════════════════════════════════════════════
# § 3  LR schedule
# ══════════════════════════════════════════════════════════════════════════════

def cosine_lr(
    step: int,
    warmup_steps: int,
    total_steps: int,
    lr_max: float,
    lr_floor_ratio: float = 0.01,
) -> float:
    """Cosine annealing with linear warmup and a non-zero floor."""
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


# ══════════════════════════════════════════════════════════════════════════════
# § 4  Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def evaluate(
    model: V10Model,
    cfg: V10Config,
    rng_seed: int = 9999,
) -> dict[str, float]:
    """
    Evaluate op-classification accuracy and result accuracy on a fresh batch.

    Metrics
    -------
    op_acc      fraction of internal nodes where argmax(logits) == ground truth
    result_acc  fraction of examples where predicted ops → kernel gives correct result
    loss        tree-aware CE loss (same formula as training)
    """
    import random
    rng = random.Random(rng_seed)
    eval_batch = generate_batch(
        rng=rng,
        batch_size=cfg.n_eval,
        max_seq_len=cfg.max_seq_len,
        max_depth=cfg.max_depth,
        max_value=cfg.max_value,
    )
    tokens, batch_tree_info = prepare_batch(eval_batch, cfg)

    # ── Compress once ──────────────────────────────────────────────────────
    h = model.compress(tokens)   # (B, L, d_model)
    mx.eval(h)

    # ── Op accuracy + predicted ops collection ─────────────────────────────
    total_ops_correct = 0
    total_ops = 0

    # Per-example predicted op assignments (node_idx → pred_op)
    all_pred_op_assignments: list[dict[int, int]] = []

    B = len(batch_tree_info)
    for b in range(B):
        tree_nodes, node_positions, op_labels_per_node = batch_tree_info[b]
        n_nodes = len(tree_nodes)

        values: list[float] = [0.0] * n_nodes
        types: list[int] = [0] * n_nodes
        pred_op_assignments: dict[int, int] = {}

        for i in range(n_nodes - 1, -1, -1):
            node = tree_nodes[i]

            if node.is_leaf:
                if node.value is None:
                    values[i] = 0.0; types[i] = 0
                elif isinstance(node.value, bool):
                    values[i] = float(int(node.value)); types[i] = 1
                else:
                    values[i] = float(node.value); types[i] = 0
                continue

            children = node.children
            child_vals_list = [0.0] * 3
            child_typs_list = [0] * 3
            for ci, child_idx in enumerate(children[:3]):
                child_vals_list[ci] = values[child_idx]
                child_typs_list[ci] = types[child_idx]

            child_vals = mx.array(child_vals_list, dtype=mx.float32)
            child_typs = mx.array(child_typs_list, dtype=mx.int32)
            pos = node_positions[i]
            context = h[b, pos]   # (d_model,)

            # Call vsm_node directly with 1D inputs (same as loss_fn)
            logits = model.vsm_node(context, child_vals, child_typs)  # (n_ops,)
            mx.eval(logits)

            pred_op = int(mx.argmax(logits).item())
            pred_op_assignments[i] = pred_op

            gt_op = op_labels_per_node[i]
            if gt_op >= 0:
                total_ops += 1
                if pred_op == gt_op:
                    total_ops_correct += 1

            # Propagate kernel value
            from kernel import kernel_eval
            try:
                child_val_list = [values[ci] for ci in children]
                child_aux_list = [0] * len(children)
                child_type_list = [types[ci] for ci in children]
                result_val, _aux, result_type = kernel_eval(
                    pred_op,
                    [int(v) for v in child_val_list],
                    child_aux_list,
                    child_type_list,
                )
                values[i] = float(result_val)
                types[i] = result_type
            except Exception:
                values[i] = 0.0; types[i] = 4

        all_pred_op_assignments.append(pred_op_assignments)

    op_acc = total_ops_correct / max(total_ops, 1)

    # ── Result accuracy (kernel re-evaluation with predicted ops) ──────────
    result_correct = 0
    result_total = 0

    for b, ex in enumerate(eval_batch.examples):
        tree = ex.tree
        pred_op_assignments = all_pred_op_assignments[b]

        # Build kernel Node list in post-order (children before parents)
        kernel_nodes_map: dict[int, KernelNode] = {}
        for node_idx, node in enumerate(tree.nodes):
            if node.is_leaf:
                v = node.value
                int_val = int(v) if isinstance(v, bool) else (v if v is not None else 0)
                kernel_nodes_map[node_idx] = KernelNode(
                    node_id=node_idx,
                    children=[],
                    value=int_val,
                )
            else:
                kernel_nodes_map[node_idx] = KernelNode(
                    node_id=node_idx,
                    children=list(node.children),
                    value=0,
                )

        # Topological post-order traversal
        ordered: list[KernelNode] = []
        visited: set[int] = set()

        def _postorder(nid: int) -> None:
            if nid in visited:
                return
            visited.add(nid)
            for cid in kernel_nodes_map[nid].children:
                _postorder(cid)
            ordered.append(kernel_nodes_map[nid])

        _postorder(tree.root)

        # Op assignments: use predicted where available, fall back to ground truth
        op_assignments: dict[int, int] = {}
        for node_idx, node in enumerate(tree.nodes):
            if not node.is_leaf:
                if node_idx in pred_op_assignments:
                    op_assignments[node_idx] = pred_op_assignments[node_idx]
                elif node.op_idx >= 0:
                    op_assignments[node_idx] = node.op_idx

        try:
            predicted_result = kernel_evaluate_tree(ordered, op_assignments)
            ground_truth = int(ex.result) if isinstance(ex.result, bool) else ex.result
            if predicted_result == ground_truth:
                result_correct += 1
        except Exception:
            pass
        result_total += 1

    result_acc = result_correct / max(result_total, 1)

    # ── Loss ──────────────────────────────────────────────────────────────
    loss_val = loss_fn(model, tokens, batch_tree_info)
    mx.eval(loss_val)
    loss_f = float(loss_val.item())

    return {
        "op_acc": op_acc,
        "result_acc": result_acc,
        "loss": loss_f,
    }


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Tournament evolution
# ══════════════════════════════════════════════════════════════════════════════

# Four mutant strategies (scale factors relative to the base budget)
MUTANT_STRATEGIES = {
    "conservative": 0.25,
    "explorer":     1.0,
    "targeted":     2.0,
    "random":       4.0,
}


def run_tournament(
    model: V10Model,
    cfg: V10Config,
    step: int,
    total_ternary: int,
    eval_batch: Batch,
    base_pct: float,
    rng: np.random.RandomState,
    row_importance: dict[str, np.ndarray],
    col_importance: dict[str, np.ndarray],
    grad_direction: dict[str, np.ndarray],
) -> dict:
    """
    One evolutionary generation: mutate → evaluate → tournament select.

    1. Save champion topology.
    2. Compute base mutation budget (bios_mutation_budget, phase-aware).
    3. For each of 4 strategies: mutate from champion, eval on eval_batch.
    4. Accept best mutant if it lowers eval loss; else restore champion.
    5. Return stats dict.
    """
    # Pre-prepare eval tensors once (same batch for all candidates)
    tokens, batch_tree_info = prepare_batch(eval_batch, cfg)

    def _eval_loss() -> float:
        lv = loss_fn(model, tokens, batch_tree_info)
        mx.eval(lv)
        return float(lv.item())

    champion_loss = _eval_loss()
    champion_snapshot = save_topology(model)

    base_budget = bios_mutation_budget(step, cfg.total_steps, total_ternary, base_pct)
    if base_budget == 0:
        return {
            "champion_loss": champion_loss,
            "budget": 0,
            "accepted": None,
            "accepted_loss": champion_loss,
            "n_tried": 0,
            "frozen": True,
        }

    best_loss = champion_loss
    best_strategy: str | None = None
    best_snapshot = None
    strategies_tried: list[dict] = []

    for strategy_name, scale in MUTANT_STRATEGIES.items():
        budget = max(1, int(base_budget * scale))

        # Always mutate FROM the champion (not from a previous mutant)
        load_topology(model, champion_snapshot)

        # Different seed per strategy
        strategy_rng = np.random.RandomState(
            int(rng.randint(0, 2**31)) ^ (hash(strategy_name) & 0x7FFFFFFF)
        )

        row_imp = row_importance if row_importance else None
        col_imp = col_importance if col_importance else None
        grad_dir = grad_direction if grad_direction else None

        # Targeted strategy: use guided importance fully; random: ignore it
        guided_frac = cfg.guided_fraction if strategy_name != "random" else 0.0

        n_applied = mutate_topology(
            model,
            budget,
            strategy_rng,
            sign_flip_rate=cfg.sign_flip_rate,
            row_importance=row_imp,
            col_importance=col_imp,
            grad_direction=grad_dir,
            guided_fraction=guided_frac,
        )

        mutant_loss = _eval_loss()
        strategies_tried.append({
            "strategy": strategy_name,
            "budget": budget,
            "applied": n_applied,
            "loss": mutant_loss,
            "delta": mutant_loss - champion_loss,
        })

        if mutant_loss < best_loss:
            best_loss = mutant_loss
            best_strategy = strategy_name
            best_snapshot = save_topology(model)

    # Accept or restore champion
    if best_snapshot is not None and best_strategy is not None:
        load_topology(model, best_snapshot)
    else:
        load_topology(model, champion_snapshot)

    return {
        "champion_loss": champion_loss,
        "budget": base_budget,
        "accepted": best_strategy,
        "accepted_loss": best_loss,
        "n_tried": len(strategies_tried),
        "strategies": strategies_tried,
        "frozen": False,
    }


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def save_checkpoint(
    model: V10Model,
    optimizer: optim.Adam,
    step: int,
    cfg: V10Config,
    checkpoint_dir: Path,
    train_losses: list[float],
    total_generations: int,
    total_accepted: int,
    eval_metrics: dict | None,
    row_importance: dict[str, np.ndarray],
    col_importance: dict[str, np.ndarray],
    grad_direction: dict[str, np.ndarray],
    mutation_rng: np.random.RandomState,
) -> None:
    """Save full training state to checkpoint_dir/step_{step:06d}/."""
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    # ── Model weights ─────────────────────────────────────────────
    flat = tree_flatten(model.parameters())
    mx.savez(str(step_dir / "model.npz"), **{k: v for k, v in flat})

    # ── Optimizer state ───────────────────────────────────────────
    opt_flat = tree_flatten(optimizer.state)
    mx.savez(str(step_dir / "optimizer.npz"), **{k: v for k, v in opt_flat})

    # ── Importance maps ───────────────────────────────────────────
    imp_data: dict[str, np.ndarray] = {}
    for path, arr in row_importance.items():
        imp_data[f"row.{path}"] = arr
    for path, arr in col_importance.items():
        imp_data[f"col.{path}"] = arr
    for path, arr in grad_direction.items():
        imp_data[f"dir.{path}"] = arr
    if imp_data:
        np.savez_compressed(str(step_dir / "importance.npz"), **imp_data)

    # ── Mutation RNG state (numpy MT19937) ────────────────────────
    rng_state = mutation_rng.get_state()
    np.savez_compressed(
        str(step_dir / "rng.npz"),
        state_array=rng_state[1],
        pos=np.array([rng_state[2]], dtype=np.int64),
        has_gauss=np.array([rng_state[3]], dtype=np.int64),
        cached_gaussian=np.array([rng_state[4]], dtype=np.float64),
    )

    # ── State JSON ────────────────────────────────────────────────
    state: dict = {
        "step": step,
        "total_generations": total_generations,
        "total_accepted": total_accepted,
        "accept_rate": total_accepted / max(total_generations, 1),
        "train_losses_last50": train_losses[-50:],
        "eval_metrics": eval_metrics or {},
        "config": {
            "d_model": cfg.d_model,
            "batch_size": cfg.batch_size,
            "total_steps": cfg.total_steps,
            "lr": cfg.lr,
            "gen_interval": cfg.gen_interval,
            "base_pct": cfg.base_pct,
            "max_seq_len": cfg.max_seq_len,
        },
    }
    (step_dir / "state.json").write_text(json.dumps(state, indent=2))

    print(f"💾 Checkpoint saved: {step_dir}", file=sys.stderr, flush=True)


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    """Return the step directory with the highest step number, or None."""
    if not checkpoint_dir.exists():
        return None
    step_dirs = sorted(checkpoint_dir.glob("step_*"))
    for d in reversed(step_dirs):
        if (d / "state.json").exists() and (d / "model.npz").exists():
            return d
    return None


def load_checkpoint(
    checkpoint_dir: Path,
    model: V10Model,
    optimizer: optim.Adam,
) -> tuple[int, dict, dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray], np.random.RandomState]:
    """
    Load model, optimizer, importance maps, RNG, and state from a checkpoint.

    Returns
    -------
    step, state_dict, row_importance, col_importance, grad_direction, mutation_rng
    """
    from mlx.utils import tree_unflatten

    # Model
    weights = dict(mx.load(str(checkpoint_dir / "model.npz")))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    # Re-freeze ternary weights after loading (load_weights resets freeze state)
    freeze_ternary_weights(model)
    restore_ternary(model)

    # Optimizer
    opt_path = checkpoint_dir / "optimizer.npz"
    if opt_path.exists():
        opt_state = dict(mx.load(str(opt_path)))
        optimizer.state = tree_unflatten(list(opt_state.items()))
        mx.eval(optimizer.state)

    # Importance maps
    row_importance: dict[str, np.ndarray] = {}
    col_importance: dict[str, np.ndarray] = {}
    grad_direction: dict[str, np.ndarray] = {}
    imp_path = checkpoint_dir / "importance.npz"
    if imp_path.exists():
        data = dict(np.load(str(imp_path)))
        for key, arr in data.items():
            if key.startswith("row."):
                row_importance[key[4:]] = arr
            elif key.startswith("col."):
                col_importance[key[4:]] = arr
            elif key.startswith("dir."):
                grad_direction[key[4:]] = arr

    # Mutation RNG
    mutation_rng = np.random.RandomState()
    rng_path = checkpoint_dir / "rng.npz"
    if rng_path.exists():
        rng_data = np.load(str(rng_path))
        state_array = rng_data["state_array"]
        pos = int(rng_data["pos"][0])
        has_gauss = int(rng_data["has_gauss"][0])
        cached_gaussian = float(rng_data["cached_gaussian"][0])
        mutation_rng.set_state(("MT19937", state_array, pos, has_gauss, cached_gaussian))

    state = json.loads((checkpoint_dir / "state.json").read_text())

    print(
        f"📂 Loaded checkpoint: {checkpoint_dir}\n"
        f"   step={state['step']}  "
        f"gens={state.get('total_generations', 0)}  "
        f"accepted={state.get('total_accepted', 0)}",
        file=sys.stderr, flush=True,
    )

    return (
        state["step"],
        state,
        row_importance,
        col_importance,
        grad_direction,
        mutation_rng,
    )


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Main training loop
# ══════════════════════════════════════════════════════════════════════════════

def train(cfg: V10Config, args: argparse.Namespace) -> None:
    """Full training loop."""
    checkpoint_dir = Path(cfg.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v10 — Self-Similar Compressor + VSMNode Tree Training", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ─────────────────────────────────────────────────────
    model = create_model(cfg)
    freeze_ternary_weights(model)

    param_counts = count_parameters(model)
    total_ternary = count_ternary_weights(model)

    print(f"\n  d_model={cfg.d_model}  n_heads={cfg.n_heads}  "
          f"n_layers_per_level={cfg.n_layers_per_level}  "
          f"n_iterations={cfg.n_iterations}",
          file=sys.stderr)
    print(f"  params: total={param_counts['total']:,}  "
          f"trainable={param_counts['trainable']:,}  "
          f"ternary_weights={total_ternary:,}",
          file=sys.stderr)
    print(f"  n_ops={cfg.n_ops}  vocab_size={cfg.vocab_size}  "
          f"max_seq_len={cfg.max_seq_len}",
          file=sys.stderr)

    # ── Optimizer ─────────────────────────────────────────────────
    optimizer = optim.Adam(
        learning_rate=cfg.lr,
        betas=[0.9, 0.999],
    )

    # ── value_and_grad ────────────────────────────────────────────
    # The new loss_fn takes (model, tokens, batch_tree_info).
    # batch_tree_info is a plain Python list — not a differentiable argument.
    # nn.value_and_grad differentiates w.r.t. model parameters only.
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Data ──────────────────────────────────────────────────────
    train_loader = InfiniteDataLoader(cfg, seed=42)
    import random
    eval_rng_py = random.Random(8888)

    # ── Importance maps (EMA from gamma grads + activation stats) ─
    row_importance: dict[str, np.ndarray] = {}
    col_importance: dict[str, np.ndarray] = {}
    grad_direction: dict[str, np.ndarray] = {}
    imp_alpha = 0.1   # EMA coefficient

    # ── Mutation RNG ──────────────────────────────────────────────
    mutation_rng = np.random.RandomState(42)

    # ── Training state ────────────────────────────────────────────
    start_step = 0
    train_losses: list[float] = []
    last_eval_metrics: dict | None = None
    total_generations = 0
    total_accepted = 0
    last_gen_result: dict | None = None

    # Moving window for avg-50 loss display
    loss_window: deque[float] = deque(maxlen=50)

    # ── Resume ────────────────────────────────────────────────────
    if args.resume:
        ckpt_path = find_latest_checkpoint(checkpoint_dir)
        if ckpt_path is None:
            print(f"  ⚠  No checkpoint found in {checkpoint_dir}, starting fresh.",
                  file=sys.stderr)
        else:
            start_step, state, row_importance, col_importance, grad_direction, mutation_rng = \
                load_checkpoint(ckpt_path, model, optimizer)
            train_losses = state.get("train_losses_last50", [])
            total_generations = state.get("total_generations", 0)
            total_accepted = state.get("total_accepted", 0)
            last_eval_metrics = state.get("eval_metrics")
            loss_window.extend(train_losses[-50:])

    # ── Warm-up optimizer state ───────────────────────────────────
    # Adam needs at least one update to initialize its state arrays.
    # If starting fresh: do a single dummy step. If resuming with populated
    # optimizer state: skip (state was loaded from checkpoint).
    if not args.resume or not optimizer.state:
        import random as _rnd
        _dummy_rng = _rnd.Random(0)
        _dummy_batch = generate_batch(
            _dummy_rng, cfg.batch_size, cfg.max_seq_len, cfg.max_depth, cfg.max_value
        )
        _dt, _dbt = prepare_batch(_dummy_batch, cfg)
        _lv, _grads = loss_and_grad(model, _dt, _dbt)
        mx.eval(_lv, _grads)
        _grads = zero_ternary_grads(model, _grads)
        optimizer.update(model, _grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

    print(
        f"\n  batch_size={cfg.batch_size}  total_steps={cfg.total_steps}  "
        f"lr={cfg.lr}  warmup={cfg.warmup_steps}\n"
        f"  gen_interval={cfg.gen_interval}  base_pct={cfg.base_pct}  "
        f"eval_interval={cfg.eval_interval}  checkpoint_dir={checkpoint_dir}\n"
        + (f"  Resuming from step {start_step}" if args.resume else ""),
        file=sys.stderr,
    )
    print("", file=sys.stderr, flush=True)

    # ══════════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════════

    t_start = time.time()

    for step in range(start_step + 1, cfg.total_steps + 1):
        t0 = time.time()

        # ── LR ────────────────────────────────────────────────────
        lr = cosine_lr(step, cfg.warmup_steps, cfg.total_steps, cfg.lr, cfg.lr_floor_ratio)
        optimizer.learning_rate = lr

        # ── Data + batch prep ─────────────────────────────────────
        batch = next(train_loader)
        tokens, batch_tree_info = prepare_batch(batch, cfg)

        # ── Forward + backward ────────────────────────────────────
        loss_val, grads = loss_and_grad(model, tokens, batch_tree_info)
        mx.eval(loss_val, grads)

        step_loss = float(loss_val.item())
        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── Accumulate gradient importance maps ───────────────────
        for path, mod in _walk_ternary_modules(model):
            if not isinstance(mod, TernaryLinear):
                continue

            # Navigate the grads pytree to find gamma grad for this module
            parts = path.split(".")
            g_node = grads
            for p in parts:
                if isinstance(g_node, dict):
                    g_node = g_node.get(p, {})
                elif isinstance(g_node, list) and p.isdigit():
                    g_node = g_node[int(p)]
                else:
                    g_node = {}
                    break
            gamma_grad = g_node.get("gamma") if isinstance(g_node, dict) else None

            if gamma_grad is not None:
                gg_np = np.array(mx.abs(gamma_grad))
                gs_np = np.array(gamma_grad)  # signed, for direction
                if path in row_importance:
                    row_importance[path] = (
                        imp_alpha * gg_np + (1.0 - imp_alpha) * row_importance[path]
                    )
                    grad_direction[path] = (
                        imp_alpha * gs_np + (1.0 - imp_alpha) * grad_direction[path]
                    )
                else:
                    row_importance[path] = gg_np
                    grad_direction[path] = gs_np

            # Column importance from input activation stats stored by TernaryLinear
            if hasattr(mod, "_x_abs_mean"):
                xm = np.array(mod._x_abs_mean)
                if path in col_importance:
                    col_importance[path] = (
                        imp_alpha * xm + (1.0 - imp_alpha) * col_importance[path]
                    )
                else:
                    col_importance[path] = xm

        # ── Zero ternary grads (topology is evolutionary only) ────
        grads = zero_ternary_grads(model, grads)

        # ── Gradient clipping ─────────────────────────────────────
        grad_sq = [mx.sum(g * g) for _, g in tree_flatten(grads)]
        mx.eval(*grad_sq)
        grad_norm = sum(float(g) for g in grad_sq) ** 0.5

        if cfg.grad_clip > 0.0 and grad_norm > cfg.grad_clip:
            scale = cfg.grad_clip / (grad_norm + 1e-8)
            grads = tree_map(lambda g: g * scale, grads)

        # ── Optimizer step ────────────────────────────────────────
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)

        # ── Safety check: ternary dtype must remain uint32/uint8 ──
        restore_ternary(model)

        dt = time.time() - t0

        # ── Per-step log ──────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            evo_str = ""
            if last_gen_result is not None:
                acc_n = total_accepted
                gen_n = total_generations
                pct = acc_n / max(gen_n, 1) * 100
                evo_str = (
                    f" | evo {acc_n}/{gen_n} ({pct:.0f}%)"
                    f" pct={cfg.base_pct:.3f}"
                )

            op_acc_str = ""
            if last_eval_metrics:
                op_acc_str = f" | op_acc {last_eval_metrics['op_acc']*100:.1f}%"

            print(
                f"step {step:>6d} | loss {step_loss:.3f}"
                f" (avg50: {avg50:.3f})"
                f" | lr {lr:.2e}"
                f"{op_acc_str}"
                f"{evo_str}"
                f" | {dt:.2f}s/step"
                f" | {elapsed:.0f}s total",
                file=sys.stderr, flush=True,
            )

        # ── Evolutionary tournament ───────────────────────────────
        if step % cfg.gen_interval == 0:
            eval_batch = generate_batch(
                rng=eval_rng_py,
                batch_size=cfg.batch_size,
                max_seq_len=cfg.max_seq_len,
                max_depth=cfg.max_depth,
                max_value=cfg.max_value,
            )

            gen_result = run_tournament(
                model=model,
                cfg=cfg,
                step=step,
                total_ternary=total_ternary,
                eval_batch=eval_batch,
                base_pct=cfg.base_pct,
                rng=mutation_rng,
                row_importance=row_importance,
                col_importance=col_importance,
                grad_direction=grad_direction,
            )

            total_generations += 1
            if gen_result["accepted"]:
                total_accepted += 1

            last_gen_result = gen_result

            accepted_str = gen_result["accepted"] or "rejected"
            delta = gen_result["accepted_loss"] - gen_result["champion_loss"]
            print(
                f"  🧬 gen {total_generations}: {accepted_str}"
                f"  Δloss={delta:+.4f}"
                f"  budget={gen_result['budget']:,}"
                f"  {total_accepted}/{total_generations}"
                f" ({total_accepted / max(total_generations, 1)*100:.0f}% accept)",
                file=sys.stderr, flush=True,
            )

        # ── Evaluation ────────────────────────────────────────────
        if step % cfg.eval_interval == 0:
            eval_metrics = evaluate(model, cfg, rng_seed=step)
            last_eval_metrics = eval_metrics
            print(
                f"📊 Eval @ step {step}: "
                f"op_acc={eval_metrics['op_acc']*100:.1f}%, "
                f"result_acc={eval_metrics['result_acc']*100:.1f}%, "
                f"loss={eval_metrics['loss']:.3f}",
                file=sys.stderr, flush=True,
            )

        # ── Checkpoint ────────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            save_checkpoint(
                model=model,
                optimizer=optimizer,
                step=step,
                cfg=cfg,
                checkpoint_dir=checkpoint_dir,
                train_losses=train_losses,
                total_generations=total_generations,
                total_accepted=total_accepted,
                eval_metrics=last_eval_metrics,
                row_importance=row_importance,
                col_importance=col_importance,
                grad_direction=grad_direction,
                mutation_rng=mutation_rng,
            )

    # ══════════════════════════════════════════════════════════════
    # Final
    # ══════════════════════════════════════════════════════════════

    elapsed_total = time.time() - t_start
    print(
        f"\n{'='*72}\n"
        f"Training complete: {cfg.total_steps - start_step} steps "
        f"in {elapsed_total:.0f}s ({elapsed_total/60:.1f} min)\n"
        f"Final train loss: {train_losses[-1]:.4f}",
        file=sys.stderr,
    )

    final_metrics = evaluate(model, cfg, rng_seed=0)
    print(
        f"Final eval: op_acc={final_metrics['op_acc']*100:.1f}%  "
        f"result_acc={final_metrics['result_acc']*100:.1f}%  "
        f"loss={final_metrics['loss']:.4f}",
        file=sys.stderr,
    )

    save_checkpoint(
        model=model,
        optimizer=optimizer,
        step=cfg.total_steps,
        cfg=cfg,
        checkpoint_dir=checkpoint_dir,
        train_losses=train_losses,
        total_generations=total_generations,
        total_accepted=total_accepted,
        eval_metrics=final_metrics,
        row_importance=row_importance,
        col_importance=col_importance,
        grad_direction=grad_direction,
        mutation_rng=mutation_rng,
    )


# ══════════════════════════════════════════════════════════════════════════════
# § 8  CLI
# ══════════════════════════════════════════════════════════════════════════════

def build_cfg_from_args(args: argparse.Namespace) -> V10Config:
    """Build V10Config with CLI overrides applied."""
    cfg = V10Config()
    if args.total_steps is not None:
        cfg.total_steps = args.total_steps
    if args.checkpoint_dir is not None:
        cfg.checkpoint_dir = args.checkpoint_dir
    if args.d_model is not None:
        cfg.d_model = args.d_model
        cfg.d_ff = args.d_model * 3
    if args.batch_size is not None:
        cfg.batch_size = args.batch_size
    if args.gen_interval is not None:
        cfg.gen_interval = args.gen_interval
    if args.base_pct is not None:
        cfg.base_pct = args.base_pct
    if args.seq_len is not None:
        # Override both seq_len aliases in config
        cfg.seq_len = args.seq_len
        cfg.max_seq_len = args.seq_len
    # Re-validate after overrides
    cfg.__post_init__()
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser(
        description="v10 — Self-similar compressor + VSMNode tree training",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--total-steps", type=int, default=None,
        help="Total training steps (default: from config)",
    )
    parser.add_argument(
        "--checkpoint-dir", type=str, default=None,
        help="Checkpoint directory (default: from config)",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume from the latest checkpoint in checkpoint-dir",
    )
    parser.add_argument(
        "--d-model", type=int, default=None,
        help="Override d_model dimension",
    )
    parser.add_argument(
        "--batch-size", type=int, default=None,
        help="Override batch_size",
    )
    parser.add_argument(
        "--gen-interval", type=int, default=None,
        help="Override gen_interval (steps between evolutionary generations)",
    )
    parser.add_argument(
        "--base-pct", type=float, default=None,
        help="Override base_pct (mutation rate)",
    )
    parser.add_argument(
        "--seq-len", type=int, default=None,
        help=(
            "Override max_seq_len (token sequence length). "
            "Default config is 4096; use e.g. 128 for faster initial training. "
            "The model works at any length since attention is windowed."
        ),
    )

    args = parser.parse_args()
    cfg = build_cfg_from_args(args)
    train(cfg, args)


if __name__ == "__main__":
    main()
