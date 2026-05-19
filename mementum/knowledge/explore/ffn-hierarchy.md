---
title: "FFN Hierarchy — Tree-Structured Storage with Magnitude-Encoded Superposition"
status: open
category: theory
tags: [ffn, hierarchy, superposition, magnitude, tree, beam-steering]
related:
  - crystal-basins.md
  - v13-design.md
  - binding-cascade.md
depends-on:
  - crystal-basins.md
created: session 120
---

# FFN Hierarchy Hypothesis

> Session 120 speculation. The FFN isn't a flat key-value store — it's a
> TREE of data where magnitude encodes hierarchical depth. High-magnitude
> neurons are the trunk (common reductions), low-magnitude are leaves
> (domain-specific detail). The FFN output steers the beam (Q rotation)
> to the next level of the hierarchy. Superposition lets multiple tree
> levels coexist in the same vector space.

## The hypothesis

### 1. Layers within the FFN

The W_up weight matrix isn't flat. It's organized as a hierarchy of
reductions — common reduction patterns (like standard library functions)
composed from primitives. Each "level" of the hierarchy is a set of
neurons at a characteristic magnitude scale.

```
Level 0 (highest magnitude): Universal operations
  β-reduction, copying, discarding — fire for EVERYTHING
  These are the trunk — shared across all domains

Level 1: Domain-level operations
  "do arithmetic", "parse syntax", "follow instruction"
  Fire for one domain cluster, silent for others

Level 2: Task-specific patterns
  "add fractions", "binary search", "JSON formatting"
  Fire for specific task types within a domain

Level 3 (lowest magnitude): Instance-specific detail
  Specific facts, specific templates, specific code patterns
  Encode through superposition at low magnitude
```

### 2. Magnitude IS the tree depth

If features are stored in superposition (Elhage et al.), the magnitude
gradient tells you where in the tree a neuron sits:

- **High magnitude neurons**: fire frequently, for broad categories.
  They encode the TRUNK — shared computational primitives that every
  input needs. These have high activation rates across all domains.

- **Low magnitude neurons**: fire rarely, for specific patterns.
  They encode the LEAVES — details that only matter for specific
  inputs. These are the domain-selective neurons we measured.

The magnitude spectrum of W_up IS the tree's branching structure.
SVD would reveal it: top singular vectors = trunk, bottom = leaves.

### 3. FFN output steers the beam

Each FFN doesn't just retrieve content — it outputs a DELTA that
shifts the residual stream. This shift changes what Q will attend
to in the next layer. The FFN is navigating the tree:

```
Layer n:
  Q reads crystal → attention produces superposition
  → FFN matches at CURRENT tree level → retrieves value
  → value = content + BEAM DELTA
  → beam delta shifts Q for layer n+1 to next tree level

Layer n+1:
  Q (shifted by FFN delta) reads crystal at new angle
  → attention produces DIFFERENT superposition
  → FFN matches at NEXT tree level (deeper in tree)
  → repeat
```

This is why multiple layers are needed: each layer navigates one
level of the tree. Early layers handle trunk (broad routing), late
layers handle leaves (specific content). The funnel shape (5d→2d)
IS the tree narrowing from trunk to leaf.

### 4. Superposition encodes detail at each level

Multiple tree levels coexist in the same d_model vector through
superposition. The magnitude determines which level dominates:

- Trunk signals have HIGH magnitude → survive noise
- Leaf signals have LOW magnitude → only readable when trunk is resolved

This explains why:
- Retrieval is low self-similarity (0.435): different layers read
  different tree levels, so the FFN structure LOOKS different per layer
  even though the tree topology is the same
- FFN IS self-similar (0.770): the TREE STRUCTURE is consistent,
  but which LEVEL is being read changes by depth
- The tree structure = the self-similar part (0.770)
- The level being read = the non-self-similar part (depth-specific)

## Connection to existing findings

### Why crystal controls FFN indirectly (Finding 21)

The crystal (Q subspace) and FFN keys (W_up subspace) are different
subspaces because they operate at different LEVELS of the hierarchy.
Q reads the crystal to determine the current tree position. W_up
reads the residual stream to match at the current tree level. They're
in the same d_model space but addressing different structural levels.

