# Changelog

Changes to the public DoseWeek help and privacy site. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The site has no version numbers or
tags. Released sections are dated by their merge to `main`, which is the GitHub Pages source.
Being on `main` does not by itself prove the live page was checked.

## [Unreleased]

On branch `codex/help-privacy-20260923` (draft PR #4 into `main`). Not merged to `main`, so not
live.

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
