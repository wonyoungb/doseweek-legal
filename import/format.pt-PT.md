# Rascunho de extração de registos do DoseWeek — versão 1

Já pode preparar e verificar um rascunho JSON. Este guia não significa que a versão instalada do DoseWeek o possa guardar. Conserve os registos originais até que a aplicação suporte explicitamente este formato.

Este formato preserva elementos de prova para revisão manual. Não é uma cópia de segurança encriptada, uma decisão clínica, uma garantia de formato de fornecedor nem uma prova de que a aplicação atual o possa importar.

Importação no Android: o rascunho guardado tem um limite de 1 MiB (1.048.576 bytes) e 10.000 linhas, separado dos 10 MiB do JSON. As linhas de sintomas e não classificadas não podem ser guardadas; preserve o texto e desmarque-as. Registos correspondentes eliminados continuam já importados e não são restaurados. A versão candidata do iOS tem um limite separado de 4 MiB para retomar rascunhos. Não pressuponha comportamento ou disponibilidade iguais nas plataformas ou na app instalada.

1. O campo format de nível superior é doseweek.record_extraction_draft; version é 1; reviewed_by_user é false. records e unreadable_sections são arrays. Rejeite campos desconhecidos em vez de os eliminar silenciosamente.

2. Cada linha contém todos os campos do modelo e um row_id único no rascunho. Os identificadores da fonte nunca se tornam automaticamente IDs de registos do DoseWeek. source_references preserva o rótulo do documento, o número de página a partir de 1 quando conhecido, o rótulo da linha e o texto visível; null significa desconhecido.

3. Mantenha os números originais como strings em dose_value_text e measurement_value_text. Preserve a grafia, os separadores decimais, as unidades e o texto de origem de data e hora. As informações ilegíveis ou não suportadas permanecem em visible_text e needs_review; nunca invente um valor.

4. date_iso usa YYYY-MM-DD apenas quando a data completa é inequívoca e válida. time_24h usa HH:mm, com segundos e frações de segundo opcionais quando visíveis. time_zone e utc_offset exigem prova explícita na fonte. Os campos em falta ou ambíguos são null, não strings vazias nem datas ou horas adivinhadas.

5. O esquema verifica a estrutura; um futuro importador também deve verificar as datas reais do calendário, as unidades, as correspondências suportadas de medicamentos e métricas, os elementos de prova da fonte, as ambiguidades de fuso horário e os duplicados. Passar apenas na validação do esquema nunca autoriza a gravação.

6. O processo de gravação previsto revê todas as linhas selecionadas, rejeita campos obrigatórios não resolvidos e adiciona a seleção de forma atómica, sem substituir automaticamente registos existentes. O significado de eventos que contêm apenas uma data deve ser explicitamente suportado antes de guardar; não é permitido usar meia-noite ou meio-dia como preenchimento provisório.

7. Mantenha privados os rascunhos e os ficheiros de origem. Este guia estático não tem formulário de carregamento. Ao escolher uma IA externa, envia os ficheiros selecionados para esse serviço segundo os respetivos termos. Pode preparar os mesmos campos manualmente ou com o reconhecimento de texto no próprio dispositivo. Se criar um ficheiro manualmente, guarde apenas o conteúdo JSON da resposta da IA num ficheiro UTF-8 terminado em .json. Um rascunho pode conter, no máximo, 10 000 registos. Cada cadeia JSON descodificada está limitada a 16 KiB (16 384 bytes UTF-8). A aplicação verifica este limite em bytes; maxLength em JSON Schema conta pontos de código Unicode, não bytes UTF-8. O ficheiro JSON está limitado a 10 MiB e a profundidade de aninhamento a 32 níveis.

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
