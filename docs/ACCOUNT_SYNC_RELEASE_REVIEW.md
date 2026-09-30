# 1.0.6 account, sync and public-notice disclosure review — unpublished candidate

Status: **BLOCKED for publication** (2026-09-30). This is implementation and legal-review
material, not a statement that the service is operating. The 17 translated candidate paragraphs,
including the deletion-page copy, are in `account-sync-content.candidate.json`; no native-speaker
review is claimed.

## Owner decisions to preserve

- Apple, Google and Kakao sign-in is optional. Existing local record features remain usable
  without a DoseWeek account. A sign-in prompt must not interrupt an existing user's records.
- Only a server-verified Plus account may use automatic cloud sync. Plus bought on either store,
  when linked to the same DoseWeek account, grants the full Plus benefits on both platforms:
  ad removal, Plus tools and encrypted sync. Both apps continue to offer their own store's
  subscription purchase and management. A sign-in alone does not grant Plus.
- Sync includes the user's full record graph and supported settings, encrypted **on the device**
  before upload. The server holds account/provider identifiers, verified Plus state, ciphertext,
  revision/access metadata and no plaintext health content or recovery code. A high-entropy code
  is needed to restore on a new device. An empty device can restore after code confirmation; a
  device with local records must preview and confirm a merge, not overwrite silently.
- Plus expiry stops new sync; encrypted server backups remain for 30 days, then are deleted.
  Account deletion targets immediate removal of account and associated server ciphertext, with
  a truthful pending/completed state. Local data, independently exported files and the existing
  optional Google Drive backup have separate deletion paths. Account deletion does not cancel
  Apple or Google billing.
- Public announcements may appear at launch before onboarding, with a per-ID seven-day local
  snooze. The planned feed is `https://doseweek.wonyoungchoi.dev/announcements/v1.json`.

## Contract checkpoint (2026-09-30)

The candidate API base is `https://doseweek.wonyoungchoi.dev/v1`. The public announcement
feed is a separate, unauthenticated static resource at
`https://doseweek.wonyoungchoi.dev/announcements/v1.json`. Its staged file and the iOS/Android
clients must use the same 17-locale schema and per-notice snooze rules. A network request may
expose an IP address to the hosting layer even though the feed carries no account or health
query data. Neither URL is evidence of a deployed DoseWeek feature.

The current `server/doseweek-cloud` candidate's provider verification has been tested only with
locally generated token fixtures, not real provider configuration. Its
`GET/PUT /v1/sync/snapshot` routes deliberately return 503 because account-
bound Apple/Play Plus verification is absent. Account deletion removes live-store state, but
provider token revocation/unlink, durable backup erasure and a working external deletion flow
are unverified. The protocol defines 30-day post-expiry ciphertext retention and recovery-code
encryption, while the shared lossless iOS/Android record graph, native key management, automatic
backup, merge and restore are not implemented. The public privacy, Terms, help and store forms
must describe these as available only after the corresponding native, server and operational
proof exists. The candidate JSON stays unpublished and the release gate rejects it meanwhile.

The existing Terms draft describes monthly and annual auto-renewing Plus. The owner selected an
**in-app claim followed by purchase verification before** distributing an individual one-month
code to an eligible prior paid-app purchaser. After the free month, the code offer is to renew
as **monthly Plus** unless the buyer cancels through the store. The redemption screen and
store offer must show the actual monthly price, billing period, renewal date and cancellation
path before acceptance. This is a design decision, not a live offer. On iOS, a verified signed
StoreKit `AppTransaction.originalAppVersion` can identify the version first acquired; its
eligibility cutoff and refund/Family Sharing treatment need a test. On Android, a user-supplied
paid-app order ID could be verified by the server using the Google Play Orders API's
`paidAppDetails` and order state; a `LICENSED` result alone does not prove a paid order. Orders
API access, order-ID discovery by users, duplicate claims, refunds and one-code-per-eligible-
purchase enforcement still need implementation and sandbox/real-account proof. Claiming would
process an account-linked app transaction ID or order ID and verification outcome. Define the
minimum fields, purpose, recipient, storage security, log exclusion, retention and deletion in
the final policy and store declarations before enabling it. The code's post-month renewal and
price must be made clear in the actual store offer. No candidate page promises an issued code.
Account deletion must remain available without Plus and must clearly say that it does not cancel
store billing.

