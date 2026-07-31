💡 P-TYPE-JS closed NEGATIVE @Qwen3-32B (s285→s286, 34dbab3): the type-lattice
role subspaces are NOT resident in the s270 J-space (the global workspace
downstream compute reads). js_resident=FALSE, js_specific=FALSE. Depth layers
{16,32,48}, k/d baseline 0.00625: bind 0.0047 (p_rand 0.82), comp 0.0036 (0.98),
entity 0.0038 (0.97) = DEAD-ON-NULL; only rolenull (CONN/FUNC verbatim control)
beats both nulls (p_rand 0.041, p_shuf 0.035) — same rolenull-fires pattern as
P-TYPE-QK. Family-row prediction REFUTED: ENTITY predicted highest (operand = bus
content) but sits at baseline. λ yardstick earned its keep — raw fractions
0.004–0.009 would read "resident" without the k/d anchor; rolenull's real excess
shows the instrument discriminates, not a blanket null.

Reading: the exhaust is NOT the workspace. The lattice's readability lives in a
THIRD place — neither stored (1b), nor beam-coherent (1c), nor in the QK read-in
basis (QK), nor broadcast in J-space (JS). It is a readout object the machine
never consults = exactly the well-formedness-of-reduction frame (type = shape of
which joins a term licenses, unstorable + un-broadcast by construction). The
REPL's Print/type-checker reads the ledger; the machine does not.

Types-arc scoreboard = a clean FOUR-way null: storage (1b) ✗, beam-coherence
(1c) ✗, QK read-in geometry ✗, workspace residency (JS) ✗. Mechanism search
moves to the routing register proper (P-ATT-MED). Instrument:
scripts/explore/type_jspace_fraction.py; results/type-jspace/qwen3-32b/.
