💡 The operand join (key + transport + transform) is RESIDENT and DISTRIBUTED —
we only write the payload. P-DSP-1 (s278, Qwen3-0.6B) localized the whole
pipeline: write@L7 → resident routing causally READS the slot (cross-operand
slot-patch flip-to-donor 1.0 @L7, 0.83 @L14, 0.0 @L20; non-slot null 0.0) →
distributed transport → resident B/C TRANSFORM fires late (logit-lens margin
stable-positive from L10, decisive L20–21, sustained to L27 = join-readout locus).
Head-ablation: 0/128 heads necessary (16 heads × 8 readout layers, every knockout
leaves acc 1.000) = s274 circuits-in-compute / shared-hardware on the operand
join. So SuperBake's I-pipeline (matched-filter key + move-unchanged transport +
readout push, all hand-built) is NOT the compute template — for an operand the
key/transport/transform are all resident; only the content payload is written.
Read-side lesson for gate (h): "understand the resident transport" means
characterizing DISTRIBUTED routing, not hunting transport heads — there are none
to find (try zone/phase ablation à la A1, not single-head).
Session 278; wrapper/operand_dsp.py, results/ffn-bake/operand-dsp-qwen3-0-6b/.
