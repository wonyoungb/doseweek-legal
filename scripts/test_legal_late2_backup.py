"""LATE2 owner backup contract; assertion REDs use only parent-available APIs."""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

import account_sync_candidate
import render_account_sync

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'scripts/legal_late2_backup_fixture.json'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def joined(value):
    return '\n\n'.join(value)


class LegalLate2BackupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
        cls.candidate = load('docs/account-sync-content.candidate.json')
        cls.staged = render_account_sync.integrated_sources()

    def each(self):
        self.assertEqual(self.fixture['localeOrder'], self.candidate['localeOrder'])
        self.assertEqual(list(self.fixture['locales']), self.candidate['localeOrder'])
        for locale, expected in self.fixture['locales'].items():
            yield locale, expected, self.candidate['locales'][locale]

    def concepts(self, locale, expected, value, keys):
        for key in keys:
            alternatives = expected['concepts'][key]
            with self.subTest(locale=locale, meaning=key):
                self.assertTrue(any(term.casefold() in value.casefold() for term in alternatives),
                                f'{locale}: missing {key}: {alternatives!r}')

    def assert_disclosed(self, locale, field, sentence, text):
        with self.subTest(locale=locale, field=field):
            self.assertTrue(sentence, f'{locale}.{field}: missing source disclosure')
            self.assertIn(sentence, text, f'{locale}.{field}: disclosure not rendered here')

    def test_automatic_backup_is_plus_e2ee_unreadable_with_free_manual_paths_all_locales(self):
        for locale, expected, entry in self.each():
            text = entry.get('automaticBackup', '')
            with self.subTest(locale=locale):
                self.assertIn('Plus', text)
            # The Free plan is named with the term each locale's live copy already uses
            # (preservedFreePrefix); English and plan-name locales may use "Free" itself.
            self.concepts(locale, expected, text,
                          ('freePlan', 'e2ee', 'unreadable', 'consent', 'manual', 'export', 'import',
                           'reminder'))

    def test_ios_icloud_and_cloudkit_do_not_back_up_app_data_all_locales(self):
        for locale, expected, entry in self.each():
            text = entry.get('iosAppDataBackup', '')
            for token in ('iCloud', 'CloudKit'):
                with self.subTest(locale=locale, token=token):
                    self.assertIn(token, text)
            self.concepts(locale, expected, text, ('icloudUnused', 'appData', 'manual'))

    def test_android_os_drive_backup_requires_verified_active_plus_all_locales(self):
        for locale, expected, entry in self.each():
            text = entry.get('androidSystemBackup', '')
            for token in ('Google Drive', 'Auto Backup', 'Plus'):
                with self.subTest(locale=locale, token=token):
                    self.assertIn(token, text)
            # Owner backup_safety_completeness (2026-10-02 15:30): without verified Plus the run
            # is skipped so the previous backup stays; never an empty or partial backup. The
            # earlier "excluded together" mechanism is retracted.
            with self.subTest(locale=locale, stale='oldExcludedWithoutPlusSentence'):
                self.assertNotIn(expected['oldExcludedWithoutPlusSentence'], text)
            self.concepts(locale, expected, text,
                          ('verified', 'active', 'database', 'key', 'records', 'together',
                           'skip', 'unverifiable', 'noPartial', 'previousKept', 'existing',
                           'restore', 'googleAccount'))

    def test_server_backups_use_manual_predeploy_snapshot_not_weekly_snapshot(self):
        for locale, expected, entry in self.each():
            text = entry.get('serverBackup', '')
            with self.subTest(locale=locale):
                self.assertNotIn(expected['oldWeeklyServerSnapshotSentence'], text)
                self.assertRegex(text, r'(?<!\d)7(?!\d)')
                self.assertIn('Amazon S3', text)
            self.concepts(locale, expected, text, ('manual', 'preDeploy'))

    def test_ios_staged_policy_support_guide_and_plus_disclose_automatic_backup(self):
        for locale, _, text in self.each():
            entry = self.staged['ios-content.json']['locales'][locale]
            privacy = render_account_sync.sections(entry['privacy'])
            support = entry['support']
            targets = {
                'privacy.backups': joined(privacy['backups']['paragraphs']),
                'support.backup': joined(support['released']['backup']['answers']),
                'support.guide': support['guide']['steps'][5]['body'],
                'support.plus.features': joined(support['plus']['features']['answers']),
            }
            for where, value in targets.items():
                self.assert_disclosed(locale, where, text.get('automaticBackup', ''), value)
            for where in ('privacy.backups', 'support.backup'):
                self.assert_disclosed(locale, where, text.get('iosAppDataBackup', ''), targets[where])
            # Calendar iCloud/Google references remain legitimate. App-data Drive and the
            # other platform's/store's names must not leak from common backup scope.
            with self.subTest(locale=locale):
                self.assertNotRegex(json.dumps(entry, ensure_ascii=False),
                                    r'(?i)(?<![A-Za-z])(?:Android|Google\s+Play|Google\s+Drive|Auto\s+Backup)(?![A-Za-z])')

    def test_android_staged_policy_support_guide_and_plus_disclose_both_backup_paths(self):
        for locale, _, text in self.each():
            entry = self.staged['android-content.candidate.json']['locales'][locale]
            privacy = render_account_sync.sections(entry['privacy'])
            support = entry['support']
            faq = {item['id']: item for item in support['faq']}
            targets = {
                'privacy.backup': joined(privacy['backup']['paragraphs']),
                'support.backup': joined(faq['backup']['answers']),
                'support.guide': support['guide']['steps'][5]['body'],
                'support.plus.features': joined(faq['plus-features']['answers']),
            }
            for where, value in targets.items():
                self.assert_disclosed(locale, where, text.get('automaticBackup', ''), value)
                self.assert_disclosed(locale, where, text.get('androidSystemBackup', ''), value)

    def test_staged_terms_disclose_auto_backup_and_platform_data_backup_limits(self):
        for locale, _, text in self.each():
            terms = render_account_sync.sections(self.staged['terms-content.json']['locales'][locale])
            self.assert_disclosed(locale, 'terms.free-plus', text.get('automaticBackup', ''),
                                  joined(terms['free-plus']['paragraphs']))
            records = joined(terms['records']['paragraphs'])
            for key in ('automaticBackup', 'iosAppDataBackup', 'androidSystemBackup'):
                self.assert_disclosed(locale, 'terms.records.' + key, text.get(key, ''), records)

    def test_staged_android_retires_old_system_exclusion_and_custom_drive_claims(self):
        for locale, expected, _ in self.each():
            entry = self.staged['android-content.candidate.json']['locales'][locale]
            serialized = json.dumps(entry, ensure_ascii=False)
            for key in ('oldPrivacySystemExclusion', 'oldOnlyAutomaticDrive',
                        'oldFaqSystemExclusion', 'oldAndroidStorageDriveSentence'):
                with self.subTest(locale=locale, stale=key):
                    self.assertNotIn(expected[key], serialized)
            for old in expected['oldCustomDriveParagraphs']:
                with self.subTest(locale=locale, stale='customDriveParagraph'):
                    self.assertNotIn(old, serialized)

    def test_staged_commercial_copy_retires_blanket_free_backup_claims_both_platforms(self):
        for locale, expected, _ in self.each():
            for platform, name in (('ios', 'ios-content.json'),
                                   ('android', 'android-content.candidate.json')):
                entry = self.staged[name]['locales'][locale]
                source = expected[platform + 'CommercialSentences']
                serialized = json.dumps(entry, ensure_ascii=False)
                for key in ('oldFreeList', 'oldAllBackupsFree', 'oldNothingMovedToPlus'):
                    with self.subTest(locale=locale, platform=platform, stale=key):
                        self.assertNotIn(source[key], serialized)
                for tail in ('preservedPlusExpiryTail', 'preservedEarlierNoticeTail'):
                    for sentence in source[tail]:
                        with self.subTest(locale=locale, platform=platform, preserved=tail):
                            self.assertIn(sentence, serialized)

    def test_staged_earlier_answers_drop_nothing_moved_into_plus_claim_all_locales(self):
        # ko, ja and tr state the 1.0.5 "nothing is deleted or moved into Plus" promise as its
        # own sentence; the other 14 locales join it to the replaced free-feature sentence. On
        # Android it contradicts androidSystemBackup (OS Drive Auto Backup is Plus-only since the
        # 15:4x owner decision), and iOS drops it too so all 17 locales say the same thing.
        for locale, expected, entry in self.each():
            ios = self.staged['ios-content.json']['locales'][locale]
            android = self.staged['android-content.candidate.json']['locales'][locale]
            faq = {x['id']: x for x in android['support']['faq']}
            for platform, staged, answer, free in (
                    ('ios', ios, ios['support']['plus']['earlier']['answers'][1],
                     entry.get('freeFeatures', '')),
                    ('android', android, faq['plus-earlier']['answers'][1],
                     entry.get('androidFreeFeatures', ''))):
                claim = expected[platform + 'CommercialSentences']['oldStandaloneNothingMovedToPlus']
                with self.subTest(locale=locale, platform=platform):
                    self.assertTrue(claim)
                    self.assertTrue(free)
                    self.assertTrue(answer.startswith(free), f'{locale}.{platform}: free list not first')
                    self.assertNotIn(claim, answer)
                    self.assertNotIn(claim, json.dumps(staged, ensure_ascii=False))

    def test_manual_crypto_recovery_and_validated_restore_details_remain(self):
        for locale, expected, _ in self.each():
            android = self.staged['android-content.candidate.json']['locales'][locale]
            privacy = joined(render_account_sync.sections(android['privacy'])['backup']['paragraphs'])
            faq = next(x for x in android['support']['faq'] if x['id'] == 'backup')
            for key in ('preservedManualPolicySentences', 'preservedManualPolicyParagraphs'):
                for sentence in expected[key]:
                    with self.subTest(locale=locale, preserved=key):
                        self.assertIn(sentence, privacy)
            for sentence in expected['preservedManualFaqSentences']:
                with self.subTest(locale=locale, preserved='manualFaq'):
                    self.assertIn(sentence, faq['answers'][0])
            ios = self.staged['ios-content.json']['locales'][locale]
            with self.subTest(locale=locale, preserved='iosManualBackup'):
                self.assertIn(expected['preservedIosManualPolicy'],
                              joined(render_account_sync.sections(ios['privacy'])['backups']['paragraphs']))
            for answer in expected['preservedIosManualFaq']:
                with self.subTest(locale=locale, preserved='iosManualFaq'):
                    self.assertIn(answer, joined(ios['support']['released']['backup']['answers']))

    def test_legacy_sources_and_price_trial_rights_contract_stay_unchanged(self):
        for name, digest in self.fixture['legacySourceSha256'].items():
            with self.subTest(source=name):
                self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)
        for name, digest in self.fixture['canonicalWithoutAwsTimingMethodSha256'].items():
            source = load(name)
            for entry in source['locales'].values():
                for section in entry['privacy']['legalSupplement']['sections']:
                    for row in section.get('table', {}).get('rows', []):
                        if row['id'] == 'aws':
                            row['cells']['timingMethod'] = 'LATE2_OWNED_AWS_TIMING_METHOD'
            normalized = json.dumps(source, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')) + '\n'
            with self.subTest(source=name, owned='AWS timingMethod only'):
                self.assertEqual(hashlib.sha256(normalized.encode()).hexdigest(), digest)

    def test_automatic_backup_decision_stays_operationally_gated(self):
        self.assertTrue(self.candidate['serverReadiness'])
        self.assertTrue(all(value is False for value in self.candidate['serverReadiness'].values()))
        self.assertEqual(self.candidate['status'], 'pre-release-candidate-not-published')
        pending = joined(self.candidate['unresolvedBeforePublication'])
        for token in ('Google Drive Auto Backup', 'iCloud', 'CloudKit', 'verified Plus',
                      'skips', 'empty or partial', 'bmgr'):
            with self.subTest(requirement=token):
                self.assertIn(token, pending)
        with self.subTest(retracted='pending exclusion mechanism'):
            self.assertNotIn('excludes the complete set otherwise', pending)
        operations = (ROOT / 'docs/LEGAL_OPERATIONS_1_0_6.md').read_text()
        for token in ('end-to-end encrypted', 'server cannot read', 'Google Drive Auto Backup',
                      'verified Plus', 'iCloud', 'CloudKit', 'existing backups', 'restore',
                      'skip the backup run', 'previous backup', 'empty or partial', 'bmgr'):
            with self.subTest(operation=token):
                self.assertIn(token, operations)
        with self.subTest(retracted='operations exclusion mechanism'):
            self.assertNotIn('exclude the database, keys and records together', operations)

    def test_app_managed_drive_backup_blocks_publication_until_removed_or_disclosed(self):
        # apps/google release/1.0.6 still ships the 1.0.5 app-managed Drive appDataFolder backup
        # (CloudBackupService, DriveAppDataApi), but the staged 1.0.6 Android copy no longer
        # describes it and no owner decision retires it (OQ-L2-1). Publication must stay blocked
        # until the build drops it or the copy discloses it.
        key = 'appManagedDriveBackupDecided'
        pending = joined(self.candidate['unresolvedBeforePublication'])
        operations = (ROOT / 'docs/LEGAL_OPERATIONS_1_0_6.md').read_text(encoding='utf-8')
        for token in ('CloudBackupService', 'appDataFolder', 'OQ-L2-1', key,
                      'removed from the 1.0.6 build or disclosed before publication'):
            with self.subTest(source='unresolvedBeforePublication', token=token):
                self.assertIn(token, pending)
            with self.subTest(source='LEGAL_OPERATIONS_1_0_6.md', token=token):
                self.assertIn(token, operations)
        with self.subTest(stale='feature called retired without a decision'):
            self.assertNotIn('retired app-managed Drive-folder disclosure', operations)
        self.assertIn(key, account_sync_candidate.SERVER_READINESS_TOKENS)
        self.assertIs(self.candidate['serverReadiness'].get(key), False)
        self.assertEqual([e for e in account_sync_candidate.transfer_disclosure_errors(self.candidate)
                          if e.startswith('serverReadiness')], [])
        ready = copy.deepcopy(self.candidate)
        ready.update(status='integrated-and-verified', unresolvedBeforePublication=[])
        ready['serverReadiness'] = {name: True for name in self.candidate['serverReadiness']}
        ready['serverReadiness'][key] = False
        with self.assertRaisesRegex(AssertionError, key):
            account_sync_candidate.require_release_ready(ready)
        del ready['serverReadiness'][key]
        with self.assertRaisesRegex(AssertionError, key):
            account_sync_candidate.require_release_ready(ready)


if __name__ == '__main__':
    unittest.main()
