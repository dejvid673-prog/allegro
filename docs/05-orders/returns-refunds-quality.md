# Zwroty, reklamacje i jakość sprzedaży

Weryfikacja: **2026-08-20**. Daty przyszłe są oznaczone jako planowane i wymagają ponownego sprawdzenia po wdrożeniu.

## Kolejka zwrotów

Każdy zwrot ma rekord z: zamówieniem i pozycjami, powodem, datą zgłoszenia, numerem przesyłki, przewidywaną i faktyczną datą odbioru, stanem towaru, dowodami, kwotą produktów, dostawy i potrąceń, terminem ustawowym/platformowym, osobą odpowiedzialną oraz wynikiem refundacji Allegro.

| Moment | Automatyczna kontrola | Działanie człowieka |
|---|---|---|
| zgłoszenie | deduplikacja, termin, powiązanie pozycji i trackingu | ocena wyjątku, jeżeli brak danych |
| pierwszy skan zwrotny | monitoring ETA | kontakt tylko przy anomalii |
| odbiór | rozpoczęcie SLA inspekcji; zdjęcia paczki i towaru | klasyfikacja A/B/uszkodzony/niezgodny |
| dzień 1 | alert, jeżeli brak decyzji/refundacji | decyzja i zwrot środków |
| dzień 5 | czerwony alert dla spraw otwartych | eskalacja właściciela |
| dzień 6–7 | blokada ryzyka automatycznego zwrotu | refundacja, odmowa lub uzasadnione zatrzymanie |
| po refundacji | uzgodnienie kwot w Allegro i księgowości | wyjaśnienie różnic |

Od **2026-09-01** Allegro zapowiada automatyczną refundację odstąpienia konsumenta: dla zwrotów zgłoszonych od tej daty na kontach firmowych i odesłanych metodą zwrotu Allegro, gdy platforma potwierdzi fizyczny odbiór, sprzedawca ma 7 dni kalendarzowych na decyzję. Jeżeli nie zwróci środków ani nie wybierze w zakładce Zwroty `Odmowa zwrotu` z powodem, Allegro ma wykonać zwrot ósmego dnia, około końca dnia. `Odmowa` może czasowo zablokować automat na czas uzasadnionej weryfikacji; kupujący widzi powód. Sama Dyskusja nie blokuje automatu. Funkcji nie można wyłączyć ani wydłużyć terminu.

Zwrot wykonany poza Allegro nie jest widoczny dla systemu. Trzeba wtedy przed deadlinem oznaczyć decyzję/odmowę z powodem „zwrot poza systemem”, aby nie doprowadzić do podwójnej refundacji. Mechanizm nie dotyczy reklamacji, paczek nieodebranych ani zwrotów wysłanych poza metodami Allegro, których platforma nie potrafi potwierdzić.

## Reklamacje i Dyskusje

- odpowiedź w Dyskusji: operacyjny alarm przed 24 godzinami, z uwzględnieniem weekendów i świąt;
- decyzja reklamacyjna w Polsce i na Węgrzech: nie później niż 14 dni; Czechy i Słowacja: 30 dni — zawsze sprawdź bieżący regulamin dla rynku;
- nie zamykaj sprawy samą wiadomością: zapisuj decyzję, kwotę, dowód i stan wykonania;
- nie używaj danych ze zdjęć klienta do innych celów; ogranicz dostęp i retencję.

## Planowana zmiana punktacji 2026-08-26

Allegro zapowiedziało przesuniętą na **2026-08-26** zmianę jakości sprzedaży. Po wejściu w życie trzeba ponownie pobrać progi z panelu i pomocy. Najważniejsze elementy zapowiedzi:

- bazowy próg `Wysyłka w terminie` 92%, zakres punktów od około -460 do 40;
- próg terminowych odpowiedzi 95%;
- `Szybkie zwroty wpłat`: malejące punkty dla średnio 1–5 dni, zero powyżej 5 dni;
- najwyższy wynik decyzji reklamacyjnych przy średniej poniżej 7 dni.

Nie ustawiaj celów na samym minimum. Wewnętrzny próg powinien mieć bufor na błąd przewoźnika i pojedynczy incydent.

## Zasady automatyzacji refundacji

Refundacja jest `RESTRICTED`, dopóki nie powstaną limity kwotowe i testy. Agent może automatycznie obliczyć propozycję, ale musi:

1. ponownie pobrać aktualne zamówienie i zwrot;
2. sprawdzić wcześniejsze refundacje i chargeback;
3. rozdzielić wartość produktu, dostawy i dopłat;
4. nie odliczać kosztów bez podstawy i dowodów;
5. pokazać kwotę brutto oraz walutę;
6. po zatwierdzeniu odczytać wynik i uzgodnić go z księgowością.
