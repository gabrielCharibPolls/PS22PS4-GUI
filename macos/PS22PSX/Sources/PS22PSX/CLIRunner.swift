import Foundation

enum CLIRunner {
    /// Locate ps22psx: app Resources, sibling Support folder, then repo/venv.
    static func resolveCLI() -> URL? {
        var roots: [URL] = []

        if let res = Bundle.main.resourceURL {
            roots.append(res.appendingPathComponent("ps22psx"))
            roots.append(res)
        }
        // Portable layout: PS22PSX.app/../Support/ps22psx or ../ps22psx
        if let exe = Bundle.main.executableURL?
            .deletingLastPathComponent() // MacOS
            .deletingLastPathComponent() // Contents
            .deletingLastPathComponent() // .app
        {
            roots.append(exe.appendingPathComponent("Support/ps22psx"))
            roots.append(exe.appendingPathComponent("ps22psx"))
        }

        // Dev: repo layout from source file
        let fromSource = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent()
            .deletingLastPathComponent() // macos
            .appendingPathComponent("ps22psx")
        roots.append(fromSource)
        roots.append(URL(fileURLWithPath: FileManager.default.currentDirectoryPath).appendingPathComponent("ps22psx"))

        for root in roots {
            let venv = root.appendingPathComponent(".venv/bin/ps22psx")
            if FileManager.default.isExecutableFile(atPath: venv.path) {
                return venv
            }
        }

        // PATH fallback
        if let pathEnv = ProcessInfo.processInfo.environment["PATH"] {
            for part in pathEnv.split(separator: ":") {
                let cand = URL(fileURLWithPath: String(part)).appendingPathComponent("ps22psx")
                if FileManager.default.isExecutableFile(atPath: cand.path) {
                    return cand
                }
            }
        }
        return nil
    }

    /// Working directory that contains bin/tools (Support or ps22psx root).
    static func resolveWorkDir(forCLI cli: URL) -> URL {
        // .../.venv/bin/ps22psx → ps22psx root
        if cli.lastPathComponent == "ps22psx" {
            let root = cli.deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
            let support = root.deletingLastPathComponent().appendingPathComponent("Support")
            if FileManager.default.fileExists(atPath: support.appendingPathComponent("bin/tools").path) {
                return support
            }
            return root
        }
        return cli
    }

    @discardableResult
    static func run(
        arguments: [String],
        onLine: ((String) -> Void)? = nil
    ) throws -> Int32 {
        guard let cli = resolveCLI() else {
            throw NSError(
                domain: "PS22PSX",
                code: 1,
                userInfo: [
                    NSLocalizedDescriptionKey:
                        "ps22psx introuvable. Ouvre le dossier Support ou installe: cd ps22psx && pip install -e .",
                ]
            )
        }

        let workDir = resolveWorkDir(forCLI: cli)
        let process = Process()
        var env = ProcessInfo.processInfo.environment
        let home = FileManager.default.homeDirectoryForCurrentUser.path
        env["PATH"] = "\(home)/bin:/opt/homebrew/bin:/usr/local/bin:" + (env["PATH"] ?? "")
        env["WINEDEBUG"] = "-all"
        if env["WINEPREFIX"] == nil {
            env["WINEPREFIX"] = "\(home)/.wine-ps22psx"
        }
        if env["PS22PSX_TOOLS"] == nil {
            let tools = workDir.appendingPathComponent("bin/tools")
            if FileManager.default.fileExists(atPath: tools.path) {
                env["PS22PSX_TOOLS"] = tools.path
            }
        }
        process.environment = env
        process.executableURL = cli
        process.arguments = arguments
        process.currentDirectoryURL = workDir

        let out = Pipe()
        let err = Pipe()
        process.standardOutput = out
        process.standardError = err

        let group = DispatchGroup()
        func pump(_ pipe: Pipe) {
            group.enter()
            DispatchQueue.global(qos: .userInitiated).async {
                defer { group.leave() }
                let handle = pipe.fileHandleForReading
                while true {
                    let data = handle.availableData
                    if data.isEmpty { break }
                    guard let chunk = String(data: data, encoding: .utf8) else { continue }
                    for line in chunk.split(whereSeparator: \.isNewline) {
                        let s = String(line)
                        DispatchQueue.main.async { onLine?(s) }
                    }
                }
            }
        }
        pump(out)
        pump(err)

        try process.run()
        process.waitUntilExit()
        group.wait()
        return process.terminationStatus
    }
}
