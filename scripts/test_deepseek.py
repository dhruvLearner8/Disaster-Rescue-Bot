"""Check that DEEPSEEK_API_KEY in .env works: one tiny call, prints the reply and the token use."""
import os

import httpx
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("DEEPSEEK_API_KEY")
if not key:
    raise SystemExit("DEEPSEEK_API_KEY is not in .env")

r = httpx.post(
    "https://api.deepseek.com/chat/completions", timeout=60,
    headers={"Authorization": f"Bearer {key.strip()}"},
    json={"model": "deepseek-chat", "max_tokens": 20,
          "messages": [{"role": "user", "content": "Reply with the single word: ok"}]},
)
print("status:", r.status_code)
if r.status_code != 200:
    raise SystemExit(r.text[:300])
body = r.json()
print("reply:", body["choices"][0]["message"]["content"], "| model:", body["model"], "| tokens:", body["usage"])
