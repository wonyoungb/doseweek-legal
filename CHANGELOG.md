## 2026-10-02 — LATE2 review-1 fix (unpublished)

- Staged earlier answers in ko, ja and tr (both platforms) drop the 1.0.5 "nothing is deleted
  or moved into Plus" sentence, like the other 14 locales (RED `d8ed26d`, GREEN `286237f`).
- New publication blocker `serverReadiness.appManagedDriveBackupDecided`: the app-managed
  Drive appDataFolder backup must be removed from the 1.0.6 build or disclosed (OQ-L2-1;
  RED `baffda8`, GREEN `74534b5`).
- 222/222 tests and 13 light checks PASS; release check BLOCKED_EFFECTIVE_DATE. Never publish.

## 2026-10-02 — LATE2 automatic backup (unpublished)

- Staged 1.0.6 privacy/help/Terms in 17 locales: Plus automatic backup is the optional,
  separately consented E2EE server backup/sync; the server cannot read record contents.
- Android OS Google Drive Auto Backup only with verified active Plus; otherwise the run is
  skipped (never an empty or partial backup), the previous backup stays restorable, and the
  backup lives in the user's Google account. iOS uses no iCloud/CloudKit for app data.
- Free keeps manual file export/import and backup reminders; Android and iOS free lists keep
  their own feature names. Server backups: daily encrypted S3 Seoul archives plus one manual
  pre-deploy OS snapshot deleted within 7 days.
- Failing-first: REDs `cfc27f7`, `051b975`, `fa684a6` (+ test correction `e691a48`); GREENs
  `880184c`, `2cfbac8`. 220/220 tests and 13 light checks PASS; release check BLOCKED_EFFECTIVE_DATE.
- No owned job/device or external action. Never publish.

## 2026-10-02 — late review 2 (unpublished)

- Resume reviewed `3cbc050` for the single major internal price-authority inconsistency.
- Choose reviewer-permitted store-price wording; preserve histories and closed gates.
- Added four focused regressions; replaced two numeric authority assertions. AST compile PASS.
- RED `778ee01` parent replay: compile PASS; six exact methods/six assertion failures,
  zero errors/skips/omissions; raw evidence retained and owned /tmp worktree removed.

- GREEN active parity/operations/provenance/account blocker now use store-price only;
  partner snapshots, public pages, trial/statutory rights and closed gates preserved.
  Source fingerprint refreshed. Focused68 exact methods PASS, zero failures/errors/skips/omissions.
- Preservation audit PASS:162 pages, assets, product/locale/trial data, partner objects, histories
  and false gates unchanged; only one account blocker edited. Independent source audit PASS.
- Full208 exact methods/13 ordinary commands PASS; 260 frozen inputs/runtime match;
  release child exit1 BLOCKED_EFFECTIVE_DATE retained as failed.
- Final provenance selector PASS with full-map/relevant-field/runner hashes; full coverage reused
  only for matching other inputs. Source GREEN committed at `889feca451642f0f61199fb2d289b990ac37efb3`.
- Final report overwritten; readback/exact-ID/loghash/frozen260inputs/provenance/stamps/
  false-gates/price-agnostic validation PASS.
- Independent final report audit PASS:208/68/1GREEN and6RED identities/logs,260inputs plus
  final-map supplement, commit trailers/files,175preserved files and historical receipts agree.
  Price-agnostic report/readiness gates explicit; no actionable issue.
- Reporting-only completion records continuity/checkpoint/audit; final report HEAD/inventory
  refresh after commit. No owned job/device/tmp worktree/scratch or external action.

## 2026-10-02 — late review 1 (historical; unpublished)

- Resume clean reviewed `fe488a5`; fix its one major via permitted store-price public wording.
- Preserve fixed one-month trial/renewal/cancel/refund and all other legal content.
- Baseline/review input hashes and historical report retained in `late-review1/`; RED stage next.
- Added5-method regression and17-locale price/trial preservation fixture; all scripts AST parse PASS.
- RED `5447afa` committed first and proved on `fe488a5`:5exactmethods,4failed,
  154assertionfailures,0errors/skips/omissions; ASTcompilePASS,temporaryworktree removed.
