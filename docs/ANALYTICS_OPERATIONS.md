# Local analytics operations

This is operator documentation, not an app notice or a generated help/privacy page. Do not put tokens, request identifiers, real report responses or private exports in this repository. The script uses Python 3.10+ and the standard library; there is no server, paid connector, BigQuery, cloud scheduler or app credential.

## Current state and cost boundary

The 2026-09-23 console receipt records property `555488369`, iOS stream `15827868073`, Android stream `15827890246`, user/event retention of **2 months**, reset on new activity **off**, Firebase **Spark $0** and no BigQuery link. These are recorded console settings, not proof of collection or completed deletion. The retention change has Google's stated 24-hour application delay. Google excludes standard aggregate reports from the user/event retention setting; neither that setting nor this tool guarantees indefinite report availability. [Google retention guidance](https://support.google.com/analytics/answer/7667196?hl=en)

The same receipt (`evidence/lean-20260923/firebase-console-cost-state.json` in the release workspace) records the collection controls that the published iOS and Android policies depend on: Google signals **off**, ads personalization **off** for all regions, granular location and device data **on** by explicit owner choice (this is what supplies the disclosed city, device model and minor OS version), and the Google Analytics data processing terms observed as **not accepted** there, with contract provenance still pending. Do not change any of these settings, or the 2-month/reset-off retention, without first updating both website policy sources and the in-app consent text. They are recorded console observations, not a live readback.

