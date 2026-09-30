# Website handoff — canonical pointer

## Now (2026-09-30) — account, encrypted sync and announcement disclosure draft

- Latest owner decision: a server-verified Apple or Google Plus purchase linked to the same
  DoseWeek account shares **all** Plus benefits across iOS and Android (ad removal, Plus tools
  and encrypted sync), while each app retains its native store purchase path. The unpublished
  17-locale account candidate now adds the ad-removal/tools disclosure. The owner also chose
  in-app prior-buyer application and purchase verification, then an individual one-month code
  that renews as **monthly Plus** after the free month unless canceled. The review draft records
  the price/period/date/cancellation disclosure requirement. Candidate source validator
  **PASSed 17/17 locales**, focused unit tests **PASSed 2/2**, and `git diff --check` PASSed;
  candidate source SHA-256 is `213d6d90872bbcec0e59940ead34ff1849911b1c54b9db08e82c2ac750ba8acb`.
  Generated public pages and their renderer inputs are unchanged, so the prior 144/144 site
  PASS remains input-matched; no new live/browser/native check ran. No public page or store
  offer changed. Source/review were committed at `d3bb6983` and pushed on the same draft
  branch. PR #11's description was appended without replacing its earlier text and read back
  exactly while open/draft, with the remote head matching the pushed branch. This follow-on
  handoff checkpoint records the final state; a further doc-only commit does not change the
  candidate source or invalidate the focused checks. **Next action:** once server/native account
  and store-offer behavior is proved, reconcile the effective 17-locale privacy, Terms and help
  sources, generate the working deletion route, settle the effective date/store declarations
  and run the release gate. Counsel and native-speaker review remain.
- Owner scope for 1.0.6: optional Apple/Google/Kakao sign-in, Plus-only automatic encrypted
  records/settings sync across iOS and Android under one DoseWeek account, a recovery code
  needed on a new device, 30-day encrypted-backup retention after Plus expiry, account deletion,
  and public start-up notices before onboarding with a per-notice one-week snooze. The planned
  API and notice feed are under `doseweek.wonyoungchoi.dev`; neither is deployed as a DoseWeek
  service. The account-deletion web path is only planned.
- `docs/account-sync-content.candidate.json` is a separate five-topic, 17-locale **unpublished**
  candidate (account, sync, retention, announcement, deletion web copy). It does not replace the
  current generated pages, which still describe the existing no-account apps.
  `docs/ACCOUNT_SYNC_RELEASE_REVIEW.md` has the store privacy/Data safety and account-deletion
  release draft, source conflicts and primary sources. `scripts/account_sync_candidate.py` validates coverage and
  `check_site.py --release` now refuses an unintegrated candidate, in addition to the existing
  date/server gates. Source SHA and exact dirty files are in
  `release/evidence/1.0.6/legal-sync-candidate-20260930/receipt.json`.
- The 2026-09-30 contract reconciliation fixes the planned API base to `/v1` and keeps the
  public static announcement feed at `/announcements/v1.json`. The candidate's unresolved list
  now names the closed Plus sync gate, missing shared record graph/merge and unpublished feed.
  `docs/ACCOUNT_SYNC_RELEASE_REVIEW.md` distinguishes those targets from implemented features;
  it also records the owner's in-app prior-buyer claim and verification decision. Apple signed
  AppTransaction and a proposed user-supplied Play order ID are design inputs; claim-data
  fields, retention, fraud checks and issuance remain unresolved, so no code is promised.
  The effective public pages were not regenerated from this draft.
  Contract receipt: `release/evidence/1.0.6/legal-sync-contract-20260930/receipt.json`.
- Verification: candidate source **PASS 17/17 locales**; focused tests **PASS 10/10**;
  `check_site.py` **PASS 144/144 generated pages** and Korean tone **PASS 1493 sentences,
  0 violations**; `git diff --check` **PASS**. Initial validator **FAIL** because it required
  the English spelling of Kakao in Korean/Japanese; logs are preserved and the narrow related
  family passed after accepting localized names. `check_site.py --release` is **BLOCKED** by the
  unset effective date; the new unintegrated-candidate refusal has a passing unit test. Native,
  browser, live API and account deletion flow are **NOT_RUN**. Logs and source hashes are in the
  receipt above. No owned process/device, publication, console change or production deployment.
  **Next action:** after the native/API contract is verified, replace conflicting effective
  privacy/terms/help sources in all 17 locales, generate the deletion route and pages, then
  verify store declarations and run the release gate. Counsel and native-speaker review remain.
