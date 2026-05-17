"""Lambda Kernel Probes — Concentrated probe set for crystallizing the lambda calculus.

Goal: Provide enough constraint density in the COMBINATORY LOGIC subspace that
the relational loss forces the model to implement the operations as distinct
deterministic kernel functions.

Design principles:
1. Minimal pairs: each pair differs in EXACTLY one operation
2. Density: 20-30 probes per operation axis
3. Natural language only (no formal notation in probes)
4. Graded complexity: simple → nested
5. Cross-operation contrast: some probes midway between operations

This file exports LAMBDA_PROBES in the same format as the crystal seed script:
    dict[str, list[str]] where keys are axis names, values are prompt lists.

Operation axes targeted:
    Tier 1 (confirmed):  K, I, B, C, M
    Tier 2 (predicted):  W, T, Φ (fork), D (deep compose)
    Tier 3 (structural): SUBST, SCOPE, WHNF
    Tier 4 (meta):       Y (recursion), QUOTE

Total: ~400 probes across ~15 operation axes

License: MIT
"""

# ══════════════════════════════════════════════════════════════════════════════
# TIER 1: CONFIRMED OPERATIONS (dense coverage for snap)
# ══════════════════════════════════════════════════════════════════════════════

# ── K: SELECT / DISCARD ──────────────────────────────────────────────────────
# K picks one argument and throws away the other.
# Linguistic signatures: topic focus, relevance filtering, conditional branch,
# choosing one alternative, ignoring distractors.

K_SELECT = [
    # Focus/topic selection (pick the subject, discard adjuncts)
    "Of all the animals in the zoo, only the lion was truly",
    "Among the candidates, the committee chose the one who had the most",
    "Between coffee and tea, she always prefers",
    "Despite the rain, the cold, and the wind, the hikers continued to",
    "Ignoring the noise from the construction site next door, the student focused on",
    # Conditional selection (take one branch, discard the other)
    "If the test is positive, the doctor will prescribe medication; otherwise the patient can go",
    "Either we leave now and catch the train, or we stay and miss",
    "The winner takes the trophy while the loser goes",
    "You must choose: save the village or pursue the",
    "The relevant factor was not the price but the",
    # Information filtering (keep relevant, discard noise)
    "The key finding of the study, setting aside methodological concerns, was that",
    "Regardless of the criticism, the project achieved its primary",
    "Whatever the reason, the result was clearly",
    "No matter what else happened that day, the important thing was that",
    "Setting aside personal feelings, the decision was based purely on",
    # Extraction from set (pick one from many)
    "From the entire library, she selected only one book about",
    "Out of hundreds of applicants, only five were invited to",
    "The detective isolated the single piece of evidence that",
    "Among all the possible explanations, the simplest one was",
    "From the wreckage they recovered only the",
    # Deletion/dropping (actively discard)
    "The editor removed all unnecessary adjectives, leaving only",
    "After stripping away the jargon, the message was simply that",
    "Reduce the fraction to its simplest form by removing common",
    "The sculptor removed marble until only the figure",
    "Delete everything except the first column and the last",
]

# ── I: IDENTITY / BINDING / REFERENCE ────────────────────────────────────────
# I passes something through unchanged. Variable reference, coreference,
# pronoun binding, direct quotation, pass-through.

I_IDENTITY = [
    # Pronoun binding (reference back to same entity)
    "John said that he would finish the project by",
    "The cat cleaned itself thoroughly before",
    "Mary asked her mother if she could borrow",
    "The students prepared their own presentations about",
    "The company announced that it would be expanding into",
    # Direct reference (identity/pass-through)
    "The answer is exactly what you think it",
    "What you see is precisely what you",
    "The output of the function is the same as the",
    "Copy the file exactly as it appears without changing",
    "Repeat after me: the password is",
    # Coreference chains (tracking same entity)
    "The old man sat on the bench. He watched the pigeons as they",
    "Alice found a book in the attic. She opened it and saw that it",
    "The car broke down on the highway. Its engine had overheated because the",
    "The twins looked identical. Both of them wore the same",
    "The river flows south through the valley. It eventually reaches the",
    # Binding at distance (long-range reference)
    "The scientist who published the paper last year now claims that her results were",
    "The building that was constructed in 1920 still has its original",
    "Every student who passed the exam received their certificate on",
    "The book that I bought yesterday turned out to be the same one that she had already",
    "The company that hired me three years ago just announced that they will",
    # Pass-through / transparency
    "According to the report, the exact figure was",
    "The witness stated that the car was, in her own words,",
    "The translation preserves the original meaning which is",
    "Verbatim, the inscription reads:",
    "The signal passed through the amplifier unchanged and emerged as",
]

