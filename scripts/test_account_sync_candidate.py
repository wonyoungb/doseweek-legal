"""Keep a planned account feature from silently becoming an effective public policy."""

import unittest

import account_sync_candidate


class AccountSyncCandidateTest(unittest.TestCase):
    def test_every_locale_has_the_full_draft_scope(self):
        candidate = account_sync_candidate.load()
        self.assertEqual(len(candidate["locales"]), 17)
        self.assertEqual(candidate["status"], "pre-release-candidate-not-published")

    def test_release_gate_refuses_unintegrated_candidate(self):
        with self.assertRaisesRegex(AssertionError, "pre-release candidate"):
            account_sync_candidate.require_release_ready()


if __name__ == "__main__":
    unittest.main()
