# Utkast för avskrift av DoseWeek-poster — version 1

Den här guiden hör till ”Importera poster från en annan app” i DoseWeek 1.0.5 eller senare på iPhone och iPad, och i DoseWeeks Android-app när den skärmen finns i din installerade version. Om du inte ser den, uppdatera DoseWeek först. Behåll de ursprungliga posterna tills importen är klar.

Formatet bevarar underlag för granskningen på DoseWeeks importskärm. Det är ingen krypterad säkerhetskopia, inget kliniskt beslut och ingen garanti för en leverantörs format.

Appens gränser: en import rymmer högst 10 000 rader och indata-JSON högst 10 MiB. Ett ofullständigt granskningsutkast får vara högst 4 MiB på iPhone och iPad och högst 1 MiB (1 048 576 byte) på Android; en större import avvisas och kortas aldrig. Symtomrader och oklassificerade rader kan inte sparas; behåll källtexten och avmarkera dem. På Android räknas rader som motsvarar poster du raderat efter en tidigare import som redan importerade och återställs inte.

1. På toppnivån är format doseweek.record_extraction_draft, version är 1 och reviewed_by_user är false. records och unreadable_sections är arrayer. Avvisa okända fält i stället för att kasta bort dem utan att ange det.

2. Varje rad har alla mallfält och ett unikt row_id som är lokalt för utkastet. Källidentifierare blir aldrig automatiskt post-ID:n i DoseWeek. source_references bevarar dokumentets etikett, sidnummer räknat från 1 när det är känt, radetikett och synlig text; null betyder okänt.

3. Behåll råa tal som strängar i dose_value_text och measurement_value_text. Bevara stavning, decimaltecken, enheter och källans datum- och tidstext. Oläslig information eller information som inte stöds stannar i visible_text och needs_review; hitta aldrig på ett värde.

4. date_iso är YYYY-MM-DD endast när det fullständiga datumet är entydigt och giltigt. time_24h är HH:mm, med sekunder och bråkdelar av sekunder om de är synliga. time_zone och utc_offset kräver uttryckligt belägg i källan. Saknade eller tvetydiga fält är null, inte tomma strängar eller gissade datum och klockslag.

5. Schemat kontrollerar bara strukturen. DoseWeeks import kontrollerar också verkliga kalenderdatum, enheter, stödda kopplingar för läkemedel och mätvärden, tidszoner och dubbletter, och du granskar fortfarande varje rad. Att klara schemat ger aldrig ensamt rätt att spara.

6. Appen avvisar markerade rader med olösta obligatoriska fält och lägger till urvalet atomärt utan att skriva över befintliga poster. En rad utan tid behöver den faktiska tiden angiven och bekräftad i appen; ingen platshållartid som midnatt eller klockan tolv används.

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
