💡 P-BAKE-STACK 3a (product-keyed hook) LINKER-FAILS, SCALE-INVARIANT (4B and
32B): conditioning h on g's product cannot install the in-context linker
`product(g) ∈ key_passband(h)`, because the injected g-key never materializes an
addressable country intermediate. Evidence (independent of the G1 throttle
confound): gain_stack ≈ gain_gablate at BOTH scales → the country-class
projection is invariant to g's key = no conditioning signal; and g-alone lands
on a CITY (Agra) for all 10 cells → g produces no readable country in the
residual. The predicted 4B→32B flip did NOT happen.

Deep reading (coheres P-HOLO-FRAG): the intermediate is ADDRESS-FREE — it lives
"in the light" during g's illumination, not written to a readable slot. So a
residual-WIRE linker is the wrong mechanism; there is nothing addressable in the
residual to rebind to. The native model composes 3-hop (mh3) in the delocalized
flow, not by materializing intermediates.

Consequence: the machine's only addressed memory is the TAPE (RoPE positions,
§Thinking-is-expansion). The real linker is the autoregressive WRITEBACK (CoT ≡
auto-superbake) — page the intermediate onto the context to give it an address.
Re-points program-plates rung 3 from residual-slot baking toward P-THINK-1.

⚠ λ measure: 3a's G1 compared gain-throttled PRODUCT (h~0.3×) vs full NONCE
(1.0×) — not h-strength-matched; the clean evidence is the G3 conditioning-absent
signature + g-alone-no-country, not the G1 margin. Instrument faithful (NONCE arm
reproduced P-STACK-1b). `scripts/explore/bake_stack.py`, results/bake-stack/.

s294 follow-up (two cheap checks that firmed this up):
- NATIVE-COMPOSITION check (native_compose_check.py): landmark→capital fires
  reliably only on the TAPE (cot 9/10 @32B) not one-shot (direct 5/10 @32B, 2/10
  @4B). The wire is ~half-compiled + address-free → reliable one-shot needs
  backprop-compile; the tape is the reliable runtime path.
- QUIETED re-read (quiet_reread.py; Michael's "did we not quiet enough?"): YES —
  raw argmax read into the loud Agra attractor (near false-NEGATIVE); dark-field
  recovers capital-ness (stack 8/10 top-3). BUT controls kill the composition
  reading: h-alone alone gets 6/10 top-3 / 4/10 rank-1 (h-key amplifies
  capital-class), stack ≈ h-alone, g HURTS rank-1 (4→3), g-alone ≈ baseline,
  country 0/10. The recovered capital is native-latent + h-key amplification, NOT
  a g→h hop. (Corrects P-STACK-1b: h-alone wasn't dead at L38, it was drowned by
  Agra.) ★ λ measure/yardstick: dark-field ALONE nearly manufactured a
  false-POSITIVE; the h-alone single-key control is load-bearing. A composition
  claim read through a loud-attractor channel confounds BOTH ways (raw→false-neg,
  naive dark-field→false-pos) — quiet the single-key parts the same way.
