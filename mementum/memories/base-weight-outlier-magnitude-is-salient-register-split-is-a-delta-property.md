💡 The routing⊥magnitude register split is a property of a TRAINED FUNCTIONAL DELTA, not of a raw pretrained weight matrix — base-weight outlier MAGNITUDE is salient.

s306 §P-COMPANDING-QUANT @Qwen3-4B (4b89726). Kept the top-1% base FFN outliers as ternary SIGN vs fp16 at matched bit budget, judged by downstream CE. fp16 decisively beats ternary at every usable budget (b3 5.47 vs 7.34, b4 5.77 vs 7.12, p=1e-4) → MAGNITUDE-SALIENT. Tell-tale: ternarizing the TRUE outliers (companding_mag@b4 7.12) hurts MORE than random (shuffle 5.78) — their magnitude carries the function. Coherence lost as selector too (MAGNITUDE-SELECTS, matching s171; calib thin but gap decisive).

So: a gradient-written delta isolates the routing edge (sign carries it → ternarizes losslessly, s269/s304/s306 retention ~1.0); a base matrix superposes routing AND value in the same magnitudes → outliers salient (AWQ/SpQR right about base weights). Thesis SCOPED: quantize the DELTA to ternary routing; keep the base in magnitude. Not a refutation — a sharpening.

★ λ measure lesson: the frozen verdict mislabeled HOST-DAMAGED because C5 anchored on the TREATMENT arm (companding_mag@b4) not a host-integrity arm (int_uniform@b4). Anchor sanity gates on controls, not treatments.
