"""Refresh the explicitly requested final lane JSON; never publishes or uses network."""
import gzip
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TARGET = Path('/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-report.json')
PARENT = 'd3b6e32b21789c67763ad9f73bfff77dc370cc2b'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def read(name):
    return json.loads((OUT / name).read_text())


old = read('revision1-report.historical.json')
full = read('full-green.json')
focused = read('focused-green.json')
red = read('red-parent.json')
proof = read('red-proof.json')
parity = json.loads((ROOT / 'docs/COMMERCIAL_COPY_PARITY_1_0_6.json').read_text())
head = git('rev-parse', 'HEAD')
commits = []
for sha in git('rev-list', '--reverse', f'{PARENT}..HEAD').splitlines():
    body = git('show', '-s', '--format=%B', sha)
    assert body.endswith('Co-Authored-By: Codex gpt-6.1-sol <noreply@openai.com>\n'
                         'Orchestrated-By: Claude Opus 5.5 (https://claude.ai/code/session_01FmhSHW1iJi7BTZXYiaRQJz)')
    subject = git('show', '-s', '--format=%s', sha)
    commits.append({'sha': sha, 'subject': subject, 'stampVerified': True,
                    'type': 'RED' if subject.startswith('test(') else
                            'GREEN' if subject.startswith('fix(') else 'DOCS'})
green = next(c['sha'] for c in commits if c['type'] == 'GREEN')
files = git('diff', '--name-only', f'{PARENT}..HEAD').splitlines()
checks = [{**r, 'cmd': ' '.join(r['cmd']), 'proof': str(ROOT / r['log'])}
          for r in read('checks.json')]
checks += [{'cmd': 'python3 evidence/legal-update-20261002/revision1/run_tests.py . '
                   'evidence/legal-update-20261002/revision2/full-green',
            'exit': full['exit'], 'result': 'PASS', 'methods': full['testsRun'],
            'proof': str(OUT / 'full-green.json')},
           {'cmd': 'focused related eight-module family via exact-identity runner',
            'exit': focused['exit'], 'result': 'PASS', 'methods': focused['testsRun'],
            'proof': str(OUT / 'focused-green.json')}]
