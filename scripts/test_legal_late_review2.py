"""Review-2: one price-agnostic contract across active legal coordination."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMERIC_PRICE = r'(?:USD|KRW|JPY|[$₩¥])\s*\d'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


class LegalLateReview2Test(unittest.TestCase):
    def test_coordination_has_store_price_contract_without_numeric_authority(self):
        record = load('docs/COMMERCIAL_COPY_PARITY_1_0_6.json')
        self.assertNotIn('requiredKoreaAnnual', record)
        self.assertEqual(record.get('requiredPriceWording'), 'store-price')
        # Partner snapshots are historical receipts, not current price authority.
        active = {k: v for k, v in record.items() if k != 'partners'}
        self.assertNotRegex(json.dumps(active, ensure_ascii=False), NUMERIC_PRICE)
        self.assertNotIn('exact final late-owner prices', record['nextAction'])
        self.assertIn('store price', record['nextAction'])
        self.assertIn('store-returned', record['nativePriceRule'])
        self.assertEqual(record['status'], 'BLOCKED_PARTNER_CHECK_RECEIPTS')
        self.assertIs(record['publicationAuthorized'], False)

    def test_operations_use_store_price_and_preserve_subscription_safeguards(self):
        text = (ROOT / 'docs/LEGAL_OPERATIONS_1_0_6.md').read_text()
        self.assertNotRegex(text, NUMERIC_PRICE)
        self.assertIn('store price', text)
        for safeguard in ('one calendar month', 'first-time subscribers', 'auto-renews',
                          'cancelled any time in the store', 'Store-returned',
                          'commercialCopyParityVerified', 'stays false'):
            self.assertIn(safeguard, text)

    def test_release_provenance_has_no_numeric_store_configuration_authority(self):
        release = load('legal-release-map.json')['legalUpdate106']
        self.assertNotRegex(release['subscription'], NUMERIC_PRICE)
        self.assertIn('store price', release['subscription'])
        for meaning in ('monthly/annual', 'full local price', 'taxes', 'before purchase',
                        '1-calendar-month', 'auto-renewal', 'cancel any time', 'store-returned'):
            self.assertIn(meaning, release['subscription'])
        self.assertIsNone(release['effectiveDate'])
        self.assertIn('commercialCopyParityVerified=false', release['commercialCopyParity'])

    def test_account_blocker_requires_store_price_and_keeps_all_readiness_closed(self):
        candidate = load('docs/account-sync-content.candidate.json')
        blocker = next(s for s in candidate['unresolvedBeforePublication']
                       if 'COMMERCIAL_COPY_PARITY_1_0_6.json' in s)
        self.assertNotIn('exact final late-owner prices', blocker)
        self.assertNotRegex(blocker, NUMERIC_PRICE)
        self.assertIn('store price', blocker)
        for meaning in ('policy', 'review copy', 'verification inputs', 'committed receipts',
                        'partner checks', 'store-returned'):
            self.assertIn(meaning, blocker)
        self.assertTrue(candidate['serverReadiness'])
        self.assertTrue(all(value is False for value in candidate['serverReadiness'].values()))


if __name__ == '__main__':
    unittest.main()
