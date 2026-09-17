# DoseWeek kayıt çıkarma taslağı — sürüm 1

Bu kılavuz, iPhone ve iPad için DoseWeek 1.0.5 veya sonrasındaki “Başka bir uygulamadan kayıt aktar” ekranıyla ve bu ekran yüklü sürümünüzde göründüğünde Android için DoseWeek uygulamasıyla kullanılır. Ekranı görmüyorsanız önce DoseWeek'i güncelleyin. Aktarma bitene kadar orijinal kayıtları saklayın.

Bu biçim, DoseWeek'in aktarma ekranındaki inceleme için kanıtları korur. Şifreli bir yedek, klinik bir karar veya bir sağlayıcının biçimi için güvence değildir.

Uygulama sınırları: bir aktarma en fazla 10.000 satır, giriş JSON'u en fazla 10 MiB olabilir. Tamamlanmamış inceleme taslağı iPhone ve iPad'de en fazla 4 MiB, Android'de en fazla 1 MiB (1.048.576 bayt) olabilir; daha büyük bir aktarma reddedilir, asla kırpılmaz. Belirti satırları ve sınıflandırılmamış satırlar kaydedilemez; kaynak metinlerini koruyup seçimlerini kaldırın. Android'de, önceki bir aktarmadan sonra sildiğiniz kayıtlarla eşleşen satırlar zaten aktarılmış sayılır ve geri getirilmez.

1. Üst düzeyde format değeri doseweek.record_extraction_draft, version değeri 1 ve reviewed_by_user değeri false olmalıdır. records ve unreadable_sections dizidir. Bilinmeyen alanları sessizce atmak yerine reddedin.

2. Her satır tüm şablon alanlarını ve taslağa özgü benzersiz bir row_id içerir. Kaynak kimlikleri hiçbir zaman otomatik olarak DoseWeek kayıt kimliklerine dönüşmez. source_references belge etiketini, biliniyorsa 1’den başlayan sayfa numarasını, satır etiketini ve görünen metni korur; null bilinmiyor demektir.

3. Ham sayıları dose_value_text ve measurement_value_text içinde metin dizeleri olarak koruyun. Yazımı, ondalık işaretlerini, birimleri ve kaynak tarih/saat metnini koruyun. Okunamayan veya desteklenmeyen bilgi visible_text ve needs_review içinde kalır; asla değer uydurmayın.

4. date_iso yalnızca tam tarih açık ve geçerliyse YYYY-MM-DD biçimindedir. time_24h HH:mm biçimindedir; kaynakta görünüyorsa saniye ve saniye kesirlerini de içerebilir. time_zone ve utc_offset için açık kaynak kanıtı gerekir. Eksik veya belirsiz alanlar null olmalıdır; boş metin veya tahmini tarih/saat olmamalıdır.

5. Şema yalnızca yapıyı denetler. DoseWeek'in aktarması ayrıca gerçek takvim tarihlerini, birimleri, desteklenen ilaç ve ölçüm eşlemelerini, saat dilimlerini ve yinelenenleri denetler; her satırı yine siz incelersiniz. Şemayı geçmek tek başına asla kaydetmeye izin vermez.

6. Uygulama, zorunlu alanları çözülmemiş seçili satırları reddeder ve seçimi mevcut kayıtların üzerine yazmadan tek ve bölünmez bir işlemle ekler. Saati olmayan bir satır için gerçek saatin uygulamada girilip onaylanması gerekir; gece yarısı veya öğlen gibi yer tutucu bir saat kullanılmaz.

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
