# Nadawanie przesyłek przez Allegro

Weryfikacja: **2026-08-20**. Kontrakt endpointów zawsze sprawdź w generowanym katalogu i Swaggerze.

## Przepływ zalecany

1. Przyjmij tylko aktualne zamówienie `READY_FOR_PROCESSING`.
2. Zarezerwuj zapas i wybierz zweryfikowany profil paczki SKU.
3. Pobierz `GET /shipment-management/delivery-proposals/{orderId}`.
4. Porównaj proponowaną usługę z metodą kupującego i ograniczeniami produktu.
5. Zbuduj paczkę z rzeczywistą masą po zapakowaniu, wymiarami, zawartością i kwotą ubezpieczenia.
6. Zapisz UUID i payload zanonimizowany; wywołaj polecenie utworzenia przesyłki.
7. Odpytuj status z `Retry-After`; obsłuż błędy poszczególnych paczek.
8. Pobierz etykietę/protokół, ale przechowuj je jako dane wrażliwe poza Git.
9. Zleć podjazd lub oznacz przekazanie do punktu.
10. Monitoruj pierwszy skan. `LABEL_CREATED` nie oznacza `HANDED_OVER`.
11. Przekaż tracking do zamówienia i klienta zgodnie z wymaganym kanałem.
12. Monitoruj ruch, doręczenie, odmowę, zwrot i uszkodzenie.

Stary `GET /shipment-management/delivery-services` jest oznaczony jako deprecated i ma zostać wyłączony w I kwartale 2027. Nowa implementacja korzysta z propozycji dla konkretnego zamówienia.

## Walidacja paczki

| Pole | Źródło prawdy | Kontrola |
|---|---|---|
| masa | pomiar zapakowanego SKU/zestawu | limit usługi i próg dopłaty |
| wymiary | kartoteka zatwierdzonego opakowania | każdy bok, suma/gabaryt, automat/punkt |
| liczba sztuk w paczce | reguła pakowania SKU | nie przekracza masy i ochrony towaru |
| typ zawartości | profil produktu | ciecz, sypki, elektronika, żywy, CLP |
| ubezpieczenie | wartość zamówienia i warunki usługi | limit odpowiedzialności przewoźnika |
| adres/punkt | bieżące zamówienie/proposal | bez ręcznej transliteracji i skracania |
| e-mail | zamaskowany e-mail Allegro | przekazany dokładnie przewoźnikowi |

## InPost

Dla `Wysyłam z Allegro` z InPost potrzebna jest właściwa umowa/ShipX token po stronie integracji. Token przewoźnika przechowujemy w sejfie sekretów. Gabaryt Paczkomatu nie jest wyznaczany wyłącznie masą: obowiązuje limit wymiarów i maksymalnie 25 kg.

## Etykiety i dokumenty

- nie umieszczaj PDF/ZPL w logach, issue ani repozytorium;
- plik wydaj tylko magazynowi uprawnionemu do danego zamówienia;
- znakuj wydruk identyfikatorem zadania, ale nie danymi zbędnymi;
- anulowanie etykiety nie oznacza automatycznie refundacji opłaty — sprawdź status rozliczenia;
- ponowny wydruk tej samej etykiety jest bezpieczniejszy niż utworzenie nowej przesyłki.
