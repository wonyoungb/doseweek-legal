> Historical snapshot. Use [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md) and
> [legal-release-map.json](../legal-release-map.json) for current status. Do not restart
> old workflows or treat original pending work below as still pending.

# Second-release candidate — what this branch publishes and what it does not

Branch `candidate/second-release`, cut from `main` `8a615a1` on 2026-09-16. Nothing here is
merged or published. It prepares the public pages for the stage-2 release of both apps:
Android **1.0.0 (versionCode 11)** and the next iOS release, whose version number is not assigned
yet. The iOS candidate source still carries `MARKETING_VERSION` 1.0.4 and build 16, but build 16 has
never been uploaded: the local ledger shows 1.0.3 (build 14) confirmed live on 2026-09-11 and
1.0.4 (build 15), a store-metadata release functionally identical to build 14, submitted for
review on 2026-09-12 with no later store observation recorded. The pages therefore name no
build as the current or next App Store version; the five bugfix-candidate FAQ answers keep the
published "iOS 1.0.4 (build 16)" candidate label from `main`, and the integrator revisits it
when the store number is chosen. Android code 10 was accepted by Play but its review was
withheld for stage 2, so every Android candidate answer names versionCode 11, the first build
users receive after live code 9.

## Cycle-2 update (2026-09-17, branch `feat/c2-legal-guide`)

Owner decisions applied on top of `274d397`; still unmerged and unpublished:

- **IOS-VERSION-104-20260917** — the pending 1.0.4 (build 15) review is cancelled and the
  stage-2 release ships as **iOS 1.0.5**. `bundleVersion`, `render_ios.py`
  `CANDIDATE_VERSION`/`PAGE_VERSION`, the five bugfix-candidate notices, the seven second-release
  notices and the candidate policy section name iOS 1.0.5 in all seventeen locales. No notice
  names a build: the store build number is chosen at upload (build 16 was never uploaded).
- **LEGAL-EFFECTIVE-DATE-20260917** — the new effective date is set after the store upload.
  It is the single constant `SECOND_RELEASE_EFFECTIVE_DATE` in `scripts/legal_release.py`
  (currently `None`); `check_site.py --release` fails until the release step fills it.
- **NUTRITION-CATALOG-RELEASE-20260917** — catalog search ships, so both candidate policy
  sections describe the bundled read-only food table (on-device search, no network download or
  update, market/search-language choices and table favorites stored on the device and in the
  encrypted backup, sources and licences listed in the app) and carry the USDA, CoFID, MEXT and
  MFDS attribution lines plus the MEXT change statement verbatim from food data release
  `d1f046b4…` `notices/NOTICE.txt`. The meals FAQ answers on both platforms describe the search.
- **TRANSFER-20260913-08/10** — `/import/` is the final six-step import guide (`supported`):
  new AI chat, attachment, copied prompt, JSON save, in-app review, selected append. The import
  FAQ answers on both support pages point to it.

The Android candidate catalog changed (food paragraph, meals and import answers), so
`DoseweekPlayStore` must adopt the new bytes of `docs/android-content.candidate.json` before the
Android pages are published; its sha256 is recorded in `legal-release-map.json`.

## Sources read for every fact

| Fact area | Source |
|---|---|
| Android policy and support copy | `DoseweekPlayStore` `feat/calendar-sync` `c7495fc` → `docs/legal/android-content.json` |
| iOS policy copy (sections 1–9) | `DoseWeek` `feat/calendar-sync` `5e82eae` → `DoseDay/Resources/Localizable.xcstrings` |
| Meals / nutrition | `feat/nutrition-p2` (iOS `a95915b`, tests-only after `af60d22`; Android `e8cb6a8`) and each repository's `docs/NUTRITION.md` |
| Chosen schedule dates | `feat/explicit-dates` (iOS `a3ee11f`, Android `d1ebfa2`) |
| Body chart references | `feat/body-charts` (iOS `88678dd`, Android `6152e7c`), `designs/body-chart-references.md` |
| Calendar sync | `feat/calendar-sync` both platforms, `designs/calendar-sync.md` |
| File import | Android `main` `dc7b973`, iOS `feat/import-parity` `7799be0` |
| Food data licences | `android-nutrition-data` `feat/nutrition-data` `a2eb701` → `docs/NUTRITION_DATA_RELEASE.md` |
| Reserved version numbers | `DoseWeek_Continuation_2026-09-15/COORDINATOR_LOG.md` "Version ledger" |
| Supported ranges | `app/build.gradle.kts` (minSdk 24, targetSdk 36, versionCode 11); `DoseDay.xcodeproj` (IPHONEOS_DEPLOYMENT_TARGET 26.0, TARGETED_DEVICE_FAMILY 1,2, MARKETING_VERSION 1.0.4, build 16) |

