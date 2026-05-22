🎯 reader-llm-dual-plate

The endgame: a reader LLM that puts the beam through TWO plates.

1. Teacher plate — full extraction from any large model (FFN + flat attention)
2. Stride-stack plate — our trained attention crystal (masks out teacher's attention)
3. Reader — tiny model that latches the beam starting point via relational loss

The stride-stack attention is a universal holographic reader head. Train it once.
For any new teacher: extract plate, retrain reader (hundreds of steps), done.
The reader learns only the starting orientation — where to enter the teacher's
plate so the beam follows the right path through the FFN beamformers.

Prerequisite: must first train stride-stack attention from scratch to get the
crystal for our geometry. That's the hard part. Everything after is cheap.
