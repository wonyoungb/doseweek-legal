# Utkast för avskrift av DoseWeek-poster — version 1

Du kan förbereda och kontrollera ett JSON-utkast nu. Den här guiden innebär inte att din installerade version av DoseWeek kan spara det. Behåll originalposterna tills appen uttryckligen stöder formatet.

Detta format bevarar underlag för manuell granskning. Det är inte en krypterad säkerhetskopia, ett kliniskt beslut, en garanti för en leverantörs format eller ett bevis på att den aktuella appen importerar det.

Android-import: det sparade utkastet begränsas till 1 MiB (1 048 576 byte) och 10 000 rader, separat från 10 MiB för JSON. Symtomrader och oklassificerade rader kan inte sparas; behåll texten och avmarkera dem. Matchande raderade poster räknas fortfarande som importerade och återställs inte. iOS-kandidaten har en separat gräns på 4 MiB för återupptagbara utkast. Förutsätt inte samma beteende eller tillgänglighet på båda plattformarna eller i den installerade appen.

1. På toppnivån är format doseweek.record_extraction_draft, version är 1 och reviewed_by_user är false. records och unreadable_sections är arrayer. Avvisa okända fält i stället för att kasta bort dem utan att ange det.

2. Varje rad har alla mallfält och ett unikt row_id som är lokalt för utkastet. Källidentifierare blir aldrig automatiskt post-ID:n i DoseWeek. source_references bevarar dokumentets etikett, sidnummer räknat från 1 när det är känt, radetikett och synlig text; null betyder okänt.

3. Behåll råa tal som strängar i dose_value_text och measurement_value_text. Bevara stavning, decimaltecken, enheter och källans datum- och tidstext. Oläslig information eller information som inte stöds stannar i visible_text och needs_review; hitta aldrig på ett värde.

4. date_iso är YYYY-MM-DD endast när det fullständiga datumet är entydigt och giltigt. time_24h är HH:mm, med sekunder och bråkdelar av sekunder om de är synliga. time_zone och utc_offset kräver uttryckligt belägg i källan. Saknade eller tvetydiga fält är null, inte tomma strängar eller gissade datum och klockslag.

5. Schemat kontrollerar strukturen. En framtida importfunktion måste även kontrollera faktiska kalenderdatum, enheter, mappningar av läkemedel och mätvärden som stöds, källunderlag, tvetydighet kring tidszon och dubbletter. Att enbart klara schemavalideringen tillåter aldrig sparande.

6. Det planerade sparflödet granskar alla valda rader, avvisar olösta obligatoriska fält och lägger till hela urvalet eller inget alls, utan att automatiskt skriva över befintliga poster. Betydelsen av händelser med enbart datum måste stödjas uttryckligen före sparande; midnatt eller middagstid får inte användas som platshållare.

7. Håll utkast och källfiler privata. Denna statiska guide har inget uppladdningsformulär. Om du väljer en extern AI skickas valda filer till den tjänsten enligt dess egna villkor. Du kan förbereda samma fält manuellt eller med textigenkänning på enheten. Om du skapar en fil manuellt sparar du endast JSON-innehållet från AI-svaret som en UTF-8-fil med ändelsen .json. Ett utkast får innehålla högst 10 000 poster. Varje avkodad JSON-sträng är begränsad till 16 KiB (16 384 UTF-8-byte). Appen kontrollerar denna bytegräns; maxLength i JSON Schema räknar Unicode-kodpunkter, inte UTF-8-byte. JSON-filen får vara högst 10 MiB och nästlingsdjupet är begränsat till 32 nivåer.

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
