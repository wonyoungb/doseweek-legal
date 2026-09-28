# DoseWeek 기록 추출 초안 — 버전 1

이 안내는 iPhone·iPad용 DoseWeek 1.0.5 이상의 ‘다른 앱에서 기록 가져오기’에서 쓸 수 있어요. Android용 DoseWeek는 설치된 버전에 이 화면이 보이면 쓸 수 있어요. 화면이 보이지 않으면 먼저 DoseWeek를 업데이트하세요. 가져오기를 마칠 때까지 원본 기록은 보관하세요.

이 형식은 DoseWeek 가져오기 화면에서 검토할 수 있도록 근거를 보존해요. 암호화 백업이나 임상 판단이 아니고, 특정 앱 형식을 보증하지도 않아요.

앱 제한: 한 번에 최대 10,000행, 입력 JSON은 최대 10MiB까지예요. 마치지 않은 검토 초안은 iPhone·iPad에서 최대 4MiB, Android에서 최대 1MiB(1,048,576바이트)까지예요. 더 큰 가져오기는 잘라 내지 않고 거부해요. 컨디션 행과 미분류 행은 저장할 수 없으니 원문을 남긴 채 선택을 해제하세요. Android에서는 예전에 가져왔다가 삭제한 기록과 일치하는 행은 이미 가져온 것으로 처리되고, 복원되지 않아요.

1. 최상위 format은 doseweek.record_extraction_draft, version은 1, reviewed_by_user는 false예요. records와 unreadable_sections는 배열이에요. 알 수 없는 필드는 조용히 버리지 않고 거부해요.

2. 각 행에는 틀의 모든 필드와, 초안 안에서 고유한 row_id가 있어요. 원본 식별자가 자동으로 DoseWeek 기록 ID가 되지는 않아요. source_references에는 문서 이름, 알 수 있을 때 1부터 시작하는 페이지 번호, 행 이름, 보이는 원문을 보존해요. null은 모른다는 뜻이에요.

3. dose_value_text와 measurement_value_text의 숫자 원문은 문자열로 보존하세요. 철자, 소수점 표기, 단위, 날짜·시각 원문을 유지하세요. 읽을 수 없거나 지원하지 않는 정보는 visible_text와 needs_review에 남기고 값을 만들지 마세요.

4. date_iso는 전체 날짜가 명확하고 유효할 때만 YYYY-MM-DD로 적어요. time_24h는 HH:mm 형식이고, 원본에 보이는 초·소수초를 덧붙일 수 있어요. time_zone과 utc_offset에는 원본의 명시적 근거가 필요해요. 빠졌거나 모호한 필드는 빈 문자열이나 추정한 날짜·시각이 아니라 null로 둬요.

5. 스키마는 구조만 확인해요. DoseWeek 가져오기는 실제 달력 날짜, 단위, 지원하는 약과 측정 항목 매핑, 시간대, 중복도 확인해요. 그래도 모든 행은 직접 검토해요. 스키마를 통과했다고 해서 저장이 허용되지는 않아요.

6. 앱은 필수 항목이 해결되지 않은 선택 행을 거부해요. 선택한 기록은 기존 기록을 덮어쓰지 않고, 모두 추가하거나 하나도 추가하지 않는 방식(원자적)으로 한 번에 추가해요. 시각이 없는 행은 앱에서 실제 시각을 입력하고 확인해야 해요. 자정이나 정오 같은 임시 시각은 쓰지 않아요.

7. 초안과 원본 파일은 비공개로 보관하세요. 이 정적 안내에는 업로드 폼이 없어요. 외부 AI를 선택하면 자료가 그 서비스로 전송되고, 그 서비스의 약관이 적용돼요. 직접 입력이나 기기 내 텍스트 인식으로도 같은 필드를 준비할 수 있어요. 파일을 직접 만들 때는 AI 응답 중 JSON 내용만 UTF-8 형식의 .json 파일로 저장하세요. 초안에는 기록을 최대 10,000개까지 넣을 수 있어요. 디코딩된 각 JSON 문자열은 UTF-8 기준 16 KiB(16,384바이트)까지예요. 이 바이트 한도는 앱이 검사해요. JSON Schema의 maxLength는 UTF-8 바이트가 아니라 Unicode 코드 포인트 수를 세어요. JSON 파일은 최대 10 MiB, 중첩 깊이는 32단계까지 허용해요.

```json
{
  "format": "doseweek.record_extraction_draft",
  "version": 1,
  "reviewed_by_user": false,
  "records": [
    {
      "row_id": "row-0001",
      "record_type": "unclassified",
      "source_app": null,
      "source_record_id": null,
      "source_references": [
        {
          "document": null,
          "page": null,
          "row": null,
          "visible_text": null
        }
      ],
      "date_text": null,
      "date_iso": null,
      "time_text": null,
      "time_24h": null,
      "time_zone": null,
      "utc_offset": null,
      "medication_name": null,
      "dose_value_text": null,
      "dose_unit": null,
      "site_text": null,
      "measurement_type": null,
      "measurement_value_text": null,
      "measurement_unit": null,
      "symptom_text": null,
      "severity_text": null,
      "note": null,
      "needs_review": []
    }
  ],
  "unreadable_sections": []
}
```
