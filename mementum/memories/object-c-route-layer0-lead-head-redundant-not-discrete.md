💡 The early object→C attention route (s252) localizes to LAYER 0 with a lead head, but is concentrated-with-redundancy — NOT a discrete head circuit.

TEST (program_edge_knockout.py mode=heads, Qwen3-14B): per-head additive-mask expansion ([B,1,Q,K]→[B,H,Q,K], -inf at one head's object-key cols) severs ONLY that head's attention to the object; 200 (layer,head) pairs across the L0-4 gateway × 20 items; readout z(C) collapse.

RESULTS: (1) LAYER-0-CONCENTRATED — all 6 significant carriers (t>2) in L0; L0 holds 67% of positive-drop mass (L1 12%, L4 10%). Sharpens s252 "L0-4 early" → ~L0 (first attention layer). (2) LEAD HEAD L0h18 (drop=0.065, t=5.5), ~3× next (L0h11 0.023, t=4.6); top5=49%. The most circuit-like locus in the whole s250 arc. (3) NOT DISCRETE — 21 heads to reach 80% → discrete_head_circuit=false; dominant head + diffuse redundant tail. (4) REDUNDANCY — single-head drops tiny (0.065) vs all-heads necessity (1.04); severing one head barely dents z(C), the rest reconstruct it (holographic, echoes s250).

NET: a privileged early gateway (L0, h18) exists — a real preferred locus — but object-application cannot be severed by a few heads. For VERBUM λ types: preferred locus yes, discreteness no. Connects s127 ({B,C}=composer heads — L0h18 is the candidate), s250 holographic reconstruction.
