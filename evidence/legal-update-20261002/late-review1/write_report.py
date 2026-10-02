"""Refresh final lane report from exact offline receipts, without external actions."""
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
BASE = 'fe488a5320e50f5afc5e4a26150d935eaa154974'
STAMP = ('Co-Authored-By: Codex gpt-6.1-sol <noreply@openai.com>\n'
         'Orchestrated-By: Claude Opus 5.5 (https://claude.ai/code/session_01FmhSHW1iJi7BTZXYiaRQJz)')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def read(name):
    return json.loads((OUT / name).read_text())


full, focused, red = [read(n) for n in ('full-green.json', 'focused-final.json', 'red-parent.json')]
proof, checks, frozen = [read(n) for n in ('red-proof.json', 'checks.json', 'frozen-input-comparison.json')]
for result in (full, focused):
    assert result['exit'] == 0 and result['compile'] == 'PASS'
    assert result['requested'] == result['executed'] and not any(result[k] for k in ('failedMethods', 'errors', 'skipped', 'omitted'))
assert red['exit'] == 1 and red['testsRun'] == 5 and len(red['failedMethods']) == 4 and red['assertionFailures'] == 154
assert red['requested'] == red['executed'] and not any(red[k] for k in ('errors', 'skipped', 'omitted'))
assert proof['removed'] is True and proof['parent'] == BASE
for stem in ('full-green', 'focused-final', 'red-parent'):
    result = read(stem + '.json')
    assert hashlib.sha256((OUT / (stem + '.log.gz')).read_bytes()).hexdigest() == result['logSha256']
    assert gzip.decompress((OUT / (stem + '.log.gz')).read_bytes())
for check in checks:
    path = ROOT / check['log']
    assert path.is_file() and path.stat().st_size and hashlib.sha256(path.read_bytes()).hexdigest() == check['logSha256']
    decoded = gzip.decompress(path.read_bytes())
    assert decoded or (check['cmd'] == ['git', 'diff', '--check'] and check['exit'] == 0)
