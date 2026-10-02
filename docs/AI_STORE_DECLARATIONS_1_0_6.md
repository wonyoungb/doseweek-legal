# AI record assistant: store declaration drafts (1.0.6, unpublished)

Drafts for the STORE-PRO step. Nothing here has been entered in App Store Connect or Play
Console, and no readback exists. The owner enters and confirms every item. Sources: PRO-SPEC
2026-10-02 section 8 (critic C19, C20, C21, C22, C24) and compliance section 9.

Texts that users read (privacy section, Terms section, consent screens, What's New) are in
`docs/ai-assistant-content.candidate.json` and `docs/ai-app-copy.candidate.json`. This file
holds only the store-facing declarations, in English.

## 1. Apple

### 1.1 App Review notes

> DoseWeek Pro adds an optional "AI record assistant": a weekly summary of the user's own logs,
> general nutrition ideas and an app-help chat. DoseWeek is a personal wellness log. The
> assistant is not a medical feature and not a medical device.
>
> - Provider: Amazon Bedrock in the Seoul Region (ap-northeast-2), running an Anthropic Claude
>   model in-Region with data retention mode "none" (no storage, no training). Requests are
>   encrypted at the app layer to our server's public key (HPKE), so the CDN sees only
>   ciphertext; our server decrypts them in memory to call Bedrock and logs no content.
>   End-to-end encryption applies to sync and backup only, and the app says so.
> - Consent: first use shows a separate consent screen with two unticked boxes that names
>   Amazon Bedrock and the model family. Every request that carries records shows a
>   confirmation sheet listing exactly what is sent, with a preview and Send / Cancel. Users can
>   withdraw in Settings > AI record assistant.
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
| Health & Fitness › Health | Yes | App Functionality | Not linked | No | Record aggregates are sent only on request, held in server memory and discarded; nothing is stored with or keyed to the account |
| User Content › Other User Content (typed questions) | Yes | App Functionality | Not linked | No | Same handling as above |
| Usage Data › Product Interaction | Yes | App Functionality | Linked | No | Monthly usage counts are kept for up to 2 months under an HMAC of the account, so they are linked. Add this type if the current label lacks it |

Apple's definition of "collect" leaves out data that is discarded right after servicing a
request. The health label is still declared, because the assistant is a primary Pro feature
and an under-declared health label is the larger review risk.

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
| Health info | Yes | No | App functionality | Yes | Encrypted in transit. Amazon Bedrock acts as a service provider, so this is not sharing. Mark "processed ephemerally" only if the console offers it and the no-logging proof exists |
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
- The AWS contracting entity for the processor table.
- Readback receipts for Bedrock retention mode "none" and invocation logging off.
- The guideline numbers quoted here come from PRO-SPEC and compliance.md as fetched on
  2026-10-02; read the current guideline text again before submission.
- If mainland China stays in the territory list, Pro is excluded there (PRO-SPEC 2.1, C25).
