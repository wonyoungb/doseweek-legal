# DoseWeek-Entwurf zur Erfassung von Aufzeichnungen — Version 1

Sie können jetzt einen JSON-Entwurf vorbereiten und prüfen. Diese Anleitung bedeutet nicht, dass Ihre installierte DoseWeek-Version ihn speichern kann. Bewahren Sie die Originalaufzeichnungen auf, bis die App dieses Format ausdrücklich unterstützt.

Dieses Format bewahrt Belege für die manuelle Prüfung. Es ist weder ein verschlüsseltes Backup noch eine klinische Entscheidung, eine Garantie für ein Anbieterformat oder ein Nachweis, dass die aktuelle App es importiert.

Android-Import: Der gespeicherte Prüfentwurf ist auf 1 MiB (1.048.576 Bytes) und 10.000 Zeilen begrenzt, unabhängig von der 10-MiB-Grenze der JSON-Eingabe. Symptom- und unklassifizierte Zeilen können nicht gespeichert werden; bewahren Sie den Quelltext auf und wählen Sie sie ab. Passende gelöschte Datensätze gelten weiterhin als importiert und werden nicht wiederhergestellt. Der iOS-Kandidat hat eine eigene 4-MiB-Grenze für fortsetzbare Entwürfe. Verhalten und Verfügbarkeit in der installierten App sind nicht automatisch plattformgleich.

1. Das übergeordnete format lautet doseweek.record_extraction_draft; version ist 1; reviewed_by_user ist false. records und unreadable_sections sind Arrays. Weise unbekannte Felder zurück, statt sie stillschweigend zu verwerfen.

2. Jede Zeile enthält alle Vorlagenfelder und eine eindeutige, nur im Entwurf gültige row_id. Quellkennungen werden niemals automatisch zu DoseWeek-Datensatz-IDs. source_references bewahren die Dokumentbezeichnung, die bei 1 beginnende Seitennummer, sofern bekannt, die Zeilenbezeichnung und den sichtbaren Text; null bedeutet unbekannt.

3. Bewahre unveränderte Zahlen als Zeichenketten in dose_value_text und measurement_value_text. Erhalte Schreibweise, Dezimalzeichen, Einheiten sowie den Quelltext zu Datum und Uhrzeit. Unleserliche oder nicht unterstützte Angaben bleiben in visible_text und needs_review; erfinde niemals einen Wert.

4. date_iso verwendet YYYY-MM-DD nur, wenn das vollständige Datum eindeutig und gültig ist. time_24h verwendet HH:mm, optional mit sichtbaren Sekunden und Sekundenbruchteilen. time_zone und utc_offset erfordern ausdrückliche Belege in der Quelle. Fehlende oder mehrdeutige Felder sind null, keine leeren Zeichenketten und keine geratenen Datums- oder Zeitangaben.

5. Das Schema prüft die Struktur. Ein späterer Importer muss außerdem tatsächliche Kalenderdaten, Einheiten, unterstützte Medikamenten- und Messgrößenzuordnungen, Quellenbelege, Zeitzonenmehrdeutigkeiten und Duplikate prüfen. Das Bestehen der Schemaprüfung allein erlaubt niemals das Speichern.

6. Der geplante Speicherablauf prüft alle ausgewählten Zeilen, weist ungeklärte Pflichtfelder zurück und fügt die Auswahl atomar hinzu, ohne bestehende Aufzeichnungen automatisch zu überschreiben. Die Bedeutung von Ereignissen mit ausschließlich einem Datum muss vor dem Speichern ausdrücklich unterstützt werden. Mitternacht oder Mittag als Platzhalter sind nicht zulässig.

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