- GREEN17leading price disclosures use store price; original trial suffixes and all other Terms
  fields preserved byte for byte. Validator/tests/blocker updated; partner gates remain closed.
- Focused6modules:33exactmethodsPASS,0failure/error/skip/omission; ASTcompilePASS.
- Terms rendererPASS;18affectedpages regenerated;sourcehashes refreshed;release date/flags unchanged.
- Interim204methods/13ordinarychecksPASS;releaseexit1BLOCKED_EFFECTIVE_DATE;259frozeninputs match.
  Independent audit requested preservation of the original bare retired-price guard; final check next.
- Restored original bare retired-price validator guard;currency and bare insertion tests retained.
- Final focused33methodsPASS,0fail/error/skip/omission;ASTcompilePASS; final full gates next.
- Independent final source/render/report-writer auditPASS;18generatedTerms match source/hashes.
  Interim coverage remains historical. Final204methods/13ordinarychecksPASS,259frozeninputs match;
  releaseexit1BLOCKED_EFFECTIVE_DATE remains failed;noownedjob/tmpworktree/scratch remains.
- SourceGREEN committed locally at `d7b04b78dfbf2f787eea2fd86d40403330fbbe3a`; report finalization next.
- Initial report-validator exit1 retained for valid empty diff-check log; parser narrowed to that
  successful command only. Product gates/hashes unchanged; report validation rerun next.
- Late report overwritten;exactidentity/loghash/frozeninput/stamp/readiness/readbackvalidationPASS
  at sourceGREEN;initialparserfailure preserved. Independent final report auditPASS:identities,
  hashes,REDproof,commits,files,checkpoint agree;reportfinalHEAD refresh aftercompletioncommit.
- No owned device, native, network, publication or other external action.

## 2026-10-02 — late owner decisions (historical; unpublished)

- Resume reviewed `a6a4e18` for final KRW19,900 annual reference and fixed1-month trial.
- All17 regional exclusions/no representative already implemented; retain safeguards and proof.
- Assertion-only RED committed at `6bf1fd5`; AST compile PASS; no product edits yet. No native, network or publication.
- RED immediateparent7methods/6failed/104assertions; supplemental pre-exclusion1method/36assertions.
  CompilePASS,0errors/skips/omissions; both detached worktrees removed.
- GREEN17price and33fixedmonth fields; other Terms fields preserved exactly.
- Focused63exactmethodsPASS; Terms rendererPASS,18affectedpages regenerated; sourcehashes refreshed.
- Final199methods/13ordinarycommandsPASS; releaseexit1BLOCKED_EFFECTIVE_DATE staysfailed.
  Site162/staged126pages; tone2078sentences,0violations,9existingexceptions.257frozeninputs/runtime match.
- Independent readonly17+33transform/18generatedTerms/sourcepreservationauditPASS.
- SourceGREEN committed locally at `b2afed9a270469d374cd6cc55518a1c33129470f`; reporting-only finalization next.
- Late report schema/readback/stamps/identity/loghash/frozeninput validationPASS at sourceGREEN.
  Original regularreport untouched; independent finalreport auditPASS. Reporting-only completion
  and mechanical report refresh record finalHEAD/cleanstatus with unchanged verifiedinputs.
- Input fingerprints and committed partner snapshots in `evidence/legal-update-20261002/late/`.

## 2026-10-02 — legal-update-legal revision 2 (historical; unpublished)

- Resumed clean reviewed `d3b6e32` under explicit review-2 authorization.
- Preserve original evidence; fix retired claim/code program, staged iOS shortened store names,
  and decimal-comma locale PIPA thresholds through new assertion RED then GREEN commits.
- Keep KRW 22,000 per review-2. Read-only partner audit: iOS matches; committed Android still
  KRW 19,900. Cross-repository commercial parity remains BLOCKED pending matching commits.
- RED `30647c4`: detached parent compile PASS; 43 methods,10 failed methods,1098 assertion failures,0 errors/skips/omissions. Wrapper count prediction corrected from retained evidence without a rerun.
- GREEN source edits remove retired workflows in all17 locales, preserve core Free features,
  ordinary Store trials and statutory/historical rights, neutralize sync token wording,
  strengthen the iOS alias guard and group PIPA thousand correctly in12paragraphs.