# ── B: COMPOSE / CHAIN ───────────────────────────────────────────────────────
# B applies f to the result of g. Sequential operations, dependent clauses,
# function chaining, pipelines, nested modification.

B_COMPOSE = [
    # Sequential operations (do g then f)
    "After washing the dishes, she dried them with a",
    "Having read the instructions, he assembled the furniture in",
    "First the butter is melted, then the flour is added to create a",
    "The water is filtered and then boiled before being served to",
    "She wrote the code, tested it, and then deployed it to the",
    # Dependent clauses (result of inner feeds into outer)
    "The man who fixed the roof was paid by the woman who owned the",
    "The fact that the economy grew suggests that the policy was",
    "Knowing that the bridge was closed, they took the longer route through",
    "The cake that she baked using the recipe that her grandmother wrote won",
    "The rumor that the CEO who fired the manager was himself going to resign spread",
    # Function chaining / pipelines
    "Take the raw text, clean it, tokenize it, then feed it into the",
    "The signal is amplified, filtered, and then converted into a",
    "The ore is mined, refined, shaped, and finally polished into a",
    "Read the file, parse the JSON, extract the field, and return the",
    "Collect the data, compute the average, then plot the result as a",
    # Nested modification (composition of properties)
    "The extremely rapidly spinning bright blue",
    "A recently discovered previously unknown species of deep-sea",
    "The heavily fortified carefully guarded ancient underground",
    "A beautifully restored meticulously maintained Victorian-era",
    "The surprisingly well-preserved recently excavated Bronze Age",
    # Cause chains (A causes B causes C)
    "The drought caused the crops to fail which led to a famine that",
    "His injury prevented him from training which cost him the competition that",
    "The storm damaged the power lines which cut electricity to the hospital where",
    "The discovery inspired a new theory that explained the phenomenon that had puzzled",
    "The invention revolutionized the industry that transformed the economy that now",
]

# ── C: FLIP / REORDER ────────────────────────────────────────────────────────
# C swaps the order of arguments. Passive voice, topicalization, inversion,
# argument reordering, free word order.

C_FLIP = [
    # Passive voice (canonical flip: agent↔patient swap)
    "The letter was written by the",
    "The window was broken by the ball that the child had",
    "The song was performed by a band that nobody had",
    "Three people were rescued by the firefighter who",
    "The problem was finally solved by the youngest member of",
    # Topicalization / focus fronting
    "This particular issue, the board discussed at length during",
    "Under no circumstances should you open the",
    "Only after the rain stopped did the children go outside to",
    "Never before had the city experienced such a severe",
    "Rarely does one encounter such a perfectly preserved example of",
    # Dative alternation (give X to Y → give Y X)
    "She gave the book to the student who had",
    "She gave the student the book that she had",
    "He sent a letter to his mother explaining",
    "He sent his mother a letter explaining",
    "They offered the job to the candidate who",
    # Inverted constructions
    "Into the room walked a tall man wearing a",
    "Down the hill rolled the enormous boulder that had been",
    "Away flew the birds when the dog started to",
    "Up rose the sun over the mountains revealing the",
    "Out came the truth about what had really",
    # Argument swap in comparison
    "The teacher taught the student, and the student taught the",
    "She trusts him more than he trusts",
    "The cat chased the dog, but then the dog chased the",
    "He gave her the ring that she later gave back to",
    "The parent protects the child until the child can protect the",
]

# ── M: MATCH / RETRIEVE ──────────────────────────────────────────────────────
# M finds a pattern in context and copies/retrieves what followed.
# Induction, in-context learning, analogy completion, pattern matching.

