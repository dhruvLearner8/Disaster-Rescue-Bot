"""Check generated questions: every label must come from the allowed lists.

Usage:
    uv run python scripts/check_questions.py data/synthetic/questions_v2_sample.jsonl
"""

import json
import sys
from collections import Counter

# Must match the lists in data/prompts/question_gen_v2.md
ALLOWED = {
    "phase": {"before", "during", "after"},
    "urgency": {"critical", "high", "medium", "low"},
    "where": {"car", "house", "apartment", "basement", "rooftop", "small patch of land",
              "in the water", "campsite", "walking outside", "workplace", "school"},
    "who": {"alone", "kids", "baby", "elderly parent", "pet", "someone injured",
            "someone who can't swim", "strangers"},
    "complication": {"none", "power out", "phone battery low", "no car", "night time",
                     "injury", "medical condition", "doesn't speak English well"},
    "state": {"calm", "worried", "panicking", "shock"},
}

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