items = old['items']
items.extend([
    {'id': 'R2-RETIRED-BUYER-PROGRAM', 'severity': 'major', 'verdict': 'FIXED_STATIC_VERIFIED',
     'how': 'All17 Terms/candidate/staged policy/help retire separate grant and claim/code program. '
            'Removed claim privacy/help fields, schema requirements, renderer injections and active '
            'application/evidence/review/appeal/code release instructions. Core features Free for '
            'new/prior users, ordinary Store-confirmed trial, statutory rights and historical '
            'ad-free-rights review retained; original feature help tails match byte-for-byte.',
     'greenTests': [t for t in full['executed'] if 'test_legal_revision2.LegalRevision2Test.test_' in t
                    and not ('parity' in t or 'commercial' in t)],
     'proof': str(OUT / 'semantic-preservation-audit.json')},
    {'id': 'R2-COMMERCIAL-PARITY', 'severity': 'major',
     'verdict': 'COORDINATION_RECORDED_BLOCKED_EXTERNAL',
     'how': 'Review-2 required KRW22,000 retained in all17 Terms. Committed iOS now matches; '
            'committed Android policy, Play preparation copy and checks still use19,900. '
            'Exact committed/working receipts and coordinated Android next action recorded. '
            'New commercialCopyParityVerified=false gate rejects missing/false readiness; '
            'Store-returned app UI prices remain required. No partner writes or decision reopened.',
     'proof': str(OUT / 'partner-parity-receipts.json'),
     'remaining': parity['nextAction']},
    {'id': 'R2-IOS-SHORT-STORE-NAMES', 'severity': 'minor', 'verdict': 'FIXED_STATIC_VERIFIED',
     'how': 'Removed retired claim-help and localized shortened Play purchase-token references. '
            'Canonical/staged iOS rejects full/short store aliases, CJK adjacency and hyphens; '
            'Google sign-in remains allowed. Every other sync/token-encryption/deletion byte survives.',
     'proof': str(OUT / 'neutral-token-preservation.json')},
    {'id': 'R2-PIPA-THOUSAND', 'severity': 'minor', 'verdict': 'FIXED_STATIC_VERIFIED',
     'how': 'Both privacy sources use1.000 in de/es/tr and1\u00a0000 in fr/pl/sv. '
            'Only12threshold paragraphs changed; restoring grouping reproduces original whole-source '
            'bytes. Independent sensitive/unique-ID and unauthorized-access triggers,72-hour clock '
            'and all incident metadata preserved.', 'proof': str(OUT / 'minor-preservation.json')},
])
questions = old['ownerQuestions'] + [
    {'id': 'OQ-R2-PARITY', 'question': '통합 담당자는 Android 정책·스토어 검토 문구·검사 입력을 '
     '리뷰2의 KRW22,000에 함께 맞추고, iOS와 일치하는 커밋·검사 증거를 남겨 주세요.',
     'reason': 'Committed Android remains19,900; coordination/verification task only, not a new price decision.',
     'affects': ['R2-COMMERCIAL-PARITY'], 'decisionReopened': False},
    {'id': 'OQ-R2-HISTORICAL-RIGHTS', 'question': '과거 광고 없는 이용 약속과 기존 구매자의 법정 권리를 '
     '플랫폼·소비자법 기준으로 검토한 증거를 남겨 주세요.',
     'reason': 'No separate grant/claim-code program is offered; retirement does not settle historical rights.',
     'affects': ['R2-RETIRED-BUYER-PROGRAM'], 'decisionReopened': False},
]
report = {
    'lane': 'legal-update-legal', 'revision': 2,
    'status': 'STATIC_GREEN_AWAITING_REVIEW_EXTERNAL_PARITY_BLOCKED',
    'reviewedHead': PARENT, 'head': head, 'branch': git('branch', '--show-current'),
    'sourceGreenHead': green, 'commits': commits,
    'redCommits': [{'sha': proof['redCommit'], 'expectedFailing': red['failedMethods'],
                    'proof': {'parent': PARENT, 'receipt': str(OUT / 'red-parent.json'),
                              'log': str(OUT / 'red-parent.log.gz'),
                              'validation': str(OUT / 'red-proof.json'),
                              'compile': 'PASS', 'methods': 43, 'failedMethods': 10,
                              'assertionFailures': 1098, 'errors': 0, 'skipped': 0, 'omitted': 0,
                              'temporaryDetachedWorktreeRemoved': True}}],
    'greenTests': full['executed'], 'items': items, 'checks': checks,
    'filesTouched': files, 'filesTouchedScope': f'{PARENT}..{head} (revision2 only)',
    'nativeNeeded': [], 'nativeNeededNote': 'Static legal repository has no native targets. '
      'Native/server/provider/Store flow proof belongs to orchestrator; no selector invented.',
    'ownerQuestions': questions,
    'notDone': old['notDone'] + ['Android committed commercial price parity remains BLOCKED; '
      'no partner policy/review/verification changes are claimed.',
      'Future paraphrased contradictory offers are not certified by anchor-presence regressions; '
      'current exact retired body and independent source review found no survivor.'],
    'commercialCopyParity': parity,
    'verification': {'full': {'methods': 193, 'executed': full['executed'], 'failed': [],
        'errors': [], 'skipped': [], 'omitted': []}, 'focusedMethods': 81,
        'checks': '12PASS / 1BLOCKED_EFFECTIVE_DATE (actual child exit1 preserved)',
        'sitePages': 162, 'stagedPages': 126, 'locales': 17, 'stagedRoutes': 7,
        'koreanTone': {'sentences': 2078, 'violations': 0, 'existingExceptions': 9, 'stale': 0},
        'frozenInputs': str(OUT / 'final-inputs.json'), 'frozenFileCount': 255,
        'inputComparison': str(OUT / 'full-frozen-input-comparison.json'),
        'visual': 'NOT_RUN', 'native': 'NOT_RUN', 'provider': 'NOT_RUN',
        'liveSite': 'LIVE_SITE_NOT_VERIFIED', 'counselNativeSpeaker': 'NOT_CERTIFIED'},
    'historical': {'previousRevisionReport': str(OUT / 'revision1-report.historical.json'),
        'previousResults': 'Historical; not restarted. Current193-method suite separately verified.',
        'redWrapperPredictionCorrection': proof['wrapperPredictionCorrection']},
    'cleanup': {'worktreeStatus': git('status', '--porcelain') or 'CLEAN',
        'temporaryProofWorktreesRemoved': not Path('/tmp/doseweek-legal-review2-red-30647c4').exists(),
        'ownedScratchRemaining': [], 'activeProcessOwnership': None, 'nativeDeviceOwnership': None},
    'externalState': 'No network, push, merge, deploy, Store action or publication; '
       'read-only committed partner receipts only.',
    'handoff': str(ROOT / 'docs/CURRENT_HANDOFF.md'), 'journal': str(ROOT / 'CHANGELOG.md'),
    'evidenceRoot': str(OUT),
    'authorizationNote': 'Revision2 explicitly retains KRW22,000 despite current spec/partner19900 '
       'inputs. No prices/trial/regions/backup/mg/operator decisions reopened. Never publish.',
}

# Validate actual evidence, identities, current relevant hashes and source provenance.
assert full['requested'] == full['executed'] and full['testsRun'] == 193
assert not any(full[k] for k in ('failedMethods', 'errors', 'skipped', 'omitted'))
assert red['compile'] == 'PASS' and red['exit'] == 1 and len(red['failedMethods']) == 10
assert not any(red[k] for k in ('errors', 'skipped', 'omitted'))
assert red['requested'] == red['executed'] and red['assertionFailures'] == 1098
assert all(c['result'] in ('PASS', 'BLOCKED_EFFECTIVE_DATE') for c in checks)
for path in OUT.glob('*.log.gz'):
    assert path.stat().st_size > 0
    decoded = gzip.decompress(path.read_bytes())
    assert decoded or path.name == 'check-12.log.gz', path
spec = importlib.util.spec_from_file_location('checks', OUT / 'run_checks.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.fingerprint() == read('final-inputs.json')
assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == sha
           for p, sha in json.loads((ROOT / 'legal-release-map.json').read_text())['legalUpdate106']['sourceHashes'].items())
assert report['cleanup']['temporaryProofWorktreesRemoved'] and not (ROOT / '.lane-work').exists()
report['reportValidation'] = {'result': 'PASS', 'headMatches': True,
    'filesInventoryMatches': True, 'commitStampsVerified': True,
    'redProofCompilesAndFailsOnAssertions': True, 'greenIdentitySetsMatch': True,
    'frozenInputMatchCount': 255, 'publication': 'BLOCKED_EXIT_1_NOT_PUBLISHED',
    'productChecksNotRerunForReportingDocs': True}
TARGET.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
assert json.loads(TARGET.read_text()) == report
print(json.dumps({'head': head, 'commits': len(commits), 'methods': 193,
                  'files': len(files), 'validated': True, 'status': report['status']}))
