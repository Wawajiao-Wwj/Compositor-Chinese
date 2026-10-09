#!/usr/bin/env python3
"""Build the independent Chinese edition using Apple's installed Command Line Tools."""
from pathlib import Path
import json
import plistlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent
BUILD = WORK / 'build'
APP = WORK / 'dist' / 'Compositor 中文.app'
ORIGINAL = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/Applications/Compositor.app')


def run(*args):
    subprocess.run([str(x) for x in args], check=True, cwd=ROOT)


def compile_catalogs():
    count = 0
    for name in ['Localizable', 'InfoPlist']:
        catalog = json.loads((ROOT / 'Compositor' / (name + '.xcstrings')).read_text())
        tables = {lang: {} for lang in ['en', 'zh-Hans', 'zh-Hant']}
        for key, entry in catalog['strings'].items():
            tables['en'][key] = key
            for language, value in entry.get('localizations', {}).items():
                if 'stringUnit' not in value:
                    raise ValueError('Unsupported catalog variation: ' + key)
                tables.setdefault(language, {})[key] = value['stringUnit']['value']
        for language, table in tables.items():
            destination = APP / 'Contents' / 'Resources' / (language + '.lproj')
            destination.mkdir(parents=True, exist_ok=True)
            # Standard UTF-8 Apple strings files; JSON quoting also escapes these keys correctly.
            (destination / (name + '.strings')).write_text('\n'.join(
                json.dumps(key, ensure_ascii=False) + ' = ' + json.dumps(value, ensure_ascii=False) + ';'
                for key, value in sorted(table.items())) + '\n', encoding='utf-8')
        if name == 'Localizable':
            count = len(tables['zh-Hans'])
    return count


def main():
    BUILD.mkdir(exist_ok=True)
    (BUILD / 'module-cache').mkdir(exist_ok=True)
    (BUILD / 'extracted').mkdir(exist_ok=True)
    if not ORIGINAL.is_dir():
        raise SystemExit('找不到原版应用：' + str(ORIGINAL))
    info = plistlib.loads((ORIGINAL / 'Contents' / 'Info.plist').read_bytes())
    if info.get('CFBundleShortVersionString') != '1.4.7':
        raise SystemExit('本补丁针对 1.4.7；请勿直接应用到其他版本。')
    if APP.exists():
        shutil.rmtree(APP)
    contents = APP / 'Contents'
    (contents / 'MacOS').mkdir(parents=True)
    shutil.copytree(ORIGINAL / 'Contents' / 'Resources', contents / 'Resources')
    for key in list(info):
        if key.startswith(('SU', 'DT', 'BuildMachine')):
            del info[key]
    info.update(CFBundleIdentifier='com.wonderassembly.compositor.chinese',
                CFBundleName='Compositor 中文', CFBundleDisplayName='Compositor 中文',
                CFBundleDevelopmentRegion='en', CFBundleLocalizations=['en', 'zh-Hans', 'zh-Hant'],
                CFBundleExecutable='Compositor', CFBundleVersion='42.1',
                NSHumanReadableCopyright='Compositor © 2026 Wonder Assembly LLC. Chinese localization by Kelvin. MIT License.')
    # The original app remains the preferred handler for the shared project type.
    for document in info.get('CFBundleDocumentTypes', []):
        document['LSHandlerRank'] = 'Alternate'
    (contents / 'Info.plist').write_bytes(plistlib.dumps(info))
    (contents / 'PkgInfo').write_bytes(b'APPL????')
    count = compile_catalogs()
    print(f'已生成 {count} 条简体中文翻译。正在编译…', flush=True)
    sdk = subprocess.check_output(['xcrun', '--sdk', 'macosx26.5', '--show-sdk-path'], text=True).strip()
    objects = []
    for source in sorted((ROOT / 'Compositor').rglob('*.c')):
        obj = BUILD / (source.stem + '.o')
        run('xcrun', 'clang', '-O3', '-arch', 'arm64', '-mmacosx-version-min=26.0',
            '-isysroot', sdk, '-c', source, '-o', obj)
        objects.append(obj)
    sources = sorted((ROOT / 'Compositor').rglob('*.swift'))
    flags = ['xcrun', 'swiftc', '-O', '-whole-module-optimization', '-num-threads', '8',
             '-swift-version', '5', '-default-isolation', 'MainActor',
             '-enable-upcoming-feature', 'NonisolatedNonsendingByDefault',
             '-enable-upcoming-feature', 'InferIsolatedConformances',
             '-enable-upcoming-feature', 'MemberImportVisibility',
             '-module-name', 'Compositor', '-target', 'arm64-apple-macosx26.0', '-sdk', sdk,
             '-module-cache-path', str(BUILD / 'module-cache'),
             '-import-objc-header', str(ROOT / 'Compositor' / 'Compositor-Bridging-Header.h'),
             '-emit-localized-strings', '-emit-localized-strings-path', str(BUILD / 'extracted'),
             '-framework', 'Accelerate', '-framework', 'CoreGraphics']
    run(*flags, *sources, *objects, '-o', contents / 'MacOS' / 'Compositor')
    shutil.copy(ROOT / 'LICENSE', contents / 'Resources' / 'Compositor-LICENSE.txt')
    shutil.copy(WORK / 'THIRD_PARTY_NOTICES.md', contents / 'Resources')
    for source in (contents / 'Resources').rglob('*.strings'):
        run('plutil', '-lint', source)
    run('codesign', '--force', '--sign', '-', APP)
    run('codesign', '--verify', '--deep', '--strict', APP)
    print('中文版已生成：' + str(APP), flush=True)


if __name__ == '__main__':
    main()
