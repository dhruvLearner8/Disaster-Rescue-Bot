#!/usr/bin/env bash
# Convert a merged model (Hugging Face folder) to GGUF f16, then quantize.
# Usage: scripts/build_finetuned_models.sh <hf_dir> <out_prefix> [quant ...]
#   e.g. scripts/build_finetuned_models.sh models/hf/dpo_merged llama32-1b-dpo
#        scripts/build_finetuned_models.sh models/hf/dpo_merged_3b llama32-3b-dpo Q8_0 Q5_K_M Q4_K_M Q3_K_M
set -euo pipefail
cd "$(dirname "$0")/.."

HF_DIR="${1:?usage: $0 <hf_dir> <out_prefix> [quant ...]}"
PREFIX="${2:?usage: $0 <hf_dir> <out_prefix> [quant ...]}"
shift 2
QUANTS=("$@"); [ ${#QUANTS[@]} -gt 0 ] || QUANTS=(Q8_0 Q4_K_M)
LLAMA=third_party/llama.cpp
OUT=models/gguf

[ -d "$HF_DIR" ] || { echo "missing $HF_DIR"; exit 1; }

mkdir -p "$OUT"
uv run python "$LLAMA/convert_hf_to_gguf.py" "$HF_DIR" --outtype f16 --outfile "$OUT/$PREFIX-f16.gguf"
for q in "${QUANTS[@]}"; do
  "$LLAMA/build/bin/llama-quantize" "$OUT/$PREFIX-f16.gguf" "$OUT/$PREFIX-$q.gguf" "$q"
done
ls -lh "$OUT"/"$PREFIX"-*.gguf
