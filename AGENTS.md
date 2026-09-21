# DoseWeek public-page working agreement

## Work without repeating completed work

1. Read `docs/CURRENT_HANDOFF.md`, inspect Git status, and verify any recorded live process or
   external state. Read only the relevant technical contract; old handoffs are not launch instructions.
2. Diagnose a failure from retained logs and inputs before editing. Fix the responsible layer,
   then exercise the related failure family. Preserve assertions and failing evidence. Do not
   retry an entire suite because the first run failed, or erase caches without evidence of corruption.
3. Freeze source, tests, runners, SDK and fixtures for a gate. Run the agreed release scope.
   Reuse completed coverage; do not restart a full matrix for an isolated test or documentation
   change. Record owner-approved scope reductions and unresolved failures explicitly. Never
   edit executing scripts or test inputs.
4. Reuse results with matching relevant input hashes. A new session, commit or documentation-only
   change does not by itself require another native gate. Record the input comparison and limits.
5. After each meaningful edit, completed check, commit/push or store action, update the existing
   handoff/journal. Before context handoff or an observed approaching usage limit, save the exact
   next action, branch/HEAD, owned dirty files, input hashes, result/evidence paths, active
   PID/device/log ownership, external state and blockers. Do not leave a second competing status ledger.
6. Keep README for product/setup, AGENTS for durable rules, CURRENT_HANDOFF for live state,
   and dated history for evidence. Update affected docs with behavior. Do not copy volatile test
   totals or branch IDs into NEXT_AI_PROMPT, README or several other entrypoints.

Use deterministic scripts for counts, hashes and inventories; retain raw logs outside the chat.
Load skills only when they match the task. Respect a request to work without delegation.
Preserve originals and unrelated work; no reset/stash/clean, force push or global process kills.
Report executed, failed, skipped, blocked and historical results separately. An uploaded artifact
is not a submitted release, and a submission is not public availability.

## Content and publication boundary

This is a static site. No analytics, trackers, remote fonts, accounts or form backend.
iOS privacy strings originate in the iOS app catalog; Android policy originates in the Android
app's docs/legal/android-content.json. Mirrors and generated pages must match those sources.
Do not change substantive privacy wording on the website alone. Preserve all 17 locales, RTL,
stable hash links, no-JavaScript fallback, source attribution and local-link checks.

The Android ML Kit exception covers only consented selected food-label OCR/barcodes and its
disclosed SDK metrics. It does not apply to iOS, generative AI, or this static website.
Do not rewrite legal attributions or claim a native-speaker review without evidence.

Before publication, run the catalog/render/site checks documented in README.md, then the
release-date gate. Owner decision 2026-09-22: align the effective date, app catalogs, mirrors,
pages and release map BEFORE final builds/signing. Then upload both immutable artifacts;
publish only after both uploads are accepted. main may publish the site.
Current observations live in docs/CURRENT_HANDOFF.md and legal-release-map.json.
