#!/usr/bin/env bash
# One-time setup for the iOS app: build the llama engine, copy the model into the app, generate the Xcode project.
# Usage: ios/setup.sh [path/to/model.gguf]     (default: the 3B flood model, Q4_K_M, about 1.9 GB)
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${1:-models/gguf/llama32-3b-dpo-Q4_K_M.gguf}"
[ -f "$MODEL" ] || { echo "model not found: $MODEL"; exit 1; }

if [ ! -d third_party/llama.cpp/build-apple/llama.xcframework ]; then
  (cd third_party/llama.cpp && ./build-xcframework.sh ios-sim ios-device)
fi

mkdir -p ios/DisasterHelper/Resources
cp -c "$MODEL" ios/DisasterHelper/Resources/flood-model.gguf
(cd ios/DisasterHelper && xcodegen generate)
echo "Done. Open ios/DisasterHelper/DisasterHelper.xcodeproj in Xcode and press Run."
