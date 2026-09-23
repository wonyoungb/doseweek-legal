# Current legal-site handoff — 2026-09-23

**Local website checks: scoped PASS. Candidate pages: UNPUBLISHED.** Current cross-repository
execution, store state and publication decisions belong to the release owner's
[handoff](../../CURRENT_HANDOFF.md) and [journal](../../release-journal.json). Historical blocks
below are observations, not instructions to restart work.

Current website candidate metadata remains Android 1.0.0/code12 and iOS 1.0.5/build17;
the release owner records actual native build/upload status. Both bundled food locks/manifests
match release `291c3210df94d6f9f6f470122b2ffefcfd40d04e23051948c9e4874d35b53697`.
The 9,913-record catalog includes 200 foods with names in 17 languages. Both help pages describe
offline search, the initial all-language search and the language setting; attribution is unchanged.
The committed food/help update regenerated seven pages and passed `check_site.py --release`.

The reviewed brand update changes README and two platform icon PNGs to use the original
five-layer syringe from `../ios/DoseDay/Resources/AppIcon.icon`. The iOS web PNG matches its
Icon Composer marketing export; the Android web PNG matches the Play PNG. Both match the current
brand manifest. This review changed only this handoff, four current catalog hash fields and
the iOS candidate note in `legal-release-map.json`. Root confirms source17 and a compiled Debug
simulator build17; final Release archive/export/upload remain pending, and ASC build16 is a
separate prior candidate. Candidate identifiers, publication fields and all seven HTML files are preserved.

## Current ownership and changes

The website owns complete 17-locale help/privacy text in [iOS source](ios-content.json),
[Android source](android-content.candidate.json), and the home/import sources listed in
[README](../README.md). [Help navigation](help-navigation.json) supplies short steps and locale
links. Apps retain required consent and minimum context, with the combined settings entry
opening the platform home; consent can link directly to policy. Legacy app-policy resources
are not the source of new website edits.

The local policy includes optional analytics and separate optional transfer consent, technical
telemetry and source-labelled possible country scope, two-month user/event retention,
withdrawal/local-reset limits, user-prepared request codes, and Android 18+. Existing health,
backup, medical and platform-specific disclosures remain. The local effective date is
2026-09-23; it does not establish an app release or public-page update.

[Analytics operations](ANALYTICS_OPERATIONS.md) now documents the local monthly exporter and
separate deletion planning. Code and synthetic validation exist; real report/API execution,
operator OAuth/access setup, production archive/reminder and a contextual long-term privacy
decision remain activation items. No Google reply or paid service is required merely to
continue release work. An unchecked amendment checkbox alone does not establish DPA status.

## Evidence and reuse

- [Current local visual and metadata review](../../evidence/lean-20260923/legal-help-brand-visual-20260923/receipt.json):
  both support pages at 320px, all 34 locale answers match source and fit horizontally;
  Korean light and Arabic RTL dark screenshots show the changed copy and current brand.
  All 284 declared local links/assets/anchors resolve. Four stale catalog hashes were corrected
  with a focused validator; the iOS source/Debug17 note was also reconciled with root readback.
  No renderer rerun was needed. Initial collapsed-FAQ observations,
  a locator timeout and the corrected bundle-path check are retained separately from PASS.
- [Committed food/help update](../../evidence/lean-20260923/legal-food-release-20260923/receipt.json):
  four renderers and strict seven-page release check passed. Current HTML matches that receipt;
  five pages were unchanged by the food update. Both 22-file food bundles still match its hashes.
- [Earlier help/site inputs](../../evidence/lean-20260923/legal-help-20260923/final-inputs.json):
  shared CSS and the unaffected page content retain their earlier coverage. The new icon pixels
  are covered by the current support-header checks, not by old screenshots. Earlier clipping
  failures and corrected screenshots remain preserved; no new full-site or no-JavaScript sweep.
- [Policy integration](../../evidence/lean-20260923/privacy-operations-candidate/actual-policy-integration/validation.json):
  17-language source/generation review. Local structure and browser observations are separate
  from native-speaker review, accessibility certification and public deployment.
- [Analytics operations receipt](../../evidence/lean-20260923/privacy-operations-candidate/monthly-export-integration/final-receipt.json):
  implementation, synthetic checks and unexecuted activation steps; not proof of a real report,
  server deletion or anonymous long-term retention.
- [Store declaration candidate](../../evidence/lean-20260923/store-privacy-final-declarations/MATRIX.md):
  candidate App Privacy/Data Safety mapping and SDK evidence limits, not a store publication.
- [Earlier documentation receipt](../../evidence/lean-20260923/legal-docs-final-20260923/receipt.json):
  the historical four-file documentation edit and its focused validation.