M_MATCH = [
    # Direct pattern completion (A B ... A → B)
    "The king sat on his throne. The queen sat on her",
    "Paris is in France. Berlin is in",
    "Cats meow. Dogs",
    "Monday, Tuesday, Wednesday,",
    "Red, orange, yellow, green, blue,",
    # In-context learned pattern
    "bip bop bap. bip bop",
    "foo: 1, bar: 2, baz:",
    "alpha → beta, gamma → delta, epsilon →",
    "if x=1 then y=a, if x=2 then y=b, if x=3 then y=",
    "input: hello → output: HELLO. input: world → output:",
    # Structural repetition
    "The first chapter introduced the characters. The second chapter introduced the",
    "She entered the room quietly. He entered the room",
    "In summer the days are long. In winter the days are",
    "The teacher asked a question and the student gave an answer. The student asked a question and the teacher gave an",
    "For breakfast he had eggs. For lunch he had",
    # Template matching (fill slot from context)
    "My name is Alice. Her name is",
    "The book costs ten dollars. The pen costs five",
    "He drives a blue car. She drives a red",
    "The dog is big and friendly. The cat is small and",
    "They arrived at noon. We arrived at",
    # Analogy/proportion (A:B :: C:?)
    "Cat is to kitten as dog is to",
    "Up is to down as left is to",
    "Author is to book as painter is to",
    "Finger is to hand as toe is to",
    "Day is to night as summer is to",
]

# ══════════════════════════════════════════════════════════════════════════════
# TIER 2: PREDICTED OPERATIONS (seeking discovery)
# ══════════════════════════════════════════════════════════════════════════════

# ── W: DUPLICATE / SELF-APPLICATION ──────────────────────────────────────────
# W uses the same argument in two places. Reflexives, shared subjects,
# self-reference, same entity in multiple roles.

W_DUPLICATE = [
    # Reflexive pronouns (entity = both agent and patient)
    "The dog bit itself on the",
    "She taught herself to play the",
    "The robot programmed itself to perform the",
    "He convinced himself that everything would be",
    "The system tested itself and found three",
    # Same argument in two slots
    "The spy who betrayed the spy was the same",
    "He compared the result with the result and found no",
    "She liked the person she had become more than the person she used to",
    "The city was both the birthplace and the burial place of the",
    "The answer to the question was the question",
    # Self-reference / fixed points
    "This sentence has exactly five",
    "The list contains its own name as the first",
    "The set of all sets that contain themselves is",
    "The statement refers to the truth of the statement",
    "The function calls itself with a smaller",
    # Shared subject across parallel predicates (same entity, two actions)
    "She sang and danced at the same",
    "The car accelerated and then braked",
    "He opened the door and closed the",
    "The bird flew up and then dove",
    "She read the letter and cried because it said",
    # Duplication in structure (same phrase in two positions)
    "What will be will",
    "Boys will be",
    "It is what it",
    "The more things change the more they stay the",
    "Easy come easy",
]

# ── T: TYPE-RAISE / ARGUMENT-TO-FUNCTOR ──────────────────────────────────────
# T converts an argument into a functor that takes the original functor.
# Topicalization, question formation, it-cleft, focus constructions.

T_TYPERAISE = [
    # It-cleft (argument promoted to focus position)
    "It was John who broke the",
    "It is the economy that voters care most",
    "It was in Paris that they first",
    "It was only after midnight that the noise finally",
    "It is this very principle that the entire argument rests",
    # Wh-questions (argument → interrogative functor)
    "Who was it that first discovered the",
    "What did the scientists find when they examined the",
    "Where did she hide the key before she",
    "When exactly did the earthquake happen according to the",
    "Which of the candidates best represents the",
    # Relative clause extraction (argument raised to gap-filler)
    "The man that everyone admires most is the one who",
    "The book which nobody expected to become popular actually sold over a million",
    "The country where the revolution began was the same place that",
    "The day when everything changed was an ordinary",
    "The reason why the experiment failed was never fully",
    # Topicalization (argument fronted, becomes topic)
    "These problems, no one seems able to",
    "That proposal, the committee unanimously",
    "His latest novel, critics have universally",
    "The money, they had already spent on",
    "Such behavior, the school does not",
    # Focus fronting with contrast
    "It's not the destination but the journey that",
    "Not money but love is what truly",
    "Coffee she drinks, but tea she absolutely",
    "The blue one I'll take, but the red one you can",
    "First prize he won easily, but second prize went to",
]

# ── Φ (PHI): FORK / PARALLEL APPLICATION ─────────────────────────────────────
# Φ applies two functions to the same input and combines results.
# Coordination, comparison, multi-property attribution, parallel predicates.

