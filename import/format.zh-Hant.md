# DoseWeek 紀錄擷取草稿 — 版本 1

你現在可以準備並核對 JSON 草稿。本指南不代表你已安裝的 DoseWeek 能夠儲存它。請保留原始紀錄，直到 App 明確支援此格式。

此格式保留來源證據，供使用者手動核對。它不是加密備份、臨床決策、廠商格式保證，也不能證明目前 App 能夠匯入它。

1. 最上層 format 為 doseweek.record_extraction_draft；version 為 1；reviewed_by_user 為 false。records 和 unreadable_sections 為陣列。遇到未知欄位應拒絕處理，不要悄悄捨棄。

2. 每列包含所有範本欄位，以及草稿內部唯一的 row_id。來源識別碼絕不能自動成為 DoseWeek 紀錄 ID。source_references 保留文件標籤、已知且從 1 開始的頁碼、列標籤和可見文字；null 表示未知。

3. 在 dose_value_text 和 measurement_value_text 中以字串保留原始數字。保留拼字、小數符號、單位和來源中的日期與時間文字。無法辨識或不支援的資訊保留在 visible_text 和 needs_review 中；絕不能編造數值。

4. 僅當完整日期明確且有效時，date_iso 才使用 YYYY-MM-DD。time_24h 使用 HH:mm；如來源顯示秒或小數秒，可保留這些部分。time_zone 和 utc_offset 需要明確的來源證據。缺少或意義不明的欄位使用 null，不使用空字串或猜測的日期與時間。

5. 結構定義只檢查結構；未來的匯入功能還必須檢查實際日曆日期、單位、支援的藥品和指標對應、來源證據、時區歧義以及重複紀錄。僅通過結構驗證，絕不代表可以儲存。

6. 規劃中的儲存流程會核對所有選定列，拒絕尚未解決的必填欄位，並在不自動覆寫現有紀錄的情況下，將選定列全部新增或全部不新增。儲存前必須明確支援僅有日期的事件所表達的意義；不得用午夜或正午作為占位時刻。

7. 請保護草稿和來源檔案的隱私。這個靜態指南不提供上傳表單。選擇外部 AI 後，選定檔案會傳送給該服務，並適用該服務本身的條款。你也可以手動填寫相同欄位，或使用裝置上的本機文字辨識功能。 如果手動建立檔案，請僅將 AI 回覆中的 JSON 內容儲存為 UTF-8 編碼的 .json 檔案。一份草稿最多包含 10,000 筆記錄。每個解碼後的 JSON 字串最多為 16 KiB（16,384 個 UTF-8 位元組）。此位元組上限由 App 檢查；JSON Schema 的 maxLength 計算 Unicode 碼點數，而不是 UTF-8 位元組數。 JSON 檔案最大為 10 MiB，巢狀深度最多為 32 層。

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
