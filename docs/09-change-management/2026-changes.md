# Zmiany Allegro 2026–2027

Stan na **2026-08-20**. `PLANNED` nie oznacza wdrożenia — po terminie trzeba sprawdzić Swagger, changelog, pomoc i zachowanie konta.

| Data | Status 2026-08-20 | Zmiana | Działanie |
|---|---|---|---|
| 2026-04-14 | ACTIVE | wyłączono zasoby `offer-variants` | używać wariantów produktowych; test braku starych wywołań |
| koniec 2026-06 | ACTIVE | obowiązkowy własny `User-Agent` | format `Nazwa/Wersja (+URL)`, monitoring 4xx |
| 2026-07-22 | ACTIVE | `type` i `dispatchCountry` w nowych cennikach | migracja modeli i test POST/PUT |
| 2026-07-29 | ACTIVE | pełna obsługa `aiCoCreatedContent.images` | deklarować pochodzenie przy pierwszym uploadzie; nieznane = blokada |
| 2026-08-02 | ACTIVE | obowiązki oznaczania treści AI | dowód pochodzenia każdego zdjęcia |
| 2026-08-26 | PLANNED | nowe progi Jakości sprzedaży | potwierdzić panel; odświeżyć KPI/testy punktacji |
| koniec 2026-08 | PLANNED/BETA | nowe „Problemy z zakupem” w Messaging | wykryć schematy w Swaggerze, dodać obsługę bez duplikacji |
| 2026-09-01 | PLANNED | automatyczne zwroty po odstąpieniu | alert dzień 1/5/6/7, uzgodnienie refundacji Allegro |
| 2026-09-01 | PLANNED | nowy Regulamin REST API dla nowych kluczy | użyć klucza w 30 dni, nie dopuścić do >90 dni bezczynności, inwentaryzacja aplikacji |
| 2026-10-28 | PLANNED | rollout Messaging dla kont firmowych | testy eventów, SLA i uprawnień |
| Q1 2027 | PLANNED | usunięcie `GET /shipment-management/delivery-services` | korzystać z `delivery-proposals/{orderId}` |

## Automatyczny radar zmian

Codziennie pobieraj hash Swaggera, news i changelog. Po zmianie:

1. wygeneruj katalog endpointów i diff;
2. wykryj nowe/usunięte/deprecated operacje, scopes, pola wymagane i enumy;
3. oznacz dotknięte moduły i testy;
4. zatrzymaj zapis tylko dla ryzykownej klasy operacji;
5. po przeglądzie zaktualizuj rejestr źródeł i daty weryfikacji.

Zmiany pomocy handlowej (Smart, prowizje, limity, Ads) wymagają osobnego radaru, bo nie muszą zmieniać Swaggera.
