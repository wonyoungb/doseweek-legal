# Bozza di estrazione delle registrazioni DoseWeek — versione 1

Puoi già preparare e controllare una bozza JSON. Questa guida non significa che la versione di DoseWeek installata possa salvarla. Conserva i dati originali finché l’app non supporterà esplicitamente questo formato.

Questo formato conserva le prove per la verifica manuale. Non è un backup crittografato, una decisione clinica, una garanzia sul formato di un fornitore né la prova che l’app attuale possa importarlo.

Importazione Android: la bozza salvata è limitata a 1 MiB (1.048.576 byte) e 10.000 righe, separatamente dai 10 MiB del JSON. Le righe dei sintomi e non classificate non si possono salvare; conservate il testo e deselezionatele. Le registrazioni corrispondenti eliminate restano già importate e non vengono ripristinate. La versione candidata iOS ha un limite separato di 4 MiB per riprendere le bozze. Non presumete comportamento o disponibilità identici nelle due piattaforme o nell’app installata.

1. Il format di primo livello è doseweek.record_extraction_draft; version è 1; reviewed_by_user è false. records e unreadable_sections sono array. Rifiuta i campi sconosciuti invece di eliminarli silenziosamente.

2. Ogni riga contiene tutti i campi del modello e un row_id univoco all’interno della bozza. Gli identificatori della fonte non diventano mai automaticamente ID di registrazioni DoseWeek. source_references conserva l’etichetta del documento, il numero di pagina a partire da 1 quando è noto, l’etichetta della riga e il testo visibile; null significa sconosciuto.

3. Conserva i numeri originali come stringhe in dose_value_text e measurement_value_text. Mantieni grafia, separatori decimali, unità e testo originale di data e ora. Le informazioni illeggibili o non supportate restano in visible_text e needs_review; non inventare mai un valore.

4. date_iso usa YYYY-MM-DD solo quando la data completa è inequivocabile e valida. time_24h usa HH:mm, con secondi e frazioni di secondo facoltativi se visibili. time_zone e utc_offset richiedono prove esplicite nella fonte. I campi mancanti o ambigui sono null, non stringhe vuote né date o orari indovinati.

5. Lo schema verifica la struttura; un futuro importatore deve anche verificare le date effettive del calendario, le unità, le corrispondenze supportate per farmaci e metriche, le prove nella fonte, le ambiguità del fuso orario e i duplicati. Superare la sola convalida dello schema non autorizza mai il salvataggio.

6. Il flusso di salvataggio previsto verifica tutte le righe selezionate, rifiuta i campi obbligatori non risolti e aggiunge la selezione in modo atomico, senza sovrascrivere automaticamente le registrazioni esistenti. Il significato degli eventi con la sola data deve essere esplicitamente supportato prima del salvataggio; non sono ammessi segnaposto a mezzanotte o a mezzogiorno.

7. Mantieni privati le bozze e i file originali. Questa guida statica non contiene un modulo di caricamento. Scegliendo un’IA esterna, invii i file selezionati a quel servizio secondo le sue condizioni. Puoi preparare gli stessi campi manualmente o con il riconoscimento del testo sul dispositivo. Se crea un file manualmente, salvi solo il contenuto JSON della risposta dell’IA in un file UTF-8 con estensione .json. Una bozza può contenere al massimo 10.000 record. Ogni stringa JSON decodificata è limitata a 16 KiB (16.384 byte UTF-8). Questo limite in byte viene verificato dall’app; maxLength in JSON Schema conta i punti di codice Unicode, non i byte UTF-8. Il file JSON è limitato a 10 MiB e l’annidamento a 32 livelli.

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
