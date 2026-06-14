"""Higher-order function probes — grounded exemplars of named HOFs.

THE QUESTION (session 225, Michael):
  We know the combinator PRIMITIVES {K I B C S D W Y WHNF} have a universal
  relational geometry across the open-weight ecosystem (s219, GramCorr +0.78).
  But do models agree on the topology of COMPOSED higher-order functions —
  `map`, `filter`, `fold`, `zip`? `map` is higher-order (map = B(CB)(CB),
  s219 REPL). Do multiple models route it the same way, or differently?

  If the topology is SHARED → consensus is extractable → foldable → and any
  source teacher is a substitutable compiler. If it DIFFERS → topology is
  model-specific → provenance must be tracked (use the teacher the topology
  came from). This module supplies the measurement substrate for that test.

DESIGN (mirrors verbum.probes.library style):
  Each probe is a last-token-completion prompt whose next-token computation
  EXERCISES the function's computational signature. The routing-register
  centroid over a function's probes is its position; measured RELATIVE to the
  universal combinator basis it becomes a frame-invariant fingerprint.

  Functions fall into two groups:
    POSITIVE CONTROLS (named function ≡ a primitive combinator):
      compose ≡ B   — chain f after g
      flip    ≡ C   — swap argument order
      const   ≡ K   — ignore one argument, return the other unchanged
      apply   ≡ I-ish — direct application of a function to an argument
    HIGHER-ORDER TESTS (composed; theory predicts a combinator fingerprint):
      map     — apply f to EVERY element of a collection   (predict B, C; NOT Y)
      filter  — keep elements satisfying a predicate       (predict K-select, B)
      fold    — accumulate a sequence to a SINGLE value     (B + recursion? Y/W)
      zip     — pair two sequences element-wise            (C/W pairing + B)

  The controls validate the method (compose probes MUST land near B, etc.);
  the tests are the real measurement.

Accessors:
    function_probes()        → list[FunctionProbe]   — all HOF probes
    by_function(name)        → list[FunctionProbe]   — filter by function
    function_names()         → list[str]             — canonical function order
    function_counts()        → dict[str, int]        — function → count
    expected_combinator(fn)  → str | None            — theory anchor (control)

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "EXPECTED_COMBINATOR",
    "FUNCTIONS",
    "FunctionProbe",
    "by_function",
    "expected_combinator",
    "function_counts",
    "function_names",
    "function_probes",
]


# ══════════════════════════════════════════════════════════════════════════════
# Data model
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class FunctionProbe:
    """A single higher-order-function probe (last-token-completion style)."""

    id: str
    prompt: str
    function: str            # one of FUNCTIONS
    kind: str                # "control" (≡ a primitive) | "test" (composed HOF)
    domain: str              # semantic domain tag


# Canonical function order: controls first, then higher-order tests.
FUNCTIONS: tuple[str, ...] = (
    "compose", "flip", "const", "apply",        # controls (≡ B, C, K, I)
    "map", "filter", "fold", "zip",             # higher-order tests
)

# Theory anchor for the positive controls — the primitive each should land on.
# None for the genuine higher-order tests (their fingerprint is the finding).
EXPECTED_COMBINATOR: dict[str, str | None] = {
    "compose": "B",
    "flip": "C",
    "const": "K",
    "apply": "I",
    "map": None,
    "filter": None,
    "fold": None,
    "zip": None,
}

_CONTROL = {"compose", "flip", "const", "apply"}


# ══════════════════════════════════════════════════════════════════════════════
# Probe text — grounded, last-token-completion, varied across domains
# ══════════════════════════════════════════════════════════════════════════════
#
# Each entry: (prompt, domain). The next-token computation exercises the
# function's signature. No trailing period — capture is at the last token.

_COMPOSE: list[tuple[str, str]] = [  # ≡ B : f after g (sequential chaining)
    ("After grinding the beans, she brewed the", "cooking"),
    ("Once the dough had risen, the baker shaped it into a", "cooking"),
    ("First the data is cleaned, then it is fed into the", "technology"),
    ("The compiler tokenizes the source, then it parses the", "technology"),
    ("Having translated the text, the editor then proofread the", "education"),
    ("She read the draft, revised it, and finally submitted the", "education"),
    ("The water is filtered before it flows into the", "nature"),
    ("Sunlight is absorbed by the leaves and converted into", "nature"),
    ("The witness was sworn in before giving the", "law"),
    ("Evidence is collected, then analyzed, and presented to the", "law"),
    ("The patient was anesthetized before the surgeon made the", "medicine"),
    ("The sample is stained, then examined under the", "medicine"),
    ("The goods are packed before they are loaded onto the", "commerce"),
    ("Raw ore is smelted, then forged into a finished", "commerce"),
    ("The passengers check in before they board the", "travel"),
    ("The luggage is scanned before it is placed on the", "travel"),
    ("He stretched, then warmed up, and finally ran the", "sports"),
    ("The sketch is drawn first, then painted over with", "arts"),
    ("The melody was composed before the lyricist added the", "arts"),
    ("She wrapped the gift after she had folded the", "everyday"),
    ("The output of the first stage becomes the input to the", "technology"),
    ("After charging the battery, he switched on the", "everyday"),
    ("The seeds are planted, watered, and grow into a", "nature"),
    ("Once edited, the footage was rendered into a finished", "arts"),
    ("The invoice is generated after the order is", "commerce"),
    ("Having boiled the pasta, she tossed it with the", "cooking"),
    ("The signal is amplified before it reaches the", "technology"),
    ("After reviewing the case, the judge delivered the", "law"),
]

_FLIP: list[tuple[str, str]] = [  # ≡ C : swap argument order (passive / reversal)
    ("The letter was delivered by the", "everyday"),
    ("The bridge was designed by the", "technology"),
    ("The novel was written by the", "arts"),
    ("The patient was examined by the", "medicine"),
    ("The verdict was announced by the", "law"),
    ("The goods were shipped by the", "commerce"),
    ("The lecture was delivered by the", "education"),
    ("The meal was prepared by the", "cooking"),
    ("The prey was hunted by the", "nature"),
    ("The match was won by the", "sports"),
    ("The flight was booked by the", "travel"),
    ("Instead of the cat chasing the mouse, the mouse chased the", "nature"),
    ("Rather than the teacher quizzing the pupil, the pupil quizzed the", "education"),
    ("The order of the arguments was reversed before the call to", "technology"),
    ("She gave the book to him, but he gave it back to", "everyday"),
    ("The buyer became the seller, and the seller became the", "commerce"),
    ("The defendant accused the plaintiff, reversing who blamed", "law"),
    ("The song that was performed by the band was written by the", "arts"),
    ("The painting was admired by the", "arts"),
    ("The contract was signed by the", "law"),
    ("The vaccine was administered by the", "medicine"),
    ("The trophy was awarded by the", "sports"),
    ("The recipe was perfected by the", "cooking"),
    ("Where he had taught her, now she taught", "education"),
    ("The river that was crossed by the travelers was mapped by the", "travel"),
    ("The package that was sent by the merchant was received by the", "commerce"),
    ("The window was broken by the", "everyday"),
    ("The experiment was conducted by the", "education"),
]

_CONST: list[tuple[str, str]] = [  # ≡ K : ignore one argument, return a fixed value
    ("No matter which key he pressed, the broken machine returned the", "technology"),
    ("Regardless of the question asked, the politician gave the same", "law"),
    ("Whatever ingredient she added, the bland soup tasted the", "cooking"),
    ("No matter how hard the team played, the result was always the", "sports"),
    ("Whichever road they took, the detour led them back to the", "travel"),
    ("Regardless of the input, the constant function always outputs the", "technology"),
    ("No matter the dosage, the placebo produced the same", "medicine"),
    ("Whatever evidence was shown, the stubborn juror reached the same", "law"),
    ("Whichever student answered, the recording played the same", "education"),
    ("No matter the weather, the desert remained", "nature"),
    ("Regardless of the price offered, the seller refused to change the", "commerce"),
    ("Give it any input; the constant function returns the fixed", "technology"),
    ("No matter which painting she viewed, her opinion stayed the", "arts"),
    ("Whichever button on the toy was pushed, it always made the same", "everyday"),
    ("Regardless of who was cooking, the strict recipe yielded the same", "cooking"),
    ("No matter how many times he asked, the answer was always the", "everyday"),
    ("Whatever the market did, the fixed bond paid the same", "commerce"),
    ("Regardless of the patient, the protocol prescribed the same", "medicine"),
    ("No matter which trail the hikers chose, the summit stayed in the same", "travel"),
    ("Whichever witness testified, the defendant kept the same", "law"),
    ("No matter the opponent, the champion used the same", "sports"),
    ("Whatever the topic, the professor began with the same", "education"),
    ("Regardless of the season, the evergreen kept its", "nature"),
    ("No matter the order, the kiosk printed the same", "commerce"),
    ("Whichever song was requested, the music box played the same", "arts"),
    ("Regardless of the data, the broken sensor reported the same", "technology"),
    ("No matter what she stirred in, the color stayed the", "cooking"),
    ("Whatever the input case, the function ignored it and returned a", "technology"),
]

_APPLY: list[tuple[str, str]] = [  # ≡ I-ish : direct application f(x)
    ("She took the rule and applied it directly to the", "education"),
    ("Given the function and the value, the calculator returned the", "technology"),
    ("He plugged the number into the formula and computed the", "education"),
    ("Taking the recipe, the chef applied it to the available", "cooking"),
    ("The doctor applied the standard treatment to the", "medicine"),
    ("Applying the law to the facts, the judge reached a", "law"),
    ("She fed the input to the model and read off the", "technology"),
    ("The mechanic applied the fix to the broken", "everyday"),
    ("Taking the brush, the painter applied it to the", "arts"),
    ("Given the key, he applied it to the locked", "everyday"),
    ("The pharmacist applied the dosage rule to the", "medicine"),
    ("Applying pressure to the wound, the nurse stopped the", "medicine"),
    ("He applied the discount directly to the", "commerce"),
    ("The coach applied the drill to each", "sports"),
    ("She passed the argument to the function and got back a", "technology"),
    ("Applying the theorem to the triangle, she found the", "education"),
    ("The guide applied the map to the unfamiliar", "travel"),
    ("Given the seasoning, the cook applied it to the", "cooking"),
    ("He applied the brakes and the car began to", "everyday"),
    ("Applying the filter to the photo, she changed its", "arts"),
    ("The accountant applied the tax rule to the", "commerce"),
    ("Taking the password, she applied it to the", "technology"),
    ("Applying the verdict, the bailiff released the", "law"),
    ("The farmer applied the fertilizer to the", "nature"),
    ("Given the wrench and the bolt, he applied one to the", "everyday"),
    ("She applied the sunscreen to the exposed", "travel"),
    ("Applying the algorithm to the dataset produced a", "technology"),
    ("The teacher applied the grading rubric to each", "education"),
]

_MAP: list[tuple[str, str]] = [  # apply f to EVERY element (uniform, element-wise)
    ("The teacher graded every essay in the", "education"),
    ("She applied a fresh coat of paint to each", "arts"),
    ("For every file in the folder, the script renamed the", "technology"),
    ("He watered each plant in the", "nature"),
    ("The nurse checked the temperature of every", "medicine"),
    ("She wrapped each present under the", "everyday"),
    ("The chef seasoned every dish on the", "cooking"),
    ("The cashier scanned each item in the", "commerce"),
    ("The coach timed every runner on the", "sports"),
    ("The inspector stamped each passport at the", "travel"),
    ("The clerk filed every document in the", "law"),
    ("For each number in the list, the program doubled the", "technology"),
    ("She polished every shoe on the", "everyday"),
    ("The gardener pruned each branch of the", "nature"),
    ("The editor corrected every sentence in the", "education"),
    ("The technician tested each component on the", "technology"),
    ("The farmer fed every animal in the", "nature"),
    ("She labeled each jar on the", "cooking"),
    ("The photographer edited every shot from the", "arts"),
    ("The accountant audited each account in the", "commerce"),
    ("The doctor vaccinated every child in the", "medicine"),
    ("The librarian catalogued each book on the", "education"),
    ("For every customer in the queue, the teller processed the", "commerce"),
    ("The painter varnished each panel of the", "arts"),
    ("He tightened every bolt on the", "everyday"),
    ("The judge reviewed each case on the", "law"),
    ("She translated every line of the", "education"),
    ("The system encrypted each record in the", "technology"),
]

_FILTER: list[tuple[str, str]] = [  # keep only elements satisfying a predicate (subset)
    ("From the basket she kept only the apples that were", "cooking"),
    ("He removed all the cards from the deck that were", "everyday"),
    ("The program discarded every record that was", "technology"),
    ("She selected only the students who had", "education"),
    ("The farmer harvested only the tomatoes that were", "nature"),
    ("The screener admitted only the passengers whose tickets were", "travel"),
    ("The editor kept only the paragraphs that were", "education"),
    ("From the inbox he deleted every message that was", "technology"),
    ("The buyer chose only the items that were", "commerce"),
    ("The doctor flagged only the samples that tested", "medicine"),
    ("The judge admitted only the evidence that was", "law"),
    ("The coach kept only the players who were", "sports"),
    ("She picked out only the berries that were", "nature"),
    ("The filter let through only the particles that were", "technology"),
    ("The librarian shelved only the books that were", "education"),
    ("From the crowd security stopped only the people who looked", "law"),
    ("The chef used only the eggs that were", "cooking"),
    ("The recruiter shortlisted only the candidates who had", "commerce"),
    ("The nurse isolated only the patients who were", "medicine"),
    ("The curator displayed only the paintings that were", "arts"),
    ("He kept only the photos that were", "arts"),
    ("The system blocked every request that was", "technology"),
    ("She saved only the receipts that were", "everyday"),
    ("The gardener pulled out every weed that was", "nature"),
    ("The auditor questioned only the transactions that were", "commerce"),
    ("The teacher rewarded only the answers that were", "education"),
    ("From the batch they rejected every part that was", "technology"),
    ("The referee penalized only the moves that were", "sports"),
]

_FOLD: list[tuple[str, str]] = [  # accumulate a sequence into a SINGLE value
    ("Adding each receipt to the running total, the clerk reached a final", "commerce"),
    ("Combining all the ingredients one by one into a single", "cooking"),
    ("Summing the scores from every round gave the team a final", "sports"),
    ("Folding each layer into the batter produced a smooth", "cooking"),
    ("Merging all the branches into one produced the final", "technology"),
    ("Tallying the votes one by one, the clerk announced the final", "law"),
    ("Stacking each brick on the last, the mason built a single", "everyday"),
    ("Reducing the long list of numbers to a single", "technology"),
    ("Gathering every tributary, the streams merged into one great", "nature"),
    ("Accumulating interest year on year grew the deposit into a larger", "commerce"),
    ("Blending all the colors together produced one muddy", "arts"),
    ("Compressing the whole archive into a single", "technology"),
    ("Adding each student's grade, the teacher computed the class", "education"),
    ("Combining every clause into one comprehensive", "law"),
    ("Stitching the panels together made a single", "arts"),
    ("Boiling the sauce down reduced it to a thick", "cooking"),
    ("Totaling the distances of each leg gave the trip's full", "travel"),
    ("Folding all the dough together formed one large", "cooking"),
    ("Summarizing the entire report into a single", "education"),
    ("Aggregating the readings into one average", "medicine"),
    ("Collecting every donation, the charity reached a grand", "commerce"),
    ("Concatenating the strings produced one long", "technology"),
    ("Pooling all the samples into a single", "medicine"),
    ("Reducing every transaction to a single balance gave the final", "commerce"),
    ("Compiling all the chapters into one complete", "arts"),
    ("Merging the datasets row by row yielded one combined", "technology"),
    ("Combining the squad's efforts into a single", "sports"),
    ("Rolling all the changes into one final", "technology"),
]

_ZIP: list[tuple[str, str]] = [  # pair two sequences element-wise
    ("She matched each sock with its corresponding", "everyday"),
    ("Each name on the list was paired with a", "education"),
    ("The dating app matched every applicant with a suitable", "everyday"),
    ("Each key was fitted to its matching", "everyday"),
    ("The teacher paired each student with a study", "education"),
    ("Every question was lined up with its correct", "education"),
    ("The system joined each order with its corresponding", "commerce"),
    ("Each runner was assigned to a numbered", "sports"),
    ("Every patient was matched to an available", "medicine"),
    ("The translator aligned each English word with its French", "education"),
    ("Each bolt was paired with the right", "everyday"),
    ("Every passenger was matched to a window or aisle", "travel"),
    ("The recipe paired each spice with a complementary", "cooking"),
    ("Each witness was matched to the relevant", "law"),
    ("The app synced each photo with its location", "technology"),
    ("Every employee was paired with a mentor", "commerce"),
    ("The dance instructor paired each lead with a", "arts"),
    ("Each lock was matched to its unique", "everyday"),
    ("The merge joined each row with its matching", "technology"),
    ("Every glove was paired with its other", "everyday"),
    ("The conference paired each speaker with a", "education"),
    ("Each color was matched to a complementary", "arts"),
    ("The vet paired each animal with its medical", "medicine"),
    ("Every invoice was matched to a corresponding", "commerce"),
    ("The hikers paired each map with the right", "travel"),
    ("Each instrument was tuned to its matching", "arts"),
    ("The algorithm zipped each input with its expected", "technology"),
    ("Every plaintiff was matched with a defense", "law"),
]


_RAW: dict[str, list[tuple[str, str]]] = {
    "compose": _COMPOSE,
    "flip": _FLIP,
    "const": _CONST,
    "apply": _APPLY,
    "map": _MAP,
    "filter": _FILTER,
    "fold": _FOLD,
    "zip": _ZIP,
}


# ══════════════════════════════════════════════════════════════════════════════
# Build + accessors
# ══════════════════════════════════════════════════════════════════════════════

def _build() -> list[FunctionProbe]:
    out: list[FunctionProbe] = []
    for fn in FUNCTIONS:
        kind = "control" if fn in _CONTROL else "test"
        for i, (prompt, domain) in enumerate(_RAW[fn]):
            out.append(FunctionProbe(
                id=f"hof_{fn}_{i:03d}",
                prompt=prompt,
                function=fn,
                kind=kind,
                domain=domain,
            ))
    return out


_PROBES: list[FunctionProbe] = _build()


def function_probes() -> list[FunctionProbe]:
    """All higher-order-function probes (controls first, then tests)."""
    return list(_PROBES)


def by_function(name: str) -> list[FunctionProbe]:
    """Probes for a single function."""
    return [p for p in _PROBES if p.function == name]


def function_names() -> list[str]:
    """Canonical function order."""
    return list(FUNCTIONS)


def function_counts() -> dict[str, int]:
    """function → probe count."""
    return {fn: len(by_function(fn)) for fn in FUNCTIONS}


def expected_combinator(fn: str) -> str | None:
    """Theory anchor for a control function (compose→B, …); None for HOF tests."""
    return EXPECTED_COMBINATOR.get(fn)


if __name__ == "__main__":
    import json
    print(json.dumps(function_counts(), indent=2))
    print(f"total: {len(_PROBES)} probes across {len(FUNCTIONS)} functions")
