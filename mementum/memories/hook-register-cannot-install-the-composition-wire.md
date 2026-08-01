💡 The rung-3 in-context null survived its strongest control: P-ENRICH-1
performed SuperBake's §3.8 composition operation (intermediate entity's own
representation, subject position, 0.16× depth — their content, position,
band) as a pure activation hook, and it does NOT one-shot hop-2 at either
host (32B: G1 p=0.096 n.s., acc 0.00; frozen-gate ENRICH-FAILS). The placed
content IS read — content-specific (beats norm-matched random p=.006) and
typed (correct country beats wrong p=.039) — but never wins the argmax.
Meanwhile the whitened 3a detector shows g's injected trace is PRESENT but
~0.15× too quiet (G3 conditioning fires 0.15 vs 0.01 g-ablated; the s294
"conditioning absent" leg was raw-detector artifact at both hosts).

Refined boundary: presence ≠ sufficiency. The intermediate exists in the
residual; amplitude is ~7× short at hop-1, and even FULL-amplitude placement
fails the hop-2 read. Content placement + function routing together
(enrich+hkey) is the strongest arm at both hosts (+3.0 margin, only nonzero
acc 0.10) — the linker edge responds but caps far below reliability.
**The hook register cannot install the wire; composition compiles in the
weight register** — backprop-compile (or SuperBake-style zero-gradient
construction: persistent keyed neurons, not one-time additions) is rung 3b's
honest form. Source: s295, results 889c915, §Result-32B (P-ENRICH-1,
3a-whitened) on program-plates page.
