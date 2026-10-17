# Allegro API — radar zmian dla MCP (2026-10-17)

**Weryfikacja źródeł publicznych: 2026-10-17.** To rejestr zmian w dokumentacji Allegro, **nie** potwierdzenie ich działania na koncie sprzedawcy. Snapshot katalogu API z 2026-08-20 pozostaje nieodświeżony: `HOLD` do czasu porównania Swaggera. Statusy **ACTIVE/PLANNED** odnoszą się do komunikatów Allegro, nie do gotowości naszej integracji.

| Komunikat / data | Status na 17.10 | Wpływ na przyszły MCP | Dowód |
|---|---|---|---|
| 2026-10-15: wycofanie rabatów typu multipack (jedna oferta) od 2026-11-30 | PLANNED | narzędzia promocji wymagają migracji, nie proponować nowego multipack jednoofertowego po dacie | [news](https://developer.allegro.pl/news/rabaty-ilosciowe-wycofujemy-mozliwosc-tworzenia-rabatu-typu-multipack-4R3MoYWrPi5) |
| 2026-10-13: opcjonalne `categoryId` w `POST /ingredients/parse` od 2026-10-13, wymagane od 2026-11-13 | ACTIVE / PLANNED | przyszła obsługa żywności/kosmetyków — migracja schematu żądania, brak zapisu w MVP | [news](https://developer.allegro.pl/news/post-ingredients-parse-dodalismy-pole-categoryid-k17omEL5ose) |
| 2026-10-07: obsługa „Problemów z zakupem” przez `/messaging` `beta.v1` od 2026-10-28 | PLANNED | ważne dla jakości sprzedaży; wyodrębnić nowe wątki od historycznych `/sale/issues`; scope i PII do zatwierdzenia | [news](https://developer.allegro.pl/news/centrum-wiadomosci-dostosuj-aplikacje-do-nowej-wersji-beta-v1-endpointow-na-sciezce-messaging-zostaly-juz-tylko-3-tygodnie-jn0YLm5rYiK) |
| 2026-10-05: nowy `POST /order/{orderId}/billing-documents/files` | ACTIVE | dokumenty faktury wrażliwe; bez uploadu w pierwszym MCP; stare ścieżki oznaczone deprecated | [news](https://developer.allegro.pl/news/zamowienia-uproscilismy-zalaczanie-faktur-jn0aj75mxcW) |
| 2026-10-02: zmiana modelu `GET /sale/user-ratings` oraz `/{ratingId}` `public.v1` od 2026-11-02 | PLANNED | testy regresji parsera ocen i nagłówków Accept | [news](https://developer.allegro.pl/news/oceny-sprzedazy-2-listopada-2026-wdrozymy-nowa-strukture-na-wersji-public-v1-3A3BzbYWjIW) |
| 2026-10-01: od 2026-10-29 numer przewozowy wyłącznie w `packages.transportingInfo` dla `GET /shipment-management/shipments/{shipmentId}` | PLANNED | krytyczne dla audytu nadania i śledzenia; nie opierać parsera na `additionalProperties` | [news](https://developer.allegro.pl/news/wysylam-z-allegro-29-pazdziernika-przestaniemy-zwracac-numery-przewozowe-w-obiekcie-additionalproperties-WvgDEDPAlfX) |
| Changelog: 2026-09-29 usunięcie `nextItemRate`; 2026-10-05 prefiks telefonu w nadaniach | ACTIVE (wg changelogu) | rozdzielić modele historyczne od nowych, testy walidacji telefonu | [changelog](https://developer.allegro.pl/changelog) |

## Priorytet implementacji

1. **P0 (do 28.10):** zaprojektować odczyt metadanych wątków bez treści i danych kupujących; oszacować ryzyko nowych Problemów z zakupem. Samo istnienie endpointu nie nadaje dostępu.
2. **P0 (do 29.10):** przygotować test fixture `transportingInfo`, stare pole oznaczyć deprecated. Nie uznawać utworzonej etykiety za nadanie.
3. **P1 (do 02.11):** kontrakt odczytu ocen `public.v1`; osobno wskazać że backend może zmienić strukturę.
4. **P1:** pełne porównanie nowego OpenAPI z migawką 2026-08-20, włącznie z path/method/scopes/media type/required fields.
5. **P2:** promocje, faktury, składniki — dopiero po wdrożeniu i zatwierdzeniu odpowiedniego zakresu.

**Ograniczenie:** daty i szczegóły opierają się na oficjalnych ogłoszeniach z ww. linków. Nie uruchamiano API z tokenem, nie testowano konta, nie pobrano nowej kompletnej migawki Swaggera. Wnioski dotyczące zgodności kodu są do zweryfikowania w przyszłym runtime.
