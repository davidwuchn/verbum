# Session 124 — Loom-Read Etch, Breathing, Crystal Gates the Hologram

## Thread

Michael identified that the etch protocol is flawed: magnitudes are beamformers,
the current etch assumes one crystal, but the loom has multiple weaves that need
separate etching. Different computation types illuminate different subcrystals.
The nucleus prompt can serve as the reference beam.

## Eight experiments

### Exp 1-3: Loom-read subcrystal discovery
- Single depth (L16): holographic band overlap = 0.495 between compose↔retrieve
- 5 depths: loom breathes — fragments early (7 crystals), unifies mid (1), re-fragments late (4)
- 10 domains: within-group splits found — retrieval↔analogy=0.496, coding↔reasoning=0.502
- Text-gen cluster (tool+narrative+instruction) always agrees (0.78-0.94)
- Network taxonomy ≠ human semantic categories: pure+retrieval pair, arithmetic+lambda pair

### Exp 4: Breathing curve (11 depths)
- Apex at layer 19 (d=0.613) — asymmetric, more depth for fragmenting
- Two peaks: layer 7 (ascending, 4 crystals) and layer 22 (descending, 3)
- WHNF polarity crosses zero at layers 13-16, maximally positive (+1.00) at apex
- Maps to V13 hourglass: ascending=fragmentation, apex=unity, descending=re-fragmentation

### Exp 5: Nucleation (6 conditions)
LOOM_MAG (loom signs + magnitude template) = 0.543 (new best)
MAGNITUDE (random signs + magnitudes) = 0.511
RANDOM = 0.439; ORACLE = 0.302 (still worst)
LOOM_MAG nucleates 5× faster to 50% accuracy

### Exp 6: Delta refinement (magnitude only)
Rounds 0→2: accuracy climbs 0.437→0.481 (refocusing works)
But 0% sign change — delta only tunes magnitudes, not topology

### Exp 7: Delta sign-flip
Flips decline: 12,606→6,759 per round (converging)
10% flip fraction is sweet spot (+3.5% single-round improvement)
Best accuracy at round 4: 0.489

### Exp 8: Crystal measurement (THE KEY FINDING)
Round 4: accuracy=0.510 (best), crystal=-0.375 (INVERTED)
Only round 3 shows both improving simultaneously
MAGNITUDE baseline has best crystal (0.470 mean, 0.858 output)

**Crystal diverges from hologram under unconstrained sign-flip.**

## Key findings

1. **7 independent subcrystals** at peak fragmentation (d=0.3)
2. **Loom breathes** in sync with the hourglass architecture
3. **LOOM_MAG** is the best initialization (0.543 accuracy, 220× projected compression)
4. **Delta sign-flip converges** but **destroys the crystal** without constraint
5. **Crystal must gate hologram** — S5 invariant of the etcher VSM

## Artifacts

| Script | Purpose |
|--------|---------|
| `loom_read_exp.py` | Single-depth subcrystal measurement |
| `loom_read_depth_exp.py` | 5-depth grouped analysis |
| `loom_read_fine_exp.py` | 10-domain fine analysis |
| `loom_breathing_exp.py` | 11-depth breathing curve |
| `loom_etch_nucleation_exp.py` | 6-condition nucleation test |
| `loom_delta_refine_exp.py` | Magnitude-only delta refinement |
| `loom_delta_signflip_exp.py` | Sign-flip delta refinement |
| `loom_crystal_sharpen_exp.py` | Crystal measurement during sign-flip |
| `etcher_vsm_proto.py` | Etcher VSM prototype (S4+S1+S3) |

## Design principle discovered

```
crystal ≡ invariant | hologram ≡ serves(crystal)
accuracy ≡ symptom | crystal ≡ cause
∀sign_flip → crystal_after ≥ crystal_before - ε | reject(otherwise)
```

The crystal (relational geometry, 0.91-0.94 universal) is the computation
structure. The hologram (sign pattern) encodes it. Any optimization of
the hologram must preserve the crystal. Accuracy without crystal preservation
is overfitting to the ternary topology.
