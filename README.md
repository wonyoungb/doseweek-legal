# DoseWeek public pages

Static product, support, privacy and record-import pages for DoseWeek on iOS and Android.
No third-party scripts, analytics, remote fonts, cookies, accounts or form backend.
This describes the website; optional app analytics and other app services are disclosed in
the platform policies. Local generated pages are candidates until publication is verified.

## Content ownership

| Content | Canonical source | Renderer |
|---|---|---|
| iOS help home and platform navigation | `docs/home-content.json` and `templates/home.html` | `scripts/render_home.py`; versions, locale names and medical notices from the website platform sources |
| Help navigation and short steps | `docs/help-navigation.json` | Shared by the home and platform page renderers |
| iOS policy and support | `docs/ios-content.json` | `scripts/render_ios.py` |
| Android policy and pages | `docs/android-content.candidate.json` | `scripts/render_android.py` |
| Import guide and downloads | `import/content.json` and templates | `scripts/render_import.py` |
| Effective date and attributions | Owner decisions and bundled data notices | `scripts/legal_release.py` |

The website owns the complete help and privacy text. Update the relevant website source and
regenerate; routine wording changes do not require copying the full policy into either app.
Apps retain required consent and minimum instructions and link to their platform's help/privacy
website. Disclosures must still match actual app behavior. Legacy full-policy app resources are
retained during the UI transition and are not upstream sources for website edits.
Android's consented food-label ML Kit diagnostics exception must not be described as zero SDK
traffic or copied into iOS policy.

## Brand assets

`assets/app-icon.png` comes from an actual Icon Composer Default render of the iOS
`DoseDay/Resources/AppIcon.icon` package; its system corner mask is already present.
`assets/android-app-icon.png` is the exact full-square Play PNG. Both show the same
original five-layer syringe geometry. Android uses static frosted gradients and depth,
not Apple runtime Liquid Glass. The release-workspace brand generator updates these
files explicitly; ordinary page rendering does not copy a new icon into the website.
Retain source/output hashes and verify the platform copies before publication. A local
asset change is not a deployed website or store-listing update.

## Locales and routes

The shared home, iOS privacy/support, Android pages and the import guide all use the same
17 locales: ko, en, ja, de, fr, es, it, nl, pt-PT,
pl, sv, hi, pt-BR, ar, zh-Hans, zh-Hant and tr. In-app help supports that same locale set.

Stable paths: `/`, `/privacy/`, `/support/`, `/android/`, `/android/privacy/`,
`/android/support/` and `/import/`. Hashes choose locale, such as `/support/#ar`.
Preserve Arabic RTL, distinct Portuguese/Chinese variants, keyboard focus and the no-JavaScript
fallback. Every home guide/privacy/import link must retain its selected locale.
The combined in-app help/privacy entry opens `/#<locale>` on iOS and
`/android/#<locale>` on Android; required consent links can open the policy directly.

## Generate and verify

Edit the canonical source, then run its renderer without `--check`. When shared navigation or
CSS changes, regenerate all four renderer outputs so their stylesheet hashes agree:

```bash
python3 scripts/render_home.py
python3 scripts/render_ios.py
python3 scripts/render_android.py
python3 scripts/render_import.py --require-all-locales
```

From this repository, verify the resulting files against the website's own sources:

```bash
python3 scripts/render_home.py --check
python3 scripts/render_ios.py --check
python3 scripts/render_android.py --check
python3 scripts/render_import.py --check --require-all-locales
python3 scripts/check_site.py
# Before publication, validate the policy date:
python3 scripts/check_site.py --release
```

The optional iOS `--catalog` comparison is a legacy diagnostic for matching historical app
resources. It is not the website's normal release gate and must not drive duplicate app edits.

Shared typography uses relative sizes, gradual viewport scaling and natural CJK/connected-script
spacing. Generated pages version the stylesheet by content hash; after a CSS change regenerate
all pages, including the shared home. The site check rejects missing locales and stale output.

Structural checks do not prove browser appearance, screen-reader use or native-speaker review.
Keep those evidence categories distinct in [the current handoff](docs/CURRENT_HANDOFF.md).

## Analytics operations

[Local analytics operations](docs/ANALYTICS_OPERATIONS.md) is the operator guide for the
optional app analytics service, not a website feature. Follow its setup checks and inspect
the dry run before an authorised monthly export. Use one private archive outside Git, keep
credentials and user request codes out of repository/logs, and retain the unbilled project.
Monthly statistics need a separate privacy review before long-term storage; suppression alone
does not prove anonymity. User deletion is a separate operator procedure: the tool plans it
but does not submit it, and local reset is not server erasure.

## Release and documentation

[legal-release-map.json](legal-release-map.json) records website-source provenance and release
decisions, retaining historical app-catalog receipts. The current handoff owns publication order;
this source-ownership change does not itself publish a page or submit an app.
The policy date does not assert app availability; a pushed branch is not a published policy.

Read [AGENTS.md](AGENTS.md), [the documentation index](docs/README.md) and
[CURRENT_HANDOFF.md](docs/CURRENT_HANDOFF.md). Dated continuation files are historical only.
Original documentation is retained under docs/history and in Git.
