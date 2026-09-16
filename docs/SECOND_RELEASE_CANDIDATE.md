# Second-release candidate — what this branch publishes and what it does not

Branch `candidate/second-release`, cut from `main` `8a615a1` on 2026-09-16. Nothing here is
merged or published. It prepares the public pages for the stage-2 release of both apps:
Android **1.0.0 (versionCode 11)** and the iOS release that follows **1.0.4 (build 16)**, whose
version number is not assigned yet.

## Sources read for every fact

| Fact area | Source |
|---|---|
| Android policy and support copy | `DoseweekPlayStore` `feat/calendar-sync` `c7495fc` → `docs/legal/android-content.json` |
| iOS policy copy (sections 1–9) | `DoseWeek` `feat/calendar-sync` `5e82eae` → `DoseDay/Resources/Localizable.xcstrings` |
| Meals / nutrition | `feat/nutrition-p2` (iOS `af60d22`, Android `e8cb6a8`) and each repository's `docs/NUTRITION.md` |
| Chosen schedule dates | `feat/explicit-dates` (iOS `a3ee11f`, Android `d1ebfa2`) |
| Body chart references | `feat/body-charts` (iOS `88678dd`, Android `6152e7c`), `designs/body-chart-references.md` |
| Calendar sync | `feat/calendar-sync` both platforms, `designs/calendar-sync.md` |
| File import | Android `main` `dc7b973`, iOS `feat/import-parity` `7799be0` |
| Food data licences | `android-nutrition-data` `feat/nutrition-data` `a2eb701` → `docs/NUTRITION_DATA_RELEASE.md` |
| Reserved version numbers | `DoseWeek_Continuation_2026-09-15/COORDINATOR_LOG.md` "Version ledger" |
| Supported ranges | `app/build.gradle.kts` (minSdk 24, targetSdk 36, versionCode 11); `DoseDay.xcodeproj` (IPHONEOS_DEPLOYMENT_TARGET 26.0, TARGETED_DEVICE_FAMILY 1,2, MARKETING_VERSION 1.0.4, build 16) |

## Deliberate limits in the published wording

- **Food data packs are described as not shipping in this version.** Neither app branch bundles
  a `fooddata` release; only the nutrition contracts are in the app assets. The pages name the
  sources and licences (USDA FoodData Central, public domain CC0 1.0 with attribution
  requested; UK CoFID under the Open Government Licence v3.0; the Japanese MEXT Standard Tables
  under the MEXT data-use statement and site terms; Korean MFDS data under the data.go.kr
  grant with no use restriction) and say the tables are still in preparation.
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
- The record-preparation guide at `/import/` was left as published: its status is still
  `preparation_only`, and its limits already name both platforms (Android 1 MiB draft, iOS
  4 MiB draft, 10,000 rows, symptom rows unsupported).

## Required before any of this is published

1. `DoseweekPlayStore` must commit the bytes of `docs/android-content.candidate.json` to
   `docs/legal/android-content.json`; the Android pages are rendered from the candidate mirror.
2. The iOS app catalog should gain equivalent strings for the candidate policy section, so the
   published policy keeps mirroring the app instead of only the site.
3. The effective date stays 2026-08-22 (iOS) and 2026-09-08 (Android). A new effective date is
   an owner decision to be made with the release, because meal records and calendar sync are
   real processing changes.
4. Publication waits for the releases themselves: Android 1.0.0 (versionCode 11) and the next
   iOS build. Until then the candidate wording names the unreleased version in every locale.
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
