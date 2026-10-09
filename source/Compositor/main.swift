import Foundation
import SwiftUI

// Choose Simplified Chinese on the first launch of this independent edition, before AppKit loads its menus.
let languageDomain = Bundle.main.bundleIdentifier ?? "com.wonderassembly.compositor.chinese"
if UserDefaults.standard.persistentDomain(forName: languageDomain)?["ChineseEditionInitialized"] == nil {
    UserDefaults.standard.set(["zh-Hans"], forKey: "AppleLanguages")
    UserDefaults.standard.set(true, forKey: "ChineseEditionInitialized")
}
CompositorApp.main()
