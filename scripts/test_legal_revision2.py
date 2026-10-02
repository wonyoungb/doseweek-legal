"""Review-2 retirement and committed-copy parity regressions; offline only."""
import copy
import json
import unittest
from pathlib import Path

import account_sync_candidate
import render_account_sync

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / 'docs' / name).read_text(encoding='utf-8'))


class LegalRevision2Test(unittest.TestCase):
    def test_all_locales_keep_free_features_and_rights_without_special_offer(self):
        anchors = json.loads((ROOT / 'scripts/fixtures/legal_revision2_rights_anchors.json').read_text())
        candidate = load('account-sync-content.candidate.json')
        terms = load('terms-content.json')
        self.assertEqual(set(anchors), set(candidate['localeOrder']))
        staged = render_account_sync.integrated_sources()
        for locale, expected in anchors.items():
            ios = staged['ios-content.json']['locales'][locale]
            android = staged['android-content.candidate.json']['locales'][locale]
            faq = {f['id']: f for f in android['support']['faq']}
            canonical = render_account_sync.sections(terms['locales'][locale])['free-plus']['paragraphs'][1]
            fields = {
                'candidate': candidate['locales'][locale]['legacyRights'],
                'canonicalTerms': canonical,
                'stagedTerms': render_account_sync.sections(staged['terms-content.json']['locales'][locale])['free-plus']['paragraphs'][1],
                'stagedIosPolicy': render_account_sync.sections(ios['privacy'])['purchases']['paragraphs'][0],
                'stagedIosHelp': '\n'.join(ios['support']['plus']['earlier']['answers']),
                'stagedAndroidPolicy': '\n'.join(render_account_sync.sections(android['privacy'])['purchases']['paragraphs']),
                'stagedAndroidHelp': '\n'.join(faq['plus-earlier']['answers']),
            }
            for field, text in fields.items():
                for meaning, anchor in expected.items():
                    with self.subTest(locale=locale, field=field, meaning=meaning):
                        self.assertIn(anchor, text)

    def test_prior_buyer_grant_and_claim_code_program_are_retired(self):
        candidate = load('account-sync-content.candidate.json')
        self.assertIs(candidate['legacyDecision'].get('separatePriorBuyerGrantOffered'), False)
        self.assertIs(candidate['legacyDecision'].get('priorBuyerClaimProgramRetired'), True)
        for loc, entry in candidate['locales'].items():
            with self.subTest(locale=loc):
                self.assertNotIn('priorBuyerClaimPrivacy', entry)
                self.assertNotIn('priorBuyerClaimHelp', entry)
        pending = '\n'.join(candidate['unresolvedBeforePublication'])
        self.assertNotIn('application/status/appeal', pending)
        self.assertNotIn('claim-evidence', pending)
        self.assertIn('prior paid-ad-free purchase', pending)

    def test_retired_claim_collection_has_no_active_release_workflow(self):
        text = (ROOT / 'docs/ACCOUNT_SYNC_RELEASE_REVIEW.md').read_text()
        self.assertIn('claim/code program is retired', text)
        for stale in ('Applications remain unavailable until',
                      'Only after application gates pass',
                      'one-month Plus→monthly auto-renewal contract becomes operative'):
            self.assertNotIn(stale, text)
        self.assertIn('subscription lookup', text)
        self.assertIn('consumer rights remains a release blocker', text)

    def test_commercial_copy_parity_is_a_distinct_closed_release_gate(self):
        candidate = load('account-sync-content.candidate.json')
        self.assertIn('commercialCopyParityVerified', candidate['serverReadiness'])
        self.assertIs(candidate['serverReadiness'].get('commercialCopyParityVerified'), False)
        self.assertIn('commercialCopyParityVerified', account_sync_candidate.SERVER_READINESS_TOKENS)
        ready = copy.deepcopy(candidate)
        ready.update(status='integrated-and-verified', unresolvedBeforePublication=[])
        ready['serverReadiness'] = {key: True for key in candidate['serverReadiness']}
        ready['serverReadiness']['commercialCopyParityVerified'] = False
        with self.assertRaisesRegex(AssertionError, 'commercialCopyParityVerified'):
            account_sync_candidate.require_release_ready(ready)
        del ready['serverReadiness']['commercialCopyParityVerified']
        with self.assertRaisesRegex(AssertionError, 'commercialCopyParityVerified'):
            account_sync_candidate.require_release_ready(ready)

    def test_parity_receipts_and_coordination_keep_required_price_and_real_blocker(self):
        path = ROOT / 'docs/COMMERCIAL_COPY_PARITY_1_0_6.json'
        self.assertTrue(path.is_file(), 'matching committed partner evidence must be recorded')
        receipt = json.loads(path.read_text())
        self.assertEqual(receipt.get('requiredPriceWording'), 'store-price')
        self.assertNotIn('requiredKoreaAnnual', receipt)
        self.assertEqual(receipt['websitePriceWording'], 'store-price')
        self.assertEqual(receipt['status'], 'BLOCKED_PARTNER_CHECK_RECEIPTS')
        self.assertIn('late owner decisions', receipt['authority'])
        for partner in receipt['partners'].values():
            self.assertRegex(partner['head'], r'^[0-9a-f]{40}$')
            self.assertRegex(partner['policySha256'], r'^[0-9a-f]{64}$')
        self.assertIn('store-returned', receipt['nativePriceRule'])
        for item in ('policy', 'review copy', 'verification inputs', 'committed receipts'):
            self.assertIn(item, receipt['nextAction'])


if __name__ == '__main__':
    unittest.main()
