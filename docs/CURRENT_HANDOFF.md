# Website handoff — canonical pointer

Read the [canonical current handoff](../../release/CURRENT_HANDOFF.md) first, then the
[workspace entry](../../START_HERE.md) and relevant [release journal](../../release/release-journal.json) entries.
These are the single source for recorded live status, repository identities, evidence and
the current owner stop. This file does not duplicate counts, HEADs or executable next steps.

## Status (2026-09-29)

- The site serves help and privacy pages from `main` via GitHub Pages at
  <https://doseweek-legal.wonyoungchoi.dev/>. PR #4 (merge `40d0359`, 2026-09-24) and PR #6
  (merge `efaf1ff`, 2026-09-28) are merged; `LICENSE` was added in `8b53cf0` (2026-09-28).
  On 2026-09-29 the live `/`, `/privacy/`, `/support/`, `/android/privacy/` and
  `/android/support/` pages matched the files on `main` at `8b53cf0` byte for byte.
- iOS 1.0.5 (build 19) is live on the App Store since 2026-09-29.
- Android 1.0.5 (versionCode 13) is being submitted to Google Play on 2026-09-29. It is not
  live yet. The site already states the Android 14 minimum for versionCode 13.
- 1.0.6 planning for both apps: [release/1.0.6/HANDOFF-1.0.6.md](../../release/1.0.6/HANDOFF-1.0.6.md)
  (being prepared on 2026-09-29).
- Per-language URLs (1.0.6 search work, 2026-09-29): 119 static pages `/<locale>/<route>/` (7 routes x 17 locales)
  with hreflang + x-default on all 126 pages and a sitemap with alternates; the hash pages (`/privacy/#ko`)
  stay canonical and keep working. Receipt: `release/evidence/1.0.6/W0/`.
- Branch and PR tidy: `release/evidence/lean-20260923/workspace-cleanup-20260923/repo-tidy-20260929-website.json`.

## Monetization candidate (2026-09-29, not published)

- Branch `claude/doseweek-free-ads-plus-himvw9` holds candidate copy for the free download with
  ads and the Plus subscription (owner instruction 2026-09-29; binding policy
  `docs/MONETIZATION_POLICY.md` in both app repositories): iOS privacy sections 11 (ads) and 12
  (purchases), Android sections 5 (ads) and 6 (purchases), Plus and ads FAQ answers on both
  support pages, and the new Terms of Use route `/terms/` (`docs/terms-content.json`,
  `scripts/render_terms.py`). The live 1.0.5 apps have none of these features. Nothing is merged
  to `main`, pushed for publication or deployed.
- The new and changed fields are translated into the 15 locales other than en and ko (2026-09-29;
  no native-speaker review is claimed). The per-language titles and descriptions keep interim
  wording. The translated server-location and retention placeholders are registered in
  `legal_release.RELEASE_PLACEHOLDERS`; `check_site.py` keeps every locale's placeholder count
  equal to en.
- Local checks on 2026-09-29 after the translation: every renderer `--check`, `check_site.py`,
  `korean_tone.py` and the four unit-test modules pass. `check_site.py --release` fails by design
  (date not set).
- Review fixes (2026-09-29, findings 14, 15, 26 and 31; all 17 locales, no native-speaker review
  claimed): both ads sections (iOS 11, Android 5) list the overseas-transfer details of the Google
  Mobile Ads SDK and UMP (recipient Google LLC, Google Ireland Limited for the EEA and Switzerland,
  contact, countries, items, timing and method, purpose, retention, how to refuse) and state
  plainly that where Google shows no consent message, for example in Korea, neither Google nor
  DoseWeek offers a refusal, so Plus is the only way to avoid ad processing. No legal basis is
  named: the Korean consent question stays with counsel (monetization policy section 1.1). The
  Android ads section names the app set ID; the Android purchases section says the server confirms
  the purchase with Google Play (no on-device signature check in release builds); iOS section 12
  gained the retention placeholder, and `legal_release.purchase_placeholder_parity_errors` (run
  by `check_site.py`, tested in `scripts/test_monetization_copy.py`) keeps the two purchase
  sections' server placeholders aligned. The Android catalog and its 17 `privacy_policy.xml`
  files in DoseweekPlayStore were regenerated from the same candidate. Checks: every renderer
  `--check`, `check_site.py`, `korean_tone.py` and the five unit-test modules pass;
  `check_site.py --release` still fails by design.
- BLOCKED: (1) the owner sets `NEXT_RELEASE_EFFECTIVE_DATE` in `scripts/legal_release.py` and
  the matching dates in the three content files; (2) the purchase-verification server's location,
  operator and retention replace `legal_release.RELEASE_PLACEHOLDERS` in all 17 locales (Android
  section 6 and iOS section 12 both carry the location and the retention sentences); (3) the app
  version for the monetization release replaces the 1.0.5 page version; (4) app UI labels quoted
  here ("Privacy choices for ads", "Report an ad", "Restore purchases", "Settings > About >
  What's new", and their translations) are matched to the final app strings in each locale;
  (5) the owner and counsel review the Terms, the ads overseas-transfer details and the section
  1.1 items of the monetization policy; (6) native-speaker review of the translations (not done);
  (7) browser review of the new pages (not run).

## Historical (2026-09-23 to 2026-09-28)

The paragraph below described the state before PR #4 and PR #6 were merged. It is kept as
history, not as current status.

> Publication remains owner-paused. The candidate help, privacy and brand pages are not public-release proof. Preserve the existing draft and follow the canonical handoff for the ordered app-upload/publication boundary and remaining privacy operations. Local checks or an old live-page response do not authorize a new deployment.

The [previous local handoff](../../release/evidence/lean-20260923/workspace-cleanup-20260923/repo-docs-before/website/docs/CURRENT_HANDOFF.md) is preserved as historical evidence only.
Do not run its old commands or treat its former next action as current authorization.
