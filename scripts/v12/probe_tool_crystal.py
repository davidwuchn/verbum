"""Probe the Tool-Calling Crystal — compare tool-call activation geometry to lambda crystal.

Hypothesis: Tool calling IS lambda calculus applied to JSON schema.
If true, the same circuits that activate for lambda composition should also
activate for tool-call schema binding (RECOGNITION → SELECTION → SCHEMA BINDING).

Methodology:
  1. Define ~200 probes across five domains
  2. Run each through Qwen3-14B, hooking hidden states at every 4th layer
  3. Build per-layer RDMs (cosine similarity matrices)
  4. Cross-domain analysis: Tool×Lambda overlap vs Tool×Prose separation
  5. High Tool×Lambda at specific layers → shared crystal

Interpretation:
  - Tool×Lambda HIGH at deep layers → shared computational substrate (strong hypothesis)
  - Tool×Lambda HIGH at mid layers only → shared features, distinct integration (partial)
  - Tool×Lambda LOW everywhere → separate circuits (null result)

Usage:
    cd /Users/mwhitford/src/verbum
    uv run python scripts/v12/probe_tool_crystal.py
    uv run python scripts/v12/probe_tool_crystal.py --model Qwen/Qwen3-8B

Outputs (lattice/tool_crystal/):
    rdms.npz            — per-layer RDM matrices (n_probes × n_probes each)
    hidden_states.npz   — per-layer hidden state matrices (n_probes × d_model each)
    analysis.json       — cross-domain similarity tables + full metadata
    probes.json         — probe corpus (for reproducibility)

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path
from typing import NamedTuple

import numpy as np

# ══════════════════════════════════════════════════════════════════════
# Probe corpus — ~200 probes across 5 domains
# ══════════════════════════════════════════════════════════════════════

# Hermes-format tool call template used for all tool-domain probes.
# Probe text is truncated at the final <|im_start|>assistant\n so the
# model's last-token activation is at the point it DECIDES whether and
# how to call a tool.  That is where the crystal lives.

def _tc(system_tools: str, user_msg: str) -> str:
    """Build a Qwen3 / Hermes-style conversation up to the assistant turn."""
    return (
        "<|im_start|>system\n"
        "You are a helpful assistant.\n\n"
        "# Tools\n\n"
        "You may call one or more functions to assist with the user query.\n\n"
        "You are provided with function signatures within XML tags:\n"
        "<tools>\n"
        f"{system_tools}\n"
        "</tools>\n"
        "<|im_end|>\n"
        f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )

# ── tool schemas used across probes ──────────────────────────────────

_WEATHER_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"},
            },
            "required": ["city"],
        },
    },
})

_SEARCH_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Search the web for recent information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results", "default": 10},
                "sort": {"type": "string", "enum": ["relevance", "date"], "default": "relevance"},
            },
            "required": ["query"],
        },
    },
})

_CALC_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate"},
            },
            "required": ["expression"],
        },
    },
})

_FILE_READ_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read contents of a file at a given path",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute file path"},
                "encoding": {"type": "string", "default": "utf-8"},
            },
            "required": ["path"],
        },
    },
})

_DB_QUERY_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "query_database",
        "description": "Execute a SQL query against the application database",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "SQL query string"},
                "params": {"type": "array", "items": {"type": "string"}, "description": "Query parameters"},
                "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
            },
            "required": ["sql"],
        },
    },
})

_FILTER_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "filter_records",
        "description": "Filter a dataset by a list of conditions",
        "parameters": {
            "type": "object",
            "properties": {
                "dataset": {"type": "string"},
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "op": {"type": "string", "enum": [">", "<", "=", ">=", "<=", "!="]},
                            "value": {},
                        },
                        "required": ["field", "op", "value"],
                    },
                },
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["dataset", "filters"],
        },
    },
})

_SEND_EMAIL_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email message",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "cc": {"type": "array", "items": {"type": "string"}},
                "attachments": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["to", "subject", "body"],
        },
    },
})

_PYTHON_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "run_python",
        "description": "Execute Python code and return its output",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to run"},
                "timeout": {"type": "integer", "default": 10},
            },
            "required": ["code"],
        },
    },
})

_BASH_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "run_bash",
        "description": "Run a bash shell command and return stdout/stderr",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "cwd": {"type": "string", "description": "Working directory"},
            },
            "required": ["command"],
        },
    },
})

_CALENDAR_TOOL = json.dumps({
    "type": "function",
    "function": {
        "name": "create_calendar_event",
        "description": "Create a new calendar event",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "attendees": {"type": "array", "items": {"type": "string"}},
                "location": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["title", "start", "end"],
        },
    },
})

# ── probe builders ────────────────────────────────────────────────────

def _build_probes() -> list[dict]:
    probes: list[dict] = []

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 1: RECOGNITION (40 probes)
    # Minimal pairs: same topic, one signals tool use, one doesn't.
    # Directly labelled recognition/tool vs recognition/no_tool so we
    # can compute the activation *difference* for the same concept.
    # ─────────────────────────────────────────────────────────────────

    _WEATHER_AND_SEARCH = f"{_WEATHER_TOOL}\n{_SEARCH_TOOL}"

    recognition_tool_pairs = [
        # (tool_prompt, no_tool_prompt, topic)
        ("What's the current weather in Tokyo?",
         "Describe what a rainy autumn day in Tokyo feels like.",
         "weather"),
        ("Calculate 15% tip on a $84.50 restaurant bill.",
         "Explain how percentages work in everyday life.",
         "math"),
        ("Search for recent papers published this month on attention mechanisms.",
         "Attention is a mechanism in neural networks that weighs token relevance.",
         "search"),
        ("What time is it right now in London?",
         "London is a major city in the United Kingdom.",
         "time"),
        ("Look up the stock price of Apple right now.",
         "Apple is one of the most valuable technology companies in the world.",
         "stocks"),
        ("Find the nearest coffee shop to 123 Main Street.",
         "Coffee shops are common gathering places in urban areas.",
         "location"),
        ("How many days until Christmas?",
         "Christmas is celebrated on December 25th each year.",
         "date"),
        ("Translate 'hello world' into French.",
         "French is a Romance language spoken in France and many other countries.",
         "translation"),
        ("Check if the website https://example.com is currently online.",
         "Websites can be hosted on servers around the world.",
         "network"),
        ("What is the current exchange rate between USD and EUR?",
         "Exchange rates fluctuate based on economic conditions.",
         "finance"),
        ("Search for the latest news about the Mars mission.",
         "Space exploration has advanced significantly in recent decades.",
         "news"),
        ("Calculate the compound interest on $1000 at 5% for 3 years.",
         "Compound interest grows faster than simple interest over time.",
         "finance2"),
        ("Get the weather forecast for Seattle this weekend.",
         "Seattle is known for its rainy and overcast weather.",
         "forecast"),
        ("Find flights from New York to Paris next Tuesday.",
         "Transatlantic flights typically take around 7-8 hours.",
         "travel"),
        ("Send this message to john@example.com: Meeting at 3pm.",
         "Email remains one of the most widely used communication tools.",
         "email"),
        ("List all files in the /home/user/documents directory.",
         "File systems organize data in hierarchical directory structures.",
         "filesystem"),
        ("Run the test suite for the current project.",
         "Test suites help developers catch bugs before deployment.",
         "code"),
        ("Query the database for all users registered in the last 30 days.",
         "Databases store structured data for efficient retrieval.",
         "database"),
        ("Schedule a meeting with Alice and Bob at 2pm tomorrow.",
         "Effective meetings have clear agendas and defined time limits.",
         "calendar"),
        ("What is the population of Brazil?",
         "Brazil is the largest country in South America.",
         "facts"),
    ]

    for tool_prompt, no_tool_prompt, topic in recognition_tool_pairs:
        probes.append({
            "prompt": _tc(_WEATHER_AND_SEARCH, tool_prompt),
            "domain": "recognition",
            "subdomain": "recognition/tool",
            "topic": topic,
        })
        probes.append({
            "prompt": (
                "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
                f"<|im_start|>user\n{no_tool_prompt}<|im_end|>\n"
                "<|im_start|>assistant\n"
            ),
            "domain": "recognition",
            "subdomain": "recognition/no_tool",
            "topic": topic,
        })

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 2: SELECTION (40 probes)
    # Same task, different tool choices — model must SELECT among tools.
    # The key question: does tool selection activate the same circuits
    # as schema binding, or is it a separate step?
    # ─────────────────────────────────────────────────────────────────

    _WEATHER_SEARCH_TOOLS = f"{_WEATHER_TOOL}\n{_SEARCH_TOOL}"
    _CALC_PYTHON_TOOLS = f"{_CALC_TOOL}\n{_PYTHON_TOOL}"
    _BASH_FILE_TOOLS = f"{_BASH_TOOL}\n{_FILE_READ_TOOL}"
    _ALL_TOOLS = f"{_WEATHER_TOOL}\n{_SEARCH_TOOL}\n{_CALC_TOOL}\n{_PYTHON_TOOL}\n{_BASH_TOOL}"

    selection_probes = [
        # Weather queries — weather_api vs web_search
        (_WEATHER_SEARCH_TOOLS,
         "I need current weather conditions in Paris.",
         "weather_vs_search"),
        (_WEATHER_SEARCH_TOOLS,
         "What's the forecast for the next 5 days in Berlin?",
         "weather_vs_search"),
        (_WEATHER_SEARCH_TOOLS,
         "Is it raining in Sydney right now?",
         "weather_vs_search"),
        (_WEATHER_SEARCH_TOOLS,
         "What was the weather like in Rome last week?",
         "weather_vs_search_historical"),
        (_WEATHER_SEARCH_TOOLS,
         "What's the best time of year to visit Iceland weather-wise?",
         "weather_vs_search_general"),

        # Math — calculator vs python
        (_CALC_PYTHON_TOOLS,
         "Calculate the square root of 144.",
         "calc_vs_python"),
        (_CALC_PYTHON_TOOLS,
         "What is 17 factorial?",
         "calc_vs_python"),
        (_CALC_PYTHON_TOOLS,
         "Compute the sum of all prime numbers less than 100.",
         "calc_vs_python"),
        (_CALC_PYTHON_TOOLS,
         "What is the 50th Fibonacci number?",
         "calc_vs_python"),
        (_CALC_PYTHON_TOOLS,
         "Plot the values of sin(x) from 0 to 2π.",
         "calc_vs_python_plot"),

        # File operations — bash vs file_read
        (_BASH_FILE_TOOLS,
         "Show me the contents of /etc/hosts.",
         "bash_vs_file"),
        (_BASH_FILE_TOOLS,
         "How many lines are in /var/log/system.log?",
         "bash_vs_file"),
        (_BASH_FILE_TOOLS,
         "What files are in the /tmp directory?",
         "bash_vs_file_listing"),
        (_BASH_FILE_TOOLS,
         "Read the README file in the current project.",
         "bash_vs_file"),
        (_BASH_FILE_TOOLS,
         "Find all Python files modified in the last hour.",
         "bash_vs_file_find"),

        # Overlapping capabilities — all tools
        (_ALL_TOOLS,
         "What is the current Bitcoin price in dollars?",
         "all_tools_price"),
        (_ALL_TOOLS,
         "Find the top 10 Python packages by downloads this month.",
         "all_tools_ranking"),
        (_ALL_TOOLS,
         "How long would it take to drive from Boston to Miami?",
         "all_tools_travel"),
        (_ALL_TOOLS,
         "What languages are available for the next Olympic Games?",
         "all_tools_events"),
        (_ALL_TOOLS,
         "Show me who won the last World Cup.",
         "all_tools_facts"),

        # Ambiguous — both tools are valid
        (_CALC_PYTHON_TOOLS,
         "Convert 100 USD to Japanese Yen.",
         "calc_vs_python_conversion"),
        (_CALC_PYTHON_TOOLS,
         "How many seconds are in a year?",
         "calc_vs_python_simple"),
        (_CALC_PYTHON_TOOLS,
         "Generate 10 random numbers between 1 and 100.",
         "calc_vs_python_rng"),
        (_BASH_FILE_TOOLS,
         "Show disk usage for each directory under /home.",
         "bash_vs_file_disk"),
        (_BASH_FILE_TOOLS,
         "What process is using port 8080?",
         "bash_vs_file_proc"),

        # Clear single-tool (high-confidence selection)
        (_ALL_TOOLS,
         "What is the weather in Reykjavik today?",
         "clear_weather"),
        (_ALL_TOOLS,
         "Compute 2 raised to the power of 32.",
         "clear_calc"),
        (_ALL_TOOLS,
         "Search for 'transformer architecture survey 2024'.",
         "clear_search"),
        (_ALL_TOOLS,
         "Run: cat /proc/cpuinfo | head -20",
         "clear_bash"),
        (_ALL_TOOLS,
         "Read the file at /etc/passwd.",
         "clear_file"),

        # Multi-step (need to chain tools)
        (_ALL_TOOLS,
         "Find the weather in the capital of Australia.",
         "multi_search_then_weather"),
        (_ALL_TOOLS,
         "Calculate the average of the first 20 Fibonacci numbers.",
         "multi_calc_then_average"),
        (_ALL_TOOLS,
         "List all .py files here and count the total lines.",
         "multi_bash_then_count"),
        (_ALL_TOOLS,
         "Search for the current price of gold and convert it to euros.",
         "multi_search_then_convert"),
        (_ALL_TOOLS,
         "Find out the timezone in Bangkok and tell me the current time there.",
         "multi_search_then_time"),

        # Tool used incorrectly
        (_CALC_PYTHON_TOOLS,
         "What is the capital of France?",
         "wrong_tool_factual"),
        (_BASH_FILE_TOOLS,
         "What is the meaning of life?",
         "wrong_tool_philosophical"),
        (_WEATHER_SEARCH_TOOLS,
         "Explain the Pythagorean theorem.",
         "wrong_tool_math"),
        (_ALL_TOOLS,
         "Write a haiku about autumn.",
         "wrong_tool_creative"),
        (_ALL_TOOLS,
         "What is the definition of entropy?",
         "wrong_tool_definition"),
    ]

    for tools, user_msg, subtopic in selection_probes:
        probes.append({
            "prompt": _tc(tools, user_msg),
            "domain": "selection",
            "subdomain": f"selection/{subtopic}",
        })

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 3: SCHEMA BINDING (60 probes)
    # Natural language → typed JSON argument mapping.
    # This is THE KEY domain — schema binding IS λ-application:
    #   bind(schema, NL) → {arg_name: typed_value, ...}
    # The same typed application circuit should activate here.
    # ─────────────────────────────────────────────────────────────────

    schema_probes = [
        # 1-arg / simple string
        (_WEATHER_TOOL,    "What's the weather in Tokyo?",
         "schema_1arg_string"),
        (_WEATHER_TOOL,    "How's the weather in New York?",
         "schema_1arg_string"),
        (_WEATHER_TOOL,    "Tell me the weather for London please.",
         "schema_1arg_string"),
        (_WEATHER_TOOL,    "Current conditions in São Paulo?",
         "schema_1arg_string"),
        (_WEATHER_TOOL,    "Weather update for Sydney.",
         "schema_1arg_string"),

        # 2-arg with enum
        (_WEATHER_TOOL,    "What's the temperature in Berlin in Fahrenheit?",
         "schema_2arg_enum"),
        (_WEATHER_TOOL,    "Get the weather in Oslo, use Celsius.",
         "schema_2arg_enum"),
        (_WEATHER_TOOL,    "How hot is it in Dubai? Use Fahrenheit.",
         "schema_2arg_enum"),

        # 2-3 arg mixed types
        (_SEARCH_TOOL,     "Search for recent papers on attention mechanisms.",
         "schema_2arg_int"),
        (_SEARCH_TOOL,     "Find me the top 5 results for 'quantum computing'.",
         "schema_2arg_int_explicit"),
        (_SEARCH_TOOL,     "Look up 'climate change solutions', sorted by date.",
         "schema_2arg_enum_sort"),
        (_SEARCH_TOOL,     "Search for 'Python tutorial' and show me 20 results sorted by date.",
         "schema_3arg_mixed"),
        (_SEARCH_TOOL,     "Find the latest news on AI regulation, limit to 3 results.",
         "schema_2arg_int_small"),
        (_SEARCH_TOOL,     "Search: 'transformer interpretability', by relevance, 15 results.",
         "schema_3arg_explicit"),

        # Integer / arithmetic args
        (_CALC_TOOL,       "Calculate 15% of 847.",
         "schema_1arg_expr"),
        (_CALC_TOOL,       "What is 2 to the power of 10?",
         "schema_1arg_expr"),
        (_CALC_TOOL,       "Compute the area of a circle with radius 7.",
         "schema_1arg_expr_derived"),
        (_CALC_TOOL,       "Evaluate: (3 + 5) * 12 / 4",
         "schema_1arg_expr_verbatim"),
        (_CALC_TOOL,       "What is the square root of 256?",
         "schema_1arg_expr_func"),

        # File path binding
        (_FILE_READ_TOOL,  "Read the file /home/user/notes.txt.",
         "schema_1arg_path"),
        (_FILE_READ_TOOL,  "Show me /etc/hosts.",
         "schema_1arg_path_short"),
        (_FILE_READ_TOOL,  "Open /var/log/app.log with UTF-8 encoding.",
         "schema_2arg_path_encoding"),
        (_FILE_READ_TOOL,  "Read /tmp/data.csv as latin-1.",
         "schema_2arg_path_encoding"),
        (_FILE_READ_TOOL,  "What's in /usr/local/bin/startup.sh?",
         "schema_1arg_path"),

        # SQL with params array
        (_DB_QUERY_TOOL,   "Get all users where status is 'active'.",
         "schema_sql_noparams"),
        (_DB_QUERY_TOOL,   "Query the orders table for the last 30 days.",
         "schema_sql_derived"),
        (_DB_QUERY_TOOL,   "Find all records in products where price > 100.",
         "schema_sql_filter"),
        (_DB_QUERY_TOOL,   "Run: SELECT COUNT(*) FROM events WHERE user_id = 42",
         "schema_sql_verbatim_params"),
        (_DB_QUERY_TOOL,   "Select the top 10 most recent log entries with timeout 60.",
         "schema_sql_3arg"),

        # Nested object filters (THE KEY TEST — JSON nesting = λ nesting)
        (_FILTER_TOOL,     "Filter the sales dataset for records where age > 30.",
         "schema_nested_1filter"),
        (_FILTER_TOOL,     "From the customers table, show me rows where country = 'US' and age >= 18.",
         "schema_nested_2filters"),
        (_FILTER_TOOL,     "Filter transactions: amount > 1000 and currency = 'USD' and status != 'pending'.",
         "schema_nested_3filters"),
        (_FILTER_TOOL,     "Get employees dataset where department = 'Engineering' and salary > 90000, limit 50.",
         "schema_nested_2filters_limit"),
        (_FILTER_TOOL,     "From products: category = 'electronics', price < 500, in_stock = true.",
         "schema_nested_3filters_bool"),

        # Array args (to/cc for email)
        (_SEND_EMAIL_TOOL, "Send an email to alice@example.com: subject 'Meeting' body 'See you at 3pm'.",
         "schema_array_1to"),
        (_SEND_EMAIL_TOOL, "Email bob@example.com and carol@example.com about the project update.",
         "schema_array_2to"),
        (_SEND_EMAIL_TOOL, "Send to team@example.com, CC manager@example.com, subject 'Report' body 'Please review.'",
         "schema_array_to_cc"),
        (_SEND_EMAIL_TOOL, "Email support@company.com with subject 'Bug report' and attach /tmp/log.txt.",
         "schema_array_attachment"),
        (_SEND_EMAIL_TOOL, "Send meeting invite to [a@x.com, b@x.com, c@x.com] subject 'Q4 Planning' body 'Agenda attached.'",
         "schema_array_3to"),

        # Calendar — datetime binding
        (_CALENDAR_TOOL,   "Schedule a meeting tomorrow at 2pm for 1 hour.",
         "schema_datetime_derived"),
        (_CALENDAR_TOOL,   "Create an event: 'Design Review' on Friday at 10am, ends at 11:30am.",
         "schema_datetime_explicit"),
        (_CALENDAR_TOOL,   "Book a 30-minute standup at 9am Monday.",
         "schema_datetime_duration"),
        (_CALENDAR_TOOL,   "Set up 'Team Lunch' for 12pm next Thursday at 'The Grill', invite alice@x.com and bob@x.com.",
         "schema_datetime_full"),
        (_CALENDAR_TOOL,   "Add 'Quarterly Review' to the calendar for the last Friday of this month, 3-5pm.",
         "schema_datetime_relative"),

        # Python code binding
        (_PYTHON_TOOL,     "Run Python to compute the sum of squares from 1 to 100.",
         "schema_code_derived"),
        (_PYTHON_TOOL,     "Execute: import os; print(os.getcwd())",
         "schema_code_verbatim"),
        (_PYTHON_TOOL,     "Use Python to reverse the string 'Hello, World!'",
         "schema_code_derived"),
        (_PYTHON_TOOL,     "Run Python with a 5-second timeout to test if numpy is installed.",
         "schema_code_timeout"),
        (_PYTHON_TOOL,     "Execute this code: [x**2 for x in range(10)]",
         "schema_code_verbatim"),

        # Name mapping edge cases (key insight: NL surface ≠ JSON key)
        (_SEARCH_TOOL,     "Look for 'attention is all you need'.",
         "schema_name_map_query"),
        (_SEARCH_TOOL,     "Find stuff about RLHF.",
         "schema_name_map_informal"),
        (_WEATHER_TOOL,    "What's it like outside in Chicago?",
         "schema_name_map_implicit"),
        (_WEATHER_TOOL,    "Temperature check for Mumbai.",
         "schema_name_map_fragment"),
        (_FILE_READ_TOOL,  "Can you show me what's inside ~/.bashrc?",
         "schema_name_map_tilde"),

        # High arity (5+ args test — the most complex schema binding)
        (_FILTER_TOOL + "\n" + _SEND_EMAIL_TOOL,
         "Filter the sales data for Q4 (year >= 2023, quarter = 4, region = 'APAC', status = 'closed', amount > 5000) and limit to 200 records.",
         "schema_5arg_complex"),
        (_CALENDAR_TOOL,
         "Create 'Annual Conference' starting 2024-06-15T09:00:00 ending 2024-06-15T18:00:00 at 'Grand Ballroom', invite all@company.com, with description 'Annual all-hands meeting'.",
         "schema_6arg_all"),
    ]

    for tools, user_msg, subtopic in schema_probes:
        probes.append({
            "prompt": _tc(tools, user_msg),
            "domain": "schema_binding",
            "subdomain": f"schema_binding/{subtopic}",
        })

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 4: FORMAT (30 probes)
    # JSON/structured output emission variations.
    # Does the format of the expected output change activation geometry,
    # or is the underlying schema-binding crystal format-independent?
    # ─────────────────────────────────────────────────────────────────

    # For FORMAT probes we show the model *partial* assistant output
    # to probe at specific emission points (Hermes vs raw JSON vs parallel).

    def _tc_partial(system_tools: str, user_msg: str, assistant_prefix: str) -> str:
        """Build conversation with partial assistant output prefix."""
        return (
            "<|im_start|>system\n"
            "You are a helpful assistant.\n\n"
            "# Tools\n\n"
            "You may call one or more functions to assist with the user query.\n\n"
            "You are provided with function signatures within XML tags:\n"
            "<tools>\n"
            f"{system_tools}\n"
            "</tools>\n"
            "<|im_end|>\n"
            f"<|im_start|>user\n{user_msg}<|im_end|>\n"
            f"<|im_start|>assistant\n{assistant_prefix}"
        )

    format_probes = [
        # Hermes-style: last token inside the tool_call block
        (_tc_partial(_WEATHER_TOOL, "What's the weather in Tokyo?",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"city": "Tokyo"'),
         "format", "format/hermes_partial_args"),
        (_tc_partial(_SEARCH_TOOL, "Search for recent AI papers.",
                     '<tool_call>\n{"name": "web_search", "arguments": {"query": "recent AI papers"'),
         "format", "format/hermes_partial_args"),
        (_tc_partial(_CALC_TOOL, "What is 15% of 200?",
                     '<tool_call>\n{"name": "calculator", "arguments": {"expression": "0.15 * 200"'),
         "format", "format/hermes_partial_args"),
        (_tc_partial(_WEATHER_TOOL, "Temperature in Dubai in Fahrenheit.",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"city": "Dubai", "units": "fahrenheit"'),
         "format", "format/hermes_2args"),
        (_tc_partial(_SEARCH_TOOL, "Find 5 results for quantum computing sorted by date.",
                     '<tool_call>\n{"name": "web_search", "arguments": {"query": "quantum computing", "limit": 5, "sort": "date"'),
         "format", "format/hermes_3args"),

        # Raw JSON object (no tool_call wrapper)
        (_tc_partial(_WEATHER_TOOL, "What's the weather in Paris?",
                     '{"name": "get_weather", "arguments": {"city": "Paris"'),
         "format", "format/raw_json_partial"),
        (_tc_partial(_CALC_TOOL, "Compute 42 * 17.",
                     '{"name": "calculator", "arguments": {"expression": "42 * 17"'),
         "format", "format/raw_json_partial"),
        (_tc_partial(_SEARCH_TOOL, "Look up Python tutorials.",
                     '{"name": "web_search", "arguments": {"query": "Python tutorials"'),
         "format", "format/raw_json_partial"),

        # Parallel calls (multiple tools in one response)
        (_tc_partial(f"{_WEATHER_TOOL}\n{_SEARCH_TOOL}",
                     "What's the weather in both Tokyo and London?",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"city": "Tokyo"}}</tool_call>\n<tool_call>\n{"name": "get_weather", "arguments": {"city": "London"'),
         "format", "format/parallel_calls"),
        (_tc_partial(f"{_WEATHER_TOOL}\n{_CALC_TOOL}",
                     "Check the weather in Miami and calculate 15% of 200.",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"city": "Miami"}}</tool_call>\n<tool_call>\n{"name": "calculator", "arguments": {"expression": "0.15 * 200"'),
         "format", "format/parallel_different_tools"),

        # Completed tool calls (full JSON, last token is closing brace)
        (_tc_partial(_WEATHER_TOOL, "Weather in Beijing.",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"city": "Beijing"}}</tool_call>'),
         "format", "format/hermes_complete"),
        (_tc_partial(_SEARCH_TOOL, "Search for news about climate.",
                     '<tool_call>\n{"name": "web_search", "arguments": {"query": "climate news", "limit": 10}}</tool_call>'),
         "format", "format/hermes_complete_2args"),

        # YAML output comparison (non-JSON structured)
        (_tc_partial(_WEATHER_TOOL, "Get weather for Nairobi.",
                     "name: get_weather\narguments:\n  city: Nairobi"),
         "format", "format/yaml_structured"),
        (_tc_partial(_CALC_TOOL, "Calculate area of circle radius 5.",
                     "name: calculator\narguments:\n  expression: 3.14159 * 5"),
         "format", "format/yaml_structured"),

        # XML output comparison
        (_tc_partial(_WEATHER_TOOL, "Weather in Cairo.",
                     "<function_call><name>get_weather</name><arguments><city>Cairo</city></arguments>"),
         "format", "format/xml_structured"),
        (_tc_partial(_SEARCH_TOOL, "Search web for rust programming.",
                     "<function_call><name>web_search</name><arguments><query>rust programming</query></arguments>"),
         "format", "format/xml_structured"),

        # Markdown code block JSON
        (_tc_partial(_WEATHER_TOOL, "What's the weather in Rome?",
                     '```json\n{"name": "get_weather", "arguments": {"city": "Rome"'),
         "format", "format/markdown_json"),
        (_tc_partial(_CALC_TOOL, "Compute 7 factorial.",
                     '```json\n{"name": "calculator", "arguments": {"expression": "7 * 6 * 5 * 4 * 3 * 2 * 1"'),
         "format", "format/markdown_json"),

        # Plain text tool call (natural language format — low formality)
        (_tc_partial(_WEATHER_TOOL, "Check the weather in Oslo.",
                     "I'll call get_weather with city=Oslo"),
         "format", "format/plaintext_nl"),
        (_tc_partial(_SEARCH_TOOL, "Search for transformer papers.",
                     "Calling web_search(query='transformer papers'"),
         "format", "format/plaintext_python_style"),

        # Malformed / truncated JSON (probes robustness of schema binding)
        (_tc_partial(_WEATHER_TOOL, "Weather in Vienna.",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"city":'),
         "format", "format/partial_truncated"),
        (_tc_partial(_SEARCH_TOOL, "Search for neural networks.",
                     '<tool_call>\n{"name": "web_search", "arguments": {'),
         "format", "format/partial_open_brace"),

        # Different argument orderings
        (_tc_partial(_SEARCH_TOOL, "Latest AI news, top 5 by date.",
                     '<tool_call>\n{"name": "web_search", "arguments": {"sort": "date", "limit": 5, "query": "latest AI news"'),
         "format", "format/args_reordered"),
        (_tc_partial(_WEATHER_TOOL, "Fahrenheit weather for Moscow.",
                     '<tool_call>\n{"name": "get_weather", "arguments": {"units": "fahrenheit", "city": "Moscow"'),
         "format", "format/args_reordered_2"),

        # Null/empty argument values
        (_tc_partial(_SEARCH_TOOL, "Just search for something interesting.",
                     '<tool_call>\n{"name": "web_search", "arguments": {"query": "interesting topics"'),
         "format", "format/vague_binding"),

        # Format: response BEFORE tool call (reasoning prefix)
        (_tc_partial(_WEATHER_TOOL, "What should I wear in Stockholm today?",
                     "To answer this, I need to check the current weather in Stockholm first.\n<tool_call>\n{\"name\": \"get_weather\", \"arguments\": {\"city\": \"Stockholm\""),
         "format", "format/reasoning_prefix"),
        (_tc_partial(_CALC_TOOL, "I need the exact value of pi squared.",
                     "Let me calculate that for you.\n<tool_call>\n{\"name\": \"calculator\", \"arguments\": {\"expression\": \"3.14159**2\""),
         "format", "format/reasoning_prefix"),
        (_tc_partial(_SEARCH_TOOL, "I want to know about recent SpaceX launches.",
                     "I'll search for the latest information.\n<tool_call>\n{\"name\": \"web_search\", \"arguments\": {\"query\": \"SpaceX recent launches\""),
         "format", "format/reasoning_prefix"),

        # Format: explicit no-tool response
        (_tc_partial(f"{_WEATHER_TOOL}\n{_CALC_TOOL}",
                     "What is the capital of Japan?",
                     "The capital of Japan is Tokyo."),
         "format", "format/no_tool_response"),
        (_tc_partial(f"{_WEATHER_TOOL}\n{_CALC_TOOL}",
                     "Explain what a hash function is.",
                     "A hash function maps data of arbitrary size to fixed-size values."),
         "format", "format/no_tool_prose"),
    ]

    for item in format_probes:
        if len(item) == 3:
            prompt_text, domain, subdomain = item
            probes.append({
                "prompt": prompt_text,
                "domain": domain,
                "subdomain": subdomain,
            })

    # ─────────────────────────────────────────────────────────────────
    # DOMAIN 5: CONTROL (30 probes)
    # Should NOT activate tool circuits.
    # If they DO activate similarly to tool probes → false positive rate.
    # Subcategories: prose, pure_math, code, lambda_calculus
    # ─────────────────────────────────────────────────────────────────

    _PLAIN_SYS = (
        "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
    )

    def _plain(user_msg: str) -> str:
        return (
            f"{_PLAIN_SYS}"
            f"<|im_start|>user\n{user_msg}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

    # Prose narratives (no computational task)
    prose_controls = [
        "Write a short story about a lighthouse keeper on a stormy night.",
        "Describe the sensation of walking barefoot on a warm sandy beach.",
        "Explain the historical significance of the printing press in three paragraphs.",
        "Write a poem about the passing of seasons.",
        "Summarize the plot of Romeo and Juliet.",
        "Describe what it feels like to watch a sunrise from a mountain summit.",
        "Write a travel guide introduction for Kyoto, Japan.",
        "Explain what empathy means in your own words.",
    ]

    # Pure math — no tool context, no tool schema, just math reasoning
    math_controls = [
        "What is 2 + 2?",
        "Prove that the square root of 2 is irrational.",
        "What is the derivative of x^3 + 2x^2 - 5x + 1?",
        "Explain the Pythagorean theorem and provide a proof.",
        "What is the integral of sin(x) from 0 to π?",
        "Describe the difference between permutations and combinations.",
        "What is a prime number? Give five examples.",
    ]

    # Code (Python function defs — NOT tool calls)
    code_controls = [
        "Write a Python function that returns the nth Fibonacci number.",
        "Implement bubble sort in Python.",
        "Write a Python decorator that measures function execution time.",
        "Show me how to read a CSV file using the pandas library.",
        "Write a recursive function to compute the factorial of n in Python.",
        "Implement a binary search function in Python.",
        "Write a Python class for a stack data structure.",
    ]

    # Lambda calculus expressions (from our existing probe domain)
    lambda_controls = [
        "Express the S combinator in lambda calculus.",
        "What is the Church encoding of the number 3?",
        "Show the beta reduction of (λx.x)(λy.y).",
        "What is the Y combinator and what does it do?",
        "Express the boolean AND operation using Church booleans.",
        "Reduce (λx.λy.x) a b to normal form.",
        "What is the difference between applicative and normal order reduction in lambda calculus?",
        "Express the composition combinator B = λf.λg.λx.f(g x) in Python.",
    ]

    for prompt in prose_controls:
        probes.append({
            "prompt": _plain(prompt),
            "domain": "control",
            "subdomain": "control/prose",
        })

    for prompt in math_controls:
        probes.append({
            "prompt": _plain(prompt),
            "domain": "control",
            "subdomain": "control/pure_math",
        })

    for prompt in code_controls:
        probes.append({
            "prompt": _plain(prompt),
            "domain": "control",
            "subdomain": "control/code",
        })

    for prompt in lambda_controls:
        probes.append({
            "prompt": _plain(prompt),
            "domain": "control",
            "subdomain": "control/lambda_calculus",
        })

    return probes


# ══════════════════════════════════════════════════════════════════════
# Model loading & activation extraction
# ══════════════════════════════════════════════════════════════════════

# Layer indices to hook for Qwen3-14B (40 layers).
# Every 4th layer + layer 39 (final): 11 hooks total.
QWEN3_14B_HOOK_LAYERS = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 39]

# For Qwen3-8B (36 layers), use every 4th + final.
QWEN3_8B_HOOK_LAYERS = [0, 4, 8, 12, 16, 20, 24, 28, 32, 35]


def get_hook_layers(n_layers: int) -> list[int]:
    """Return hook layer indices for a model with n_layers transformer blocks."""
    # Every 4th layer
    layers = list(range(0, n_layers, 4))
    # Ensure final layer is included
    if n_layers - 1 not in layers:
        layers.append(n_layers - 1)
    return sorted(set(layers))


def run_extraction(
    model_name: str,
    probes: list[dict],
    device: str = "mps",
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    """Load model, register hooks, run all probes, return hidden states and RDMs.

    Returns:
        hidden_states: {layer_idx: (n_probes, d_model) float32 array}
        rdms:          {layer_idx: (n_probes, n_probes) float32 cosine sim matrix}
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"\n  Loading model: {model_name}", file=sys.stderr, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    # Detect transformer layer list (handles LlamaModel/Qwen2Model architecture)
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        layers = model.model.layers
    elif hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        layers = model.transformer.h
    elif hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        layers = model.gpt_neox.layers
    else:
        raise ValueError(f"Cannot find transformer layers in {model_name}")

    n_layers = len(layers)
    hook_layers = get_hook_layers(n_layers)
    d_model = model.config.hidden_size

    print(f"  Architecture: {n_layers} layers, d_model={d_model}", file=sys.stderr, flush=True)
    print(f"  Hooking layers: {hook_layers}", file=sys.stderr, flush=True)

    # Storage: list of per-probe tensors, one list per layer
    captures: dict[int, list] = {li: [] for li in hook_layers}
    hooks = []

    for li in hook_layers:
        def make_hook(layer_idx: int):
            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                # Last-token hidden state → CPU float32 immediately
                captures[layer_idx].append(
                    h[:, -1, :].detach().cpu().to(torch.float32)
                )
            return hook_fn
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Run probes one at a time — simple, low memory
    print(f"\n  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(
            probe["prompt"], return_tensors="pt"
        ).to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed * 1000
            print(f"    {i+1}/{len(probes)} probes "
                  f"({elapsed:.0f}s, {rate:.0f}ms/probe)",
                  file=sys.stderr, flush=True)

    elapsed = time.time() - t0
    print(f"  Finished: {len(probes)} probes in {elapsed:.1f}s "
          f"({elapsed/len(probes)*1000:.0f}ms/probe)",
          file=sys.stderr, flush=True)

    # Remove hooks before building arrays
    for h in hooks:
        h.remove()

    # Stack per-layer hidden states
    hidden_states: dict[int, np.ndarray] = {}
    rdms: dict[int, np.ndarray] = {}

    for li in hook_layers:
        hs = torch.cat(captures[li], dim=0).numpy()   # (n_probes, d_model)
        assert hs.shape == (len(probes), d_model), (
            f"Layer {li}: expected ({len(probes)}, {d_model}), got {hs.shape}"
        )
        hidden_states[li] = hs.astype(np.float32)

        # L2-normalise → cosine similarity via matrix multiply
        norms = np.linalg.norm(hs, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        hs_norm = (hs / norms).astype(np.float32)
        rdm = hs_norm @ hs_norm.T   # (n_probes, n_probes)
        rdms[li] = rdm

        print(f"    Layer {li:2d}: RDM {rdm.shape}, "
              f"mean_sim={rdm.mean():.4f}, "
              f"off_diag_mean={rdm[~np.eye(len(probes), dtype=bool)].mean():.4f}",
              file=sys.stderr, flush=True)

    # Cleanup
    del model, tokenizer
    for li in hook_layers:
        captures[li].clear()
    gc.collect()
    try:
        if device == "mps":
            torch.mps.empty_cache()
        elif device.startswith("cuda"):
            torch.cuda.empty_cache()
    except Exception:
        pass

    return hidden_states, rdms


# ══════════════════════════════════════════════════════════════════════
# Cross-domain analysis
# ══════════════════════════════════════════════════════════════════════

class DomainStats(NamedTuple):
    layer: int
    tool_self: float        # mean within-tool (all non-control) cosine sim
    lambda_self: float      # mean within lambda_calculus control cosine sim
    tool_lambda: float      # mean between schema_binding and lambda_calculus
    tool_prose: float       # mean between tool and prose control
    schema_self: float      # mean within schema_binding probes
    recognition_delta: float  # tool_recognition_sim - notool_recognition_sim
    selectivity: float      # (tool_self - tool_prose) / (tool_self + tool_prose + ε)


def _mean_cross_sim(rdm: np.ndarray, idx_a: list[int], idx_b: list[int]) -> float:
    """Mean cosine similarity between probe sets A and B (off-diagonal if A==B)."""
    if not idx_a or not idx_b:
        return float("nan")
    sub = rdm[np.ix_(idx_a, idx_b)]
    if idx_a == idx_b:
        # Exclude diagonal (self-similarity = 1.0)
        mask = ~np.eye(len(idx_a), dtype=bool)
        vals = sub[mask]
    else:
        vals = sub.flatten()
    return float(vals.mean()) if len(vals) > 0 else float("nan")


def analyse(
    rdms: dict[int, np.ndarray],
    probes: list[dict],
) -> tuple[list[DomainStats], dict]:
    """Per-layer cross-domain analysis.

    Returns:
        stats: list of DomainStats (one per layer)
        full:  nested dict with all per-layer, per-subdomain metrics
    """
    # Build domain → probe index lists
    domain_indices: dict[str, list[int]] = {}
    subdomain_indices: dict[str, list[int]] = {}
    for i, p in enumerate(probes):
        d = p["domain"]
        sd = p["subdomain"]
        domain_indices.setdefault(d, []).append(i)
        subdomain_indices.setdefault(sd, []).append(i)

    # Convenient index sets
    all_tool_idx = (
        domain_indices.get("recognition", []) +
        domain_indices.get("selection", []) +
        domain_indices.get("schema_binding", []) +
        domain_indices.get("format", [])
    )
    lambda_idx = subdomain_indices.get("control/lambda_calculus", [])
    prose_idx  = subdomain_indices.get("control/prose", [])
    schema_idx = domain_indices.get("schema_binding", [])
    recog_tool_idx   = subdomain_indices.get("recognition/tool", [])
    recog_notool_idx = subdomain_indices.get("recognition/no_tool", [])

    stats_list: list[DomainStats] = []
    full: dict = {}

    for li, rdm in sorted(rdms.items()):
        tool_self   = _mean_cross_sim(rdm, all_tool_idx, all_tool_idx)
        lambda_self = _mean_cross_sim(rdm, lambda_idx, lambda_idx)
        tool_lambda = _mean_cross_sim(rdm, schema_idx, lambda_idx)
        tool_prose  = _mean_cross_sim(rdm, all_tool_idx, prose_idx)
        schema_self = _mean_cross_sim(rdm, schema_idx, schema_idx)

        # Recognition delta: cosine sim between tool and no-tool pairs
        recog_tool_self = _mean_cross_sim(rdm, recog_tool_idx, recog_tool_idx)
        recog_notool_self = _mean_cross_sim(rdm, recog_notool_idx, recog_notool_idx)
        recognition_delta = recog_tool_self - recog_notool_self

        selectivity = (
            (tool_self - tool_prose) / (tool_self + tool_prose + 1e-8)
            if not (np.isnan(tool_self) or np.isnan(tool_prose))
            else float("nan")
        )

        # Per-subdomain within-similarity
        per_subdomain = {}
        for sd, idx in sorted(subdomain_indices.items()):
            if len(idx) > 1:
                per_subdomain[sd] = round(_mean_cross_sim(rdm, idx, idx), 6)
            else:
                per_subdomain[sd] = None

        # All pairwise domain averages
        domain_pairs = {}
        domain_keys = sorted(domain_indices.keys())
        for di in domain_keys:
            for dj in domain_keys:
                key = f"{di}_x_{dj}"
                domain_pairs[key] = round(
                    _mean_cross_sim(rdm, domain_indices[di], domain_indices[dj]), 6
                )

        stats = DomainStats(
            layer=li,
            tool_self=round(tool_self, 6),
            lambda_self=round(lambda_self, 6),
            tool_lambda=round(tool_lambda, 6),
            tool_prose=round(tool_prose, 6),
            schema_self=round(schema_self, 6),
            recognition_delta=round(recognition_delta, 6),
            selectivity=round(selectivity, 6),
        )
        stats_list.append(stats)

        full[li] = {
            "tool_self": stats.tool_self,
            "lambda_self": stats.lambda_self,
            "tool_lambda_overlap": stats.tool_lambda,
            "tool_prose_separation": stats.tool_prose,
            "schema_self": stats.schema_self,
            "recognition_delta": stats.recognition_delta,
            "selectivity": stats.selectivity,
            "per_subdomain": per_subdomain,
            "domain_pairs": domain_pairs,
        }

    return stats_list, full


# ══════════════════════════════════════════════════════════════════════
# Interpretation
# ══════════════════════════════════════════════════════════════════════

def interpret(stats_list: list[DomainStats]) -> str:
    """Summarise findings into a human-readable hypothesis verdict."""
    if not stats_list:
        return "No data."

    # Find layer with peak Tool×Lambda overlap
    peak = max(stats_list, key=lambda s: s.tool_lambda if not np.isnan(s.tool_lambda) else -1)
    max_overlap = peak.tool_lambda
    max_selectivity = max(
        (s.selectivity for s in stats_list if not np.isnan(s.selectivity)), default=0.0
    )

    lines = ["", "  ── Hypothesis Verdict ──"]
    if max_overlap >= 0.80:
        lines.append(
            f"  STRONG SUPPORT: Tool×Lambda overlap peaks at {max_overlap:.3f} "
            f"at layer {peak.layer}."
        )
        lines.append(
            "  The tool-calling crystal SHARES circuitry with the lambda crystal."
        )
        lines.append(
            "  Tool calling IS lambda calculus applied to JSON schema (as hypothesised)."
        )
    elif max_overlap >= 0.65:
        lines.append(
            f"  PARTIAL SUPPORT: Tool×Lambda overlap peaks at {max_overlap:.3f} "
            f"at layer {peak.layer}."
        )
        lines.append(
            "  Shared features at some depths, but distinct integration at others."
        )
        lines.append(
            "  Possible: shared syntax/structure circuit, distinct semantic binding."
        )
    else:
        lines.append(
            f"  WEAK/NULL: Tool×Lambda overlap peaks at only {max_overlap:.3f} "
            f"at layer {peak.layer}."
        )
        lines.append(
            "  Tool calling and lambda calculus appear to use SEPARATE circuits."
        )
        lines.append(
            "  The hypothesis needs revision: JSON schema binding may be a distinct skill."
        )

    lines.append(f"  Max selectivity: {max_selectivity:.3f}")
    lines.append(
        "  (Selectivity = how much tool probes cluster relative to prose controls)"
    )
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
# Output
# ══════════════════════════════════════════════════════════════════════

def save_outputs(
    hidden_states: dict[int, np.ndarray],
    rdms: dict[int, np.ndarray],
    full_analysis: dict,
    probes: list[dict],
    model_name: str,
    output_dir: Path,
) -> None:
    """Save all outputs to lattice/tool_crystal/."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── rdms.npz ──────────────────────────────────────────────────────
    rdm_data = {f"layer_{li:02d}": rdm.astype(np.float32)
                for li, rdm in rdms.items()}
    rdm_path = output_dir / "rdms.npz"
    np.savez_compressed(str(rdm_path), **rdm_data)
    print(f"  💾 {rdm_path} ({rdm_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)

    # ── hidden_states.npz ─────────────────────────────────────────────
    hs_data = {f"layer_{li:02d}": hs.astype(np.float32)
               for li, hs in hidden_states.items()}
    hs_path = output_dir / "hidden_states.npz"
    np.savez_compressed(str(hs_path), **hs_data)
    print(f"  💾 {hs_path} ({hs_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)

    # ── analysis.json ─────────────────────────────────────────────────
    # Convert int keys to strings for JSON
    json_analysis = {
        "model": model_name,
        "n_probes": len(probes),
        "hook_layers": sorted(rdms.keys()),
        "per_layer": {
            str(li): v for li, v in full_analysis.items()
        },
    }
    analysis_path = output_dir / "analysis.json"
    with open(analysis_path, "w") as f:
        json.dump(json_analysis, f, indent=2)
    print(f"  💾 {analysis_path} ({analysis_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)

    # ── probes.json ───────────────────────────────────────────────────
    probes_path = output_dir / "probes.json"
    with open(probes_path, "w") as f:
        json.dump(probes, f, indent=2)
    print(f"  💾 {probes_path} ({probes_path.stat().st_size / 1024:.1f} KB)",
          file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Summary table
# ══════════════════════════════════════════════════════════════════════

def print_summary_table(stats_list: list[DomainStats]) -> None:
    """Print per-layer summary table to stderr."""
    header = (
        f"{'Layer':>6} | "
        f"{'ToolSelf':>9} | "
        f"{'SchemaSelf':>10} | "
        f"{'LambdaSelf':>10} | "
        f"{'Tool×Lambda':>11} | "
        f"{'Tool×Prose':>10} | "
        f"{'RecogΔ':>8} | "
        f"{'Selectivity':>11}"
    )
    sep = "─" * len(header)
    print("\n" + sep, file=sys.stderr, flush=True)
    print(header, file=sys.stderr, flush=True)
    print(sep, file=sys.stderr, flush=True)

    def _fmt(v: float) -> str:
        return f"{v:9.4f}" if not np.isnan(v) else "      nan"

    for s in stats_list:
        # Highlight high Tool×Lambda overlap
        flag = "◀ SHARED" if s.tool_lambda >= 0.75 else ""
        print(
            f"{s.layer:>6} | "
            f"{_fmt(s.tool_self)} | "
            f"{_fmt(s.schema_self)} | "
            f"{_fmt(s.lambda_self)} | "
            f"{_fmt(s.tool_lambda)} | "
            f"{_fmt(s.tool_prose)} | "
            f"{_fmt(s.recognition_delta)} | "
            f"{_fmt(s.selectivity)}"
            f"  {flag}",
            file=sys.stderr, flush=True,
        )

    print(sep, file=sys.stderr, flush=True)
    print(
        "  ToolSelf    = mean cosine sim within all tool-domain probes\n"
        "  SchemaSelf  = mean cosine sim within schema_binding probes\n"
        "  LambdaSelf  = mean cosine sim within lambda_calculus control probes\n"
        "  Tool×Lambda = mean cosine sim between schema_binding & lambda probes\n"
        "  Tool×Prose  = mean cosine sim between tool probes & prose controls\n"
        "  RecogΔ      = recognition/tool cluster sim minus recognition/no_tool\n"
        "  Selectivity = (ToolSelf−Tool×Prose)/(ToolSelf+Tool×Prose)",
        file=sys.stderr, flush=True,
    )


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe the tool-calling crystal and compare to lambda crystal."
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-14B",
        help="HuggingFace model ID (default: Qwen/Qwen3-14B)",
    )
    parser.add_argument(
        "--device",
        default="mps",
        choices=["mps", "cuda", "cpu"],
        help="Inference device (default: mps)",
    )
    parser.add_argument(
        "--output-dir",
        default="lattice/tool_crystal",
        help="Output directory (default: lattice/tool_crystal)",
    )
    args = parser.parse_args()

    t_start = time.time()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Tool-Calling Crystal Probe", file=sys.stderr, flush=True)
    print(f"  Model:  {args.model}", file=sys.stderr, flush=True)
    print(f"  Device: {args.device}", file=sys.stderr, flush=True)
    print(f"  Output: {args.output_dir}/", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    # ── 1. Build probe corpus ─────────────────────────────────────────
    print("\n1. Building probe corpus...", file=sys.stderr, flush=True)
    probes = _build_probes()

    # Domain breakdown
    domain_counts: dict[str, int] = {}
    subdomain_counts: dict[str, int] = {}
    for p in probes:
        domain_counts[p["domain"]] = domain_counts.get(p["domain"], 0) + 1
        subdomain_counts[p["subdomain"]] = subdomain_counts.get(p["subdomain"], 0) + 1

    print(f"  Total probes: {len(probes)}", file=sys.stderr, flush=True)
    for domain, count in sorted(domain_counts.items()):
        print(f"    {domain:20s}: {count}", file=sys.stderr, flush=True)

    # ── 2. Load model & extract activations ───────────────────────────
    print("\n2. Extracting activations...", file=sys.stderr, flush=True)
    hidden_states, rdms = run_extraction(args.model, probes, args.device)

    # ── 3. Cross-domain analysis ──────────────────────────────────────
    print("\n3. Cross-domain analysis...", file=sys.stderr, flush=True)
    stats_list, full_analysis = analyse(rdms, probes)

    # ── 4. Print summary table ────────────────────────────────────────
    print_summary_table(stats_list)

    # ── 5. Print interpretation ───────────────────────────────────────
    verdict = interpret(stats_list)
    print(verdict, file=sys.stderr, flush=True)

    # ── 6. Save outputs ───────────────────────────────────────────────
    print("\n4. Saving outputs...", file=sys.stderr, flush=True)
    output_dir = Path(args.output_dir)
    save_outputs(hidden_states, rdms, full_analysis, probes, args.model, output_dir)

    elapsed = time.time() - t_start
    print(f"\n{'='*72}", file=sys.stderr, flush=True)
    print(f"  Done in {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"  Probes: {len(probes)}", file=sys.stderr, flush=True)
    print(f"  Layers: {sorted(rdms.keys())}", file=sys.stderr, flush=True)
    print(f"  Output: {output_dir}/", file=sys.stderr, flush=True)
    print(f"{'='*72}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
