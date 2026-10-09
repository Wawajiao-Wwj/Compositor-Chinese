#!/usr/bin/env python3
"""Check translation parameters and coverage of compiler-extracted localized strings."""
from pathlib import Path
from collections import Counter
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent
catalog_only = "--catalog-only" in sys.argv
(WORK / "build").mkdir(exist_ok=True)
catalog = json.loads((ROOT / 'Compositor/Localizable.xcstrings').read_text())['strings']
# A prose percentage followed by a word isn't a printf argument.
placeholder = re.compile(r'%(?:[0-9]+\$)?[-+#0]*(?:[0-9]+|\*)?(?:\.(?:[0-9]+|\*))?(?:hh|ll|[hlLzjtq])?[@aAcCdDeEfFgGiInNoOpsSuUxX%]')
def parameters(text):
    return Counter(re.sub(r'%[0-9]+\$', '%', p) for p in placeholder.findall(text) if p != '%%')

failures = []
counts = {}
for language in ['zh-Hans', 'zh-Hant']:
    count = 0
    for key, entry in catalog.items():
        unit = entry.get('localizations', {}).get(language, {}).get('stringUnit')
        if not unit:
            continue  # Technical strings such as px, %lld and sRGB can use English fallback.
        count += 1
        if parameters(key) != parameters(unit['value']):
            failures.append(f'{language}: incompatible parameters: {key}')
    counts[language] = count

extracted = set()
for file in (WORK / 'build/extracted').glob('*.strings'):
    result = subprocess.check_output(['plutil', '-convert', 'json', '-o', '-', str(file)], text=True)
    extracted.update(json.loads(result))
for file in (WORK / 'build/extracted').glob('*.stringsdata'):
    data = json.loads(file.read_text())
    extracted.update(entry['key'] for entry in data.get('tables', {}).get('Localizable', []))
if not extracted and not catalog_only:
    failures.append('No compiler-extracted strings were found; build the app first.')
# This separator has no language-specific content.
allowed_invariants = {'·'}
missing = sorted(k for k in extracted if k not in catalog and k not in allowed_invariants)
if missing:
    failures.extend('Missing catalog key: ' + k for k in missing)

report = {'translationCounts': counts, 'compilerExtractedKeys': len(extracted),
          'coverageChecked': not catalog_only,
          'unchangedSymbols': sorted(extracted & allowed_invariants),
          'parameterAndCoverageFailures': failures}
(WORK / 'build/localization-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(bool(failures))
