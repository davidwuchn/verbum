"""Minimal-pair natural-prose HOF stimuli — does the model USE higher-order
functions when working with ordinary prose?

THE QUESTION (session 225, Michael):
  s225 (function_topology_consensus) showed higher-order functions have a
  universal routing topology — but measured on CURATED probes built to exercise
  them. Does the model RECRUIT that same topology when reading ORDINARY prose
  where the function is incidental? Or was the topology a probe artifact?

DESIGN — minimal pairs:
  Each item is a PAIR: a naturalistic narrative sentence that INVOKES the HOF
  (iteration / selection / accumulation / pairing) and a matched CONTROL with
  closely matched vocabulary/length (often the same final token), but no HOF
  (single object, no iteration). The contrast isolates HOF-ness. To avoid a
  last-token lexical confound the engagement instrument MEAN-POOLS the routing
  register over the sentence rather than reading only the last token. Style is
  embedded/narrative and vocabulary is held-out vs the curated probes ⇒ a
  transfer test.

  Functions: map (apply to every element), filter (keep a subset by predicate),
  fold (accumulate to one value), zip (pair two sequences).

Usage:
    from verbum.probes.hof_prose import prose_pairs, by_function
    for p in by_function("map")[:3]:
        print(p.hof, "  |  ", p.control)

Accessors:
    prose_pairs()      → list[ProsePair]
    by_function(name)  → list[ProsePair]
    function_names()   → list[str]
    pair_counts()      → dict[str, int]

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
    """A HOF-invoking sentence and its matched non-HOF control (shared last token)."""

    id: str
    function: str            # map | filter | fold | zip
    hof: str                 # invokes the higher-order function
    control: str             # matched, no HOF, same last token
    domain: str


FUNCTIONS: tuple[str, ...] = ("map", "filter", "fold", "reduce", "zip")


# (hof, control, domain) — hof and control share the final token.
_MAP: list[tuple[str, str, str]] = [
    ("She moved down the row and watered each plant near the",
     "She paused by the sill and watered the plant near the", "nature"),
    ("The auditor opened the ledger and checked every entry against the",
     "The auditor opened the ledger and checked one entry against the", "commerce"),
    ("Going desk to desk, the clerk collected each signed form from the",
     "Stopping at the front, the clerk collected the signed form from the", "law"),
    ("He walked the aisles and restocked every empty shelf in the",
     "He walked to the back and restocked the empty shelf in the", "commerce"),
    ("By closing time she had greeted every customer who came through the",
     "By closing time she had greeted the customer who came through the", "commerce"),
    ("The nurse went bed to bed and recorded each patient's reading on the",
     "The nurse stopped once and recorded the patient's reading on the", "medicine"),
    ("Over the weekend he repainted every fence along the",
     "Over the weekend he repainted the fence along the", "everyday"),
    ("The teacher circled the room and praised each drawing pinned to the",
     "The teacher came over and praised the drawing pinned to the", "education"),
    ("Methodically the curator dusted every sculpture standing in the",
     "Carefully the curator dusted the sculpture standing in the", "arts"),
    ("The inspector tested every smoke alarm mounted in the",
     "The inspector tested the smoke alarm mounted in the", "everyday"),
    ("Down the platform she helped every passenger board the",
     "On the platform she helped the passenger board the", "travel"),
    ("All morning the chef seasoned each portion before it left the",
     "Just once the chef seasoned the portion before it left the", "cooking"),
    ("The coach timed every sprinter as they crossed the",
     "The coach timed the sprinter as they crossed the", "sports"),
    ("Patiently the vet examined each animal brought into the",
     "Quickly the vet examined the animal brought into the", "medicine"),
    ("The intern photocopied every page of the contract on the",
     "The intern photocopied one page of the contract on the", "law"),
    ("She tagged every photo before she uploaded them to the",
     "She tagged the photo before she uploaded it to the", "technology"),
    ("Row by row the farmer inspected each vine growing along the",
     "At the gate the farmer inspected the vine growing along the", "nature"),
    ("The waiter refilled every glass at the long",
     "The waiter refilled the glass at the long", "cooking"),
    ("He proofread each chapter before he emailed them to the",
     "He proofread the chapter before he emailed it to the", "education"),
    ("The technician updated every laptop connected to the",
     "The technician updated the laptop connected to the", "technology"),
    ("One by one she signed every card stacked on the",
     "Without pausing she signed the card stacked on the", "everyday"),
    ("The guide pointed out every landmark visible from the",
     "The guide pointed out the landmark visible from the", "travel"),
]

_FILTER: list[tuple[str, str, str]] = [
    ("Sorting through the pile, she kept only the photographs that showed the",
     "Flipping it over, she kept the single photograph that showed the", "arts"),
    ("The editor read the stack and forwarded only the essays that met the",
     "The editor read it once and forwarded the essay that met the", "education"),
    ("From the whole crate he picked out only the oranges that were past the",
     "From the top he picked out the one orange that was past the", "cooking"),
    ("Security waved through only the travelers whose passports cleared the",
     "Security waved through the traveler whose passport cleared the", "travel"),
    ("The recruiter set aside only the applicants who had finished the",
     "The recruiter set aside the applicant who had finished the", "commerce"),
    ("She deleted every email except the ones that mentioned the",
     "She deleted the email except the one that mentioned the", "technology"),
    ("The judge admitted only the documents that bore the official",
     "The judge admitted the document that bore the official", "law"),
    ("The doctor flagged only the samples that came back above the",
     "The doctor flagged the sample that came back above the", "medicine"),
    ("Out of the whole litter they kept only the puppies that had the",
     "From the basket they kept the puppy that had the", "nature"),
    ("The coach benched everyone except the players who passed the",
     "The coach benched the rookie except the player who passed the", "sports"),
    ("She skimmed the shelf and borrowed only the books that covered the",
     "She reached up and borrowed the book that covered the", "education"),
    ("The buyer accepted only the crates that survived the long",
     "The buyer accepted the crate that survived the long", "commerce"),
    ("He saved only the receipts that he would need for the",
     "He saved the receipt that he would need for the", "everyday"),
    ("The gallery hung only the canvases that fit the season's",
     "The gallery hung the canvas that fit the season's", "arts"),
    ("Quality control rejected every part except the ones that matched the",
     "Quality control rejected the part except the one that matched the", "technology"),
    ("The chef used only the herbs that were still fresh that",
     "The chef used the herb that was still fresh that", "cooking"),
    ("The clerk filed only the claims that arrived before the",
     "The clerk filed the claim that arrived before the", "law"),
    ("From the flock the shepherd separated only the sheep that had the",
     "From the pen the shepherd separated the sheep that had the", "nature"),
    ("The agent booked only the flights that landed before the",
     "The agent booked the flight that landed before the", "travel"),
    ("She kept only the messages that came from the night",
     "She kept the message that came from the night", "everyday"),
]

_FOLD: list[tuple[str, str, str]] = [
    ("Going through the receipts one by one, the bookkeeper added them into a single",
     "Glancing at the top receipt, the bookkeeper copied it into a single", "commerce"),
    ("She combined all the leftover scraps of dough into one large",
     "She set the small scrap of dough beside one large", "cooking"),
    ("Tallying the ballots through the night, the clerk reported a final",
     "Reading the first ballot aloud, the clerk noted a single", "law"),
    ("He merged every branch of the project into one stable",
     "He opened a single branch of the project into one stable", "technology"),
    ("Adding up the miles from each leg, they recorded the trip's total",
     "Noting the miles of the first leg, they recorded that leg's", "travel"),
    ("Stacking brick upon brick all summer, the mason finished a whole",
     "Setting one brick in place, the mason finished a small", "everyday"),
    ("Folding the chapters together, the writer produced one finished",
     "Reading a single chapter, the writer produced one short", "arts"),
    ("Pooling the donations from every branch, the charity reached a grand",
     "Counting the donation from one branch, the charity reached a small", "commerce"),
    ("Boiling the sauce down for an hour, the chef reduced it to a thick",
     "Tasting the sauce once, the chef poured it as a thin", "cooking"),
    ("Summing the grades from the whole class, the teacher computed the term",
     "Marking the grade of one student, the teacher noted the day's", "education"),
    ("Gathering the streams from across the valley, the river became one wide",
     "Following one small stream uphill, the hiker found one narrow", "nature"),
    ("Combining the readings from every sensor, the system produced one average",
     "Logging the reading from one sensor, the system stored one raw", "technology"),
    ("Rolling all the day's changes into a single release, the team shipped one",
     "Noting one small change in the log, the team shipped one", "technology"),
    ("Knitting the separate squares into one large blanket, she finished a single",
     "Holding one finished square aside, she started a single", "arts"),
    ("Aggregating every patient's results, the lab issued one combined",
     "Recording one patient's result, the lab issued one routine", "medicine"),
    ("Totaling the points from all four quarters, the scorer posted the final",
     "Marking the points from one quarter, the scorer posted a partial", "sports"),
    ("Compiling the notes from every meeting into one report, she sent a single",
     "Copying the notes from one meeting into a memo, she sent a single", "commerce"),
    ("Blending the whole basket of fruit into one smooth",
     "Slicing a single piece of fruit onto one small", "cooking"),
    ("Consolidating the debts into one monthly payment, he wrote a single",
     "Reviewing one small debt on the page, he wrote a single", "commerce"),
    ("Summing the rainfall over the entire month, the station logged a record",
     "Noting the rainfall on one wet day, the station logged a small", "nature"),
]

_ZIP: list[tuple[str, str, str]] = [
    ("Down the line each lid was matched to its corresponding",
     "At the bench the lid was set beside the corresponding", "technology"),
    ("The registrar paired every incoming student with a returning",
     "The registrar introduced one incoming student to a returning", "education"),
    ("One by one she fitted each key to its matching",
     "After a moment she fitted the key to its matching", "everyday"),
    ("The host seated each guest next to a chosen dinner",
     "The host seated one guest next to a chosen dinner", "everyday"),
    ("The app linked every photo to its recorded",
     "The app linked one photo to its recorded", "technology"),
    ("On the field the coach assigned each defender to an opposing",
     "On the bench the coach assigned one defender to an opposing", "sports"),
    ("The translator lined up each English line with its French",
     "The translator read one English line beside its French", "education"),
    ("Backstage they paired every dancer with a suitable",
     "Backstage they paired one dancer with a suitable", "arts"),
    ("The pharmacist matched each prescription to the right",
     "The pharmacist matched one prescription to the right", "medicine"),
    ("The clerk joined every invoice to its corresponding",
     "The clerk joined one invoice to its corresponding", "commerce"),
    ("At the gate each passenger was matched to an assigned",
     "At the desk one passenger was matched to an assigned", "travel"),
    ("In the lab they paired each sample with a control",
     "In the lab they paired one sample with a control", "medicine"),
    ("The teacher coupled every question with its model",
     "The teacher coupled one question with its model", "education"),
    ("Along the rack she matched each glove to its other",
     "On the hook she matched the glove to its other", "everyday"),
    ("The merge aligned every row with its matching",
     "The lookup aligned one row with its matching", "technology"),
    ("The conference paired each speaker with a session",
     "The conference paired one speaker with a session", "education"),
    ("The designer matched every color to a complementary",
     "The designer matched one color to a complementary", "arts"),
    ("At intake the vet linked each animal to its medical",
     "At intake the vet linked one animal to its medical", "medicine"),
    ("The court assigned every plaintiff to a defense",
     "The court assigned one plaintiff to a defense", "law"),
    ("In the orchestra she tuned each string to its reference",
     "Before the show she tuned one string to its reference", "arts"),
]


_REDUCE: list[tuple[str, str, str]] = [
    ("The analyst aggregated the whole year of sales into one annual",
     "The analyst noted a single day of sales as one daily", "commerce"),
    ("The script collapsed the entire folder of logs into one summary",
     "The script opened a single log file as one plain", "technology"),
    ("She condensed the team's many notes into one short",
     "She copied one team member's note into one short", "education"),
    ("The chef reduced the big pot of stock down to a concentrated",
     "The chef poured a single cup of stock into a thin", "cooking"),
    ("The query summed every transaction into a single running",
     "The query read one transaction as a single line", "technology"),
    ("Distilling the long trial into a verdict, the jury reached one",
     "Reading one piece of evidence, the jury noted one", "law"),
    ("The model compressed the high-dimensional dataset into one",
     "The model logged one data point as one", "technology"),
    ("Averaging all the patients' results, the lab issued one combined",
     "Recording one patient's result, the lab issued one routine", "medicine"),
    ("The editor boiled the sprawling draft down to one tight",
     "The editor marked one line of the draft as one tight", "arts"),
    ("Merging every regional report, headquarters produced one global",
     "Filing one regional report, headquarters produced one local", "commerce"),
    ("The census reduced millions of responses to a single national",
     "The census recorded one response as a single local", "education"),
    ("Consolidating all his debts, he was left with one monthly",
     "Reviewing one small debt, he was left with one monthly", "commerce"),
    ("The funnel narrowed thousands of leads down to one qualified",
     "The rep called one lead and noted one qualified", "commerce"),
    ("Folding the partial counts together, the system returned one final",
     "Logging one partial count, the system returned one raw", "technology"),
    ("The committee distilled the dozens of proposals into one unified",
     "The committee read one proposal and noted one minor", "law"),
    ("Aggregating every sensor's reading, the dashboard showed one overall",
     "Showing one sensor's reading, the dashboard showed one raw", "technology"),
    ("Summing the rainfall across the whole season into one record",
     "Noting the rainfall on one day as one small", "nature"),
    ("The archive compressed the entire library into a single",
     "The archive stored one book as a single", "education"),
    ("Pooling all the donations together, the charity announced one grand",
     "Counting one donation, the charity announced one modest", "commerce"),
    ("The reducer combined every shard into one consolidated",
     "The loader opened one shard as one plain", "technology"),
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
                id=f"prose_{fn}_{i:03d}",
                function=fn, hof=hof, control=control, domain=domain,
            ))
    return out


_PAIRS: list[ProsePair] = _build()


def prose_pairs() -> list[ProsePair]:
    """All HOF prose minimal pairs."""
    return list(_PAIRS)


def by_function(name: str) -> list[ProsePair]:
    """Pairs for a single function."""
    return [p for p in _PAIRS if p.function == name]


def function_names() -> list[str]:
    return list(FUNCTIONS)


def pair_counts() -> dict[str, int]:
    return {fn: len(by_function(fn)) for fn in FUNCTIONS}


if __name__ == "__main__":
    import json
    print(json.dumps(pair_counts(), indent=2))
    # verify shared last token within each pair
    bad = [p.id for p in _PAIRS if p.hof.split()[-1] != p.control.split()[-1]]
    print(f"total pairs: {len(_PAIRS)}; last-token-mismatch: {len(bad)} {bad}")
