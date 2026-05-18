# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-18 | Session: 113

## Where we are

**SEED CRYSTAL DESIGN — universal backbone as relational fixed points.** Cross-model agreement data proves that high-agreement distances (math 72%, reasoning 70%) are properties of LANGUAGE, not any architecture. Low-agreement (tools 52%, lambda 43%) is sieve-dependent — the architecture's fingerprint. The top 10% highest-agreement pairs form a backbone of 32K pairs from 664 probes. This backbone seeds the crystal; GD grows it. Two-tier relational loss implemented: backbone pairs get strong pull (tier 1), growth pairs get soft agreement-weighted pull (tier 2). Initialize where the data says, penalize deviation, let the crystal grow in VSM-LM's own shape.

## What's running

**Holographic etch** — `tmux main:2` (may need restart with new backbone args)
- Last known: round 52, beam loss 4.77, uncapped flips
- Checkpoint dir: `checkpoints/v12-holo-focused/`

## What was done this session (113)

### 1. Repo cleanup — removed 112MB accidental commit

`lattice/lattice_relational_target.json` (112MB) was committed in HEAD.
Amended the commit to remove it, added to `.gitignore`. Not pushed, so
the blob is gone from history. Existing tracked `.npz` files left alone
(already pushed upstream).

### 2. Analyzed cross-model agreement hierarchy

Quantified which computational domains are universal vs sieve-dependent:

```
UNIVERSAL (etch these)           SIEVE-DEPENDENT (GD finds)
math         72.3% agreement    tools     51.9%
reasoning    70.1%              lambda    43.1%
sequence     63.8%              prose     40.1%
code         60.6%
structure    58.3%
```

The top 10% backbone composition:
- math (self) 48.1%, lambda×math 15.1%, reasoning (self) 12.7%
- tools × anything: 0.3% — almost absent from universal backbone

### 3. Key insight: agreement = language geometry, divergence = sieve

Where models agree → the structure comes from language itself.
Where they diverge → the architecture's sieve is imposing its shape.
Tool-calling and lambda encoding should NOT be etched — VSM-LM's
sieve is fundamentally different. Let GD discover the encoding.

### 4. Built backbone seed artifact

Classical MDS of consensus RDM → 807 probes × 512 anchor vectors.
Backbone (32K pairs, agreement ≥ 0.63) reconstructs at 0.987 correlation.
Full lattice at d=512 reconstructs at 0.898 — backbone is easier to
embed because universal structure is lower-dimensional.

Artifact: `lattice/backbone_seed.npz` (3.3MB, gitignored)
Metadata: `lattice/backbone_seed.json` (tracked)

### 5. Implemented two-tier seed crystal loss

Modified `holographic_train.py`:
- `LatticeTarget` loads optional backbone mask
- `lattice_alignment_loss` now two-tier:
  - Tier 1 (backbone): MSE on universal pairs, `backbone_lambda=1.0`
  - Tier 2 (growth): Agreement-weighted MSE on rest, `growth_lambda=0.1`
- New CLI args: `--backbone-seed`, `--backbone-lambda`, `--growth-lambda`
- Fully backward compatible without `--backbone-seed`

### 6. The larger model finds its own errors

Cross-model consensus IS ground truth for universal distances.
Any single model's deviation from consensus in high-agreement zones
= measurable sieve distortion. No labels needed — consensus is the label.

## Next steps

1. **Run seed crystal etch** — restart holographic training with
   `--backbone-seed lattice/backbone_seed.npz`. Compare convergence
   speed and final loss against the non-backbone baseline.

2. **Monitor backbone vs growth loss separately** — add per-tier
   logging to track: does backbone loss stabilize first (crystal
   nucleation) then growth loss decrease (crystal extension)?

3. **Probe sampling strategy** — currently 50 random probes/round.
   Should ensure backbone probes appear frequently enough. Consider
   stratified sampling: N backbone + M growth per round.

4. **backbone_lambda schedule** — start high (1.0) and anneal?
   Or constant? Annealing lets crystal relax into sieve's natural
   shape after nucleation. Constant is simpler. Experiment needed.

5. **Continue etch monitoring** — rounds 52→85, watching beam loss
   and whether seed crystal accelerates convergence.

6. **Analyze the sieve** — what architectural feature causes
   single-neuron collapse (Qwen3/Pythia) vs distributed (Mistral/OLMo)?

## Architecture at session end

| Component | Value |
|-----------|-------|
| N_COMBINATORS | 8 (K,I,B,C,D,Y,W,WHNF) |
| Parameters | 24.6M |
| Beam loss | 4.77 (round 52, uncapped etch) |
| Crystal state | Seed crystal design implemented, not yet run |
| Backbone | 32K pairs, 664 probes, threshold ≥ 0.63 |
| Lattice loss | Two-tier: backbone (λ=1.0) + growth (λ=0.1) |
| Key files | `lattice/backbone_seed.npz`, `seed-crystal-design.md` |