## Current-source conflict inventory

The current candidate pages were written for the no-account app. These locations must be
reconciled across **all 17 locales** before rendering the new feature into public pages:

| Source | Fields that currently conflict or omit the new behavior |
|---|---|
| `ios-content.json` | `privacy.storage`, `privacy.backups`, `privacy.deletion`, `privacy.purchases`; support `released.backup`, `released.deletion`, `plus.features` and `plus.manage` need account/sync/deletion paths. iOS purchases currently says the app sends no purchase data to the developer and the server has no account linkage. Confirm the implemented token path before replacing it. |
| `android-content.candidate.json` | `privacy.scope`, `no-collection`, `backup`, `purchases`, `retention`, `security`; support FAQ `accounts`, `backup`, `deletion`, `recovery`, `plus-features` and `plus-restore`. Existing manual file and Google Drive features stay distinct; cross-platform server sync is a third path. |
| `terms-content.json` | `free-plus`, `billing`, `records` currently say no cross-platform account and only local records. Add optional account, server sync entitlement, recovery-code loss and deletion consequences without changing store cancellation/refund language. |
| Generated pages | `/privacy/`, `/support/`, `/android/privacy/`, `/android/support/`, `/terms/` and their 17 language pages are still generated from the old sources. Do not hand-edit them. |

The purchase-verification server and the new account service may share infrastructure, but their
data uses differ. The new account records cannot be described as only hashed purchase tokens.
The owner-provided Lightsail address and SSH key do not prove server region, processor terms,
retention or that the API is live. Record those facts from the actual deployment and contract.

## Account deletion web source and release route

Planned direct route: `https://doseweek-legal.wonyoungchoi.dev/account/delete/`. The final page
must provide a **working** authenticated path to request deletion without reinstalling the app.
The app must also expose Settings → Account → Delete account and confirm the result. The static
site has no account backend or form today; publishing a dead button or a policy-only link would
not meet the Play web-resource requirement. Do not ask for health records or recovery codes in
support mail. A web flow can redirect to the new authenticated API once deployed. It should
show what is deleted, separate device/export/Drive data, the store subscription cancellation
link and any legally required retention. For Kakao-linked accounts the service should request
Kakao unlink and handle provider-initiated unlink webhooks; for Sign in with Apple, revoke
associated tokens. Provider sign-out alone is not DoseWeek account deletion.

Before the route is generated for 17 locales, the API owner must supply its exact deletion
endpoint, auth and reauthentication flow, idempotent deletion receipt, provider revocation
behavior, audit/log and backup erasure limits, and a tested response. The 17-locale candidate
`retention` text is a draft **target**; it must not be published as a completed guarantee.

## Store privacy and Data safety draft

These are **review prompts**, not final Console answers. Fill them from a release-build SDK
inventory and consent-before/after network traces, then read back both consoles.

