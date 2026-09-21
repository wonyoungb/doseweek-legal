# Documentation index

Start with [the product README](../README.md), [AGENTS](../AGENTS.md) and
[CURRENT_HANDOFF](CURRENT_HANDOFF.md). The handoff owns live execution state.
Read one relevant source; historical plans do not override current contracts.

## Current sources

- [Release map](../legal-release-map.json): catalog provenance and release decisions.
- [Release-date contract](../scripts/legal_release.py): effective date and publication gate.
- [iOS catalog mirror](ios-content.json) and [iOS renderer](../scripts/render_ios.py).
- [Android catalog mirror](android-content.candidate.json) and [Android renderer](../scripts/render_android.py).
- [Site checks](../scripts/check_site.py): generated content, links and release consistency.

App catalogs own substantive privacy wording. The product README lists the exact validation
commands and upstream source paths. CHANGELOG records history, not the current store version.

## Historical references

The following are preserved snapshots, not current execution instructions:

- [September15 evening handoff](CONTINUATION_2026-09-15_EVENING.md).
- [September15 continuation prompt](CONTINUATION_2026-09-15_NEXT_PROMPT.md).
- [Original second-release candidate decisions](SECOND_RELEASE_CANDIDATE.md).
- [Historical README](history/README-2026-09-21.md).

Do not restart their old launch commands, pending tasks or branches. Keep their original
observations and failed outcomes as evidence; use CURRENT_HANDOFF for what remains today.
