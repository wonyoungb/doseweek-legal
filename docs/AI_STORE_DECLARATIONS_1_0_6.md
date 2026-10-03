# AI record assistant: store declaration drafts (1.0.6, unpublished)

Drafts for the STORE-PRO step. Nothing here has been entered in App Store Connect or Play
Console, and no readback exists. The owner enters and confirms every item. Sources: PRO-SPEC
2026-10-02 section 8 (critic C19, C20, C21, C22, C24) and compliance section 9.

ai-consent-v3 (2026-10-03, owner decision: Pro AI ships on Gemini through Google with a
cross-border transfer consent). The provider facts below come from Google's published
documentation and terms, saved with SHA-256 in the lane evidence `FACTS.md`
(release/evidence/1.0.6/CODEX-LANES-20261002/codex-takeover-20261003/legal-self-review/claude-20261003).
The owner decided both switches on 2026-10-03 (late-decisions.md, 17:35 and 19:00 KST; wording
rule 19:10 KST). Replace every [SWITCH] mark with the selected wording:

- SWITCH_LOCATION = global (SELECTED): "location Global (Google's global endpoint). Google
  states that such requests "may be processed in any Google Cloud location around the world".
  The country where the content is processed can change with each request, depending on which
  Google servers handle it; Google decides this, so the country cannot be fixed or named in
  advance. Of the named recipients, Google LLC is located in the United States and Google Asia
  Pacific Pte. Ltd. in Singapore".
  Not selected, SWITCH_LOCATION = us: "with AI processing and storage in the United States
  (Google Cloud multi-region us; under Google's terms other processing may take place in other
  countries where Google or its subprocessors have facilities)".
- SWITCH_AWS_GUARDRAIL = off (SELECTED): nothing more; the recipient is Google only. This text
  must not be submitted while the server still calls the Amazon Web Services Guardrail
  (readiness.serverGuardrailCallRemovedReadback). Not selected, SWITCH_AWS_GUARDRAIL = on: add
  "Answer text in English, Spanish and French is also checked by Amazon Web Services in Seoul."

Texts that users read (privacy section, Terms section, consent screens, What's New) are in
`docs/ai-assistant-content.candidate.json` and `docs/ai-app-copy.candidate.json`. This file
holds only the store-facing declarations, in English.

## 1. Apple

### 1.1 App Review notes

> DoseWeek Pro adds an optional "AI record assistant": a weekly summary of the user's own logs,
> general nutrition ideas and an app-help chat. DoseWeek is a personal wellness log. The
> assistant is not a medical feature and not a medical device.
>
> - Provider: Google. Gemini, a Google AI model, on Google Cloud Vertex AI (Google now calls the
>   platform Gemini Enterprise Agent Platform), [SWITCH location]. Google acts as our processor
>   under its Cloud Data Processing Addendum; for a billing address in the Republic of Korea,
>   Google's published terms name Google Cloud Korea LLC as the contracting entity, with Google
>   Asia Pacific Pte. Ltd. and its affiliates including Google LLC. Google does not use the content to train AI models. Google may hold it in memory
>   for up to 24 hours, and may store a prompt for up to 90 days if its automated abuse checks
>   flag it; authorized Google staff may review a flagged prompt. Our server keeps no content.
>   [SWITCH guardrail]
> - Requests are encrypted at the app layer to our server's public key (HPKE), so the CDN sees
>   only ciphertext; our server (Seoul, Republic of Korea) decrypts them in memory to call
>   Google and logs no content. End-to-end encryption applies to sync and backup only, and the
>   app says so.
> - Consent: first use shows a separate consent screen with three unticked boxes (health
>   information, transfer of the information to Google in another country, age 18 or older).
>   The screen names Google, Gemini and the country [SWITCH location], and states the recipient,
>   the items, the purpose, the retention and how to refuse. It is shown on every storefront.
>   Every request that carries records shows a confirmation sheet listing exactly what is sent,
>   with a preview and Send / Cancel. Users can withdraw in Settings > AI record assistant.
> - Apple Health (HealthKit) data is never sent to the AI.
> - The assistant gives no dose, side-effect, diagnosis or drug advice. Such questions return a
>   fixed message telling the user to talk to a clinician (try: "주사 용량을 늘려도 될까요?").
>   Every answer is labelled as AI-generated and as not medical advice, and has a Report button.
> - The AI requires a declared age of 18 or older.
> - The other Pro benefits work without the AI consent.
> - Sign-in for review: {REVIEWER_SIGN_IN}. The sandbox Pro purchase unlocks the assistant.
>   Pro is in the same subscription group as Plus.
> - Path: Today > "이번 주 AI 요약" (weekly AI summary).

`{REVIEWER_SIGN_IN}` is filled by the owner at submission (sign-in method or demo account).
Never commit an account, a password or a token to this repository.

Each new Pro subscription product also needs its own App Review screenshot (the Pro paywall)
and review note, and both Pro products are attached to the app version submission (C21).

### 1.2 App Privacy answers (conservative; not tracking)

| Data type | Collected | Purpose | Linked to the user | Tracking | Rationale |
|---|---|---|---|---|---|
| Health & Fitness › Health | Yes | App Functionality | Not linked | No | Record aggregates are sent only on request. Our server holds them in memory and discards them. Google, our processor, may hold them in memory for up to 24 hours and may store a flagged prompt for up to 90 days; nothing is stored with or keyed to the account |
| User Content › Other User Content (typed questions) | Yes | App Functionality | Not linked | No | Same handling as above |
| Usage Data › Product Interaction | Yes | App Functionality | Linked | No | Monthly usage counts are kept for up to 2 months under an HMAC of the account, so they are linked. Add this type if the current label lacks it |

Apple's definition of "collect" leaves out data that is discarded right after servicing a
request. With Google's 24-hour memory cache and its abuse-review log of up to 90 days that
exemption cannot be relied on, so the health label is declared. Apple guideline 5.1.2(i) also
asks for explicit permission before personal data is shared with third-party AI: Screen A names
Google and asks for it.

### 1.3 Age rating

Answer the questionnaire again counting the AI feature. Keep 16+ worldwide and 15+ in Korea
unless the owner chooses 18+. The assistant has its own declared-age gate of 18.

### 1.4 Guideline 5.1.1(ix)

Residual risk: the guideline says apps with healthcare or sensitive data "should be submitted
by a legal entity", not an individual developer. The review notes describe DoseWeek as a
personal wellness log, not a healthcare service. The organization conversion (D-U-N-S on file
with the owner) is the fallback if App Review cites 5.1.1(ix). The same holds for Google Play's
organization-account requirement for health apps.

### 1.5 What's New (Guideline 2.3.12)

Guideline 2.3.12 requires new features to be described, so the AI feature is listed with one
neutral line. The line never mentions ads, Plus, Pro or any paid tier, subscriptions, prices
or trials (owner rule 2026-10-02), and never names Android or Google Play. The 17-locale line
is `locales.<code>.whatsNew` in `docs/ai-app-copy.candidate.json`. The owner sees it at gate 6.

## 2. Google Play

### 2.1 Data safety

| Data type | Collected | Shared | Purpose | Optional | Notes |
|---|---|---|---|---|---|
| Health info | Yes | No | App functionality | Yes | Encrypted in transit. Google (Gemini on Google Cloud Vertex AI) acts as a service provider under its Cloud Data Processing Addendum, so this is not sharing. Do NOT mark "processed ephemerally": Google may hold the content in memory for up to 24 hours and may store a flagged prompt for up to 90 days |
| Other user-generated content (typed questions) | Yes | No | App functionality | Yes | Same handling |
| App activity › App interactions | Yes | No | App functionality | No | Monthly usage counts under an HMAC of the account, kept up to 2 months |

### 2.2 Health apps declaration

Add: "AI-assisted wellness features: on request, the app creates a weekly summary of the
user's own records, general nutrition ideas and app-help answers. It gives no diagnosis,
treatment or dosing advice." Keep the existing categories truthful (medication and treatment
tracking, nutrition). State: "Health Connect data is not used by the AI feature."

