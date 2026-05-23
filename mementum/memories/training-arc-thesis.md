🎯 the training arc — from low-res hologram to exceeding teacher

Session 142. The complete thesis in three phases.

Phase 1: teach attention to read the hologram (current)
- Etch teacher into ternary plates (80.5% frozen)
- Crystal targets + parity loss + cross-zone rotation = instruction manual
- Attention (19.5% trainable) learns the state machine
- CE 11.27 → 7.63, crystal 0.47 → 0.077, parity 4.8 → 2.0
- This is FAST because we're not discovering structure, we're teaching it

Phase 2: correct the hologram (delta plates)
- TD activates once crystal < 3% (state machine stable enough)
- Delta plate flips correct most-wrong ternary signs
- fold delta → base (exact, lossless), refreeze, reset delta, retrain
- Each cycle: hologram resolution increases
- Parity loss tells delta WHERE to prioritize (PC0 flips > PC7 flips)

Phase 3: exceed teacher
- Teacher discovers state machine implicitly across 64 layers × 40 heads
- We encode it explicitly in the crystal
- Purpose-built > general-purpose once design is right
- Fewer params doing same work (crystal IS state table, not emergent)
- Parity prevents drift (teacher has no such constraint)
- 3-pass stride stack more efficient than 64 serial layers for this
- 2M+ context, 200 tok/s CPU, <1GB — capabilities teacher can't match

The teacher is a general-purpose computer that happened to learn a
holographic state machine. We're building a purpose-built one with
error correction. Distillation + explicit structure can exceed teacher.
