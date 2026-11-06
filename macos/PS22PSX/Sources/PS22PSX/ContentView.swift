import SwiftUI
import UniformTypeIdentifiers
import AppKit

struct ContentView: View {
    @State private var isoURL: URL?
    @State private var emulatorURL: URL?
    @State private var iconURL: URL?
    @State private var backgroundURL: URL?
    @State private var outputDir: URL = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("PS22PSX-out", isDirectory: true)
    @State private var gameName: String = ""
    @State private var logText: String = "PS22PSX — interface native macOS (SwiftUI)\nLe build appelle le CLI Python en arrière-plan.\n"
    @State private var busy = false
    @State private var doctorOK: Bool?

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            header
            Form {
                fileRow("ISO / BIN PS2", selection: $isoURL, types: [.data], message: "Choisir ISO/BIN")
                fileRow("Émulateur .pkg", selection: $emulatorURL, types: [.data], message: "Choisir PKG")
                fileRow("Icône", selection: $iconURL, types: [.image], message: "Choisir image")
                fileRow("Fond", selection: $backgroundURL, types: [.image], message: "Choisir image")
                folderRow("Dossier sortie", selection: $outputDir)
                TextField("Nom du jeu (optionnel)", text: $gameName)
            }
            .formStyle(.grouped)

            HStack(spacing: 12) {
                Button("Doctor") { runDoctor() }
                    .disabled(busy)
                Button("Créer PKG PS4") { runCreate() }
                    .buttonStyle(.borderedProminent)
                    .disabled(busy || !canBuild)
                if busy { ProgressView().controlSize(.small) }
                Spacer()
                if let doctorOK {
                    Label(
                        doctorOK ? "Toolchain OK" : "Toolchain KO",
                        systemImage: doctorOK ? "checkmark.seal.fill" : "xmark.octagon.fill"
                    )
                    .foregroundStyle(doctorOK ? .green : .red)
                }
            }

            TextEditor(text: $logText)
                .font(.system(.body, design: .monospaced))
                .scrollContentBackground(.hidden)
                .padding(8)
                .background(Color(nsColor: .textBackgroundColor))
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .frame(minHeight: 220)
        }
        .padding(18)
        .frame(minWidth: 720, minHeight: 560)
        .onAppear { runDoctor() }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("PS22PSX")
                .font(.largeTitle.weight(.bold))
            Text("PS2 → fPKG PS4  ·  UI native SwiftUI")
                .foregroundStyle(.secondary)
        }
    }

    private var canBuild: Bool {
        isoURL != nil && emulatorURL != nil && iconURL != nil && backgroundURL != nil
    }

    @ViewBuilder
    private func fileRow(
        _ title: String,
        selection: Binding<URL?>,
        types: [UTType],
        message: String
    ) -> some View {
        LabeledContent(title) {
            HStack {
                Text(selection.wrappedValue?.lastPathComponent ?? "—")
                    .foregroundStyle(selection.wrappedValue == nil ? .secondary : .primary)
                    .lineLimit(1)
                Spacer(minLength: 8)
                Button("Choisir…") {
                    pickFile(types: types, message: message) { selection.wrappedValue = $0 }
                }
            }
        }
    }

    private func folderRow(_ title: String, selection: Binding<URL>) -> some View {
        LabeledContent(title) {
            HStack {
                Text(selection.wrappedValue.path)
                    .lineLimit(1)
                    .truncationMode(.middle)
                Spacer(minLength: 8)
                Button("Choisir…") {
                    pickFolder { selection.wrappedValue = $0 }
                }
            }
        }
    }

    private func appendLog(_ line: String) {
        logText += line + "\n"
    }

    private func runDoctor() {
        busy = true
        appendLog("> ps22psx doctor")
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let code = try CLIRunner.run(arguments: ["doctor"]) { line in
                    appendLog(line)
                }
                DispatchQueue.main.async {
                    doctorOK = (code == 0)
                    busy = false
                    if code != 0 { appendLog("doctor exit \(code)") }
                }
            } catch {
                DispatchQueue.main.async {
                    doctorOK = false
                    busy = false
                    appendLog("error: \(error.localizedDescription)")
                }
            }
        }
    }

    private func runCreate() {
        guard let iso = isoURL, let emu = emulatorURL, let icon = iconURL, let bg = backgroundURL else { return }
        try? FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)
        var args = [
            "create", iso.path,
            "--emulator", emu.path,
            "--icon", icon.path,
            "--background", bg.path,
            "--output", outputDir.path,
        ]
        if !gameName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            args += ["--name", gameName]
        }
        busy = true
        appendLog("> ps22psx " + args.joined(separator: " "))
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let code = try CLIRunner.run(arguments: args) { line in
                    appendLog(line)
                }
                DispatchQueue.main.async {
                    busy = false
                    if code == 0 {
                        appendLog("Terminé.")
                        NSWorkspace.shared.activateFileViewerSelecting([outputDir])
                    } else {
                        appendLog("create exit \(code)")
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    busy = false
                    appendLog("error: \(error.localizedDescription)")
                }
            }
        }
    }

    private func pickFile(types: [UTType], message: String, onPick: @escaping (URL) -> Void) {
        let panel = NSOpenPanel()
        panel.title = message
        panel.allowsMultipleSelection = false
        panel.canChooseDirectories = false
        panel.allowedContentTypes = types
        if panel.runModal() == .OK, let url = panel.url {
            onPick(url)
        }
    }

    private func pickFolder(onPick: @escaping (URL) -> Void) {
        let panel = NSOpenPanel()
        panel.canChooseFiles = false
        panel.canChooseDirectories = true
        panel.allowsMultipleSelection = false
        if panel.runModal() == .OK, let url = panel.url {
            onPick(url)
        }
    }
}
