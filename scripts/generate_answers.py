"""Generate an answer (with reasoning) for each question using Claude.

Usage:
    # 10 random questions
    uv run python scripts/generate_answers.py --sample 10 --seed 1
    # specific questions by line number in the questions file
    uv run python scripts/generate_answers.py --lines 4 17 230
"""

import argparse
import json
import random
from pathlib import Path

import anthropic
from dotenv import load_dotenv

QUESTIONS_FILE = Path("data/synthetic/questions_v7.jsonl")

# USD per 1M tokens (input, output)
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
}

# The API guarantees the reply matches this shape. Reasoning comes first,
# so the model works out the logic before it writes the answer.
SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string"},
        "answer": {"type": "string"},
    },
    "required": ["reasoning", "answer"],
    "additionalProperties": False,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", type=int, help="answer this many random questions")
    group.add_argument("--lines", type=int, nargs="+", help="answer these line numbers (1-based)")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--prompt", default="v1", help="answer prompt version, e.g. v1")
    parser.add_argument("--model", default="claude-sonnet-5-5", choices=sorted(PRICES))
    args = parser.parse_args()

    prompt_file = Path(f"data/prompts/answer_gen_{args.prompt}.md")
    out_file = Path(f"data/synthetic/answers_{args.prompt}.jsonl")
    price_in, price_out = PRICES[args.model]

    rows = [json.loads(line) for line in QUESTIONS_FILE.open()]
    if args.lines:
        picked = [(n, rows[n - 1]) for n in args.lines]
    else:
        numbered = list(enumerate(rows, 1))
        picked = random.Random(args.seed).sample(numbered, args.sample)

    load_dotenv()
    client = anthropic.Anthropic()
    template = prompt_file.read_text()

    cost = 0.0
    with out_file.open("a") as out:
        for i, (line_no, row) in enumerate(picked, 1):
            response = client.beta.messages.create(
                model=args.model,
                max_tokens=8000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                output_config={
                    "effort": "high",  # safety advice: worth the extra thinking
                    "format": {"type": "json_schema", "schema": SCHEMA},
                },
                messages=[{"role": "user", "content": template.format(question=row["question"])}],
            )
            cost += (response.usage.input_tokens * price_in
                     + response.usage.output_tokens * price_out) / 1_000_000

            if response.stop_reason != "end_turn":
                print(f"{i}: line {line_no} skipped, stop_reason={response.stop_reason}")
                continue

            text = next(b.text for b in response.content if b.type == "text")
            result = json.loads(text)
            out.write(json.dumps({
                **row, "question_line": line_no,
                "reasoning": result["reasoning"], "answer": result["answer"],
                "answer_model": response.model, "answer_prompt": prompt_file.name,
            }) + "\n")
            print(f"{i}/{len(picked)}: line {line_no} answered")

    print(f"\nwrote answers to {out_file}, cost about ${cost:.3f}")


if __name__ == "__main__":
    main()
