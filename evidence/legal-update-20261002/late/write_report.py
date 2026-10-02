"""Write and validate the requested late-decision report; no publication/network."""
import gzip
import hashlib
import importlib.util
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = Path('/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-late-report.json')
BASE = 'a6a4e18f70bcf866a6bb50aacb8a64164cba8bde'
STAMP = ('Co-Authored-By: Codex gpt-6.1-sol <noreply@openai.com>\n'
         'Orchestrated-By: Claude Opus 5.5 (https://claude.ai/code/session_01FmhSHW1iJi7BTZXYiaRQJz)')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def read(name):
    return json.loads((OUT / name).read_text())


full, focused, red = (read(n) for n in ('full-green.json', 'focused-green.json', 'red-parent.json'))
proof = read('red-proof.json')
checks = read('checks.json')
for result in (full, focused):
    assert result['exit'] == 0 and result['compile'] == 'PASS'
    assert result['requested'] == result['executed']
    assert not any(result[k] for k in ('failedMethods', 'errors', 'skipped', 'omitted'))
assert red['exit'] == 1 and red['assertionFailures'] == 104
assert red['testsRun'] == 7 and len(red['failedMethods']) == 6
assert red['requested'] == red['executed'] and not any(red[k] for k in ('errors', 'skipped', 'omitted'))
for item in checks:
    path = ROOT / item['log']
    assert path.is_file() and path.stat().st_size > 0
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['logSha256']
    gzip.decompress(path.read_bytes())