PHI_FORK = [
    # Coordination with shared subject (two predicates, one entity)
    "The diplomat spoke fluent French and understood the local",
    "The new policy both reduced costs and improved",
    "The medication effectively treats pain and prevents",
    "The software analyzes data and generates",
    "The earthquake destroyed buildings and disrupted",
    # Comparative constructions (apply measure to two things, compare)
    "The tower is taller than any other building in the",
    "She runs faster than anyone else on the",
    "This version is both cheaper and more reliable than the",
    "The new model outperforms the old one in speed and",
    "His second novel was more complex but less popular than his",
    # Multi-property attribution (multiple predicates on same subject)
    "The old stone house was both beautiful and",
    "The candidate was experienced, articulate, and extremely",
    "The river was wide, deep, and dangerously",
    "Her argument was logical, well-structured, and thoroughly",
    "The solution is elegant, efficient, and surprisingly",
    # Split/merge patterns (one input → two paths → combine)
    "The light passed through the prism and split into red and blue that then",
    "The river forks at the mountain and the two branches rejoin at the",
    "She divided her time between work and family, balancing both",
    "The signal was split, processed separately, and then recombined into",
    "His attention was divided between the road and the map until he finally",
    # Conjunction reduction (shared structure, parallel fillers)
    "The doctor examined and treated the",
    "She bought bread, milk, and",
    "The law applies to citizens and non-citizens",
    "They searched the house, the garden, and the",
    "He studied mathematics, physics, and",
]

# ── D: DEEP COMPOSE / NESTED APPLICATION ─────────────────────────────────────
# D = B∘B. Composition at depth > 1. Ditransitives, serial operations,
# deeply nested modification, multi-level dependencies.

D_DEEPCOMPOSE = [
    # Ditransitives (three-place predicates with nested roles)
    "She gave him the book that she had found in the library that was built by",
    "He told her that the man who owned the house had sold it to the woman who",
    "They showed the visitors the paintings that the artist had created during",
    "The teacher explained to the students how the machine that the inventor designed actually",
    "He promised her that the surprise he had planned for months would",
    # Serial verbs / sequential multi-step
    "She went to buy the ingredients to make the cake to bring to the",
    "He called to ask whether she was ready to leave to catch the",
    "They tried to find someone to help them to carry the equipment to",
    "I need you to help me to understand how to fix the code that",
    "She asked him to try to remember where he had put the",
    # Deeply nested relative clauses
    "The house that the man who the dog that bit the cat belonged to built was",
    "The paper that the student who the professor that won the award supervised wrote was",
    "The idea that the theory that the evidence that the experiment produced supported proposed",
    "The car that the mechanic who the garage that burned down employed fixed was",
    "The song that the band that the label that went bankrupt signed recorded was",
    # Multi-level causation
    "The rain that caused the flood that destroyed the bridge that connected the towns that",
    "The policy that created the incentive that motivated the behavior that produced the outcome that",
    "The gene that produces the protein that inhibits the enzyme that catalyzes the reaction that",
    "The event that triggered the response that overwhelmed the system that managed the process that",
    "The mistake that caused the error that crashed the server that hosted the website that",
    # Pipeline depth (more than 3 steps)
    "Read the data, parse it, transform it, validate it, and store it in the",
    "The raw material is mined, transported, refined, processed, and finally shaped into",
    "The message was encoded, transmitted, received, decoded, and then displayed on the",
    "The patient was examined, diagnosed, treated, monitored, and eventually discharged from the",
    "The proposal was drafted, reviewed, revised, approved, and finally implemented across the",
]

# ══════════════════════════════════════════════════════════════════════════════
# TIER 3: STRUCTURAL OPERATIONS (sub-beta-reduction steps)
# ══════════════════════════════════════════════════════════════════════════════

# ── SCOPE: Quantifier scope / binding depth / nested frames ──────────────────

SCOPE_MANAGE = [
    # Scope ambiguity (same words, different scoping)
    "Every student read a book about",
    "A student read every book about",
    "Someone loves everyone in the",
    "Everyone loves someone in the",
    "No student solved every problem on the",
    # Nested quantifiers (increasing depth)
    "Every dog chases some",
    "Every boy knows a girl who likes some",
    "For every problem there exists a solution that works in all",
    "In every city there is a person who knows someone who has",
    "Every theory predicts that some experiment will show that all",
    # Scope islands (blocked scope interactions)
    "If every student passes, the teacher will celebrate",
    "The claim that every student passed surprised",
    "She denied that anyone had taken the",
    "They wondered whether some candidate would",
    "Nobody believes that everyone can",
    # De dicto / de re (scope relative to attitude)
    "She wants to marry a doctor who is",
    "He believes that a spy is following",
    "They are looking for a unicorn that has",
    "She thinks someone stole her",
    "He hopes that a miracle will",
    # Donkey sentences (complex binding)
    "Every farmer who owns a donkey beats",
    "If a student fails an exam, he must retake",
    "Any linguist who finds a counterexample will publish",
    "Whoever breaks a window must pay for",
    "Every city that has a river has a bridge over",
]

