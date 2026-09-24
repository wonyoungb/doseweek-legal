# Documentation index

Start with the [README](../README.md), [AGENTS.md](../AGENTS.md) and
[CURRENT_HANDOFF.md](CURRENT_HANDOFF.md). The handoff points to the live workspace status.

## Content sources

- [iOS policy and support](ios-content.json), rendered by [render_ios.py](../scripts/render_ios.py).
- [Android policy and pages](android-content.candidate.json), rendered by
  [render_android.py](../scripts/render_android.py).
- [Home copy](home-content.json) and [help navigation](help-navigation.json), rendered by
  [render_home.py](../scripts/render_home.py). The platform renderers share the help navigation.
- [Import guide](../import/content.json), rendered by [render_import.py](../scripts/render_import.py).
- [Release constants](../scripts/legal_release.py): the effective date and the food-data
  attribution lines.

## Checks and records

- [Site checks](../scripts/check_site.py): generated pages, local links, locales and
  disclosures. `--release` also requires the effective date.
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