### 2.3 App description

Keep the exact non-medical-device disclaimer and "consult a healthcare professional".
Describe the AI as record summaries and general meal ideas. Where Pro is described, mention
the separate consent and the limit of 150 requests a month.

### 2.4 AI-Generated Content

Every AI output has an in-app Report control, reached without leaving the app. Note its
location in the App access instructions: the Report button under each answer on the AI record
assistant screen and on the weekly AI summary card.

### 2.5 App access

Provide a license-tester account with Pro ({REVIEWER_SIGN_IN}, filled by the owner in the
console only), the steps to reach the assistant (Today > weekly AI summary), and the example
refusal prompt "주사 용량을 늘려도 될까요?".

### 2.6 Release notes

Use the same neutral line as on the App Store.

## 3. Listing and marketing rules

Never claim: "AI 상담", "맞춤 처방", "부작용 관리", "체중 감량 효과", "종단간 암호화로 AI까지
보호", "무제한". The product name is "AI 기록 도우미" (EN "AI record assistant") and the
human-support perk is "우선 문의 답변": a first reply to app-use questions within 1 business
day, never medical answers.

## 4. Open before submission

- Console entry and readback of every table above (owner-gated).
- Replace every [SWITCH] mark above with the selected wording (SWITCH_LOCATION = global,
  SWITCH_AWS_GUARDRAIL = off). The owner accepted on 2026-10-03 19:00 KST that the Korean
  transfer notice cannot name one country for location Global.
- Readback that the deployed server makes no Amazon Web Services Guardrail call, before any
  declaration that names Google as the only recipient is submitted.
- The DoseWeek server location (Seoul, Republic of Korea) is sourced: an AWS Lightsail instance in
  the Seoul Region, lane receipt server-hardening-20261003/receipt.md.
- The Google contracting entity on an invoice or in the billing console of project
  doseweek-507313. A read-only billing-account describe on 2026-10-03 shows currency KRW and no
  entity or address field, so the draft only repeats what Google's terms name for a billing
  address in South Korea (Google Cloud Korea LLC, marked there as an authorized reseller).
- Readback of the Google project settings: in-memory cache (default on, 24 hours) and
  request-response logging (default off). No abuse-monitoring exception has been requested, so
  no zero-data-retention claim is made anywhere.
- If the guardrail switch is on: the Amazon Web Services contracting entity for the Seoul
  Guardrail.
- The guideline numbers quoted here come from PRO-SPEC and compliance.md as fetched on
  2026-10-02; read the current guideline text again before submission.
- If mainland China stays in the territory list, Pro is excluded there (PRO-SPEC 2.1, C25).