Standard Google Analytics is offered without charge; Analytics 360 is the paid edition. Keep the existing project unbilled and use only the standard Data API. Never attach billing, switch to Blaze/360, enable BigQuery or accept paid support to make this workflow succeed. Stop if setup requires a billing commitment. [Google pricing explanation](https://business.google.com/us/support/)

`runReport` consumes the Core quota. Current standard limits are 200,000 tokens/property/day, 40,000 tokens/property/hour, 14,000 tokens/project/property/hour, 10 concurrent requests and 10 server errors/project/property/hour. Quota tokens measure capacity, not money; their exact consumption is determined by Google. One sequential monthly request uses this existing quota. The tool requests quota metadata but never archives it or attempts a quota purchase, upgrade or automatic retry. [Google quota table, checked 2026-09-23](https://developers.google.com/analytics/devguides/reporting/data/v1/quotas)

## One monthly result, no raw archive

`export-month` sends one fixed request to the existing property's [Data API `runReport`](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport). It queries a completed calendar month, using the **actual property timezone**, at least seven full days after month-end. This buffer is an operating choice, not a Google finality guarantee. Use the eighth day of each month as a manual reminder; no scheduler is installed.

Both app streams are combined into the single metric `activeUsers`, with no output dimensions. GA active users are not verified distinct people: multiple installations, devices, resets and reporting estimation matter. No health content, user/app-instance IDs, device model, city, OS, platform slice, event name, route, daily count, cumulative count or engagement total is exported. [Google metric definitions](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema)

The exact report remains in process memory only. Counts below 20, zero and a report with no rows all yield the same suppressed result. Other counts become ranges of width 20, such as 40–59. Unknown response fields, additional dimensions/metrics, timezone mismatch, sampling, truncation, thresholding and restrictions reject the entire export. Raw response bytes, exact counts, raw-response hashes, credential values and provider error bodies are never written by the exporter. Python memory and OS swap are not secure-erasure guarantees. [Response metadata](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/ResponseMetaData)

The only durable output is an owner-only `YYYY-MM.json` in one designated local archive outside Git, created atomically without replacement. An exclusive month lock prevents concurrent queries to the same archive. An existing month is rejected **before** token access or any new request. A crash may leave a lock or a private temporary file containing only the already-minimised aggregate. Inspect the state and active process before removing a stale lock; never delete a valid monthly result to rerun it. Do not create parallel archives or alternate names for revised counts: comparing versions can reveal information by subtraction. A correction needs an explicit privacy review of all retained versions.

Suppression and bucketing are risk controls, **not proof of anonymisation or a statutory threshold**. Each output retains `privacy_review: PENDING` and `long_term_storage_approved: false`. Before treating a monthly result as anonymous for long-term retention, assess the health-app context, audience size, people with multiple installations, auxiliary information, all other retained statistics and access controls. Keep a separate decision record containing month, reviewer/date and retain/discard outcome, with no participant details or exact count. Do not modify or duplicate the statistical output. If reasonable identification/inference risk remains, discard it or use a separately justified finite personal-data schedule; do not label it anonymous or retain it indefinitely by default. The Korean statutory test considers identification using other information with reasonable time, cost and technology. [PIPA Article 58-2](https://law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1022694479)

## Prepare once; execution remains off by default

Before the first real export:

1. Read back the property's timezone, standard edition, the two stream IDs and reporting identity. Record consent/collection scope separately; do not infer collection from registration. Keep the 2-month/reset-off settings and Spark/no-billing boundary. The exporter verifies the timezone returned by Google but does not read Admin settings itself.
2. Confirm the Google Analytics Data API is enabled in the existing project and the operator can view this property. If absent, enable only this API through the normal owner-authorised setup; no such action was executed by this implementation. [Google setup guide](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart)
3. Use an authorised operator OAuth client to obtain a **short-lived access token** with `https://www.googleapis.com/auth/analytics.readonly`. A desktop OAuth client and browser consent, if not already configured, remain a separate setup step. The tool does not log in, create a client, refresh tokens, use API keys, load ADC automatically or hold a service-account key. Keep any client/refresh credentials in the operator's private credential store, outside apps and Git. [Google desktop OAuth flow](https://developers.google.com/identity/protocols/oauth2/native-app), [accepted report scopes](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport)
4. Save that existing token as one line in an owner-only regular file (mode 0600 or owner-read-only) **outside both Git and the aggregate archive**. Do not paste tokens into command arguments, shell history, chat, fixtures or logs. The script rejects symlinks, group/world permissions and invalid token shape, but cannot inspect the token's granted scope or expiry offline. Remove the token file after the run, including backup/trash copies as applicable; its creation/deletion is the operator's responsibility.
5. Choose one private local archive, for example `$HOME/Library/Application Support/DoseWeek/analytics-monthly`. It is created with mode 0700; existing shared directories are rejected. Restrict backup scope to approved aggregate files and the non-identifying review record. Do not back up tokens or raw responses. Neither an archive nor a reminder is installed by this task.

Run from the repository root, replacing month/timezone/path with verified operator values. This example uses a deliberately non-IANA timezone placeholder and cannot be executed unchanged:

```sh
python3 scripts/privacy_ops.py export-month \
  --month YYYY-MM \
  --timezone ACTUAL_PROPERTY_TIMEZONE \
  --archive-dir "$HOME/Library/Application Support/DoseWeek/analytics-monthly"
```

That command is a dry run: no token access, directories, Google calls or output data files. It shows the fixed request and destination filename. After inspecting it, the same command with a private token path and **explicit** `--execute` performs one readonly request:

```sh
python3 scripts/privacy_ops.py export-month \
  --month YYYY-MM \
  --timezone ACTUAL_PROPERTY_TIMEZONE \
  --archive-dir "$HOME/Library/Application Support/DoseWeek/analytics-monthly" \
  --access-token-file /private/operator/access-token \
  --execute
```

On success stdout contains only status, call count and the monthly filename, not the result or token. For 401/403, fix authorised access outside the tool; for 429/5xx or transport errors, stop and check quota/service status before a later manual attempt. There are no retries. No aggregate is written for a rejected/failed request. A filesystem error after atomic publication can leave the final file; inspect it before retrying. Never bypass duplicate protection.

The original `monthly-request` and `sanitise-month` commands remain for offline/synthetic diagnostics. Do not use the file-based sanitiser as a normal production path: a manually saved raw response could enter backups. Synthetic test commands do not require credentials:

```sh
python3 -m unittest discover -s scripts -p test_privacy_ops.py -v
```

## User deletion stays separate

This tool still only plans deletion; it never submits it. Before local withdrawal/reset, an already-initialised and currently consented app may show a code shaped `DWGA1:ios:<appInstanceID>` or `DWGA1:android:<appInstanceID>`. This is the current Analytics app-instance identifier with a transport prefix, not a new identity or proof of ownership. A user can independently contact the published privacy address. No ID retrieval should initialise/re-enable analytics or delay refusal/withdrawal. Once reset/withdrawal makes the identifier unavailable, do not promise that support can recover or reconstruct it.

Where users find the code, as described in the website policies: iOS **Settings > Usage analytics (optional) > View deletion request code** (a Copy code button writes a local-only pasteboard item that expires after 60 seconds); Android **Settings > Usage analytics (optional) > Analytics deletion request code > View deletion request code** (selectable text, no copy button). On phones the Usage analytics (optional) card sits directly in the single-pane settings list, above the Data management card, which holds only Delete all local records; only in the two-pane list-detail layout used on some wide screens is it reached through the **Data management** entry first, and the Android policy says so. Both apps show it only while both optional consents are granted and collection is active, keep it in memory only, and never send it automatically. The policies tell users to email it to the published privacy address and not to send health records. They do not promise completed erasure. Withdrawing either consent or deleting local app data resets the identifier: immediately when the SDK is running in that process, otherwise before any later collection starts again.

The operator validates authority/context and strips the prefix before a separately authorised request to `POST https://analyticsadmin.googleapis.com/v1alpha/properties/555488369:submitUserDeletion`, using `analytics.edit`, with `{"appInstanceId":"<private raw identifier>"}`. Keep this privileged token separate from monthly readonly access. Google's returned `deletionRequestTime` records the accepted request/cutoff, **not completed erasure**. Do not equate local reset or disabling collection with deletion of uploaded data; existing aggregate reports are a separate retention class. Retain only a minimal private case receipt under a defined finite case schedule, not an enduring ID-to-person mapping. [Current Admin user-deletion method](https://developers.google.com/analytics/devguides/config/admin/v1/rest/v1alpha/properties/submitUserDeletion)

## Activation and evidence

Implementation status on 2026-09-23: runnable code prepared, no live report, authenticated API call, OAuth setup, account/API activation, scheduler registration, production archive, server deletion or publication by this task. Known local ADC and Google credential environment variables were absent; no credential contents were read. This limited local check does not establish whether a cloud OAuth client already exists.

Operational completion still needs actual timezone/identity/access readback, existing unbilled API/OAuth setup confirmation, a first authorised real response compatibility check, selection of the single private archive and monthly reminder, and a contextual long-term anonymity decision. Those are concrete activation items, not an assertion that a Google response or new paid service is necessary. Website policy/native consent and production collection proofs stay in the release owner's separate scope.

Current input hashes, console-setting provenance, synthetic test results and NOT RUN items are recorded outside the repository in `evidence/lean-20260923/privacy-operations-candidate/monthly-export-integration/` of the release workspace. The earlier external candidate and its 20 tests are preserved; this integrated exporter has a new matching test receipt. The website README and AGENTS now link to this guide.

The published policies currently say that no monthly export has been made with real data yet and that long-term storage waits for a privacy review. After the first reviewed export is retained, or if the deletion procedure changes, update `docs/ios-content.json` and `docs/android-content.candidate.json` in the same change and regenerate the pages.
