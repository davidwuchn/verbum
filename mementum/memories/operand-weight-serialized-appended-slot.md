✅ The installed operand graduates hook → WEIGHTS: E1 WEIGHT-SERIALIZED confirmed at Qwen3-4B
(s279, wrapper/operand_bake.py). ONE appended MLP recognition neuron at layer L reproduces the
runtime operand-install hook with NO hook: baked covering 0.824 ≈ hook 0.941 (agrees 15/17; the
2 disagreements = the mammal→fur weak cell inherited from the content direction, not a bake
artifact), nonce-specific (shuffled-key 0.353=chance, decoy nonce inert, real words unharmed).

MECHANISM (SuperBake §6 bias-free fix, method reference; our code MIT): Qwen3 MLP has no bias,
so a neuron computes only x·k. Make the key k PERPENDICULAR to the carrier μ̂ (population mean
dir) → x·k ≡ (x−μ)·k identically → silu's knee lands at the mean with NO bias term. Selectivity
from the multiplicative gate×up form with gate=up: neuron = silu(z)·z, so a token at ratio ρ of
the target gets ~ρ² of the output ("born hard"). Slot: gate_row=up_row=β·k, down_col=scale·d_E/m
with z_nonce=β·⟨k,x_nonce⟩ set to target_z, m=silu(z)·z.

⚠ BUG (feed-forward): the payload must be scale·d_E, NOT d_E — the appended slot must match the
hook DOSE (under-dose → 0.647; correct → 0.824). ⚠ SCOPE: in-memory weight edit (uniform-E MLP
expand + save() a stock checkpoint = the f2/f3 quant prereq); 4B; one operand at a time; 0.6B
squish (hook itself fails, but baked TRACKS hook = mechanism-equivalent). Next: f2 quant-survival
measured AS a routing-topology change; f3 ternary-mirror robustify = the shipping artifact.
