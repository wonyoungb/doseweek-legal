# DoseWeek public pages

This repository contains the public landing, support, and privacy pages for **DoseWeek**.
It is a dependency-free static site: no analytics, remote fonts, third-party scripts, cookies,
accounts, or form backend.

## Source of truth

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

The support FAQ must remain consistent with the same catalog and with the shipped behavior.
In particular, keep the exact four read-only Apple Health types, local-notification boundary,
encrypted user-directed backup boundary, recovery-code warning, and
`SystemLanguageModel.default` availability/manual fallback accurate. Keep plaintext PDF/CSV
exports distinct from encrypted backups: they are generated on request, go only to the share-sheet
destination the user selects, and are outside the app's control afterward. The deletion copy must
also distinguish immediate logical removal from the secure database-file cleanup retry, and App
Lock support must never suggest that authentication can be bypassed.

The app icon is derived from:

```text
DoseDay/Resources/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png
```

The web copy at `assets/app-icon.png` is resized to 512 px for download size. Keep its aspect
ratio and do not replace it with an unrelated mark.

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

For that no-script fallback, localized panels intentionally stay in **English, Japanese,
Korean** DOM order. Do not reorder them without updating the sibling selectors in
`assets/site.css`. Privacy table-of-contents IDs start with their locale (`en-health`,
`ja-health`, `ko-health`), which lets the shared script retain the correct panel.

## Files

- `index.html` — branded landing page
- `support/index.html` — FAQ, privacy-safe contact guidance, and medical safety notice
- `privacy/index.html` — public policy mirrored from the app catalog
- `assets/site.css` — shared responsive, dark-mode, focus, and reduced-motion styles
- `assets/language.js` — hash/browser-language selection only
- `scripts/check_site.py` — dependency-free structural, metadata, accessibility, disclosure, and
  local-link checks

## Local verification

Run before every handoff or publish:

```bash
python3 scripts/check_site.py
python3 scripts/check_site.py --catalog /path/to/DoseDay/Resources/Localizable.xcstrings
node --check assets/language.js
git diff --check
python3 -m http.server 4173
```

Then inspect all nine locale URLs above at desktop and narrow-mobile widths. Check light and
dark appearance, keyboard focus, FAQ disclosure controls, privacy table-of-contents links,
browser back/forward, and one run with JavaScript disabled. Confirm only one localized panel is
visible and the language tab has the matching `aria-current` value.

Publishing is a separate, explicit step. Do not commit, push, or deploy from a preview-only
review task.
