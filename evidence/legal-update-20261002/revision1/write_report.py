"""Write and validate the final offline lane report from retained exact receipts."""
import datetime
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path.cwd()
EVIDENCE = ROOT / 'evidence/legal-update-20261002/revision1'
REPORT = Path('/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-report.json')


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def path(name):
    return str(EVIDENCE / name)


r = read('initial-report.historical.json')
red, green, baseline = read('red-parent.json'), read('full-green.json'), read('baseline.json')
frozen = read('final-inputs.json')
assert red['compile'] == 'PASS' and red['exit'] == 1 and red['assertionFailures'] > 0
assert not red['errors'] and not red['skipped'] and not red['omitted']
assert green['exit'] == 0 and not green['failedMethods'] and not green['errors']
assert not green['skipped'] and not green['omitted']
assert green['requested'] == green['executed'] and green['testsRun'] == len(green['executed'])
for name, expected in frozen['hashes'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
for name, expected in baseline['inputs'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name

revision_red = git('rev-parse', 'a33a8b8')
source_green = git('rev-parse', '3ded23a')
head = git('rev-parse', 'HEAD')
required_stamp = ('Co-Authored-By: Codex gpt-6.1-sol <noreply@openai.com>\n'
                  'Orchestrated-By: Claude Opus 5.5 (https://claude.ai/code/session_01FmhSHW1iJi7BTZXYiaRQJz)')
commits = []
prior_types = {c['sha']: c['type'] for c in r['commits']}
for sha in git('rev-list', '--reverse', r['base'] + '..HEAD').splitlines():
    assert git('show', '-s', '--format=%B', sha).endswith(required_stamp), sha
    kind = prior_types.get(sha, 'RED' if sha == revision_red else 'GREEN' if sha == source_green else 'DOCS')
    commits.append({'sha': sha, 'subject': git('show', '-s', '--format=%s', sha),
                    'stampVerified': True, 'type': kind})

r.update(head=head, branch=git('branch', '--show-current'), sourceGreenCommit=source_green,
         completedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(), commits=commits,
         status='REVISION_1_STATIC_CANDIDATE_VERIFIED_RELEASE_BLOCKED',
         evidenceRoot=str(EVIDENCE), archiveIndex=None)
r['revision1'] = {'reviewedHead': baseline['parent'], 'redCommit': revision_red,
                  'sourceGreenCommit': source_green, 'commits': [c for c in commits if c['sha'] not in prior_types],
                  'result': 'ALL_REVIEW_1_ISSUES_FIXED_AWAITING_ORCHESTRATOR_REVIEW',
                  'independentReadOnlyReviews': 'regional_review and operator_ios_review: no material issues',
                  'preservationAudit': path('semantic-preservation-audit.json'),
                  'filesTouched': git('diff', '--name-only', baseline['parent'], 'HEAD').splitlines()}
r['redCommits'].append({'sha': revision_red, 'expectedFailing': red['failedMethods'], 'proof': {
    'parent': baseline['parent'], 'methodCount': red['testsRun'],
    'distinctFailingMethods': len(red['failedMethods']), 'assertionSubtestFailures': red['assertionFailures'],
    'compileExit': 0, 'runExit': 1, 'errors': 0, 'skipped': 0, 'omitted': [],
    'command': 'PYTHONDONTWRITEBYTECODE=1 python3 evidence/legal-update-20261002/revision1/run_tests.py /tmp/doseweek-legal-revision1-red evidence/legal-update-20261002/revision1/red-parent test_terms_legal_update test_privacy_legal_update test_legal_operations test_legal_revision1',
    'method': 'Detached reviewed parent plus only four RED test files; all script ASTs compile; assertion-only failures; parent worktree restored and removed before RED commit.',
    'receipt': path('red-parent.json'), 'log': path('red-parent.log.gz'),
    'testHashes': baseline['redTests']}})
for name, expected in baseline['redTests'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected
    assert hashlib.sha256(subprocess.check_output(['git', 'show', revision_red + ':' + name])).hexdigest() == expected
r['greenTests'] = {'result': 'PASS', 'methods': green['testsRun'], 'passingMethods': green['testsRun'],
                   'requested': green['requested'], 'discovered': green['requested'],
                   'executed': green['executed'], 'failed': [], 'errors': [], 'skipped': [],
                   'cancelled': [], 'omitted': [], 'receipt': path('full-green.json'),
                   'log': path('full-green.log.gz'), 'focusedMethods': 77}
r['checks'] = [{**c, 'proof': str(ROOT / c['log'])} for c in read('checks.json')]
r['checks'].append({'cmd': 'PYTHONDONTWRITEBYTECODE=1 python3 evidence/legal-update-20261002/revision1/run_tests.py . evidence/legal-update-20261002/revision1/full-green',
                    'exit': green['exit'], 'result': 'PASS', 'proof': path('full-green.json')})
for item in r['items']:
    item['greenTests'] = [ident.replace('test_unverified_provider_details_block_release_and_reps_marked_pending',
         'test_unverified_provider_and_sales_configuration_block_release_without_rep_appointment')
         for ident in item.get('greenTests', [])]
    assert set(item['greenTests']) <= set(green['executed']), item['id']
    if item['id'] == 'LEGAL-14':
        item['how'] = item['how'].replace('KRW3300/month19900/year', 'KRW3300/month22000/year (superseding owner/spec decision)')
        item['redProof'].append(revision_red)
    if item['id'] == 'LEGAL-11':
        item['how'] += ' Revision 1 also corrects every Android scope operator paragraph; all 102 canonical operator-bearing fields audited.'
        item['redProof'].append(revision_red)
    if item['id'] == 'LEGAL-22':
        item['how'] = '1.0.6 EU/EEA, UK and Switzerland sales excluded; no EU/UK representative designated or appointment placeholder. Applicable existing-user Art.6/9 bases, one-month rights, safeguards, transfer mechanisms and breach clocks preserved; actual Store exclusions remain false-gated.'
        item['remaining'] = 'Actual Store availability readback and recipient-specific safeguards/contracts/DPIA/processing records remain unverified. Appointment is not a prerequisite for this decided 1.0.6 scope; future reopening needs an applicability review.'
        item['redProof'].append(revision_red)
    if item['id'] == 'LEGAL-25':
        item['how'] += ' Canonical/staged iOS policy/help contain no Android/Google Play; full shared retention survives localized neutral store names, including separate verifier 90/30-day clauses.'
        item['redProof'].append(revision_red)
for ident, title, how, method_names in [
    ('R1-PRICE', 'Major: Korean annual price', '17 offers, renderer/test expectations and regenerated Terms use KRW22,000/year; actual Store prices still prevail.', ['test_terms_legal_update.TermsLegalUpdateTest.test_all_17_locales_keep_final_prices_and_store_localization']),
    ('R1-OPERATOR', 'Major: Android business operator', 'All 17 Android scope paragraphs now name Wonyoung Labs; representative/privacy officer and unrelated age/consent clauses preserved.', ['test_legal_revision1.LegalRevision1Test.test_operator_bearing_fields_use_business_and_keep_representative']),
    ('R1-MARKETS', 'Major: sales exclusions and representatives', 'All 34 policy paragraphs, exact metadata, readiness validation and operations align with excluded markets/no appointed reps; existing-user rights/safeguards retained.', ['test_legal_revision1.LegalRevision1Test.test_excluded_market_prose_preserves_existing_user_rights_all_locales', 'test_legal_revision1.LegalRevision1Test.test_market_contract_rejects_reopened_regions_and_fake_rep_contact', 'test_legal_revision1.LegalRevision1Test.test_release_still_requires_actual_sales_exclusion_readback']),
    ('R1-IOS', 'Minor: competing platform/store names in iOS copy', 'Neutralized all canonical/staged iOS policy/help platform/store references while preserving all retention/verifier clauses and numbers.', ['test_legal_revision1.LegalRevision1Test.test_canonical_ios_policy_and_help_avoid_other_platform_names', 'test_legal_revision1.LegalRevision1Test.test_staged_ios_policy_and_help_avoid_other_platform_names', 'test_legal_revision1.LegalRevision1Test.test_neutral_ios_retention_preserves_other_store_verifier_and_deletion_bounds'])]:
    r['items'].append({'id': ident, 'title': title, 'verdict': 'FIXED_STATIC_VERIFIED',
                       'how': how, 'greenTests': method_names, 'redProof': [revision_red]})

for q in r['ownerQuestions']:
    if q['id'] == 'OQ-01':
        q.update(question='1.0.6의 EU/EEA·영국·스위스 판매 제외를 실제 두 스토어 설정으로 확인하고, 기존 이용자에게 적용되는 권리·이전 보호·사고 대응 증거를 제공해 주세요.',
                 reason='Latest owner/spec excludes these markets and requires no EU/UK representative for this version; actual Store exclusion configuration and existing-user safeguards are operational evidence, not a reopened decision.')
        q.pop('placeholder', None)
    if q['id'] == 'OQ-09':
        q['question'] = '통합 담당자가 발효일·공급업체 사실·실제 판매 제외 설정·운영/native 증거를 확인하고 법률/번역/시각 검토를 완료한 뒤 기존 출시 순서에 따라 게시 게이트를 판단해 주세요.'
r['notDone'] = [text.replace(' and EU/UK contacts remain unverified', ' and actual Store exclusions remain unverified')
                for text in r['notDone']]
r['notDone'] = [text.replace('No push, merge, deployment, web publication, Store-console work or production/network calls.', 'No push, merge, deployment, web publication, Store-console work or production/network calls.') for text in r['notDone']]
r['scope']['stagedReceipt'] = path('staged-artifacts.json')
r['inputs'] = {'externalFingerprints': baseline['inputs'], 'python': green['python'],
               'frozenGateManifest': path('final-inputs.json'),
               'frozenGateComparison': read('frozen-input-comparison.json'),
               'sourceToCheckComparison': '249 source/test/runner/CSS/assets/template/locale/config/artifact fingerprints unchanged through final reporting. Documentation and derived release-map updates do not invalidate matching gates.'}
r['historicalResults']['initialAcceptedStaticCandidateLaterRejected'] = {
    'head': baseline['parent'], 'report': path('initial-report.historical.json'),
    'reason': 'review-1 identified three major decided-copy/spec mismatches and one minor iOS branding issue'}
r['historicalResults']['revisionCheckWrapperClassification'] = read('check-classification-correction.json')
r['historicalResults']['originalReportValidation'] = r['reportValidation']
candidate = json.loads((ROOT / 'docs/account-sync-content.candidate.json').read_text())
privacy = {name: json.loads((ROOT / 'docs' / name).read_text()) for name in ('ios-content.json', 'android-content.candidate.json')}
r['publicationGate']['closedReadiness'].update(serverReadiness=candidate['serverReadiness'],
    unresolvedCount=len(candidate['unresolvedBeforePublication']),
    privacyLegalReadiness={name: value['legalReadiness'] for name, value in privacy.items()})
r['publicationGate']['proof'] = path('check-11.log.gz')
r['publicationGate']['representatives'] = {name: value['representatives'] for name, value in privacy.items()}
r['publicationGate']['marketAvailability'] = candidate['marketAvailability']
r['cleanup'].update(worktreeStatus='CLEAN' if not git('status', '--porcelain') else 'REPORTING_DOCS_ONLY_PENDING_COMMIT',
                    temporaryProofWorktreesRemoved=True, ownedScratchRemaining=[],
                    activeProcessOwnership=None, nativeDeviceOwnership=None,
                    externalState='No network or external readback/mutation; never published.')
r['authorizationNote'] = 'Revision-1 instruction applies the current authoritative spec/owner decisions: KRW22000 annual and excluded EU/EEA, UK, Switzerland sales supersede earlier inputs. No decisions reopened and no publication authorization inferred.'
r['filesTouched'] = git('diff', '--name-only', r['base'], 'HEAD').splitlines()
r['filesTouchedCount'] = len(r['filesTouched'])
r['reportValidation'] = {'result': 'PASS', 'headMatches': True, 'filesInventoryMatches': True,
    'commitStampsVerified': True, 'redProofCompilesAndFailsOnAssertions': True,
    'greenIdentitySetsMatch': True, 'frozenInputMatchCount': len(frozen['hashes']),
    'finalHead': head, 'publication': 'BLOCKED_EXIT_1_NOT_PUBLISHED',
    'productChecksNotRerunForReportingDocs': True}
assert r['nativeNeeded'] == []
assert all(c['result'] in ('PASS', 'BLOCKED_EFFECTIVE_DATE') for c in r['checks'])
assert all(not v for v in candidate['serverReadiness'].values())
assert all(not v for source in privacy.values() for v in source['legalReadiness'].values())
for p in EVIDENCE.glob('*.log.gz'):
    assert p.stat().st_size > 0
    gzip.decompress(p.read_bytes())  # A silent diff log is valid empty stdout.
for key in ('head', 'commits', 'redCommits', 'greenTests', 'items', 'checks', 'filesTouched', 'nativeNeeded', 'ownerQuestions', 'notDone'):
    assert key in r
REPORT.write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n')
assert json.loads(REPORT.read_text()) == r
print(json.dumps({'head': head, 'commits': len(commits), 'revisionCommits': len(r['revision1']['commits']),
                  'tests': green['testsRun'], 'reportReadback': 'PASS',
                  'reportSha256': hashlib.sha256(REPORT.read_bytes()).hexdigest()}))
