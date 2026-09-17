# Brouillon d’extraction de données DoseWeek — version 1

Ce guide s’utilise avec « Importer des données d’une autre app » dans DoseWeek 1.0.5 ou ultérieur sur iPhone et iPad, et dans l’app Android DoseWeek dès que cet écran apparaît dans votre version installée. Si vous ne le voyez pas, mettez d’abord DoseWeek à jour. Conservez vos données d’origine jusqu’à la fin de l’import.

Ce format conserve les éléments de preuve pour la vérification dans l’écran d’import de DoseWeek. Ce n’est ni une sauvegarde chiffrée, ni une décision clinique, ni une garantie sur le format d’un éditeur.

Limites de l’app : un import contient au plus 10 000 lignes et le JSON importé au plus 10 Mio. Un brouillon de vérification non terminé peut atteindre 4 Mio sur iPhone et iPad et 1 Mio (1 048 576 octets) sur Android ; un import plus grand est refusé, jamais tronqué. Les lignes de symptôme ou non classées ne peuvent pas être enregistrées ; gardez leur texte source et désélectionnez-les. Sur Android, les lignes correspondant à des données supprimées après un import précédent comptent comme déjà importées et ne sont pas restaurées.

1. Le format de premier niveau est doseweek.record_extraction_draft ; version vaut 1 ; reviewed_by_user vaut false. records et unreadable_sections sont des tableaux. Rejette les champs inconnus au lieu de les supprimer silencieusement.

2. Chaque ligne contient tous les champs du modèle et un row_id unique dans le brouillon. Les identifiants source ne deviennent jamais automatiquement des identifiants de données DoseWeek. source_references conserve le libellé du document, le numéro de page commençant à 1 lorsqu’il est connu, le libellé de la ligne et le texte visible ; null signifie inconnu.

3. Conserve les nombres bruts sous forme de chaînes dans dose_value_text et measurement_value_text. Préserve l’écriture, les séparateurs décimaux, les unités et le texte source de date et d’heure. Les informations illisibles ou non prises en charge restent dans visible_text et needs_review ; ne fabrique jamais de valeur.

4. date_iso utilise YYYY-MM-DD uniquement si la date complète est valide et sans ambiguïté. time_24h utilise HH:mm, avec les secondes et fractions de seconde facultatives lorsqu’elles sont visibles. time_zone et utc_offset exigent des éléments explicites dans la source. Les champs manquants ou ambigus valent null, pas des chaînes vides ni des dates ou heures devinées.

5. Le schéma ne vérifie que la structure. L’import de DoseWeek vérifie aussi les dates réelles du calendrier, les unités, les correspondances de médicaments et de mesures prises en charge, les fuseaux horaires et les doublons, et vous vérifiez toujours chaque ligne. Réussir le schéma n’autorise jamais à lui seul l’enregistrement.

6. L’app refuse les lignes sélectionnées dont des champs obligatoires restent non résolus et ajoute la sélection de façon atomique, sans écraser les données existantes. Une ligne sans heure exige l’heure réelle saisie et confirmée dans l’app ; aucune heure fictive comme minuit ou midi n’est utilisée.

7. Gardez les brouillons et les fichiers source privés. Ce guide statique ne comporte aucun formulaire d’envoi. Choisir une IA externe transmet les fichiers sélectionnés à ce service selon ses propres conditions. Vous pouvez préparer les mêmes champs manuellement ou avec la reconnaissance de texte sur votre appareil. Si vous créez un fichier manuellement, enregistrez uniquement le contenu JSON de la réponse de l’IA dans un fichier UTF-8 se terminant par .json. Un brouillon peut contenir au maximum 10 000 enregistrements. Chaque chaîne JSON décodée est limitée à 16 KiB (16 384 octets UTF-8). Cette limite en octets est vérifiée par l’application ; maxLength dans JSON Schema compte les points de code Unicode, pas les octets UTF-8. La taille du fichier JSON est limitée à 10 MiB et l’imbrication à 32 niveaux.

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
