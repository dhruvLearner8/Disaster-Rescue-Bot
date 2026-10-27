import Foundation

struct ChatMessage: Identifiable {
    let id = UUID()
    let isUser: Bool
    var text: String
}

@MainActor
final class ChatViewModel: ObservableObject {
    enum State: Equatable { case loading, ready, generating, failed(String) }

    @Published var messages: [ChatMessage] = []
    @Published var input = ""
    @Published var state: State = .loading

    private var engine: LlamaEngine?
    private var task: Task<Void, Never>?

    /// The model file is added to the app by ios/setup.sh (Resources/flood-model.gguf).
    func loadModel() async {
        guard engine == nil else { return }
        guard let path = Bundle.main.path(forResource: "flood-model", ofType: "gguf") else {
            state = .failed("flood-model.gguf is not in the app. Run ios/setup.sh, then build again.")
            return
        }
        do {
            engine = try await Task.detached { try LlamaEngine(path: path) }.value
            state = .ready
            log("model loaded")
        } catch {
            state = .failed("The model could not be loaded. It may need more memory than this device has.")
            return
        }
        // Test hook: launch with  -autoask "your question"  to send it automatically.
        if let question = UserDefaults.standard.string(forKey: "autoask") {
            input = question
            send()
        }
    }

    func send() {
        let text = input.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty, state == .ready, let engine else { return }
        input = ""
        messages.append(ChatMessage(isUser: true, text: text))
        messages.append(ChatMessage(isUser: false, text: ""))
        state = .generating
        task = Task {
            await engine.generate(text) { [weak self] piece in await self?.append(piece) }
            finish()
        }
    }

    func stop() { task?.cancel() }

    /// Test-hook output goes to stderr, which is not buffered, so it shows up at once in the console.
    private func log(_ text: String) {
        if UserDefaults.standard.string(forKey: "autoask") != nil { fputs(text + "\n", stderr) }
    }

    private func append(_ piece: String) {
        guard !messages.isEmpty else { return }
        messages[messages.count - 1].text += piece
        if messages[messages.count - 1].text.count == piece.count { log("first token") }
    }

    private func finish() {
        state = .ready
        if UserDefaults.standard.string(forKey: "autoask") != nil, let last = messages.last {
            log("ANSWER_START\n\(last.text)\nANSWER_END")
        }
    }
}
