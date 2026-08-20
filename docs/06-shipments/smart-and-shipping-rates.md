# Allegro Smart i cenniki dostaw

Weryfikacja: **2026-08-20**, rynek `allegro.pl`, wysyłka z Polski. Kwoty są czasowe; integracja ma przechowywać wersję cennika i datę obowiązywania.

Źródła główne: [warunki Smart dla konta firmowego](https://help.allegro.com/pl/sell/a/allegro-smart-na-allegro-pl-informacje-dla-sprzedajacych-z-kontem-firmowym-9g0rWRXKxHG), [Allegro Delivery](https://help.allegro.com/pl/sell/a/program-dostaw-allegro-delivery-informacje-dla-sprzedajacych-9gzevkzEGs1), [limity w Wysyłam z Allegro](https://help.allegro.com/pl/sell/c/narzedzie-nadawcze-wysylam-z-allegro) i [InPost](https://help.allegro.com/pl/sell/a/allegro-paczkomaty-inpost-informacje-dla-sprzedajacych-x5KaWzABkI5).

## Minimalne wymagania Smart dla konta firmowego

1. Jakość sprzedaży wyższa niż `Neutralny` albo co najmniej `Neutralny` na wszystkich kontach.
2. Terminowo opłacone faktury i zgodność z regulaminem.
3. Pełen dostępny pakiet Allegro Delivery pasujący do miejsca nadania i rozmiaru produktu.
4. Ceny metod spoza Allegro Delivery mieszczące się w dopuszczonych przedziałach.
5. Warunki zwrotów, a dla dostawy Polska→Polska adres zwrotu w Polsce.
6. Pełny, niezmieniony zamaskowany e-mail zamówienia przekazany przewoźnikowi. Błąd może spowodować pełną opłatę zamiast rozliczenia Smart.

Ogłoszenia nie mogą mieć oznaczenia Smart. To wyklucza zwykłe użycie Smart dla ofert żywych ryb prowadzonych w trybie ogłoszeniowym.

## Których przewoźników używać

| Rola | Metody | Zastosowanie RaFish |
|---|---|---|
| podstawowy pełny pakiet | Allegro Delivery: One, ORLEN, DHL, DPD — metody dostępne dla lokalizacji i gabarytu | większość suchych, standardowych SKU |
| szeroka sieć automatów | Allegro Paczkomaty InPost | małe i średnie paczki do 25 kg i 41 × 38 × 64 cm |
| ciężkie paczki | Allegro Kurier DPD, ewentualnie DHL/One zgodnie z bieżącym limitem | kreda/wapno 20–31,5 kg po zweryfikowaniu masy |
| uzupełniający | Pocztex/punkty/automat | gdy profil i lokalizacja spełniają limit; Pocztex w WzA ma obecnie 20 kg |
| długie | DPD kurier lub zatwierdzona usługa specjalna | wędki i elementy przekraczające automat; dokładny limit metody sprawdzać runtime |
| paletowe | osobny kontrakt/usługa paletowa, nie zwykła paczka Smart | zamówienia ponad limit jednej paczki i duże ilości worków |
| żywe ryby | wyłącznie przewoźnik i umowa dopuszczające żywe zwierzęta | poza zwykłym automatem Smart; ręczna kwalifikacja pogody i dobrostanu |

`Pełen pakiet` nie oznacza włączenia metody, do której produkt fizycznie nie pasuje. Dla produktu zapakowanego z bokiem ponad 120 cm Smart może działać z co najmniej jedną metodą kurierską bez punktów/automatów. Masa sama w sobie nie uruchamia tego wyjątku.

## Próg kupującego i wkład sprzedawcy

Dla Smart aktywowanego/odnowionego od 2026-03-02 próg bezpłatnej dostawy kupującego wynosi **49,90 zł** zarówno do punktu/automatu, jak i kurierem. Starszy okres abonamentowy może do odnowienia zachować progi 45/65 zł. Rozliczenie sprzedawcy nadal ma pięć progów wartości zamówienia.

### Automaty i punkty — opłata sprzedawcy brutto

| Operator | 30–44,99 | 45–64,99 | 65–99,99 | 100–149,99 | od 150 | maks. cena w cenniku |
|---|---:|---:|---:|---:|---:|---:|
| Allegro Delivery: One/ORLEN/DHL/DPD | 0,99 | 1,99 | 3,69 | 6,19 | 7,99 | 10,49 |
| InPost/Poczta Polska | 1,59 | 3,19 | 5,19 | 7,89 | 9,99 | 10,95 |

### Kurier — opłata sprzedawcy brutto

| Operator | 30–44,99 | 45–64,99 | 65–99,99 | 100–149,99 | od 150 | maks. cena w cenniku |
|---|---:|---:|---:|---:|---:|---:|
| Allegro Delivery: One/DPD/DHL | 1,79 | 3,69 | 5,59 | 8,99 | 11,29 | 14,99 |
| Pocztex | 1,99 | 3,99 | 6,09 | 9,49 | 11,89 | 14,99 |

To nie jest pełny koszt logistyczny: dochodzą opakowanie, praca, dopłata gabarytowa/wagowa, druga paczka, pobranie i szkody. Bieżąca dopłata Smart za pobranie wynosi **4,99 zł**; kupujący płaci tę kwotę oprócz produktu. Aktualną wartość mimo to pobieramy z cennika w dniu kalkulacji.

Za pierwszą paczkę obowiązuje próg wartości zamówienia. Za kolejną paczkę w zamówieniu od 150 zł Allegro nalicza obecnie stawkę z progu 100–149,99 zł; poniżej 150 zł kolejne paczki kosztują tyle co pierwsza. Dlatego `maxQuantityPerPackage` i rzeczywisty split paczek bezpośrednio wpływają na marżę.

Allegro zwraca podstawową opłatę Smart w określonych przypadkach zwrotu/nieodebrania, ale nie usługi dodatkowe. Warunkiem rozliczenia jest m.in. płatność przez Allegro, prawidłowy zamaskowany e-mail i zakończona płatność. Nie zakładaj refundacji kosztu, dopóki rabat nie jest widoczny w rozliczeniach.

## Rekomendowany cennik startowy RaFish

To stawki dla kupującego, nie prognoza kosztu firmy. Przed wdrożeniem trzeba potwierdzić cenniki w ustawieniach konta.

| Profil | Cena do punktu/automatu | Cena kuriera | Uwagi |
|---|---:|---:|---|
| `S/M-STANDARD` | 10,49 Allegro Delivery; 10,95 InPost | 14,99 | proste i zgodne z obecnym maksimum; optymalizować dopiero po pomiarze kosztów |
| `H-20` | tylko metody rzeczywiście dopuszczające masę; maks. 10,49/10,95 | 14,99 | nie każdy automat AD ma ten sam limit; sprawdź konkretną usługę |
| `H-25` | InPost wyłącznie ≤25 kg po zapakowaniu i w gabarycie | 14,99 | domyślnie kurier dla worka 24 kg, bo opakowanie zmniejsza bufor |
| `H-31.5` | wyłącz punkty/automaty | 14,99 | DPD kurier po potwierdzeniu limitu i dopłat; marża musi pokryć różnicę |
| `LONG` | zwykle wyłącz | 14,99 lub bieżące maksimum usługi | jeden bok >120 cm pozwala na kurierski wyjątek Smart |
| `PALLET/SPECIAL/LIVE` | nie stosuj standardowej stawki | kalkulacja indywidualna | osobna usługa/umowa i ręczna kwalifikacja |

Ceny 16/17/19 zł publikowane w sklepie RaFish dotyczą własnego kanału sklepowego i nie są automatycznie odpowiednim cennikiem Allegro. Na Allegro stawka klienta jest ograniczona, a niepokrytą różnicę trzeba uwzględnić w marży produktu.

## Porady operacyjne ze społeczności

Poniższe obserwacje są lekcjami praktyków, a nie regulaminem; zawsze weryfikuj je w oficjalnym cenniku:

- przy paczkach granicznych przewoźnicy naliczają dopłaty za pomiar gabarytu/wagi — dokumentuj wagę i trzy wymiary zamkniętej paczki;
- `etykieta utworzona` nie oznacza odbioru; jakość sprzedaży zależy od faktycznego skanu;
- błędny limit sztuk na paczkę prowadzi do dodatkowych etykiet finansowanych przez sprzedawcę;
- Smart jest darmowy dla kupującego po spełnieniu progu, ale nie dla sprzedawcy;
- zbyt ambitny cutoff i czas wysyłki obniża jakość, jeśli magazyn lub podjazd go nie dotrzymuje.

## Zasada zmian

Nie hardkoduj tych kwot w kodzie. Tabela `shipping_tariff_version` ma przechowywać `validFrom`, `validTo`, rynek, metodę, progi, brutto/netto, źródło i datę weryfikacji. Każda zmiana wywołuje ponowne przeliczenie marż SKU.
