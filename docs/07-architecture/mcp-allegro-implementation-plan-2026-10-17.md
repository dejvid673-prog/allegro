# MCP Allegro — plan implementacji w etapach, 2026-10-17

**Status: PROPOSED, awaiting design/implementation approval.** Nie oznacza gotowego adaptera Allegro. Plan odnosi się do [proponowanej architektury](mcp-allegro-business-operator-proposal-2026-10-17.md) i [audytu historycznego MCP](../../audit/legacy-allegro-mcp-2026-10-17.md).

## Kolejność prac

### Sprint 0 — odzyskanie i decyzje (P0)
- [x] Zweryfikować `allegro`/ `7dejv-mcp`/ `mcp` + historyczny README Allegro 1.0 i QA; zapisać ograniczenia.
- [x] Potwierdzić oficjalne endpointy WzA, ofert i ograniczenia API konkurencji.
- [x] Spisać przepływy narzędzi, granice uprawnień i kontrakty.
- [ ] Uzyskać review dokumentu architektury i wybór runtime, głównego ownera produktu/stocku i dostaw.
- [ ] Odszukać oryginalny pełny ZIP Allegro MCP 1.0/v0.10 i zrobić **separate source/security audit**; bez tego nie kopiować kodu.
- [ ] Zweryfikować stan `2026-10-17` OpenAPI w osobnym PR po pełnym schema/media diff; ostatni HEAD katalogu jest z 20.08.

### Sprint 1 — offline preflight bez konta Allegro (P0)
Czysty Python moduł `allegro_domain`, żadnych tokenów i sieci; dopiero zaakceptowaną fasadę opublikować jako nowe typed tools MCP.

- [ ] `audit_shipment_plan(order_summary, packing_plan, shipping_profiles)`: `PASS/HUMAN_REQUIRED/BLOCK`, kody `MISSING_WEIGHT`, `WRONG_PARCEL_COUNT`, `MIXED_CHALK_LIQUID`, `UNAPPROVED_SERVICE`, `PALLET_COD_MISMATCH`, `LABEL_NOT_HANDED_OVER`.
- [ ] `audit_cost_snapshot(cost_model)`: walidacja kompletności pól `KNOWN/ZERO_CONFIRMED/NOT_APPLICABLE/UNKNOWN`, NET/GROSS/VAT, marża jako `Decimal`, stop dla `UNKNOWN`.
- [ ] `compare_assortment_snapshot(offers, product_master)`: wskazuje duplicate/sku/EAN, price/stock drift, błędny stan; nie wykonuje write.
- [ ] Testy braku danych, niepełnej paczki, 4 baniek (2+2), >4 baniek (HUMAN_REQUIRED), 24/25 kg i przekroczenia limitów, PALLET COD, nieznany VAT, zero vs UNKNOWN, cross-account identyfikatory.
- [ ] Etykiety statusów testów: unit vs integration vs end-to-end; workflow GitHub sprawdza pełne testy i stdio subprocess, a nie wyłącznie `Client(mcp)`.
- **Bramka:** wszystkie offline testy PASS, żaden tool nie może pobrać sekretu i żaden nie wywołuje HTTP.

### Sprint 2 — własny bezpieczny API client READ (P0)
- [ ] Wybrać `connectionId` registry, storage sekretów, obsługę scopes i wielu kont; nigdy token jako input toola.
- [ ] OAuth Device/Authorization Code zgodny z aktualnymi poradnikami; atomowa rotacja, 401 single refresh, 429 Retry-After, timeout/error redaction, poprawna wersja Accept i User-Agent.
- [ ] Mocked/contract tests `GET /me`, `GET /sale/offers`, `GET /sale/product-offers/{offerId}`, `GET /order/checkout-forms`, `GET /order/events`.
- [ ] Sandbox user approval + test live read only, kontrola identyfikacji sellerId, marketplace, tenant isolation.
- **Bramka:** kod klienta działa bez MCP; dokładne dowody sandbox GET, brak PII i cross-account leakage.

### Sprint 3 — fulfillment READ / audyt (P0)
- [ ] Import profile shipping/limity per usługa; `GET /shipment-management/delivery-proposals/{orderId}`, statusy command i shipment tracking; od 29.10.2026 `packages.transportingInfo`.
- [ ] Mapping order→1..N parcel, statusy `LABEL_CREATED` vs `HANDED_OVER`, monitoring first scan, COD and pallet exception.
- [ ] Operacja `audit_order_shipping` z weryfikowalnymi findings, timestamps i podpięciem do zamówień; bez pobierania PDF etykiet do AI.
- **Bramka:** realny audyt zamówienia na Sandbox + testy awarii/duplikacji + ręczne potwierdzenie procesów.

### Sprint 4 — ekonomia i katalog (P0/P1)
- [ ] Ustalić owner `ProductMaster` i stock; eksport i mapowanie SKU/GTIN dla wszystkich kont.
- [ ] Uzyskać cenę zakupu z VAT basis, rzeczywiste shipping/Smart, komisje, Ads i zwroty. Dla produktów kreda 24/25/30 kg testy wagi po zapakowaniu.
- [ ] Raport rentowności kanał×SKU×konto×metoda dostawy; kontrola brakujących kosztów i porównanie z rozliczeniami `GET /billing/billing-entries`.
- [ ] Neutralny `OfferTemplate` i compliance preflight; wersjonowane produkty i kategorie.
- **Bramka:** różnice kosztów < zaakceptowana tolerancja na rzeczywistych rozliczeniach; brak UNKNOWN w przypadkach dopuszczonych do propozycji ceny.

