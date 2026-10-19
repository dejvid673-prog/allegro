# Allegro MCP — cztery narzędzia operacyjne offline (19.10.2026)

**Status: IMPLEMENTED / CI unit & MCP smoke pending review. NOT CONNECTED to Allegro.**
MCP przyjmuje wyłącznie dane przesłane przez operatora; **niczego nie czyta z kont sprzedawcy, nie nadaje paczek, nie zmienia cen i nie pobiera rynku przez scraping.** Testy mogą dowieść poprawności arytmetyki i walidatorów, ale nie prawdziwości wprowadzonych danych. Wszystkie identyfikatory (konto, zamówienie, SKU) są tekstem.

## Narzędzia

### 1. `allegro_assortment_audit_offline(offers, product_master)`

Porównuje ofertę z jawnymi oczekiwaniami **osobno dla każdego `connection_id`**. Stan magazynowy nie jest bez dowodu traktowany jako stan publikowany na kontach.

```json
{
  "offers": [
    {
      "connection_id": "allegro-a", "offer_id": "12345678", "sku": "KREDA-25",
      "gtin": "5901234123457", "stock": 4, "price_gross": "55.00",
      "status": "ACTIVE"
    },
    {
      "connection_id": "allegro-b", "offer_id": "87654321", "sku": "KREDA-25",
      "gtin": "5901234123457", "stock": 2, "price_gross": "57.00",
      "status": "ACTIVE"
    }
  ],
  "product_master": [
    {
      "sku": "KREDA-25", "gtin": "5901234123457",
      "expected_stock_by_connection": {"allegro-a": 4, "allegro-b": 2},
      "expected_price_by_connection": {"allegro-a": "55.00", "allegro-b": "57.00"}
    }
  ]
}
```

`status=PASS` oznacza wyłącznie zgodność tych danych. `REVIEW` zawiera `STOCK_DRIFT`, `PRICE_DRIFT`, `SKU_MISSING_IN_MASTER`, `GTIN_MISMATCH` lub `POSSIBLE_MULTI_ACCOUNT_DUPLICATE`. Odnotowanie trzeciej aktywnej oferty jest **sygnałem do oceny produktu/kategorii i regulaminu**, nie automatycznym stwierdzeniem naruszenia.

### 2. `allegro_price_change_proposal_offline(current_offer, proposed_price_gross, projected_cost_snapshot)`

Zwraca nieegzekwowalną propozycję zmiany jednej ceny, zachowując `expected_price_gross`. Wymaga **nowego kompletnego** modelu `cost_snapshot` identycznego jak dla `allegro_cost_preflight_offline`, w tym:

- `salesPriceGross` = proponowana cena; `salesRevenueNet` jako kwota netto po prawidłowym przeliczeniu VAT;
- wszystkie 17 pól kosztów z `templates/cost-model.schema.json`: `KNOWN`, `ZERO_CONFIRMED` lub `NOT_APPLICABLE`, każde z `sourceRef` i `effectiveAt`;
- kwoty wyłącznie dokładne ciągi dziesiętne, np. `"55.00"`, **nie** liczby zmiennoprzecinkowe;
- opłaty zależne od nowej ceny (prowizja, promocje, reklama) muszą być **ponownie skalkulowane** przez operatora; program sam ich nie estymuje;
- waluta `PLN`, `taxBasis=NET`, dodatnia cena, wymagana marża minimalna.

Wynik: `DRAFT` albo `BLOCK`; nigdy `APPROVED`. Funkcja nie oblicza automatycznie VAT ani nie tworzy pliku uprawniającego do zapisu w Allegro. Przed realną zmianą wymagana nowa, aktualna kontrola oferty i jednoznaczna zgoda.

### 3. `allegro_market_comparison_offline(own_offers, competitor_observations)`

Porównuje **brutto produktu + zadeklarowany koszt dostawy** i cenę za kg. Dane wejściowe muszą mieć:

- po stronie własnej: `connection_id`, `offer_id`, `sku`, `gtin`, `net_weight_grams`, `units_per_offer`, `condition`, `price_gross`, `shipping_gross`;
- po stronie konkurenta: `offer_ref`, `source_type` (`USER_PROVIDED_EXPORT` albo `LICENSED_FEED`), `source_ref`, `observed_at` ze strefą czasu oraz te same parametry produktu i dostawy.

