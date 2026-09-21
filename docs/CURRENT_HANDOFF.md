# Current legal-site handoff

Updated: 2026-09-21T23:38:26.333033+09:00
Status: WORKING; no candidate publication in this continuation.

- Branch: codex/privacy-completion-20260920. Use Git HEAD for the exact current commit.
- Current iOS and Android policy mirrors passed structural/catalog parity on 2026-09-21.
  Both support routes and the supported import guide cover all 17 locales. Native-speaker
  review and browser/accessibility observations remain separate evidence categories.
- The bundled food release is 680bce02fff6f08ab25e27b18caef32f0b978becaec13fa4e7e97e349e0f387b.
- The Android food-label-only ML Kit disclosure is included; it does not authorize Nano,
  cloud OCR or iOS SDK telemetry. Keep the canonical app policy and store answers aligned.
- SECOND_RELEASE_EFFECTIVE_DATE remains unset. The approved order is both store uploads,
  then consistent effective-date update, release gate, main integration and publication.
- iOS candidate 1.0.5/build16 and Android 1.0.0/code11 are not uploaded by this work yet.
  Store state must be refreshed before the next mutation; a branch push is not public availability.
- Completed: shorter Korean/English/Japanese platform chooser with versioned guide labels;
  responsive typography and natural CJK/Arabic/Hindi heading spacing. Content-hashed CSS URLs
  prevent stale shared styles. Four render/catalog/site checks pass. Home12 viewport/locale
  and secondary18 narrow route/locale checks show no clipping. Representative light/dark,
  RTL, keyboard focus, help navigation and no-JavaScript observations are retained in
  ../evidence/continuation-20260921/homepage/browser-proof.json; not full accessibility proof.
- Documentation reconciled; preserve docs/history and treat dated prompts as history.

Next action: finish current documentation/site checks; retain their exact evidence, then follow
accepted app-upload receipts to the effective-date/publication step. Do not merge an unready
legal candidate into a branch that publishes the site.
