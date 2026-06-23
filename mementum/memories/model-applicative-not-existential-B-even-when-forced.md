💡 The model NEVER does existential-B composition — even when syntax FORCES the wide-scope
existential. It computes quantified sentences APPLICATIVELY (objects/witnesses as
arguments → C), regardless of scope marking. B was an artifact of OUR kernel, not the model.

s248 cont.3 (the causal test, Michael: "let's do that final test"). gen_scope_probes.py →
data/scope-probes.jsonl: 45 matched subj/verb/obj triples × 3 paired conditions —
  PLAIN "Every cat fears a dog."              (applicative GT S,B,C)
  CLEFT "There is a dog that every cat fears." (∃ fronted GT S,B,B,B, no C)
  RELCL "Every cat fears a dog that runs."     (∃ object GT S,B,B,B, no C)
ffn_scope_forcing.py decodes gate+attn, mean z per combinator over L25-30, paired Wilcoxon
within triple (predict ΔB>0 if the model CAN do existential-B when forced).

Qwen3-8B (45 triples): z(B) does NOT rise — it FALLS.
- FFN: plain z(B)=−0.104 → cleft −0.301 → relcl −0.227; ΔB cleft frac+ 0.18 p=1.0,
  relcl frac+ 0.02 p=1.0; B-share falls. C-share stays high (cleft Cprop 0.722→0.988).
- attn: plain z(B)=+0.31 → cleft −0.11 (ΔB med −0.43, p=1.0).
Robustly refuted in BOTH registers and BOTH forcing constructions.

⇒ The model has ONE compositional strategy: APPLICATION (C), not B-composition. Forcing
the existential syntactically routes it EVEN MORE through C, never B. INTERPRETATION: B is
an artifact of OUR bracket-abstraction kernel (Turner emits B to thread quantifiers), not a
necessary feature of how a system composes. "B inherent from the ordering" = our kernel's
ordering; the model's actual β-program is C-applicative.

CAVEATS: cleft/relcl differ in surface form from plain (not perfect minimal pairs) — but
the direction (B falls, opposite the prediction) is robust across two forcings + both
registers; relcl (closest to plain) also falls. We measure B-crystal routing as the
composition proxy; a non-B-shaped ∃ composition would be missed (but that IS the finding).
The model may compose ∃ applicatively under the hood (apply predicate to a skolem → C).
