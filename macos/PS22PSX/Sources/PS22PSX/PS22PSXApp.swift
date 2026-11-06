import SwiftUI

@main
struct PS22PSXApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .defaultSize(width: 780, height: 640)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}
