# 3B results (Llama-3.2-3B-Instruct)

Answers to the 49 held-out questions in `data/splits/test.jsonl`.
Run in Colab with Hugging Face (fp16, greedy, batch 8, max 512 new tokens).
Same system prompt as the 1B runs. The 1B GGUF results are in `../test49/`.

Compare 3B Colab runs with the 1B Colab numbers. llama.cpp and Hugging Face
round a little differently, so the same model can change by 1-2 answers.

| File | Model |
|---|---|
| llama32-3b-base-fp16-hf.jsonl | 3B base, no training |
| llama32-3b-sft-fp16-hf.jsonl | 3B + SFT (LoRA r=8, 3 epochs, 78 steps), merged |
| llama32-3b-sft-smoke5-fp16-hf.jsonl | 3B + SFT adapter from the 5-step smoke test. NOT a real result. |

| llama32-3b-dpo-{f16,Q8_0,Q5_K_M,Q4_K_M,Q3_K_M}-gguf.jsonl | 3B + SFT + DPO as GGUF, run with llama.cpp (scripts/run_test_gguf.py) |
