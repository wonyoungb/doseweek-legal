# DoseWeek public pages

This repository contains the public landing, support, and privacy pages for **DoseWeek**.
It is a dependency-free static site: no analytics, remote fonts, third-party scripts, cookies,
accounts, or form backend.

## Sources of truth

The privacy copy does not originate here. Its canonical source is the app repository:

```text
DoseDay/Resources/Localizable.xcstrings
```

The public policy must mirror, verbatim and in all three languages:

- `privacy.intro`
- `privacy.effectiveDate`
- `privacy.section1.title` through `privacy.section8.body`
- `privacy.medical.title` and `privacy.medical.body`
- `common.notAMedicalDevice` (the second medical-disclaimer paragraph)

Change those app strings first, review the clinical/privacy meaning there, and then copy the
approved values into `privacy/index.html`. Never make a substantive policy change only on the
website. The current effective date is **August 22, 2026**.

Android policy and support copy has a separate canonical source in the Android app repository:

```text
DoseweekPlayStore/docs/legal/android-content.json
```

That catalog pins the Android application ID, effective date, language order, text direction,
and all localized product, privacy, and support copy for the Android pages. Change and review
Android behavior and that catalog together, then regenerate `android/` with
`scripts/render_android.py`. Never copy the iOS policy into the Android routes: the platforms
deliberately differ in health integrations, AI, notifications, exports, backup transport, and
deletion behavior.

The existing iOS support FAQ must remain consistent with the iOS app catalog and with the
shipped iOS behavior. In particular, keep the exact four read-only Apple Health types,
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
/privacy/#ko  /privacy/#en  /privacy/#ja
```

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

For that no-script fallback, localized panels intentionally stay in **English, Japanese,
Korean** DOM order. Do not reorder them without updating the sibling selectors in
`assets/site.css`. Privacy table-of-contents IDs start with their locale (`en-health`,
`ja-health`, `ko-health`), which lets the shared script retain the correct panel.

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
- `scripts/render_android.py` — deterministic Android page renderer
- `scripts/check_site.py` — dependency-free structural, metadata, accessibility, disclosure, and
  local-link checks

## Local verification

Run before every handoff or publish:

```bash
python3 scripts/check_site.py
python3 scripts/check_site.py --catalog /path/to/DoseDay/Resources/Localizable.xcstrings
python3 scripts/render_android.py --content /path/to/DoseweekPlayStore/docs/legal/android-content.json --check
python3 scripts/check_site.py \
  --catalog /path/to/DoseDay/Resources/Localizable.xcstrings \
  --android-content /path/to/DoseweekPlayStore/docs/legal/android-content.json
node --check assets/language.js
git diff --check
python3 -m http.server 4173
```

Then inspect the nine existing iOS locale URLs and all Android routes at desktop and
narrow-mobile widths. Check light and dark appearance, keyboard focus, FAQ disclosure controls,
privacy table-of-contents links, browser back/forward, Arabic right-to-left layout, and one run
with JavaScript disabled. Confirm only one localized panel is visible and the language tab has
the matching `aria-current` value. Before publishing an Android change, also prove that
`index.html`, `privacy/index.html`, and `support/index.html` did not change unless the task
explicitly includes an iOS policy update.

Publishing is a separate, explicit step. Do not commit, push, or deploy from a preview-only
review task.
