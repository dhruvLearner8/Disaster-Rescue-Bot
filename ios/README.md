# Disaster Helper (iOS)

Offline chat app. A SwiftUI screen on top of llama.cpp runs the fine-tuned flood model on the phone.

## Run it
1. `ios/setup.sh` (builds the llama engine once, copies the model into the app, generates the Xcode project).
   Use another model with `ios/setup.sh models/gguf/llama32-1b-dpo-Q8_0.gguf`.
2. Open `ios/DisasterHelper/DisasterHelper.xcodeproj` in Xcode and press Run.
   - Simulator: works as is.
   - iPhone: Signing & Capabilities -> pick your Team, then choose your phone.

## Notes
- Default model: 3B flood model, Q4_K_M (1.9 GB). It needs about 2.5 GB of free memory.
  If the app is killed on a small phone, use the 1B model above.
- The model file is copied into the app and is not in git (`Resources/flood-model.gguf`).
- Each question is answered on its own, because the model was trained on single questions.
  The prompt in `Sources/LlamaEngine.swift` matches the training prompt exactly. Keep them in sync.
- Mic button (later): add it next to the text field in `ChatView.swift` and write the text into `vm.input`.
- Test without typing: launch with the argument `-autoask "your question"`.
