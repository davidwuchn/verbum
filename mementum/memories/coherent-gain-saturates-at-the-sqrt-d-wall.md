💡 P-CAPACITY-LAW (s301, results b90cdb8): the ternary store obeys closed-form
law at every gate — HRR decline β=−0.503 vs −½ (p=.005), time-Bragg 5.6σ,
replay exact through 1024 commits + undo + squash, 1-bit snapshot loss →
√(2/π). The one frozen FAIL is the finding: coherent gain does NOT grow in
SNR — it saturates at √D. Wrong-key noise = ‖state‖, and in the
shared-address register the state norm grows coherently with the signal:
SNR = kcD/√(k(1−c²)D + k²c²D) → √D, measured ≤5.5% error at every k
(33→65, wall 64). Gain is real in the CORRELATION register (∝ kcD; G3:
lives in address sharing — independent keys whiten it away, p=.0001);
discriminability against the medium's own energy caps at √D. The §3
"storage doesn't grow" escape hatch is bounded, not killed. Recursive λ
measure lesson: the oracle-rd-1 error class (right sign, wrong
normalization) reappeared inside our own pre-reg; the declared null caught
it — a tuned gate would have passed and buried the wall. Bonus observed:
one mid-chain collapse-checkpoint IMPROVES recall (crosstalk
normalization) — near rung-3b's internal-collapse target.
