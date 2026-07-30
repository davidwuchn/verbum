💡 The multi-hop pipeline's stages are PINNED to absolute depth zones — the depth budget
is a missed-deadline problem, not sliding fuel. s280 depth-budget (Qwen3-4B, commit
46910e9, stage-resolved install sweep + fine bridge-swap window): class logit-lens peak
sits at L30-31 for EVERY install layer L5→L25 (zero variance = stronger than a failed
slide correlation); hop-2's bridge-reader operates L11-21 and closes sharply L23→L25.
Install too late (L17+) and hop-1 STILL completes (class acc 1.0-0.833, peak L31) but
its product arrives after the fixed reader has passed → covering falls to chance. Fuel
accounting: L_max_1hop=25, L_max_2hop=13, D_hop2=12, L_close=25. Drift control clean:
cos(d_E@L5,@L9)=0.61 composes 0.824 while cos@L17=0.61 is chance → basis drift ≠ the
cliff. Coheres with A1 zone-ablation (fixed ENRICH/COMMIT zones) and refines C8: depth
scheduling is ZONE-CAPACITY, the compute does not re-schedule around a moved input.
Consequence: 3-HOP-ROOM-AT-4B=False (4 < 12) — no install layer fixes a missing zone;
run d1 3-hop as a capacity experiment (pre-register 4B-FAIL / 27B-PASS = the strongest
depth-as-fuel evidence available, merges (d) into (c)). Instrument lesson: restrict
lens-peak search to post-install layers (bare-nonce prior fakes early peaks).
