# Offline Disaster Assistant

A small language model that gives short, numbered safety steps during a disaster and runs
**entirely on a phone, with no internet**. Llama-3.2 (1B and 3B) is fine-tuned with LoRA,
compressed with GGUF quantization, and runs through llama.cpp inside an iOS app.

> **Research prototype, not a safety tool.** The models still give dangerous advice in about
> 1 in 5 answers on our hardest tests (see [Results](#results)). Do not use it in a real emergency.
> If you are in danger, call your local emergency number (911 in the US and Canada).

## Why this is hard

A base Llama-3.2-1B gives confident, long, generic advice. Asked about a flooded basement it
writes a cleanup guide, and it sends people to the breaker panel while they stand in water.
Fine-tuning fixes the format (short, action first, a reason per step) and most of the
behaviour, but not all of it. The remaining mistakes are the point of this project.

## What was built

| Stage | What | Status |
|---|---|---|
| Flood model | 501 synthetic flood questions + answers, SFT, then DPO on unsafe/safe pairs | done |
| Quantization | f16 / Q8_0 / Q5_K_M / Q4_K_M / Q3_K_M GGUF, tested on 49 questions | done |
| Multi-disaster model | 22 more disasters (earthquake, wildfire, tornado, tsunami, ...), 5,903 questions + answers, SFT on everything mixed | SFT done (1B, 3B) |
| LLM judge | Claude scores every answer pass/fail (`scripts/judge_answers.py`) | done |
| iOS app | SwiftUI chat screen + llama.cpp, fully offline | runs in the simulator |
| Next | DPO for the new disasters, microphone input, device speed tests, Android | planned |

## Results

Test questions were held out before training and never trained on. "Acceptable" means **an
answer fails only if following it could plausibly hurt someone**; weak, messy or long answers pass.

**Flood model** (49 held-out flood questions, answers read and judged by hand, one judge):

| Model | Acceptable |
|---|---|
| Llama-3.2-1B base | 80% |
| + SFT | 86% |
| + SFT + DPO | 94% |
| Llama-3.2-3B base | 94% |
| 3B + SFT | 92% |
| 3B + SFT + DPO | **96%** |

3B DPO model at different sizes (same questions): f16 6.0 GB **98%**, Q8_0 3.2 GB 94%,
Q5_K_M 2.2 GB 94%, **Q4_K_M 1.9 GB 94%**, Q3_K_M 1.6 GB 96%. Quantization cost nothing measurable
on 3B (differences of 1-2 answers are noise at this test size). The 1B DPO model lost more at 4-bit.

**Multi-disaster model** (181 held-out questions, 23 disasters, SFT only):

| Judge | 1B | 3B |
|---|---|---|
| Hand verdicts (lenient rule) | 91% | not done |
| Claude judge (strict) | 75% | **80%** |

The Claude judge is stricter than the hand rule: it caught 16 of the 17 answers I failed
by hand and flagged 30 more (some are real misses, some over-strict). **Compare models with
the same judge; do not compare the absolute percentages.** The 3B fixes 30 of the 1B's failures
but adds 20 new ones. Weakest areas: avalanche, tornado, tsunami, chemical and radiological
questions, plus the old flood cases ("stay in the basement", "do not go up the stairs").

Known problems: answers mention 911 almost every time (98%), a few use the rule of the wrong
disaster, and some medical advice is wrong (insulin, oxygen).

## Honest limits

- **Small tests, one judge.** 49 and 181 questions; one answer is 2% or 0.6%. Verdicts are a
  strong hint, not a measurement. The Claude judge was calibrated against hand verdicts (83% agreement).
- **Synthetic, unreviewed data.** Questions and answers were written by commercial LLMs
  (Claude for flood questions, an external chat model for flood answers, DeepSeek for the other
  disasters) and were **not reviewed by an expert**. Those providers' terms may restrict using
  their outputs to train other models. Check them before any use beyond research.
- **Not tested on a real iPhone** (speed, battery, memory).
- `data/dpo/dpo_train_REJECTED_UNSAFE.jsonl` contains **deliberately dangerous answers** as
  negative examples. Never show them to users.

## Repo layout

```
data/prompts/        prompts for questions, answers and the judge (+ CHANGELOG.md)
data/synthetic/      generated questions and answers (flood, and multi/ for 22 disasters)
data/splits*/        train/test files (flood: splits/, all disasters: splits_multi/)
data/dpo/            DPO pairs (rejected answers are unsafe on purpose, see its README)
scripts/             generators, split, GGUF build, test runner, LLM judge
eval/                20 seed scenarios, run_eval.py, and all results (eval/results/)
notebooks/           Colab: plain HF (flood), plain HF multi-disaster, Unsloth multi-disaster
ios/                 SwiftUI app + setup script (see ios/README.md)
docs/                experiment write-ups, loss curves, interview guide
models/ third_party/ (gitignored) weights, GGUF files, llama.cpp pinned to b11240
```

## Reproduce

```bash
# 1. setup (macOS, Apple Silicon)
brew install cmake && uv sync
./scripts/build_base_models.sh                 # llama.cpp + base GGUFs

# 2. data (needs DEEPSEEK_API_KEY / ANTHROPIC_API_KEY in .env)
uv run python scripts/generate_questions_deepseek.py --prompt multi_v3
uv run python scripts/generate_answers_deepseek.py --prompt multi_v2
uv run python scripts/split_data_multi.py      # holds out the test set first

# 3. train in Colab: notebooks/disaster_assistant_unsloth_colab.ipynb
#    upload data/splits_multi/train.jsonl and test_eval.jsonl, download the merged model

# 4. convert + quantize + test on the Mac
scripts/build_finetuned_models.sh models/hf/<merged> <name> Q8_0 Q4_K_M
uv run python scripts/run_test_gguf.py models/gguf/<name>-Q4_K_M.gguf

# 5. judge accuracy with an LLM (about $0.70 per 181 answers)
uv run python scripts/judge_answers.py <results.json>

# 6. iOS app
ios/setup.sh && open ios/DisasterHelper/DisasterHelper.xcodeproj
```

The base weights come from `unsloth/Llama-3.2-*-Instruct`, an ungated copy of Meta's release.
The Llama 3.2 Community License applies.

## Lessons so far

- Loss does not measure safety. Every model had a smooth, healthy loss curve and still said
  "stay in the basement" for a flood. Read the answers.
- Code must decide the data mix (disaster, phase, scenario); models ignore "how many of each".
- Mix all disasters in one training file. Training one disaster at a time makes the model forget
  the others, and some rules are opposite (flood: go up; tornado: go to the lowest floor).
- Preference pairs must match format and length, or the model learns the formatting, not the safety.
- Run a 5-step smoke test before every long run (and label its outputs so they are never reused).

More detail: `docs/experiment_01_lora_1b_r8.md`, `docs/experiment_02_dpo.md`, `docs/interview_guide.md`.
