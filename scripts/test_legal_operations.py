"""Release evidence for legal operations, separate from published-copy assertions."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class LegalOperationsTest(unittest.TestCase):
    def procedure(self):
        path = ROOT / 'docs/LEGAL_OPERATIONS_1_0_6.md'
        return path.read_text() if path.exists() else ''

    def test_breach_procedure_covers_sdk_disclosure_and_separate_clocks(self):
        text = self.procedure()
        for requirement in ('unauthorized SDK disclosure', 'PIPC/KISA', '72 hours',
                            '60 calendar days', '500', 'calendar year',
                            'media', 'substitute notice', 'discovery time',
                            'ciphertext', 'metadata', 'FTC', 'GDPR'):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, text)

    def test_backup_procedure_requires_physical_deletion_not_only_lifecycle(self):
        text = self.procedure()
        for requirement in ('S3', 'object versions', 'replicas', 'temporary exports',
                            'manual pre-deploy', '7 days', 'deletion ledger',
                            'restore', 'lifecycle alone', 'actual deletion'):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, text)

    def test_release_readiness_cannot_omit_new_legal_gates(self):
        source = json.loads((ROOT / 'docs/account-sync-content.candidate.json').read_text())
        flags = source.get('serverReadiness', {})
        for flag in ('processorInventoryVerified', 'healthConsentVerified',
                     'salesRegionExclusionsVerified', 'breachProcedureOperational',
                     'regionalSubscriptionNoticesVerified', 'consumerHealthRightsVerified'):
            with self.subTest(flag=flag):
                self.assertIn(flag, flags)
                self.assertIs(flags.get(flag), False,
                              'Copy drafting is not operational/provider proof')


if __name__ == '__main__':
    unittest.main()
