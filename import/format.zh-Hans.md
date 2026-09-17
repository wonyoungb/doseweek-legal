# DoseWeek 记录提取草稿 — 版本 1

本指南配合 iPhone 和 iPad 上 DoseWeek 1.0.5 或更高版本中的“从其他应用导入记录”使用；Android 版 DoseWeek 在已安装的版本中出现该界面后同样适用。如果找不到该界面，请先更新 DoseWeek。导入完成前请保留原始记录。

此格式为在 DoseWeek 导入界面中核对而保留依据。它不是加密备份、临床决定，也不是对任何厂商格式的保证。

应用限制：一次导入最多 10,000 行，输入的 JSON 最大 10 MiB。未完成的核对草稿在 iPhone 和 iPad 上最大 4 MiB，在 Android 上最大 1 MiB（1,048,576 字节）；更大的导入会被拒绝，绝不截断。症状行和未分类行无法保存；请保留其原文并取消选择。在 Android 上，与之前导入后又删除的记录相匹配的行视为已导入，不会被恢复。

1. 顶层 format 为 doseweek.record_extraction_draft；version 为 1；reviewed_by_user 为 false。records 和 unreadable_sections 为数组。遇到未知字段应拒绝处理，不要悄悄丢弃。

2. 每行包含所有模板字段，以及草稿内部唯一的 row_id。来源标识符绝不能自动成为 DoseWeek 记录 ID。source_references 保留文档标签、已知且从 1 开始的页码、行标签和可见文本；null 表示未知。

3. 在 dose_value_text 和 measurement_value_text 中以字符串保留原始数字。保留拼写、小数符号、单位和来源中的日期与时间文本。无法辨认或不支持的信息保留在 visible_text 和 needs_review 中；绝不能编造数值。

4. 仅当完整日期明确且有效时，date_iso 才使用 YYYY-MM-DD。time_24h 使用 HH:mm；如来源显示秒或小数秒，可保留这些部分。time_zone 和 utc_offset 需要明确的来源证据。缺失或含义不明确的字段使用 null，不使用空字符串或猜测的日期与时间。

5. 架构只检查结构。DoseWeek 的导入还会检查真实的日历日期、单位、受支持的药物与测量项映射、时区和重复，而且每一行仍由您核对。仅通过架构校验，绝不代表可以保存。

6. 应用会拒绝仍有未解决必填字段的所选行，并以原子方式一次添加所选内容，不覆盖现有记录。没有时间的行需要在应用中输入并确认实际时间；不会使用午夜或中午之类的占位时间。

7. 请保护草稿和来源文件的隐私。这个静态指南不提供上传表单。选择外部 AI 后，选定文件会发送给该服务，并适用该服务自身的条款。你也可以手动填写相同字段，或使用设备上的本地文字识别功能。 如果手动创建文件，请仅将 AI 回复中的 JSON 内容保存为 UTF-8 编码的 .json 文件。一份草稿最多包含 10,000 条记录。每个解码后的 JSON 字符串最多为 16 KiB（16,384 个 UTF-8 字节）。此字节上限由应用检查；JSON Schema 的 maxLength 计算 Unicode 码点数，而不是 UTF-8 字节数。 JSON 文件最大为 10 MiB，嵌套深度最多为 32 层。

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
