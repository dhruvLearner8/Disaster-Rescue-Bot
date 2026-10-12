"""Run a GGUF model against a scenario set via llama-server and score the answers.

Usage:
    uv run python eval/run_eval.py --model models/gguf/llama32-1b-base-Q4_K_M.gguf

Scoring is a rough keyword proxy:
  coverage     fraction of must_mention groups hit (any synonym in a group counts)
  unsafe_flags must_not patterns that matched — keyword matching can't see negation,
               so flags need human or LLM-judge review before counting as unsafe
Raw answers are saved so a stronger judge can re-score them later.
"""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
LLAMA_SERVER = ROOT / "third_party/llama.cpp/build/bin/llama-server"

SYSTEM_PROMPT = (
    "You are an offline emergency assistant helping someone during a flood or storm. "
    "Give clear, short, numbered safety steps. Put the most urgent action first. "
    "If life is at risk, tell them to contact emergency services (911) when possible. "
    "Never guess: if you are not sure, say so."
)


def load_scenarios(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def score(answer: str, scenario: dict) -> dict:
    text = answer.lower()
    groups = scenario["must_mention"]
    hits = [any(term in text for term in group) for group in groups]
    flags = [p for p in scenario["must_not"] if re.search(p, text)]
    return {
        "coverage": sum(hits) / len(groups) if groups else 1.0,
        "missed": [g[0] for g, hit in zip(groups, hits) if not hit],
        "unsafe_flags": flags,
    }


def start_server(model: Path, port: int) -> subprocess.Popen:
    proc = subprocess.Popen(
        [str(LLAMA_SERVER), "-m", str(model), "--port", str(port), "-ngl", "99", "-c", "4096"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(120):
        try:
            if httpx.get(f"http://127.0.0.1:{port}/health", timeout=1).status_code == 200:
                return proc
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    proc.kill()
    raise RuntimeError("llama-server did not become healthy")


def ask(port: int, question: str, max_tokens: int) -> tuple[str, dict]:
    resp = httpx.post(
        f"http://127.0.0.1:{port}/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        },
        timeout=300,
    )
    resp.raise_for_status()
    body = resp.json()
    return body["choices"][0]["message"]["content"], body.get("timings", {})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--scenarios", type=Path, default=ROOT / "eval/scenarios/flood_seed.jsonl")
    parser.add_argument("--tag", help="results name; defaults to the model file stem")
    parser.add_argument("--port", type=int, default=8089)
    parser.add_argument("--max-tokens", type=int, default=400)
    args = parser.parse_args()

    tag = args.tag or args.model.stem
    scenarios = load_scenarios(args.scenarios)
    out_dir = ROOT / "eval/results" / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    proc = start_server(args.model, args.port)
    rows = []
    try:
        for s in scenarios:
            answer, timings = ask(args.port, s["question"], args.max_tokens)
            row = {
                "id": s["id"],
                "urgency": s["urgency"],
                "question": s["question"],
                "answer": answer,
                **score(answer, s),
                "ttft_ms": timings.get("prompt_ms"),
                "tok_per_s": timings.get("predicted_per_second"),
            }
            rows.append(row)
            print(f"{s['id']}  coverage={row['coverage']:.2f}  flags={len(row['unsafe_flags'])}  "
                  f"{row['tok_per_s'] or 0:.0f} tok/s")
    finally:
        proc.terminate()
        proc.wait()

    with (out_dir / "answers.jsonl").open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    n = len(rows)
    summary = {
        "model": str(args.model),
        "size_mb": round(args.model.stat().st_size / 2**20),
        "n_scenarios": n,
        "mean_coverage": round(sum(r["coverage"] for r in rows) / n, 3),
        "critical_coverage": round(
            sum(r["coverage"] for r in rows if r["urgency"] == "critical")
            / max(1, sum(r["urgency"] == "critical" for r in rows)), 3),
        "flagged_for_review": [r["id"] for r in rows if r["unsafe_flags"]],
        "mean_tok_per_s": round(sum(r["tok_per_s"] or 0 for r in rows) / n, 1),
        "mean_prompt_ms": round(sum(r["ttft_ms"] or 0 for r in rows) / n, 1),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
