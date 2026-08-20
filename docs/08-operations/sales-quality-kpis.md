# Jakość sprzedaży — KPI i alerty

Jakość sprzedaży jest głównym KPI projektu. Panel Allegro jest źródłem wyniku platformowego, a wewnętrzne wskaźniki mają ostrzegać wcześniej niż panel.

## Tablica dzienna

| KPI | Zielony cel wewnętrzny | Żółty | Czerwony / reakcja |
|---|---:|---:|---|
| wysyłka zgodnie z deklaracją | ≥98% | 95–97,99% | <95%: zamroź skracanie czasu i usuń przyczynę |
| pierwszy skan do cutoffu | ≥98% | 95–97,99% | <95%: audyt podjazdów i magazynu |
| zamówienia gotowe po terminie | 0 | 1 | >1 lub >2 h po cutoff: P1 |
| odpowiedzi w wymaganym czasie | ≥99% | 97–98,99% | <97%: dyżur i kolejka SLA |
| decyzja reklamacyjna średnio | <3 dni | 3–6,99 dnia | ≥7 dni: eskalacja właściciela |
| refundacja po odbiorze zwrotu | ≤1 dzień | >1–3 dni | >3 dni: eskalacja; od 2026-09-01 dodatkowy alarm dnia 5/7 |
| etykiety bez pierwszego skanu | 0 | 1 | >1 lub po cutoff: P1 |
| anulowania z winy braku zapasu | 0 | 1 / 30 dni | >1: blokada problematycznego SKU |
| oferty nieaktywne bez planu | 0 | — | każda: przypisz przyczynę i właściciela |
| niezgodność z opisem / uszkodzenie | trend spadkowy | stabilny | wzrost 2 tygodnie: audyt SKU/opakowania |

Cele są świadomie wyższe niż zapowiedziany próg punktacji wysyłki 92% od 2026-08-26. Minimum platformy nie jest bezpiecznym celem firmy.

## Osiem obszarów panelu

Panel Allegro pokazuje osiem miar/obszarów jakości (ich nazwy i punktacja mogą się zmieniać). Importuj wynik dzienny z datą, wartością, punktem odniesienia i szczegółami zamówień. Większość miar używa okna 30 dni, a wskaźniki wysyłkowe mogą posługiwać się szczególnym 28-dniowym oknem; integracja przechowuje definicję z dnia odczytu.

## Alerty wyprzedzające

- 2 godziny przed cutoff: nieprzydzielone `READY`;
- 30 minut przed cutoff: zapakowane bez etykiety;
- po cutoff: etykieta bez odbioru/skanu;
- co rano: przesyłki bez ruchu, zwroty otwarte, dyskusje bez odpowiedzi, oferty nieaktywne;
- dzień 1/5/6/7 zwrotu: kolejne poziomy alertu;
- tygodniowo: trend terminowości, zwrotów, reklamacji, anulowań i marży po Ads.

## Root-cause, nie korekta kosmetyczna

Każdy czerwony KPI otrzymuje przyczynę: `STOCK`, `PICK_PACK`, `CARRIER_PICKUP`, `LABEL_API`, `BAD_DIMENSION`, `PRODUCT_DATA`, `CUSTOMER_CONTACT`, `RETURN_QUEUE`, `ACCOUNT_POLICY` lub `UNKNOWN`. Powtarzające się `UNKNOWN` są błędem procesu.

## Zmiana zapowiedziana na 2026-08-26

Allegro zapowiada m.in. próg 92% wysyłki w terminie, 95% terminowych odpowiedzi i mocniejsze premiowanie szybkich refundacji. Dokument źródłowy: [zmiany panelu jakości](https://help.allegro.com/pl/sell/a/27-lipca-wprowadzimy-zmiany-w-panelu-jakosc-mojej-sprzedazy-1n8WWl3Kdu8). Po 26 sierpnia status należy zmienić z `planned` na `active` dopiero po sprawdzeniu panelu konta.
