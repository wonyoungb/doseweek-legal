# DoseWeek record extraction draft — version 1

You can prepare and check a JSON draft now. This guide does not mean your installed DoseWeek can save it. Keep the original records until the app explicitly supports this format.

This format preserves evidence for manual review. It is not an encrypted backup, a clinical decision, a vendor format guarantee, or proof that the current app imports it.

Android import: the stored review draft is limited to 1 MiB (1,048,576 bytes) and 10,000 rows, separately from the 10 MiB input JSON limit. Symptom and unclassified rows cannot be saved; keep their source text and deselect them. Matching deleted records remain already imported and are not restored. The iOS candidate has a separate 4 MiB draft-resume limit; do not assume identical platform behavior or availability in the installed app.

1. The top-level format is doseweek.record_extraction_draft; version is 1; reviewed_by_user is false. records and unreadable_sections are arrays. Reject unknown fields rather than silently discarding them.

2. Every row has all template fields and a unique draft-local row_id. Source identifiers never become DoseWeek record IDs automatically. source_references preserve the document label, one-based page when known, row label, and visible text; null means unknown.

3. Keep raw numbers as strings in dose_value_text and measurement_value_text. Preserve spelling, decimal marks, units, and date/time source text. Unreadable or unsupported information stays in visible_text and needs_review; never fabricate a value.

4. date_iso is YYYY-MM-DD only when the full date is unambiguous and valid. time_24h is HH:mm with optional visible seconds and fractional seconds. time_zone and utc_offset require explicit source evidence. Missing or ambiguous fields are null, not empty strings or guessed dates/times.

5. The schema checks structure; a later importer must also check actual calendar dates, units, supported medication and metric mappings, source evidence, time-zone ambiguity, and duplicates. Passing the schema alone never authorizes saving.

6. The intended save flow reviews all selected rows, rejects unresolved required fields, and adds the selection atomically without automatically overwriting existing records. The meaning of date-only events must be explicitly supported before saving; no midnight or noon placeholder is allowed.

7. Keep drafts and source files private. This static guide has no upload form. Choosing an external AI sends the selected files to that service under its own terms. You can prepare the same fields manually or with on-device text recognition. If you create a file manually, save only the AI’s JSON content as a UTF-8 file ending in .json. A draft can contain at most 10,000 records. Each decoded JSON string is limited to 16 KiB (16,384 UTF-8 bytes). This byte limit is enforced by the app; JSON Schema maxLength counts Unicode code points, not UTF-8 bytes. The JSON file limit is 10 MiB; nesting is limited to 32 levels.

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
