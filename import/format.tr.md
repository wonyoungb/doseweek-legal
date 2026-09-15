# DoseWeek kayıt çıkarma taslağı — sürüm 1

Şimdi bir JSON taslağı hazırlayıp kontrol edebilirsiniz. Bu kılavuz, yüklü DoseWeek sürümünüzün taslağı kaydedebildiği anlamına gelmez. Uygulama bu biçimi açıkça destekleyene kadar özgün kayıtları saklayın.

Bu biçim, elle inceleme için kaynak kanıtlarını korur. Şifreli yedek, klinik karar, sağlayıcı biçimi garantisi veya mevcut uygulamanın bunu içe aktardığının kanıtı değildir.

Android içe aktarma: kayıtlı taslak sınırı, JSON için 10 MiB sınırından ayrı olarak 1 MiB (1.048.576 bayt) ve 10.000 satırdır. Belirti ve sınıflandırılmamış satırlar kaydedilemez; metinlerini koruyup seçimlerini kaldırın. Eşleşen silinmiş kayıtlar zaten içe aktarılmış sayılır ve geri yüklenmez. iOS aday sürümünde taslağı sürdürmek için ayrı bir 4 MiB sınırı vardır. Platformlarda veya yüklü uygulamada aynı davranış ve kullanılabilirliği varsaymayın.

1. Üst düzeyde format değeri doseweek.record_extraction_draft, version değeri 1 ve reviewed_by_user değeri false olmalıdır. records ve unreadable_sections dizidir. Bilinmeyen alanları sessizce atmak yerine reddedin.

2. Her satır tüm şablon alanlarını ve taslağa özgü benzersiz bir row_id içerir. Kaynak kimlikleri hiçbir zaman otomatik olarak DoseWeek kayıt kimliklerine dönüşmez. source_references belge etiketini, biliniyorsa 1’den başlayan sayfa numarasını, satır etiketini ve görünen metni korur; null bilinmiyor demektir.

3. Ham sayıları dose_value_text ve measurement_value_text içinde metin dizeleri olarak koruyun. Yazımı, ondalık işaretlerini, birimleri ve kaynak tarih/saat metnini koruyun. Okunamayan veya desteklenmeyen bilgi visible_text ve needs_review içinde kalır; asla değer uydurmayın.

4. date_iso yalnızca tam tarih açık ve geçerliyse YYYY-MM-DD biçimindedir. time_24h HH:mm biçimindedir; kaynakta görünüyorsa saniye ve saniye kesirlerini de içerebilir. time_zone ve utc_offset için açık kaynak kanıtı gerekir. Eksik veya belirsiz alanlar null olmalıdır; boş metin veya tahmini tarih/saat olmamalıdır.

5. Şema yapıyı denetler; ilerideki içe aktarıcı ayrıca gerçek takvim tarihlerini, birimleri, desteklenen ilaç ve ölçüm eşlemelerini, kaynak kanıtlarını, saat dilimi belirsizliğini ve tekrarları denetlemelidir. Yalnızca şema doğrulamasını geçmek, kaydetmeye asla izin vermez.

6. Planlanan kaydetme akışı tüm seçili satırları inceler, çözümlenmemiş zorunlu alanları reddeder ve mevcut kayıtların üzerine otomatik yazmadan seçimin tamamını tek işlemde ekler ya da hiçbirini eklemez. Yalnızca tarih içeren olayların anlamı, kaydetmeden önce açıkça desteklenmelidir; gece yarısı veya öğlen yer tutucusu kullanılamaz.

7. Taslakları ve kaynak dosyaları gizli tutun. Bu statik kılavuzda yükleme formu yoktur. Harici bir yapay zekâ seçmek, seçili dosyaları o hizmetin kendi koşulları kapsamında hizmete gönderir. Aynı alanları elle veya cihaz üzerinde metin tanımayla hazırlayabilirsiniz. Dosyayı elle oluşturuyorsanız yalnızca yapay zekâ yanıtının JSON içeriğini UTF-8 kodlamasıyla, adı .json ile biten bir dosyaya kaydedin. Bir taslak en fazla 10.000 kayıt içerebilir. Kodu çözülmüş her JSON dizesi en fazla 16 KiB (16.384 UTF-8 bayt) olabilir. Bu bayt sınırını uygulama denetler; JSON Schema içindeki maxLength, UTF-8 baytlarını değil Unicode kod noktalarını sayar. JSON dosyası en fazla 10 MiB olabilir; iç içe geçme derinliği en fazla 32 düzeydir.

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
