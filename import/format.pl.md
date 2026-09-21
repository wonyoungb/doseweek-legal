# Wersja robocza odczytu zapisów DoseWeek — wersja 1

Ten przewodnik służy do ekranu „Importuj wpisy z innej aplikacji” w DoseWeek 1.0.5 lub nowszym na iPhonie i iPadzie oraz w aplikacji DoseWeek na Androida, gdy ten ekran pojawi się w zainstalowanej wersji. Jeśli go nie widzisz, najpierw zaktualizuj DoseWeek. Zachowaj oryginalne wpisy do końca importu.

Ten format zachowuje dowody do sprawdzenia na ekranie importu DoseWeek. Nie jest zaszyfrowaną kopią zapasową, decyzją kliniczną ani gwarancją formatu innego dostawcy.

Limity aplikacji: jeden import mieści do 10 000 wierszy, a wejściowy JSON do 10 MiB. Niedokończony szkic do sprawdzenia może mieć do 4 MiB na iPhonie i iPadzie oraz do 1 MiB (1 048 576 bajtów) na Androidzie; większy import jest odrzucany, nigdy obcinany. Wierszy z objawami ani niesklasyfikowanych nie można zapisać; zachowaj ich tekst źródłowy i odznacz je. Na Androidzie wiersze odpowiadające wpisom usuniętym po wcześniejszym imporcie są traktowane jako już zaimportowane i nie są przywracane.

1. Na najwyższym poziomie format ma wartość doseweek.record_extraction_draft; version ma wartość 1; reviewed_by_user ma wartość false. records i unreadable_sections są tablicami. Odrzucaj nieznane pola zamiast po cichu je pomijać.

2. Każdy wiersz ma wszystkie pola szablonu i unikatowy row_id lokalny dla wersji roboczej. Identyfikatory źródłowe nigdy nie stają się automatycznie identyfikatorami zapisów DoseWeek. source_references zachowują etykietę dokumentu, numer strony liczony od 1, jeśli jest znany, etykietę wiersza oraz widoczny tekst; null oznacza wartość nieznaną.

3. Zachowaj surowe liczby jako ciągi znaków w dose_value_text i measurement_value_text. Zachowaj pisownię, znaki dziesiętne, jednostki oraz źródłowy tekst daty i godziny. Nieczytelne lub nieobsługiwane informacje pozostają w visible_text i needs_review; nigdy nie fabrykuj wartości.

4. date_iso ma format YYYY-MM-DD tylko wtedy, gdy pełna data jest jednoznaczna i prawidłowa. time_24h ma format HH:mm z opcjonalnymi sekundami i ułamkami sekund, jeśli są widoczne. time_zone i utc_offset wymagają wyraźnego potwierdzenia w źródle. Brakujące lub niejednoznaczne pola mają wartość null, a nie puste ciągi znaków lub odgadnięte daty i godziny.

5. Schemat sprawdza tylko strukturę. Import DoseWeek sprawdza też rzeczywiste daty kalendarzowe, jednostki, obsługiwane przypisania leków i pomiarów, strefy czasowe i duplikaty, a Ty nadal sprawdzasz każdy wiersz. Samo przejście walidacji schematu nigdy nie uprawnia do zapisu.

6. Aplikacja odrzuca zaznaczone wiersze z nierozstrzygniętymi wymaganymi polami i dodaje zaznaczenie atomowo, bez nadpisywania istniejących wpisów. Wiersz bez godziny wymaga rzeczywistej godziny wpisanej i potwierdzonej w aplikacji; nie używa się zastępczej godziny, takiej jak północ czy południe.

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
