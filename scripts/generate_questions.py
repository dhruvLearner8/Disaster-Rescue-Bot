"""Generate synthetic user questions with Claude, one random scenario per API call.

Each call picks a random scenario (phase, where, who, complication, state), fills it
into the prompt, and asks for --n messages for that scenario. Results are appended
to the output file, so you can run it several times and the data adds up.

Usage:
    uv run python scripts/generate_questions.py --calls 5 --prompt v4 --model claude-sonnet-5-5
"""

import argparse
import json
import os
import random
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from labels import ALLOWED

# USD per 1M tokens (input, output)
PRICES = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
}

# Target message lengths and how often each is picked
LENGTHS = {"2-6 words": 0.35, "7-15 words": 0.45, "16-30 words": 0.20}

# Places that only make sense while the flood is happening
DURING_ONLY = {"in the water", "rooftop", "small patch of land"}
# People that don't fit once the water has gone down
NOT_AFTER = {"someone who can't swim"}

# The API guarantees the reply matches this shape
SCHEMA = {
    "type": "object",
    "properties": {
        "messages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "urgency": {"type": "string", "enum": sorted(ALLOWED["urgency"])},
                    "question": {"type": "string"},
                },
                "required": ["urgency", "question"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["messages"],
    "additionalProperties": False,
}


def pick_scenario(rng: random.Random) -> dict:
    phase = rng.choice(sorted(ALLOWED["phase"]))
    places = [w for w in sorted(ALLOWED["where"]) if phase == "during" or w not in DURING_ONLY]
    people = [p for p in sorted(ALLOWED["who"]) if phase != "after" or p not in NOT_AFTER]
    return {
        "phase": phase,
        "where": rng.choice(places),
        "who": rng.choice(people),
        "complication": rng.choice(sorted(ALLOWED["complication"])),
        "state": rng.choice(sorted(ALLOWED["state"])),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calls", type=int, default=5, help="number of API calls")
    parser.add_argument("--n", type=int, default=3, help="messages per call")
    parser.add_argument("--seed", type=int, default=None, help="for repeatable scenarios")
    parser.add_argument("--prompt", default="v4", help="prompt version, e.g. v4")
    parser.add_argument("--model", default="claude-sonnet-5-5", choices=sorted(PRICES))
    args = parser.parse_args()

    prompt_file = Path(f"data/prompts/question_gen_{args.prompt}.md")
    out_file = Path(f"data/synthetic/questions_{args.prompt}.jsonl")
    price_in, price_out = PRICES[args.model]

    load_dotenv()  # reads ANTHROPIC_API_KEY (and optional ANTHROPIC_WORKSPACE_ID) from .env
    # Keys that aren't scoped to a workspace must name one on every request
    workspace = os.environ.get("ANTHROPIC_WORKSPACE_ID")
    headers = {"anthropic-workspace-id": workspace} if workspace else None
    client = anthropic.Anthropic(default_headers=headers)
    rng = random.Random(args.seed)
    template = prompt_file.read_text()

    written = 0
    cost = 0.0
    with out_file.open("a") as out:
        for i in range(1, args.calls + 1):
            scenario = pick_scenario(rng)
            lengths = rng.choices(list(LENGTHS), weights=list(LENGTHS.values()), k=args.n)
            length_lines = "\n".join(f"{j}. {length}" for j, length in enumerate(lengths, 1))
            # Older prompts have no {lengths} slot; format() ignores unused values
            prompt = template.format(n=args.n, lengths=length_lines, **scenario)

            response = client.beta.messages.create(
                model=args.model,
                max_tokens=4000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",  # if Opus declines, the API retries on another model
                output_config={
                    "effort": "low",  # short creative task, deep thinking isn't needed
                    "format": {"type": "json_schema", "schema": SCHEMA},
                },
                messages=[{"role": "user", "content": prompt}],
            )
            cost += (response.usage.input_tokens * price_in
                     + response.usage.output_tokens * price_out) / 1_000_000

            if response.stop_reason != "end_turn":
                print(f"call {i}: skipped, stop_reason={response.stop_reason}")
                continue

            text = next(b.text for b in response.content if b.type == "text")
            for j, msg in enumerate(json.loads(text)["messages"]):
                row = {**scenario, "urgency": msg["urgency"], "question": msg["question"],
                       "target_length": lengths[j] if j < len(lengths) else None,
                       "model": response.model, "prompt": prompt_file.name}
                out.write(json.dumps(row) + "\n")
                written += 1

            print(f"call {i}/{args.calls}: {scenario['phase']} / {scenario['where']} / "
                  f"{scenario['who']} -> {len(json.loads(text)['messages'])} messages")

    print(f"\nwrote {written} questions to {out_file}, cost about ${cost:.3f}")


if __name__ == "__main__":
    main()