# ── SUBST: Substitution / reduction pairs ────────────────────────────────────
# Before and after beta reduction. The probe pairs show the SAME meaning
# expressed in unreduced vs reduced form.

SUBST_REDUCE = [
    # Function applied to argument → simplified result
    "The thing that makes ice cold is the low",
    "The low temperature makes ice",
    "The person who teaches students at school is the",
    "The teacher teaches students at",
    "The process by which plants convert sunlight into energy is",
    # Periphrastic → direct expression
    "It is the case that the weather is getting",
    "The weather is getting warmer every single",
    "What he did was open the door and walk",
    "He opened the door and walked into the",
    "The way in which she accomplished the task was by carefully",
    # Lambda application visible in natural language
    "Apply the operation of doubling to the number five to get",
    "Take the function that adds three and apply it to seven to get",
    "The result of sorting the list and then taking the first element is",
    "If you reverse the string and then capitalize it you get",
    "First square the number, then add one, giving you",
    # Unreduced relative clause → reduced participle
    "The man who is running in the park",
    "The man running in the park",
    "The building which was destroyed by the fire",
    "The building destroyed by the fire",
    "The students who are waiting outside the",
    # Complex → simple (multiple reductions)
    "It is not the case that it is not raining today",
    "It is raining today according to the weather",
    "The brother of the mother of John is the",
    "John's uncle is the same person who",
    "The thing that she is afraid of is the possibility that it might",
]

# ── WHNF: Normal form detection (already reduced / stop signal) ──────────────
# Simple atomic content vs complex reducible structure.
# The model should recognize when something is "done" vs needs more processing.

WHNF_TERMINAL = [
    # Atomic values (already in normal form)
    "The number is seven and nothing more needs to be",
    "The color is blue without any further",
    "The answer is simply yes and that is",
    "The value is true with no conditions",
    "The answer to life the universe and everything is forty-two",
    # Complex structures (not yet reduced, need processing)
    "The number is whatever you get when you multiply three by the square root of",
    "The color is the one that you see when you mix the primary colors in equal",
    "The answer depends on whether the initial conditions satisfy the constraints that",
    "The truth value of the conjunction of all the premises given that some are",
    "The result of applying the algorithm to the input after preprocessing and",
    # Simple predicates (values with type)
    "The dog is brown",
    "Water freezes at zero degrees",
    "Paris is a city",
    "Two is an even number",
    "Gold is a metal",
    # Complex predicates (require resolution)
    "The animal that the witness described to the police was",
    "The temperature at which the substance begins to decompose under pressure is",
    "The city where the conference will be held next year is",
    "The number that satisfies both equations simultaneously is",
    "The person who knows the answer to the question that nobody else could solve is",
    # Imperatives vs declarations (action-needed vs statement)
    "Calculate the sum of all prime numbers less than",
    "The sum of all prime numbers less than twenty is",
    "Find the shortest path between nodes A and",
    "The shortest path between nodes A and B has length",
    "Determine whether the given string is a valid",
]

# ══════════════════════════════════════════════════════════════════════════════
# TIER 4: HIGHER-ORDER / META OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

# ── Y: RECURSION / FIXED POINT / SELF-REFERENCE ──────────────────────────────

