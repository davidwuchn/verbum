🔁 Mistral-7B-v0.3 and OLMo-2-1124-13B are BASE models — `tok.chat_template` is None,
so `tok.apply_chat_template(...)` raises ValueError("Cannot use chat template ...").
A try/except that retries apply_chat_template still crashes. Correct pattern: guard
`if getattr(tok, "chat_template", None):` and fall back to the RAW few-shot prompt
(the s003 base-model continuation cue — prompt ends with the answer marker, e.g.
"Proof:"). Record `prompt_mode` ∈ {chat, base/raw} in the result for provenance.
Second trap (s228): a single `none`/negative DEMO in the few-shot anchors a raw base
continuation toward copying it (OLMo answered `none` 15/20, sensitivity 0.00) — base
models need their own gate (more shots, no degenerate anchor) and their scores are NOT
comparable to chat models without it. The chat models (Qwen series) apply_chat_template
with enable_thinking=False cleanly. Bit me mid-run in proof_inhabitation.py; cost a
re-run of the two base models.
