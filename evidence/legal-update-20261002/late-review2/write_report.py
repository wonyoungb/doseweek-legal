"""Write the final review-2 report from retained offline evidence only."""
import gzip
import hashlib
import importlib.util
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = Path('/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-late-report.json')
BASE = '3cbc050be05cb9a8ae84a8916ed34f15419dcf40'
STAMP = ('Co-Authored-By: Codex gpt-6.1-sol <noreply@openai.com>\n'
         'Orchestrated-By: Claude Opus 5.5 (https://claude.ai/code/session_01FmhSHW1iJi7BTZXYiaRQJz)')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def read(name):
    return json.loads((OUT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


full, focused, provenance, red = [read(name + '.json') for name in
                                 ('full-green', 'focused-green', 'provenance-green', 'red-parent')]
for result, count in ((full, 208), (focused, 68), (provenance, 1)):
    assert result['exit'] == 0 and result['compile'] == 'PASS' and result['testsRun'] == count
    assert result['requested'] == result['executed']
    assert not any(result[k] for k in ('failedMethods', 'errors', 'skipped', 'omitted'))
assert red['exit'] == 1 and red['compile'] == 'PASS'
assert red['testsRun'] == len(red['failedMethods']) == red['assertionFailures'] == 6
assert red['requested'] == red['executed']
assert not any(red[k] for k in ('errors', 'skipped', 'omitted'))
proof = read('red-proof.json')
assert proof['removed'] and proof['parent'] == BASE
assert not Path(proof['temporaryWorktree']).exists()
assert git('rev-parse', proof['redCommit'] + '^') == BASE
for stem in ('full-green', 'focused-green', 'provenance-green', 'red-parent'):
    log = OUT / (stem + '.log.gz')
    assert sha(log) == read(stem + '.json')['logSha256'] and gzip.decompress(log.read_bytes())
checks = read('checks.json')
for check in checks:
    path = ROOT / check['log']
    assert path.is_file() and sha(path) == check['logSha256']
    decoded = gzip.decompress(path.read_bytes())
    assert decoded or (check['cmd'] == ['git', 'diff', '--check'] and check['exit'] == 0)
assert len(checks) == 14 and sum(c['result'] == 'PASS' for c in checks) == 13
blocked = [c for c in checks if c['result'] != 'PASS']
assert len(blocked) == 1 and blocked[0]['exit'] == 1
assert blocked[0]['result'] == 'BLOCKED_EFFECTIVE_DATE'
spec = importlib.util.spec_from_file_location('review_checks', OUT / 'run_checks.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
frozen = read('frozen-input-comparison.json')
assert frozen['match'] and read('final-inputs.json') == runner.fingerprint()
supplement = read('provenance-input-comparison.json')
assert supplement['match'] and supplement['before'] == supplement['after']
assert sha(ROOT / 'legal-release-map.json') == supplement['after']['sha256']
assert sha(OUT / 'verify_provenance.py') == supplement['after']['supplementRunnerSha256']
assert supplement['coverage'] == provenance['executed']
preservation = read('preservation-audit.json')
assert preservation['result'] == 'PASS'
for path, hashes in preservation['preservedFiles'].items():
    assert sha(ROOT / path) == hashes['baseline'] == hashes['current']
assert read('independent-source-audit.json')['result'] == 'PASS_NO_BLOCKING_OR_MAJOR'
for name, gate in [('account-sync-content.candidate.json', 'serverReadiness'),
                   ('ios-content.json', 'legalReadiness'),
                   ('android-content.candidate.json', 'legalReadiness')]:
    source = json.loads((ROOT / 'docs' / name).read_text())
    assert source[gate] and all(value is False for value in source[gate].values())
head = git('rev-parse', 'HEAD')
commits = []
for commit in git('rev-list', '--reverse', f'{BASE}..HEAD').splitlines():
    assert git('show', '-s', '--format=%B', commit).endswith(STAMP)
    commits.append({'sha': commit, 'subject': git('show', '-s', '--format=%s', commit),
                    'stampVerified': True})
green = next(c['sha'] for c in commits if c['subject'].startswith('fix('))
previous = read('late-report.historical.json')
assert previous['head'] == BASE
questions = [q for q in previous['ownerQuestions'] if q['id'] != 'OQ-LATE-PARITY']
questions.append({
    'id': 'OQ-LATE-PARITY',
    'question': '통합 담당자는 두 앱의 정책·스토어 검토 문구·검사 입력을 스토어 가격 기준으로 맞추고, 해당 커밋의 검사 결과를 남겨 주세요. 앱은 스토어가 돌려준 가격을 표시해요.',
    'reason': 'Historical partner snapshots remain receipts only. Consistent store-price copy and matching committed partner checks are required before the parity gate opens; actual Store configuration needs separate readback.',
    'affects': ['LATE-02', 'LATE-REVIEW2-PRICE-AUTHORITY'], 'decisionReopened': False,
})
report = {
    'lane': 'legal-update-legal', 'scope': 'late review-2 single-major revision; prior legal implementation preserved',
    'status': 'STATIC_GREEN_RELEASE_GATE_BLOCKED_UNPUBLISHED',
    'reviewedHead': BASE, 'head': head, 'sourceGreenHead': green,
    'branch': git('branch', '--show-current'), 'commits': commits,
    'redCommits': [{'sha': proof['redCommit'], 'expectedFailing': red['failedMethods'],
                    'proof': {**proof, 'receipt': str(OUT / 'red-parent.json'),
                              'log': str(OUT / 'red-parent.log.gz')}}],
    'inheritedRedCommits': previous['redCommits'] + previous['inheritedRedCommits'],
    'greenTests': full['executed'],
    'items': [
        {'id': 'LATE-REVIEW2-PRICE-AUTHORITY', 'severity': 'major',
         'verdict': 'FIXED_STATIC_VERIFIED',
         'how': 'Active coordination, operations, account blocker, release provenance, tests and this report use price-agnostic store-price wording. Numeric configuration authority removed. Historical partner objects and evidence unchanged, with derived numeric matches explicitly historical. Actual Store prices need readback and native UI uses Store-returned prices. All publication/parity/readiness gates remain closed.',
         'proof': str(OUT / 'preservation-audit.json')},
        {'id': 'REVIEW-1-PRICE', 'verdict': 'PRESERVED_STATIC_VERIFIED',
         'how': 'All17 canonical/staged Terms and all162 generated pages unchanged; store-price public wording, full local price/taxes/billing-period-before-purchase requirements and rejection guards preserved.'},
        {'id': 'LATE-01', 'verdict': 'PRESERVED_STATIC_VERIFIED',
         'how': 'All17 EU/EEA, UK and Switzerland exclusions and no appointed representative preserved, with existing-user rights and safeguards. Actual Store exclusions remain unverified.'},
        {'id': 'LATE-02', 'verdict': 'FIXED_PERMITTED_STORE_PRICE_ALTERNATIVE',
         'how': 'Public and active internal copy consistently use store price. No numeric Store-configuration authority is asserted in this lane. Native UI shows Store-returned localized prices. Partner copy/check receipts and Store readback remain separate prerequisites.'},
        {'id': 'LATE-03', 'verdict': 'PRESERVED_STATIC_VERIFIED',
         'how': 'All17 first-time one-calendar-month trial, eligibility, auto-renewal, cancellation and refund/statutory safeguards unchanged. Trials can be cancelled any time in the store.'},
        {'id': 'INHERITED-LEGAL-MUSTS', 'verdict': 'PRESERVED_STATIC_VERIFIED_OPERATIONAL_GATES_CLOSED',
         'how': 'Privacy/US-health/PIPA/FTC/processors/deletion/backup sources preserved; all earlier regressions executed. Source receipts do not certify actual provider/native/rights/incident/backup operation.'},
        {'id': 'CONTINUITY-MINOR', 'verdict': 'FIXED',
         'how': 'Removed obsolete RED-stage no-product-edit wording from active handoff; previous outcome sections clearly historical.'},
    ],
    'checks': [{**c, 'cmd': shlex.join(c['cmd']), 'proof': str(ROOT / c['log'])} for c in checks]
              + [{'cmd': 'python3 evidence/legal-update-20261002/late-review2/run_tests.py ROOT OUT test_legal_late_review2 test_legal_late_review1 test_legal_late_decisions test_legal_revision2 test_terms_legal_update test_monetization_copy test_account_sync_candidate',
                  'exit': 0, 'result': 'PASS', 'methods': focused['testsRun'],
                  'proof': str(OUT / 'focused-green.json')},
                 {'cmd': 'python3 evidence/legal-update-20261002/late-review2/verify_provenance.py',
                  'exit': 0, 'result': 'PASS', 'methods': provenance['testsRun'],
                  'proof': str(OUT / 'provenance-input-comparison.json')}],
    'filesTouched': git('diff', '--name-only', f'{BASE}..HEAD').splitlines(),
    'filesTouchedScope': f'{BASE}..{head}; late review-2 only',
    'nativeNeeded': [], 'nativeNeededNote': 'Static repository has no native targets/selectors. Native/provider/Store proof belongs to the orchestrator; none run or invented here.',
    'ownerQuestions': questions,
    'notDone': [
        'No push, merge, deployment, publication, Store-console, production or network action.',
        'Release check actually exits1 for null effective date. All readiness/parity flags stay false; the failed gate is not PASS.',
        'Partner repositories outside scope; final store-price policy/review/check receipts and actual Store readback remain unverified.',
        'Actual supplier contracts/transfer particulars, native health consent/deletion, backup/restore7-day erasure, incident and consumer-rights operations remain unverified.',
        'Native/provider/Store/live/visual/counsel/native-speaker verification NOT_RUN.',
    ],
    'inputFingerprints': str(OUT / 'baseline.json'),
    'frozenInputs': {'receipt': str(OUT / 'final-inputs.json'),
                     'comparison': str(OUT / 'frozen-input-comparison.json'),
                     'files': frozen['files'], 'match': True,
                     'scope': 'source/tests/runner/fixtures/generated pages/assets/config/Python runtime',
                     'additionalInput': str(OUT / 'provenance-input-comparison.json'),
                     'additionalScope': 'final full release-map hash and exact new provenance selector'},
    'preservationAudit': str(OUT / 'preservation-audit.json'),
    'independentSourceAudit': str(OUT / 'independent-source-audit.json'),
    'historicalLateReport': {'path': str(OUT / 'late-report.historical.json'),
                             'head': BASE, 'sha256': sha(OUT / 'late-report.historical.json')},
    'externalState': {**previous['externalState'], 'publication': 'NOT_PERFORMED',
                       'ownedProcess': None, 'device': None, 'temporaryWorktreesRemoved': True},
    'workingTree': git('status', '--short'),
    'reportValidation': {'exactIdentities': True, 'logsAndHashes': True, 'frozenInputs': True,
                         'provenanceSupplement': True, 'commitStamps': True,
                         'falseReadinessGates': True, 'priceAgnosticActiveAuthority': True},
    'nextAction': 'Orchestrator reviews/integrates new commits; obtains final store-price partner copy/check receipts and operational/Store proof. Never publish from this lane.',
}
active = {key: report[key] for key in ('items', 'ownerQuestions', 'nextAction')}
assert not re.search(r'(?:USD|KRW|JPY|[$₩¥])\s*\d', json.dumps(active, ensure_ascii=False))
assert 'exact final late-owner prices' not in json.dumps(active)
audit = OUT / 'independent-report-audit.json'
if audit.exists():
    assert json.loads(audit.read_text())['result'] == 'PASS'
    report['independentReportAudit'] = str(audit)
TARGET.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
assert json.loads(TARGET.read_text()) == report
if '--checkpoint' in sys.argv:
    (OUT / 'report-validation-precompletion.json').write_text(json.dumps({
        'head': head, 'reportSha256': sha(TARGET), 'result': 'PASS',
        'reportValidation': report['reportValidation']}, indent=2) + '\n')
print(json.dumps({'head': head, 'tests': full['testsRun'], 'ordinaryChecksPass': 13,
                  'releaseGate': blocked[0]['result'], 'report': str(TARGET),
                  'validation': 'PASS'}))
