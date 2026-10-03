# DoseWeek help and privacy site

Static help, support, privacy, terms and record-import pages for the DoseWeek iOS and Android apps,
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
| `/terms/` | Terms of Use for both apps (free version with ads, Plus subscription, App Store and Google Play billing). Published 2026-10-03 by `scripts/publish_release.py` |
| `/<locale>/…` | The same nine routes once per locale, one language per page (for example `/ar/support/`, `/zh-Hant/android/privacy/`) |
| `/us-health/` | Separate US Consumer Health Data Privacy Policy, with consent, recipients and state rights; published 2026-10-03 by `scripts/publish_release.py` |
| `/robots.txt`, `/sitemap.xml` | Search discovery. The sitemap lists all 162 pages (9 routes x the hash page and 17 language pages), each with its hreflang alternates; `check_site.py` keeps it equal to the generated pages |
| `/app-ads.txt` | AdMob authorized seller record. Keep the publisher ID equal to the snippet in the owner's AdMob account; publish this plain-text file at the domain root |

Every route covers 17 locales: ko, en, ja, de, fr, es, it, nl, pt-PT, pl, sv, hi, pt-BR, ar,
zh-Hans, zh-Hant and tr. Keep Arabic right-to-left, the separate Portuguese and Chinese
variants, stable hash links and the no-JavaScript fallback.

Each route has two kinds of page:

- **The hash page** (`/support/`, `/privacy/#ko`, …) holds all 17 languages. The URL hash
  selects the locale (for example `/support/#ar`); without JavaScript it shows Korean, and a
  hash link still opens its language. The apps and store listings link to these pages, so their
  URLs and hash links must keep working. Each hash page stays canonical and is the `x-default`
  of its route.
- **The language pages** (`/<locale>/<route>`) show one language each, so search engines see
  one language per URL: `<html lang>` (and `dir="rtl"` for Arabic), a self-referencing canonical
  link, a localized title and description, and links to the same page in the other languages.
  They need no JavaScript; `assets/language.js` only scrolls the current language into view.

Every page of a route lists the same 18 `<link rel="alternate" hreflang>` links: the 17 language
pages and `x-default` (the hash page). Language folders use the exact locale tags of the hash
links (`pt-PT`, `zh-Hans`); GitHub Pages is case-sensitive, so `/pt-pt/` is not an alias.

A language page's title is the title the hash page's script sets for that panel. Descriptions
reuse existing localized copy, one field per route:

| Route | Description source |
|---|---|
| `/<locale>/` | `docs/home-content.json` `intro` |
| `/<locale>/support/`, `/<locale>/privacy/` | `docs/ios-content.json` `support.labels.lead`, `privacy.intro` |
| `/<locale>/android/` | `docs/home-content.json` `androidBody` |
| `/<locale>/android/support/`, `/<locale>/android/privacy/` | `docs/android-content.candidate.json` `home.supportLinkBody`, `home.privacyLinkBody` |
| `/<locale>/import/` | `import/content.json` `lead` |
| `/<locale>/terms/` | `docs/terms-content.json` `intro` |
| `/<locale>/us-health/` | `docs/us-health-content.json` `intro` |

## Privacy stance

- **This website** is plain HTML and CSS with two small local scripts (`assets/language.js`,
  `assets/import.js`). It has no analytics, trackers, third-party scripts, remote fonts,
  cookies, accounts or form backend.
