# 다음 세션에 그대로 전달할 프롬프트 (2026-09-15 저녁판)

DoseWeek 개발을 이어서 실제로 수행해 주세요. 전체 요구는 아직 미완료입니다. 답변과 서브에이전트 보고는 전부 /caveman ultra, 토큰 절약(리뷰어 1명, 재개 우선, 통과한 검사 반복 금지)이지만 검증·guard·요구사항 범위는 줄이지 마세요.

먼저 읽을 파일:
1. `/Users/wonyoungchoi/Documents/Coding Work/DoseWeek_Continuation_2026-09-15/HANDOFF_EVENING.md`
2. 같은 폴더 `COORDINATOR_LOG.md`(시간순 기록, "Version ledger", 실행 큐), `STATE.json`(decisions 배열 전부 확정), `designs/`
3. `HANDOFF.md`(아침 인수인계 확정 원칙), `/Users/wonyoungchoi/Documents/Coding Work/DoseWeek_Final_v11_2026-09-13/00_MASTER_PROMPT.md`와 specs, 각 저장소 AGENTS.md

작업 위치는 `/private/tmp/doseweek-v11-20260913/` 아래 worktree들입니다(HANDOFF_EVENING.md 표). 모든 브랜치는 원격에 푸시되어 있으니 /tmp가 사라졌으면 fetch로 복구하세요. 기존 파일을 reset/clean/stash로 지우지 마세요.

할 일 순서: (1) 살아있던 워크플로 3개를 `workflows/` 스크립트로 재개(각 worktree 상태 확인 후 "이어서" 주석 추가) — Android import 게이트·병합, stage 2(개별 예정일·그래프·캘린더·영양 P2, 8레인), 버그수정 검증·통합. (2) iOS `codex/v11-bugfix` 통합 후 전체 CI(Terminal `.command`, expected-head 갱신) → PR #7 main 병합 → BUGFIX_BASELINE.json. (3) Android `release/candidate-2026-09-15`에 import·stage2·감사 수정(`designs/android-bug-audit.md`, 레인 미착수) 병합 → 매트릭스 pin 재발견 → 17개 언어 85장 재촬영 → CI+매트릭스 → main. (4) 최종 통합 검증, legal 갱신·게시(`candidate/import-guide`), 스토어 자산.

확정 원칙: 수정·커밋·푸시·PR·main 병합·빌드는 사전 승인, 재질문 금지. 의미가 불명확하면 질문을 한 번에 묶어서 하고 독립 작업은 계속. 소유자 실기기(adb R3CX804JPJX)는 읽기 전용, 에뮬레이터 명령은 `ANDROID_SERIAL` 명시. 사용자 메시지 초안 금지. 실기기 없는 검증만 BLOCKED. 호스트 24GB: iOS 빌드는 개인 DerivedData·자체 시뮬레이터, 동시 xcodebuild 2개 이하.
