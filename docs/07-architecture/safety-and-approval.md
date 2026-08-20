# Bezpieczeństwo i zatwierdzanie

## Zasada dwóch kroków

Operacja zmieniająca Allegro ma dwa niezależne kroki:

1. `proposal`: migawka danych, minimalny diff, koszt, walidacje i czas ważności;
2. `execute`: po zatwierdzeniu, pod warunkiem że revision i dane krytyczne się nie zmieniły.

Zmiana ceny, zapasu, kategorii, produktu, dostawy, compliance lub statusu unieważnia wcześniejszą zgodę.

## Zakres zgody

Token zatwierdzenia jest jednorazowy, krótko ważny i związany z kontem, operacją, listą zasobów oraz hashem diffu. Zgoda na jedną ofertę nie uprawnia do masowej edycji ani do drugiego konta.

## Kill switch i limity

- osobny przełącznik dla ofert, cen/zapasu, przesyłek i refundacji;
- limit operacji/dzień, maksymalna kwota zmiany ceny i refundacji;
- stop po pierwszym nieznanym wyniku lub wzroście błędów;
- stop przy niespójności konta, marketplace lub źródła master;
- automatyczne przejście do read-only przy problemie OAuth, 429 lub incydencie Allegro.

## Kontrole wielokontowe

Każdy zasób jest przypisany do `accountId`. Przed publikacją wyszukaj duplikaty na wszystkich powiązanych kontach. Token i zgoda są account-bound. Raport nie może mieszać jakości ani zamówień kont bez jawnego oznaczenia.

## Sekrety

Client Secret, refresh/access token i ShipX znajdują się w sejfie. Baza przechowuje wyłącznie referencję i metadane rotacji. Logi redagują nagłówki `Authorization`, e-mail, telefon, adres i treść etykiety.

## Testy obowiązkowe przed write

- timeout po POST z późniejszym sukcesem;
- powtórzony event i event poza kolejnością;
- połączone/anulowane zamówienie podczas pakowania;
- częściowy błąd Command;
- oferta zmieniona po zatwierdzeniu;
- paczka przekracza wagę po zapakowaniu;
- dwa konta z tym samym produktem;
- brak kosztu i ujemna marża;
- powrót 429/5xx oraz wygasły token;
- zdjęcie AI o nieznanym pochodzeniu;
- planowany parametr staje się wymagany.
