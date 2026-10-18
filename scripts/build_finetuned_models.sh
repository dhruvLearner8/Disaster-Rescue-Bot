#!/usr/bin/env bash
# Convert a merged fine-tuned model (Hugging Face folder) to GGUF f16, Q8_0 and Q4_K_M.
# Usage: scripts/build_finetuned_models.sh <name>
#   <name> = sft  -> reads models/hf/sft_merged, writes models/gguf/llama32-1b-sft-*.gguf
#   <name> = dpo  -> reads models/hf/dpo_merged, writes models/gguf/llama32-1b-dpo-*.gguf
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="${1:?usage: $0 <sft|dpo>}"
LLAMA=third_party/llama.cpp
HF_DIR="models/hf/${NAME}_merged"
OUT=models/gguf

[ -d "$HF_DIR" ] || { echo "missing $HF_DIR"; exit 1; }

mkdir -p "$OUT"
uv run python "$LLAMA/convert_hf_to_gguf.py" "$HF_DIR" --outtype f16 --outfile "$OUT/llama32-1b-$NAME-f16.gguf"
for q in Q8_0 Q4_K_M; do
  "$LLAMA/build/bin/llama-quantize" "$OUT/llama32-1b-$NAME-f16.gguf" "$OUT/llama32-1b-$NAME-$q.gguf" "$q"
done
ls -lh "$OUT"/llama32-1b-"$NAME"-*.gguf
