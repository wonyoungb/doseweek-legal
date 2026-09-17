# DoseWeek-concept voor gegevensextractie — versie 1

Deze handleiding hoort bij ‘Gegevens uit een andere app importeren’ in DoseWeek 1.0.5 of later op iPhone en iPad, en in de Android-app van DoseWeek zodra dat scherm in uw geïnstalleerde versie verschijnt. Ziet u het niet, werk DoseWeek dan eerst bij. Bewaar de oorspronkelijke registraties tot het importeren klaar is.

Dit formaat bewaart bewijs voor de controle in het importscherm van DoseWeek. Het is geen versleutelde back-up, geen klinische beslissing en geen garantie voor het formaat van een leverancier.

App-limieten: één import bevat maximaal 10.000 regels en de ingelezen JSON maximaal 10 MiB. Een onvoltooid controleconcept mag op iPhone en iPad maximaal 4 MiB en op Android maximaal 1 MiB (1.048.576 bytes) zijn; een grotere import wordt geweigerd, nooit ingekort. Regels met symptomen of zonder categorie kunnen niet worden bewaard; houd hun brontekst en deselecteer ze. Op Android gelden regels die overeenkomen met registraties die na een eerdere import zijn verwijderd als al geïmporteerd; ze worden niet hersteld.

1. Het format op het hoogste niveau is doseweek.record_extraction_draft; version is 1; reviewed_by_user is false. records en unreadable_sections zijn arrays. Wijs onbekende velden af in plaats van ze stilzwijgend weg te laten.

2. Elke rij heeft alle sjabloonvelden en een unieke row_id binnen het concept. Bron-ID’s worden nooit automatisch DoseWeek-registratie-ID’s. source_references bewaart het documentlabel, het paginanummer vanaf 1 indien bekend, het rijlabel en de zichtbare tekst; null betekent onbekend.

3. Bewaar onbewerkte getallen als strings in dose_value_text en measurement_value_text. Behoud schrijfwijze, decimaaltekens, eenheden en de brontekst voor datum en tijd. Onleesbare of niet-ondersteunde informatie blijft in visible_text en needs_review; verzin nooit een waarde.

4. date_iso gebruikt YYYY-MM-DD alleen als de volledige datum ondubbelzinnig en geldig is. time_24h gebruikt HH:mm, met optionele zichtbare seconden en fracties van seconden. time_zone en utc_offset vereisen expliciet bewijs uit de bron. Ontbrekende of dubbelzinnige velden zijn null, geen lege strings of geraden datums en tijden.

5. Het schema controleert alleen de structuur. De import van DoseWeek controleert ook echte kalenderdatums, eenheden, ondersteunde koppelingen van medicijnen en metingen, tijdzones en dubbele registraties, en u controleert nog steeds elke regel. Alleen slagen voor het schema geeft nooit toestemming om te bewaren.

6. De app weigert geselecteerde regels met onopgeloste verplichte velden en voegt de selectie atomair toe zonder bestaande registraties te overschrijven. Een regel zonder tijd heeft de werkelijke tijd nodig, ingevuld en bevestigd in de app; er wordt geen plaatsvervangende tijd zoals middernacht of het middaguur gebruikt.

7. Houd concepten en bronbestanden privé. Deze statische gids heeft geen uploadformulier. Als je een externe AI kiest, worden de geselecteerde bestanden onder de eigen voorwaarden van die dienst verstuurd. Je kunt dezelfde velden handmatig voorbereiden of tekstherkenning op je apparaat gebruiken. Als u handmatig een bestand maakt, sla dan alleen de JSON-inhoud van het AI-antwoord op als UTF-8-bestand met de extensie .json. Een concept mag maximaal 10.000 records bevatten. Elke gedecodeerde JSON-tekenreeks is beperkt tot 16 KiB (16.384 UTF-8-bytes). De app controleert deze bytelimiet; maxLength in JSON Schema telt Unicode-codepunten, geen UTF-8-bytes. Het JSON-bestand mag maximaal 10 MiB groot zijn; de nestingsdiepte is beperkt tot 32 niveaus.

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
