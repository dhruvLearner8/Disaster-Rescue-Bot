"""Check generated questions: every label must come from the allowed lists.

Usage:
    uv run python scripts/check_questions.py data/synthetic/questions_v2_sample.jsonl
"""

import json
import sys
from collections import Counter

from labels import ALLOWED

path = sys.argv[1]
rows = [json.loads(line) for line in open(path) if line.strip()]
problems = 0

for i, row in enumerate(rows, 1):
    for field, allowed in ALLOWED.items():
        if row.get(field) not in allowed:
            print(f"line {i}: {field}={row.get(field)!r} is not an allowed label")
            problems += 1
    if not row.get("question", "").strip():
        print(f"line {i}: empty question")
        problems += 1

print(f"\n{len(rows)} questions, {problems} problems\n")

# How the questions are spread across each label
for field in ALLOWED:
    counts = Counter(row.get(field) for row in rows)
    print(f"{field:13} " + ", ".join(f"{k} {v}" for k, v in counts.most_common()))
