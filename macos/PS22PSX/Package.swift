// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "PS22PSX",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "PS22PSX", targets: ["PS22PSX"]),
    ],
    targets: [
        .executableTarget(
            name: "PS22PSX",
            path: "Sources/PS22PSX"
        ),
    ]
)
