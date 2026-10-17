# Audyt zmiany katalogu Allegro OpenAPI — 2026-10-17

Stan: **HOLD — candidate only, not approved/pinned**. Wynik z oficjalnego `https://developer.allegro.pl/swagger.yaml`, pobranego przez GitHub Actions dnia 2026-10-17 o 08:31:56 UTC. Powtarzalny run: https://github.com/dejvid673-prog/allegro/actions/runs/39017702654 — artefakt `allegro-openapi-unreviewed` (retencja: 30 dni). Źródłem raportu jest `scripts/compare_api_catalogs.py` zestawiający stan przyjęty 2026-08-20 z kandydatem 2026-10-17.

## Metryki kontraktu

| Wartość | Pinned 2026-08-20 | Candidate 2026-10-17 | Różnica |
|---|---:|---:|---:|
| Ścieżki | 201 | 204 | +3 |
| Operacje | 267 | 270 | +3 |
| Schematy komponentów | 967 | 982 | +15 |
| Operacje oznaczone deprecated | 6 | 11 | +5 |
| SHA-256 pobranego dokumentu | `a8ce81f568d9b97986360cc2a62c6708dbe23686051a6fbcf18244e6eb7cd1c8` | `78ed5d11ae9728e12b2d2bfb85c8751a6c5593833b35b934d3ecfdbe2b52f285` | różne |

**Modyfikacje katalogu operacji:** 3 dodane, 0 usuniętych, 13 ze zmianami w monitorowanych polach. To NIE jest pełny diff 982 schematów. Zmiany w polach `required`, strukturach request/response, media types i enumach mogą istnieć poza niniejszym porównaniem.

## Nowe operacje

- `GET /fulfillment/warehouse` — nowy odczyt magazynu, nie udostępniać agentowi bez sprawdzenia scope/danych.
- `POST /ingredients/parse` — operacja zapisu/przetwarzania; pierwszy MCP jest offline i jej nie wywołuje.
- `POST /order/{orderId}/billing-documents/files` — upload plików faktur; dane potencjalnie wrażliwe, narzędzie **BLOCKED**.

## Zmiany istniejących operacji

1. `DELETE /sale/offer-additional-services/groups/{groupId}/translations/{language}`: scope z `allegro:api:sale:offers:write` na `allegro:api:sale:settings:write`. **Ważna zmiana autoryzacji**; przed przyszłym zapisem wymagany jawny audyt.
2. `GET /messaging/threads`: liczba parametrów z **7 na 8**; sprawdzić nazwę, wymagania i `beta.v1`. Endpoint może zwracać dane osobowe — brak dostępu w MVP.
3. Sześć odczytów wyników zadań poleceń ofert otrzymało dodatkową deklarowaną odpowiedź HTTP **400**:
   - `GET /sale/offer-bulk-modification-commands/{commandId}/tasks`
   - `GET /sale/offer-modification-commands/{commandId}/tasks`
   - `GET /sale/offer-price-automation-commands/{commandId}/tasks`
   - `GET /sale/offer-price-change-commands/{commandId}/tasks`
   - `GET /sale/offer-publication-commands/{commandId}/tasks`
   - `GET /sale/offer-quantity-change-commands/{commandId}/tasks`
4. **Nowo deprecated (5):**
   - `GET /sale/turnover-discount`
   - `PUT /sale/turnover-discount/{marketplaceId}`
   - `PUT /sale/turnover-discount/{marketplaceId}/deactivate`
   - `POST /order/checkout-forms/{id}/invoices`
   - `PUT /order/checkout-forms/{id}/invoices/{invoiceId}/file`

## Decyzja o bezpieczeństwie MCP

- **Nie nadpisano** zatwierdzonego `sources/generated/openapi-metadata.json`, `endpoints.json` ani `docs/02-api/endpoint-catalog.md`. Aktualny kontrakt jest kandydatem w artefakcie.
- Różnica hash jest potwierdzona, ale **nie określa automatycznie breaking changes**. Co najmniej jedna modyfikacja scope i zmiana parametrów wymagają analizy przed dopuszczeniem kolejnego etapu.
- Do czasu pełnej inspekcji schematów request/response, zakresów, enumów, media types i testów regresji stan katalogu: **HOLD**.
- Następny etap: zrobić review pełnej specyfikacji; jeżeli kompatybilność została potwierdzona, osobny PR aktualizujący wszystkie trzy generowane pliki; dopiero po akceptacji zmienić bazowy hash.

## Terminowe ryzyka operacyjne

- **2026-10-28:** `/messaging` `beta.v1` i Problemy z zakupem dla kont firmowych. Źródło: https://developer.allegro.pl/news/centrum-wiadomosci-dostosuj-aplikacje-do-nowej-wersji-beta-v1-endpointow-na-sciezce-messaging-zostaly-juz-tylko-3-tygodnie-jn0YLm5rYiK.
- **2026-10-29:** dla `GET /shipment-management/shipments/{shipmentId}` numery przewozowe przenoszone do `packages.transportingInfo`. Źródło: https://developer.allegro.pl/news/wysylam-z-allegro-29-pazdziernika-przestaniemy-zwracac-numery-przewozowe-w-obiekcie-additionalproperties-WvgDEDPAlfX.
- **2026-11-02:** zmiana modelu odczytu ocen w `public.v1` (wymagany test integracyjny).
- **2026-11-13:** wymagany `categoryId` przy `POST /ingredients/parse`.
- **2026-11-30:** wycofanie jednoofertowych rabatów multipack.

Opis dotyczy wyłącznie dokumentacji i testów generowania. Nie wykonano odczytu autoryzowanego konta Allegro ani testu produkcyjnego.
