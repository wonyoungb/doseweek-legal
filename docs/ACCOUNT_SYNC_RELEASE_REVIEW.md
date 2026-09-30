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

The current account/provider/Plus/health-sync service remains **OFF**. Server lifecycle, signed Plus assertions, shared record adapters and retention sweep have source candidates and bounded synthetic checks. They are not a verified production service. Real provider configuration, store/native assertion handling, full record graph/settings cut and restore, native key custody, TLS/deployment, request-independent pruning and backup erasure still require their corresponding proof. The staged17locale sources render target behavior under an explicit unpublished/OFF heading; the public release gate continues to reject them. No local output proves that a URL, provider unlink or server deletion works in production.

The existing Terms draft describes monthly and annual auto-renewing Plus. The owner selected an
**in-app claim followed by purchase verification before** distributing an individual one-month
code to an eligible prior paid-app purchaser. After the free month, the code offer is to renew
as **monthly Plus** unless the buyer cancels through the store. The redemption screen and
store offer must show the actual monthly price, billing period, renewal date and cancellation
path before acceptance. This is a design decision, not a live offer. On iOS, a verified signed
StoreKit `AppTransaction.originalAppVersion` can identify the version first acquired; its
eligibility cutoff and refund/Family Sharing treatment need a test. On Android, a user-supplied
paid-app order ID could be verified by the server using the Google Play Orders API's
`paidAppDetails` and order state; a `LICENSED` result alone does not prove a paid order. An
order ID also does not prove that its submitter was the buyer. The owner decided that if this
identity link cannot be proved automatically, the request goes to manual review and dispute
handling without automatic code issuance. Orders API access, order-ID discovery by users,
duplicate claims, refunds and one-code-per-eligible-
purchase enforcement still need implementation and sandbox/real-account proof. Claiming would
process an account-linked app transaction ID or order ID and verification outcome. Define the
minimum fields, purpose, recipient, storage security, log exclusion, retention and deletion in
the final policy and store declarations before enabling it. The code's post-month renewal and
price must be made clear in the actual store offer. No candidate page promises an issued code.
Account deletion must remain available without Plus and must clearly say that it does not cancel
store billing.

The owner has resolved the earlier paid-buyer policy question: original primary features remain Free, but **perpetual ad-free use is not guaranteed**. Prior paid acquisition alone starts neither a Plus subscription nor a charge. The requested verified one-month Plus code→monthly auto-renewing program remains a design, with no delivery promise before the actual store offer and claim path can be operated. Acquiring the app by a promotional code alone is not evidence of actual payment; buyer identity and actual paid acquisition must be established, with Android manual review/disputes when they cannot be proved automatically.

