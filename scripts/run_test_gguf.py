"""Run data/splits/test.jsonl through one GGUF model and save the answers.

Starts llama-server, sends each test question with the same system prompt as
training (greedy decoding), and writes one JSON line per question.

    uv run python scripts/run_test_gguf.py models/gguf/llama32-1b-base-f16.gguf
    -> eval/results/test49/llama32-1b-base-f16.jsonl
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eval"))
from run_eval import SYSTEM_PROMPT, LLAMA_SERVER  # noqa: E402

TEST = ROOT / "data/splits/test.jsonl"
OUT_DIR = ROOT / "eval/results/test49"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gguf")
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--max-tokens", type=int, default=512)
    args = ap.parse_args()

    gguf = Path(args.gguf)
    out = OUT_DIR / f"{gguf.stem}.jsonl"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in TEST.read_text().splitlines() if line.strip()]

    server = subprocess.Popen(
        [str(LLAMA_SERVER), "-m", str(gguf), "--port", str(args.port), "-c", "4096"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{args.port}"
    try:
        for _ in range(120):
            try:
                if httpx.get(f"{base}/health", timeout=2).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(1)
        else:
            raise RuntimeError("llama-server did not start")

        t0 = time.time()
        with out.open("w") as f:
            for i, r in enumerate(rows, 1):
                question = r["messages"][1]["content"]
                resp = httpx.post(
                    f"{base}/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": question},
                        ],
                        "temperature": 0,
                        "max_tokens": args.max_tokens,
                    },
                    timeout=300,
                ).json()
                choice = resp["choices"][0]
                f.write(json.dumps({
                    "idx": i,
                    "question": question,
                    "urgency": r["labels"]["urgency"],
                    "phase": r["labels"]["phase"],
                    "reference": r["messages"][2]["content"],
                    "answer": choice["message"]["content"],
                    "finish_reason": choice.get("finish_reason"),
                    "model": gguf.stem,
                }) + "\n")
                print(f"{i}/{len(rows)}  {time.time() - t0:.0f}s", flush=True)
        print("wrote", out)
    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    main()
