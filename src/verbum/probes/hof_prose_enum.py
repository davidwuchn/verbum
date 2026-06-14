"""Enumerated-prose HOF stimuli — does the gather circuit RE-ENGAGE when natural
prose carries a LITERAL enumeration?

THE QUESTION (session 227, Michael): the gather heads are strongly causally
necessary in-domain (explicit lists, hof_lists) but only weakly necessary on plain
prose (hof_prose). Hypothesis: plain prose has no literal list to gather over, so the
explicit-enumeration gather mechanism is the right circuit only when an enumeration is
present. Test: inject an explicit "A, B, and C" enumeration into naturalistic prose
and re-measure causal necessity.

DESIGN — minimal pairs where BOTH members carry the SAME enumeration:
  Each pair is (hof, control), both listing the same three items "A, B, and C". The
  HOF member applies a higher-order operation OVER the items (iterate / accumulate /
  select-subset / pair); the control mentions the same three items but does a
  NON-iterative thing (a single action, a static grouping, or picks one). Because the
  enumeration is held CONSTANT across the pair, the diff-in-diff isolates the
  HOF ITERATION over the list — not the mere presence of a list. Contrast this set's
  necessity against hof_prose (no enumeration): if necessity recovers here, the
  gather circuit keys off explicit enumeration and plain prose simply lacks a target.

  Functions: map (apply to each), filter (keep a subset), fold (accumulate to one),
  reduce (collapse to one), zip (pair each with a counterpart).

Same API/dataclass as hof_prose so the ablation instruments load it unchanged.

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "FUNCTIONS",
    "ProsePair",
    "by_function",
    "function_names",
    "pair_counts",
    "prose_pairs",
]


@dataclass(frozen=True, slots=True)
class ProsePair:
    """An enumerated HOF sentence and its matched enumerated non-HOF control."""

    id: str
    function: str            # map | filter | fold | reduce | zip
    hof: str                 # applies the HOF over the listed items
    control: str             # same three items, no HOF (single / static / pick-one)
    domain: str


FUNCTIONS: tuple[str, ...] = ("map", "filter", "fold", "reduce", "zip")


# (hof, control, domain) — both carry the same "A, B, and C" enumeration.
_MAP: list[tuple[str, str, str]] = [
    (
        "She watered the rose, the fern, and the ivy, tending to each in the",
        "She watered the rose, the fern, and the ivy, then rested in the",
        "nature",
    ),
    (
        "He checked the stove, the oven, and the kettle, switching off each in the",
        "He checked the stove, the oven, and the kettle, then left the",
        "everyday",
    ),
    (
        "The teacher graded the essay, the quiz, and the report, marking each in the",
        "The teacher graded the essay, the quiz, and the report, then closed the",
        "education",
    ),
    (
        "The nurse visited Ward A, Ward B, and Ward C, charting each on the",
        "The nurse visited Ward A, Ward B, and Ward C, then paused at the",
        "medicine",
    ),
    (
        "The clerk stamped the form, the deed, and the permit, signing each at the",
        "The clerk stamped the form, the deed, and the permit, then filed the",
        "law",
    ),
    (
        "She repainted the gate, the bench, and the shed, redoing each in the",
        "She repainted the gate, the bench, and the shed, then admired the",
        "everyday",
    ),
    (
        "He tuned the violin, the cello, and the bass, adjusting each before the",
        "He tuned the violin, the cello, and the bass, then opened the",
        "arts",
    ),
    (
        "The waiter cleared table four, table five, and table six, wiping each near "
        "the",
        "The waiter cleared table four, table five, and table six, then reached the",
        "cooking",
    ),
    (
        "The coach timed the sprint, the relay, and the hurdles, recording each by the",
        "The coach timed the sprint, the relay, and the hurdles, then watched the",
        "sports",
    ),
    (
        "The intern scanned the contract, the invoice, and the memo, copying each onto "
        "the",
        "The intern scanned the contract, the invoice, and the memo, then mailed the",
        "commerce",
    ),
    (
        "The guide noted the tower, the bridge, and the dome, describing each from the",
        "The guide noted the tower, the bridge, and the dome, then boarded the",
        "travel",
    ),
    (
        "The tech updated the laptop, the router, and the server, patching each on the",
        "The tech updated the laptop, the router, and the server, then rebooted the",
        "technology",
    ),
    (
        "She tagged the lion, the zebra, and the heron, photographing each at the",
        "She tagged the lion, the zebra, and the heron, then left the",
        "nature",
    ),
    (
        "The farmer inspected the wheat, the barley, and the oats, weighing each in "
        "the",
        "The farmer inspected the wheat, the barley, and the oats, then closed the",
        "nature",
    ),
]

_FILTER: list[tuple[str, str, str]] = [
    (
        "Of the apples, the pears, and the plums, she kept only the ones that were",
        "Of the apples, the pears, and the plums, she grabbed a single one that was",
        "cooking",
    ),
    (
        "From the essays, the quizzes, and the reports, he forwarded only those that "
        "met the",
        "From the essays, the quizzes, and the reports, he forwarded a single one "
        "meeting the",
        "education",
    ),
    (
        "Among the cars, the vans, and the trucks, they flagged only the ones above "
        "the",
        "Among the cars, the vans, and the trucks, they flagged a single one above the",
        "everyday",
    ),
    (
        "Of the claims, the deeds, and the permits, the judge admitted only those "
        "bearing the",
        "Of the claims, the deeds, and the permits, the judge admitted a single one "
        "bearing the",
        "law",
    ),
    (
        "From the blood, the urine, and the tissue samples, the lab returned only "
        "those above the",
        "From the blood, the urine, and the tissue samples, the lab returned a single "
        "one above the",
        "medicine",
    ),
    (
        "Among the roses, the tulips, and the lilies, she cut only the ones past their",
        "Among the roses, the tulips, and the lilies, she cut a single one past its",
        "nature",
    ),
    (
        "Of the laptops, the tablets, and the phones, QA rejected only those that "
        "failed the",
        "Of the laptops, the tablets, and the phones, QA rejected a single one that "
        "failed the",
        "technology",
    ),
    (
        "From the flights, the trains, and the buses, the agent booked only those "
        "before the",
        "From the flights, the trains, and the buses, the agent booked a single one "
        "before the",
        "travel",
    ),
    (
        "Among the sprinters, the jumpers, and the throwers, the coach kept only those "
        "who cleared the",
        "Among the sprinters, the jumpers, and the throwers, the coach kept a single "
        "one who cleared the",
        "sports",
    ),
    (
        "Of the crates, the barrels, and the sacks, the buyer accepted only those that "
        "survived the",
        "Of the crates, the barrels, and the sacks, the buyer accepted a single one "
        "that survived the",
        "commerce",
    ),
    (
        "From the sketches, the prints, and the canvases, the gallery hung only those "
        "that fit the",
        "From the sketches, the prints, and the canvases, the gallery hung a single "
        "one that fit the",
        "arts",
    ),
    (
        "Among the emails, the texts, and the calls, she saved only those from the",
        "Among the emails, the texts, and the calls, she saved a single one from the",
        "everyday",
    ),
    (
        "Of the cabbages, the carrots, and the leeks, the chef used only those still",
        "Of the cabbages, the carrots, and the leeks, the chef used a single one still",
        "cooking",
    ),
    (
        "From the puppies, the kittens, and the rabbits, they chose only those with "
        "the",
        "From the puppies, the kittens, and the rabbits, they chose a single one with "
        "the",
        "nature",
    ),
]

_FOLD: list[tuple[str, str, str]] = [
    (
        "He combined the flour, the sugar, and the butter into one smooth",
        "He set the flour, the sugar, and the butter beside one clean",
        "cooking",
    ),
    (
        "She merged the London, Paris, and Tokyo branches into one global",
        "She moved the London, Paris, and Tokyo files into one spare",
        "commerce",
    ),
    (
        "They folded the red, the gold, and the blue threads into one woven",
        "They laid the red, the gold, and the blue threads near one empty",
        "arts",
    ),
    (
        "The clerk totaled the rent, the power, and the water bills into one monthly",
        "The clerk copied the rent, the power, and the water bills onto one blank",
        "everyday",
    ),
    (
        "The chef blended the mango, the banana, and the lime into one thick",
        "The chef sliced the mango, the banana, and the lime onto one white",
        "cooking",
    ),
    (
        "The team rolled the login, the search, and the upload fixes into one stable",
        "The team logged the login, the search, and the upload fixes in one shared",
        "technology",
    ),
    (
        "The valley gathered the brook, the creek, and the spring into one wide",
        "The hiker crossed the brook, the creek, and the spring near one tall",
        "nature",
    ),
    (
        "The editor wove the prologue, the climax, and the ending into one finished",
        "The editor read the prologue, the climax, and the ending from one printed",
        "arts",
    ),
    (
        "The charity pooled the gala, the auction, and the raffle takings into one "
        "grand",
        "The charity recorded the gala, the auction, and the raffle takings on one "
        "neat",
        "commerce",
    ),
    (
        "The lab averaged the morning, the noon, and the evening readings into one "
        "daily",
        "The lab stored the morning, the noon, and the evening readings in one labeled",
        "medicine",
    ),
    (
        "The scorer summed the first, the second, and the third quarters into one "
        "final",
        "The scorer marked the first, the second, and the third quarters on one paper",
        "sports",
    ),
    (
        "She knitted the front, the back, and the sleeves into one whole",
        "She folded the front, the back, and the sleeves onto one flat",
        "arts",
    ),
    (
        "He consolidated the card, the loan, and the mortgage into one monthly",
        "He reviewed the card, the loan, and the mortgage under one short",
        "commerce",
    ),
    (
        "The station combined the rain, the snow, and the hail totals into one "
        "seasonal",
        "The station noted the rain, the snow, and the hail totals on one daily",
        "nature",
    ),
]

_REDUCE: list[tuple[str, str, str]] = [
    (
        "The analyst distilled the sales, the costs, and the returns into one annual",
        "The analyst filed the sales, the costs, and the returns under one local",
        "commerce",
    ),
    (
        "The script compressed the logs, the traces, and the dumps into one summary",
        "The script opened the logs, the traces, and the dumps as one plain",
        "technology",
    ),
    (
        "She condensed the intro, the body, and the close into one short",
        "She copied the intro, the body, and the close onto one short",
        "education",
    ),
    (
        "The chef reduced the stock, the wine, and the cream into one rich",
        "The chef poured the stock, the wine, and the cream into one thin",
        "cooking",
    ),
    (
        "The jury distilled the motive, the means, and the alibi into one clear",
        "The jury read the motive, the means, and the alibi from one thick",
        "law",
    ),
    (
        "The model collapsed the height, the width, and the depth into one single",
        "The model logged the height, the width, and the depth as one raw",
        "technology",
    ),
    (
        "Headquarters merged the north, the south, and the central reports into one "
        "global",
        "Headquarters filed the north, the south, and the central reports as one local",
        "commerce",
    ),
    (
        "The census reduced the city, the town, and the village counts into one "
        "national",
        "The census recorded the city, the town, and the village counts as one local",
        "education",
    ),
    (
        "The funnel narrowed the leads, the trials, and the demos into one qualified",
        "The rep called the leads, the trials, and the demos from one short",
        "commerce",
    ),
    (
        "The system folded the morning, the midday, and the night counts into one "
        "final",
        "The system logged the morning, the midday, and the night counts as one raw",
        "technology",
    ),
    (
        "The committee distilled the budget, the timeline, and the scope into one "
        "unified",
        "The committee read the budget, the timeline, and the scope from one minor",
        "law",
    ),
    (
        "The dashboard aggregated the wind, the rain, and the heat readings into one "
        "overall",
        "The dashboard showed the wind, the rain, and the heat readings as one raw",
        "technology",
    ),
    (
        "The archive compressed the letters, the diaries, and the maps into one single",
        "The archive stored the letters, the diaries, and the maps as one plain",
        "education",
    ),
    (
        "The charity pooled the cash, the checks, and the pledges into one grand",
        "The charity counted the cash, the checks, and the pledges as one modest",
        "commerce",
    ),
]

_ZIP: list[tuple[str, str, str]] = [
    (
        "He matched the red, the blue, and the green wires each to its own",
        "He bundled the red, the blue, and the green wires under one shared",
        "technology",
    ),
    (
        "The registrar paired the freshmen, the juniors, and the seniors each with a "
        "returning",
        "The registrar gathered the freshmen, the juniors, and the seniors into one "
        "large",
        "education",
    ),
    (
        "She fitted the brass, the iron, and the silver keys each to its matching",
        "She dropped the brass, the iron, and the silver keys into one small",
        "everyday",
    ),
    (
        "The host seated the bride, the groom, and the guests each beside a chosen",
        "The host welcomed the bride, the groom, and the guests into one wide",
        "everyday",
    ),
    (
        "The app linked the photo, the video, and the audio each to its recorded",
        "The app saved the photo, the video, and the audio in one shared",
        "technology",
    ),
    (
        "The coach assigned the forward, the midfielder, and the keeper each to an "
        "opposing",
        "The coach called the forward, the midfielder, and the keeper onto one open",
        "sports",
    ),
    (
        "The translator aligned the German, the French, and the Spanish lines each "
        "with its English",
        "The translator read the German, the French, and the Spanish lines from one "
        "printed",
        "education",
    ),
    (
        "The pharmacist matched the tablet, the syrup, and the cream each to the right",
        "The pharmacist placed the tablet, the syrup, and the cream on one clean",
        "medicine",
    ),
    (
        "The clerk joined the invoice, the receipt, and the order each to its "
        "corresponding",
        "The clerk stacked the invoice, the receipt, and the order in one neat",
        "commerce",
    ),
    (
        "At the gate they matched the child, the parent, and the elder each to an "
        "assigned",
        "At the gate they waved the child, the parent, and the elder through one open",
        "travel",
    ),
    (
        "In the lab they paired the sample, the swab, and the slide each with a "
        "control",
        "In the lab they logged the sample, the swab, and the slide in one shared",
        "medicine",
    ),
    (
        "The teacher coupled the question, the hint, and the answer each with its "
        "model",
        "The teacher wrote the question, the hint, and the answer on one shared",
        "education",
    ),
    (
        "The designer matched the scarlet, the amber, and the teal each to a "
        "complementary",
        "The designer chose the scarlet, the amber, and the teal for one single",
        "arts",
    ),
    (
        "The court assigned the plaintiff, the witness, and the juror each to a "
        "separate",
        "The court called the plaintiff, the witness, and the juror into one shared",
        "law",
    ),
]


_RAW: dict[str, list[tuple[str, str, str]]] = {
    "map": _MAP,
    "filter": _FILTER,
    "fold": _FOLD,
    "reduce": _REDUCE,
    "zip": _ZIP,
}


def _build() -> list[ProsePair]:
    out: list[ProsePair] = []
    for fn in FUNCTIONS:
        for i, (hof, control, domain) in enumerate(_RAW[fn]):
            out.append(ProsePair(
                id=f"enum_{fn}_{i:03d}",
                function=fn, hof=hof, control=control, domain=domain,
            ))
    return out


_PAIRS: list[ProsePair] = _build()


def prose_pairs() -> list[ProsePair]:
    """All enumerated HOF prose minimal pairs."""
    return list(_PAIRS)


def by_function(name: str) -> list[ProsePair]:
    return [p for p in _PAIRS if p.function == name]


def function_names() -> list[str]:
    return list(FUNCTIONS)


def pair_counts() -> dict[str, int]:
    return {fn: len(by_function(fn)) for fn in FUNCTIONS}


if __name__ == "__main__":
    import json
    print(json.dumps(pair_counts(), indent=2))
    print(f"total pairs: {len(_PAIRS)}")
