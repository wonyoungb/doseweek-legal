# 1.0.6 account, sync and public-notice disclosure review — unpublished candidate

Status: **BLOCKED for publication** (2026-09-30). This is implementation and legal-review
material, not a statement that the service is operating. The 17 translated candidate paragraphs,
including the deletion-page copy, are in `account-sync-content.candidate.json`; no native-speaker
review is claimed.

## Owner decisions to preserve

- Apple and Google sign-in is optional; these are the only sign-in providers (owner decision
  2026-10-01). Existing local record features remain usable without a DoseWeek account.
  A sign-in prompt must not interrupt an existing user's records.
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

The approved prior-buyer application contract is SOURCE_OFF (`242f0690`, 2026-10-01). Current clients submit only a manual Apple request or a Play request with `orderId:null`; they collect no raw order or AppTransaction evidence, provide no code or price, and cannot grant Plus. No production routes or authorized reviewer operations are established by these source seams. Applications remain unavailable until approved minimal-case handling, retention/deletion, account authority and operational safeguards are qualified. The account-bound application is optional, needs no Plus, and login alone does not submit it.

The three closed application routes expose only current status/revision/reason and permitted appeal. Application, appeal, review approval and code delivery never authorize Plus or advance paidUntil. `approved_pending_offer` means evidence approval with no available offer. Payment and claimant ownership both need independent qualification; Play remains manual review/dispute handling. Acquisition, promo code, version/date, login or an untrusted order hint is not paid ownership. Missing or uncertain evidence does not automatically prove ineligibility. Unknown mutation outcomes reconcile the same case; no automatic duplicate application or false success is promised.

An enabled manual-only service processes account linkage, opaque claim/store identifiers, current status, request/review/appeal receipts and minimal security/audit metadata for verification, appeals and duplicate-claim prevention. Account-linked data is not anonymous. Approved category-specific case/evidence/audit/receipt and duplicate-marker horizons, deletion and backup erasure must be defined before collection; missing policy disables manual-only reads/writes as well as optional proof collection. Account deletion remains available. It removes account-linked cases, receipts, audit and evidence. Any retained verified-purchase duplicate marker needs its separately approved purpose, minimal fields and expiry; no indefinite or anonymity assumption.

Optional future non-null Play references or qualified signed Apple AppTransaction evidence require separate pre-transmission notice/consent, approved collection/retention policy, actual verifier readiness and an independently configured claim-evidence vault. Its server encryption key is distinct from health E2EE, subscription-reference and provider-capability keys. Authorized reviewers can decrypt proof solely for approved review; it is not health E2EE. No health/recovery data, photos, payment-card data or free text is requested. Raw proof/order/key does not enter logs, analytics, response or email. Claim retention never inherits health-backup30days. Actual operator/location/recipients/access controls, category deadlines and backup erasure remain unfilled release gates, with no invented date or duration.

Release-language stages are separate. Current candidate copy says applications and codes are unavailable in present tense. Only after application gates pass may release copy say Free users can sign in, apply, see their own manual review and appeal when permitted; it still says codes are unavailable and approval does not activate Plus. Only a separately qualified store offer may promise a one-month benefit: before acceptance the actual store shows free period, monthly price/currency, renewal date and cancellation, with monthly renewal after that period unless canceled. One-month versus Play30-day semantics require the real offer. Only the verified resulting subscription activates Plus. Actual code stock, unique audited issuance, redemption, claimant/payment verification and no-double-charge handling remain separate gates; no guessed price or automatic issuance.

The owner has resolved the earlier paid-buyer policy question: original primary features remain Free, but **perpetual ad-free use is not guaranteed**. Prior paid acquisition alone starts neither a Plus subscription nor a charge. Current codes are unavailable. The one-month Plus→monthly auto-renewal contract becomes operative only with the verified actual store offer and qualified issuance path. Acquiring the app by a promotional code alone is not evidence of actual payment; buyer identity and actual paid acquisition must be established, with Android manual review/disputes when they cannot be proved automatically.

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

App initiation still needs Settings→Account→Delete account with a truthful confirmation/result. Account/server erasure is distinct from provider unlinking and store billing cancellation. Apple refresh capability uses a separate server encryption key. Show provider results separately and provide manual provider-account removal instructions if disconnection fails or is unconfirmed; no automatic retry is promised. Preserve distinct local/exported/Drive deletion paths,30day Plus-expiry retention, any legally justified retention, and operational backup erasure limits. Native/provider/TLS/backup-deletion proof is NOT_RUN/BLOCKED.

