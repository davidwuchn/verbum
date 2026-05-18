"""Build a diverse probe corpus for full-geometry extraction.

This corpus spans every domain we want the crystal to cover.
It's used to:
  1. Extract the teacher's RDM (complete cloud topology)
  2. Compute the student's RDM during holographic training
  3. The RDM loss drives the student toward the teacher's geometry

The corpus is NOT training data. It's a MEASUREMENT instrument.
Each example is a probe that reveals the model's internal geometry
for that domain. The pairwise distances between probes form the RDM.

Diversity is key: the more diverse the corpus, the more of the
cloud topology we capture. We want examples that span:
  - Every computational primitive (KIBC, math, logic, sequence)
  - Every domain (code, math, prose, reasoning, tools)
  - Every scale (token, phrase, sentence, paragraph)
  - Every language (English, Python, SQL, bash, math notation)

License: MIT
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path


def build_corpus(seed: int = 42) -> list[dict]:
    """Build the diverse probe corpus.

    Returns list of {"prompt": str, "domain": str, "subdomain": str}
    """
    rng = random.Random(seed)
    corpus = []

    # ═══════════════════════════════════════════════════════════
    # LAMBDA CALCULUS (combinators — the structural crystal)
    # ═══════════════════════════════════════════════════════════

    # Import existing lambda kernel probes
    probes_dir = Path(__file__).parent.parent.parent / "probes"
    sys.path.insert(0, str(probes_dir))
    try:
        from lambda_kernel_probes import LAMBDA_PROBES
        for axis, prompts in LAMBDA_PROBES.items():
            for prompt in prompts:
                corpus.append({
                    "prompt": prompt,
                    "domain": "lambda",
                    "subdomain": axis,
                })
    except ImportError:
        print("  WARNING: lambda_kernel_probes not found, skipping", file=sys.stderr)

    # ═══════════════════════════════════════════════════════════
    # ARITHMETIC (math crystal)
    # ═══════════════════════════════════════════════════════════

    math_templates = [
        # Addition
        ("What is {a} + {b}?", "add"),
        ("{a} plus {b} equals", "add"),
        ("Calculate: {a} + {b} =", "add"),
        # Subtraction
        ("What is {a} - {b}?", "sub"),
        ("{a} minus {b} equals", "sub"),
        # Multiplication
        ("What is {a} × {b}?", "mul"),
        ("{a} times {b} equals", "mul"),
        ("Calculate: {a} * {b} =", "mul"),
        # Division
        ("What is {a} ÷ {b}?", "div"),
        ("{a} divided by {b} equals", "div"),
        # Comparison
        ("Which is larger, {a} or {b}?", "cmp"),
        ("Is {a} greater than {b}?", "cmp"),
        # Multi-step
        ("What is ({a} + {b}) × {c}?", "multi"),
        ("Calculate {a} × {b} + {c} =", "multi"),
    ]

    for _ in range(200):
        a, b, c = rng.randint(1, 999), rng.randint(1, 999), rng.randint(1, 99)
        template, subdomain = rng.choice(math_templates)
        prompt = template.format(a=a, b=b, c=c)
        corpus.append({"prompt": prompt, "domain": "math", "subdomain": subdomain})

    # ═══════════════════════════════════════════════════════════
    # PROGRAMMING (code crystal — multiple languages)
    # ═══════════════════════════════════════════════════════════

    code_examples = [
        # Python
        ("def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)", "python", "recursion"),
        ("def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a", "python", "iteration"),
        ("squares = [x**2 for x in range(10) if x % 2 == 0]", "python", "comprehension"),
        ("result = list(map(lambda x: x * 2, filter(lambda x: x > 0, numbers)))", "python", "higher_order"),
        ("with open('file.txt') as f:\n    data = json.load(f)", "python", "context_manager"),
        ("class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val", "python", "class"),
        ("from collections import defaultdict\nd = defaultdict(list)\nfor k, v in pairs:\n    d[k].append(v)", "python", "aggregation"),
        ("async def fetch(url):\n    async with aiohttp.ClientSession() as session:\n        return await session.get(url)", "python", "async"),
        ("try:\n    result = int(user_input)\nexcept ValueError:\n    result = 0", "python", "error_handling"),
        ("sorted_items = sorted(items, key=lambda x: (x.priority, -x.date))", "python", "sorting"),

        # Rust
        ("fn factorial(n: u64) -> u64 {\n    match n {\n        0 | 1 => 1,\n        _ => n * factorial(n - 1),\n    }\n}", "rust", "recursion"),
        ("let result: Vec<i32> = numbers.iter().filter(|&&x| x > 0).map(|&x| x * 2).collect();", "rust", "iterator"),
        ("fn find_max<T: Ord>(list: &[T]) -> Option<&T> {\n    list.iter().max()\n}", "rust", "generics"),
        ("match command {\n    Command::Quit => break,\n    Command::Move { x, y } => move_to(x, y),\n    _ => println!(\"unknown\"),\n}", "rust", "pattern_match"),
        ("let handle = thread::spawn(move || {\n    expensive_computation(data)\n});", "rust", "concurrency"),
        ("impl Display for Point {\n    fn fmt(&self, f: &mut Formatter) -> fmt::Result {\n        write!(f, \"({}, {})\", self.x, self.y)\n    }\n}", "rust", "trait_impl"),

        # JavaScript
        ("const result = arr.reduce((acc, x) => acc + x, 0);", "javascript", "reduce"),
        ("const debounce = (fn, ms) => {\n  let timer;\n  return (...args) => {\n    clearTimeout(timer);\n    timer = setTimeout(() => fn(...args), ms);\n  };\n};", "javascript", "closure"),
        ("async function fetchData() {\n  const res = await fetch(url);\n  return res.json();\n}", "javascript", "async"),
        ("const merged = {...defaults, ...userConfig, timestamp: Date.now()};", "javascript", "spread"),

        # SQL
        ("SELECT department, AVG(salary) as avg_sal FROM employees GROUP BY department HAVING AVG(salary) > 50000 ORDER BY avg_sal DESC;", "sql", "aggregation"),
        ("SELECT e.name, d.name FROM employees e INNER JOIN departments d ON e.dept_id = d.id WHERE e.hire_date > '2020-01-01';", "sql", "join"),
        ("WITH ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) as rn FROM employees) SELECT * FROM ranked WHERE rn = 1;", "sql", "window"),
        ("INSERT INTO audit_log (action, user_id, timestamp) SELECT 'login', id, NOW() FROM users WHERE last_login < NOW() - INTERVAL '30 days';", "sql", "subquery"),

        # Bash
        ("find /var/log -name '*.log' -mtime +30 -exec rm {} \\;", "bash", "file_ops"),
        ("cat access.log | grep 'ERROR' | awk '{print $1}' | sort | uniq -c | sort -rn | head -10", "bash", "pipeline"),
        ("for f in *.csv; do echo \"Processing $f\"; python process.py \"$f\" > \"${f%.csv}.json\"; done", "bash", "loop"),
        ("tar czf backup-$(date +%Y%m%d).tar.gz --exclude='*.tmp' /home/user/data", "bash", "archive"),
        ("ssh user@server 'pg_dump mydb | gzip' > backup.sql.gz", "bash", "remote"),

        # Haskell
        ("quicksort [] = []\nquicksort (x:xs) = quicksort smaller ++ [x] ++ quicksort larger\n  where smaller = filter (<= x) xs\n        larger  = filter (> x) xs", "haskell", "recursion"),
        ("fmap (+1) (Just 5)  -- Just 6\nfmap (+1) Nothing   -- Nothing", "haskell", "functor"),
        ("do\n  x <- getLine\n  let n = read x :: Int\n  putStrLn (show (n * 2))", "haskell", "monad"),
    ]

    for code, lang, subdomain in code_examples:
        corpus.append({"prompt": code, "domain": "code", "subdomain": f"{lang}_{subdomain}"})

    # Generate more code variations
    algorithms = [
        "binary search", "merge sort", "breadth-first search",
        "depth-first search", "dijkstra's algorithm", "hash table lookup",
        "linked list reversal", "tree traversal", "dynamic programming",
    ]
    languages = ["Python", "Rust", "JavaScript", "Go", "C"]
    for algo in algorithms:
        for lang in languages:
            corpus.append({
                "prompt": f"Implement {algo} in {lang}:\n",
                "domain": "code",
                "subdomain": f"{lang.lower()}_{algo.replace(' ', '_')}",
            })

    # ═══════════════════════════════════════════════════════════
    # LOGIC & REASONING (reasoning crystal)
    # ═══════════════════════════════════════════════════════════

    logic_examples = [
        # Modus ponens
        ("If it rains, the ground gets wet. It is raining. Therefore,", "modus_ponens"),
        ("All mammals are warm-blooded. A whale is a mammal. Therefore,", "syllogism"),
        ("If A implies B, and B implies C, then A implies", "transitivity"),

        # Contrapositive
        ("If it rains, the ground is wet. The ground is dry. Therefore,", "contrapositive"),
        ("All birds can fly. This animal cannot fly. Therefore,", "contrapositive"),

        # Quantified reasoning
        ("Every student passed the exam. John is a student. Did John pass?", "universal"),
        ("Some cats are black. Whiskers is a cat. Is Whiskers necessarily black?", "existential"),
        ("No reptile is warm-blooded. A snake is a reptile. Is a snake warm-blooded?", "universal_neg"),

        # Conditional reasoning
        ("If and only if the switch is on, the light is on. The light is off. Is the switch on?", "biconditional"),
        ("Either it will rain or it will snow. It didn't rain. Therefore,", "disjunction"),

        # Causal reasoning
        ("The vase broke because it fell. If the vase hadn't fallen, would it have broken?", "counterfactual"),
        ("Every time I water the plant, it grows. I stopped watering it. What happens?", "causal"),

        # Planning / multi-step
        ("To bake a cake: 1) mix ingredients, 2) pour into pan, 3) bake at 350F. What is step 2?", "sequence"),
        ("I need to go from A to C. A connects to B. B connects to C. What is the path?", "path_finding"),
        ("The meeting is at 3pm. It takes 30 minutes to drive there. When should I leave?", "temporal"),
    ]

    for prompt, subdomain in logic_examples:
        corpus.append({"prompt": prompt, "domain": "reasoning", "subdomain": subdomain})

    # Generate more reasoning variations
    for _ in range(100):
        a = rng.choice(["dogs", "cats", "birds", "fish", "students", "teachers", "doctors"])
        b = rng.choice(["loyal", "independent", "intelligent", "fast", "careful", "diligent"])
        c = rng.choice(["animals", "beings", "creatures", "professionals", "people"])
        corpus.append({
            "prompt": f"All {a} are {b}. All {b} {c} are respected. Are {a} respected?",
            "domain": "reasoning",
            "subdomain": "syllogism_chain",
        })

    # ═══════════════════════════════════════════════════════════
    # TOOL CALLING (tool crystal)
    # ═══════════════════════════════════════════════════════════

    tool_examples = [
        ('{"function": "search", "parameters": {"query": "weather today"}}', "function_call"),
        ('Use the calculator tool to compute 15% of 847.', "tool_selection"),
        ('Call the API endpoint /users/123 with GET method.', "api_call"),
        ('Execute: bash("ls -la /home/user/documents")', "bash_tool"),
        ('Run the Python function: analyze_data(filepath="data.csv", columns=["age", "income"])', "python_tool"),
        ('Search the database for all orders placed in the last 7 days.', "db_query"),
        ('Send an email to team@company.com with subject "Weekly Report".', "action"),
        ('Schedule a meeting for tomorrow at 2pm with the engineering team.', "action"),
    ]

    for prompt, subdomain in tool_examples:
        corpus.append({"prompt": prompt, "domain": "tools", "subdomain": subdomain})

    # ═══════════════════════════════════════════════════════════
    # STRUCTURED OUTPUT (structure crystal)
    # ═══════════════════════════════════════════════════════════

    structure_examples = [
        ('Convert to JSON: name is Alice, age is 30, city is Portland', "json"),
        ('Format as CSV: headers are date, amount, description', "csv"),
        ('Generate a markdown table with columns: Feature, Status, Notes', "markdown"),
        ('Create a YAML config with: host: localhost, port: 8080, debug: true', "yaml"),
        ('Write an XML element: <user id="1"><name>Bob</name></user>', "xml"),
    ]

    for prompt, subdomain in structure_examples:
        corpus.append({"prompt": prompt, "domain": "structure", "subdomain": subdomain})

    # ═══════════════════════════════════════════════════════════
    # PROSE (language crystal — multiple registers)
    # ═══════════════════════════════════════════════════════════

    prose_examples = [
        # Narrative
        ("The old lighthouse keeper watched the storm approach from the west. Each wave grew larger than the last, and", "narrative"),
        ("She opened the letter carefully, already knowing what it would say. The handwriting was", "narrative"),

        # Expository
        ("Photosynthesis is the process by which plants convert sunlight into energy. The key steps are", "expository"),
        ("The French Revolution began in 1789 when", "expository"),
        ("Machine learning models learn patterns from data by", "expository"),

        # Argumentative
        ("While some argue that remote work reduces productivity, the evidence suggests that", "argumentative"),
        ("The most compelling reason to invest in renewable energy is", "argumentative"),

        # Technical
        ("The TCP three-way handshake works as follows:", "technical"),
        ("In a B-tree of order m, each node can have at most", "technical"),
        ("The time complexity of merge sort is O(n log n) because", "technical"),

        # Conversational
        ("Hey, have you tried that new restaurant downtown? I heard their", "conversational"),
        ("So basically what happened was, the server went down at 3am and", "conversational"),

        # Instructional
        ("To change a tire: First, loosen the lug nuts. Then,", "instructional"),
        ("Step 1: Open the terminal. Step 2: Navigate to the project directory. Step 3:", "instructional"),
    ]

    for prompt, subdomain in prose_examples:
        corpus.append({"prompt": prompt, "domain": "prose", "subdomain": subdomain})

    # ═══════════════════════════════════════════════════════════
    # COUNTING & AGGREGATION (sequence crystal)
    # ═══════════════════════════════════════════════════════════

    counting_examples = [
        ("How many vowels are in the word 'mississippi'?", "count_chars"),
        ("How many words are in this sentence: 'The quick brown fox jumps over the lazy dog'?", "count_words"),
        ("Count the number of items: apple, banana, cherry, date, elderberry.", "count_items"),
        ("What is the sum of 1 + 2 + 3 + 4 + 5?", "sum"),
        ("Sort these numbers from smallest to largest: 7, 2, 9, 1, 5", "sort"),
        ("What is the average of 10, 20, 30, 40, 50?", "average"),
        ("Find the maximum value: 23, 45, 12, 67, 34", "max"),
        ("Reverse the list: [1, 2, 3, 4, 5]", "reverse"),
    ]

    for prompt, subdomain in counting_examples:
        corpus.append({"prompt": prompt, "domain": "sequence", "subdomain": subdomain})

    # ═══════════════════════════════════════════════════════════
    # Shuffle and report
    # ═══════════════════════════════════════════════════════════

    rng.shuffle(corpus)

    # Stats
    domains = {}
    for ex in corpus:
        d = ex["domain"]
        domains[d] = domains.get(d, 0) + 1

    print(f"\n  Diverse corpus built: {len(corpus)} examples", file=sys.stderr)
    for d, n in sorted(domains.items(), key=lambda x: -x[1]):
        print(f"    {d:15s}: {n:4d}", file=sys.stderr)

    return corpus


def main():
    corpus = build_corpus()

    output_path = Path("lattice/diverse_corpus.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(corpus, f, indent=2)
    print(f"\n  💾 Saved: {output_path} ({len(corpus)} examples)", file=sys.stderr)


if __name__ == "__main__":
    main()