Y_RECURSE = [
    # Recursive definitions
    "A folder contains files and other folders which contain files and other folders which",
    "She told a story about a girl who told a story about a girl who",
    "The dream was about having a dream which was about having a dream that",
    "He opened a box inside a box inside a box inside a",
    "The mirror reflected the mirror which reflected the mirror reflecting the",
    # Self-reference / quines
    "This sentence is about this sentence being about",
    "The definition of recursion is: see the definition of",
    "In order to understand recursion you must first understand",
    "The word that describes itself is",
    "A self-referential statement is a statement that refers to",
    # Inductive definitions (base case + recursive case)
    "To count to ten: if the number is ten, stop. Otherwise, say the number and count from",
    "To sort a list: if empty, return it. Otherwise, split it in half, sort each half, and",
    "A sentence is a noun phrase followed by a verb phrase, where a noun phrase is",
    "Factorial of n: if n is zero, the answer is one. Otherwise multiply n by the factorial of",
    "The ancestor of a person is either their parent or an ancestor of their",
    # Iterative processes (loop structure)
    "Keep adding one until you reach the",
    "Repeat the process until the error is less than",
    "Double the amount each day for thirty",
    "Try again and again until you",
    "Each generation passes the knowledge to the next generation which passes it to the",
    # Mathematical recursion
    "The Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21,",
    "Powers of two: 1, 2, 4, 8, 16, 32, 64,",
    "Each term is the sum of the previous two",
    "The fractal pattern repeats at every scale getting smaller each",
    "The infinite series converges because each term is half of the",
]

# ── QUOTE: META / USE-MENTION / LEVEL SHIFT ──────────────────────────────────

QUOTE_META = [
    # Direct quotation (mention, not use)
    "The word 'cat' has three",
    "She said 'I will be there at",
    "The sign read 'No parking between the hours of",
    "He wrote 'The end' at the bottom of the",
    "The definition of 'irony' is",
    # Use vs mention contrast
    "Cats are furry animals that like to",
    "The word 'cats' is a plural",
    "Freedom is worth fighting",
    "The concept of 'freedom' has been debated for",
    "Love conquers",
    # Metalanguage (talking about language)
    "The sentence 'colorless green ideas sleep furiously' is grammatically correct but",
    "In English, adjectives come before the",
    "The verb 'to be' is the most irregular verb in",
    "A paragraph should have a topic sentence that",
    "The passive voice is formed by using a form of 'to be' followed by the",
    # Reported speech / embedded perspectives
    "He said that he would come, but she thought that he was",
    "The report claims that the economy grew, although critics argue that it actually",
    "According to the theory, light travels in waves, but experiments show that it also behaves like",
    "She believes that honesty is the best policy, even though her experience suggests that",
    "They announced that the project was on schedule, despite evidence that it was actually",
    # Code as data (programs about programs)
    "The program that prints its own source code is called a",
    "A compiler is a program that translates other programs into",
    "The debugger examines the running program to find where it",
    "A test is code that verifies that other code does what it",
    "Documentation describes how the code works so that others can",
]


# ══════════════════════════════════════════════════════════════════════════════
# CROSS-OPERATION CONTRAST PROBES
# These are designed to be AMBIGUOUS between two operations, forcing the
# RDM to place them at measured distances between axes.
# ══════════════════════════════════════════════════════════════════════════════

CONTRAST_K_vs_I = [
    # Is this selecting one thing (K) or referencing the same thing (I)?
    "He picked up the red ball and threw it to",  # K=red ball selected, or I=same ball referenced?
    "She read the first book and then read the",   # K=first selected, or I=same one again?
    "The winner is the person who was fastest which means the winner is",
    "Take the answer from step one and use that same answer in step",
    "Of all his works, his masterpiece was the one that he considered to be his",
]

CONTRAST_B_vs_C = [
    # Is this composition (B) or reordering (C)?
    "The package was delivered to the address that the sender had written on",
    "She read what he wrote before he had a chance to",
    "The food she cooked with ingredients he had bought tasted",
    "He answered the question that she had asked about the thing that they had",
    "The message sent by the person hired by the company reached the",
]

CONTRAST_W_vs_I = [
    # Is this duplication (W=same arg twice) or just reference (I=point to same)?
    "He hurt himself while working on the",  # W: same entity in agent AND patient
    "He said he would go",                    # I: just referencing same person
    "The dog that chased the dog was the",    # W: same entity in both positions?
    "She reminded herself of herself from years",  # W: deeply duplicated
    "She knew that she had been wrong about",      # I: reference chain
]

CONTRAST_B_vs_D = [
    # Is this simple composition (B) or deep composition (D)?
    "She asked him to help her finish the",     # B: two-level
    "She asked him to help her finish building the model that she had started", # D: multi-level
    "He went to buy the food",                  # B: simple chain
    "He went to buy the food to cook the dinner to serve at the party that",  # D: deep chain
    "The plan that the team proposed worked",   # B: one embedding level
]

