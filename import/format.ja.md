# DoseWeek記録抽出の下書き — バージョン1

現在できるのはJSONの下書き作成と原本との照合です。このガイドは、インストール済みのDoseWeekで保存できることを意味しません。アプリがこの形式への対応を明示するまで、元の記録を保管してください。

手動確認のための根拠を保つ形式です。暗号化されたバックアップ、医学的判断、提供元の形式への対応保証、現在のアプリが取り込めることの証拠ではありません。

Androidの取り込みでは、保存する確認用下書きの上限は1 MiB（1,048,576バイト）、10,000行で、入力JSONの10 MiB制限とは別です。症状と未分類の行は保存できません。原文を残し、選択を外してください。削除済み記録と一致する行も取り込み済みとなり、復元されません。iOS候補版の下書き再開用上限は別途4 MiBです。両OSの動作やインストール済みアプリでの対応を同一と想定しないでください。

1. 最上位のformatはdoseweek.record_extraction_draft、versionは1、reviewed_by_userはfalseです。recordsとunreadable_sectionsは配列です。未知のフィールドは黙って破棄せず拒否します。

2. 各行にはひな形の全フィールドと、下書き内で一意のrow_idがあります。原本の識別子が自動でDoseWeekの記録IDになることはありません。source_referencesは文書名、分かる場合は1から始まるページ番号、行名、見える原文を保ちます。nullは不明を意味します。

3. dose_value_textとmeasurement_value_textの数値原文は文字列で保ってください。つづり、小数点の表記、単位、日付・時刻の原文を維持してください。判読不能・未対応の情報はvisible_textとneeds_reviewに残し、値を作らないでください。

4. date_isoは、完全な日付が明確で有効な場合だけYYYY-MM-DDにします。time_24hはHH:mmで、原本に見える秒・小数秒を追加できます。time_zoneとutc_offsetには原本の明示的な根拠が必要です。欠落や曖昧なフィールドには、空文字や推定した日付・時刻ではなくnullを使います。

5. スキーマは構造を検査します。今後の取り込みでは、実際の暦日、単位、対応する薬剤・指標の割り当て、原本の根拠、タイムゾーンの曖昧さ、重複も検査する必要があります。スキーマ通過だけで保存を許可してはいけません。

6. 予定する保存の流れでは、選択した全行を確認し、必須項目が未解決なら拒否し、既存記録を自動上書きせず選択分を一括で追加します。日付だけの出来事の意味は保存前に明示的に対応する必要があり、午前0時や正午の仮の時刻を補ってはいけません。

7. 下書きと原本ファイルは非公開で保管してください。この静的ガイドにはアップロードフォームがありません。外部AIを選ぶと、そのサービスに選択したファイルが送られ、そのサービスの規約が適用されます。手作業や端末内の文字認識でも同じフィールドを準備できます。 ファイルを手作業で作る場合は、AIの応答のJSON本文だけをUTF-8の.jsonファイルとして保存してください。下書きの記録数は最大10,000件です。デコード後の各JSON文字列はUTF-8で16 KiB（16,384バイト）までです。このバイト上限はアプリが検査します。JSON SchemaのmaxLengthはUTF-8のバイト数ではなくUnicodeコードポイント数を数えます。 JSONファイルの上限は10 MiBで、入れ子の深さは32階層までです。

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
