"""Keep a planned account feature from silently becoming an effective public policy."""

import unittest

import account_sync_candidate


class AccountSyncCandidateTest(unittest.TestCase):
    def test_prior_buyer_fields_reach_only_related_staged_sections(self):
        import render_account_sync
        candidate = account_sync_candidate.load()
        for loc, entry in candidate['locales'].items():
            self.assertTrue(entry.get('priorBuyerClaimPrivacy'), loc)
            self.assertTrue(entry.get('priorBuyerClaimHelp'), loc)
        sources = render_account_sync.integrated_sources()
        for loc, entry in candidate['locales'].items():
            ios = sources['ios-content.json']['locales'][loc]
            android = sources['android-content.candidate.json']['locales'][loc]
            terms = sources['terms-content.json']['locales'][loc]
            ip = render_account_sync.sections(ios['privacy'])
            ap = render_account_sync.sections(android['privacy'])
            faq = {f['id']: f for f in android['support']['faq']}
            self.assertIn(entry['priorBuyerClaimPrivacy'], ip['purchases']['paragraphs'][0])
            self.assertIn(entry['priorBuyerClaimPrivacy'], '\n\n'.join(ap['purchases']['paragraphs']))
            self.assertIn(entry['priorBuyerClaimHelp'], '\n\n'.join(ios['support']['plus']['earlier']['answers']))
            self.assertIn(entry['priorBuyerClaimHelp'], '\n\n'.join(faq['plus-earlier']['answers']))
            self.assertIn(entry['legacyRights'], render_account_sync.sections(terms)['free-plus']['paragraphs'])
            self.assertNotIn(entry['priorBuyerClaimPrivacy'], entry['sync'])

    def test_prior_buyer_copy_preserves_off_and_separate_evidence_policy(self):
        candidate = account_sync_candidate.load()
        en = candidate['locales']['en']
        ko = candidate['locales']['ko']
        self.assertIn('currently unavailable', en['priorBuyerClaimHelp'])
        self.assertIn('현재 사용할 수 없어요', ko['priorBuyerClaimHelp'])
        for phrase in ('no order number or transaction proof', 'separate server encryption key',
                       'not the health-backup 30 days', 'none is presumed indefinite or anonymous'):
            self.assertIn(phrase, en['priorBuyerClaimPrivacy'])
        self.assertIn('approval does not deliver a code or activate Plus', en['priorBuyerClaimHelp'])
        self.assertIn('verified resulting subscription activates Plus', en['legacyRights'])
        self.assertNotIn('준비하고', ko['legacyRights'])
        self.assertNotIn('planned program', en['legacyRights'])
        self.assertIn('claim', '\n'.join(candidate['unresolvedBeforePublication']))

    def test_every_locale_has_the_full_draft_scope(self):
        candidate = account_sync_candidate.load()
        self.assertEqual(len(candidate["locales"]), 17)
        self.assertEqual(candidate["status"], "pre-release-candidate-not-published")

    def test_external_deletion_request_uses_existing_support_without_plus(self):
        candidate = account_sync_candidate.load()
        route = candidate.get("deletionRequest", {})
        self.assertEqual(route.get("method"), "support-email")
        self.assertEqual(route.get("supportEmail"), "wonyoung@wonyoungchoi.dev")
        self.assertIs(route.get("requiresPlus"), False)
        self.assertEqual(route.get("result"), "request-not-completed-erasure")

    def test_candidate_localizes_off_status_analytics_and_legacy_rights_review(self):
        candidate = account_sync_candidate.load()
        for locale, entry in candidate["locales"].items():
            for field in ("releaseStatus", "analytics", "legacyRights", "deletionTitle", "requestLabel"):
                self.assertTrue(entry.get(field), (locale, field))

    def test_staged_sources_reconcile_account_denials_without_a_date(self):
        import render_account_sync
        sources = render_account_sync.integrated_sources()
        self.assertTrue(all(d["effectiveDate"] is None for d in sources.values()))
        for d in sources.values():
            self.assertEqual(list(d["locales"]), list(account_sync_candidate.LOCALES))
        english = __import__("json").dumps(sources["android-content.candidate.json"]["locales"]["en"])
        self.assertFalse("no developer server for health records" in english)
        self.assertFalse("there is no DoseWeek account" in english)
        self.assertFalse("keeps no server copy" in english)
        self.assertFalse(account_sync_candidate.load()["legacyDecision"]["perpetualAdFreeGuaranteed"])

    def test_staged_ios_support_lead_replaces_legacy_account_denial(self):
        import json
        import render_account_sync
        c = account_sync_candidate.load()
        baseline = json.loads((render_account_sync.ROOT / "docs/ios-content.json").read_text())
        staged = render_account_sync.integrated_sources()["ios-content.json"]
        for loc in c["localeOrder"]:
            lead = staged["locales"][loc]["support"]["labels"]["lead"]
            old = baseline["locales"][loc]["support"]["labels"]["lead"]
            self.assertFalse(old in lead, f"{loc}: retained legacy account denial")
            self.assertIn(c["locales"][loc]["releaseStatus"], lead)
            self.assertIn(c["locales"][loc]["account"], lead)
        self.assertNotIn("There is no account or support dashboard", staged["locales"]["en"]["support"]["labels"]["lead"])
        self.assertNotIn("계정이나 지원용 관리 화면이 없어요", staged["locales"]["ko"]["support"]["labels"]["lead"])

    def test_staged_page_inventory_and_no_fabricated_effective_date(self):
        import render_account_sync
        c = account_sync_candidate.load()
        pages = render_account_sync.rendered_pages(render_account_sync.integrated_sources(), c)
        expected = {
            render_account_sync.ROOT / prefix / route / "index.html"
            for prefix in ("", *c["localeOrder"]) for route in render_account_sync.ROUTES
        }
        self.assertEqual(set(pages), expected)
        for path, markup in pages.items():
            self.assertIn('name="robots" content="noindex,nofollow"', markup)
            self.assertNotIn('datetime="None"', markup)
            self.assertIn("account/delete/", markup)
            loc = path.relative_to(render_account_sync.ROOT).parts[0]
            locales = [loc] if loc in c["locales"] else c["localeOrder"]
            for loc in locales:
                self.assertIn(__import__("html").escape(c["locales"][loc]["releaseStatus"]), markup)

    def test_external_deletion_locales_provide_email_and_separate_outcomes(self):
        import render_account_sync
        c = account_sync_candidate.load()
        for loc in c["localeOrder"]:
            panel = render_account_sync.deletion_panel(c, loc)
            self.assertIn("mailto:wonyoung@wonyoungchoi.dev?subject=DoseWeek+account+deletion+request", panel)
            self.assertIn(__import__("html").escape(c["locales"][loc]["webDeletion"]), panel)
            self.assertIn(__import__("html").escape(c["locales"][loc]["retention"]), panel)
            self.assertIn('dir="rtl"' if loc == "ar" else 'dir="ltr"', panel)

    def test_release_gate_refuses_unintegrated_candidate(self):
        with self.assertRaisesRegex(AssertionError, "pre-release candidate"):
            account_sync_candidate.require_release_ready()


if __name__ == "__main__":
    unittest.main()