- New closed commercial parity gate links committed iOS/Android evidence and coordinated next action.
- Focused related family:81 exact methods PASS,0 failure/error/skip/omission; retained raw log/identity receipt.
- Seven renderer commands PASS; affected source-owned privacy/Terms outputs regenerated; release source fingerprints refreshed.
- Final full193 exact methods PASS; all12ordinary static commands PASS; release exit1 remains
  BLOCKED_EFFECTIVE_DATE. Site162/staged126pages; tone2078sentences,0violations,9existingexceptions.
  All255frozen relevant inputs/runtime match;51retired-body and34core-help preservation checks PASS.
- Independent read-only review found no material current source issue; Android parity remains blocked.
- Source GREEN committed locally at `5f96792321df89783e22b73aa7c43e1979e3a46c`; final report
  overwritten and schema/identity/evidence/hash/stamp validation PASS. Reporting-only completion
  and final mechanical HEAD/inventory refresh preserve all 255 verified product inputs.
  Independent read-only final report audit found no material inconsistency.
- Owned translation scratch/proof worktree removed. No native/device/network, push, merge,
  deployment or publication.

# Changelog

Changes to the public DoseWeek help and privacy site. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The site has no version numbers or
tags. Released sections are dated by their merge to `main`, which is the GitHub Pages source.
Being on `main` does not by itself prove the live page was checked.

## 2026-10-02 — legal-update-legal revision 1 (unpublished)

- RED `a33a8b8` proves all four review findings on detached `a264899`: compile PASS,
  32 methods / 12 failed methods / 235 assertion failures; 0 errors/skips/omissions.
- Corrected every locale's Korean annual reference to KRW 22,000; Android scope now names
  Wonyoung Labs, preserving Wonyoung Choi as representative/privacy officer.
- 1.0.6 policy/metadata/operations now exclude EU/EEA, UK and Switzerland sales with no
  appointed EU/UK representative. Applicable existing-user rights, transfer safeguards,
  incident clocks and iOS portability are preserved. Actual Store exclusions remain false-gated.
- Canonical and staged iOS policy/help use neutral other-platform/store references while
  retaining shared purchase-verifier and deletion disclosures. Affected pages regenerated.
- Focused 77 and full 182 methods PASS, 0 failures/errors/skips/omissions. Every ordinary
  static gate PASS; 162 site and 126 in-memory staged pages. All 249 frozen inputs match.
  Two independent reviews and exact preservation/operator audits found no material issue.
- Release gate exit1 remains BLOCKED on null date and operational proof. First wrapper
  classification failure and actual terminal log retained; classification corrected without
  rerunning product checks. Evidence: `evidence/legal-update-20261002/revision1/`.
- Source GREEN committed at `3ded23a5f655c79fc99b7c2b777019884d805b54`. Final report overwritten
  and validated; a reporting-only completion commit and mechanical final HEAD/inventory refresh
  do not change the 249 verified product inputs. Exact final state is in the lane JSON report.
- Owned proof worktree and translation scratch removed. No native/network/store action,
  push, merge, deployment, publication or new visual/counsel/native-speaker certification.

## 2026-10-02 — legal-update-legal initial result (historical; rejected review-1)

- Local source GREEN: `2efa2b0f8e368c074fc24f947a4d014776636e0d`. Completion documentation
  records this checkpoint without changing matching verification inputs; final HEAD is in the
  lane JSON report. Temporary proof worktrees are removed and no owned check process remains.
- Final JSON written and validated, including 29 evidence paths and independent reporting
  review. Completion matches 45/46 frozen inputs; only derived release-map metadata changed.
  Adult-only copy remains; child controls and claim-substantiation follow-up are not certified.
- Added 17-locale privacy/rights/breach and processor-table drafts, explicit sensitive-health
  consent, Wonyoung Labs operator contacts, daily encrypted S3 Seoul  + weekly OS backups with
  deletion within 7 days, immediate requested erasure, Store-confirmed end + 30 days / at most 7 days outage retention.