assert len(checks) == 14
assert [c['result'] for c in checks].count('PASS') == 13
blocked = [c for c in checks if c['result'] != 'PASS']
assert len(blocked) == 1 and blocked[0]['result'] == 'BLOCKED_EFFECTIVE_DATE' and blocked[0]['exit'] == 1
spec = importlib.util.spec_from_file_location('late_checks', OUT / 'run_checks.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert read('final-inputs.json') == module.fingerprint(), 'Verified product/runner inputs changed'
assert read('frozen-input-comparison.json')['match'] is True

head = git('rev-parse', 'HEAD')
commits = []
for sha in git('rev-list', '--reverse', f'{BASE}..HEAD').splitlines():
    assert git('show', '-s', '--format=%B', sha).endswith(STAMP)
    subject = git('show', '-s', '--format=%s', sha)
    commits.append({'sha': sha, 'subject': subject, 'stampVerified': True,
                    'type': 'RED' if subject.startswith('test(') else
                            'GREEN' if subject.startswith('fix(') else 'DOCS'})
green = next(c['sha'] for c in commits if c['type'] == 'GREEN')
old = read('baseline-report.historical.json')
original_report = TARGET.with_name('legal-update-legal-report.json')
assert original_report.read_bytes() == (OUT / 'baseline-report.historical.json').read_bytes(), 'Original baseline report changed'
questions = [q for q in old['ownerQuestions'] if q['id'] != 'OQ-R2-PARITY']
questions.append({'id': 'OQ-LATE-PARITY',
    'question': '통합 담당자는 최종 가격에 맞는 두 앱의 정책·스토어 검토 문구·검사 입력 커밋과 검사 결과를 확인해 주세요. 앱은 스토어가 돌려준 가격을 표시해요.',
    'reason': 'Immutable snapshots are historical and partner lanes may advance. Final committed parity and partner check receipts must be acquired at integration; no price decision is reopened.',
    'affects': ['LATE-02'], 'decisionReopened': False})
report = {
    'lane': 'legal-update-legal', 'scope': '2026-10-02 late owner decisions',
    'status': 'STATIC_GREEN_RELEASE_GATE_BLOCKED_UNPUBLISHED',
    'reviewedHead': BASE, 'head': head, 'sourceGreenHead': green,
    'branch': git('branch', '--show-current'), 'commits': commits,
    'redCommits': [{'sha': proof['redCommit'], 'expectedFailing': red['failedMethods'],
        'proof': {'parent': BASE, 'receipt': str(OUT / 'red-parent.json'),
                  'log': str(OUT / 'red-parent.log.gz'), 'compile': 'PASS',
                  'testsRun': 7, 'failedMethods': 6, 'assertionFailures': 104,
                  'errors': 0, 'skipped': 0, 'omitted': 0,
                  'temporaryDetachedWorktreeRemoved': True}}],
    'supplementalHistoricalRegionalRed': proof['proofs'][1],
    'greenTests': full['executed'],
    'items': [
        {'id': 'LATE-01', 'verdict': 'INHERITED_STATIC_VERIFIED',
         'how': 'All17 EU/EEA, UK and Switzerland sales exclusions and null/not-designated representative contacts already present at reviewed HEAD. No contact placeholder/promise remains. Existing-user rights, transfer safeguards and breach clocks preserved. New source guard fails on historical pre-exclusion source:1 method,36 assertion failures,0 errors/skips/omissions. Current full suite passes it; no regional implementation edits needed.',
         'proof': str(OUT / 'preservation-audit.json')},
        {'id': 'LATE-02', 'verdict': 'FIXED_STATIC_VERIFIED',
         'how': 'All17 source/staged Terms use USD1.99/month,13.99/year; KRW3,300/month,19,900/year; JPY300/month,1,980/year; store-converted other prices. Renderer guards final amounts and rejects retired prices. All18 regenerated pages verified. Active operations/blocker/parity/map updated; historical evidence preserved. Native UI must use store-returned prices. Final partner check receipts and actual Store configuration remain unverified.',
         'proof': str(OUT / 'preservation-audit.json')},
        {'id': 'LATE-03', 'verdict': 'FIXED_STATIC_VERIFIED',
         'how': 'Fixed one-calendar-month Store-confirmed first-time trial, auto-renewal and cancel-anytime meaning guarded across17 canonical/staged locales. Removed33 variable-duration qualifiers in11locales across offer and both store billing subsections. Eligibility/account warnings and all other Terms fields retained; no native-speaker certification.',
         'proof': str(OUT / 'source-change-receipt.json')},
        {'id': 'INHERITED-LEGAL-MUSTS', 'verdict': 'STATIC_RECHECKED_OPERATIONAL_GATES_CLOSED',
         'how': 'Original reviewed legal/store implementation and assertion RED history preserved. Current199method full suite reruns all prior MUST regressions. Privacy/UShealth/processor/PIPA/FTC/deletion/backup sources and relevant renderers match baseline hashes. Operational evidence remains unverified and false-gated.',
         'proof': str(OUT / 'baseline-report.historical.json')},
    ],
    'checks': [{**c, 'cmd': shlex.join(c['cmd']), 'proof': str(ROOT / c['log'])} for c in checks]
              + [{'cmd': 'focused related six-module family via exact-identity runner',
                  'exit': focused['exit'], 'result': 'PASS', 'methods': focused['testsRun'],
                  'proof': str(OUT / 'focused-green.json')}],
    'filesTouched': git('diff', '--name-only', f'{BASE}..HEAD').splitlines(),
    'filesTouchedScope': f'{BASE}..{head} (late decisions only)',
    'nativeNeeded': [], 'nativeNeededNote': 'No native target in this static repository; orchestrator owns native/provider/Store verification. No test selector invented.',
    'ownerQuestions': questions,
    'notDone': [
        'No push, merge, deployment, publication, Store-console or production/network action.',
        'Release-date check actually exits1 on null effective date; all operational/legal readiness flags remain false. Not relabelled PASS.',
        'Final partner committed policy/review/verification parity and matching check receipts await integration; historical snapshots do not certify final partner or Store state.',
        'Actual supplier particulars/contracts/transfer mechanisms; native consent/deletion; backup/restore7-day erasure; incident/rights execution remain unverified.',
        'Native/provider/Store readbacks, live/public deletion URL, visual/counsel/native-speaker review NOT_RUN by this lane.',
        'Other repository app/store/web implementation and age-controls/medical-classification/claims/account requirements not changed or certified.',
    ],
    'inputFingerprints': str(OUT / 'baseline.json'),
    'frozenInputs': {'receipt': str(OUT / 'final-inputs.json'), 'comparison': str(OUT / 'frozen-input-comparison.json'),
                     'files': 257, 'match': True, 'scope': 'source/tests/runner/fixtures/generated pages/assets/config/Python runtime'},
    'preservationAudit': str(OUT / 'preservation-audit.json'),
    'baselineReport': {'path': str(OUT / 'baseline-report.historical.json'), 'head': BASE,
                       'sha256': hashlib.sha256((OUT / 'baseline-report.historical.json').read_bytes()).hexdigest(),
                       'originalExternalReportUnchanged': True},
    'externalState': {'appStoreRegionalExclusion': 'OWNER_REPORTED_REMOVED_NOT_READ_BACK',
                      'playRegionalExclusion': 'OWNER_REPORTED_TO_FOLLOW', 'publication': 'NOT_PERFORMED',
                      'ownedProcess': None, 'device': None, 'temporaryWorktreesRemoved': True},
    'workingTree': git('status', '--short'),
    'nextAction': 'Orchestrator reviews/integrates new commits, acquires final partner parity/check receipts and operational/Store evidence; publication is outside this lane.',
}
for source_name, gate in [('account-sync-content.candidate.json', 'serverReadiness'),
                          ('ios-content.json', 'legalReadiness'), ('android-content.candidate.json', 'legalReadiness')]:
    source = json.loads((ROOT / 'docs' / source_name).read_text())
    assert source[gate] and all(v is False for v in source[gate].values())
    assert source.get('effectiveDate') is None or source_name != 'account-sync-content.candidate.json'
assert not any('APPOINTED' in json.dumps(q) or 'KRW22,000' in json.dumps(q) for q in questions)
TARGET.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
assert json.loads(TARGET.read_text()) == report
validation = {'head': head, 'report': str(TARGET), 'reportSha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(),
              'schemaReadback': 'PASS', 'commitStamps': 'PASS', 'identitiesAndLogs': 'PASS',
              'frozenInputComparison': 'PASS', 'ownedTemporaryWorktreesRemoved': True,
              'methods': full['testsRun'], 'ordinaryCheckPasses': 13, 'releaseGate': blocked[0],
              'workingTreeClean': not report['workingTree']}
if '--final' not in sys.argv[1:]:
    (OUT / 'report-validation-precompletion.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps(validation))
