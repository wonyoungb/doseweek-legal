# DoseWeek 인수인계 — 2026-09-15 저녁 (사용량 90% 시점 체크포인트)

전체 요청은 미완료다. 이 문서는 진행 중인 병렬 작업이 세션 종료로 끊길 때 다음 세션이 그대로 이어가기 위한 것이다. 당일 상세 기록은 같은 폴더의 `COORDINATOR_LOG.md`(시간순), 결정은 `STATE.json`의 `decisions`(HEALTH/DESIGN/NUTRITION/BUGFIX-PARITY/CORE/IMPORT-20260915-*), 설계는 `designs/`, 워크플로 스크립트 사본은 `workflows/`에 있다. 아침 인수인계 `HANDOFF.md`의 확정 원칙은 계속 유효하다.

## 1. 저장소별 브랜치 상태 (전부 원격 푸시됨, main 미병합)

### iOS (`wonyoungb/DoseWeek`, 로컬 폴더 `DoseDay`, worktree `/private/tmp/doseweek-v11-20260913/ios*`)
| 브랜치 | HEAD | 내용 / 검증 |
|---|---|---|
| `codex/v11-bugfix` | 93ae0e2 | 아침 기준 + 내보내기 달력 경계 수정(7e8681b, 93ae0e2). 전체 CI는 이 위에서 중단됨(호스트 과부하로 코디네이터가 중지, 결과 아님). 검증 레인이 아래 4개를 여기에 병합 중. |
| `fix/history-visible-actions` | 7e87079 | ED01b/PR10/ED04. 작성·리뷰 완료, 검증 레인이 컴파일·red/green 중. |
| `fix/record-flow-past-drafts` | 4107c89 | PR09/PR03/ED11/PR11. 동일. |
| `test/bugfix-variants` | d9661a3 (+검증 중 WIP는 `test/bugfix-variants-verify-wip` a87f905) | 변형 테스트 + "Front view". |
| `fix/health-body-composition` | 6c5312e | BMI 가져오기, 계산 체지방량, 체중+체지방률 동시 입력. 단위 1188 통과, UI 5/5 3기기. 전체 CI 전. |
| `feat/history-import` | 5d542d7 | 기록 가져오기 전체. 단위 88/88, UI 3/3 3기기. red 증명 5건 미실행(`docs/HISTORY_IMPORT_HANDOFF.md`). |
| `feat/core-engines` | 450c104 | 개별 예정일·그래프 기준·캘린더 planner 순수 엔진, fixture v4 SHA 고정, 122/122. |
| `feat/nutrition-core` | 5013e92 | 영양 계산 core P1, 147/147. |
| `feat/stage2-base` | 68f5d8d | import(e7b973b)+core+nutrition 병합 베이스. stage 2 레인이 여기서 분기. 5d542d7은 아직 미병합. |

### Android (`wonyoungb/DoseweekPlayStore`, worktree `/private/tmp/doseweek-v11-20260913/android*`)
| 브랜치 | HEAD | 내용 / 검증 |
|---|---|---|
| `main` | 79bb210 | 검증된 main(변경 없음). |
| `feat/history-import` | 7c5cdb3 | UI·데이터 서브레인 병합 + 실제 파일 선택기·CSV/TSV·17개 언어 여정. 게이트(공식 CI+매트릭스) 실행 중 → 통과 시 PR·main 병합까지 레인이 수행. |
| `fix/temporal-parity` fd7e34f, `fix/record-drafts-retry` 37ab427, `test/bugfix-variants` a3ab0ac | 버그수정 후속. 검증 레인이 완료. |
| `fix/health-body-composition` | 6bada41 | 계산 체지방량, JVM 증명. Compose 테스트 4건 기기 미실행. |
| `fix/drive-unregistered-status` | f75b661 | Google 코드 8 등록오류 분류. UI 문자열 변경 → 85장 재촬영 필요, 병합 보류. |
| `release/candidate-2026-09-15` | de22f09 | 위 5개 버그수정 브랜치 병합 후보(검증 레인 산출). import·stage2 병합 예정. 매트릭스 pin 재발견·재촬영 필요. |
| `feat/core-engines` 998a101, `feat/nutrition-core` 3bdda12, `feat/nutrition-data` a2eb701 (release d1f046b4…), `feat/stage2-base` a8e96e8 | 엔진·영양 core·식품 데이터 릴리스·stage2 베이스. |

