## ACTIVE — Publish 1 of the 1.0.6 legal pages (2026-10-03; owner-ordered, no AI/Pro)

Branch `publish/legal-106-p1` from `integ/legal-106-predeploy` 9ff91c4, merged to `main` for
GitHub Pages. Build: `python3 scripts/publish_release.py` (writes `docs/published/*` and 144
pages), check: `python3 scripts/publish_release.py --check` and `python3 scripts/check_site.py`.
Do not run the single renderers (`render_ios.py`, `render_android.py`, `render_terms.py`,
`render_us_health.py`, `render_home.py`) without `--check` on a published tree: they render
the base sources and would overwrite the public pages; their `--check` now fails by design.
Decisions and their text: `docs/publication-decisions-20261003.json`. Not verified at
publication: `docs/published/manifest.json`. Statutory mapping and gaps: release ledger
`web-predeploy-20261003/statutory-checklist.json` (gaps: 파기방법, 전화번호, 통신판매업 신고번호,
processor-table cells that still say 미확인, AI transfer not yet published).
Open: publish 2 (AI/Pro text) from `integ/legal-106-predeploy` once ai-consent-v3 is approved
and carries the 19:10 wording rule; it must be live before the Android 1.0.6 store release.
After 1.0.6 is in the store, change the scope sentence "current version 1.0.5" (17 locales).
Next action: publish 2.

## HISTORICAL — predeploy integration check (2026-10-03; unpublished, main untouched)

