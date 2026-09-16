# DoseWeek public pages

This repository contains the public landing, support, privacy, and record-preparation pages for **DoseWeek**.
It is a dependency-free static site: no analytics, remote fonts, third-party scripts, cookies,
accounts, or form backend.

## Sources of truth

The privacy copy does not originate here. Its canonical source is the app repository:

```text
DoseDay/Resources/Localizable.xcstrings
```

`privacy/index.html` and `support/index.html` are generated. `docs/ios-content.json` holds a
verbatim mirror of those app strings for all seventeen locales, the repository-local
second-release candidate section, and the support FAQ copy, and `scripts/render_ios.py`
renders both pages from it. Change the app strings first, then re-mirror and regenerate;
`python3 scripts/render_ios.py --check --catalog <xcstrings>` compares every mirrored policy
string with the app catalog. The Korean, English, and Japanese support answers are the
previously published text; the other fourteen locales were written for the second-release
candidate and have not had a native-speaker review.

The public policy must mirror, verbatim and in all three languages:

- `privacy.intro`
- `privacy.effectiveDate`
- `privacy.section1.title` through `privacy.section9.body` (section 9 is the optional
  calendar sync that ships with the unreleased next version)
- `privacy.medical.title` and `privacy.medical.body`
- `common.notAMedicalDevice` (the second medical-disclaimer paragraph)

Change those app strings first, review the clinical/privacy meaning there, and then copy the
approved values into `privacy/index.html`. Never make a substantive policy change only on the
website. The current effective date is **August 22, 2026**.

Android policy and support copy has a separate canonical source in the Android app repository:

```text
DoseweekPlayStore/docs/legal/android-content.json
```

`docs/android-content.candidate.json` in this repository is an unpublished mirror of that
catalog as it stands on the app's stage-2 branches, and is what the committed `android/`
pages are currently rendered from. Before publishing, the app repository must carry the same
bytes; the candidate file is not a second source of truth.

That catalog pins the Android application ID, effective date, language order, text direction,
and all localized product, privacy, and support copy for the Android pages. Change and review
Android behavior and that catalog together, then regenerate `android/` with
`scripts/render_android.py`. Never copy the iOS policy into the Android routes: the platforms
deliberately differ in health integrations, AI, notifications, exports, backup transport, and
deletion behavior.

The existing iOS support FAQ must remain consistent with the iOS app catalog and with the
shipped iOS behavior. In particular, keep the exact five read-only Apple Health types,
local-notification boundary,
encrypted user-directed backup boundary, recovery-code warning, and
`SystemLanguageModel.default` availability/manual fallback accurate. Keep plaintext PDF/CSV
exports distinct from encrypted backups: they are generated on request, go only to the share-sheet
destination the user selects, and are outside the app's control afterward. The deletion copy must
also distinguish immediate logical removal from the secure database-file cleanup retry, and App
Lock support must never suggest that authentication can be bypassed.

The existing iOS app icon is derived from:

```text
DoseDay/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png
```

The web copy at `assets/app-icon.png` is resized to 512 px for download size. Keep its aspect
ratio and do not replace it with an unrelated mark.

The Android pages use their own shipped Google Play icon. Its canonical source and generated
web copy are:

```text
DoseweekPlayStore/marketing/GooglePlay/play-icon-512.png
doseweek-legal/assets/android-app-icon.png
```

Update the web copy from that exact Android source. Do not replace the existing iOS web icon
when the Android artwork changes.

## Locale URL contract

Every main page has three localized panels and these stable deep links:

```text
/#ko       /#en       /#ja
/support/#ko  /support/#en  /support/#ja
```

`/privacy/` and `/support/` now serve the same seventeen locales as the Android and
record-preparation pages, with the identical panel, localized skip link, and right-to-left
contract:

```text
/privacy/#ko  /privacy/#en  /privacy/#ja  /privacy/#de  …  /privacy/#tr
/support/#ko  /support/#en  /support/#ja  /support/#de  …  /support/#tr
```

The landing page still serves Korean, English, and Japanese. The in-app online-help link in
`RecordHelpView.swift` still sends every other language to `/support/#en`; owner decision
BUGFIX-PARITY-20260915-07 asks for that mapping to cover all seventeen locales.

A valid hash wins. With no valid hash, `assets/language.js` chooses the first supported browser
language and falls back to Korean. It updates the document language, title, visible panel, and
`aria-current`. With JavaScript disabled, CSS defaults to Korean and the three language links
still show one panel at a time.

Android uses the same hash contract below `/android/`, `/android/privacy/`, and
`/android/support/`, with these seventeen exact BCP-47 tags:

