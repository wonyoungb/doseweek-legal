# DoseWeek public pages

Static product, support, privacy and record-import pages for DoseWeek on iOS and Android.
No third-party scripts, analytics, remote fonts, cookies, accounts or form backend.

## Content ownership

| Content | Canonical source | Mirror / renderer |
|---|---|---|
| iOS policy | iOS `DoseDay/Resources/Localizable.xcstrings` | `docs/ios-content.json`, `scripts/render_ios.py` |
| Android pages | Android `docs/legal/android-content.json` | `docs/android-content.candidate.json`, `scripts/render_android.py` |
| Import guide and downloads | `import/content.json` and templates | `scripts/render_import.py` |
| Effective date and attributions | Owner decisions and bundled data notices | `scripts/legal_release.py` |

Change app behavior and its canonical policy together, then mirror and regenerate. Public
privacy text is not an independent source. Android's consented food-label ML Kit diagnostics
exception must not be described as zero SDK traffic or copied into iOS policy.

## Locales and routes

The iOS landing page has Korean, English and Japanese panels. iOS privacy/support, Android
pages and the supported import guide have 17 locales: ko, en, ja, de, fr, es, it, nl, pt-PT,
pl, sv, hi, pt-BR, ar, zh-Hans, zh-Hant and tr. In-app help supports that same locale set.

Stable paths: `/`, `/privacy/`, `/support/`, `/android/`, `/android/privacy/`,
`/android/support/` and `/import/`. Hashes choose locale, such as `/support/#ar`.
Preserve Arabic RTL, distinct Portuguese/Chinese variants, keyboard focus and the no-JavaScript
fallback. Do not reorder landing panels without checking the CSS sibling selectors.

## Verify

From this repository, substitute the actual neighboring checkout paths when necessary:

```bash
python3 scripts/render_ios.py --check --catalog ../ios/DoseDay/Resources/Localizable.xcstrings
python3 scripts/render_android.py --content ../android/docs/legal/android-content.json --check
python3 scripts/render_import.py --check --require-all-locales
python3 scripts/check_site.py --catalog ../ios/DoseDay/Resources/Localizable.xcstrings --android-content ../android/docs/legal/android-content.json
# Publication additionally requires the accepted-upload/effective-date sequence:
python3 scripts/check_site.py --release
```

Structural checks do not prove browser appearance, screen-reader use or native-speaker review.
Keep those evidence categories distinct in [the current handoff](docs/CURRENT_HANDOFF.md).

## Release and documentation

[legal-release-map.json](legal-release-map.json) binds candidate catalogs and release decisions.
The owner-approved second-release date is set after both platform builds are uploaded, then
mirrored consistently. Until then the release gate intentionally fails. main publication follows
the authorized release sequence; a pushed branch is not a published policy.

Read [AGENTS.md](AGENTS.md), [the documentation index](docs/README.md) and
[CURRENT_HANDOFF.md](docs/CURRENT_HANDOFF.md). Dated continuation files are historical only.
Original documentation is retained under docs/history and in Git.
