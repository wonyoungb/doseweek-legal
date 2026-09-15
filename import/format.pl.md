# Wersja robocza odczytu zapisów DoseWeek — wersja 1

Możesz już przygotować i sprawdzić wersję roboczą JSON. Ten poradnik nie oznacza, że zainstalowana wersja DoseWeek może ją zapisać. Zachowaj oryginalne zapisy, dopóki aplikacja nie będzie wyraźnie obsługiwać tego formatu.

Ten format zachowuje dane źródłowe do ręcznego sprawdzenia. Nie jest zaszyfrowaną kopią zapasową, decyzją kliniczną, gwarancją formatu dostawcy ani dowodem, że bieżąca aplikacja go importuje.

1. Na najwyższym poziomie format ma wartość doseweek.record_extraction_draft; version ma wartość 1; reviewed_by_user ma wartość false. records i unreadable_sections są tablicami. Odrzucaj nieznane pola zamiast po cichu je pomijać.

2. Każdy wiersz ma wszystkie pola szablonu i unikatowy row_id lokalny dla wersji roboczej. Identyfikatory źródłowe nigdy nie stają się automatycznie identyfikatorami zapisów DoseWeek. source_references zachowują etykietę dokumentu, numer strony liczony od 1, jeśli jest znany, etykietę wiersza oraz widoczny tekst; null oznacza wartość nieznaną.

3. Zachowaj surowe liczby jako ciągi znaków w dose_value_text i measurement_value_text. Zachowaj pisownię, znaki dziesiętne, jednostki oraz źródłowy tekst daty i godziny. Nieczytelne lub nieobsługiwane informacje pozostają w visible_text i needs_review; nigdy nie fabrykuj wartości.

4. date_iso ma format YYYY-MM-DD tylko wtedy, gdy pełna data jest jednoznaczna i prawidłowa. time_24h ma format HH:mm z opcjonalnymi sekundami i ułamkami sekund, jeśli są widoczne. time_zone i utc_offset wymagają wyraźnego potwierdzenia w źródle. Brakujące lub niejednoznaczne pola mają wartość null, a nie puste ciągi znaków lub odgadnięte daty i godziny.

5. Schemat sprawdza strukturę. Przyszły importer musi też sprawdzać rzeczywiste daty kalendarzowe, jednostki, mapowanie obsługiwanych leków i pomiarów, dowody źródłowe, niejednoznaczność strefy czasowej oraz duplikaty. Samo przejście walidacji schematu nigdy nie upoważnia do zapisu.

6. Planowany zapis obejmuje sprawdzenie wszystkich wybranych wierszy, odrzucenie nierozstrzygniętych pól wymaganych i dodanie całego wyboru albo żadnego wiersza, bez automatycznego nadpisywania istniejących zapisów. Znaczenie zdarzeń zawierających tylko datę musi być wyraźnie obsługiwane przed zapisem; zastępcza północ lub południe są niedozwolone.

7. Chroń prywatność wersji roboczych i plików źródłowych. Ten statyczny poradnik nie ma formularza przesyłania plików. Wybranie zewnętrznego AI oznacza wysłanie wybranych plików do tej usługi na jej warunkach. Te same pola można przygotować ręcznie lub przez rozpoznawanie tekstu na urządzeniu. Jeśli tworzysz plik ręcznie, zapisz wyłącznie treść JSON z odpowiedzi AI jako plik UTF-8 z rozszerzeniem .json. Wersja robocza może zawierać maksymalnie 10 000 rekordów. Każdy zdekodowany ciąg JSON ma limit 16 KiB (16 384 bajtów UTF-8). Ten limit bajtów sprawdza aplikacja; maxLength w JSON Schema liczy punkty kodowe Unicode, a nie bajty UTF-8. Plik JSON może mieć najwyżej 10 MiB, a głębokość zagnieżdżenia jest ograniczona do 32 poziomów.

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