Dla porównania **wymagany jest identyczny GTIN, jednostki, gramatura i stan towaru**. Nie porównujemy 24 kg z 25 kg jako tego samego produktu. Obserwacja starsza niż 14 dni jest pomijana i zgłaszana jako `STALE_MARKET_OBSERVATION`. Brak deklaracji źródła blokuje cały raport. Brak potwierdzonego źródła **nie pozwala twierdzić**, że jest to aktualny lub kompletny obraz konkurencji.

To nie jest skaner Allegro. Obecne zwykłe REST API sprzedawcy nie udostępnia ogólnego `GET /offers/listing`. Import ma pochodzić z uprawnionego eksportu lub licencjonowanego dostawcy.

### 4. `allegro_shipment_events_audit_offline(shipments, as_of=None)`

Ocena kontroli po wystawieniu etykiety; `as_of` to opcjonalny czas oceny w ISO 8601 z UTC offsetem (nie jest to czas nadania). Przykład jednej pozycji:

```json
{
  "connection_id": "allegro-a", "order_id": "order-1",
  "shipment_id": "shipment-1", "tracking_number": "tracking-1",
  "status": "LABEL_CREATED",
  "label_created_at": "2026-10-18T10:00:00Z",
  "first_scan_at": null, "first_scan_verified": false,
  "cod_required": false
}
```

Narzędzie wykrywa:
- `LABEL_OLDER_THAN_24H_NO_FIRST_SCAN` (etykieta od ponad 24 h bez skanu);
- `FALSE_HANDOVER_STATUS` (status przekazania bez zweryfikowanego skanu);
- `FIRST_SCAN_UNVERIFIED`, `SCAN_VERIFIED_WITHOUT_TIMESTAMP`, czas skanu sprzeczny z datą etykiety;
- `COD_AMOUNT_MISMATCH` i `COD_AMOUNT_MISSING` dla pobrań;
- `TRACKING_ASSIGNED_TO_MULTIPLE_ORDERS` w jednym koncie.

`confirmed_handover_count` to liczba rekordów z flagą `first_scan_verified=true` i prawidłowym czasem skanu; funkcja **nie weryfikuje sama tej flagi u przewoźnika**. Reguła 24h jest operacyjnym alertem przyjętym na potrzeby pierwszych testów, nie ogólną deklaracją SLA operatora.

## Inwarianty i ograniczenia

- Każdy tool zwraca `writes_performed=false`, bez tokenów i bez sieci.
- `PASS` = sprawdzono wewnętrzną spójność danych operatora, nie potwierdzono realnego zamówienia Allegro.
- Maksymalnie 500 elementów na zbiór. Nie należy przekazywać danych osobowych kupujących do tych tools.
- Rozdzielnie traktujemy `expected_stock_by_connection` i `expected_price_by_connection`. Brak oczekiwań = alert, nie zero.
- Konieczna jest późniejsza warstwa `READ` z aktualnego API i weryfikacja tożsamości obu kont, źródła kosztów i danych konkurencji.
- Każda operacja realnego WRITE (nadanie, publikacja, zmiana ceny) wymaga oddzielnego kontraktu bezpieczeństwa, zatwierdzenia, trwałego operation ledger i reconciliation.

## Uruchomienie/test

```bash
python -m pip install -r requirements-mcp.txt
python -m unittest discover -s tests -v
python -m scripts.smoke_mcp
python -m allegro_mcp.server
```

Środowisko: Python 3.11+, SDK `mcp==2.3.0`. W `stdio` logi na stdout kolidują z protokołem. Kompletne testy Github Actions obejmują `compileall`, `unittest` oraz połączenie klient–serwer SDK w pamięci. **Nie jest to jeszcze test uruchomienia desktopowego na Windows ani operacji live.**

## Powiązane materiały

- [Główna propozycja architektury](mcp-allegro-business-operator-proposal-2026-10-17.md)
- [Wcześniejszy audyt](../../audit/legacy-allegro-mcp-2026-10-17.md)
- [Model kosztów](../../templates/cost-model.schema.json)
- [Profil paczki](../../templates/shipping-profile.schema.json)
- [Oficjalna dokumentacja Allegro](https://developer.allegro.pl/)