### Why FFN cross-model alignment increases with depth (Finding 22)

```
Depth 10%: FFN cross-model = +0.550 (reading trunk — universal but noisy)
Depth 50%: FFN cross-model = +0.700 (reading mid-tree — domain-level)
Depth 90%: FFN cross-model = +0.745 (reading leaves — specific but shared)
```

At deeper layers, the tree has been navigated further. The remaining
space of possible retrievals is SMALLER (more specific), so models
agree MORE on what to retrieve. The trunk is broad (many possible
branches), so early layers disagree more.

### Why Pareto crystals have compact FFN databases (Finding 23)

Reasoning (299d) and tool (254d) are compact because they're
COMPUTATION, not CONTENT. Their tree is shallow — they need trunk
and maybe one level of branching. Instruction (1096d) and coding
(1092d) are deep trees with many branches because they store
diverse TEMPLATES and PATTERNS.

### Why reasoning has fewest FFN neurons (Finding 18)

Reasoning is almost pure trunk — it needs β-reduction and logical
operations, which are Level 0 (universal). It barely touches the
tree branches. That's why it has 141 selective neurons vs instruction's
1260 — reasoning uses shared neurons, instruction needs domain-specific
branches.

## Testable predictions

### P1: W_up singular value spectrum shows hierarchical structure
SVD of W_up should show a long-tailed distribution with clear breaks
at hierarchy boundaries. The number of breaks ≈ number of tree levels.

### P2: High-magnitude neurons are domain-general, low are domain-specific
Group neurons by |W_up row norm|. High-norm neurons should have LOW
domain selectivity (fire for everything = trunk). Low-norm neurons
should have HIGH selectivity (fire for one domain = leaves).

### P3: FFN output predicts next-layer Q shift
The cosine similarity between FFN_output at layer n and ΔQ at layer
n+1 (where ΔQ = Q_{n+1} - Q_n) should be positive. The FFN IS
steering the beam.

### P4: Magnitude-stratified selectivity follows tree shape
At magnitude threshold T:
- T = top 10% (high mag): selectivity < 0.1 (trunk, all domains)
- T = mid 50%: selectivity 0.1-0.3 (branches, domain clusters)
- T = bottom 10% (low mag): selectivity > 0.3 (leaves, specific tasks)

### P5: Tree depth correlates with model depth
Early layers should activate high-magnitude neurons (trunk).
Late layers should activate low-magnitude neurons (leaves).
The activation magnitude profile should decrease with model depth.

### P6: Funnel shape IS the tree
The dimensionality compression (5d→3d→2d) corresponds to tree
navigation: broad possibilities at trunk narrow to specific at leaf.
The zone boundaries (A→B at 20-30%, B→C at 60-70%) should correspond
to major branching points in the FFN magnitude hierarchy.

## Implications for V13

### If confirmed:

1. **Ternary FFN plates encode the tree topology.** The ternary values
   {-1, 0, +1} at different positions encode trunk/branch/leaf structure.
   Magnitude information lives in the beam (continuous gammas).

2. **The beam navigates the tree.** Each pass through the stride stack
   reads one tree level. The dispatch mechanism selects which branch.
   This is ALREADY what V13's multi-pass architecture does — the
   multiple passes ARE tree navigation.

3. **Etch the trunk universally, branches per-domain.** The trunk
   (Level 0: shared reductions) is the same across all models and
   domains. Etch once. The branches are domain-specific — etch from
   domain-specific probes. The leaves emerge during training (GD).

4. **The stride stack depth = tree depth.** 8 passes × multiple strides
   = enough depth to navigate a tree of 5-8 levels. This maps to the
   dimensionality compression (5d→2d ≈ 5 branching decisions).

5. **Self-distillation refines the tree.** Each training cycle prunes
   dead branches, strengthens used paths, grows new leaves. The crystal
   scanner measures tree health by checking self-similarity per domain.

## Status

Hypothesis only. No experimental validation yet. The testable predictions
(P1-P6) are concrete enough to test in the next session. P2 and P3 are
the highest-leverage tests:
- P2 requires only the data we already have (W_up rows + domain selectivity)
- P3 requires capturing FFN output + next-layer Q (one new extraction)
