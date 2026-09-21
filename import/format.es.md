# Borrador de extracción de registros de DoseWeek — versión 1

Esta guía se usa con «Importar registros de otra app» en DoseWeek 1.0.5 o posterior para iPhone y iPad, y en la app de DoseWeek para Android cuando esa pantalla aparezca en su versión instalada. Si no la ve, actualice primero DoseWeek. Conserve los registros originales hasta terminar la importación.

Este formato conserva las pruebas para la revisión en la pantalla de importación de DoseWeek. No es una copia de seguridad cifrada, una decisión clínica ni una garantía sobre el formato de un proveedor.

Límites de la app: una importación admite hasta 10.000 filas y el JSON de entrada hasta 10 MiB. Un borrador de revisión sin terminar puede ocupar hasta 4 MiB en iPhone y iPad y hasta 1 MiB (1.048.576 bytes) en Android; una importación mayor se rechaza, nunca se recorta. Las filas de síntomas o sin clasificar no se pueden guardar; conserve su texto de origen y desmárquelas. En Android, las filas que coinciden con registros eliminados tras una importación anterior cuentan como ya importadas y no se restauran.

1. El format del nivel superior es doseweek.record_extraction_draft; version es 1; reviewed_by_user es false. records y unreadable_sections son arrays. Rechaza los campos desconocidos en lugar de descartarlos silenciosamente.

2. Cada fila contiene todos los campos de la plantilla y un row_id único dentro del borrador. Los identificadores de origen nunca se convierten automáticamente en identificadores de registros de DoseWeek. source_references conserva la etiqueta del documento, la página numerada desde 1 cuando se conozca, la etiqueta de la fila y el texto visible; null significa desconocido.

3. Conserva los números originales como cadenas en dose_value_text y measurement_value_text. Mantén la escritura, los separadores decimales, las unidades y el texto de origen de fecha y hora. La información ilegible o no admitida permanece en visible_text y needs_review; nunca inventes un valor.

4. date_iso usa YYYY-MM-DD únicamente cuando la fecha completa es inequívoca y válida. time_24h usa HH:mm, con segundos y fracciones de segundo opcionales si son visibles. time_zone y utc_offset requieren pruebas explícitas en la fuente. Los campos ausentes o ambiguos son null, no cadenas vacías ni fechas u horas adivinadas.

5. El esquema solo comprueba la estructura. La importación de DoseWeek también comprueba fechas reales del calendario, unidades, correspondencias admitidas de medicamentos y mediciones, zonas horarias y duplicados, y usted sigue revisando cada fila. Superar el esquema nunca autoriza por sí solo el guardado.

6. La app rechaza las filas seleccionadas con campos obligatorios sin resolver y añade la selección de forma atómica sin sobrescribir registros existentes. Una fila sin hora necesita la hora real introducida y confirmada en la app; no se usa ninguna hora ficticia como medianoche o mediodía.

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