| Area | Candidate treatment / verification |
|---|---|
| Account identifiers | DoseWeek account ID and Apple/Google/Kakao subject identifiers are developer-collected and linked to an account. Determine whether name/email is requested at all; Apple private relay email is still contact information if collected. Do not claim anonymity. |
| Purchase state | Verified store/plan/expiry and account link are collected for entitlement, fraud control and cross-platform sync. Payment card details remain with the stores; confirm the exact token path. |
| Encrypted health payload | Health records/settings are deliberately sent off device as ciphertext. In Play Data safety, the official E2EE exception may apply **only after proof** no developer, intermediary or provider can decrypt and only sender/recipient hold keys. Account, size, timing, revision and access metadata still need assessment. Apple's App Privacy form has its own collection/readability rules; determine classification from the actual implementation and seek counsel/ASC review rather than importing Play's exception. |
| Ads/analytics | Existing non-personalized GMA/UMP and optional Firebase analytics declarations remain separate. No health data or sync metadata goes to ad targeting. A future tracking/ATT change requires its own owner and legal approval. |
| Announcements | Public feed request can expose IP address, app version, locale and request/access logs. Document actual fields, processor and retention; do not call it data-free. Per-notice snooze stays on device if implementation confirms it. |
| Deletion | Play requires both an in-app path and an external web resource for account deletion; Apple requires an easy in-app initiation. Disclose the 30-day Plus-expiry backup rule separately from immediate account-deletion target and any legal retention exceptions. |
| Security | Verify TLS, on-device authenticated encryption, independent recovery key, rate limits and key-loss behavior. E2EE protects content confidentiality but does not erase account metadata or remove breach/incident duties. |

## Legal and operational gates

1. Korean health data is sensitive information: counsel must confirm the separate consent and
   overseas-transfer/processor basis, including identity providers and any cloud processing.
   PIPA Articles 23, 28-8 and 30 need review against actual data flows. Do not equate E2EE with
   no personal-data processing.
2. Confirm whether the FTC Health Breach Notification Rule and Washington My Health My Data Act
   apply to served users, then document incident/deletion response. E2EE does not by itself
   establish an exemption; classification depends on facts and law.
3. Record the real Lightsail region/operator, AWS role and subcontractors, IP/access-log fields
   and retention, ciphertext/object lifecycle, deletion propagation and backups. AWS uses shared
   responsibility; the developer must secure the instance and app data.
4. Finalize the effective date, all 17 native labels and counsel/native-speaker review. Run every
   renderer, site checks, `--release`, browser inspection and app link validation before any
   publication. The draft PR and local render cannot establish public availability.

## Primary sources checked 2026-09-30

- [Apple App Review Guidelines §§4.8, 5.1](https://developer.apple.com/app-store/review/guidelines/)
  and [Apple account deletion guidance](https://developer.apple.com/support/offering-account-deletion-in-your-app/).
- [Apple Sign in with Apple deletion/token guidance](https://developer.apple.com/documentation/technotes/tn3194-handling-account-deletions-and-revoking-tokens-for-sign-in-with-apple)
  and [App Privacy Details](https://developer.apple.com/app-store/app-privacy-details/).
- [Apple StoreKit AppTransaction business-model change](https://developer.apple.com/documentation/storekit/supporting-business-model-changes-by-using-the-app-transaction)
  and [Google Play Orders API](https://developers.google.com/android-publisher/api-ref/rest/v3/orders).
- [Google Play account-deletion requirements](https://support.google.com/googleplay/android-developer/answer/13327111?hl=en),
  [Data safety disclosure rules and E2EE exception](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en),
  [User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311?hl=en).
- [Kakao Login account deletion and unlink](https://developers.kakao.com/docs/en/kakaologin/common).
- [Korean Personal Information Protection Act](https://law.go.kr/LSW/LsiJoLinkP.do?docType=JO&joNo=001700000&languageType=KO&lsNm=%EA%B0%9C%EC%9D%B8%EC%A0%95%EB%B3%B4+%EB%B3%B4%ED%98%B8%EB%B2%95&paras=1)
  (review current Articles 23, 28-8 and 30 with counsel).
- [AWS Lightsail shared-responsibility guidance](https://docs.aws.amazon.com/lightsail/latest/userguide/security.html),
  [FTC Health Breach Notification Rule guidance](https://www.ftc.gov/business-guidance/resources/complying-ftcs-health-breach-notification-rule-0),
  [Washington AG My Health My Data Act guidance](https://www.atg.wa.gov/protecting-washingtonians-personal-health-data-and-privacy).
