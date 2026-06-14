✅ s226 CAUSAL ABLATION of the HOF gather heads (Phase A/B were observational; this
is the necessity leg). Full head-knockout (zero the head's slice at o_proj input =
remove its QK gather + OV write) of the Phase-A top-8 gather heads, vs an equal number
of RANDOM heads (specificity). `scripts/experiments/hof_attention_ablation.py`,
5 models / 3 arch.

VERDICT (mixed, honest — λ measure):
- MECHANISM necessity 4/5: on the LIST stims the heads were found on, ablation
  disrupts the HOF aggregation token (KL@last) MORE than control AND more than random
  heads (Qwen3-14B/32B, OLMo, Mistral; 8B the lone fail = weakest observational model).
- GENERALIZATION (natural prose, diff-in-diff ΔNLL on engaged HOFs fold/reduce/filter/
  zip, map excluded per s225) 1/5: only OLMo decisive (t=+3.21). Directionally right in
  4/5 (gather > random) but underpowered (whole-sentence per-token NLL dilutes).
- Per-HOF signature COHERENT (OLMo): filter/fold/zip POSITIVE, map NEGATIVE — exactly
  consistent with s225 (map not in this FFN/attention-projection register).

⇒ in-domain causal necessity CONFIRMED; natural-prose necessity SUGGESTIVE not robust
(IOU: stronger readout, e.g. last-content-word logprob or activation-patching, not
whole-sentence NLL). The list-KL-at-last-token is noisy (gather heads sit upstream of
the immediate logit) — prose diff-in-diff is the principled metric.