```text
ko en ja de fr es it nl pt-PT pl sv hi pt-BR ar zh-Hans zh-Hant tr
```

Portuguese and Chinese variants remain distinct, and Arabic panels declare right-to-left
direction. `assets/language.js` derives each page's supported languages from its own navigation,
prefers an exact locale before applying the documented Portuguese/Chinese fallback, and defaults
to Korean. Each Android panel and localized skip link carries its own `lang` and `dir`, so direct
hash links keep the selected language, reading direction, and skip destination even without
JavaScript; JavaScript also updates the document root metadata. The existing iOS URLs and their
three-language behavior remain unchanged.

For that no-script fallback, the landing page's localized panels intentionally stay in
**English, Japanese, Korean** DOM order. Do not reorder them without updating the sibling
selectors in `assets/site.css`. The generated privacy and support pages use the seventeen-locale
order instead. Privacy table-of-contents IDs start with their locale (`en-health`, `ja-health`,
`ko-health`), which lets the shared script retain the correct panel.

## Files

- `index.html` — branded landing page
- `support/index.html` — FAQ, privacy-safe contact guidance, and medical safety notice
- `privacy/index.html` — public policy mirrored from the app catalog
- `android/index.html` — Android landing page generated from the Android legal catalog
- `android/support/index.html` — Android-only support and safety guidance
- `android/privacy/index.html` — Android-only public policy
- `assets/site.css` — shared responsive, dark-mode, focus, and reduced-motion styles
- `assets/language.js` — page-scoped hash/browser-language selection only
- `assets/app-icon.png` — existing iOS icon
- `assets/android-app-icon.png` — Android Google Play icon
- `docs/ios-content.json` — mirrored iOS policy strings, the candidate section, and the
  seventeen-locale support copy
- `docs/android-content.candidate.json` — unpublished mirror of the Android legal catalog
- `scripts/render_ios.py` — deterministic iOS privacy and support page renderer
- `scripts/render_android.py` — deterministic Android page renderer
- `scripts/check_site.py` — dependency-free structural, metadata, accessibility, disclosure, and
  local-link checks
- `legal-release-map.json` — per-platform candidate, catalog hash, decision, and check record

## Local verification

Run before every handoff or publish:

```bash
python3 scripts/check_site.py
python3 scripts/render_ios.py --check --catalog /path/to/DoseDay/Resources/Localizable.xcstrings
python3 scripts/check_site.py --catalog /path/to/DoseDay/Resources/Localizable.xcstrings
python3 scripts/render_android.py --content /path/to/DoseweekPlayStore/docs/legal/android-content.json --check
# Until the app repository adopts the candidate catalog, pass docs/android-content.candidate.json
# instead of the app-repository path in the two commands above and below.
python3 scripts/check_site.py \
  --catalog /path/to/DoseDay/Resources/Localizable.xcstrings \
  --android-content /path/to/DoseweekPlayStore/docs/legal/android-content.json
node --check assets/language.js
git diff --check
python3 -m http.server 4173
```

Then inspect all seventeen iOS locale URLs and all Android routes at desktop and
narrow-mobile widths. Check light and dark appearance, keyboard focus, FAQ disclosure controls,
privacy table-of-contents links, browser back/forward, Arabic right-to-left layout, and one run
with JavaScript disabled. Confirm only one localized panel is visible and the language tab has
the matching `aria-current` value. Before publishing an Android change, also prove that
`index.html`, `privacy/index.html`, and `support/index.html` did not change unless the task
explicitly includes an iOS policy update.

Publishing is a separate, explicit step. Do not commit, push, or deploy from a preview-only
review task.

## Record preparation guide

`/import/#<locale>` provides the same three-step guide in all seventeen supported locales.
It has its own localized prompt copy control and downloadable Markdown prompts, Markdown
format notes, an empty JSON draft, and `draft-v1.schema.json`. It uses the existing language
script without changing the landing, privacy, or platform support pages.

The canonical copy is `import/content.json`; regenerate it with `python3 scripts/render_import.py`.
Run `python3 scripts/render_import.py --check --require-all-locales` before publishing.
The normal site checker also validates all generated guide files and language links.

The current status is `preparation_only`: users can prepare and review drafts, but the guide
must not claim that the released app saves this JSON. Change that status and its localized
wording together only when the corresponding app importer and manual-review flow have been
verified. An extraction draft is never an encrypted full backup. The format uses identical
machine keys in every language, preserves source text, and leaves unknown values null.

The intended later save operation adds selected validated rows atomically, keeps manual
review mandatory, and never automatically overwrites existing records. Date-only event
semantics and vendor-specific formats require separate implementation and verification.
No real health record, screenshot, or extracted patient value belongs in this repository.
