# Documentation index

Start with the [README](../README.md), [AGENTS.md](../AGENTS.md) and
[CURRENT_HANDOFF.md](CURRENT_HANDOFF.md). The handoff points to the live workspace status.

## Content sources

- [iOS policy and support](ios-content.json), rendered by [render_ios.py](../scripts/render_ios.py).
- [Android policy and pages](android-content.candidate.json), rendered by
  [render_android.py](../scripts/render_android.py).
- [Home copy](home-content.json) and [help navigation](help-navigation.json), rendered by
  [render_home.py](../scripts/render_home.py). The platform renderers share the help navigation;
  each platform source holds its own six-step getting-started guide (`support.guide`).
- [Import guide](../import/content.json), rendered by [render_import.py](../scripts/render_import.py).
- [Terms of Use](terms-content.json) for both apps (candidate for the monetization release), rendered
  by [render_terms.py](../scripts/render_terms.py). Its medical section reuses the iOS disclaimer
  wording verbatim.
- [Account, encrypted sync and announcement copy](account-sync-content.candidate.json) is an
  unpublished 17-locale 1.0.6 draft, including the planned account-deletion web-page copy. It is
  not rendered into the effective pages. [render_account_sync.py](../scripts/render_account_sync.py)
  stages separate1.0.6 sources and local pages, including support-email account-deletion initiation
  without Plus or reinstall; it refuses output into the public checkout. [Release review](ACCOUNT_SYNC_RELEASE_REVIEW.md) lists
  source conflicts, store declarations, primary sources and operational blockers.
- Per-language pages (`/<locale>/<route>`), hreflang links and the sitemap:
  [locale_pages.py](../scripts/locale_pages.py), used by every renderer, and
  [render_sitemap.py](../scripts/render_sitemap.py). The README explains the hash pages and the
  language pages.
- [Release constants](../scripts/legal_release.py): the live and next effective dates, the
  release placeholders that must be replaced before publication, and the food-data attribution
  lines.

- [US Consumer Health Data Privacy Policy](us-health-content.json) is a separate 17-locale
  1.0.6 candidate rendered by `scripts/render_us_health.py` at `/us-health/`. Both privacy
  policies link to it; all new copy remains unpublished.
- [Legal operations](LEGAL_OPERATIONS_1_0_6.md) defines incident notices, deletion/backup proof,
  rights, processor contracts and regional subscription notice gates. It does not prove execution.

## Checks and records

- [Site checks](../scripts/check_site.py): generated pages, hreflang clusters, the sitemap,
  local links, locales and disclosures, and that every locale carries the same release
  placeholders as en. `--release` also requires the effective date and refuses the release
  placeholders in every locale. It also refuses an unintegrated account/sync candidate.
- [Release map](../legal-release-map.json): where the website sources came from, and the
  release decisions.
- [CHANGELOG](../CHANGELOG.md): site history.

## Operations

- [Analytics operations](ANALYTICS_OPERATIONS.md): operator guide for the apps' optional
  analytics, covering monthly exports, retention review and deletion requests. It is not a
  website feature, and it does not mean any of these operations have been run. Keep
  credentials and user request codes out of Git.

The website owns the full policy text. The apps keep the required consent screens and short
instructions. Old app-policy copies are not inputs for website edits. Past handoffs and snapshots
were removed from the tree and are kept in Git history.