## Store privacy and Data safety draft

These are **review prompts**, not final Console answers. Fill them from a release-build SDK
inventory and consent-before/after network traces, then read back both consoles.

| Area | Candidate treatment / verification |
|---|---|
| Account identifiers | DoseWeek account ID and Apple/Google subject identifiers are developer-collected and linked to an account. Determine whether name/email is requested at all; Apple private relay email is still contact information if collected. Do not claim anonymity. |
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

## 2026-10-01 owner decision: Apple and Google sign-in only

The owner dropped Kakao login ("아니다 카카오 로그인은 빼자"). The
candidate `account` copy in all 17 locales now names only Apple and Google, the Kakao unlink-token
sentence is removed, and the unresolved provider item covers only Apple refresh capability.
`scripts/account_sync_candidate.py` and `check_site.py` now fail if the candidate or a
sign-in-bearing legal source names Kakao. The 2026-09-30 provider reconciliation and primary-source
entries above that mention Kakao are historical.

## 2026-10-02 lane LEGAL-STORE: operator, region, Cloudflare transfer, D8 and backups

Drafted in all 17 locales of `account-sync-content.candidate.json` (no native-speaker or counsel
review claimed). Each fact and its source:

| Fact | Source checked |
|---|---|
| Operator: Wonyoung Choi, individual developer in the Republic of Korea | The current iOS/Android policies' contact and scope sections already name him |
| Account/sync server on AWS Lightsail, Seoul region `ap-northeast-2` | Deploy receipt host `3.36.148.59` (workspace `release/evidence/1.0.6/SERVER-DEPLOY-20261001/receipt.json`) lies in `3.36.0.0/14`, region `ap-northeast-2`, of AWS's published `ip-ranges.json` (createDate `2026-10-01-17-37-06`, read 2026-10-02) |
| Cloudflare proxies every request, terminates TLS and sees tokens and request bodies; named as processor with the PIPA Art. 28-8 particulars (recipient, countries, items, timing/method, purpose, retention, refusal) | Deploy receipt `owner_decisions[1]` ("Cloudflare 유지 + 처리방침에 명시"); DW-WEB README (Cloudflare DNS/proxy) |
| E2EE: server keeps only ciphertext snapshots and the account/purchase records it needs; key stays on devices behind the recovery code | Server `PROTOCOL.md` (client encryption, recovery code) and `README.md` ("never receives a recovery code, plaintext record or app settings") on `next-ai/sync-and-integ` |
| D1: all record kinds (plans and changes, dose records, meals, body measurements, supplies, import history) and supported settings on both platforms | Owner decision D1 (2026-10-01) |
| D8: deleted 30 days after the last server-verified Store end; Store recheck first; outage defers up to 7 days | Server `src/store.js` (`THIRTY_DAYS`, `RETENTION_OUTAGE_DEFERRAL_MS = 7 days`, `settleSnapshotRetention`) and `src/maintenance.js` (`runSnapshotRetention`) |
| Reset sync deletes only the server copy; account deletion deletes everything server-side | `PROTOCOL.md` `DELETE /v1/sync/snapshot`; `store.deleteSnapshot`. The HTTP route is not in the server branch yet (listed as unresolved) |
| Daily Lightsail snapshots, 7 kept: deleted data leaves backups within 7 days | Owner decision round 2 `server_backup` (2026-10-01); `PROTOCOL.md` rollback row. A plan, not a configured readback |

The staged 1.0.6 purchase sections (`render_account_sync.py`) now carry the `processors` text in
place of the two "listed before release" placeholders, so the staged sources hold no
`legal_release.RELEASE_PLACEHOLDERS`. The effective public sources keep them (they describe the
1.0.5 purchase-verification server) until the integrator replaces those sources.

Not stated because not verified, and listed in `unresolvedBeforePublication`: Cloudflare's actual
log retention period (the text points to its own terms), the AWS contracting entity, the host of
the standalone Android purchase-verification server, and Nginx access-log fields/retention
(HOST-07). Counsel must confirm the transfer basis (Articles 23, 28-8 and 30) before publication.
The sync text names "both platforms" rather than iOS and Android because the Android pages'
catalog guard refuses the token "iOS".
