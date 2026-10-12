#!/usr/bin/env bash
# Download Llama-3.2-1B-Instruct, convert to GGUF, and build the quantized variants.
set -euo pipefail
cd "$(dirname "$0")/.."

LLAMA=third_party/llama.cpp
HF_DIR=models/hf/Llama-3.2-1B-Instruct
OUT=models/gguf

if [ ! -d "$LLAMA" ]; then
  git clone https://github.com/ggml-org/llama.cpp "$LLAMA"
  git -C "$LLAMA" checkout b11240
fi
if [ ! -x "$LLAMA/build/bin/llama-server" ]; then
  cmake -S "$LLAMA" -B "$LLAMA/build" -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF
  cmake --build "$LLAMA/build" --config Release -j --target llama-cli llama-server llama-quantize llama-bench
fi

uv run hf download unsloth/Llama-3.2-1B-Instruct --local-dir "$HF_DIR" --exclude "*.pth" "original/*"

mkdir -p "$OUT"
uv run python "$LLAMA/convert_hf_to_gguf.py" "$HF_DIR" --outtype f16 --outfile "$OUT/llama32-1b-base-f16.gguf"
for q in Q8_0 Q5_K_M Q4_K_M; do
  "$LLAMA/build/bin/llama-quantize" "$OUT/llama32-1b-base-f16.gguf" "$OUT/llama32-1b-base-$q.gguf" "$q"
done
