# Model kosztów i rentowności

## Jedna jednostka rachunku

Koszty operacyjne przechowuj netto, jeśli firma rozlicza VAT i ma poprawną stawkę; cenę klienta przechowuj także brutto. Każde pole ma `taxTreatment`. Nigdy nie odejmuj kosztu brutto od przychodu netto bez konwersji.

## Rachunek zamówienia

```text
przychód_netto
− koszt_towaru_netto
− transport_przychodzący_netto
− opakowanie_i_praca_netto
− prowizja_i_opłaty_Allegro_netto
− wkład_Smart_i_dopłaty_przewoźnika_netto
− promocje_i_Ads_netto
− rezerwa_zwrotów_i_szkód_netto
= marża_kontrybucyjna_netto
```

`marża % = marża_kontrybucyjna_netto / przychód_netto × 100`.

## Alokacja kosztów

| Koszt | Zalecana alokacja |
|---|---|
| dostawa wielu SKU | masa gabarytowa lub reguła pakowania; nie sama wartość |
| Smart | faktyczna opłata zamówienia, następnie paczka/pozycja |
| druga paczka | pozycja, która spowodowała przekroczenie profilu |
| Ads | raport atrybucji + dodatkowo eksperyment inkrementalny |
| promocja stała | okres aktywności i sprzedane sztuki; niesprzedana część to koszt kampanii |
| zwroty | rzeczywisty koszt oraz rezerwa według rodziny/rozmiaru |
| praca | standard minut × pełny koszt minuty, kalibrowany pomiarem |

## Cena minimalna

Cena minimalna nie jest prostym narzutem na zakup. Solver musi uwzględnić prowizję procentową zależną od ceny, próg Smart, VAT, promocję procentową i koszty stałe. Dla każdej planowanej ceny licz wynik iteracyjnie i zapisuj założenia.

Publikację blokuje:

- `complete=false`;
- dowolny koszt wymagany ma stan `UNKNOWN`;
- marża kwotowa lub procentowa poniżej zatwierdzonego progu rodziny;
- cena poniżej prawnie/regulaminowo wymaganej ceny referencyjnej w promocji;
- ujemny wynik po scenariuszu ciężkiej dopłaty lub drugiej paczki.

## Scenariusze

Każdy SKU liczymy co najmniej w wariantach: sprzedaż bez Smart, Smart przy każdym progu wartości zamówienia, jedna/druga paczka, Ads on/off, wyróżnienie, zwrot całkowity, zwrot częściowy i dopłata gabarytowa. Dla żywych ryb dochodzi utrata przesyłki/wstrzymanie pogodowe; dla odzieży wyższa rezerwa zwrotów.
