# DoseWeek 1.0.6 legal operations — unpublished release requirements

Owner: Wonyoung Labs, sole proprietorship; representative and privacy officer Wonyoung Choi.
Support: wonyoung@wonyoungchoi.dev. This procedure is a prepared operating contract, not proof
that notices, deletion, provider agreements or Store exclusions are operational.
The current handoff and account candidate readiness flags own release status.

## Incident response

1. Record discovery time, source, affected versions, countries and estimated affected people in
   an access-controlled incident record outside Git. Stop the affected disclosure, preserve
   evidence and restrict access. Include unauthorized SDK disclosure and accidental sharing,
   not only intrusion. Do not put identifiers, health records or credentials in public logs.
2. Assess ciphertext, usable keys, readable account/purchase data and health-revealing metadata
   separately. Encryption does not automatically remove breach duties. Identify each controller
   and processor, notify the controller without undue delay and obtain processor cooperation.
3. Korea: notify affected people without delay with the items, occurrence/discovery time,
   circumstances, protective actions, remedies and contact. Assess PIPC/KISA reporting within
   72 hours: sensitive-data breaches or qualifying unlawful external access can trigger it
   independently of the 1,000-person threshold. If permitted initial details are incomplete,
   send the required initial notice/report and promptly supplement; retain the legal reason
   for any delay. Do not borrow the FTC 60-day ceiling for Korean notice.
4. EU/UK: preserve applicable duties for existing users even though 1.0.6 sales are excluded.
   Assess GDPR/UK GDPR authority reporting within 72 hours of awareness where required;
   document reasons for delay. Assess notice to individuals without undue delay where high risk.
   Document a decision not to notify and the evidence supporting it; security of ciphertext is
   part of that assessment, not an automatic exemption.
5. US: evaluate whether DoseWeek is a covered vendor under the FTC Health Breach Notification
   Rule, and each processor's role. Individual notice is without unreasonable delay and no
   later than 60 calendar days after discovery. For 500 or more affected people, notify FTC at
   the same time as individuals. For fewer than 500, keep the incident log and report to FTC
   within 60 days after the calendar year ends. For 500 or more affected residents of a state
   or jurisdiction, give required media notice within the same individual-notice period.
6. Prepare plain notice with what happened and dates, exposed categories, potentially exposed
   recipients, protective actions, mitigation and contact procedures. Apply the rule's electronic
   notice requirements (including required conspicuous notices where applicable), individual
   first-class mail/email choices, and substitute notice for insufficient contact details.
   Assess state-specific shorter obligations and lawful law-enforcement delays separately.
7. Track delivery, regulator filings, affected-recipient follow-up, correction and completion.
   Have the responsible operator/counsel approve applicability and contents. Operational
   readiness requires a tested contact/escalation route and dated private receipts; drafting
   this file does not set breachProcedureOperational=true.

## Deletion and hybrid-backup acceptance

- Daily app-data backup: encrypt before upload to Amazon S3 in Seoul (ap-northeast-2).
  Distinguish device E2EE payloads from backup encryption: account/purchase metadata may be
  readable to the operator after backup decryption. A weekly OS recovery snapshot is separate
  and have the same personal-data deletion bound.
- Requested deletion or health-consent withdrawal makes covered data unavailable immediately
  and removes active copies without delay; never wait for Plus expiry. Full account deletion
  remains possible during an active subscription. Store cancellation is a separate action.
- Automatic expiry purge is anchored to the Store-confirmed end +30 days, with an entitlement
  recheck before purge. Rechecks do not reset that end. A Store outage can add at most 7 days.
- Remove deleted personal data from every relevant backup within 7 days, including object versions, replicas, temporary exports, logs/caches and snapshots that contain it. Do not
  treat S3 lifecycle alone as actual deletion proof: expiration is asynchronous and old
  versions/manual snapshots may remain. Preserve failed cleanup evidence.
- Before release, demonstrate bounded independent cleanup, disabled or explicitly covered
  versioning/replication/Object Lock, no legacy automatic snapshots, snapshot expiration and
  actual deletion readback. The supplied backup research proposes a conservative independent
  cutoff of 143 hours with hourly cleanup and lifecycle no longer than 6 days; receipt of that
  configuration and a failed-job recovery test are required, not assumed from this document.
- Keep the minimal deletion ledger outside the restorable dataset. Reapply deletions before
  restore becomes accessible; verify deleted records cannot reappear. Keep no unjustified
  identifiers indefinitely in that ledger. Retain a dated private restore/deletion receipt.
