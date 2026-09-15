# Rascunho de extração de registros do DoseWeek — versão 1

Você já pode preparar e conferir um rascunho JSON. Este guia não significa que a versão instalada do DoseWeek possa salvá-lo. Mantenha os registros originais até que o app ofereça suporte explícito a este formato.

Este formato preserva evidências para revisão manual. Não é um backup criptografado, uma decisão clínica, uma garantia de formato de fornecedor nem uma prova de que o app atual possa importá-lo.

Importação no Android: o rascunho salvo tem limite de 1 MiB (1.048.576 bytes) e 10.000 linhas, separado dos 10 MiB do JSON. Linhas de sintomas e não classificadas não podem ser salvas; preserve o texto e desmarque-as. Registros correspondentes excluídos continuam já importados e não são restaurados. A versão candidata do iOS tem um limite separado de 4 MiB para retomar rascunhos. Não presuma comportamento ou disponibilidade iguais nas plataformas ou no app instalado.

1. O campo format no nível superior é doseweek.record_extraction_draft; version é 1; reviewed_by_user é false. records e unreadable_sections são arrays. Rejeite campos desconhecidos em vez de descartá-los silenciosamente.

2. Cada linha contém todos os campos do modelo e um row_id exclusivo dentro do rascunho. Identificadores da fonte nunca se tornam automaticamente IDs de registros do DoseWeek. source_references preserva o rótulo do documento, o número da página a partir de 1 quando conhecido, o rótulo da linha e o texto visível; null significa desconhecido.

3. Mantenha os números originais como strings em dose_value_text e measurement_value_text. Preserve a escrita, os separadores decimais, as unidades e o texto de origem de data e horário. Informações ilegíveis ou não suportadas permanecem em visible_text e needs_review; nunca invente um valor.

4. date_iso usa YYYY-MM-DD somente quando a data completa é inequívoca e válida. time_24h usa HH:mm, com segundos e frações de segundo opcionais quando visíveis. time_zone e utc_offset exigem evidências explícitas na fonte. Campos ausentes ou ambíguos são null, não strings vazias nem datas ou horários adivinhados.

5. O esquema verifica a estrutura; um futuro importador também deve verificar datas reais do calendário, unidades, correspondências suportadas de medicamentos e métricas, evidências da fonte, ambiguidades de fuso horário e duplicatas. Passar apenas na validação do esquema nunca autoriza o salvamento.

6. O fluxo de salvamento previsto revisa todas as linhas selecionadas, rejeita campos obrigatórios não resolvidos e adiciona a seleção de forma atômica, sem sobrescrever automaticamente registros existentes. O significado de eventos que têm apenas uma data deve ser explicitamente suportado antes de salvar; não é permitido usar meia-noite ou meio-dia como preenchimento provisório.

7. Mantenha privados os rascunhos e os arquivos de origem. Este guia estático não tem formulário de envio. Ao escolher uma IA externa, você envia os arquivos selecionados a esse serviço conforme os termos dele. É possível preparar os mesmos campos manualmente ou com o reconhecimento de texto no próprio dispositivo. Se criar um arquivo manualmente, salve apenas o conteúdo JSON da resposta da IA em um arquivo UTF-8 terminado em .json. Um rascunho pode conter no máximo 10.000 registros. Cada string JSON decodificada é limitada a 16 KiB (16.384 bytes UTF-8). O aplicativo verifica esse limite em bytes; maxLength no JSON Schema conta pontos de código Unicode, não bytes UTF-8. O arquivo JSON é limitado a 10 MiB e a profundidade de aninhamento a 32 níveis.

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
