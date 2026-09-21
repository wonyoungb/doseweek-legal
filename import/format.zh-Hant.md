# DoseWeek 紀錄擷取草稿 — 版本 1

本指南搭配 iPhone 與 iPad 上 DoseWeek 1.0.5 或更新版本中的「從其他 App 匯入紀錄」使用；Android 版 DoseWeek 在已安裝的版本出現該畫面後同樣適用。若找不到該畫面，請先更新 DoseWeek。匯入完成前請保留原始紀錄。

此格式為在 DoseWeek 匯入畫面中核對而保留依據。它不是加密備份、臨床決定，也不是對任何廠商格式的保證。

App 限制：一次匯入最多 10,000 列，輸入的 JSON 最大 10 MiB。未完成的核對草稿在 iPhone 與 iPad 上最大 4 MiB，在 Android 上最大 1 MiB（1,048,576 位元組）；更大的匯入會被拒絕，絕不截斷。症狀列與未分類列無法儲存；請保留其原文並取消選取。在 Android 上，與先前匯入後又刪除的紀錄相符的列視為已匯入，不會被還原。

1. 最上層 format 為 doseweek.record_extraction_draft；version 為 1；reviewed_by_user 為 false。records 和 unreadable_sections 為陣列。遇到未知欄位應拒絕處理，不要悄悄捨棄。

2. 每列包含所有範本欄位，以及草稿內部唯一的 row_id。來源識別碼絕不能自動成為 DoseWeek 紀錄 ID。source_references 保留文件標籤、已知且從 1 開始的頁碼、列標籤和可見文字；null 表示未知。

3. 在 dose_value_text 和 measurement_value_text 中以字串保留原始數字。保留拼字、小數符號、單位和來源中的日期與時間文字。無法辨識或不支援的資訊保留在 visible_text 和 needs_review 中；絕不能編造數值。

4. 僅當完整日期明確且有效時，date_iso 才使用 YYYY-MM-DD。time_24h 使用 HH:mm；如來源顯示秒或小數秒，可保留這些部分。time_zone 和 utc_offset 需要明確的來源證據。缺少或意義不明的欄位使用 null，不使用空字串或猜測的日期與時間。

5. 結構描述只檢查結構。DoseWeek 的匯入還會檢查真實的日曆日期、單位、支援的藥物與測量項目對應、時區與重複，而且每一列仍由您核對。僅通過結構描述驗證，絕不代表可以儲存。

6. App 會拒絕仍有未解決必填欄位的所選列，並以不可分割的方式一次新增所選內容，不覆寫現有紀錄。沒有時間的列需要在 App 中輸入並確認實際時間；不會使用午夜或中午之類的暫代時間。

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