- Rights requests use the minimum identity/provider information, without passwords, recovery
  codes, health records or purchase tokens. Support email is request transport; send a separate
  completion confirmation. Do not call an email timestamp completed erasure.

## Rights, transfers and recurring charges

- Korean access response: normally within 10 days, with lawful postponement/refusal notice,
  reason and objection route. EU/UK rights normally within one month, including applicable
  machine-readable portability; PDF reporting alone does not prove portability. Apply the US
  health-policy state clocks to confirmed/authenticated requests and downstream deletion.
- Preserve only transaction evidence whose category, legal basis and finite retention are
  established; quarantine it from ordinary use. Korean e-commerce records, where held, use
  statutory categories: contract/withdrawal and payment/supply 5 years, complaints/disputes
  3 years, advertising 6 months. Purchase tombstone/replay records need their own justified
  expiry; hashes are not automatically anonymous. Store custody does not prove DoseWeek holds
  those records. No blanket indefinite retention.
- Complete recipient entity/contact, destination countries, timing/method, data, legal basis,
  purpose, finite active/log/cache/backup periods, refusal/effect and subprocessors before
  release. Cloudflare/AWS processor contracts and actual access/announcement paths need proof.
  Optional analytics/independent advertising are not automatically contract-necessary transfers;
  consent-dependent transmissions wait for consent. Paid Plus alone is not proof of lawful refusal.
- For 1.0.6, EU/EEA, UK and Switzerland are excluded from sale; there is no EU/UK representative
  appointed for this version. Obtain actual Store availability readback before release
  (`salesRegionExclusionsVerified` remains false until that proof). Existing installations may
  continue; preserve applicable rights and safeguards for existing users. Maintain applicable
  EU/UK processor agreements, processing records, onward-transfer mechanisms and DPIA assessment
  where high risk. Assess representative duties before any future reopening, without treating
  the sales exclusion as an automatic exemption for existing processing.
  Korea adequacy is not global onward-transfer authorization. Assess Japan special-care
  consent/foreign-transfer information and Brazil specific highlighted consent/ANPD mechanisms.
- Before payment show actual Store eligibility, one-calendar-month trial, selected full annual
  or monthly price, billing cycle, renewal and simple cancellation. No hidden mandatory pricing,
  preselected add-ons, obstructed cancellation or repeated interference. If relying on the
  Korean repeated-prompt exception, provide effective suppression for at least 7 days.
- Korean conversion/price increase needs affirmative consent within the preceding 30-day window,
  required price/date/payment/cancellation information and no conversion without consent.
  Preserve statutory withdrawal/refund rights; apply service/digital-content refund timing.
- Verify Store/owner coverage for conditional Korean annual continuous-transaction 50–20-day
  renewal notice, California annual initial-term renewal 15–45-day notice, fee changes 7–30
  days before and annual reminders. A genuine one-month trial is not automatically a >31-day
  trial. Record any uncovered owner notification obligation before release.

## Commercial copy parity and prior users

The prior-buyer claim/code program is retired. No separate prior-buyer Plus grant is offered.
Core features remain Free for new and prior users; standard Store-confirmed trials, statutory
rights and review of historical ad-free rights remain. Do not advertise claim/evidence/appeal
or code issuance flows as pending activation.

Late owner decisions require USD 1.99/month and USD 13.99/year; Korea KRW 3,300/month
and KRW 19,900/year; Japan JPY 300/month and JPY 1,980/year; other storefronts use
store-converted prices. The fixed Store-managed free trial is one calendar month for eligible
first-time subscribers; it auto-renews and can be cancelled any time in the store.
Commercial parity remains BLOCKED until the orchestrator obtains matching committed policy,
review copy and verification inputs with partner check receipts.
[Commercial parity record](COMMERCIAL_COPY_PARITY_1_0_6.json) links immutable committed snapshots
and the concrete next action. `commercialCopyParityVerified` stays false. Use Store-returned native
UI prices; static copy does not prove actual Store configuration. No decision is reopened.

## Publication gate

Every source/render/site check must pass; effective date, 17-locale parity, native/provider
behavior, operational facts and deletion route publication require separate owner evidence.
No EU/UK representative appointment is a 1.0.6 publication prerequisite under the decided
excluded-market scope. Store availability readback and applicable existing-user safeguards
remain unverified; a future market reopening needs a separate applicability review. Unknown
supplier details cannot be filled with guessed countries or periods. No publication is authorized
by this lane. Console/store/account-type/trader declarations and medical classification are
orchestrator follow-ups; no native, provider, legal or native-speaker certification is claimed.
