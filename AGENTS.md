# DoseWeek public-page working agreement

## Canonical workspace entry

Before repository work, read the [canonical current handoff](../release/CURRENT_HANDOFF.md),
[workspace entry](../START_HERE.md), and relevant [release journal](../release/release-journal.json) entries.
They own recorded live status across repositories. Honor an `OWNER_PAUSE_RELAUNCH` stop;
historical local notes do not authorize restarting code, native tests or release actions.
The current user request remains authoritative. Keep the technical contracts below intact.

## Work without repeating completed work

1. Read `docs/CURRENT_HANDOFF.md`, inspect Git status, and verify any recorded live process or
   external state. Read only the relevant technical contract; old handoffs are not launch instructions.
2. Diagnose a failure from retained logs and inputs before editing, then exercise its related
   family before another whole suite. A second unexplained failure needs a new evidence-backed
   hypothesis or an explicit blocker. Preserve assertions and failed evidence. Change time budgets
   only from measured execution and retained scope; never hide failures with retries or more time.
   Do not erase caches without evidence of corruption, unless the user explicitly authorizes
   cleanup and an exact inactive-cache allowlist plus source/proof-preservation receipts define
   its scope. Preserve sources, secrets, signed artifacts, unique results and device data; record
   the actual cleanup outcome without claiming an estimated size as reclaimed space.
3. Freeze source, tests, runners, SDK and fixtures for a gate. Run the agreed release scope.
   Reuse completed coverage; do not restart a full matrix for an isolated test or documentation
   change. Record owner-approved scope reductions and unresolved failures explicitly. Never
   edit executing scripts or test inputs.
4. Reuse results only for matching relevant source, test/runner, artifact, toolchain/runtime,
   fixture and configuration hashes. Record the scope-to-input comparison; partial runs cover
   only explicitly completed cases. A new session, commit or documentation-only change does not
   by itself require discovery, a full build or another native gate.
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

## Verification evidence

Before treating a check or screenshot as evidence, verify the check's dependencies and required
outputs. A command's success does not prove complete coverage or valid capture bytes. Preserve
failed/cancelled outcomes, validate every required artifact, and inspect the expected page/state.
Resume any recorded live process before replacing it; wait for owned cleanup before reusing output
paths. Keep canonical-source parity and publication gates intact when integrating documentation.
Record requested and completed routes/locales/checks separately; missing, skipped, inaccessible
or failed checks cannot be counted as PASS. An inaccessible live site is `LIVE_SITE_NOT_VERIFIED`,
not proof of an outage. A successful local render or old live GET does not prove the new copy
is public. Reuse browser/source receipts only after comparing the relevant source, generated
HTML, CSS and verification inputs; documentation-only edits do not invalidate matching evidence.

## Content and publication boundary

This is a static site. No analytics, trackers, remote fonts, accounts or form backend.
Owner instruction 2026-09-23: the website owns complete help/privacy wording in
docs/ios-content.json and docs/android-content.candidate.json. Generated pages must match those
sources. Apps keep required consent and minimum instructions and link to the platform website;
do not copy a full policy change back into app catalogs. During the UI transition, preserve
legacy app-policy resources until their readers and guards are retired by the native owner.
Keep substantive disclosures aligned with actual app behavior. Preserve all 17 locales, RTL,
stable hash links, no-JavaScript fallback, source attribution and local-link checks.
Shared help navigation belongs to `docs/help-navigation.json`; home and import copy keep the
sources listed in README. Edit source before rendering, never fix generated HTML alone. When
several owners share a renderer or JSON file, agree on separate fields/functions and sequence
writes, preserving the other owner's input hashes. Regenerate all affected pages after shared
CSS/navigation changes and verify source/output parity.

The Android ML Kit exception covers only consented selected food-label OCR/barcodes and its
disclosed SDK metrics. It does not apply to iOS, generative AI, or this static website.
Do not rewrite legal attributions or claim a native-speaker review without evidence.

Before publication, run the website-source/render/site checks documented in README.md, then the
release-date gate. Align the effective date, website sources, generated pages and release map.
Follow the release owner's current authorised upload/publication order recorded in the handoff;
main may publish the site. Existing user authorisation remains authoritative. Keep dated build
IDs and external state in the current handoff/release map, not as permanent rules here.

## Private analytics operations

Use `docs/ANALYTICS_OPERATIONS.md` for app analytics exports and deletion requests. Keep tokens,
user identifiers, request codes and report responses outside Git and public content. Preserve
the tool's default dry run, single-archive duplicate protection and cost boundary; execute only
within the owner's existing authorisation. Synthetic checks are not real API or deletion proof.
Do not label a minimised monthly result anonymous or approved for indefinite retention without
the contextual privacy review, or claim a deletion request timestamp proves completed erasure.
