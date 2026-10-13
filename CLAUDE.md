# Offline Disaster Assistant

A small LLM (Llama-3.2-1B-Instruct) fine-tuned to guide people through floods,
running fully offline on an Android phone. Portfolio/learning project. Scope: floods,
US + Canada (the user lives in Vancouver and will test it there).

## How to work with this user

- **They want to learn while building.** Go one step at a time, explain the why
  before doing things, let them make the decisions, and run a small test before
  anything big. Don't race through whole phases.
- **Use uv only:** `uv add`, `uv run python ...`. Never pip.
- Commit when they ask. They're happy for Claude to run the git commands.
- Ask before anything that spends API money, and give a cost estimate.
- They push for speed or shortcuts sometimes. Give an honest recommendation once,
  then respect their call, except on the API terms issue below.

## Pipeline and status

1. ✅ **Setup.** llama.cpp built with Metal in `third_party/llama.cpp` (pinned b11240).
   Base model in `models/hf/` and as GGUF (f16 / Q8_0 / Q4_K_M) in `models/gguf/`.
   `models/` and `third_party/` are git-ignored; rebuild with `scripts/build_base_models.sh`.
2. ✅ **Baseline eval** (`eval/run_eval.py`, 20 seed scenarios in `eval/scenarios/`):
   Q8 ≈ F16 at 2× speed, Q4 loses ~11 pts. The base model gives dangerous advice
   (e.g. "wait for rescue" in a sinking car). The scoring is keyword-based and crude.
3. ✅ **Questions: 501 synthetic user questions** in `data/synthetic/questions_v7.jsonl`
   (prompt v7, claude-sonnet-5-5, seed 42, cost $0.56). The user is satisfied with
   them; they declined a top-up for rare scenarios.
4. ⛔ **Answers: blocked, decision pending.** See below.
5. ⬜ Test/train split (no data leakage), fine-tune with LoRA (MLX on the Mac, or
   Colab), re-run the eval, quantize, put it on Android.

## ⚠️ The API terms issue (important)

The plan is to train Llama on a big model's answers (distillation). When we tried
Claude for answers (`scripts/generate_answers.py`, prompt `answer_gen_v1.md`), **every
request was refused** with `stop_reason=refusal`, `category=reasoning_extraction`:
"violates Anthropic's Terms of Service restrictions on reverse engineering or
duplicating model outputs."

- The OpenAI Services Agreement and the Gemini API terms also restrict using
  outputs to develop competing models. Our project doesn't fit OpenAI's exceptions.
- The user asked to "trick" the providers. **Claude declined and must keep
  declining**: no renaming fields, rephrasing or anything else to slip past the
  classifier or the terms.
- The same terms also apply to the 501 questions already generated with Claude.
  The user has been told this.
- **Recommended next step: run an open-weight teacher model locally**, e.g.
  gpt-oss-20b (Apache 2.0; check the license on the model card) via the
  llama.cpp already built, then run the same 10-question answer test. Alternative:
  answers written from official sources (PreparedBC etc.) with the user reviewing.
- The user had not decided yet when the session ended.

The 10-question answer test set (line numbers in questions_v7.jsonl, chosen to cover
critical, wrong-belief, conditional, broken-English and low-urgency cases):
`9 31 6 127 27 139 67 174 350 54`

## Design decisions and lessons so far

- **Questions come from AI, answers must be trustworthy.** A wrong question is
  harmless; a wrong answer can kill. The user later chose to let a big model
  answer from its own knowledge with no sources (their decision, risk explained).
- **Answer format** (answer_gen_v1): a `reasoning` field first (logic, never shown
  to the user), then a short answer: the most important action first, 2–5 steps each
  with a brief "why", 911 only (no other phone numbers), under 80 words if critical.
- **Code decides distributions, the model writes.** Models ignore "how many of each"
  instructions. The script picks scenario and target length at random per call.
- **Use off-topic examples in prompts** (v6 copied "basment" 9×; v7 fixed it).
- **Keep the changelog out of the prompt file**: the whole file is sent to the
  model. History goes in `data/prompts/CHANGELOG.md`.
- **Change one thing per experiment** (v4 changed prompt and model together).
- **Urgency labels from the generator are unreliable** (e.g. a gas smell plus a
  cigarette labeled "high"). Plan: a separate labeling/review pass later.
- Known data quirks: "tonite" ×33, "water went down" opens 25 questions, messages
  are about 2× longer than the target, rooftop/in the water/small patch of land are
  rare (21/15/3), 1 exact duplicate.
- The test set and the training set must stay separate.

## Files

- `scripts/labels.py`: shared label lists (phase, urgency, where, who, complication, state)
- `scripts/generate_questions.py`: `--calls --n --seed --prompt v7 --model`
- `scripts/check_questions.py <file>`: checks labels and prints the spread
- `scripts/generate_answers.py`: `--sample N --seed` or `--lines ...`, `--prompt --model`
- `data/prompts/`: question_gen_v1–v7, answer_gen_v1, CHANGELOG.md
- `data/raw/preparedbc/`: PreparedBC flood guide (PDF + extracted text). Only about
  1 in 5 test questions is fully answered by it; gas, pets and medicine aren't covered.
- `.env` holds `ANTHROPIC_API_KEY` (workspace-scoped key) and is git-ignored. The
  user also has OpenAI and Gemini keys.

## Models (Anthropic API)

claude-sonnet-5-5 ($2/$10 per 1M tokens) for generation. claude-opus-5-5 ($4/$20).
Structured outputs via `output_config.format` (json_schema); `fallbacks="default"`
with beta `server-side-fallback-2026-07-01`.
