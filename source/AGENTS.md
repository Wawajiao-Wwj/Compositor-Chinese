# Notes for AI agents

Compositor is a macOS image editor for compositing and photo work, written in Swift (SwiftUI and AppKit, with some C for pixel work).

## Designing or editing a Compositor project

If you've been asked to make or change an image in a `.comp` project, you don't need the app's source code. Read [docs/writing-comp-files.md](docs/writing-comp-files.md): it covers the file format, the rules that make a project load, and how to write it safely while it's open, so the person can watch the canvas update as you work.

## Working on the app itself

- Build the Chinese release from the repository root with `python3 source/scripts/build_chinese.py`. See `../docs/build.md` for prerequisites. The upstream Xcode project is retained for development.
- Upstream tests: the `CompositorTests` target (`xcodebuild ... test -only-testing:CompositorTests`) requires full Xcode. This repository CI checks translation parameters and the project page; it does not run the full application test suite. See `../docs/validation.md`.
- Match the surrounding code: its naming, its comment style and density.
- American spelling in code, comments and UI ("color", not "colour").
- The project file format is described in [docs/project-format.md](docs/project-format.md). A change to what's saved means a format version bump there and in `ProjectManifest.current`.