## Deliberate limits in the published wording

- **Food data (updated in cycle 2).** The pages first described the food tables as still in
  preparation; since NUTRITION-CATALOG-RELEASE-20260917 they describe the bundled table and
  carry its attribution lines (see the cycle-2 update above). The wording stays at the privacy
  level (on-device search, storage, backup, source listing) because the catalog search branches
  were not yet pushed when it was written; re-check it against the shipped apps before
  publishing.
- The MFDS clearance is written as the data.go.kr grant, not as a KOGL type 1 mark: the release
  notes record that the dataset pages carry no 공공누리 mark and that MFDS was not consulted.
- **Backup numbers are described by behaviour, not by number.** The ledger reserves iOS schema
  V7–V10 with payloads 9–11 and Android database 13–16 with payloads 10–12, but the integrator
  renumbers in merge order, so the pages only say the format number rises, that older backups
  still restore, and that an older app refuses a newer file.
- **No device claim beyond the verified range.** Android says API 24 through API 36 with
  automated checks on both; iOS says iOS 26.0 or later on iPhone and iPad with landscape only in
  the full-screen chart. Neither page claims foldable or dual-screen support; Duo is not
  mentioned at all.
- **Calendar sync** is written from the implemented contract: off by default, one chosen
  calendar, at most 24 events inside the next 84 days, 30 minutes each, generic title unless the
  user opts into the descriptive one, no medication, dose, site, notes or alerts, app-owned
  events only, user-edited events left alone, provider accounts store and sync under their own
  policies. iOS notes that the event links survive a restore on the same device.
- **Health integrations are unchanged** and stay read-only on both platforms.
- The import guide at `/import/` is `supported` since cycle 2; its limits name both platforms
  (Android 1 MiB draft, iOS 4 MiB draft, 10,000 rows, 10 MiB input, symptom and unclassified
  rows unsupported).

## Required before any of this is published

1. `DoseweekPlayStore` must commit the bytes of `docs/android-content.candidate.json` to
   `docs/legal/android-content.json`; the Android pages are rendered from the candidate mirror.
2. The iOS app catalog should gain equivalent strings for the candidate policy section, so the
   published policy keeps mirroring the app instead of only the site.
3. The effective date stays 2026-08-22 (iOS) and 2026-09-08 (Android) until the release step
   fills `SECOND_RELEASE_EFFECTIVE_DATE` after the store upload (LEGAL-EFFECTIVE-DATE-20260917)
   and changes, in the same commit, the catalogs' `effectiveDate`, the mirrored
   `privacy.effectiveDate` strings (the iOS app catalog must carry the same value) and the
   "effective date is set when that version is released" sentences.
4. Publication waits for the store upload of iOS 1.0.5 and Android 1.0.0 (versionCode 11), then
   `check_site.py --release` must pass before `candidate/second-release` is merged to `main`.
5. The iOS support FAQ now serves all seventeen locales. The fourteen locales beyond Korean,
   English and Japanese were written in this branch from the published English answers and
   have not had a native-speaker review; the in-app link mapping in `RecordHelpView.swift`
   still sends those languages to `/support/#en` (owner decision BUGFIX-PARITY-20260915-07).

## Verification run on this branch

```bash
python3 scripts/render_ios.py --check --catalog <ios>/DoseDay/Resources/Localizable.xcstrings
python3 scripts/render_android.py --content docs/android-content.candidate.json --check
python3 scripts/render_import.py --check --require-all-locales   # footer now links /support/#<locale>
python3 scripts/check_site.py --catalog <ios>/DoseDay/Resources/Localizable.xcstrings \
  --android-content docs/android-content.candidate.json
node --check assets/language.js
git diff --check
```

All passed on 2026-09-16. Browser checks at desktop and narrow-mobile widths, in light and dark
appearance, with JavaScript disabled and with VoiceOver, were not run in this session.
