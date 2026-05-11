🔄 Multi-cycle descending arm (3 cycles) collapsed dispatch to 3 ops (98.3%):
sub(61%), min_max(26%), and_or(11%). Much more concentrated than single-cycle
v10-vsm which spread across 4-5 ops. Hypothesis: 3× descending compute with
identical routing lets the model exploit one good op path rather than diversify.
Dead CycleContinue meant all cycles ran at full strength on all content,
removing any pressure to route differently per-cycle. Session 076.