- Final owner prices and Store-eligible 1-calendar-month trial, automatic renewal/cancellation,
  Korean statutory refund/consent and regional notices are preserved in Terms; integration
  appends account retention without overwriting billing rights. Separate US policy linked.
- Assertion-only REDs `a7febe9`, `2e51e28`, `147c533` proved on their parents. Initial tone,
  assembly and generated-content failures retained and corrected through related families.
  Final 173 methods PASS,0 errors/skips/omissions; all static light gates PASS,162 site / 126 staged
  pages verified. Inputs and exact identities retained under `evidence/legal-update-20261002/`.
- Release remains BLOCKED on unset date and unresolved provider/native/operational facts;
  explicit EU/UK representative contacts pending. Local file browser review policy-blocked;
  no visual/counsel/native-speaker/native/provider certification, publication or push.

## Unreleased candidate: free version with ads, Plus and Terms of Use (not published)

Candidate copy for the monetization release (owner instruction 2026-09-29,
`docs/MONETIZATION_POLICY.md` in both app repositories), prepared on branch
`claude/doseweek-free-ads-plus-himvw9`. The live 1.0.5 apps have none of these features, and this
branch is not merged or published.

- iOS privacy: new sections 11 (ads in the free version: Google Mobile Ads SDK and UMP,
  non-personalized ads without App Tracking Transparency, what Google still processes, consent,
  what DoseWeek never sends, AdMob not linked to Firebase, reporting an ad) and 12 (Plus through
  the App Store, on-device verification, device-local cache and counters, Plus tool data, cancel
  and restore, earlier buyers); the 1.0.5 section is now 13. The analytics section opens with a
  paragraph that scopes its advertising-ID statements to analytics; the deletion section adds what
  Delete All does with Plus data. The intro no longer claims to describe the app "exactly".
- iOS support: six Plus and ads answers (`#<locale>-plus-<key>`).
- iOS privacy and support (2026-10-01, branch `next-ai/icloud-disclosure-revert`): the optional
  automatic iCloud backup disclosure from `ab8f52e` is withdrawn because the 1.0.6 iOS app ships with
  that feature switched off (App Store Review Guideline 5.1.3(ii)). The privacy `backups` paragraph,
  the manual-backup exception sentence, the iCloud deletion sentences and the third support backup
  answer are removed in all 17 locales, and `render_ios.py` again renders `backups` as one paragraph.
  The Korean and Japanese support leads keep the `679b03c` wording without "only". The withdrawn
  text stays in Git history at `ab8f52e` for a future release that turns the feature on.
- Android privacy: new sections 5 (ads) and 6 (Plus, Google Play Billing, purchase-verification
  server); retention, security, changes and the 1.0.0 section move to 7 to 10, backup stays 4.
  "Advertising" leaves the not-used list (crash reporting stays); the support intro, accounts
  answer and feature badges scope "no developer server" to health records. Six Plus and ads
  answers are appended to the FAQ.
