import SwiftUI

enum SettingsTab: String {
    case general, shortcuts
    static let storageKey = "settingsTab"
}

struct SettingsView: View {
    let applicationDelegate: CompositorApplicationDelegate
    @AppStorage(SettingsTab.storageKey) private var tab = SettingsTab.general
    var body: some View {
        TabView(selection: $tab) {
            GeneralSettings(applicationDelegate: applicationDelegate)
                .tabItem { Label("General", systemImage: "gearshape") }.tag(SettingsTab.general)
            KeyboardShortcutsSheet(settings: .shared)
                .tabItem { Label("Keyboard Shortcuts", systemImage: "keyboard") }.tag(SettingsTab.shortcuts)
        }
        .roundedControls()
    }
}

/// Edit › Keyboard Shortcuts… opens Settings on that tab.
struct KeyboardShortcutsMenuItem: View {
    @Environment(\.openSettings) private var openSettings
    var body: some View {
        Button("Keyboard Shortcuts…") {
            UserDefaults.standard.set(SettingsTab.shortcuts.rawValue, forKey: SettingsTab.storageKey)
            openSettings()
        }
    }
}

/// The app's own language, stored as this app's AppleLanguages: the same setting as System Settings › General ›
/// Language & Region › Applications. macOS picks the language at launch, so a change applies after a restart.
enum AppLanguage: String, CaseIterable, Identifiable {
    case system = "", simplifiedChinese = "zh-Hans", traditionalChinese = "zh-Hant", english = "en"
    var id: String { rawValue }
    private static let key = "AppleLanguages"

    static var current: AppLanguage {
        let saved = (UserDefaults.standard.persistentDomain(forName: Bundle.main.bundleIdentifier ?? "")?[key] as? [String])?.first
        guard let saved else { return .system }
        return allCases.first { $0 != .system && saved.hasPrefix($0.rawValue) } ?? .system
    }

    func apply() {
        if self == .system { UserDefaults.standard.removeObject(forKey: Self.key) }
        else { UserDefaults.standard.set([rawValue], forKey: Self.key) }
    }

    /// Whether choosing this would change the language the app is showing now.
    var changesRunningLanguage: Bool {
        let preferences = self == .system
            ? UserDefaults.standard.persistentDomain(forName: UserDefaults.globalDomain)?[Self.key] as? [String] ?? Locale.preferredLanguages
            : [rawValue]
        return Bundle.preferredLocalizations(from: Bundle.main.localizations, forPreferences: preferences).first
            != Bundle.main.preferredLocalizations.first
    }
}

private struct GeneralSettings: View {
    let applicationDelegate: CompositorApplicationDelegate
    @State private var language = AppLanguage.current
    @State private var asksToRestart = false
    var body: some View {
        Form {
            Picker("Language", selection: $language) {
                Text("System Default").tag(AppLanguage.system)
                Divider()
                // Each language is named in itself, so the right one can be found from any language.
                Text(verbatim: "简体中文").tag(AppLanguage.simplifiedChinese)
                Text(verbatim: "繁體中文").tag(AppLanguage.traditionalChinese)
                Text(verbatim: "English").tag(AppLanguage.english)
            }
            Text("Menus and controls use this language after Compositor restarts. It’s the same setting as System Settings › General › Language & Region › Applications.")
                .font(.callout).foregroundStyle(.secondary).fixedSize(horizontal: false, vertical: true)
        }
        .formStyle(.grouped)
        .frame(width: 480)
        .fixedSize()
        .onChange(of: language) { _, language in
            language.apply()
            asksToRestart = language.changesRunningLanguage
        }
        .alert("Restart Compositor to use the new language?", isPresented: $asksToRestart) {
            Button("Restart Now") {
                applicationDelegate.relaunchesAfterQuit = true
                NSApp.terminate(nil)
            }
            Button("Later", role: .cancel) { }
        } message: {
            Text("You’ll be asked to save any unsaved changes first.")
        }
    }
}