### Legal (`wonyoungb/doseweek-legal`)
`candidate/import-guide` cc6fa49: 17개 언어 가져오기 안내 후보(preparation_only). 미병합·미게시.

## 2. 세션 종료 시 살아있던 워크플로 (재개 명령)

스크립트는 `workflows/` 또는 `~/.claude/projects/.../workflows/scripts/`. 재개: `Workflow({scriptPath, resumeFromRunId})` — 완료된 에이전트는 캐시, 중단된 에이전트는 처음부터 다시 실행되므로 각 worktree의 `git status`/`git log`를 먼저 보고 프롬프트에 "이어서" 주석을 추가한다(지난 재개 때 그렇게 했다).
- `android-history-import-finish` wf_66648d52-299: gate 단계 실행 중(공식 `run_ci.sh` + 매트릭스는 Terminal `.command`로). 끝나면 PR·main 병합.
- `stage2-features-persistence-ui` wf_3361d0dd-0c0: iOS 베이스 빌드 단계(메모리 대기), Android 베이스 완료. 8레인(개별 예정일·그래프·캘린더·영양 P2 × 2) 미시작. 버전 예약표는 `COORDINATOR_LOG.md` "Version ledger".
- `bugfix-verify-and-fold` wf_101ba8aa-b18: Android 레인 완료(release/candidate 생성), iOS 레인 진행 중(`ios-variant-tests` 병합 정리 후 검증, 이후 `codex/v11-bugfix`에 4개 병합·푸시).

## 3. 완료된 것 (오늘)
Drive 오류 원인 확정·해결(OAuth 클라이언트 3개 = Play 서명키 3종; 실기기 연결 성공 로그 `evidence/device-drive-20260915/`), Android 버그 감사 13건(`designs/android-bug-audit.md`), 설계 5건 + 요구사항 전수 대조(`designs/`), 공유 엔진 v4, 영양 core P1, 식품 데이터 릴리스(USDA/CoFID/MEXT/식약처, 식약처 산출 요리는 검색·표시 전용), iOS 가져오기, 건강 체성분 수정, 버그수정 후속 6개 브랜치 작성.

## 4. 다음 순서
1. 살아있던 워크플로 3개 재개(위 명령). 2. iOS: 검증 레인이 `codex/v11-bugfix`에 병합 완료 후, xcodebuild 없는 틈에 `full-ci-launcher/Run-Full-CI.command`(expected-head 갱신) 실행. 통과 시 PR #7 main 병합, `BUGFIX_BASELINE.json` 작성. 3. Android: import 게이트 통과·병합 → `release/candidate`에 import·stage2·감사 수정 병합 → 매트릭스 pin 재발견 → 17개 언어 85장 재촬영 → CI+매트릭스 → main. 4. Android 감사 수정 레인(`fix/audit-2026-09-15`, 목록은 로그) 미착수. 5. stage 2 통합 후 양 플랫폼 최종 통합 검증, legal 갱신·게시, 스토어 자산. 6. 실기기 전용 항목만 BLOCKED 유지.

## 5. 주의
- 소유자 실기기 R3CX804JPJX 연결됨: 절대 설치/삭제/테스트 대상 아님. 모든 에뮬레이터 명령은 `ANDROID_SERIAL` 명시.
- 답변·서브에이전트 보고는 caveman ultra, 토큰 절약(리뷰어 1명, resume 우선, 통과한 검사 반복 금지). 사용자 메시지 초안 작성 금지.
- 호스트 24GB: iOS 빌드는 개인 DerivedData·자체 시뮬레이터, 동시 xcodebuild 2개 이하, swap 70~80% 넘으면 대기.