- The prior source `25e9c95` and handoff `6cbb04e` commits are on local and remote
  `claude/doseweek-free-ads-plus-himvw9`. The contract edit's source validator **PASSed 17/17
  locales** and focused tests **PASSed 2/2**; `git diff --check` PASSed. The previous 144-page
  site PASS is reusable because generated pages, renderers and site-check inputs are unchanged;
  no new browser or native check ran. The release gate remains BLOCKED by the unset date and
  unintegrated candidate. The one-month-code claim-data addition passed the same focused 17/17
  validator, 2/2 tests and diff check. Source commits `db177ad` and `9da5a47` were pushed.
  PR #11 is open/draft; its head matched local and remote `9da5a47` and its description was
  read back exactly after updating the unpublished account/sync draft and in-app promo design.
  No merge or publication. **Next action:** after the server and native contracts are verified,
  replace conflicting effective 17-locale privacy, Terms and help sources, generate the working
  deletion route, settle the effective date and store declarations, then run the release gate.

Read the [canonical current handoff](../../release/CURRENT_HANDOFF.md) first, then the
[workspace entry](../../START_HERE.md) and relevant [release journal](../../release/release-journal.json) entries.
These are the single source for recorded live status, repository identities, evidence and
the current owner stop. This file does not duplicate counts, HEADs or executable next steps.

## Open owner questions (2026-09-30)

- The owner chose to include free + ads + Plus in 1.0.6. The release effective date is still
  unset, and the app/page version fields still describe 1.0.5; the release coordinator must
  align them with the final 1.0.6 builds before publication.
- The purchase-verification server's location, operator and retention, the Korean ad-data
  overseas-transfer basis, the Terms and ad-transfer legal review, and the final UI-label and
  native-speaker reviews remain open. `check_site.py --release` must keep failing until the
  date and registered server placeholders are resolved.
- The owner chose in-app application and prior paid-app purchase verification before individual
  one-month code delivery, followed by monthly Plus auto-renewal unless canceled. Eligibility,
  fraud controls, actual store price and offer configuration, and issuance are unresolved; no
  candidate page promises an issued code.

## Now (2026-09-30) — 1.0.6 rewarded-ad copy candidate

- On `claude/doseweek-free-ads-plus-himvw9`, commit `c97f8582` records the 17-locale iOS,
  Android and Terms sources now describe one earned reward adding 24 hours, no more than two
  in a rolling 24 hours, at most 48 hours remaining, and another offer only when at most
  24 hours remain. The help and Terms copy explains the five-minute clock-rollback pause and
  that automatic ads and Plus offers are hidden during the pass. The privacy copy replaces
  the old 30-minute record and describes local reward times, expiry and last-observed device
  time. The existing earned-reward and early-close conditions remain. No effective date or
  server placeholder was filled. Sources: `docs/{ios-content.json,android-content.candidate.json,
  terms-content.json}`; renderer guard and regression test:
  `scripts/{render_terms.py,test_monetization_copy.py}`; 90 generated HTML pages updated.
- Source SHA-256: iOS `507576784ad768917d2c8c19c8f028fcd63a98aa9f6442b60c73b30c89e76ece`,
  Android `98da96328b7ccea419704accd8f22fc6c98d9befafd86a98fe171d3d28a5857b`,
  Terms `e6774ee2263ad58ec754ff2226345c860c7598d92390c882da39ca1ca2e0e16e`.
  The six renderer `--check` commands PASS; `check_site.py` PASS (144 pages);
  `korean_tone.py` PASS (0 violations); the five listed unit modules PASS (105 tests);
  `git diff --check` PASS. The release coordinator preserved the logs and hashes in
  `release/evidence/1.0.6/monetization-integration-20260930/legal/receipt.json`.
  The complete six-renderer log was recaptured with identical inputs and preserved at
  `release/evidence/1.0.6/monetization-integration-20260930/legal/render-checks-complete.log` (SHA-256
  `138d675304d118e9b3ff91599ad5c47008ef043be3876b3fcfc8d80bd3ae75a6`);
  the initial renderer log captured only the final sitemap command and is retained as partial
  evidence. `check_site.py --release` is BLOCKED by `NEXT_RELEASE_EFFECTIVE_DATE=None`;
  browser appearance review is NOT_RUN. These are source/render checks, not native app validation.
- No owned process or device. Commit `c97f8582` was pushed to the same branch and draft
  PR #11's description now records the new reward rules, verification results and blockers;
  it remains open and unmerged. The changed set was the three JSON sources, two Python files,
  this handoff and 90 generated HTML pages; no unrelated files were changed. GitHub Pages still
  serves `main`, so the candidate copy is not public.
- **Next action:** once the owner supplies the 1.0.6 effective date and verification-server
  location/operator/retention, replace the registered placeholders in all 17 locales and
  align the page versions; then complete counsel, app-string, native-speaker and browser
  reviews before the release gate. Do not merge or publish on the strength of local checks.

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