### Sprint 5 — kontrolowany WRITE (P1, AFTER approvals)
- [ ] Rejestrowanie jednorazowego approval snapshotu (actor, seller connection, order/offer, version, amount, expiry, hash).
- [ ] Jeden zatwierdzony test `POST /shipment-management/shipments/create-commands` na Sandbox i status reconciliation/label — bez duplikatu po timeout.
- [ ] `POST /sale/product-offers` jako **szkic**, bez publikowania; walidacja katalog/GPSR/CLP/AI i duplikatów.
- [ ] `PATCH /sale/product-offers/{offerId}` wyłącznie cena albo stock w allowliście, expected-state check + readback. Publikacja i ending osobnymi gates.
- [ ] Realne nadanie, wypisane etykiety, promocje i masowe działania NIE wchodzą do pierwszego testu WRITE.
- **Bramka:** oddzielna zgoda na każdy typ operacji i deduplikowany ledger; sandbox evidence; plan recovery.

### Sprint 6 — legalna analiza rynku (P1)
- [ ] Udokumentować licencję/warunki źródła market dataset; `GET /offers/listing` nie jest aktualnie dostępny.
- [ ] Ręczny import zatwierdzonych ofert konkurencji, EAN/masa/sztuki/metody/wysyłka/marketplace, aktualność źródła.
- [ ] Match confidence + unit-price, shipping-inclusive price, alert konkurencyjny jako raport uruchamiany ręcznie.
- [ ] Integracja z kalkulatorem marży, bez automatycznego repricing na podstawie niepewnych danych.
- **Bramka:** audyt źródła, prawo do użycia, test antymanipulacyjny, potwierdzenie użytkownika.

## Komplet minimalnych testów regresji

| ID | Sytuacja | Oczekiwany wynik |
|---|---|---|
| SHIP-001 | 5 worków kredy, 4 paczki | `BLOCK/WRONG_PARCEL_COUNT` |
| SHIP-002 | kreda i bańka 5 L w jednej paczce | `BLOCK/MIXED_CHALK_LIQUID` |
| SHIP-003 | 4 bańki 5 L zapakowane jako 3+1 | ostrzeżenie/human review, preferowane 2+2 |
| SHIP-004 | >4 bańki 5 L bez zaakceptowanego algorytmu | `HUMAN_REQUIRED` |
| SHIP-005 | produkt 25 kg bez masy opakowania, metoda limit 25 kg | `HUMAN_REQUIRED`, brak etykiety |
| SHIP-006 | paleta pobraniowa, przewoźnik nie obsługuje COD | `BLOCK` |
| SHIP-007 | etykieta utworzona, brak skanu | nie oznaczać `HANDED_OVER` |
| SHIP-008 | timeout po POST, ponowne żądanie tego samego zamówienia | reconcile, **zero blind retries** |
| COST-001 | dowolny wymagany koszt UNKNOWN | `BLOCK`; nie obliczać price floor |
| COST-002 | status ZERO_CONFIRMED bez dowodu | `BLOCK` |
| COST-003 | koszt brutto zmieszany z netto, brak VAT | `BLOCK` |
| COST-004 | doliczona druga paczka + Smart/Ads | marża uwzględnia oba koszty |
| STOCK-001 | master stock różni się od ofert | raport, brak automatycznej korekty |
| OFFER-001 | duplikat tego samego nowego produktu na powiązanych kontach | `BLOCK` zależnie od bieżących reguł |
| OFFER-002 | brak GPSR/pochodzenia AI/GTIN | brak publikacji |
| AUTH-001 | actor na koncie A wybiera connection B | `CONNECTION_ACCESS_DENIED` |
| AUTH-002 | odświeżenie 401 równoczesne z drugim requestem | jednokrotna rotacja, brak wycieku |
| API-001 | WzA 202 command IN_PROGRESS i Retry-After | poll, brak fałszywego sukcesu |
| MARKET-001 | źródło `/offers/listing` bez uprawnienia | `SOURCE_UNAVAILABLE`, żadnego „scrape by surprise” |

## Operacyjny podział etapów

- **Nowy MCP jest małym interfejsem**; domena i klient Allegro pozostają testowalne bez AI i innego MCP SDK.
- **Rozwijamy tylko na repo GitHub** dopóki lokalny PC jest wyłączony: source, test fixtures, CI, audyt; tajne dane i ręczne produkcyjne testy na późniejszym etapie.
- **Żadne zaplanowane workflow handlowe** nie są uruchamiane samodzielnie. GitHub Actions służy wyłącznie CI i radarowi publicznej dokumentacji.
- Pull requests zamiast bezpośrednich modyfikacji głównej gałęzi; po merge potwierdzić CI main. Ścieżki zależne od właściciela produktu, źródła rynku i sekretów mają status BLOCKED, a nie PASS.
