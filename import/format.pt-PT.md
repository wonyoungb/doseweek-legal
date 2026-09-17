# Rascunho de extração de registos do DoseWeek — versão 1

Este guia usa-se com «Importar registos de outra aplicação» no DoseWeek 1.0.5 ou posterior para iPhone e iPad, e na aplicação DoseWeek para Android quando esse ecrã aparecer na versão instalada. Se não o vir, atualize primeiro o DoseWeek. Guarde os registos originais até a importação terminar.

Este formato preserva as provas para a revisão no ecrã de importação do DoseWeek. Não é uma cópia de segurança encriptada, uma decisão clínica nem uma garantia sobre o formato de um fornecedor.

Limites da aplicação: uma importação contém no máximo 10 000 linhas e o JSON de entrada no máximo 10 MiB. Um rascunho de revisão por terminar pode ter até 4 MiB no iPhone e iPad e até 1 MiB (1 048 576 bytes) no Android; uma importação maior é recusada, nunca cortada. As linhas de sintomas ou não classificadas não podem ser guardadas; mantenha o texto de origem e desmarque-as. No Android, as linhas que correspondem a registos eliminados após uma importação anterior contam como já importadas e não são restauradas.

1. O campo format de nível superior é doseweek.record_extraction_draft; version é 1; reviewed_by_user é false. records e unreadable_sections são arrays. Rejeite campos desconhecidos em vez de os eliminar silenciosamente.

2. Cada linha contém todos os campos do modelo e um row_id único no rascunho. Os identificadores da fonte nunca se tornam automaticamente IDs de registos do DoseWeek. source_references preserva o rótulo do documento, o número de página a partir de 1 quando conhecido, o rótulo da linha e o texto visível; null significa desconhecido.

3. Mantenha os números originais como strings em dose_value_text e measurement_value_text. Preserve a grafia, os separadores decimais, as unidades e o texto de origem de data e hora. As informações ilegíveis ou não suportadas permanecem em visible_text e needs_review; nunca invente um valor.

4. date_iso usa YYYY-MM-DD apenas quando a data completa é inequívoca e válida. time_24h usa HH:mm, com segundos e frações de segundo opcionais quando visíveis. time_zone e utc_offset exigem prova explícita na fonte. Os campos em falta ou ambíguos são null, não strings vazias nem datas ou horas adivinhadas.

5. O esquema só verifica a estrutura. A importação do DoseWeek também verifica datas reais do calendário, unidades, correspondências suportadas de medicamentos e medições, fusos horários e duplicados, e continua a rever cada linha. Passar no esquema, por si só, nunca autoriza a gravação.

6. A aplicação recusa linhas selecionadas com campos obrigatórios por resolver e adiciona a seleção de forma atómica, sem substituir registos existentes. Uma linha sem hora precisa da hora real introduzida e confirmada na aplicação; não é usada nenhuma hora fictícia como meia-noite ou meio-dia.

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