- New route `/terms/` (Terms of Use for both apps, 17 locales, App Store and Google Play
  subsections, Apple's standard EULA linked) rendered by `scripts/render_terms.py`; the privacy
  and support pages link to it. The sitemap now lists 144 URLs (8 routes).
- `legal_release.py`: the live effective date is 2026-09-23 for both platforms;
  `NEXT_RELEASE_EFFECTIVE_DATE` is unset, so `check_site.py --release` fails until the owner sets
  the release date, then also fails while the purchase-verification server placeholders remain.
- The new and changed fields are translated into the other 15 locales (90 fields each: iOS 26,
  Android 37, Terms 27; German uses Sie, Dutch u). The translations are not reviewed by native
  speakers, and none is claimed. The per-language page titles and descriptions keep their interim
  wording.
- `legal_release.RELEASE_PLACEHOLDERS` also lists the translated server-location and retention
  placeholder sentences, and `check_site.py` requires every locale to carry as many registered
  placeholders as en, so `--release` keeps refusing a translated placeholder and no locale keeps
  one after en and ko are filled in.

## 2026-09-30: AdMob seller verification

- Added the root `app-ads.txt` record for Google publisher `pub-9675683489444791`.

## Unreleased: per-language URLs

- Every route now also has one static page per locale at `/<locale>/<route>` (7 routes x 17
  locales = 119 pages), rendered from the same panels as the hash pages. Each shows one language
  with its own `<html lang>` (`dir="rtl"` for Arabic), canonical link, localized title and
  description (existing copy only), and links to the same page in the other languages. The
  legal and help text is unchanged: `check_site.py` compares each language page's panel with the
  hash page's panel.
- The hash pages (`/support/#ko` and the others) keep their URLs, hash switching and
  no-JavaScript fallback. They stay canonical and are the `x-default` of their route. Every page
  of a route lists the same 18 hreflang alternates (17 languages and `x-default`).
- `sitemap.xml` is generated by `scripts/render_sitemap.py`: 126 URLs, each with its
  `xhtml:link` alternates. `check_site.py` checks every generated page, hreflang reciprocity,
  `x-default`, canonical links, sitemap coverage and local links;
  `scripts/test_locale_pages.py` is an independent spec over the generated files.
- `assets/language.js` leaves a language page as rendered (it only scrolls the current language
  into view). Its URL now carries a content version (`language.js?v=…`), like `site.css`, so a
  cached old script never runs on a new page.

## Unreleased: search discovery

- Added `robots.txt` and `sitemap.xml` for the seven pages. `check_site.py` now fails when the
  sitemap and the canonical pages differ, or when `robots.txt` does not name the sitemap.
- The home page title is now the localized guide label (for example "DoseWeek 이용 안내",
  "DoseWeek Guide") instead of the product slogan. The description and social metadata describe
  the help content.

## 2026-09-28: license (`8b53cf0`)

- Added `LICENSE`: proprietary, all rights reserved.

## 2026-09-28: Korean voice and legal alignment (PR #6, merge `efaf1ff`)

Merged to `main` on 2026-09-28. The merge also brought the Android 14 minimum (2823234, listed in
the next section), the Android policy and help scoped to 1.0.0 (versionCode 12) and later with
1.0.5 as the current version (90fb129), and the formal register in the iOS German and Dutch
text (7d9a87b).

### Changed

- All Korean copy on every page (help, privacy, import, home) uses plain 해요체. Legal facts,
  numbers, processors, recipients and retention periods are unchanged.
- Android privacy policy and FAQ, all 17 locales: the file backup is one you make yourself, and
  the only automatic backup is the optional Google Drive backup (off by default); on-device
  processing is stated with the exception of optional integrations, backups and exports; copies
  kept separately include CSV exports; Korean and Chinese meal answers no longer say meals stay
  only on the device.

### Added

- `scripts/korean_tone.py` with shared rules, a reviewed allow-list and self-tests.
  `check_site.py` runs them and fails on any Korean tone violation.

## 2026-09-24: help, privacy and syringe branding (PR #4, merge `40d0359`)

Merged to `main` on 2026-09-24. The Android 14 minimum entry below came later, with PR #6.

### Added

- Both privacy policies (17 locales) describe optional usage analytics for the upcoming app
  releases: Google Analytics for Firebase, off by default, with separate consent for analytics
  and for overseas transfer (c9ce28f, dbb7393).
- The home page and both platform pages share the same short help tasks
  (`docs/help-navigation.json`) (c9ce28f).
- An operator tool and guide for the apps' analytics exports and deletion requests
  (`scripts/privacy_ops.py`, `docs/ANALYTICS_OPERATIONS.md`). It runs as a dry run unless told
  otherwise, and has unit tests (c9ce28f).
- Both support pages open with a six-step "Getting started" guide in 17 locales (setup,
  schedule, recording, meals, import, settings), each step linking to the matching answer. The
  home "Getting started" card opens it (`#<locale>-start`). The FAQ below is titled "FAQ and
  troubleshooting" (2026-09-24).

### Changed

- The policy effective date is set to 2026-09-23 on both platforms (c9ce28f).
- Food help: 200 foods can be found by name in 17 languages, and the search languages can be
  chosen in Settings (0ec408e).
- The site shows the refreshed syringe app icons (4e77f2c).
- The privacy text now matches how analytics works in the apps. The deletion-request code
  appears only while analytics is on. Turning analytics off asks for a local reset. The operator
  is named. The Android policy names the Android ID (SSAID) instead of the iOS-only IDFV
  (dbb7393).
- Policy and FAQ text is split into separate paragraphs instead of one long block (dbb7393).
- Easier to read in all locales. The contact address sits on its own line. The Android policy
  list follows the sentence that introduces it. The iOS deletion FAQ gives the delete-all
  instruction once. Long support URLs wrap. Korean list items no longer break mid-word (d459c90).
- The shipped 1.0.5 / versionCode 12 features are no longer labelled "Candidate guidance" or
  unreleased. Each of those FAQ answers now opens with a one-line version scope ("This applies
  to ..." for backups between versions and supported devices), and the last policy section on
  each platform is titled "Features added in ..." (2026-09-24).
- Audit text fixes in all locales: iOS backups and Android backups cannot be restored on the other
  platform; the Android Drive recovery code can be shown again until confirmed, a pending file
  backup code stays wrapped on the device, and each Drive backup is a separate file that is kept
  until deleted; the estimate's reference medication is not in a backup; the iOS policy discloses
  the one pre-upgrade copy of records; the iOS calendar example names Exchange instead of
  Samsung; the Polish date no longer ends in a double period (2026-09-24).
- Android support FAQ, all 17 locales: DoseWeek needs Android 14 or later from versionCode 13.
  Android 8.0 to 13 devices keep their installed versionCode 12 without updates, and Google
  Play offers no new installs on them. The renderer and site check expect versionCode 13 in
  that answer's scope line (owner decision 2026-09-25; 2823234, merged with PR #6 on
  2026-09-28).

### Removed

- These files were removed from `docs/`: the 2026-09-15 continuation handoff and prompt, the
  second-release candidate snapshot, a README snapshot and a 1.5 MB continuation archive. Once
  merged, Pages will stop serving them. Git history still has them. (Documentation cleanup,
  2026-09-24.)

## 2026-09-22: unified 17-language site (PR #3, merge `acfb108`)

- The home page is shared by both platforms and available in all 17 locales. It has simpler
  layout and responsive type (61159a1, 8aee312).
- The iOS privacy policy and support page are available in all 17 locales (4a113e5, 439428d).
- New Android candidate pages, with a candidate policy section and support answers
  (f25c1fc).
- The import guide at `/import/` became the final six-step guide in 17 locales
  (456c63a).
- Both policies describe the bundled offline food table and include its attribution lines
  (7b9089f).
- The Android policy discloses the optional food-label recognition, which uses Google ML Kit
  (9d05d3a). The policy date is aligned before the final app builds (2a140d5).

## 2026-09-15: import preparation guide (PR #2, merge `8a615a1`)

- New multilingual guide for preparing records to import (cc6fa49). Import limits and
  Apple Health disclosures are aligned (8bdd83c).

## 2026-09-13: recording guidance

- New versioned recording guidance for both apps (f6bd054). The iOS backup help now matches the
  Files picker (a4dd741).

## 2026-08-31 to 2026-09-11: Android pages and custom domain

- New Android legal pages, with parity updates and the Android app icon (0b7a812, efd1cde,
  a3265ee). They re-render from the current Android content, including the widget (ef6dce0).
- The pages describe the optional Health Connect import and Google Drive backup (7c5d211). The
  landing page covers both platforms (5d42df4).
- The site moved to `doseweek-legal.wonyoungchoi.dev` (fc4d322, 54f688e).
- The backup text says backups leave the app through the file picker (2d432d5, ad5b79c).

## 2026-08-19 to 2026-08-22: first pages and redesign

- The first privacy and support pages, in ko, en and ja (ded4e96). The app was renamed from
  DoseDay to DoseWeek (6f7287b). The support contact changed (c8fcd9c).
- The privacy policy gained the on-device AI section (de120bc).
- The support and legal site was redesigned, and the privacy and support guidance made
  clearer (daf80f0, a94f3e0).