- **The apps** support basic local recording without a DoseWeek account. As the policy sources in `docs/` describe, the 1.0.5
  app releases add optional usage analytics (Google Analytics for Firebase). It is off by default
  and starts only after the user agrees to analytics and, separately, to overseas transfer. The
  live 1.0.5 apps are paid downloads without ads. The candidate sources on this branch describe
  the next release, a free download that shows non-personalized ads (Google Mobile Ads SDK with
  Google's consent platform) to Free users, with an optional Plus subscription; that copy is not
  published.
- A separate [1.0.6 account/sync disclosure draft](docs/ACCOUNT_SYNC_RELEASE_REVIEW.md) covers
  optional sign-in and Plus-only encrypted sync requested by the owner. The API, deletion web
  flow and updated policy are not public or verified; the release check blocks publication
  until the draft is reconciled with the implementation and all 17 languages.
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
| `docs/home-content.json`, `templates/home.html` | `scripts/render_home.py` | `index.html`, `<locale>/index.html` |
| `docs/help-navigation.json` | shared by the home and platform renderers | help cards and guide headings; the guide steps live in each platform source (`support.guide`) |
| `docs/ios-content.json` | `scripts/render_ios.py` | `privacy/`, `support/`, `<locale>/privacy/`, `<locale>/support/` |
| `docs/android-content.candidate.json` | `scripts/render_android.py` | `android/**`, `<locale>/android/**` |
| `docs/terms-content.json` (medical section reuses `docs/ios-content.json` wording) | `scripts/render_terms.py` | `terms/index.html`, `<locale>/terms/index.html` |
| `docs/us-health-content.json` | `scripts/render_us_health.py` | `us-health/index.html`, `<locale>/us-health/index.html` |
| `import/content.json` | `scripts/render_import.py` | `import/index.html`, `<locale>/import/index.html`, `import/*.md`, `import/draft-v1.schema.json`, `import/draft.example.json` |
| locales, routes, hreflang links, language-page shell | `scripts/locale_pages.py` (shared) and `scripts/render_sitemap.py` | the language pages' head and navigation, `sitemap.xml` |
| effective dates, release placeholders, food-data attributions | `scripts/legal_release.py` | used by the iOS, Android and Terms renderers and `check_site.py` |

Render (writes files). After changing CSS, `assets/language.js` or shared navigation, run all
seven:

```bash
python3 scripts/render_home.py
python3 scripts/render_ios.py
python3 scripts/render_android.py
python3 scripts/render_import.py --require-all-locales
python3 scripts/render_terms.py
python3 scripts/render_us_health.py
python3 scripts/render_sitemap.py
```

Check (read-only):

```bash
python3 scripts/render_home.py --check
python3 scripts/render_ios.py --check
python3 scripts/render_android.py --check
python3 scripts/render_import.py --check --require-all-locales
python3 scripts/render_terms.py --check
python3 scripts/render_us_health.py --check
python3 scripts/render_sitemap.py --check
python3 scripts/check_site.py            # pages, hreflang, sitemap, local links, locales, disclosures, Korean tone
python3 scripts/account_sync_candidate.py
python3 scripts/ai_assistant_candidate.py       # unpublished Pro AI record assistant sources
python3 scripts/render_account_sync.py --check  # in-memory unpublished 1.0.6 sources/pages
python3 scripts/korean_tone.py           # Korean 해요체 voice check alone (lists violations)
python3 scripts/check_site.py --release  # also requires the release effective date and no release placeholders
python3 scripts/publish_release.py --check  # published state: public pages == base sources + overlays + owner decisions (docs/published)
python3 -m unittest discover -s scripts -p 'test_*.py'
```

`render_ios.py --catalog <path>` is an optional legacy comparison against old app resources. It
is not a release gate.

Korean copy follows the owner's plain 해요체 voice (2026-09-25). `check_site.py` runs the
`korean_tone.py` self-tests and fails on any Korean sentence that breaks the shared rules in
`scripts/korean_tone_rules.json`. Add an entry to `scripts/korean_tone_allowlist.json` only for a
reviewed exception, with its key, rule, match and reason.

Unpublished account/legal integration can be reviewed with
`python3 scripts/render_account_sync.py --output /absolute/path/to/local-review-directory`.
The output must be outside this checkout. `--check` validates all staged pages in memory without writing. It materializes separate 1.0.6 privacy/help/Terms
sources and a localized account-deletion request route using the existing public support
email. Its effective date stays null, pages carry an unpublished/OFF notice, and requesting
by email does not prove completed erasure. Original served pages are preserved. See
[the account release review](docs/ACCOUNT_SYNC_RELEASE_REVIEW.md) for publication gates.

## Repository layout

```text
index.html, privacy/, support/, android/, import/, terms/, us-health/   generated hash pages (served)
ko/, en/, … zh-Hant/, tr/                           generated language pages (served)
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
- [docs/CURRENT_HANDOFF.md](docs/CURRENT_HANDOFF.md): pointer to the live workspace handoff,
  a short dated site status and the link to the 1.0.6 plan
- [docs/ANALYTICS_OPERATIONS.md](docs/ANALYTICS_OPERATIONS.md): operator guide for the apps'
  analytics exports and deletion requests (not a website feature)
- [CHANGELOG.md](CHANGELOG.md): site history

Older handoffs, continuation prompts and snapshots were removed from the tree. They remain in
Git history.

Prepared 1.0.6 disclosures include the Wonyoung Labs operator, separate health-sync consent,
processor/transfer tables, regional rights, daily encrypted S3 Seoul backups and manual pre-deploy OS
snapshots with the seven-day deletion limit, trial/subscription terms and a separate US policy.
1.0.6 excludes EU/EEA, UK and Switzerland sales and has no appointed EU/UK representative;
applicable existing-user rights and safeguards remain. Supplier facts, actual Store exclusions
and native/operational behavior remain gated. The
[legal operations procedure](docs/LEGAL_OPERATIONS_1_0_6.md) defines the breach/deletion/rights
work required before publication; it is not a claim that those operations have been run.

## Notices

- Food-data attribution lines (USDA FoodData Central, PHE CoFID, Japan MEXT, Korea MFDS) are
  kept verbatim in `scripts/legal_release.py` and rendered on both privacy policies.
- Support contact: wonyoung@wonyoungchoi.dev.
- [LICENSE](LICENSE): proprietary, all rights reserved. Third-party material keeps its own
  license.
