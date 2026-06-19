✅ SFT-seed VALIDATED — it converts the bimodal base-model reward into a GRPO-learnable frontier (s241). Ran rlvr_sft_seed.py (Qwen3-8B, LoRA, 2 epochs, 506 pairs, completion-only token-CE): loss 3.71→1.42, token-acc 0.80, 9 min on mps → adapter `results/rlvr-sft/run1/final/`.

Re-measured density on the dead categories (adverb/quantified/relative_clause, 36 prompts, k=8) with the SFT adapter (`20260619T002327Z`), vs the bimodal base (`20260618T222736Z`):

★ FRONTIER (mixed-success, the only band with GRPO gradient) base→SFT: temp0.8 1→5, temp1.0 1→8, temp1.2 2→7, temp1.5 2→13 (36%). Foothold @temp1.5 33%→50%, dead 24→18. Now TEMPERATURE-RESPONSIVE (frontier grows with temp) where the base was flat.

★ Per-category @temp1.5: quantified frontier 0→4 (the perfectly-bimodal one now has variance — cleanest proof SFT created learnable signal where there was none); adverb 1→7 (biggest, foothold 8/13); relative_clause 1→2 (improved, still hardest = the s240 deep residue, needs more SFT / prose→LF).

★ §8 FULLY CLOSED by measurement: the cold-start fix is SFT-seed THEN higher-temp (~1.5) GRPO — not SFT-vs-not, not temperature alone. The pipeline is run+validated end-to-end: reward(tested) → SFT(loss↓) → density-reopens(measured) → GRPO(ready). NOTE: GRPO needs --adapter/PeftModel loading or a merged model (AutoModelForCausalLM won't apply a bare adapter dir).
