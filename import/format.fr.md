# Brouillon d’extraction de données DoseWeek — version 1

Vous pouvez dès maintenant préparer et vérifier un brouillon JSON. Ce guide ne signifie pas que votre version installée de DoseWeek peut l’enregistrer. Conservez les données originales jusqu’à ce que l’app prenne explicitement en charge ce format.

Ce format conserve les éléments justificatifs pour une vérification manuelle. Ce n’est ni une sauvegarde chiffrée, ni une décision clinique, ni une garantie de format fournisseur, ni la preuve que l’app actuelle peut l’importer.

1. Le format de premier niveau est doseweek.record_extraction_draft ; version vaut 1 ; reviewed_by_user vaut false. records et unreadable_sections sont des tableaux. Rejette les champs inconnus au lieu de les supprimer silencieusement.

2. Chaque ligne contient tous les champs du modèle et un row_id unique dans le brouillon. Les identifiants source ne deviennent jamais automatiquement des identifiants de données DoseWeek. source_references conserve le libellé du document, le numéro de page commençant à 1 lorsqu’il est connu, le libellé de la ligne et le texte visible ; null signifie inconnu.

3. Conserve les nombres bruts sous forme de chaînes dans dose_value_text et measurement_value_text. Préserve l’écriture, les séparateurs décimaux, les unités et le texte source de date et d’heure. Les informations illisibles ou non prises en charge restent dans visible_text et needs_review ; ne fabrique jamais de valeur.

4. date_iso utilise YYYY-MM-DD uniquement si la date complète est valide et sans ambiguïté. time_24h utilise HH:mm, avec les secondes et fractions de seconde facultatives lorsqu’elles sont visibles. time_zone et utc_offset exigent des éléments explicites dans la source. Les champs manquants ou ambigus valent null, pas des chaînes vides ni des dates ou heures devinées.

5. Le schéma vérifie la structure ; un futur importateur devra aussi vérifier les dates calendaires réelles, les unités, les correspondances prises en charge pour les médicaments et les mesures, les éléments source, les ambiguïtés de fuseau horaire et les doublons. La seule validation du schéma n’autorise jamais l’enregistrement.

6. Le parcours d’enregistrement prévu vérifie toutes les lignes sélectionnées, rejette les champs obligatoires non résolus et ajoute la sélection de façon atomique sans écraser automatiquement les données existantes. Le sens des événements comportant seulement une date doit être explicitement pris en charge avant leur enregistrement ; aucun remplacement par minuit ou midi n’est autorisé.

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
