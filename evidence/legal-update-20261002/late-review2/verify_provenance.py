"""Supplement the retained gate with the new test's release-map input."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'legal-release-map.json'
TEST = ('test_legal_late_review2.LegalLateReview2Test.'
        'test_release_provenance_has_no_numeric_store_configuration_authority')


def fingerprint():
    release = json.loads(SOURCE.read_text())['legalUpdate106']
    return {
        'path': 'legal-release-map.json',
        'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'testedFields': {key: release[key] for key in
                         ('subscription', 'effectiveDate', 'commercialCopyParity')},
        'runnerSha256': hashlib.sha256((OUT / 'run_tests.py').read_bytes()).hexdigest(),
        'supplementRunnerSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


before = fingerprint()
proc = subprocess.run(['python3', str(OUT / 'run_tests.py'), str(ROOT),
                       str(OUT / 'provenance-green'), TEST], cwd=ROOT)
after = fingerprint()
receipt = json.loads((OUT / 'provenance-green.json').read_text())
assert before == after and proc.returncode == 0
assert receipt['requested'] == receipt['executed'] == [TEST]
assert not any(receipt[k] for k in ('failedMethods', 'errors', 'skipped', 'omitted'))
(OUT / 'provenance-input-comparison.json').write_text(json.dumps({
    'before': before, 'after': after, 'match': True, 'result': 'PASS',
    'coverage': [TEST],
    'reason': 'The reused full-gate runner excludes derived release-map reporting. '
              'This supplement fingerprints the new test input and replays only its method.'
}, indent=2) + '\n')
print('PASS: exact provenance selector, full map and relevant-field fingerprints match')