Branch `integ/legal-106-predeploy` = `next-ai/legal-store-legal-cx` 868932c + origin/main e652734
(PR #12 app-ads.txt; CHANGELOG/README conflicts, both sides kept). 222/222 unittest methods PASS,
`check_site.py` PASS (162 pages), `render_account_sync.py --check` PASS (126 staged pages, in memory).
`check_site.py --release` exit 1: NEXT_RELEASE_EFFECTIVE_DATE unset. Also still closed: 2 release
placeholders per locale on both privacy pages (server location/operator, retention), 19
serverReadiness flags false, the app-managed Drive backup (OQ-L2-1; CloudBackupService is still in
the Android integration tree 57f096247), and the AI text (ai-consent-v3 on `next-ai/pro-legal-ai`
a88ab73: both switches null in the files, every readiness flag false, not merged here).
The pages on this branch still show effective date 2026-09-23 and do not render the account,
sync, encrypted server backup or AI disclosures, so publishing it would not meet the Play privacy
requirement for Android 1.0.6. Not published. Public site verified unchanged: 126/126 sitemap URLs
200, app-ads.txt exact. Evidence: `Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/web-predeploy-20261003/report.json`.
Next action: owner sets the effective date and answers OQ-L2-1; fill the two placeholders; then
merge ai-consent-v3 with location=global, guardrail=off and pass `check_site.py --release` before main.

## ACTIVE — legal-update-legal LATE2 review-1 fix (2026-10-02; unpublished)

Objective: fix the two majors from the review that rejected `04f43c5`. Branch
`next-ai/legal-store-legal-cx`. Pass status: COMPLETE (static).
1. ko/ja/tr kept the 1.0.5 sentence "nothing is deleted or moved into Plus" in the staged earlier
   answer (Android FAQ plus-earlier, iOS support plus/earlier), because the renderer replaced
   only sentence 0. It now replaces every sentence before the closing notice on both platforms.
   RED `d8ed26d` (fixture claim per locale/platform; standalone sentence no longer "preserved"),
   GREEN `286237f`. Only those 6 staged fields changed; the other 14 locales are byte-identical.
2. The app-managed Drive appDataFolder backup (CloudBackupService) still ships in apps/google
   release/1.0.6 but is no longer described. It is now a publication blocker: new
   `serverReadiness.appManagedDriveBackupDecided=false`, an unresolved item and an operations
   blocker ("removed from the 1.0.6 build or disclosed before publication"); OQ-L2-1 stays open.
   RED `baffda8`, GREEN `74534b5`.
Checks: 222/222 unittest methods PASS; 13 light commands PASS; `check_site.py --release`
BLOCKED_EFFECTIVE_DATE as expected; frozen inputs match (263 files). Evidence:
`evidence/legal-update-20261002/late2-fix1/summary.json`. Temporary RED worktrees removed.
No native/provider/live check applies. Never publish.
Next action: orchestrator re-review; the owner answers OQ-L2-1 (remove or disclose the
app-managed Drive backup) before the flag can open.

## HISTORICAL — legal-update-legal LATE2 automatic backup (2026-10-02; unpublished)

Objective: apply the late owner backup decisions in all 17 staged 1.0.6 privacy/help/Terms
locales. Plus automatic backup = optional, separately consented end-to-end encrypted server
backup/sync (server cannot read contents). Android OS Google Drive Auto Backup carries the
complete app-data set only during verified active Plus; otherwise the run is skipped, never an
empty or partial backup, so the previous backup stays restorable (owner
backup_safety_completeness, 15:30). No iCloud/CloudKit app-data backup. Free keeps manual file
export/import and backup reminders. Server: daily encrypted S3 Seoul archives plus one manual
pre-deploy OS snapshot deleted within 7 days (owner 14:48; weekly snapshots dropped).
Branch `next-ai/legal-store-legal-cx`; base reviewed `4890013`. Pass status: COMPLETE (static).
Commits: RED `cfc27f7` (Codex), RED `051b975` (manual snapshot assertions), test correction
`e691a48` (Free plan named with each locale's live term), GREEN `880184c`, RED `fa684a6`
(skip-not-empty), GREEN `2cfbac8`, then this docs/evidence commit. HEAD is in the lane report.
Codex was cut off at 15:33 with GREEN uncommitted and failing on one Android catalog guard
("visit prep"); fixed by a separate Android free-feature list (`androidFreeFeatures`).
Shared deletion text now gives a neutral cloud-storage example instead of Google Drive, so
iOS copy names no Android-side service.
Checks: 220/220 unittest methods PASS (0 failures/errors/skips/omissions); 13 light commands
PASS; `check_site.py --release` exit 1 BLOCKED_EFFECTIVE_DATE as expected; frozen inputs match
(263 files). RED proofs: `late2/red-final-proof.json`, `red2-proof.json`, `red3-proof.json`.
Raw 7 MB RED logs replaced by excerpts with recorded sha256. No native/provider/live/visual
check applies or is claimed. No owned PID/device/worktree remains. Never publish.
Next action: orchestrator review of HEAD; Android Drive skip mechanism and bmgr proof belong
to the Android BackupAgent lane; publication gates stay closed.

## HISTORICAL — legal-update-legal late review 2 (2026-10-02; unpublished)

Objective: resolve the single major in late.review-2 with its permitted price-agnostic
store-price contract across active coordination, operations, provenance, tests and report.
Reviewed HEAD `3cbc050be05cb9a8ae84a8916ed34f15419dcf40`; branch `next-ai/legal-store-legal-cx`.
Initial worktree clean. Baseline/input hashes and untouched prior report in
`evidence/legal-update-20261002/late-review2/`. Historical evidence remains immutable.
Owned scope: regression/assertions, four active contracts, local evidence/runners, handoff
and CHANGELOG. Git status owns the exact dirty inventory. All scripts AST compile PASS.
No owned PID/device/live job or external action; canonical release ledger read only.
Partner snapshots remain historical; effective date/readiness/publication gates stay closed.
RED committed at `778ee01` (full identity in Git/report) before product edits.
RED parent replay PASS as failure proof: six exact methods, six assertion failures,
AST compile PASS; zero errors/skips/omissions. Raw identities/logs in `late-review2/red-parent.*`.
Owned detached /tmp worktree removed; no running job.
GREEN edit: parity schema now requires store-price wording; remove numeric setup authority
from operations/provenance and numeric alternative from account blocker. Partner objects are
byte-equivalent historical receipts; trials/rights/public pages/readiness untouched. Candidate
source fingerprint refreshed. Owned dirty also includes four active contracts and RED evidence.
Focused seven-module family: 68 exact methods PASS; AST compile PASS; zero failure/error/skip/omission.
Preservation audit PASS: all162 generated pages/assets/17-locale product and account data,
partner objects, historical evidence and readiness unchanged; only one account blocker changed.
Release-map source fingerprints match. Evidence `late-review2/preservation-audit.json`.
Independent read-only source audit PASS; no blocking/major issues.
Full208 exact methods and13 ordinary commands PASS; zero failure/error/skip/omission.
Release child exit1 BLOCKED_EFFECTIVE_DATE retained as failed; all gates remain closed.
260 frozen inputs/runtime match. No product/test input edits during checks.
New provenance assertion reads release-map reporting: supplement its final exact fields and
full-file fingerprint with a targeted replay; other unchanged inputs retain matching full coverage.
Supplemental final provenance selector PASS with matching full-map/runner/field hashes;
260 full-gate frozen inputs still match. Exact receipt `late-review2/provenance-input-comparison.json`.
New report writer validates identities/logs/inputs/stamps/false gates and uses store-price only.
Owned proof worktree and preparation scratch removed; no running owned process/device.
Source GREEN committed locally at `889feca451642f0f61199fb2d289b990ac37efb3`; verified product inputs unchanged.
Final report overwritten at requested external path. Schema/readback/exact-ID/loghash/
frozen260inputs/provenance/stamps/false-gates/price-agnostic-fields validation PASS; checkpoint
in `late-review2/report-validation-precompletion.json`. Independent report audit PASS: exact identities/logs/all260inputs/provenance/stamps/
175preservedfiles/historicalreceipts/falsegates/price-agnostic report agree; no actionable issue.
Receipt `late-review2/independent-report-audit.json`.
Reporting-only completion owns handoff/CHANGELOG/checkpoint/audit; product inputs unchanged.
After completion commit, mechanically refresh final report HEAD/commits/files/clean status.
No running owned process/device, temporary worktree or scratch remains. No publication/push/
merge/deploy/native/provider/Store/network action performed. Existing blockers remain explicit.
Next action for orchestrator: review/integrate these RED/GREEN/completion commits, obtain
matching final store-price partner copy/check receipts and operational/Store evidence. Never publish from this lane.

## HISTORICAL — legal-update-legal late review 1 (2026-10-02; unpublished)

Objective: fix the single major in late.review-1 with reviewer-permitted store-price wording
in all17 Terms locales. Final owner price decisions remain authoritative for Store setup;
no price decision is reopened. Preserve trial/renewal/cancel/refund, other legal MUSTs and histories.
Branch `next-ai/legal-store-legal-cx`; reviewed HEAD `fe488a5320e50f5afc5e4a26150d935eaa154974`.
Initial clean state, input fingerprints and historical late report in
`evidence/legal-update-20261002/late-review1/baseline.json` and `late-report.historical.json`.
Owned scope: regression/fixture, Terms offer/validator, generated Terms, parity/operations blocker,
release-map source fingerprints, this handoff and dated CHANGELOG. Git status owns dirty inventory.
No owned PID/device, native or external action. Existing partner receipts stay historical and
commercialCopyParityVerified=false until final committed partner copy/check receipts are acquired.
New5-method regression and17locale fixture added; every Python script AST parse PASS.
Owned dirty: tests/fixture, baseline/historical receipt, copied offline runners, handoff/CHANGELOG.
RED `5447afae57d1dfbede924ed971c8f29255028f14` committed first; detached parent `fe488a5320e50f5afc5e4a26150d935eaa154974` compiled and ran5exact methods;
4methods failed with154assertion failures,0errors/skips/omissions.
Raw logs/identities in `late-review1/red-parent.*`; proof worktree removed. No live owned job.
GREEN source edit: only17leading price disclosures replaced; restoring17fields reproduces
reviewed Terms bytes. All trial suffix hashes match; other billing/rights/features untouched.
Renderer enforces monthly/annual store-price and full-price/tax/period-before-purchase wording;
related historic price guards now cover the permitted alternative, retired-price insertions.
Parity/operations blocker explains store-price choice; historical receipts/gates remain closed.
Focused related6modules: 33exactmethods PASS,0failure/error/skip/omission; ASTcompilePASS.
Exact identities/logs in `late-review1/focused-green.*`. No inputs edited during run.
Terms rendererPASS;18affected hash/locale pages regenerated from canonical source.
Release-map fingerprints refreshed; effective date/readiness flags remain closed.
Interim fullsuite204exactmethods and13ordinarychecks PASS; releaseexit1 BLOCKED_EFFECTIVE_DATE.
259relevant input hashes/runtime match. Retained `interim-*` receipts cover the earlier validator.
Independent audit confirmed17prefix/trial transformations and10unchangedlegal sources/assets;
found the original bare2,900/22,000 validator guard should also survive.
Original bare retired-price guard restored; existing late mutation test now inserts both
currency-prefixed and bare variants. No product copy changed after generation.
Final focused6modules:33exactmethods PASS,0fail/error/skip/omission;ASTcompilePASS.
No source changes during check; final exact identities/logs in `late-review1/focused-final.*`.
Final fullsuite204exactmethods PASS,0failure/error/skip/omission;all13ordinarycommands PASS.
Release child exit1 BLOCKED_EFFECTIVE_DATE retained as failed.259frozeninput hashes/Python/runner
match before/after. Raw command logs,exact identities and frozen inputs in `late-review1/`.
Independent final source/render/report-writer auditPASS;18actualTerms match output/hashes.
All readiness flags/effective date remain closed. Partner snapshots unchanged/historical;
no native/provider/Store/live/visual/counsel/native-speaker verification claimed.
No owned running process/device or temporary worktree/scratch remains.
Source GREEN committed locally at `d7b04b78dfbf2f787eea2fd86d40403330fbbe3a`; product/test/artifact inputs unchanged.
Initial report-validator exit1 retained: it incorrectly required text from successful `git diff
--check`; its valid empty gzip is expected. Narrow parser fix only; product inputs unchanged.
Late report overwritten at requested external path; schema/readback/exactidentities/loghashes/
259frozeninputs/commitstamps/falsegates validationPASS at sourceGREEN. Precompletioncheckpoint
in `late-review1/report-validation-precompletion.json`; initial parser failure preserved separately.
Independent final report auditPASS: identities/loghashes/259inputs/REDproof/trailers/files/checkpoint
agree; releaseexit1/initialwriterFAIL and partner/operational blockers explicit. Receipt:
`late-review1/independent-report-audit.json`. Reporting-only completion records this handoff,
CHANGELOG, report-writer parser fix/checkpoint/audit. No verified product input changes.
After completion commit mechanically refresh report finalHEAD/commits/files/cleanstatus.
Next action for orchestrator: review/integrate new commits and obtain matching final partner
copy/check receipts plus operational/Store proofs; publication remains outside this lane. Never publish/push/merge.

## HISTORICAL — legal-update-legal late owner decisions (2026-10-02; unpublished)

Objective: apply final owner decisions in new assertion RED/GREEN commits; never publish.
Branch `next-ai/legal-store-legal-cx`; starting HEAD `a6a4e18f70bcf866a6bb50aacb8a64164cba8bde`.
Final references: USD 1.99/month,13.99/year; KRW3,300/month,19,900/year;
JPY300/month,1,980/year; store-converted other prices and store-returned native UI.
EU/EEA, UK and Switzerland exclusions/no representative already implemented in all17locales;
preserve those rights/safeguards and inherited proof. Fixed1-calendar-month Store-confirmed
first-time trial, auto-renewal and cancel-anytime wording; remove contradictory duration overrides.
Owned dirty: Terms source/renderer, account publication blocker, commercial parity/operations,
late tests/evidence and continuity files. Git status owns exact inventory. No owned PID/device or external action.
Inputs: `evidence/legal-update-20261002/late/baseline.json`; prior revision2 evidence remains historical.
Read-only partner snapshots: iOS committed policy reflects finalprice; Android snapshot still old.
Snapshots do not prove partner checks or Store configuration; commercial parity gate remains false.
Canonical workspace status read from original workspace; no concurrent canonical ledger written.
RED committed locally at `6bf1fd5`; AST compile PASS. No product edits yet.
RED immediate parent:7 exact methods,6 failed methods,104 assertion failures; compile PASS,
0 errors/skips/omissions. Supplemental pre-exclusion source:1 method,36 assertion failures;
regional placeholders/exclusions fail as expected. Both owned detached worktrees removed.
Raw logs and identities: `late/red-parent.*`, `late/pre-exclusion-source.*`, `late/red-proof.json`.
GREEN edit:17 final annualprice fields and33 fixedmonth duration clauses changed. Restoring
those fields reproduces whole originalTerms bytes; no other billing/rights/features modified.
All17regional policies/UShealth/breach/deletion/processor wording retained. Latest partner snapshots
remain historical, not final parity verification.
Focused related family:63 exactmethods PASS,0failure/error/skip/omission; ASTcompilePASS.
Terms rendererPASS;18hash/localePages regenerated; releaseMap source fingerprints refreshed.
Final fullsuite:199exactmethods PASS,0fail/error/skip/omission; every13ordinary command PASS
(including fullsuite/diff). Release child exit1 BLOCKED_EFFECTIVE_DATE remains failed, not waived.
Site162pages/17locales; staged126pages/7routes; tone2078sentences,0violations,9existingexceptions.
All257relevant input hashes and Python/runner/runtime match before/after; logs/identities retained.
Independent readonly audit:17price+33trial transforms exact; all18Terms pages finalprice; account
only blocker[27] changed; privacy/UShealth/breach/processor/deletion sources and renderers unchanged.
Preservation hashes in `late/preservation-audit.json`; originalREDs/failures preserved.
No owned running process or temporary worktree. Native/provider/Store/live/visual NOT_RUN;
release date null and every readiness flag remains false. Never published/pushed/merged.
Source GREEN committed locally at `b2afed9a270469d374cd6cc55518a1c33129470f`; source/test/artifact inputs remain unchanged.
Late report written and schema/readback/commitstamps/exactidentities/loghashes/frozeninputs
validationPASS at sourceGREEN; checkpoint in `late/report-validation-precompletion.json`.
Original regular report preserved unchanged and copied as historical baseline evidence.
Independent final report auditPASS: exactidentities/loghashes/commits/files/257inputs agree;
no obsolete price or representative-appointment question. Receipt: `late/independent-review.json`.
Reporting-only completion updates handoff/journal/writer/checkpoint; final mechanical report refresh
records finalHEAD/commits/cleanstatus without changing257verified productinputs or rerunninggates.
Next action: orchestrator reviews/integrates late commits, acquires matching final partner policy/
review/check receipts plus operational/Store proof; publication remains outside this lane.
Report target: `/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-late-report.json`.

## HISTORICAL — legal-update-legal revision 2 (2026-10-02; unpublished)

Objective: fix review-2 issues in new RED/GREEN commits; never publish or rewrite history.
Branch `next-ai/legal-store-legal-cx`; reviewed parent `d3b6e32b21789c67763ad9f73bfff77dc370cc2b`.
Owned scope: retired prior-buyer grant/claim-code copy; shortened competing-store references
in staged iOS; six-locale PIPA threshold grouping; committed commercial-copy parity receipts.
Keep KRW 22,000/year per review-2; iOS current committed copy matches; Android remains blocked
on KRW 19,900. Store-returned native UI prices remain the required contract.
No owned PID/device, native or external action. Previous proofs/history preserved below and
in `evidence/legal-update-20261002/revision2/revision1-report.historical.json`.
Inputs and clean reviewed state: `revision2/baseline.json`; current dirty files: new regression
and evidence/continuity files only until the RED stage is proved. Exact Git status is authoritative.
RED `30647c4` proved on detached `d3b6e32` under /tmp: 43 exact methods, 10 failed methods,
1098 assertion failures; compile PASS, 0 errors/skips/omissions. Retained raw gzip and JSON in
`revision2/red-parent.*`; an incorrect wrapper prediction of 11 failed methods is corrected
against the unchanged retained result without rerunning. Proof identity/hashes in `red-proof.json`.
Owned proof worktree removed. GREEN source edit: retired grant/claim/code workflow removed from
17 Terms and staged policy/help; core feature answers and statutory/historical rights retained.
Shared token wording neutralized in 17 sync fields; remaining lookup/encryption/deletion prose
matches exactly. PIPA grouping changed in 12 paragraphs only; remaining privacy source bytes
match the parent after threshold restoration. iOS renderer rejects short Play aliases.
Commercial parity false gate and committed partner coordination record added; Android stays BLOCKED.
Current dirty: source/renderer/docs plus retained RED/change receipts; no owned running job.
Focused related family PASS:81 exact methods,0 failure/error/skip/omission; AST compile PASS.
Lossless result/identities/log in `revision2/focused-green.*`; no source changes during this check.
Seven render commands PASS; affected iOS/Android privacy and17 Terms locale/hash pages regenerated
from sources. Release map fingerprints refreshed; no effective date or readiness proof invented.
Final full suite PASS:193 exact methods,0 failure/error/skip/omission. Every ordinary README
check PASS (12 commands), release command exit1 BLOCKED_EFFECTIVE_DATE remains an actual failed
gate. Site162 pages/17locales; staged126 pages/7routes; tone2078sentences,0violations,9existing
exceptions,0stale. Exact255 relevant input hashes and Python executable/runtime match before/after.
Independent read-only review: no material current source issue; current51retired-body and34core-help
preservation receipts PASS. Regression presence guards do not certify future paraphrased contradictions.
Evidence in `revision2/`: full/focused/RED identities and logs,13check receipts, frozen inputs,
126staged artifact hashes, minor/token and semantic preservation audits, committed partner receipts.
All17server flags and5legal flags per privacy source remain false. Android committed commercial
parity BLOCKED; iOS matches requiredKRW22000. No price decision reopened. Source GREEN committed locally at `5f96792321df89783e22b73aa7c43e1979e3a46c`. Owned proof worktree and translation scratch removed; no running owned job.
Native/provider/live/visual NOT_RUN; no counsel/native-speaker certification or publication.
Final report overwritten and schema/identity/evidence/log/hash/stamp validation PASS at sourceGREEN;
`revision2/report-validation-precompletion.json` retains this checkpoint. Independent read-only
report audit also found no material inconsistency; receipt in `revision2/independent-review.json`. Final reporting-only
commit will change this handoff, dated journal and report writer/receipt; the mechanical final
report refresh records final HEAD/commit/file inventory and clean status without changing any
of255verified product inputs. No competing workspace handoff or release journal is written.
Next action: orchestrator reviews/integrates the candidate and coordinates Android committed
policy/review/check parity to KRW22,000 before opening its gate; remaining operational ownerQuestions
and actual Store/native/provider proofs still block release. Publication is outside this lane.
Report: `/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-report.json`.

## HISTORICAL — legal-update-legal revision 1 (2026-10-02; unpublished)

Objective: resolve every major and the minor in review-1, using the latest owner/spec decisions.
Branch `next-ai/legal-store-legal-cx`; reviewed parent `a2648991d78ad1dd92e604e015af4a535d5319eb`.
RED `a33a8b8` committed before GREEN: detached reviewed parent compiled all scripts,
32 exact methods executed, 12 failed methods / 235 assertion failures, 0 errors/skips/omitted.
Temporary proof worktree was restored to its parent and removed; no history rewritten.

All 17 locales now use KRW 22,000/year, Wonyoung Labs as operator, and 1.0.6 EU/EEA,
UK and Switzerland sales exclusions with no appointed EU/UK representative. Applicable
existing-user rights/transfer safeguards/breach clocks and iOS PDF portability are preserved.
Actual Store-exclusion false gates replace appointment-only false gates. Canonical/staged iOS
policy/help use neutral other-platform/store references; verifier/retention clauses survive.
Product/source GREEN committed locally at `3ded23a5f655c79fc99b7c2b777019884d805b54`.
Owned GREEN changes: three policy/Terms sources plus account candidate, bounded validators/
renderers, regenerated iOS/Android/Terms pages, README/operations/release map and evidence.

Focused GREEN: 77 exact methods PASS. Final full repository GREEN: 182 exact methods PASS,
0 failures/errors/skips/omitted. Seven renderer checks, candidate, in-memory account render,
site, tone and diff checks PASS. Site 162 pages; staged 126 noindex/null-date pages.
Tone 2104 sentences, 0 violations, 9 existing exceptions and 0 stale entries. All 249 frozen
source/test/runner/assets/artifact hashes match. Two independent read-only reviews found no
material issue; audit retained 34 regional-policy safeguards and checked 102 operator fields.

Evidence: `evidence/legal-update-20261002/revision1/` holds exact requested/executed IDs,
lossless RED/focused/full/check logs, input fingerprints, staged hashes and preservation audit.
The first check wrapper misclassified the release assertion due to an expected-text mismatch;
its exit1/raw receipt is retained. Corrected classification uses the unchanged retained terminal
log, without rerunning product checks: release child exit1 remains BLOCKED on null effective date.
16 account/server flags and 5 legal flags per privacy source remain false; actual supplier,
Store exclusion, native/deletion/backup/rights/incident proof is still required. No EU/UK
appointment question remains for this excluded-market version. No counsel/native-speaker or
visual certification; visual/native/provider/live checks NOT_RUN. No network, push, merge,
store action, deployment or publication. No owned job/device or temporary/scratch files remain.

Final report overwritten and readback/identity/hash/schema/stamp validation PASS at source
GREEN; `revision1/report-validation-precompletion.json` retains that result. The reporting-only
completion commit changes this handoff, dated journal and report writer/receipt. A final
mechanical report refresh records its final HEAD/commits/files and clean status; no checked
product input changes and no tests are rerun. Current Git HEAD and the final lane report own
exact inventory; no concurrent competing handoff or release journal was written.
Next action: orchestrator reviews/integrates the revision candidate and resolves the remaining
operational ownerQuestions. Publication remains outside this lane.
Report: `/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-report.json`.
Older snapshots below are historical and cannot authorize release work.

## HISTORICAL — legal-update-legal initial result (2026-10-02; rejected review-1)

Owner scope: 1.0.6 legal/store/web copy from approved `1714082f`, branch
`next-ai/legal-store-legal-cx`. All 17 locales updated: privacy/rights/breach/processor table,
separate health consent, immediate deletion and hybrid 7-day backups, subscription/trial/refund
Terms, separate linked US health-data policy. Current Git HEAD is authoritative; the final
report records commits and owned files. No native/device job, network, push, merge or publication.

Product/source GREEN committed locally at `2efa2b0f8e368c074fc24f947a4d014776636e0d`.
The following completion commit changes only this handoff and the dated journal; it does not
change the verified source, tests, renderers or artifacts. Final HEAD and complete owned-file
inventory are recorded in the external report. No lane check process or temporary worktree remains.

Final static gates PASS: seven renderer checks, account validator, site/tone/link/RTL/source
parity; exact 173 methods executed: 173 PASS,0 failure/error/skip/omitted. Site: 162 pages (9x18),
staged: 126 pages (7x18, noindex/null date, in memory); tone: 2101 sentences,0 violations,
9 narrow clinical/category exceptions,0 stale. Final input 46-file freeze comparison matched.
REDs `a7febe9`/`2e51e28`: each 36 methods / 619 assertion subtest failures; `147c533` privacy 12 methods /
376 failures. Each compiles on its detached parent,0 errors/skips; temporary worktrees removed.

Durable evidence: `evidence/legal-update-20261002/legal-update/` contains final inputs,
exact requested/discovered/executed identities, staged content hashes, closed gates and lossless
RED/intermediate/final logs. Prior failed first full gate (173 methods: 171 PASS / 2 FAIL), assembly
errors and tone failures are preserved; none is relabelled PASS. Clinical record wording and
SDK metadata are distinct after independent 17-locale semantic review.

Publication gate remains BLOCKED: effective date unset, 16 server readiness flags and 5 legal
readiness flags per privacy source are false; actual provider/country/contact/retention,
contracts, representatives, deletion/backup/incident/rights and Store/native proofs pending.
EU/UK contact placeholders are explicit. No counsel/native-speaker certification. Browser
policy blocked the local file URL, so visual review is NOT_RUN; no workaround was attempted.

Report: `/Users/wonyoungchoi/Documents/Coding Work/Doseweek/release/evidence/1.0.6/CODEX-LANES-20261002/legal-update-legal-report.json`.
Report written and checked: required fields, 29 actual evidence paths, exact identity/count and
commit inventories verified; independent reporting review completed. Completion hashes match
45/46 frozen inputs; the sole difference is derived release-map status/source-hash metadata,
with effective date still null. Existing adult-only scope is preserved; regional child controls
and marketing-claim substantiation are follow-up, not implemented or certified by this lane.
Next action: orchestrator reviews/integrates this candidate and resolves the report's
ownerQuestions/operational gates; publication remains outside this lane. Older snapshots below
are historical for this resumed lane. Only derived receipts/docs change after this frozen gate.

## OWNER_PAUSE_RELAUNCH — 다른 AI 인수인계 (2026-10-01)

사용자가 다른 AI에게 이어서 맡기도록 요청하여 이 세션의 구현·새 검증을 중지했습니다. 자동 재개 doseweek-1-0-6은 PAUSED입니다. 새 담당자가 이어받기 프롬프트로 재개하면 이 표시를 해제하고 현재 live 상태부터 진행합니다. 전체 작업·출시 준비는 미완료이며 운영 배포·콘솔·상품/광고 활성화·제출·웹 공개·merge는 수행하지 않았습니다.

Workspace `/Users/wonyoungchoi/Documents/Coding Work/Doseweek`의 `release/HANDOFF_OTHER_AI-2026-10-01.md`, `release/NEXT_AI_PROMPT-2026-10-01.md`, `release/evidence/1.0.6/other-ai-transfer-20261001/STATE.json`과 `ready-inputs.json`이 최신 전달 자료입니다. 기존 root journal과 각 failed receipt는 보존합니다. 현재 문서 커밋은 제품 입력을 변경하지 않습니다.

- iOS 제품3056 SDK/current3042/588 seal PASS. Mapping2+6 distinct scoped8 PASS; original19 FAIL 유지. Native24=6PASS18CloudKit134060 INITFAIL/runner65/parser1, owner/persistence assertions 도달0. Product local factories.none; test common makeStore.none 한 인자 수정12f5/review6936704/config4557728 ready지만 primary 통합/새SDK/native NOT_RUN.
- Android 제품624624 priorbuyer28/17locale544 및 server6 통합·push. Matching JVM32 fakeports, XML17parse, Node unit34+privateHTTP22=56 PASS는 해당 입력만. 새 Gradle/Compose/native NOT_RUN. Native4 start0/executed0/omitted4 FAIL/causeUNKNOWN; forensichelpFAIL1/actualrc-unretained도 유지. Exact drain82119, oldAPKs e8/8eb sealed d342. Baseline2/configd776와 forensicdelta/review3e2 SOURCE_ONLY 준비; 새 device grant 없음.
- UI finitePID evidence-only review3643868 approved; fresh current representative1→remaining5 NOT_RUN. Authority/bootstrap/full retirement10과 Android causal product14는 미구현. Full19 실제 동기화·자동백업·복원 연결/삭제완결성/provider/payment/consent/release6 gates가 큰 남은 범위입니다.
- Legal4d9/web72b matching static/visual proof와 store drafts는 기존 범위만 보존; 법률·원어민·provider·public availability를 주장하지 않습니다.

정확한 다음 작업: 최종 STATE의 doc-only HEAD와 기존3056 config의 selected preimage/dependency/review를 대조한 derivative를 만든 뒤, reviewed testfixture1 .none을 exact integrate/commit/push/PR13 갱신합니다. ONE incremental UnitSDK/exact selectors → originalOwnerRead1 먼저 → PASS면 remaining7owner+persistent10. Matching mapping8은 반복하지 않습니다. Android baseline/source 및 forensic binding은 병렬 준비하되 builder/device는 exclusive입니다. 더 큰 계획 문서 대신 기존 실제 코드의 연결과 검증에 집중합니다.

## CANDIDATE — round 3 of the account/sync facts (2026-10-02, reviews of e3da3bd)

Same branch. RED `df06a41` (detectors and tests only): `RETIRED_HEALTH_SYNC`,
`RETIRED_OFFLINE_CLAUSES`, `RETIRED_BACKUP_MECHANISM`/`BACKUP_WINDOW_SENTENCES`, CJK "。 " joins,
`recordsSync`/`mealsSync` presence and `RECORD_DENIALS`/`MEAL_DENIALS` in the staged sources,
`serverReadiness.backupWindowVerified`/`accessLogDisclosed`, and
`legal_release.PENDING_DIGEST_BASIS`. At the RED: candidate tests 32 run / 8 FAIL / 0 ERROR,
`check_site.py` exit 1 (89 findings), CLI exit 1. GREEN `b6412a8`: non-exclusive `healthSync`,
new `recordsSync`/`mealsSync` (17 locales) replacing the staged iOS support/meals and Android meals
denials, mechanism-neutral backup window, unresolved item for the hybrid backup decision, two new
false readiness flags, ja/zh joins. Agent-drafted translations.

- PASS at head: six renderer `--check`s, `check_site.py` (Korean tone 1595 sentences),
  `korean_tone.py` (0), the 6-module unittest set, candidate CLI, staged render (108 pages).
  BLOCKED: `check_site.py --release` (effective date unset, and 10 open readiness flags).
- Routed outside the lane: iOS `Localizable.xcstrings` `privacy.section1.body` (same records
  denial) to the iOS in-app copy owner; `check_site.py --release` and the Android
  `privacy_account_sync_guard.py --release` into `release/1.0.6/scripts/release_gate_checklist.py`
  (integrator).
- Evidence: workspace `release/evidence/1.0.6/LEGAL-STORE-20261002/round3/legal/`.

## CANDIDATE — account/sync server facts, Cloudflare transfer and D8 retention (2026-10-02)

Lane LEGAL-STORE, branch `next-ai/legal-store-legal` from `33e7f63`; not pushed, merged or
published. Failing-first `702c296`: `account_sync_candidate.hosting_retention_errors()` (operator,
AWS Lightsail `ap-northeast-2`, Cloudflare with its PIPA transfer links, 30/7-day figures, D1
record scope) and `staged_placeholder_errors()` (no release placeholder in the staged 1.0.6
sources), wired into `check_site.py` and the candidate CLI. On the base: candidate tests 17 run /
3 FAIL, `check_site.py` exit 1 (170 missing facts), CLI exit 1. Fix: new `processors` field and
rewritten `sync` lead and `retention` head in all 17 locales; the staged purchase sections use
`processors` instead of the placeholders; review doc section "2026-10-02 lane LEGAL-STORE".

- PASS: six renderer `--check`s, `check_site.py` (Korean tone 1575 sentences), `korean_tone.py`
  (0 violations), README unittest set + candidate tests (122), candidate CLI, staged render to a
  scratch directory (108 pages, no placeholder, Cloudflare/ap-northeast-2 on every privacy panel),
  `git diff --check`.
- BLOCKED (unchanged): `check_site.py --release` (effective date unset). NOT_RUN: browser visual
  review, native-speaker and counsel review, live host/backup readback.
- Owner/counsel: Cloudflare log retention period, AWS contracting entity, entitlement-verifier
  host, HOST-07 access logs, PIPA transfer basis; OPS-HOST must make the 7-day backup window true.
- Follow-up `88536b6` (RED: formal German/Dutch address in the candidate, 1 FAIL on nl
  `webDeletion` "je") and `b7266d9` (fix: "uw"), found because the Android in-app policy now
  carries this copy. Final: 123 unit tests, check_site/korean_tone/CLI/staged render PASS.
- Evidence: workspace `release/evidence/1.0.6/LEGAL-STORE-20261002/legal/`.

## CANDIDATE — round 2 of the account/sync facts (2026-10-02, reviews 1 and 2)

Same branch. RED `f098410` (test-only detectors): `transfer_disclosure_errors()` and
`staged_disclosure_errors()` wired into `check_site.py`; 5 of 25 candidate tests FAIL on
assertions, `check_site.py` exit 1 (159 findings). GREEN `e53d9ed`: true Cloudflare refusal and
announcement occasion, Google token claims, notice names Cloudflare, data-key wording, new
`healthSync` field, kept tombstone/verifier records, Turkish "eşitleme", ko/ja/zh word order,
`serverReadiness` (8 flags, all false) with one unresolved item each, `require_release_ready()`
refuses open flags, `--release` refuses the registered pending sentences. Hardening `04aa477`:
`SYNC_SCOPE` in all 17 locales (debbd1c had narrowed RED 702c296's D1 assertion to en/ko).
`212c91b` (self-found, no RED owed): the refusal no longer says the announcement check is skipped
"only" when offline (it is also gated by age/privacy/unlock and skipped on timeout); the candidate
CLI now runs the same detector as `check_site.py`.

- PASS at head: six renderer `--check`s, `check_site.py` (Korean tone 1590 sentences),
  `korean_tone.py` (0), README unittest set + candidate tests (131), candidate CLI, staged render
  (108 pages). BLOCKED: `check_site.py --release` (effective date unset).
- Open (owner/counsel): announcement-check transfer route or opt-out, Cloudflare privacy contact and
  log retention, verifier host, tombstone retention. Server/app: `recheckPlus` wiring in
  `src/index.js`, `DELETE /v1/sync/snapshot` (SRV-HTTP `ab92fcf6`), both reset-sync controls.
- Evidence: workspace `release/evidence/1.0.6/LEGAL-STORE-20261002/round2/legal/`.

## CANDIDATE — Kakao sign-in removed; Apple and Google only (2026-10-01)

Owner decision 2026-10-01 ("아니다 카카오 로그인은 빼자"): the account feature keeps only Sign in
with Apple and Google. Branch `next-ai/drop-kakao-legal` from `4cd08b3`; not pushed, merged or
published. Failing-first `003dfe9` added a retired-provider detector (Kakao, 카카오, カカオ) in
`scripts/account_sync_candidate.py` over the sign-in-bearing sources (account-sync candidate, iOS,
Android, Terms, home, help navigation; `import/content.json` is excluded because those names also
mean cacao), a `check_site.py` gate and three unit tests. On the base data it failed:
`test_account_sync_candidate` 13 run / 2 FAIL, `check_site.py` exit 1 (18 fields), validator CLI
exit 1. Fix `a3323c2`: 17-locale candidate `account` copy names Apple and Google only and drops the
Kakao unlink-token sentence; the unresolved provider item covers only Apple refresh capability;
`load()` refuses any retired-provider mention; the release review lists Apple/Google identifiers.
Generated public pages are unchanged (the candidate is staged only).

- PASS: six renderer `--check`s, `check_site.py` (144 pages, Korean tone 1550 sentences),
  `korean_tone.py` (0 violations), validator CLI, README unittest set (105),
  `test_account_sync_candidate` (13), staged `render_account_sync.py` to a scratch directory
  (108 pages, no Kakao), `git diff --check`.
- BLOCKED (unchanged): `check_site.py --release` (effective date unset). NOT_RUN: browser visual
  review, native-speaker/counsel review, native/provider checks.
- Kakao entries in the dated 2026-09-30 sections below are historical; they no longer describe
  the candidate.
- Next: integrate with the native/server Kakao removal lanes; merge and publication stay owner
  release gates.

## CANDIDATE — iOS automatic iCloud backup disclosure withdrawn (2026-10-01)

Commit `3aa200f` on the candidate branch, after `ab8f52e` and `679b03c` (both already pushed as the PR #11 head); a forward revert, so no rebase or force push. Not merged or published. The 1.0.6
iOS app ships with the automatic iCloud backup lane switched OFF (App Store 5.1.3(ii)), so the
`ab8f52e` disclosure is reverted: `docs/ios-content.json` (17 locales: privacy `backups` second
paragraph, manual-backup exception sentence, iCloud sentences in privacy `deletion` and the support
deletion answer, third support `backup` answer), `scripts/render_ios.py`
(`SECTION_PARAGRAPHS` without `backups`) and the 36 regenerated iOS privacy/support pages now match
`ca1d810` except the `679b03c` fixes, which stay (ko/ja support lead without "only"; account-sync
`legacyRights` tone fix). The withdrawn wording is retained in Git history at `ab8f52e`; restore it
from there, rechecked against iOS source, when a release turns the feature on.

- PASS: six renderer `--check`s, `check_site.py` (144 pages, Korean tone 1551 sentences),
  `korean_tone.py` (0 violations), README unittest set (105), `test_account_sync_candidate` (10).
- NOT_RUN: `check_site.py --release` (effective date unset), browser visual review, native review.
- Next: keep the forward revert on the candidate branch; merge and publication stay owner release gates.

## ACTIVE — prior-buyer application disclosure SOURCE_OFF5 (2026-10-01)

Changed only candidate JSON three fields across17 locales plus blockers, existing validator/staged renderer/related tests/review. Optional accountbound application/status/appeal has no Plus prerequisite; current routes are unavailable/manual-only and collect no raw order/proof or provide code, price or entitlement. Review approval is not benefit delivery. Claim-evidence server vault is separate from health E2EE and sync retention; missing approved case/evidence/audit/receipt/duplicate-marker policy disables collection, no invented periods/operator/date.

- Retained PASS: exact10 focusedmethods,17source locales,108candidate format/panel/hreflang/bytes and5047links;90privacy/help/terms output hashes changed,18deletionoutputs unchanged. Independent78c6d7be source review135 readonly assertions approves5. Root exactpre/post/diff/unselectedpreservation verified; public144/canonical3 sources untouched.
- FAIL retained: failing-first1; initial10 6PASS4FAIL from existing2-answercontract, responsible renderer correction related1 then final10PASS; parserpackaging failure no test rerun. Native-speaker/legal/browser/native/provider/operational/store proofs NOT_RUN/BLOCKED. Candidate noindex/null-date/OFF, no publication.
- Next: integrate reviewed priorbuyer backend and typedapp clients, then qualify actual account/retention/reviewer/store-offer disclosure gates before effective publiccopy. Real offer/price/renewal wording requires actual verified code inventory and store terms. Evidence ../../release/evidence/1.0.6/IOS-SYNC-EXPERIENCE/20261001/release-acceptance-next-scope/prior-buyer-claim-proposal/legal-implementation-20261001/.

## Current — reviewed candidate integrated; publication gates pending (2026-09-30)

Owner resumed autonomous safe work. Canonical workspace release/CURRENT_HANDOFF.md owns current cross-platform status; the old pause and pre-integration notes below are historical.

Reviewed account/privacy source packet is committed at product checkpoint3cf3f952 and draft PR11. Independent final SOURCE_OFF approval: workspace release/evidence/1.0.6/legal-effective-sync-20260930/independent-final-review.json. Retained focused8 PASS,108 candidate page checks/5047 links PASS; reviewed17 localized support leads/18 affected pages close the earlier P2. This handoff correction leaves every source/renderer/test/public page byte unchanged, so matching results are reused without rebuilding.

NOT_RUN: actual provider/native/TLS/operational erasure and browser visual. BLOCKED: legal/operator/processing-location/DPA/international-transfer/effective-date, native full19 durability/key custody, retention/backup deletion/store disclosure gates. Candidate remains noindex/unpublished and readinessOFF; public144 pages remain unchanged. No active owned process/device.

Next: continue canonical native verification and resolve the listed release gates before applying candidate content to effective public pages; no publication from this draft push.

# Website handoff — canonical pointer

## Resumed local effective account integration (2026-09-30)

Independent review’s P2 iOS support-lead contradiction is repaired in the staging transform only: all17localized leads now use existing unpublished/OFF + optional-account source. The new regression failed first1/1, then exact related8/8PASS. Regeneration changed exactly18iOSsupport candidate pages; other90candidate page hashes match the before-repair receipt. EN/KO source/output truth PASS,108format/panel/hreflang/byte checks and5047local links PASS; tone1738/0 violations. Canonical source JSON/144public pages and baseline renderer dependencies remain byte-matched to earlier36iOS/54Android parity, so no whole144/native rerun. Source SHA28c8ff is unchanged; renderer/test and generated source/page hashes are refreshed in receipt.json. Earlier independent-review receipt remains historical P2 evidence until reviewer recheck; no browser appearance/deployment proof is claimed.

- Ready for coordinator review at legal primary `5fce11f6`, branch `claude/doseweek-free-ads-plus-himvw9`: ten owned source/renderer/test/review/setup/handoff files only. No commit/push/publication by this packet owner. SHA, exact dirty inventory, commands and evidence are in workspace `release/evidence/1.0.6/legal-effective-sync-20260930/receipt.json`; input source SHA28c8ff7199bc84f6027796e8a24aa4d3ad30702f36815fb61251c3a2dccfb655.
- Source17locales and focused8exact methods PASS (fail/skip/omit0). Separate1.0.6 null-date sources and108pages generated: six routes × (hash+17locales), exact panel/hreflang/output-byte identities PASS,5047local links PASS. Changed baseline renderers preserve original36iOS/54Android bytes; unchanged public144pages were not rehashed or rerun as a whole. Scoped Korean source check1738sentences/0 violations,2existing allowed/1uncovered import allowance; no native-speaker review. py_compile/diff check PASS.
- External `/account/delete/` candidate is a prominent localized email request action using the existing public support address, no Plus/reinstall/subscription-cancellation prerequisite. It requests only provider/known account ID, with identity verification before erasure; passwords/recovery/health/purchase tokens excluded. Email initiation, account/server erasure and provider unlink outcomes are distinct. No real mail/API/provider deletion request, native/TLS/operational proof, browser appearance review or publication ran.
- All 17locales carry unpublished/OFF notices and separate optional analytics/transfer choices. Original primary features stay Free; the owner does not guarantee perpetual ad-free use, and promotional acquisition alone is not paid-purchase proof. Verified1month→monthly Plus program is unimplemented and makes no issuance promise. Owner choice is resolved; prior ad-free purchase-claim counsel/platform review remains BLOCKED. Effective date/operator/location/DPA/international transfer/full19native settings+key custody/provider/retention/backup deletion/store forms remain release gates. Actual provider/health sync stays OFF.
- First assertion/render/link failures are retained and their related repairs passed. The initial custom tone audit failed before auditing because the wrong Rules type was supplied; its raw file was accidentally overwritten, so only a clearly labelled tool-trace summary is retained. Both release readiness/date guards remain BLOCKED. No active PID/device. **Next action:** coordinator reviews the bounded packet, commits/pushes the same draft PR11, and resolves listed gates before replacing effective public sources or publishing.

## Historical checkpoints before this resumed local packet

The checkpoints below retain their original evidence and next-action text as history. The resumed packet above and canonical workspace handoff own current instructions.

## Historical — OWNER_PAUSE_RELAUNCH home continuation (2026-09-30)

The owner requested a handoff for continuation from home. Development, new native jobs,
activation and publication are paused until the owner asks to resume. The canonical live
state is `release/CURRENT_HANDOFF.md` in the Doseweek workspace; exact heads, owned dirty
inputs, process cleanup, PASS/FAIL/NOT_RUN/BLOCKED and one next action are in
`release/evidence/1.0.6/home-continuation-20260930/receipt.json` there. Preserve local isolated
worktrees and original Claude lanes; do not re-run old start commands or whole suites.

The last iOS instant/journal gate ended65: exact13 executed,12PASS/1FAIL
(`nativeRoundTrip()`: `.lossyPrecision`), skipped/omitted0; diagnostics timeout retained,
cleanup0 and owned processes drained. Retained scoped passes do not make the combined
apps or full encrypted sync validated. After owner resume, diagnose that exact failure,
then assign separate reviewed full19/signedPlus/provider-repair scopes. This checkpoint
changes handoff documentation only; previously frozen product inputs are unchanged.

## Now (2026-09-30) — provider deletion disclosure candidate

- All 17 unpublished locales distinguish server-encrypted Apple refresh capability from health E2EE keys, request-only Kakao unlink token (not retained), and account/server-data erasure from provider disconnection. Failed/unconfirmed disconnection requires manual instructions; no automatic retry is promised. These are planned OFF contracts, not public/live behavior.
- Independent server review retains concurrent link/delete, multi-identity capability coverage and proxy/client deadline activation blockers. Hourly retention pruning is source-only; operational deployment, monitoring/backup erasure and bounded lag are unproven. Older request-only pruning snapshot below is historical.
- Verification **PASS17locale validator + existingfocused2/2**, diffPASS; only three owned candidate/review/handoff paths changed, all public/generated/renderer inputs unchanged versus dd711. Prior144-page source parity reused only for rendering. Native/provider/webdelete/live/counsel/date remain NOT_RUN/BLOCKED. Receipt/logs: workspace `release/evidence/1.0.6/legal-provider-lifecycle-20260930/receipt.json`. No process/device or publication.
- Exact next action: validate this source candidate, publish only to same draft PR11, then integrate repaired reviewed server/native truth into effective17 sources and working deletion page.

## Now (2026-09-30) — account, encrypted sync and announcement disclosure draft

- Current unpublished purchase-vault disclosure: all17 locales now distinguish server-only
  AES-256-GCM encrypted Apple original transaction ID/Play token lookup references from
  end-to-end health records and separate recovery keys. The source candidate prunes refs
  only during Plus refresh; request-independent scheduled erasure, keyed tombstone legal
  basis/retention and operational backup deletion remain BLOCKED. Validator17/17, exact
  focused tests2/2, diff check PASS; no native/TLS/provider/publication proof. Source SHA
  `930e2048558d5b25b67e15c9a99d60a49015c20315cb281e94eb6fb295f3e5fe`; receipt
  `release/evidence/1.0.6/legal-purchase-vault-disclosure-20260930/receipt.json`.
  Source/review commit `be891c01` is pushed; local, remote-tracking and open/draft PR #11
  head match. PR body readback SHA `2a2c295839811d5957bdef4b862493d2ae1f6b405dca766da24cc9c2d1fc858b` matches the saved body.
  First remote-head preflight saw the previous4abb head just after push and FAILED before
  body mutation; refreshed readback showed be891c01, then exact body/head checks passed.
  Source-backed terminology correction: purchase tombstones retain a keyed digest and
  store marker with the account link removed; no legal anonymity claim is made. This
  docs-only correction leaves candidate930e2048/renderer/native inputs unchanged.
  Public render inputs/pages remain unchanged. Next: complete source/API/native erasure
  proof and legal review, then reconcile effective disclosures and deletion route.

- Current release blocker: official Apple §3.1.2(a) requires preserving prior paid buyers'
  primary functionality when moving to subscriptions. The owner is deciding the separate
  perpetual legacy-rights/ad-free boundary; the agreed one-month new Plus code alone does not
  resolve it. `docs/ACCOUNT_SYNC_RELEASE_REVIEW.md` records this source-backed question.
  Candidate JSON and generated pages remain byte-unchanged and unpublished. Docs-only diff
  check PASS; candidate SHA `213d6d90872bbcec0e59940ead34ff1849911b1c54b9db08e82c2ac750ba8acb`
  matches the prior 17-locale/2-test/144-page results, which remain reusable. No new native or
  public check ran. Receipt: `release/evidence/1.0.6/legal-legacy-rights-gate-20260930/receipt.json`.
  Review/handoff source commit `49a58c3` was pushed; local, remote and open/draft PR #11 matched.
  Its description now states current behavior, exact verification and blockers, with the previous
  body retained in evidence; the new body was read back exactly. This follow-on doc checkpoint
  records that completed stage and changes no candidate/render/test input.
  Next action:
  record the owner answer, prove the actual legacy entitlement and restore behavior, then
  reconcile effective disclosures with the completed native/API/store contract.
- Latest owner decision: a server-verified Apple or Google Plus purchase linked to the same
  DoseWeek account shares **all** Plus benefits across iOS and Android (ad removal, Plus tools
  and encrypted sync), while each app retains its native store purchase path. The unpublished
  17-locale account candidate now adds the ad-removal/tools disclosure. The owner also chose
  in-app prior-buyer application and purchase verification, then an individual one-month code
  that renews as **monthly Plus** after the free month unless canceled. The review draft records
  the price/period/date/cancellation disclosure requirement. Candidate source validator
  **PASSed 17/17 locales**, focused unit tests **PASSed 2/2**, and `git diff --check` PASSed;
  candidate source SHA-256 is `213d6d90872bbcec0e59940ead34ff1849911b1c54b9db08e82c2ac750ba8acb`.
  Generated public pages and their renderer inputs are unchanged, so the prior 144/144 site
  PASS remains input-matched; no new live/browser/native check ran. No public page or store
  offer changed. Source/review were committed at `d3bb6983` and pushed on the same draft
  branch. PR #11's description was appended without replacing its earlier text and read back
  exactly while open/draft, with the remote head matching the pushed branch. This follow-on
  handoff checkpoint records the final state; a further doc-only commit does not change the
  candidate source or invalidate the focused checks. **Next action:** once server/native account
  and store-offer behavior is proved, reconcile the effective 17-locale privacy, Terms and help
  sources, generate the working deletion route, settle the effective date/store declarations
  and run the release gate. Counsel and native-speaker review remain.
- Subsequent owner decision: when an Android paid-app order lookup cannot prove that the
  claimant is the original buyer, the in-app code request must go to **manual review and
  dispute handling**; it cannot automatically issue a code. The unpublished release review
  now records this. No buyer-submitted order ID, code or receipt was handled, and no public
  candidate page promises issuance. Docs-only diff check **PASSed** and the unchanged
  unpublished candidate still validates 17/17 locales. Existing 2/2 candidate unit and
  144-page site results retain identical relevant inputs; no native/live check ran. The review
  and this handoff were committed/pushed on the same draft branch, and PR #11 remained open/draft
  with the manual-review section appended to its existing body and read back exactly. This
  doc-only checkpoint records that state; no publication occurred. **Next action:** after
  actual app/API/offer proof, reconcile the effective 17-locale privacy, Terms and help sources,
  working deletion route, date and store declarations, then run release/counsel review.
- Owner scope for 1.0.6: optional Apple/Google/Kakao sign-in, Plus-only automatic encrypted
  records/settings sync across iOS and Android under one DoseWeek account, a recovery code
  needed on a new device, 30-day encrypted-backup retention after Plus expiry, account deletion,
  and public start-up notices before onboarding with a per-notice one-week snooze. The planned
  API and notice feed are under `doseweek.wonyoungchoi.dev`; neither is deployed as a DoseWeek
  service. The account-deletion web path is only planned.
- `docs/account-sync-content.candidate.json` is a separate five-topic, 17-locale **unpublished**
  candidate (account, sync, retention, announcement, deletion web copy). It does not replace the
  current generated pages, which still describe the existing no-account apps.
  `docs/ACCOUNT_SYNC_RELEASE_REVIEW.md` has the store privacy/Data safety and account-deletion
  release draft, source conflicts and primary sources. `scripts/account_sync_candidate.py` validates coverage and
  `check_site.py --release` now refuses an unintegrated candidate, in addition to the existing
  date/server gates. Source SHA and exact dirty files are in
  `release/evidence/1.0.6/legal-sync-candidate-20260930/receipt.json`.
- The 2026-09-30 contract reconciliation fixes the planned API base to `/v1` and keeps the
  public static announcement feed at `/announcements/v1.json`. The candidate's unresolved list
  now names the closed Plus sync gate, missing shared record graph/merge and unpublished feed.
  `docs/ACCOUNT_SYNC_RELEASE_REVIEW.md` distinguishes those targets from implemented features;
  it also records the owner's in-app prior-buyer claim and verification decision. Apple signed
  AppTransaction and a proposed user-supplied Play order ID are design inputs; claim-data
  fields, retention, fraud checks and issuance remain unresolved, so no code is promised.
  The effective public pages were not regenerated from this draft.
  Contract receipt: `release/evidence/1.0.6/legal-sync-contract-20260930/receipt.json`.
- Verification: candidate source **PASS 17/17 locales**; focused tests **PASS 10/10**;
  `check_site.py` **PASS 144/144 generated pages** and Korean tone **PASS 1493 sentences,
  0 violations**; `git diff --check` **PASS**. Initial validator **FAIL** because it required
  the English spelling of Kakao in Korean/Japanese; logs are preserved and the narrow related
  family passed after accepting localized names. `check_site.py --release` is **BLOCKED** by the
  unset effective date; the new unintegrated-candidate refusal has a passing unit test. Native,
  browser, live API and account deletion flow are **NOT_RUN**. Logs and source hashes are in the
  receipt above. No owned process/device, publication, console change or production deployment.
  **Next action:** after the native/API contract is verified, replace conflicting effective
  privacy/terms/help sources in all 17 locales, generate the deletion route and pages, then
  verify store declarations and run the release gate. Counsel and native-speaker review remain.
- The prior source `25e9c95` and handoff `6cbb04e` commits are on local and remote
  `claude/doseweek-free-ads-plus-himvw9`. The contract edit's source validator **PASSed 17/17
  locales** and focused tests **PASSed 2/2**; `git diff --check` PASSed. The previous 144-page
  site PASS is reusable because generated pages, renderers and site-check inputs are unchanged;
  no new browser or native check ran. The release gate remains BLOCKED by the unset date and
  unintegrated candidate. The one-month-code claim-data addition passed the same focused 17/17
  validator, 2/2 tests and diff check. Source commits `db177ad` and `9da5a47` were pushed.
  PR #11 is open/draft; its head matched local and remote `9da5a47` and its description was
  read back exactly after updating the unpublished account/sync draft and in-app promo design.
  No merge or publication. **Next action:** after the server and native contracts are verified,
  replace conflicting effective 17-locale privacy, Terms and help sources, generate the working
  deletion route, settle the effective date and store declarations, then run the release gate.

Read the [canonical current handoff](../../release/CURRENT_HANDOFF.md) first, then the
[workspace entry](../../START_HERE.md) and relevant [release journal](../../release/release-journal.json) entries.
These are the single source for recorded live status, repository identities, evidence and
the current owner stop. This file does not duplicate counts, HEADs or executable next steps.

## Open owner questions (2026-09-30)

- Resolved in the resumed packet: original primary features remain Free, perpetual ad-free use is not guaranteed, and promotional acquisition alone is not paid-purchase proof. Counsel/platform assessment of prior ad-free purchase claims remains a release blocker; the owner decision is no longer pending.
- The owner chose to include free + ads + Plus in 1.0.6. The release effective date is still
  unset, and the app/page version fields still describe 1.0.5; the release coordinator must
  align them with the final 1.0.6 builds before publication.
- The purchase-verification server's location, operator and retention, the Korean ad-data
  overseas-transfer basis, the Terms and ad-transfer legal review, and the final UI-label and
  native-speaker reviews remain open. `check_site.py --release` must keep failing until the
  date and registered server placeholders are resolved.
- The owner chose in-app application and prior paid-app purchase verification before individual
  one-month code delivery, followed by monthly Plus auto-renewal unless canceled. Eligibility,
  fraud controls, actual store price and offer configuration, and issuance are unresolved; no
  candidate page promises an issued code.

## Now (2026-09-30) — 1.0.6 rewarded-ad copy candidate

- On `claude/doseweek-free-ads-plus-himvw9`, commit `c97f8582` records the 17-locale iOS,
  Android and Terms sources now describe one earned reward adding 24 hours, no more than two
  in a rolling 24 hours, at most 48 hours remaining, and another offer only when at most
  24 hours remain. The help and Terms copy explains the five-minute clock-rollback pause and
  that automatic ads and Plus offers are hidden during the pass. The privacy copy replaces
  the old 30-minute record and describes local reward times, expiry and last-observed device
  time. The existing earned-reward and early-close conditions remain. No effective date or
  server placeholder was filled. Sources: `docs/{ios-content.json,android-content.candidate.json,
  terms-content.json}`; renderer guard and regression test:
  `scripts/{render_terms.py,test_monetization_copy.py}`; 90 generated HTML pages updated.
- Source SHA-256: iOS `507576784ad768917d2c8c19c8f028fcd63a98aa9f6442b60c73b30c89e76ece`,
  Android `98da96328b7ccea419704accd8f22fc6c98d9befafd86a98fe171d3d28a5857b`,
  Terms `e6774ee2263ad58ec754ff2226345c860c7598d92390c882da39ca1ca2e0e16e`.
  The six renderer `--check` commands PASS; `check_site.py` PASS (144 pages);
  `korean_tone.py` PASS (0 violations); the five listed unit modules PASS (105 tests);
  `git diff --check` PASS. The release coordinator preserved the logs and hashes in
  `release/evidence/1.0.6/monetization-integration-20260930/legal/receipt.json`.
  The complete six-renderer log was recaptured with identical inputs and preserved at
  `release/evidence/1.0.6/monetization-integration-20260930/legal/render-checks-complete.log` (SHA-256
  `138d675304d118e9b3ff91599ad5c47008ef043be3876b3fcfc8d80bd3ae75a6`);
  the initial renderer log captured only the final sitemap command and is retained as partial
  evidence. `check_site.py --release` is BLOCKED by `NEXT_RELEASE_EFFECTIVE_DATE=None`;
  browser appearance review is NOT_RUN. These are source/render checks, not native app validation.
- No owned process or device. Commit `c97f8582` was pushed to the same branch and draft
  PR #11's description now records the new reward rules, verification results and blockers;
  it remains open and unmerged. The changed set was the three JSON sources, two Python files,
  this handoff and 90 generated HTML pages; no unrelated files were changed. GitHub Pages still
  serves `main`, so the candidate copy is not public.
- **Next action:** once the owner supplies the 1.0.6 effective date and verification-server
  location/operator/retention, replace the registered placeholders in all 17 locales and
  align the page versions; then complete counsel, app-string, native-speaker and browser
  reviews before the release gate. Do not merge or publish on the strength of local checks.

## Status (2026-09-29)

- The site serves help and privacy pages from `main` via GitHub Pages at
  <https://doseweek-legal.wonyoungchoi.dev/>. PR #4 (merge `40d0359`, 2026-09-24) and PR #6
  (merge `efaf1ff`, 2026-09-28) are merged; `LICENSE` was added in `8b53cf0` (2026-09-28).
  On 2026-09-29 the live `/`, `/privacy/`, `/support/`, `/android/privacy/` and
  `/android/support/` pages matched the files on `main` at `8b53cf0` byte for byte.
- iOS 1.0.5 (build 19) is live on the App Store since 2026-09-29.
- Android 1.0.5 (versionCode 13) is being submitted to Google Play on 2026-09-29. It is not
  live yet. The site already states the Android 14 minimum for versionCode 13.
- 1.0.6 planning for both apps: [release/1.0.6/HANDOFF-1.0.6.md](../../release/1.0.6/HANDOFF-1.0.6.md)
  (being prepared on 2026-09-29).
- Per-language URLs (1.0.6 search work, 2026-09-29): 119 static pages `/<locale>/<route>/` (7 routes x 17 locales)
  with hreflang + x-default on all 126 pages and a sitemap with alternates; the hash pages (`/privacy/#ko`)
  stay canonical and keep working. Receipt: `release/evidence/1.0.6/W0/`.
- Branch and PR tidy: `release/evidence/lean-20260923/workspace-cleanup-20260923/repo-tidy-20260929-website.json`.

## Monetization candidate (2026-09-29, not published)

- Branch `claude/doseweek-free-ads-plus-himvw9` holds candidate copy for the free download with
  ads and the Plus subscription (owner instruction 2026-09-29; binding policy
  `docs/MONETIZATION_POLICY.md` in both app repositories): iOS privacy sections 11 (ads) and 12
  (purchases), Android sections 5 (ads) and 6 (purchases), Plus and ads FAQ answers on both
  support pages, and the new Terms of Use route `/terms/` (`docs/terms-content.json`,
  `scripts/render_terms.py`). The live 1.0.5 apps have none of these features. Nothing is merged
  to `main`, pushed for publication or deployed.
- The new and changed fields are translated into the 15 locales other than en and ko (2026-09-29;
  no native-speaker review is claimed). The per-language titles and descriptions keep interim
  wording. The translated server-location and retention placeholders are registered in
  `legal_release.RELEASE_PLACEHOLDERS`; `check_site.py` keeps every locale's placeholder count
  equal to en.
- Local checks on 2026-09-29 after the translation: every renderer `--check`, `check_site.py`,
  `korean_tone.py` and the four unit-test modules pass. `check_site.py --release` fails by design
  (date not set).
- Review fixes (2026-09-29, findings 14, 15, 26 and 31; all 17 locales, no native-speaker review
  claimed): both ads sections (iOS 11, Android 5) list the overseas-transfer details of the Google
  Mobile Ads SDK and UMP (recipient Google LLC, Google Ireland Limited for the EEA and Switzerland,
  contact, countries, items, timing and method, purpose, retention, how to refuse) and state
  plainly that where Google shows no consent message, for example in Korea, neither Google nor
  DoseWeek offers a refusal, so Plus is the only way to avoid ad processing. No legal basis is
  named: the Korean consent question stays with counsel (monetization policy section 1.1). The
  Android ads section names the app set ID; the Android purchases section says the server confirms
  the purchase with Google Play (no on-device signature check in release builds); iOS section 12
  gained the retention placeholder, and `legal_release.purchase_placeholder_parity_errors` (run
  by `check_site.py`, tested in `scripts/test_monetization_copy.py`) keeps the two purchase
  sections' server placeholders aligned. The Android catalog and its 17 `privacy_policy.xml`
  files in DoseweekPlayStore were regenerated from the same candidate. Checks: every renderer
  `--check`, `check_site.py`, `korean_tone.py` and the five unit-test modules pass;
  `check_site.py --release` still fails by design.
- BLOCKED: (1) the owner sets `NEXT_RELEASE_EFFECTIVE_DATE` in `scripts/legal_release.py` and
  the matching dates in the three content files; (2) the purchase-verification server's location,
  operator and retention replace `legal_release.RELEASE_PLACEHOLDERS` in all 17 locales (Android
  section 6 and iOS section 12 both carry the location and the retention sentences); (3) the app
  version for the monetization release replaces the 1.0.5 page version; (4) app UI labels quoted
  here ("Privacy choices for ads", "Report an ad", "Restore purchases", "Settings > About >
  What's new", and their translations) are matched to the final app strings in each locale;
  (5) the owner and counsel review the Terms, the ads overseas-transfer details and the section
  1.1 items of the monetization policy; (6) native-speaker review of the translations (not done);
  (7) browser review of the new pages (not run).

## Historical (2026-09-23 to 2026-09-28)

The paragraph below described the state before PR #4 and PR #6 were merged. It is kept as
history, not as current status.

> Publication remains owner-paused. The candidate help, privacy and brand pages are not public-release proof. Preserve the existing draft and follow the canonical handoff for the ordered app-upload/publication boundary and remaining privacy operations. Local checks or an old live-page response do not authorize a new deployment.

The [previous local handoff](../../release/evidence/lean-20260923/workspace-cleanup-20260923/repo-docs-before/website/docs/CURRENT_HANDOFF.md) is preserved as historical evidence only.
Do not run its old commands or treat its former next action as current authorization.
