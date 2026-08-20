# Model danych

## Główne encje

| Encja | Klucz | Ważne pola |
|---|---|---|
| `account` | `account_id` tekst | marketplace, status, scopes, quality level |
| `application_credential_ref` | `app_id` | referencja do sejfu, ostatnie użycie; bez sekretu |
| `sku` | `sku` | GTIN, nazwa, profil, masa/wymiary zapakowane, master source |
| `product_binding` | account + SKU + marketplace | Allegro product id, category id, verification time |
| `offer` | account + offer id | SKU, status, publication, price, stock, shipping rate, revision |
| `offer_snapshot` | offer + observed_at | znormalizowany stan i hash |
| `offer_template` | template id + version | neutralne pola oferty, compliance i źródła |
| `policy_finding` | finding id | severity, rule id/version, evidence, resolution |
| `cost_snapshot` | SKU + channel + valid_from | pełne koszty, cena, margin, completeness |
| `order` | account + checkout form id | revision, READY, buyer ref, delivery, totals |
| `order_line` | lineItem id | SKU, qty, offer id, price, tax |
| `parcel` | order + sequence | service, packed dimensions, command id, tracking, state |
| `parcel_event` | carrier + event id/hash | occurred_at, received_at, raw ref, normalized state |
| `return_case` | return id | order lines, received_at, SLA, decision, refund |
| `operation` | operation UUID | type, level, request hash, approval, state, Trace-Id |
| `outbox` | event id | payload ref, attempts, next attempt, published_at |
| `source_version` | source id + fetched_at | URL, hash, effective date, status |

## Zasady typów

- identyfikatory zawsze tekstowe;
- kwoty jako `numeric` + `currency`, nigdy float;
- data/czas jako UTC z zachowaniem źródłowej strefy/cutoffu;
- wymiary w mm i masa w g jako liczby całkowite;
- wartości `UNKNOWN`, `NOT_APPLICABLE` i `ZERO_CONFIRMED` muszą być rozróżnialne;
- surowy JSON tylko jako dowód wersjonowany; logika działa na jawnych polach znormalizowanych.

## Wersjonowanie

Oferta, profil paczki, koszt, reguła i cennik dostawy są wersjonowane czasowo. Rekalkulacja historycznej marży używa wersji obowiązującej w momencie zamówienia, nie dzisiejszej.

## PII i retencja

Dane kupującego przechowuj tylko w zakresie potrzebnym do realizacji i obowiązków prawnych. W logach używaj pseudonimowego `buyer_ref`. Etykiety i zdjęcia zwrotu mają osobny dostęp/retencję. Dane testowe nie mogą być kopiami produkcyjnych klientów.