assert len(checks) == 14 and sum(c['result'] == 'PASS' for c in checks) == 13
blocked = [c for c in checks if c['result'] != 'PASS']
assert len(blocked) == 1 and blocked[0]['result'] == 'BLOCKED_EFFECTIVE_DATE' and blocked[0]['exit'] == 1
spec = importlib.util.spec_from_file_location('review_checks', OUT / 'run_checks.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
assert frozen['match'] is True and read('final-inputs.json') == runner.fingerprint()
for name, gate in [('account-sync-content.candidate.json', 'serverReadiness'), ('ios-content.json', 'legalReadiness'), ('android-content.candidate.json', 'legalReadiness')]:
    source = json.loads((ROOT / 'docs' / name).read_text())
    assert source[gate] and all(value is False for value in source[gate].values())
head = git('rev-parse', 'HEAD')
commits = []
for sha in git('rev-list', '--reverse', f'{BASE}..HEAD').splitlines():
    assert git('show', '-s', '--format=%B', sha).endswith(STAMP)
    subject = git('show', '-s', '--format=%s', sha)
    commits.append({'sha': sha, 'subject': subject, 'stampVerified': True})
green = next(c['sha'] for c in commits if c['subject'].startswith('fix('))
previous = read('late-report.historical.json')
questions = [q for q in previous['ownerQuestions'] if q['id'] != 'OQ-LATE-PARITY']
questions.append({'id': 'OQ-LATE-PARITY', 'question': '통합 담당자는 두 앱의 정책·스토어 검토 문구·검사 입력과 검사 결과를 확인해 주세요. 문구는 스토어 가격 또는 최종 확정 가격을 사용하고, 앱은 스토어가 돌려준 가격을 표시해요.', 'reason': 'Historical partner snapshots are preserved; consistent store-price wording or final owner amounts and matching final committed partner checks remain integration prerequisites. No price decision is reopened.', 'affects': ['LATE-02', 'REVIEW-1-PRICE'], 'decisionReopened': False})
report = {
    'lane': 'legal-update-legal', 'scope': 'late decisions review-1 revision; prior implementation retained',
    'status': 'STATIC_GREEN_RELEASE_GATE_BLOCKED_UNPUBLISHED', 'reviewedHead': BASE, 'head': head,
    'sourceGreenHead': green, 'branch': git('branch', '--show-current'), 'commits': commits,
    'redCommits': [{'sha': proof['redCommit'], 'expectedFailing': red['failedMethods'], 'proof': {**proof, 'receipt': str(OUT / 'red-parent.json'), 'log': str(OUT / 'red-parent.log.gz')}}],
    'inheritedRedCommits': previous['redCommits'], 'greenTests': full['executed'],
    'items': [
        {'id': 'REVIEW-1-PRICE', 'severity': 'major', 'verdict': 'FIXED_STATIC_VERIFIED', 'how': 'Use reviewer/owner-permitted store price wording consistently in all17 canonical/staged offers and18 generated Terms pages. Monthly/annual plan, full local price, applicable taxes and billing period before purchase preserved. Validator/tests enforce store-only public wording and reject reintroduced currency amounts and bare retired prices. Final owner Store setup amounts unchanged; historical partner policy snapshots remain gated, not claimed aligned.', 'proof': str(OUT / 'preservation-audit.json')},
        {'id': 'LATE-01', 'verdict': 'PRESERVED_STATIC_VERIFIED', 'how': 'EU/EEA, UK and Switzerland exclusions and no appointed representative preserved in all17 policy locales; applicable existing-user safeguards retained. Privacy sources unchanged from reviewed HEAD; full prior regressions pass.'},
        {'id': 'LATE-02', 'verdict': 'FIXED_PERMITTED_STORE_PRICE_ALTERNATIVE', 'how': 'Public offers use store price consistently. Internal Store configuration authority remains USD1.99/13.99, KRW3300/19900, JPY300/1980; other storefronts store-converted. Native UI must show Store-returned prices. No price decision reopened or partner/Store state certified.'},
        {'id': 'LATE-03', 'verdict': 'PRESERVED_STATIC_VERIFIED', 'how': 'All17 first-time1-calendar-month trial, eligibility/account warning, auto-renewal and cancel-anytime suffixes unchanged byte for byte. All remaining Terms fields, refund/statutory/price-change consent and Store billing subsections unchanged byte for byte.'},
        {'id': 'INHERITED-LEGAL-MUSTS', 'verdict': 'PRESERVED_STATIC_VERIFIED_OPERATIONAL_GATES_CLOSED', 'how': 'Original researched implementation and prior RED history preserved. Privacy/UShealth/processor/PIPA/FTC/deletion/backup sources and renderers match baseline hashes; all prior regression methods executed in final full suite. Actual operations and supplier particulars remain unverified and false-gated.'},
    ],
    'checks': [{**c, 'cmd': shlex.join(c['cmd']), 'proof': str(ROOT / c['log'])} for c in checks] + [{'cmd': 'focused six-module family via exact-identity runner', 'exit': focused['exit'], 'result': 'PASS', 'methods': focused['testsRun'], 'proof': str(OUT / 'focused-final.json')}],
    'filesTouched': git('diff', '--name-only', f'{BASE}..HEAD').splitlines(),
    'filesTouchedScope': f'{BASE}..{head}; review-1 revision only',
    'nativeNeeded': [], 'nativeNeededNote': 'Static repository has no native target or selectors. Orchestrator owns native/provider/Store checks; none invented.',
    'ownerQuestions': questions,
    'notDone': [
        'No push, merge, deploy, publication, Store-console or production/network action.',
        'Release check actually exits1 for null effective date; all readiness flags remain false. Not counted PASS.',
        'Partner repositories are outside lane scope. Historical conflicting numeric policy snapshots are preserved; final committed partner policy/review/check receipts and actual Store configuration are integration prerequisites, not certified here.',
        'Actual supplier particulars/contracts/transfers, native consent/deletion, backup/restore7-day erasure and incident/rights procedure execution remain unverified.',
        'Native/provider/Store readback, live/public deletion URL, visual/counsel/native-speaker review NOT_RUN.',
    ],
    'inputFingerprints': str(OUT / 'baseline.json'),
    'frozenInputs': {'receipt': str(OUT / 'final-inputs.json'), 'comparison': str(OUT / 'frozen-input-comparison.json'), 'files': frozen['files'], 'match': True, 'scope': 'source/tests/runner/fixtures/generated pages/assets/config/Python runtime'},
    'preservationAudit': str(OUT / 'preservation-audit.json'),
    'independentSourceAudit': str(OUT / 'independent-source-audit.json'),
    'independentReportAudit': str(OUT / 'independent-report-audit.json'),
    'historicalLateReport': {'path': str(OUT / 'late-report.historical.json'), 'head': BASE, 'sha256': hashlib.sha256((OUT / 'late-report.historical.json').read_bytes()).hexdigest()},
    'intermediateVerification': {'receipt': str(OUT / 'interim-checks.json'), 'result': 'Historical earlier GREEN checks before restoration of original bare-price validator guard; final receipts supersede only matching coverage'},
    'externalState': {**previous['externalState'], 'publication': 'NOT_PERFORMED', 'ownedProcess': None, 'device': None, 'temporaryWorktreesRemoved': True},
    'workingTree': git('status', '--short'),
    'reportWriterInitialFailure': str(OUT / 'report-validation-initial-failure.json'),
    'reportValidation': {'exactIdentities': True, 'logsAndHashes': True, 'frozenInputs': True, 'commitStamps': True, 'falseReadinessGates': True},
    'nextAction': 'Orchestrator reviews/integrates revision commits, obtains final committed partner copy/check receipts and operational/Store evidence; never publish from this lane.',
}
assert not any('TO BE APPOINTED' in json.dumps(q) for q in questions)
TARGET.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
assert json.loads(TARGET.read_text()) == report
if '--checkpoint' in sys.argv:
    (OUT / 'report-validation-precompletion.json').write_text(json.dumps({'head': head, 'reportSha256': hashlib.sha256(TARGET.read_bytes()).hexdigest(), 'result': 'PASS', 'reportValidation': report['reportValidation']}, indent=2) + '\n')
print(json.dumps({'head': head, 'tests': full['testsRun'], 'ordinaryChecksPass': 13, 'releaseGate': blocked[0]['result'], 'frozenFiles': frozen['files'], 'report': str(TARGET), 'validation': 'PASS'}))
