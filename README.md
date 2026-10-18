# Allegro Integration Knowledge Base

Repozytorium jest źródłem wiedzy i specyfikacją budowy bezpiecznego operatora Allegro dla RaFish / HelpFish / StawExpert. Łączy oficjalną dokumentację Allegro, generowany katalog API, reguły ofert, procesy operacyjne oraz kontrakty danych dla przyszłego agenta.

Stan źródeł i API zweryfikowano **2026-08-20**. Allegro zmienia API, kategorie, parametry i regulaminy, dlatego dokumentacja statyczna nie zastępuje odczytu aktualnych danych z API.

## Zacznij tutaj

1. [START_HERE.md](START_HERE.md) — mapa dokumentacji i kolejność wdrożenia.
2. [AGENTS.md](AGENTS.md) — obowiązkowe zasady dla Codex i agentów AI.
3. [BUSINESS_RULES.md](BUSINESS_RULES.md) — jakość sprzedaży, pełne koszty i bramy publikacji.
4. [Źródło prawdy](docs/01-sources/source-of-truth.md) — hierarchia źródeł i rozstrzyganie sprzeczności.
5. [Macierz wysyłek RaFish](docs/06-shipments/rafish-shipping-matrix.md) — dobór przewoźnika do asortymentu.
6. [Smart i cenniki](docs/06-shipments/smart-and-shipping-rates.md) — progi, wkład sprzedawcy i stawki.
7. [Jakość sprzedaży](docs/08-operations/sales-quality-kpis.md) — KPI, alerty i procedury.
8. [Architektura operatora](docs/07-architecture/allegro-operator.md) — moduły i odpowiedzialności.
9. [Roadmapa](ROADMAP.md) — etapy od dokumentacji do kontrolowanej automatyzacji.

## Zakres

- OAuth 2.0, zakresy dostępu, tokeny, limity i obsługa błędów;
- kompletny katalog endpointów generowany z oficjalnego Swagger/OpenAPI;
- tworzenie nowej oferty z produktu, szablonu lub starej oferty;
- audyt aktywności, ceny, zapasu, parametrów i braków wymaganych przez Allegro;
- reguły tytułów, opisów, zdjęć, duplikatów, GPSR i oznaczania obrazów AI;
- oddzielne profile dla chemii stawowej, karm i żywych ryb;
- zamówienia, anulowania, zwroty, statusy, przesyłki i etykiety;
- Smart, cenniki, ciężkie/długie/specjalne paczki i macierz asortymentu RaFish;
- Top oferta, czynniki popularności, Allegro Ads, wyróżnienia i marża po reklamie;
- obowiązkowy model pełnych kosztów oraz jakość sprzedaży jako nadrzędny KPI;
- model danych, ślad audytowy, idempotencja, zatwierdzenia człowieka i procedury awaryjne;
- projekt narzędzi MCP/ChatGPT, które mogą później stanowić „wtyczkę” do obsługi Allegro.

## Najważniejsza zasada

Agent może przygotować i sprawdzić zmianę, ale operacje o skutkach biznesowych lub prawnych wymagają zatwierdzenia człowieka, dopóki konkretny typ operacji nie przejdzie testów i nie zostanie jawnie dopuszczony do automatyzacji.

## Odświeżenie katalogu API

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_api_catalog.py
python scripts/validate_repository.py
python scripts/check_openapi_freshness.py
```

Skrypt pobiera `https://developer.allegro.pl/swagger.yaml`, zapisuje metadane i generuje katalog endpointów. Pełny Swagger nie jest wersjonowany — źródłem kontraktu jest zawsze oficjalny plik Allegro.

Migawka z 2026-08-20 obejmuje **201 ścieżek, 267 operacji i 967 schematów**. Jej SHA-256 znajduje się w `sources/generated/openapi-metadata.json`.

Workflow GitHub waliduje repo przy pull requeście/pushu, a codziennie porównuje hash oficjalnego Swaggera z migawką. Zmiana wymaga wygenerowania katalogu i przeglądu różnic — workflow nie modyfikuje repo automatycznie.

## MCP Allegro — start wersji offline (2026-10-17)

Uruchamialny **lokalny** serwer MCP z trzema narzędziami tylko do odczytu zapisanej dokumentacji API: `allegro_catalog_status`, `allegro_find_read_endpoints`, `allegro_get_read_endpoint`. Nie ma tokenów, dostępu do konta ani możliwości zmian ofert; obecna migawka OpenAPI wciąż pochodzi z 2026-08-20.

- [Fundament MCP, granice bezpieczeństwa, testy](docs/07-architecture/mcp-allegro-foundation.md)
- [Radar zmian API — 17.10.2026](docs/09-change-management/mcp-allegro-radar-2026-10-17.md)
- [Audyt aktualnego OpenAPI — 270 operacji, 13 różnic (HOLD)](audit/openapi-drift-2026-10-17.md)
- [Serwer MCP — kod](allegro_mcp/server.py)