CONTRAST_M_vs_B = [
    # Is this pattern matching (M) or composition (B)?
    "Monday comes before Tuesday and Tuesday comes before",  # M: pattern
    "First comes spring, which brings flowers that attract the",  # B: composition
    "Red means stop. Green means",  # M: pattern lookup
    "The heat causes expansion which causes pressure that",  # B: causal chain
    "Input: 2 → Output: 4. Input: 3 → Output:",  # M: pattern
]

CONTRAST_PHI_vs_K = [
    # Is this parallel application (Φ) or selection (K)?
    "The book was both entertaining and",     # Φ: two properties, same subject
    "The book was entertaining rather than",   # K: one selected, other discarded
    "She was smart and kind to everyone she",  # Φ: parallel attributes
    "She was smart but not particularly",      # K: select smart, discard other
    "The car is fast and efficient on the",    # Φ: two properties
]


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT: Combined probe dictionary for crystal seed infrastructure
# ══════════════════════════════════════════════════════════════════════════════

LAMBDA_PROBES = {
    # Tier 1: confirmed operations
    "lambda_K_select": K_SELECT,
    "lambda_I_identity": I_IDENTITY,
    "lambda_B_compose": B_COMPOSE,
    "lambda_C_flip": C_FLIP,
    "lambda_M_match": M_MATCH,

    # Tier 2: predicted operations
    "lambda_W_duplicate": W_DUPLICATE,
    "lambda_T_typeraise": T_TYPERAISE,
    "lambda_PHI_fork": PHI_FORK,
    "lambda_D_deepcompose": D_DEEPCOMPOSE,

    # Tier 3: structural operations
    "lambda_SCOPE_manage": SCOPE_MANAGE,
    "lambda_SUBST_reduce": SUBST_REDUCE,
    "lambda_WHNF_terminal": WHNF_TERMINAL,

    # Tier 4: higher-order operations
    "lambda_Y_recurse": Y_RECURSE,
    "lambda_QUOTE_meta": QUOTE_META,

    # Cross-operation contrast (disambiguation probes)
    "contrast_K_vs_I": CONTRAST_K_vs_I,
    "contrast_B_vs_C": CONTRAST_B_vs_C,
    "contrast_W_vs_I": CONTRAST_W_vs_I,
    "contrast_B_vs_D": CONTRAST_B_vs_D,
    "contrast_M_vs_B": CONTRAST_M_vs_B,
    "contrast_PHI_vs_K": CONTRAST_PHI_vs_K,
}

# ══════════════════════════════════════════════════════════════════════════════
# STATISTICS
# ══════════════════════════════════════════════════════════════════════════════

def print_stats():
    """Print probe set statistics."""
    total = sum(len(v) for v in LAMBDA_PROBES.values())
    print(f"\n{'='*60}")
    print(f"Lambda Kernel Probe Set — Statistics")
    print(f"{'='*60}")
    print(f"Total probes: {total}")
    print(f"Operation axes: {len(LAMBDA_PROBES)}")
    print(f"Pairwise constraints (per layer): {total * (total-1) // 2:,}")
    print(f"\nPer-axis breakdown:")
    for axis, probes in LAMBDA_PROBES.items():
        print(f"  {axis:30s}  {len(probes):3d} probes")
    print(f"\nTier breakdown:")
    tier1 = sum(len(v) for k, v in LAMBDA_PROBES.items() if k.startswith("lambda_") and k.split("_")[1] in "KIBCM")
    tier2 = sum(len(v) for k, v in LAMBDA_PROBES.items() if k.startswith("lambda_") and k.split("_")[1] in ["W", "T", "PHI", "D"])
    tier3 = sum(len(v) for k, v in LAMBDA_PROBES.items() if k.startswith("lambda_") and k.split("_")[1] in ["SCOPE", "SUBST", "WHNF"])
    tier4 = sum(len(v) for k, v in LAMBDA_PROBES.items() if k.startswith("lambda_") and k.split("_")[1] in ["Y", "QUOTE"])
    contrast = sum(len(v) for k, v in LAMBDA_PROBES.items() if k.startswith("contrast_"))
    print(f"  Tier 1 (confirmed KIBC-M):    {tier1:3d}")
    print(f"  Tier 2 (predicted W,T,Φ,D):   {tier2:3d}")
    print(f"  Tier 3 (structural):          {tier3:3d}")
    print(f"  Tier 4 (higher-order):        {tier4:3d}")
    print(f"  Contrast (cross-operation):   {contrast:3d}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print_stats()
