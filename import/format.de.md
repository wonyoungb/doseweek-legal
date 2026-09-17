# DoseWeek-Entwurf zur Erfassung von Aufzeichnungen — Version 1

Diese Anleitung gilt für „Einträge aus einer anderen App importieren“ in DoseWeek 1.0.5 oder neuer auf iPhone und iPad sowie in der Android-App von DoseWeek, sobald dieser Bildschirm in Ihrer installierten Version erscheint. Wenn Sie ihn nicht sehen, aktualisieren Sie DoseWeek zuerst. Bewahren Sie die Originaleinträge auf, bis der Import abgeschlossen ist.

Dieses Format bewahrt Belege für die Prüfung im Importbildschirm von DoseWeek. Es ist keine verschlüsselte Sicherung, keine klinische Entscheidung und keine Garantie für das Format eines Anbieters.

App-Grenzen: Ein Import umfasst höchstens 10.000 Zeilen, die eingelesene JSON-Datei höchstens 10 MiB. Ein nicht abgeschlossener Prüfentwurf darf auf iPhone und iPad bis zu 4 MiB und unter Android bis zu 1 MiB (1.048.576 Byte) groß sein; ein größerer Import wird abgelehnt, nie gekürzt. Symptomzeilen und nicht zugeordnete Zeilen können nicht gespeichert werden; behalten Sie ihren Quelltext und wählen Sie sie ab. Unter Android gelten Zeilen, die nach einem früheren Import gelöschten Einträgen entsprechen, als bereits importiert und werden nicht wiederhergestellt.

1. Das übergeordnete format lautet doseweek.record_extraction_draft; version ist 1; reviewed_by_user ist false. records und unreadable_sections sind Arrays. Weise unbekannte Felder zurück, statt sie stillschweigend zu verwerfen.

2. Jede Zeile enthält alle Vorlagenfelder und eine eindeutige, nur im Entwurf gültige row_id. Quellkennungen werden niemals automatisch zu DoseWeek-Datensatz-IDs. source_references bewahren die Dokumentbezeichnung, die bei 1 beginnende Seitennummer, sofern bekannt, die Zeilenbezeichnung und den sichtbaren Text; null bedeutet unbekannt.

3. Bewahre unveränderte Zahlen als Zeichenketten in dose_value_text und measurement_value_text. Erhalte Schreibweise, Dezimalzeichen, Einheiten sowie den Quelltext zu Datum und Uhrzeit. Unleserliche oder nicht unterstützte Angaben bleiben in visible_text und needs_review; erfinde niemals einen Wert.

4. date_iso verwendet YYYY-MM-DD nur, wenn das vollständige Datum eindeutig und gültig ist. time_24h verwendet HH:mm, optional mit sichtbaren Sekunden und Sekundenbruchteilen. time_zone und utc_offset erfordern ausdrückliche Belege in der Quelle. Fehlende oder mehrdeutige Felder sind null, keine leeren Zeichenketten und keine geratenen Datums- oder Zeitangaben.

5. Das Schema prüft nur die Struktur. Der Import von DoseWeek prüft zusätzlich echte Kalenderdaten, Einheiten, unterstützte Zuordnungen von Medikamenten und Messwerten, Zeitzonen und Duplikate, und Sie prüfen weiterhin jede Zeile. Das Bestehen des Schemas allein erlaubt nie das Speichern.

6. Die App lehnt ausgewählte Zeilen mit ungeklärten Pflichtfeldern ab und fügt die Auswahl atomar hinzu, ohne vorhandene Einträge zu überschreiben. Eine Zeile ohne Uhrzeit braucht die in der App eingegebene und bestätigte tatsächliche Uhrzeit; Platzhalter wie Mitternacht oder Mittag werden nicht verwendet.

7. Bewahren Sie Entwürfe und Quelldateien privat auf. Diese statische Anleitung enthält kein Uploadformular. Wenn Sie eine externe KI wählen, werden die ausgewählten Dateien gemäß den Bedingungen dieses Dienstes an ihn gesendet. Sie können dieselben Felder von Hand oder mithilfe der Texterkennung auf Ihrem Gerät vorbereiten. Wenn Sie eine Datei manuell erstellen, speichern Sie nur den JSON-Inhalt der KI-Antwort als UTF-8-Datei mit der Endung .json. Ein Entwurf darf höchstens 10.000 Datensätze enthalten. Jede dekodierte JSON-Zeichenfolge ist auf 16 KiB (16.384 UTF-8-Bytes) begrenzt. Die App prüft diese Bytegrenze; maxLength in JSON Schema zählt Unicode-Codepunkte, nicht UTF-8-Bytes. Die JSON-Datei darf höchstens 10 MiB groß sein; die Verschachtelung ist auf 32 Ebenen begrenzt.

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
