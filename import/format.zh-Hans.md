# DoseWeek 记录提取草稿 — 版本 1

你现在可以准备并核对 JSON 草稿。本指南不代表你已安装的 DoseWeek 能够保存它。请保留原始记录，直到应用明确支持此格式。

此格式保留来源证据，供用户手动核对。它不是加密备份、临床决策、厂商格式保证，也不能证明当前应用能够导入它。

Android 导入：保存草稿上限为 1 MiB（1,048,576 字节）和 10,000 行，独立于 JSON 的 10 MiB 上限。症状行和未分类行无法保存，请保留原文并取消选择。已删除的匹配记录仍视为已导入，不会恢复。iOS 候选版本用于继续编辑的草稿保存上限另为 4 MiB。请勿假定两个平台或已安装应用的行为与可用功能相同。

1. 顶层 format 为 doseweek.record_extraction_draft；version 为 1；reviewed_by_user 为 false。records 和 unreadable_sections 为数组。遇到未知字段应拒绝处理，不要悄悄丢弃。

2. 每行包含所有模板字段，以及草稿内部唯一的 row_id。来源标识符绝不能自动成为 DoseWeek 记录 ID。source_references 保留文档标签、已知且从 1 开始的页码、行标签和可见文本；null 表示未知。

3. 在 dose_value_text 和 measurement_value_text 中以字符串保留原始数字。保留拼写、小数符号、单位和来源中的日期与时间文本。无法辨认或不支持的信息保留在 visible_text 和 needs_review 中；绝不能编造数值。

4. 仅当完整日期明确且有效时，date_iso 才使用 YYYY-MM-DD。time_24h 使用 HH:mm；如来源显示秒或小数秒，可保留这些部分。time_zone 和 utc_offset 需要明确的来源证据。缺失或含义不明确的字段使用 null，不使用空字符串或猜测的日期与时间。

5. 结构定义只检查结构；未来的导入功能还必须检查实际日历日期、单位、支持的药品和指标映射、来源证据、时区歧义以及重复记录。仅通过结构验证，绝不意味着可以保存。

6. 计划中的保存流程会核对所有选定行，拒绝尚未解决的必填字段，并在不自动覆盖现有记录的情况下，将选定行全部添加或全部不添加。保存前必须明确支持仅有日期的事件所表达的含义；不得用午夜或正午作为占位时刻。

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