### Dwa narzędzia biznesowe offline (18.10.2026)

Oprócz 3 narzędzi katalogowych serwer udostępnia teraz **2 narzędzia lokalnego preflightu**:
- `allegro_shipment_preflight_offline(order, parcels)` — kontrola przydziału towarów do paczek, reguł kredy i baniek 5 L, COD, masy i statusu nadania;
- `allegro_cost_preflight_offline(cost_snapshot)` — weryfikacja kompletności danych kosztowych i kalkulacja marży netto (Decimal) wyłącznie z jawnie dostarczonych danych.

Dokumentacja: [Offline business preflight](docs/07-architecture/offline-business-preflight-2026-10-18.md). **Brak połączenia z Allegro, OAuth, faktycznego nadawania, kontroli realnych cen lub rozliczeń**; PASS oznacza jedynie sprawdzenie wprowadzonego planu. Dotychczasowa migawka Swagger nadal wymaga przeglądu.

- [Katalog źródeł](sources/registry.json) (zarejestrowane nowe komunikaty i oficjalna specyfikacja MCP)

```bash
python -m pip install -r requirements-mcp.txt
python -m unittest discover -s tests -v
python -m scripts.smoke_mcp
python -m allegro_mcp.server
```

Wymagane Python 3.11+ i SDK przypięte do wersji `2.3.0`. Polecenie uruchomienia serwera używa standardowego MCP `stdio` (klient musi uruchomić proces). **Nie wystawiać po HTTP bez uwierzytelnienia MCP i Allegro.** Testy GitHub Actions sprawdzają protokół bez połączenia z kontem.

Uwaga: powyższa aktualizacja dokumentów i źródeł z 2026-10-17 **nie oznacza**, że generowany katalog Swagger został odświeżony; przed integracją live niezbędny jest kontrolowany diff i PR.

## Klient Allegro REST API — tylko READ, jeszcze bez logowania (18.10.2026)

Rozpoczęto rzeczywisty adapter API: [allegro_api/read_client.py](allegro_api/read_client.py). Kod implementuje sześć stałych operacji GET dla ofert, zamówień, zdarzeń oraz propozycji dostaw. Konta są rozdzielone przez serwerowy rejestr połączeń i uprawnienia aktorów; backend obsługuje limity, błędy i maskowanie tokenów.

**UWAGA: nie jest to jeszcze połączenie z kontem Allegro.** Nie ma OAuth, magazynu tokenów, autoryzowanego klienta MCP ani realnych testów Sandbox. HTTP transport jest gotowy jako moduł biblioteczny, ale nikt go nie uruchomił z rzeczywistym kontem. W dalszym ciągu MCP wystawia **5 narzędzi offline**.

[Dokumentacja i testy adaptera READ](docs/07-architecture/allegro-read-client-2026-10-18.md).

## Kierunek: pełny MCP operator sprzedaży (audyt 17.10.2026)

Na podstawie wcześniejszego Allegro MCP 1.0 oraz repozytoriów `7dejv-mcp` i `mcp` opracowano **audyt, propozycję architektury i plan**, które **nie są jeszcze implementacją** obsługi sprzedawcy.

- [Audyt wcześniejszego Allegro MCP i luk](audit/legacy-allegro-mcp-2026-10-17.md)
- [PROPOSED: operator przesyłek, kosztów, produktów, cen i konkurencji](docs/07-architecture/mcp-allegro-business-operator-proposal-2026-10-17.md)
- [PROPOSED: plan wdrożenia i testy akceptacyjne](docs/07-architecture/mcp-allegro-implementation-plan-2026-10-17.md)

Kolejność: audyt przesyłek / offline packing preflight → kosztorys → OAuth READ → rzeczywisty audyt WzA → kontrolowane nadawanie, drafty i zmiany cen → analiza rynku z legalnego źródła. Obecny serwer MCP ma **3 narzędzia dokumentacyjne i 2 narzędzia biznesowego audytu offline**; klient Allegro READ nie jest jeszcze udostępniony przez MCP. Konkurencyjny `GET /offers/listing` nie jest dostępny w zwykłym API Allegro; nie zakładać tego źródła.

## Czego repozytorium nie zawiera

- Client ID, Client Secret, access tokenów i refresh tokenów;
- eksportów danych kupujących ani pełnych payloadów produkcyjnych;
- danych logowania do Allegro, PrestaShop, BaseLinkera lub przewoźników;
- zgody na samodzielne publikowanie, kończenie ofert, zmianę cen lub nadawanie przesyłek.
