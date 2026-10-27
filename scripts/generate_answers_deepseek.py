"""Generate an answer (with reasoning) for each multi-disaster question using DeepSeek.

Resumable (skips questions already answered), parallel, with a spending cap. Each row gets
automatic flags (other phone numbers, too long) so problems are easy to find later.
Needs DEEPSEEK_API_KEY in .env.

    uv run python scripts/generate_answers_deepseek.py --prompt multi_v1 --sample 25 --seed 1 --out data/synthetic/multi_pilot/answers_multi_v1.jsonl
    uv run python scripts/generate_answers_deepseek.py --prompt multi_v1 --dry-run --sample 1
"""

import argparse
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import httpx
from dotenv import load_dotenv

URL = "https://api.deepseek.com/chat/completions"
PRICE = (0.28, 0.42)  # USD per 1M tokens (input, output). Estimate: check your DeepSeek dashboard.
PHONE = re.compile(r"\b(?:\d{3}[-. ]\d{3,4}[-. ]?\d{0,4}|1-8\d\d\S*|211|311|811|988|112|999)\b")


def normalize(answer: str) -> str:
    """Put inline numbered steps ("1. ... 2. ...") on their own lines."""
    return re.sub(r"(?<=[.!?:])[ \t]+(?=[1-5]\.\s)", "\n", answer.strip())


def flags(row: dict, answer: str) -> list[str]:
    out = []
    if PHONE.search(answer):
        out.append("other_phone_number")
    limit = 80 if row["urgency"] == "critical" else 120
    if len(answer.split()) > limit:
        out.append("too_long")
    if "911" not in answer and row["urgency"] in ("critical", "high"):
        out.append("no_911")
    return out


def ask(key: str, model: str, prompt: str) -> tuple[dict, int, int]:
    for attempt in range(5):
        try:
            r = httpx.post(URL, timeout=180, headers={"Authorization": f"Bearer {key}"},
                           json={"model": model, "temperature": 0.7, "max_tokens": 1500,
                                 "response_format": {"type": "json_object"},
                                 "messages": [{"role": "user", "content": prompt}]})
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** attempt); continue
            r.raise_for_status()
            body = r.json()
            data = json.loads(body["choices"][0]["message"]["content"])
            if not isinstance(data.get("reasoning"), str) or not isinstance(data.get("answer"), str):
                raise ValueError("bad shape")
            return data, body["usage"]["prompt_tokens"], body["usage"]["completion_tokens"]
        except (httpx.HTTPError, ValueError, KeyError, json.JSONDecodeError):
            time.sleep(2 ** attempt)
    raise RuntimeError("failed after 5 tries")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="e.g. multi_v1 (data/prompts/answer_gen_multi_v1.md)")
    ap.add_argument("--input", default="data/synthetic/multi/questions_multi_v3_clean.jsonl")
    ap.add_argument("--out", default=None)
    ap.add_argument("--model", default="deepseek-chat")
    ap.add_argument("--sample", type=int, default=None, help="answer this many random questions (pilot)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--max-usd", type=float, default=3.0, help="hard spending cap")
    ap.add_argument("--dry-run", action="store_true", help="print the first prompt, no API call")
    args = ap.parse_args()

    template = Path(f"data/prompts/answer_gen_{args.prompt}.md").read_text()
    out_file = Path(args.out or f"data/synthetic/multi/answers_{args.prompt}.jsonl")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    rows = [{**json.loads(l), "q_id": i} for i, l in enumerate(Path(args.input).open(), 1)]
    if args.sample:
        rows = random.Random(args.seed).sample(rows, args.sample)
    done = {json.loads(l)["q_id"] for l in out_file.open()} if out_file.exists() else set()
    todo = [r for r in rows if r["q_id"] not in done]
    print(f"{len(todo)} to answer, {len(done)} already done")

    def prompt_for(r: dict) -> str:
        return template.format(question=r["question"], disaster=r["disaster"])

    if args.dry_run:
        print(prompt_for(todo[0])); return

    load_dotenv()
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is not in .env")

    cost, fails, n = 0.0, 0, 0
    with out_file.open("a") as out, ThreadPoolExecutor(args.workers) as pool:
        futs = {pool.submit(ask, key, args.model, prompt_for(r)): r for r in todo}
        for f in as_completed(futs):
            r = futs[f]
            try:
                data, tin, tout = f.result()
            except RuntimeError as e:
                fails += 1
                print(f"q_id {r['q_id']}: {e}")
                if fails >= 5:
                    pool.shutdown(cancel_futures=True); break
                continue
            cost += (tin * PRICE[0] + tout * PRICE[1]) / 1e6
            out.write(json.dumps({**r, "reasoning": data["reasoning"].strip(), "answer": normalize(data["answer"]),
                                  "flags": flags(r, normalize(data["answer"])), "answer_model": args.model,
                                  "answer_prompt": f"answer_gen_{args.prompt}.md"}) + "\n")
            out.flush(); n += 1
            if n % 100 == 0:
                print(f"{n} done, about ${cost:.3f}")
            if cost >= args.max_usd:
                print("spending cap reached"); pool.shutdown(cancel_futures=True); break
    print(f"\nwrote {n} answers to {out_file}, cost about ${cost:.4f} (estimate), failures={fails}")


if __name__ == "__main__":
    main()
