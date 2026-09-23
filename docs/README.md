# Documentation index

Start with [the product README](../README.md), [AGENTS](../AGENTS.md) and
[CURRENT_HANDOFF](CURRENT_HANDOFF.md). The handoff owns live execution state.
Read one relevant source; historical plans do not override current contracts.

## Current sources

- [Release map](../legal-release-map.json): website-source provenance and release decisions.
- [Release-date contract](../scripts/legal_release.py): effective date and publication gate.
- [iOS website policy/support source](ios-content.json) and [iOS renderer](../scripts/render_ios.py).
- [Android website policy/page source](android-content.candidate.json) and [Android renderer](../scripts/render_android.py).
- [Help navigation and short steps](help-navigation.json), [home copy](home-content.json)
  and [home renderer](../scripts/render_home.py).
- [Import guide source](../import/content.json) and [import renderer](../scripts/render_import.py).
- [Site checks](../scripts/check_site.py): generated content, links and release consistency.
- [Analytics operations](ANALYTICS_OPERATIONS.md): private monthly export preparation,
  retention review and the separate user-deletion procedure; no live execution implied.

The website owns the full policies; apps retain required consent and minimum instructions.
The product README lists validation commands using these local sources. Legacy app-policy
copies are not inputs for new website edits. CHANGELOG records history, not the current store version.
Use the operator guide for credentials, commands and activation steps rather than copying them
into public pages. The current handoff separates local verification, live-page observations,
store drafts and publication receipts.

## Historical references

The following are preserved snapshots, not current execution instructions:

- [September15 evening handoff](CONTINUATION_2026-09-15_EVENING.md).
- [September15 continuation prompt](CONTINUATION_2026-09-15_NEXT_PROMPT.md).
- [Original second-release candidate decisions](SECOND_RELEASE_CANDIDATE.md).
- [Historical README](history/README-2026-09-21.md).

Do not restart their old launch commands, pending tasks or branches. Keep their original
observations and failed outcomes as evidence; use CURRENT_HANDOFF for what remains today.
