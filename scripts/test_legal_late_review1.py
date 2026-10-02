"""Review-1: permitted store-price copy, with no numeric-price conflict or lost trial rights."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

import render_account_sync
import render_terms

ROOT = Path(__file__).resolve().parents[1]
CURRENCY_PRICE = r'(?:USD|KRW|JPY|[$₩¥])\s*\d'


def fixture():
    return json.loads((ROOT / 'scripts/fixtures/legal_late_review1_store_prices.json').read_text())


def offer(entry):
    return next(s for s in entry['sections'] if s['id'] == 'free-plus')['paragraphs'][2]


class LegalLateReview1Test(unittest.TestCase):
    def test_all_locales_use_store_price_without_numeric_conflict(self):
        terms, _ = render_terms.load()
        anchors = fixture()
        self.assertEqual(set(anchors), set(terms['localeOrder']))
        staged = render_account_sync.integrated_sources()['terms-content.json']
        for stage, source in (('canonical', terms), ('staged', staged)):
            for locale, entry in source['locales'].items():
                with self.subTest(stage=stage, locale=locale):
                    self.assertNotRegex(offer(entry), CURRENCY_PRICE)
                    self.assertTrue(offer(entry).startswith(anchors[locale]['storePricePrefix']))

    def test_store_price_edit_preserves_trial_suffix_exactly(self):
        terms, _ = render_terms.load()
        for locale, anchor in fixture().items():
            with self.subTest(locale=locale):
                text = offer(terms['locales'][locale])
                suffix = text[text.index(anchor['trialStart']):]
                self.assertEqual(hashlib.sha256(suffix.encode()).hexdigest(), anchor['trialSuffixSha256'])

    def test_renderer_accepts_store_price_in_each_locale(self):
        terms, ios = render_terms.load()
        for locale, anchor in fixture().items():
            candidate = copy.deepcopy(terms)
            section = next(s for s in candidate['locales'][locale]['sections'] if s['id'] == 'free-plus')
            text = section['paragraphs'][2]
            section['paragraphs'][2] = anchor['storePricePrefix'] + text[text.index(anchor['trialStart']):]
            with self.subTest(locale=locale):
                render_terms.validate(candidate, ios)

    def test_renderer_rejects_reintroduced_price_amounts(self):
        terms, ios = render_terms.load()
        for locale in terms['localeOrder']:
            for price in ('USD 1.99', 'USD 13.99', 'KRW 3,300', 'KRW 19,900', 'JPY 300', 'JPY 1,980', 'KRW 22,000', 'KRW 2,900'):
                candidate = copy.deepcopy(terms)
                section = next(s for s in candidate['locales'][locale]['sections'] if s['id'] == 'free-plus')
                section['paragraphs'][2] += ' ' + price
                with self.subTest(locale=locale, price=price):
                    with self.assertRaises(AssertionError):
                        render_terms.validate(candidate, ios)

    def test_parity_record_uses_store_price_and_keeps_receipt_gate_closed(self):
        record = json.loads((ROOT / 'docs/COMMERCIAL_COPY_PARITY_1_0_6.json').read_text())
        self.assertEqual(record.get('websitePriceWording'), 'store-price')
        self.assertEqual(record['requiredKoreaAnnual'], 'KRW 19,900')
        self.assertEqual(record['status'], 'BLOCKED_PARTNER_CHECK_RECEIPTS')
        self.assertFalse(record['publicationAuthorized'])
        candidate = json.loads((ROOT / 'docs/account-sync-content.candidate.json').read_text())
        self.assertIs(candidate['serverReadiness']['commercialCopyParityVerified'], False)
        for item in ('store price', 'policy', 'review copy', 'verification inputs', 'committed receipts'):
            self.assertIn(item, record['nextAction'])


if __name__ == '__main__':
    unittest.main()
