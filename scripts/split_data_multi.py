"""Build train/test files for the multi-disaster model.

Test rows are chosen BEFORE any training and never trained on: about 10% of each new disaster
plus the 49 flood test questions. Flood train rows (452) are kept so the model keeps its flood skill.
All rows use the same general system prompt (not "flood or storm"), because the model must work for every disaster.

    uv run python scripts/split_data_multi.py
Writes data/splits_multi/{train.jsonl, test_full.jsonl, test_eval.jsonl}
  train.jsonl      chat format only ({"messages": [...]}), answer only (no reasoning)
  test_full.jsonl  all held-out rows with labels and the reference answer
  test_eval.jsonl  a smaller, balanced sample of test_full (for reading answers by hand)
"""

import json
import random
import re
from collections import defaultdict
from pathlib import Path

SYSTEM_PROMPT = (
    "You are an offline emergency assistant helping someone during a disaster. "
    "Give clear, short, numbered safety steps. Put the most urgent action first. "
    "If life is at risk, tell them to contact emergency services (911) when possible. "
    "Never guess: if you are not sure, say so."
)
SRC = Path("data/synthetic/multi/answers_multi_v2.jsonl")
OUT = Path("data/splits_multi")
OTHER_NUMBER = re.compile(r"\b(?:211|311|411|511|811|988)\b")  # real "other phone number" rows (not "100-120 per minute")
TEST_SHARE, EVAL_PER_DISASTER = 0.10, 6


def chat(question: str, answer: str) -> dict:
    return {"messages": [{"role": "system", "content": SYSTEM_PROMPT},
                         {"role": "user", "content": question},
                         {"role": "assistant", "content": answer}]}


def main() -> None:
    rng = random.Random(42)
    rows = [json.loads(l) for l in SRC.open()]
    kept = [r for r in rows if not OTHER_NUMBER.search(r["answer"])]
    print(f"{len(rows)} answers, dropped {len(rows) - len(kept)} that name another phone number (211/311...)")

    by_disaster: dict[str, list[dict]] = defaultdict(list)
    for r in kept:
        by_disaster[r["disaster"]].append(r)

    train, test = [], []
    for d, rs in sorted(by_disaster.items()):
        rng.shuffle(rs)
        n_test = max(5, round(TEST_SHARE * len(rs)))
        test += rs[:n_test]
        train += rs[n_test:]

    # balanced sample for reading: per disaster up to 3 critical, 2 high, then anything
    eval_rows = []
    for d, rs in sorted(by_disaster.items()):
        pool = [r for r in test if r["disaster"] == d]
        pick = []
        for urgency, k in (("critical", 3), ("high", 2)):
            pick += [r for r in pool if r["urgency"] == urgency][:k]
        pick += [r for r in pool if r not in pick][:EVAL_PER_DISASTER - len(pick)]
        eval_rows += pick[:EVAL_PER_DISASTER]

    # flood rows from the earlier flood split (452 train, 49 test)
    flood_train = [json.loads(l) for l in open("data/splits/train.jsonl")]
    flood_test = [json.loads(l) for l in open("data/splits/test.jsonl")]
    flood_train_chat = [chat(m["messages"][1]["content"], m["messages"][2]["content"]) for m in flood_train]

    def test_row(r: dict) -> dict:
        return {**chat(r["question"], r["answer"]),
                "labels": {"disaster": r["disaster"], "phase": r["phase"], "urgency": r["urgency"]}}

    def flood_test_row(m: dict) -> dict:
        return {**chat(m["messages"][1]["content"], m["messages"][2]["content"]),
                "labels": {"disaster": "flood", "phase": m["labels"]["phase"], "urgency": m["labels"]["urgency"]}}

    train_all = [chat(r["question"], r["answer"]) for r in train] + flood_train_chat
    rng.shuffle(train_all)
    test_full = [test_row(r) for r in test] + [flood_test_row(m) for m in flood_test]
    test_eval = [test_row(r) for r in eval_rows] + [flood_test_row(m) for m in flood_test]

    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("train", train_all), ("test_full", test_full), ("test_eval", test_eval)):
        with (OUT / f"{name}.jsonl").open("w") as f:
            f.writelines(json.dumps(x) + "\n" for x in data)
        print(f"{name:10} {len(data):5} rows")

    q_train = {x["messages"][1]["content"].strip().lower() for x in train_all}
    q_test = {x["messages"][1]["content"].strip().lower() for x in test_full}
    print("question overlap between train and test:", len(q_train & q_test))


if __name__ == "__main__":
    main()
