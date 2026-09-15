# DoseWeek 기록 추출 초안 — 버전 1

지금은 JSON 초안을 만들고 원본과 대조할 수 있습니다. 이 안내가 현재 설치된 DoseWeek의 저장 지원을 뜻하지는 않습니다. 앱이 이 형식을 명시적으로 지원할 때까지 원본 기록을 보관하세요.

수동 검토에 필요한 근거를 보존하는 형식입니다. 암호화된 백업, 의료적 판단, 업체 형식 지원 보장, 현재 앱 가져오기의 증거가 아닙니다.

1. 최상위 format은 doseweek.record_extraction_draft, version은 1, reviewed_by_user는 false입니다. records와 unreadable_sections는 배열입니다. 알 수 없는 필드는 조용히 버리지 말고 거부합니다.

2. 각 행에는 틀의 모든 필드와 초안 안에서 고유한 row_id가 있습니다. 원본 식별자가 자동으로 DoseWeek 기록 ID가 되지 않습니다. source_references는 문서 이름, 알 수 있을 때 1부터 시작하는 페이지 번호, 행 이름, 보이는 원문을 보존합니다. null은 모른다는 뜻입니다.

3. dose_value_text와 measurement_value_text의 숫자 원문은 문자열로 보존하세요. 철자, 소수점 표기, 단위, 날짜·시각 원문을 유지하세요. 판독 불가·미지원 정보는 visible_text와 needs_review에 남기고 값을 만들지 마세요.

4. date_iso는 전체 날짜가 명확하고 유효할 때만 YYYY-MM-DD입니다. time_24h는 HH:mm이며 원본에 보이는 초·소수초를 추가할 수 있습니다. time_zone과 utc_offset은 원본의 명시적 근거가 필요합니다. 누락·모호한 필드는 빈 문자열이나 추정 날짜·시각이 아닌 null입니다.

5. 스키마는 구조를 검사합니다. 향후 가져오기는 실제 달력 날짜, 단위, 지원 약품·지표 매핑, 원본 근거, 시간대 모호함, 중복도 검사해야 합니다. 스키마 통과만으로 저장을 허용하지 않습니다.

6. 예정된 저장 흐름은 선택한 모든 행을 검토하고 미해결 필수값이 있으면 거부하며 기존 기록을 자동 덮어쓰기 없이 원자적으로 추가합니다. 날짜만 있는 사건의 의미는 저장 전에 명시적으로 지원되어야 하며 임의 자정·정오를 채우면 안 됩니다.

7. 초안과 원본 파일은 비공개로 보관하세요. 이 정적 안내에는 업로드 폼이 없습니다. 외부 AI를 선택하면 자료가 해당 서비스에 전송되고 그 서비스의 약관이 적용됩니다. 직접 입력이나 기기 내 문자 인식으로도 같은 필드를 준비할 수 있습니다. 파일을 직접 만들 때는 AI 응답 중 JSON 내용만 UTF-8 형식의 .json 파일로 저장하세요. 초안에는 최대 10,000개 기록을 넣을 수 있습니다. 디코딩된 각 JSON 문자열은 UTF-8 기준 16 KiB(16,384바이트)까지입니다. 이 바이트 한도는 앱이 검사합니다. JSON Schema의 maxLength는 UTF-8 바이트가 아닌 Unicode 코드 포인트 수를 셉니다. JSON 파일은 최대 10 MiB이며 중첩 깊이는 32단계까지 허용합니다.

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
