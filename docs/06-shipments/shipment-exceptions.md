# Wyjątki przesyłek i paczki, które nie wyjechały

## Najważniejsze rozróżnienie

Utworzenie etykiety, zamówienie podjazdu i przekazanie przesyłki to trzy różne zdarzenia. Za dowód wyjazdu przyjmujemy pierwszy wiarygodny skan przewoźnika albo elektroniczny protokół odbioru powiązany z numerem przesyłki.

## Alerty

| Kod | Warunek | Priorytet | Pierwsza reakcja |
|---|---|---:|---|
| `NO_PICKUP` | podjazd minął, brak odbioru | P1 | sprawdź protokół i inne paczki z podjazdu; zgłoś problem w Centrum Sprzedaży |
| `NO_FIRST_SCAN` | etykieta istnieje, a brak skanu do cutoff/ustalonego bufora | P1 | potwierdź fizyczną lokalizację paczki; nie twórz drugiej etykiety |
| `PARTIAL_PICKUP` | część etykiet z jednego podjazdu ma skan | P1 | raport listy numerów odebranych i pozostawionych |
| `LABEL_ERROR` | Command zakończony częściowo/błędem | P1 | odczytaj wynik per paczka; retry tylko nieutworzonej części |
| `STALLED_TRANSIT` | brak nowego skanu ponad SLA trasy | P2 | zgłoszenie do przewoźnika i informacja klienta |
| `WRONG_DIMENSION` | dopłata/odmowa z powodu gabarytu | P2 | zabezpiecz pomiar i zdjęcia; popraw profil paczki |
| `RETURN_TO_SENDER` | odmowa, brak odbioru lub problem adresu | P2 | powiąż zwrot, nie wprowadzaj od razu do sprzedaży |
| `WEATHER_HOLD` | ryzyko dobrostanu żywych ryb | P0 | wstrzymaj nadanie i skontaktuj się z klientem |

## Runbook: brak pierwszego skanu

1. Zablokuj automatyczne ponowne nadanie.
2. Sprawdź strefę czasu, deklarowany cutoff i status API przewoźnika.
3. Ustal, czy paczka jest na magazynie, w punkcie czy została zabrana bez skanu.
4. Zbierz: numer podjazdu, numery przesyłek, godzinę, protokół, zdjęcie stosu/paczki i nazwę usługi.
5. Zgłoś w oficjalnym kanale Allegro/przewoźnika. Problemy z podjazdem zamówionym przez `Wysyłam z Allegro` zgłaszaj niezwłocznie w Centrum Sprzedaży.
6. Poinformuj klienta konkretnie, bez deklarowania doręczenia, którego przewoźnik nie potwierdził.
7. Utwórz nową etykietę tylko po ustaleniu, że pierwsza nie jest w ruchu, i anuluj/uzgodnij koszt pierwszej.
8. Po zamknięciu popraw cutoff, trasę magazynową lub profil opakowania.

## Dowody pomiaru

Przy ciężkich i granicznych paczkach zapisuj zdjęcie zamkniętej paczki na wadze, trzy wymiary z miarą, identyfikator opakowania i czas pomiaru. To materiał do reklamacji dopłaty oraz do kalibracji kartoteki. Dane klienta nie powinny być widoczne na zdjęciu.

## Codzienne uzgodnienie

Codziennie zestaw:

- wszystkie zamówienia `READY`/`ALLOCATED` po terminie;
- etykiety bez pierwszego skanu;
- przesyłki bez ruchu, zwracane i doręczone;
- podjazdy częściowe;
- etykiety anulowane bez potwierdzenia rozliczenia;
- obiecany czas wysyłki z rzeczywistym pierwszym skanem.
