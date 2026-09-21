# DoseWeek記録抽出の下書き — バージョン1

このガイドは、iPhone・iPad用DoseWeek 1.0.5以降の「ほかのアプリから記録を取り込む」と、インストール済みのバージョンにこの画面が表示されたAndroid用DoseWeekで使います。画面が見つからない場合は、先にDoseWeekをアップデートしてください。取り込みが終わるまで元の記録は残しておいてください。

この形式は、DoseWeekの取り込み画面で確認できるよう根拠を保持します。暗号化バックアップ、臨床判断、特定アプリの形式の保証ではありません。

アプリの上限: 1回の取り込みは最大10,000行、入力JSONは最大10 MiBです。終わっていない確認用下書きはiPhone・iPadで最大4 MiB、Androidで最大1 MiB（1,048,576バイト）で、それより大きい取り込みは切り詰めずに拒否します。症状と未分類の行は保存できないため、元の文字を残したまま選択を外してください。Androidでは、以前に取り込んだ後で削除した記録と一致する行は取り込み済みとして扱われ、復元されません。

1. 最上位のformatはdoseweek.record_extraction_draft、versionは1、reviewed_by_userはfalseです。recordsとunreadable_sectionsは配列です。未知のフィールドは黙って破棄せず拒否します。

2. 各行にはひな形の全フィールドと、下書き内で一意のrow_idがあります。原本の識別子が自動でDoseWeekの記録IDになることはありません。source_referencesは文書名、分かる場合は1から始まるページ番号、行名、見える原文を保ちます。nullは不明を意味します。

3. dose_value_textとmeasurement_value_textの数値原文は文字列で保ってください。つづり、小数点の表記、単位、日付・時刻の原文を維持してください。判読不能・未対応の情報はvisible_textとneeds_reviewに残し、値を作らないでください。

4. date_isoは、完全な日付が明確で有効な場合だけYYYY-MM-DDにします。time_24hはHH:mmで、原本に見える秒・小数秒を追加できます。time_zoneとutc_offsetには原本の明示的な根拠が必要です。欠落や曖昧なフィールドには、空文字や推定した日付・時刻ではなくnullを使います。

5. スキーマは構造だけを確認します。DoseWeekの取り込みでは、実在する日付、単位、対応する薬と測定項目の対応付け、タイムゾーン、重複も確認し、すべての行をあなたが確認します。スキーマに合格しただけで保存が認められることはありません。

6. アプリは必須項目が未解決の選択行を拒否し、選んだ記録を既存の記録を上書きせずに一括で追加します。時刻のない行は、アプリで実際の時刻を入力して確認する必要があり、午前0時や正午などの仮の時刻は使いません。

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
