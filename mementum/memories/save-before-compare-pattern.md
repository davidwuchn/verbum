❌ Lost hours of training to a post-training crash — save-first pattern

Session 106: relational distill ran for hours at 21 tok/s. Training
completed successfully. Then the comparison/display code crashed on
a missing key (`final_student_rdms` absent from skipped condition).
Results never saved. Hours wasted.

Fix: save-first architecture.
1. Save results IMMEDIATELY after training, BEFORE any comparison code
2. Wrap comparison in try/except (display crash can't kill data)
3. Add incremental checkpoints DURING training (history + weights)

Pattern: ∀expensive_computation → save(result) → try: display(result)
Never put display/analysis code between compute and save.

Also: batch probe forward passes. 311 sequential unbatched forward
passes = 311 MPS kernel launches = 21 tok/s. Pad + batch = 1 launch.
