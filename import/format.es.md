# Borrador de extracción de registros de DoseWeek — versión 1

Ya puedes preparar y comprobar un borrador JSON. Esta guía no significa que la versión de DoseWeek que tienes instalada pueda guardarlo. Conserva los registros originales hasta que la app admita expresamente este formato.

Este formato conserva pruebas para una revisión manual. No es una copia de seguridad cifrada, una decisión clínica, una garantía de formato de un proveedor ni una prueba de que la app actual pueda importarlo.

1. El format del nivel superior es doseweek.record_extraction_draft; version es 1; reviewed_by_user es false. records y unreadable_sections son arrays. Rechaza los campos desconocidos en lugar de descartarlos silenciosamente.

2. Cada fila contiene todos los campos de la plantilla y un row_id único dentro del borrador. Los identificadores de origen nunca se convierten automáticamente en identificadores de registros de DoseWeek. source_references conserva la etiqueta del documento, la página numerada desde 1 cuando se conozca, la etiqueta de la fila y el texto visible; null significa desconocido.

3. Conserva los números originales como cadenas en dose_value_text y measurement_value_text. Mantén la escritura, los separadores decimales, las unidades y el texto de origen de fecha y hora. La información ilegible o no admitida permanece en visible_text y needs_review; nunca inventes un valor.

4. date_iso usa YYYY-MM-DD únicamente cuando la fecha completa es inequívoca y válida. time_24h usa HH:mm, con segundos y fracciones de segundo opcionales si son visibles. time_zone y utc_offset requieren pruebas explícitas en la fuente. Los campos ausentes o ambiguos son null, no cadenas vacías ni fechas u horas adivinadas.

5. El esquema comprueba la estructura; un futuro importador también debe comprobar las fechas reales del calendario, las unidades, las correspondencias admitidas de medicamentos y métricas, las pruebas de origen, la ambigüedad de zona horaria y los duplicados. Superar únicamente la validación del esquema nunca autoriza a guardar.

6. El flujo de guardado previsto revisa todas las filas seleccionadas, rechaza los campos obligatorios sin resolver y añade la selección de forma atómica, sin sobrescribir automáticamente los registros existentes. El significado de los acontecimientos que solo tienen fecha debe admitirse expresamente antes de guardarlos; no se permite usar medianoche o mediodía como marcador.

7. Mantén privados los borradores y los archivos de origen. Esta guía estática no tiene ningún formulario de subida. Al elegir una IA externa, los archivos seleccionados se envían a ese servicio conforme a sus propias condiciones. Puedes preparar los mismos campos manualmente o con el reconocimiento de texto de tu dispositivo. Si crea un archivo manualmente, guarde solo el contenido JSON de la respuesta de la IA como archivo UTF-8 terminado en .json. Un borrador puede contener como máximo 10.000 registros. Cada cadena JSON decodificada está limitada a 16 KiB (16.384 bytes UTF-8). La aplicación comprueba este límite en bytes; maxLength de JSON Schema cuenta puntos de código Unicode, no bytes UTF-8. El archivo JSON está limitado a 10 MiB y el anidamiento a 32 niveles.

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
