# Repository notes

This is the unofficial Chinese adaptation of Compositor 1.4.7. App sources are under `source/`; the static GitHub Pages site is under `docs/`.

- Preserve upstream MIT copyright and Kelvin localization attribution.
- Keep saved project identifiers and enum raw values stable; translate displayed labels only.
- See `docs/build.md` for the tested local build environment and `docs/validation.md` for coverage limitations.
- Run `python3 source/scripts/verify_localization.py --catalog-only` for catalog-only edits, or omit the flag after compiling the application.
- Run `python3 scripts/check_pages.py` after page or publication-link edits.
- Release binaries belong in GitHub Releases, not in the Git source tree. Do not commit `build/`, `dist/`, local application preferences, or personal test projects.
- The static page illustration is not an application screenshot. Preserve that disclosure.