Apple’s [App Review Guidelines §3.1.2(a)](https://developer.apple.com/app-store/review/guidelines/) were reopened on2026-09-30. They say “should not take away the primary functionality existing users have already paid for.” The guideline does not expressly decide whether this app’s past ad-free promise is primary functionality. The owner’s no-perpetual-ad-free choice settles the product decision; **counsel/platform review of the original sales representation and consumer rights remains a release blocker**. A one-month trial alone is not proof of compliance. Verify original-feature restore, paid-versus-promo acquisition, refunds and Family Sharing without assuming the owner choice is legally cleared.

## Historical public-source and staged integration inventory

The preserved public inputs and144pages describe the historical no-account app. The deterministic `scripts/render_account_sync.py` now reconciles the following fields in separate1.0.6 sources and108local review pages (privacy/help for each platform, Terms, deletion; hash +17locales). It uses the existing renderers, keeps effectiveDate null and marks each page unpublished/OFF. This does not replace effective public sources or prove service readiness.

| Source | Fields that currently conflict or omit the new behavior |
|---|---|
| `ios-content.json` | `privacy.storage`, `privacy.backups`, `privacy.deletion`, `privacy.purchases`; support `released.backup`, `released.deletion`, `plus.features` and `plus.manage` need account/sync/deletion paths. iOS purchases currently says the app sends no purchase data to the developer and the server has no account linkage. Confirm the implemented token path before replacing it. |
| `android-content.candidate.json` | `privacy.scope`, `no-collection`, `backup`, `purchases`, `retention`, `security`; support FAQ `accounts`, `backup`, `deletion`, `recovery`, `plus-features` and `plus-restore`. Existing manual file and Google Drive features stay distinct; cross-platform server sync is a third path. |
| `terms-content.json` | `free-plus`, `billing`, `records` currently say no cross-platform account and only local records. Add optional account, server sync entitlement, recovery-code loss and deletion consequences without changing store cancellation/refund language. |
| Generated pages | `/privacy/`, `/support/`, `/android/privacy/`, `/android/support/`, `/terms/` and their 17 language pages are still generated from the old sources. Do not hand-edit them. |

The purchase-verification server and the new account service may share infrastructure, but their
data uses differ. The new account records cannot be described as only hashed purchase tokens.
The independently reviewed source candidate now also persists server-only AES-256-GCM
purchase lookup references (Apple original transaction ID or Play purchase token) under
separate private vault keys, in addition to keyed purchase digests. The server decrypts
these references solely to recheck Store status; this is distinct from end-to-end health
records whose recovery keys never reach it. Account deletion erases the references and
retains keyed purchase tombstones with the account link removed to prevent duplicate
ownership claims; this is not a claim that the markers are legally anonymous.
An hourly expiry/pruning sweep is an independently reviewed source candidate. Scheduled execution, bounded lag and actual deployment are unproved. Required automatic erasure
without app requests, tombstone legal basis and retention limit remain release blockers. Source review
and synthetic/local HTTP tests do not prove real Store calls, cron execution or deletion of
operational backups. The 17-locale candidate now discloses this distinction; native-speaker
and counsel review remain pending.

The owner-provided Lightsail address and SSH key do not prove server region, processor terms,
retention or that the API is live. Record those facts from the actual deployment and contract.

## Account deletion web request source and release route

Target: `https://doseweek-legal.wonyoungchoi.dev/account/delete/`, with17locale routes and stable locale hashes. The staged page prominently identifies DoseWeek and provides the existing public support address `wonyoung@wonyoungchoi.dev` as a working `mailto:` request action and visible address. A user can initiate the request without reinstalling the app, purchasing Plus, or first canceling billing. Only the sign-in provider and known DoseWeek account ID are requested; support explains identity verification before erasure. Passwords, health data, recovery codes and purchase tokens must not be mailed. Drafting/sending mail is not confirmation of account deletion. No real message was sent, no mailbox response or deletion was exercised, and the route is not published.

[Google Play’s official account-deletion guidance](https://support.google.com/googleplay/android-developer/answer/13327111?hl=en), reopened2026-09-30, permits a customer-service email as an external request pathway. A functional, prominent request route naming the app is required even when the app can be used without an account. A deployed authenticated API is **not a prerequisite for an email request page**. Publication, mailbox ownership/handling, identity verification, reasonably prompt actual account-associated-data erasure and final Console URL/readback remain gates. The existing verified public contact link establishes the address only, not operational deletion proof or platform approval.

App initiation still needs Settings→Account→Delete account with a truthful confirmation/result. Account/server erasure is distinct from provider unlinking and store billing cancellation. Apple refresh capability uses a separate server encryption key; Kakao unlink token is request-only and not retained. Show provider results separately and provide manual provider-account removal instructions if disconnection fails or is unconfirmed; no automatic retry is promised. Preserve distinct local/exported/Drive deletion paths,30day Plus-expiry retention, any legally justified retention, and operational backup erasure limits. Native/provider/TLS/backup-deletion proof is NOT_RUN/BLOCKED.

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
3. Record the real Lightsail region/operator, processor DPA and AWS role/subcontractors, IP/access-log fields
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

## 2026-09-30 provider lifecycle disclosure reconciliation

All17 unpublished locales now distinguish Apple server-encrypted refresh capability from health-record E2EE keys, request-only non-retained Kakao unlink access token, and local/account-data deletion from provider-disconnection outcome. A provider failure requires explicit manual instructions; no background retry is promised. This is planned OFF behavior, not a production claim.

Isolated server lifecycle d615 has123 synthetic test passes but independent review blocks activation: concurrent link/delete, multiple provider identities/capability coverage and proxy/client deadlines need repaired immutable review. Existing primary hourly retention sweep is source-only; request-independent deployment, at-most-one-hour sweep lag, monitoring and operational backup erasure remain unproven. Account deletion must erase health ciphertext/account references and show the truthful provider result; no health/recovery data may be sent to support. Counsel, real provider revocation, native response UI, effective date and public deletion route remain release gates.

## Local staged renderer packet (2026-09-30)

Run `python3 scripts/render_account_sync.py --output <review-directory-outside-this-checkout>`. The generator refuses the public checkout. Sources are materialized in the review directory’s `sources/`; affected108pages have exact route/locale SHA receipts in `render-receipt.json`. Existing public144outputs are preserved; only the two changed baseline renderers were checked for backward byte parity (36iOS+54Android). No historical whole144site rerun is required solely by this continuation. Final release needs counsel/effective date/operator-DPA-transfers, verified account/Plus/full19native/settings/recovery/provider/deletion/retention behavior, store declarations, final localized UI labels and native-speaker review. Nothing is committed, pushed, deployed or published by this packet owner.

Independent review follow-up: the staged iOS help introduction inherited the original no-account denial. The staging transform now replaces that entire localized lead with the existing OFF and optional-account source in all17locales. The failing-first regression, eight related passing methods, exact18changed help-page hashes, and EN/KO source/output checks are retained in the packet. Original effective sources/pages remain preserved; source verification is not browser visual or production availability.
