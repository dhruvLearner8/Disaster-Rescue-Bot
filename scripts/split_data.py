"""Split the answers file into train/test sets, ready for LoRA fine-tuning.

Why split here, once: the test set must never be seen in training. Doing it in one
place with a fixed seed means every re-run gives the same split.

Train rows are chat-format ({"messages": [...]}) and use the same system prompt as
eval/run_eval.py, so the model is trained on the same input it sees at eval time.
Test rows keep the labels and the reference answer.

    uv run python scripts/split_data.py                  # train on the answer only
    uv run python scripts/split_data.py --with-reasoning # answer preceded by reasoning
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eval"))
from run_eval import SYSTEM_PROMPT  # noqa: E402

SRC = ROOT / "data/synthetic/flood_answers_500.jsonl"
OUT = ROOT / "data/splits"


def to_messages(row: dict, with_reasoning: bool) -> dict:
    reply = row["answer"]
    if with_reasoning:
        reply = f"Reasoning: {row['reasoning']}\n\n{reply}"
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": row["question"]},
            {"role": "assistant", "content": reply},
        ]
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-size", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--with-reasoning", action="store_true")
    args = ap.parse_args()

    rows = [json.loads(line) for line in SRC.read_text().splitlines() if line.strip()]

    # Rows with identical question text go in the same group, so a duplicate can't
    # end up in train and test at once.
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["question"].strip().lower()].append(r)

    # Stratify by urgency so test has the same critical/high/medium/low mix as train.
    by_urgency: dict[str, list[list[dict]]] = defaultdict(list)
    for g in groups.values():
        by_urgency[g[0]["urgency"]].append(g)

    rng = random.Random(args.seed)
    total = len(groups)
    test_groups: list[list[dict]] = []
    train_groups: list[list[dict]] = []
    for urgency in sorted(by_urgency):
        gs = by_urgency[urgency]
        rng.shuffle(gs)
        n_test = max(1, round(args.test_size * len(gs) / total))
        test_groups += gs[:n_test]
        train_groups += gs[n_test:]

    test = [r for g in test_groups for r in g]
    train = [r for g in train_groups for r in g]
    rng.shuffle(train)
    rng.shuffle(test)

    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "train.jsonl").open("w") as f:
        for r in train:
            f.write(json.dumps(to_messages(r, args.with_reasoning)) + "\n")
    with (OUT / "test.jsonl").open("w") as f:
        for r in test:
            f.write(json.dumps({**to_messages(r, False), "labels": {
                k: r[k] for k in ("phase", "where", "who", "complication", "state", "urgency")
            }}) + "\n")

    print(f"train {len(train)}  test {len(test)}  (seed {args.seed}, "
          f"{'with' if args.with_reasoning else 'no'} reasoning)")
    for name, part in (("train", train), ("test", test)):
        counts = {u: sum(r["urgency"] == u for r in part) for u in sorted(by_urgency)}
        print(f"  {name} urgency: {counts}")


if __name__ == "__main__":
    main()
