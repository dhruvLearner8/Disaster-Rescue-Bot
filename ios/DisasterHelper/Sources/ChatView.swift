import SwiftUI

struct ChatView: View {
    @StateObject private var vm = ChatViewModel()

    var body: some View {
        VStack(spacing: 0) {
            Text("AI advice can be wrong. If you are in danger, call 911.")
                .font(.footnote.weight(.semibold))
                .multilineTextAlignment(.center)
                .frame(maxWidth: .infinity)
                .padding(8)
                .background(Color.red.opacity(0.15))

            switch vm.state {
            case .loading:
                Spacer(); ProgressView("Loading the model…"); Spacer()
            case .failed(let message):
                Spacer(); Text(message).foregroundStyle(.red).padding(); Spacer()
            default:
                messageList
            }
            inputBar
        }
        .task { await vm.loadModel() }
    }

    private var messageList: some View {
        ScrollViewReader { proxy in
            ScrollView {
                if vm.messages.isEmpty {
                    Text("Describe what is happening. For example: water is coming into my basement.")
                        .foregroundStyle(.secondary).padding(32)
                }
                LazyVStack(spacing: 10) {
                    ForEach(vm.messages) { m in Bubble(message: m).id(m.id) }
                }
                .padding()
            }
            .onChange(of: vm.messages.last?.text) { _ in
                if let id = vm.messages.last?.id { proxy.scrollTo(id, anchor: .bottom) }
            }
        }
    }

    private var inputBar: some View {
        HStack(alignment: .bottom, spacing: 8) {
            // Future: a microphone button goes here (Speech framework), filling vm.input.
            TextField("What is happening?", text: $vm.input, axis: .vertical)
                .lineLimit(1...4)
                .textFieldStyle(.roundedBorder)
                .submitLabel(.send)
                .onSubmit { vm.send() }
            if vm.state == .generating {
                Button { vm.stop() } label: { Image(systemName: "stop.circle.fill").font(.title) }
            } else {
                Button { vm.send() } label: { Image(systemName: "arrow.up.circle.fill").font(.title) }
                    .disabled(vm.state != .ready || vm.input.trimmingCharacters(in: .whitespaces).isEmpty)
            }
        }
        .padding(10)
        .background(.bar)
    }
}

private struct Bubble: View {
    let message: ChatMessage
    var body: some View {
        HStack {
            if message.isUser { Spacer(minLength: 40) }
            Text(message.text.isEmpty ? "…" : message.text)
                .padding(12)
                .background(message.isUser ? Color.blue : Color(.secondarySystemBackground))
                .foregroundStyle(message.isUser ? .white : .primary)
                .clipShape(RoundedRectangle(cornerRadius: 16))
            if !message.isUser { Spacer(minLength: 40) }
        }
    }
}
