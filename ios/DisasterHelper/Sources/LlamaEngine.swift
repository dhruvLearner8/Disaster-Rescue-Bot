import Foundation
import llama

enum EngineError: Error { case loadFailed, contextFailed }

/// Runs one question at a time through the model.
/// Every question starts from an empty cache: the model was trained on single questions,
/// so earlier turns are not fed back in.
actor LlamaEngine {
    private let model: OpaquePointer
    private let context: OpaquePointer
    private let vocab: OpaquePointer
    private let sampler: UnsafeMutablePointer<llama_sampler>
    private var batch: llama_batch

    static let maxNewTokens = 350

    // Same system prompt and chat format the model was trained and tested with
    // (the Llama 3.2 template, including its fixed date header).
    static let systemPrompt = "You are an offline emergency assistant helping someone during a flood or storm. Give clear, short, numbered safety steps. Put the most urgent action first. If life is at risk, tell them to contact emergency services (911) when possible. Never guess: if you are not sure, say so."

    static func prompt(for question: String) -> String {
        "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCutting Knowledge Date: December 2023\nToday Date: 26 Jul 2024\n\n\(systemPrompt)<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n\(question)<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    }

    init(path: String) throws {
        llama_backend_init()
        var mp = llama_model_default_params()
        #if targetEnvironment(simulator)
        mp.n_gpu_layers = 0   // the simulator cannot run the Metal path
        #endif
        guard let m = llama_model_load_from_file(path, mp) else { throw EngineError.loadFailed }

        var cp = llama_context_default_params()
        cp.n_ctx = 2048
        let threads = Int32(max(2, min(6, ProcessInfo.processInfo.processorCount - 2)))
        cp.n_threads = threads
        cp.n_threads_batch = threads
        guard let c = llama_init_from_model(m, cp) else {
            llama_model_free(m)
            throw EngineError.contextFailed
        }
        model = m
        context = c
        vocab = llama_model_get_vocab(m)
        sampler = llama_sampler_chain_init(llama_sampler_chain_default_params())
        llama_sampler_chain_add(sampler, llama_sampler_init_greedy())   // greedy, like our tests
        batch = llama_batch_init(1024, 0, 1)
    }

    deinit {
        llama_sampler_free(sampler)
        llama_batch_free(batch)
        llama_free(context)
        llama_model_free(model)
        llama_backend_free()
    }

    /// Streams the answer piece by piece through `onToken`. Stops when the task is cancelled.
    func generate(_ question: String, onToken: @Sendable (String) async -> Void) async {
        llama_memory_clear(llama_get_memory(context), true)
        llama_sampler_reset(sampler)

        let tokens = tokenize(Self.prompt(for: String(question.prefix(800))))
        guard !tokens.isEmpty, tokens.count < 1000 else { return }

        batch.n_tokens = 0
        for (i, t) in tokens.enumerated() { add(t, Int32(i), logits: i == tokens.count - 1) }
        guard llama_decode(context, batch) == 0 else { return }

        var pos = Int32(tokens.count)
        var pending: [UInt8] = []   // bytes of a character that is still incomplete
        for _ in 0..<Self.maxNewTokens {
            if Task.isCancelled { break }
            let token = llama_sampler_sample(sampler, context, batch.n_tokens - 1)
            if llama_vocab_is_eog(vocab, token) { break }

            pending += pieceBytes(token)
            if let text = String(bytes: pending, encoding: .utf8) {
                pending.removeAll()
                await onToken(text)
            }

            batch.n_tokens = 0
            add(token, pos, logits: true)
            pos += 1
            guard llama_decode(context, batch) == 0 else { break }
        }
    }

    private func add(_ id: llama_token, _ pos: Int32, logits: Bool) {
        let i = Int(batch.n_tokens)
        batch.token[i] = id
        batch.pos[i] = pos
        batch.n_seq_id[i] = 1
        batch.seq_id[i]![0] = 0
        batch.logits[i] = logits ? 1 : 0
        batch.n_tokens += 1
    }

    private func tokenize(_ text: String) -> [llama_token] {
        let count = text.utf8.count
        var buffer = [llama_token](repeating: 0, count: count + 8)
        // add_special = false (the prompt already starts with <|begin_of_text|>), parse_special = true
        let n = llama_tokenize(vocab, text, Int32(count), &buffer, Int32(buffer.count), false, true)
        return n < 0 ? [] : Array(buffer.prefix(Int(n)))
    }

    private func pieceBytes(_ token: llama_token) -> [UInt8] {
        var buffer = [CChar](repeating: 0, count: 32)
        var n = llama_token_to_piece(vocab, token, &buffer, Int32(buffer.count), 0, false)
        if n < 0 {
            buffer = [CChar](repeating: 0, count: Int(-n))
            n = llama_token_to_piece(vocab, token, &buffer, Int32(buffer.count), 0, false)
        }
        return buffer.prefix(Int(max(n, 0))).map { UInt8(bitPattern: $0) }
    }
}