Existing public URLs remain stable. Earlier live GET receipts describe the pages observed then;
they do not prove this candidate is deployed. This review used a loopback-only server and a new
owned browser tab, both now closed; temporary viewport/media overrides were cleared. Public
availability is `LIVE_SITE_NOT_VERIFIED` for this review. No native, store or publication action.

## Owner and next action

Review-base legal branch: `codex/help-privacy-20260923`; HEAD:
`0ec408e6233cda2c8361c28c71121d0491fe3242`. Root reports the normal push to draft
[PR #4](https://github.com/wonyoungb/doseweek-legal/pull/4); this review did not query or change
GitHub. Reviewed files: README, two brand PNGs, this handoff and `legal-release-map.json`.
Other owners' work is preserved. This task owns no active process/device.

Next: root commit/push the reviewed brand/documentation/metadata changes and reconcile final build
metadata and SDK/consent evidence with store answers. Keep the authorised order: native notices before final
build/signing, both accepted immutable uploads before site publication. After publication,
record real URL/version/content readback. Do not re-run matching site/native evidence merely
because these documentation links changed, or copy the full policies back into app catalogs.

## Historical local snapshots — superseded by the current block


Current local candidate update — 2026-09-23: 17-language Firebase/privacy and platform-specific widget disclosures are applied locally. No public publication or store declaration update has occurred. iOS app catalog application, actual SDK/consent/network proof, complete cross-border/DPA and deletion workflow, and final release date/build mapping remain required. Do not apply the older widget-only patch over this merged candidate. Current source of truth: ../../CURRENT_HANDOFF.md and ../../release-journal.json from this docs directory; evidence ../../evidence/lean-20260923/firebase-privacy-applied.json.

### Historical early 2026-09-23 legal continuation

Current main was read with `git ls-remote`: `acfb1083857441d3762d1e5406015504954a319f`. Its committed tree matches this worktree HEAD `2a140d5c77767c1e6827d86ddd18a4a1d19bdb5a`; do not remerge or repeat branch deletion.
Android canonical policy and mirror remain byte-identical at SHA256 `28946a2bb250a852dd3cab76f99b71b974f9c047771fad0fcd5ee1736098c924`. The iOS catalog now adds two widget-only keys; all existing values, including the complete privacy subset, remain unchanged (see `../evidence/lean-20260923/widget-catalog-delta.json`). Reuse concerns the policy subset, not the changed whole-file hash. Prior exact-source 7-page legal gate is reused; no fresh browser/accessibility or store-state PASS is claimed.
Canonical live task and evidence: `../CURRENT_HANDOFF.md`, `../release-journal.json`, `../evidence/lean-20260923` relative to this repository root. User authorizes normal release work after required gates and substitutes emulator checks for phone checks; that is not physical-device proof. Public copy is unchanged.

## Historical 2026-09-22 handoff — prior observations only

### Historical legal-site handoff

Updated: 2026-09-22
Status: WORKING; no candidate publication in this continuation.

- Branch: codex/privacy-completion-20260920. Use Git HEAD for the exact current commit.
- Current iOS and Android policy mirrors passed structural/catalog parity on 2026-09-21.
  Both support routes and the supported import guide cover all 17 locales. Native-speaker
  review and browser/accessibility observations remain separate evidence categories.
- The bundled food release is 680bce02fff6f08ab25e27b18caef32f0b978becaec13fa4e7e97e349e0f387b.
- The Android food-label-only ML Kit disclosure is included; it does not authorize Nano,
  cloud OCR or iOS SDK telemetry. Keep the canonical app policy and store answers aligned.
- SECOND_RELEASE_EFFECTIVE_DATE is 2026-09-22. Owner approved date/catalog alignment BEFORE
  final builds/signing → both accepted uploads → site publication. Supersedes 2026-09-17 order.
- iOS candidate 1.0.5/build16 and Android 1.0.0/code11 are not uploaded by this work yet.
  Store state must be refreshed before the next mutation; a branch push is not public availability.
- Completed: shorter shared platform chooser in all17 guide locales with versioned guide labels;
  responsive typography and natural CJK/Arabic/Hindi heading spacing. Content-hashed CSS URLs
  prevent stale shared styles. Four render/catalog/site checks pass. Home68 viewport/locale
  and secondary18 narrow route/locale checks show no clipping. All outgoing home links keep
  their locale; import-to-home no longer falls back to English for14 locales. Representative light/dark,
  RTL, keyboard focus, help navigation and no-JavaScript observations are retained in
  ../evidence/continuation-20260921/homepage/locales17-progress.json; not full accessibility proof.
- Documentation reconciled; preserve docs/history and treat dated prompts as history.

Next action: retain final catalog/site checks, then wait for both accepted app-upload receipts
before main integration/publication. Do not merge an unready
legal candidate into a branch that publishes the site.
