"""Keep a planned account feature from silently becoming an effective public policy."""

import json
import unittest

import account_sync_candidate


class AccountSyncCandidateTest(unittest.TestCase):
    def test_sign_in_providers_are_apple_and_google_only(self):
        # Owner decision 2026-10-01: Kakao login is dropped. Read the raw source so the check
        # does not depend on load() accepting it.
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(account_sync_candidate.retired_provider_mentions(raw), [])
        for locale, entry in raw["locales"].items():
            for provider in account_sync_candidate.SIGN_IN_PROVIDERS:
                self.assertIn(provider, entry["account"], locale)

    def test_live_and_staged_legal_sources_name_no_retired_provider(self):
        import render_account_sync
        self.assertEqual(account_sync_candidate.retired_provider_errors(), [])
        staged = render_account_sync.integrated_sources()
        hits = {name: account_sync_candidate.retired_provider_mentions(source)
                for name, source in staged.items()}
        self.assertEqual({name: found for name, found in hits.items() if found}, {})

    def test_retired_provider_detector_covers_localized_names(self):
        mentions = account_sync_candidate.retired_provider_mentions
        for text in ("Kakao", "KAKAO", "카카오로 로그인", "カカオでログイン", {"kakaoId": 1}):
            self.assertTrue(mentions(text), text)
        self.assertEqual(mentions({"account": "Apple or Google", "n": 3, "list": ["Google"]}), [])

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

    def test_every_locale_names_operator_region_and_cloudflare_transfer(self):
        # Lane LEGAL-STORE: operator, AWS Lightsail ap-northeast-2 and the Cloudflare PIPA
        # transfer particulars, in every locale. Reads the raw source (load() may lag behind).
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        for locale in account_sync_candidate.LOCALES:
            hosting = raw["locales"][locale].get(account_sync_candidate.HOSTING_FIELD, "")
            for token in (*account_sync_candidate.HOSTING_TOKENS,
                          *account_sync_candidate.CLOUDFLARE_TRANSFER_LINKS):
                self.assertIn(token, hosting, locale)

    def test_retention_states_the_d8_and_backup_numbers(self):
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        self.assertEqual([e for e in account_sync_candidate.hosting_retention_errors(raw)
                          if ".retention:" in e or ".sync:" in e], [])

    def test_staged_privacy_sources_keep_no_release_placeholder(self):
        import render_account_sync
        self.assertEqual(account_sync_candidate.staged_placeholder_errors(
            render_account_sync.integrated_sources()), [])

    def test_sync_scope_is_checked_in_every_locale(self):
        # Review 2 (2026-10-02): the D1 record-kind scope was machine-checked in en/ko only.
        self.assertEqual(set(account_sync_candidate.SYNC_SCOPE), set(account_sync_candidate.LOCALES))
        for locale, terms in account_sync_candidate.SYNC_SCOPE.items():
            self.assertEqual(len(terms), 8, locale)

    def test_hosting_detector_rejects_a_placeholder_candidate(self):
        locales = {loc: {"processors": "The server location is listed before release.",
                         "retention": "Kept for 30 days.", "sync": "On iOS only."}
                   for loc in account_sync_candidate.LOCALES}
        errors = account_sync_candidate.hosting_retention_errors({"locales": locales})
        self.assertIn("en.processors: missing 'Cloudflare'", errors)
        self.assertIn("ko.retention: missing the 7-day figure", errors)
        self.assertIn("en.sync: missing 'both platforms' (full cross-platform scope)", errors)
        self.assertIn("ko.sync: missing '가져오기 기록' (full cross-platform scope)", errors)
        self.assertNotIn("en.retention: missing the 30-day figure", errors)
        # 17 or 70 days is not the 7-day figure.
        locales["en"]["retention"] = "Kept 30 days; backups 17 or 70 days."
        self.assertIn("en.retention: missing the 7-day figure",
                      account_sync_candidate.hosting_retention_errors({"locales": locales}))

    def test_candidate_addresses_german_and_dutch_readers_formally(self):
        # The Android in-app policy injects this copy, and the Android repository's
        # scripts/formal_address.txt (German Sie, Dutch u) rejects these informal words there.
        import re
        informal = {"de": ("du", "dir", "dich", "dein", "deine", "deinen", "deinem", "deiner", "deines"),
                    "nl": ("je", "jij", "jou", "jouw")}
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        found = {}
        for locale, words in informal.items():
            pattern = re.compile(r"\b(?:%s)\b" % "|".join(words), re.IGNORECASE)
            for field, text in raw["locales"][locale].items():
                if pattern.search(text):
                    found[f"{locale}.{field}"] = sorted(set(pattern.findall(text)))
        self.assertEqual(found, {})

    # Lane LEGAL-STORE round 2: findings of the two 2026-10-02 reviews.

    def test_cloudflare_transfer_covers_the_announcement_check_and_refuses_truthfully(self):
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        errors = account_sync_candidate.transfer_disclosure_errors(raw)
        self.assertEqual([e for e in errors if ".processors:" in e or ".notice:" in e], [])

    def test_sync_key_health_sync_and_kept_records_are_stated(self):
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        errors = account_sync_candidate.transfer_disclosure_errors(raw)
        self.assertEqual([e for e in errors if ".sync:" in e or ".healthSync:" in e
                          or ".retention:" in e or e.startswith("tr:")], [])

    def test_unshipped_server_and_client_paths_are_tracked_as_readiness(self):
        # D8 pruning (src/index.js passes no recheckPlus), DELETE /v1/sync/snapshot, both
        # reset-sync controls, the verifier host and the tombstone retention are not shipped or
        # decided: each needs a False flag with its own unresolved item.
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        self.assertIn("serverReadiness", raw)
        self.assertEqual(set(raw["serverReadiness"]), set(account_sync_candidate.SERVER_READINESS_TOKENS))
        for key in ("retentionRecheckWired", "syncResetRoute", "syncResetUiIos",
                    "syncResetUiAndroid", "verifierHostDecided", "tombstoneRetentionDecided"):
            self.assertIs(raw["serverReadiness"][key], False, key)
        self.assertEqual([e for e in account_sync_candidate.transfer_disclosure_errors(raw)
                          if e.startswith("serverReadiness")], [])
        unresolved = "\n".join(raw["unresolvedBeforePublication"])
        self.assertIn("src/index.js", unresolved)
        self.assertIn("ab92fcf6", unresolved)

    def test_release_gate_refuses_open_readiness_flags(self):
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        self.assertIn("serverReadiness", raw)
        ready = dict(raw, status="integrated-and-verified", unresolvedBeforePublication=[])
        with self.assertRaisesRegex(AssertionError, "serverReadiness"):
            account_sync_candidate.require_release_ready(ready)

    def test_staged_sources_carry_health_sync_and_the_pending_verifier_location(self):
        import render_account_sync
        self.assertEqual(account_sync_candidate.staged_disclosure_errors(
            render_account_sync.integrated_sources()), [])

    def test_pending_markers_are_distinct_from_release_placeholders(self):
        import legal_release
        for locale in account_sync_candidate.LOCALES:
            for marker in (legal_release.PENDING_VERIFIER_LOCATION[locale],
                           legal_release.PENDING_TOMBSTONE_RETENTION[locale]):
                self.assertEqual(legal_release.release_placeholders(marker), [], marker)
                self.assertEqual(legal_release.pending_release_markers(marker), [marker])
        self.assertEqual(legal_release.pending_release_markers(
            " ".join(legal_release.RELEASE_PLACEHOLDERS)), [])

    def test_transfer_detector_rejects_the_reviewed_false_refusal(self):
        raw = json.loads(account_sync_candidate.SOURCE.read_text(encoding="utf-8"))
        entry = dict(raw["locales"]["en"])
        entry["processors"] = (entry["processors"] + " "
                               + account_sync_candidate.RETIRED_TRANSFER_REFUSALS["en"])
        entry["notice"] = "A public announcement can be checked when the app opens."
        broken = dict(raw, locales={**raw["locales"], "en": entry})
        errors = account_sync_candidate.transfer_disclosure_errors(broken)
        self.assertIn("en.processors: false refusal (not signing in does not stop the announcement check)", errors)
        self.assertIn("en.notice: does not say the announcement request passes through Cloudflare", errors)

    def test_release_gate_refuses_unintegrated_candidate(self):
        with self.assertRaisesRegex(AssertionError, "pre-release candidate"):
            account_sync_candidate.require_release_ready()


if __name__ == "__main__":
    unittest.main()
