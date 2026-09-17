# DoseWeek record extraction draft — version 1

This guide works with “Import records from another app” in DoseWeek 1.0.5 or later on iPhone and iPad, and in the DoseWeek Android app once that screen appears in your installed version. If you don’t see it, update DoseWeek first. Keep your original records until the import is finished.

This format preserves evidence for the review on DoseWeek’s import screen. It is not an encrypted backup, a clinical decision or a vendor format guarantee.

App limits: one import holds up to 10,000 rows and the input JSON up to 10 MiB. An unfinished review draft may be up to 4 MiB on iPhone and iPad and up to 1 MiB (1,048,576 bytes) on Android; a larger import is refused, never cut short. Symptom and unclassified rows cannot be saved; keep their source text and deselect them. On Android, rows that match records you deleted after an earlier import count as already imported and are not restored.

1. The top-level format is doseweek.record_extraction_draft; version is 1; reviewed_by_user is false. records and unreadable_sections are arrays. Reject unknown fields rather than silently discarding them.

2. Every row has all template fields and a unique draft-local row_id. Source identifiers never become DoseWeek record IDs automatically. source_references preserve the document label, one-based page when known, row label, and visible text; null means unknown.

3. Keep raw numbers as strings in dose_value_text and measurement_value_text. Preserve spelling, decimal marks, units, and date/time source text. Unreadable or unsupported information stays in visible_text and needs_review; never fabricate a value.

4. date_iso is YYYY-MM-DD only when the full date is unambiguous and valid. time_24h is HH:mm with optional visible seconds and fractional seconds. time_zone and utc_offset require explicit source evidence. Missing or ambiguous fields are null, not empty strings or guessed dates/times.

5. The schema checks structure only. DoseWeek’s importer also checks real calendar dates, units, supported medication and metric mappings, time zones and duplicates, and you still review every row. Passing the schema alone never authorizes saving.

6. The app refuses selected rows with unresolved required fields and adds the selection atomically without overwriting existing records. A row without a time needs the actual time entered and confirmed in the app; no midnight or noon placeholder is used.

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
