🔁 A "sharpens with scale" trend across a MIXED-family model set can be a
single-undercooked-model artifact. s211's topology share "0.33→0.79 with scale"
was driven entirely by pythia-160m (0.33); the clean within-Qwen3 series
(0.6B→4B→8B→14B→32B, s212) shows NO trend (Spearman −0.20) and 32B even reverses
(0.645, CI below 14B). The real picture: a scale-STABLE plateau ~0.7, not an
asymptote to 1.0.

Rules that fall out:
- Test scale claims on a CLEAN within-family series (one tokenizer/architecture,
  vary only size); cross-family size-ordering conflates architecture with scale.
- DROP undercooked tiny models from scale trends — a single low point at the
  small end manufactures a fake monotone climb.
- Report subsample CIs (m-out-of-n, frac≈0.8, WITHOUT replacement) for
  RDM-separation statistics. A with-replacement bootstrap injects duplicate
  probes → zero-distance same-label pairs → deflated within-class mean →
  spuriously inflated separation gap.
- When two metrics of "the same thing" disagree (sep_frac_sign reversed,
  agree_sign_full mildly rose), they measure different quantities (share of the
  separation gap vs RDM reconstruction); neither alone settles the claim.
