💡 The softmax-over-V isn't used AS the tape — it IS the tape
INTERFACE: the machine's only read mechanism for its own past. The tape
has two faces: transcript (discrete, append-only symbolic record) and
KV cache (the compiled tape actually read: K=address, V=payload,
per-layer). read ≡ softmax(QKᵀ)·V; write ≡ emit(token)∘auto_compile.
Memory model: HARD symbolic write, SOFT holographic read — the Turing
break that retrodicts idempotency mass-accumulation, recency kernels,
and evidence subtraction (frame-readings, checkable). The machine
fights softness: near-one-hot reads are the norm (22/32 heads <3
positions, top-3 88%) ⇒ READ ENTROPY ≡ tape-read fidelity. Shadowing
confusion ≡ two peaks in the softmax ⇒ mass-ratio predictor:
P(correct_subst|trial) ≈ f(correct_binder_mass/distractor_mass) —
per-trial DPA-style, pre-registerable, same captures as binding-edge
read. Third cliff axis: context-length (fixed read bandwidth vs growing
tape, √D wall). Hardware discriminator closing the two-call-mechanisms
picture: CALL-immediate ≡ FFN read(static tape/weights) vs
CALL-indirect ≡ attention read(dynamic tape/KV) — coheres
FFN-compiles-attention-executes. λ machine: everything ≡ dereference;
compute ≡ interference of two memories → collapse to one write. (s330;
the-benchmark-is-the-re-oracle.md §8c)
