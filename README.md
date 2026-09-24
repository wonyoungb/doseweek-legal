# DoseWeek help and privacy site

Static help, support, privacy and record-import pages for the DoseWeek iOS and Android apps,
served at <https://doseweek-legal.wonyoungchoi.dev/>.

GitHub Pages publishes the root of `main`. Any other branch, a pushed commit or a local render is
a candidate only: it is not public until it is merged to `main` and the live page is checked.
[docs/CURRENT_HANDOFF.md](docs/CURRENT_HANDOFF.md) points to the live status and publication order.

## Pages

| Route | Content |
|---|---|
| `/` | Shared home: choose a platform, short help tasks |
| `/support/`, `/privacy/` | iOS support (six-step getting-started guide, then FAQ) and privacy policy |
| `/android/`, `/android/support/`, `/android/privacy/` | Android overview, support (getting-started guide, then FAQ) and privacy policy |
| `/import/` | Guide for importing records from another app, with localized prompt and format downloads |

Every route covers 17 locales: ko, en, ja, de, fr, es, it, nl, pt-PT, pl, sv, hi, pt-BR, ar,
zh-Hans, zh-Hant and tr. The URL hash selects the locale (for example `/support/#ar`). Keep
Arabic right-to-left, the separate Portuguese and Chinese variants, stable hash links and the
no-JavaScript fallback.

## Privacy stance

- **This website** is plain HTML and CSS with two small local scripts (`assets/language.js`,
  `assets/import.js`). It has no analytics, trackers, third-party scripts, remote fonts,
  cookies, accounts or form backend.
- **The apps** need no DoseWeek account and show no ads. As the policy sources in `docs/`
  describe, the upcoming app releases add optional usage analytics (Google Analytics for
  Firebase). It is off by default and starts only after the user agrees to analytics and,
  separately, to overseas transfer.
- The website owns the full policy text. The apps keep the required consent screens and short
  instructions, and link here. Policy text must match what the apps actually do.

## Requirements

- Python 3, standard library only. There is no package install and no build step. Checked
  with Python 3.14.
- A browser for visual review. The scripts check structure, not appearance.

## Generate and check

Edit the source first, then render. Do not hand-edit generated HTML.

| Source | Renderer | Output |
|---|---|---|
| `docs/home-content.json`, `templates/home.html` | `scripts/render_home.py` | `index.html` |
| `docs/help-navigation.json` | shared by the home and platform renderers | help cards and guide headings; the guide steps live in each platform source (`support.guide`) |
| `docs/ios-content.json` | `scripts/render_ios.py` | `privacy/`, `support/` |
| `docs/android-content.candidate.json` | `scripts/render_android.py` | `android/**` |
| `import/content.json` | `scripts/render_import.py` | `import/index.html`, `import/*.md`, `import/draft-v1.schema.json`, `import/draft.example.json` |
| effective date, food-data attributions | `scripts/legal_release.py` | used by the iOS and Android renderers and `check_site.py` |

Render (writes files). After changing CSS or shared navigation, run all four:

```bash
python3 scripts/render_home.py
python3 scripts/render_ios.py
python3 scripts/render_android.py
python3 scripts/render_import.py --require-all-locales
```

Check (read-only):

```bash
python3 scripts/render_home.py --check
python3 scripts/render_ios.py --check
python3 scripts/render_android.py --check
python3 scripts/render_import.py --check --require-all-locales
python3 scripts/check_site.py            # pages, local links, locales, disclosures
python3 scripts/check_site.py --release  # also requires the policy effective date
(cd scripts && python3 -m unittest test_render_paragraphs test_privacy_ops)
```

`render_ios.py --catalog <path>` is an optional legacy comparison against old app resources. It
is not a release gate.

## Repository layout

```text
index.html, privacy/, support/, android/, import/   generated pages (served)
assets/          stylesheets, local scripts, app icons
docs/            content sources (*.json) and maintainer docs
templates/       home page template
scripts/         renderers, site checks, analytics-operations tool, unit tests
legal-release-map.json   release provenance and decisions
CNAME            custom domain for GitHub Pages
```

## Brand assets

`assets/app-icon.png` is an Icon Composer render of the iOS app icon.
`assets/android-app-icon.png` is the Google Play icon. `render_android.py` compares it with (or
copies) the Play icon only when `--content` points to the Play catalog
(`DoseweekPlayStore/docs/legal/android-content.json`). With the default source it neither compares
nor rewrites the icon. No script in this repository writes `assets/app-icon.png`.

## Documentation

- [AGENTS.md](AGENTS.md): working rules for people and AI agents
- [docs/README.md](docs/README.md): documentation index
- [docs/CURRENT_HANDOFF.md](docs/CURRENT_HANDOFF.md): pointer to the live workspace handoff
- [docs/ANALYTICS_OPERATIONS.md](docs/ANALYTICS_OPERATIONS.md): operator guide for the apps'
  analytics exports and deletion requests (not a website feature)
- [CHANGELOG.md](CHANGELOG.md): site history

Older handoffs, continuation prompts and snapshots were removed from the tree. They remain in
Git history.

## Notices

- Food-data attribution lines (USDA FoodData Central, PHE CoFID, Japan MEXT, Korea MFDS) are
  kept verbatim in `scripts/legal_release.py` and rendered on both privacy policies.
- Support contact: wonyoung@wonyoungchoi.dev.
- This repository has no LICENSE file.
