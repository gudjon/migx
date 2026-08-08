// migx (Swift) — ADR-009 wave 2 stub.
//
// Proves the ONE thing that makes the migration mechanical: a Swift binary and
// the Python one answer `--json` identically from the same files. ADR-008 binds
// command IDs, JSON shape and exit codes; it never bound a language. If parity
// holds here, every later port is a port and not a redesign.
//
// Reads the same config and state as migx-cli. It does NOT own them: while both
// binaries exist the filesystem is the only shared truth, and a Swift-side
// cache would be a second one.
//
// Build:  swiftc -O tools/migx-swift/Sources/main.swift -o build/migx-swift

import Foundation

let version = "0.1.0-stub"

// MARK: - paths (must match migx_cli.config / migx_cli.sessionlock)

func home() -> URL { FileManager.default.homeDirectoryForCurrentUser }

func configPath() -> URL {
    if let override = ProcessInfo.processInfo.environment["MIGX_CONFIG"] {
        return URL(fileURLWithPath: override)
    }
    return home().appendingPathComponent(".config/migx/config.json")
}

func loadConfig() -> [String: Any] {
    guard let data = try? Data(contentsOf: configPath()),
          let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
    else { return [:] }
    return obj
}

/// Dotted lookup so `library.root` works whether the file nests it or flattens it.
func configValue(_ cfg: [String: Any], _ dotted: String) -> Any? {
    if let flat = cfg[dotted] { return flat }
    var node: Any? = cfg
    for part in dotted.split(separator: ".") {
        guard let dict = node as? [String: Any] else { return nil }
        node = dict[String(part)]
    }
    return node
}

func emit(_ payload: [String: Any], json: Bool, human: String) -> Never {
    // `__exit` is internal control, not part of the contract. Emitting it put a
    // field in the JSON that the Python binary does not produce — the one thing
    // this stub exists to prove does not happen. Strip before serialising.
    var body = payload
    body.removeValue(forKey: "__exit")
    if json,
       let data = try? JSONSerialization.data(
           withJSONObject: body, options: [.prettyPrinted, .sortedKeys]),
       let text = String(data: data, encoding: .utf8) {
        print(text)
    } else {
        print(human)
    }
    exit(payload["__exit"] as? Int32 ?? 0)
}

// MARK: - commands

func cmdConfigShow(json: Bool) -> Never {
    let cfg = loadConfig()
    let root = configValue(cfg, "library.root") as? String ?? ""
    emit(
        [
            "schema": "migx.config/1",
            "config_path": configPath().path,
            "library.root": root,
            "library.template": configValue(cfg, "library.template") as? String ?? "dj",
        ],
        json: json,
        human: "config: \(configPath().path)\n  library.root  \(root)")
}

func cmdSessionNow(json: Bool) -> Never {
    let cfg = loadConfig()
    let root = configValue(cfg, "library.root") as? String ?? ""

    // "nothing playing" and "cannot tell" are different answers. Same
    // distinction the Python side makes, for the same reason: an agent that
    // conflates them keeps coaching from its last known track after a drive
    // is ejected.
    var isDir: ObjCBool = false
    let mounted = FileManager.default.fileExists(atPath: root, isDirectory: &isDir)
        && isDir.boolValue
    if !mounted {
        emit(
            [
                "schema": "migx.live-status/1",
                "status": "library-unreachable",
                "library_root": root,
                "error": "\(root) is not mounted — cannot tell what is playing "
                    + "(this is NOT the same as nothing playing)",
                "__exit": Int32(2),
            ],
            json: json,
            human: "\(root) is not mounted — cannot tell what is playing "
                + "(this is NOT the same as nothing playing)")
    }

    let live = URL(fileURLWithPath: root).appendingPathComponent("_live.json")
    var doc: [String: Any] = [:]
    if let data = try? Data(contentsOf: live),
       let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
        doc = obj
    }
    let path = doc["path"] as? String
    emit(
        [
            "schema": "migx.live-status/1",
            "path": path ?? NSNull(),
            "room": doc["room"] as? [String: Any] ?? [:],
        ],
        json: json,
        human: "now: \(doc["name"] as? String ?? "—")  [-]  \(path ?? "(unbound)")")
}

// MARK: - dispatch

var args = Array(CommandLine.arguments.dropFirst())
let wantsJSON = args.contains("--json")
args.removeAll { $0 == "--json" }

switch args.first {
case "config.show": cmdConfigShow(json: wantsJSON)
case "session.now": cmdSessionNow(json: wantsJSON)
case "--version": print("migx-swift \(version)"); exit(0)
default:
    FileErrorHandle: do {
        FileHandle.standardError.write(
            Data("usage: migx-swift {config.show|session.now} [--json]\n".utf8))
    }
    exit(2)
}
