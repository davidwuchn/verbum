💡 Routing geometry is the function INVENTORY (which combinators exist + how they
relate); capability is USAGE (how to drive them) = the CONTINUATION, which must be
TRAINED, not folded. Michael (s224): "capability won't ever transfer with just
routing geometry — it needs to be trained so the model can use the functions the
geometry gives it." Maps to routing⊕continuation: routing rules COMPOSITION (foldable,
universal, s219 reverse-harvest +0.78); continuation rules RECURSION {Y,W,WHNF} = "how
to use" (lives in the architecture's recurrence, per-task, trained). Triangulated 3
ways: s223 b-column (GC hidden 1.000, zero function), s223 Goodhart (agreement ≠
capability), s224 2-contributor fold (GC fold→teacher +0.84 yet dCE +0.15). Geometry
match = NECESSARY not SUFFICIENT. ⇒ distributed protocol is TWO-PHASE: (1) fold the
shared routing geometry (cheap, donates the function basis) → (2) train the
continuation to drive it (the real per-node capability work). Decisive test:
FOLD-THEN-TRAIN-CONTINUATION — does CE recover faster than continuation-from-scratch?
✅ CONFIRMED (s224, 3 seeds, fold_then_train_continuation.py): freeze folded routing
(inventory, 132k) + train continuation (usage, 604k) → CE 2.44→2.05, BELOW A-baseline
2.27; beats RANDOM frozen inventory (scratch 2.135, clean separation) ⇒ geometry is
real/useful NOT inert; folded geometry PERSISTS through continuation training
(z 2.26→2.38, L<1). Geometry necessary-not-sufficient; good geometry + trained
continuation = capability. Two-phase distributed protocol (fold geometry → train
continuation) validated. (F_cont≈A_cont: homogeneous shards, heterogeneous = next.)
