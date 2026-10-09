#!/usr/bin/env python3
"""Package the validated Chinese application and write its SHA-256 checksum."""
from pathlib import Path
import hashlib
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dist/Compositor 中文.app"
ASSET = ROOT / "dist/Compositor-1.4.7-Chinese-arm64.zip"


def main():
    if not (APP / "Contents/MacOS/Compositor").is_file():
        raise SystemExit("Build the application before packaging.")
    subprocess.run(["python3", str(ROOT / "source/scripts/verify_localization.py")], check=True)
    subprocess.run(["codesign", "--verify", "--deep", "--strict", str(APP)], check=True)
    if ASSET.exists():
        ASSET.unlink()
    # Python writes the UTF-8 filename flag and Unix file permissions explicitly.
    # The bundle uses regular files; resource-fork metadata is not required.
    with zipfile.ZipFile(ASSET, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in [APP, *sorted(APP.rglob("*"))]:
            if path.is_symlink():
                raise SystemExit("Unexpected symlink in application bundle: " + str(path))
            archive.write(path, arcname=path.relative_to(APP.parent))
    with zipfile.ZipFile(ASSET) as archive:
        if archive.testzip() is not None:
            raise SystemExit("Archive integrity check failed.")
        required = ["Compositor 中文.app/Contents/MacOS/Compositor",
                    "Compositor 中文.app/Contents/Resources/Compositor-LICENSE.txt",
                    "Compositor 中文.app/Contents/Resources/THIRD_PARTY_NOTICES.md",
                    "Compositor 中文.app/Contents/Resources/zh-Hans.lproj/Localizable.strings",
                    "Compositor 中文.app/Contents/Resources/zh-Hant.lproj/Localizable.strings"]
        for member in required:
            if member not in archive.namelist():
                raise SystemExit("Missing release file: " + member)
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    (ROOT / "dist/SHA256SUMS.txt").write_text(digest + "  " + ASSET.name + "\n")
    print(f"Release ready: {ASSET.name} ({ASSET.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
