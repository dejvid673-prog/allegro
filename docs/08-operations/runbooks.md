# Runbooki operacyjne

## Dzienny start

1. Sprawdź status API Allegro i przewoźników.
2. Pobierz nowe zdarzenia, następnie wykonaj uzgodnienie pełnego stanu.
3. Obsłuż kolejno: P0 bezpieczeństwo/żywe zwierzęta, P1 zamówienia i paczki, zwroty z terminem, wiadomości/reklamacje, oferty nieaktywne, optymalizacje.
4. Zapisz wynik jakości, koszty naliczone poprzedniego dnia i odstępstwa.

## Oferta zakończona lub nieaktywna

1. Odczytaj bieżący status, publikację na rynkach, zapas, błędy i ostatnie zdarzenie.
2. Sklasyfikuj: sprzedaż całego zapasu, błąd, ręczne zakończenie, naruszenie, archiwizacja, przerwa, brak produktu lub problem ceny.
3. Nie wznawiaj naruszenia ani nie duplikuj oferty.
4. Przeprowadź preflight aktualnych parametrów, produktu, kosztów i duplikatów.
5. Pokaż zmianę i uzyskaj zatwierdzenie.
6. Po wznowieniu zweryfikuj aktywność oraz naliczenie/promowanie.

## Rozjazd zapasu

1. Wstrzymaj automatyczne zwiększanie ilości.
2. Ustal system master i porównaj ostatnie zdarzenia sprzedaży/przyjęcia.
3. Chroń przed oversellingiem: zmniejszenie do bezpiecznej wartości jest ważniejsze niż ekspozycja.
4. Napraw idempotencję/lock, wykonaj inwentaryzację i dopiero potem odblokuj.

## Błąd API/timeout po `POST`

1. Nie powtarzaj requestu.
2. Zapisz `Trace-Id`, czas, identyfikator polecenia i hash payloadu.
3. Sprawdź status Command lub wyszukaj utworzony zasób.
4. Jeżeli wynik nadal nieznany, oznacz `UNKNOWN_OUTCOME` i skieruj do człowieka.
5. Retry dopiero po dowodzie, że zasób nie powstał.

## Incydent masowy

1. Wyłącz tylko klasę operacji zapisu objętą incydentem; odczyt pozostaw, jeśli bezpieczny.
2. Zachowaj kolejkę i nie zwiększaj równoległości.
3. Sprawdź status Allegro, limity i aktualności.
4. Uzgodnij stan zasobów przed wznowieniem.
5. Wznawiaj małą partią, monitorując duplikaty i jakość.

## Pogoda i żywe ryby

1. Przed pakowaniem sprawdź warunki na całej trasie i zdolność przewoźnika do terminowego transportu.
2. Nadawaj tylko w zatwierdzone dni i opakowaniu dobrostanowym.
3. Przy ryzyku upału/mrozu/opóźnienia wstrzymaj, poinformuj kupującego i zaproponuj nowy termin lub odbiór.
4. Nie ukrywaj żywej zawartości przed przewoźnikiem.
