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

## Czego repozytorium nie zawiera

- Client ID, Client Secret, access tokenów i refresh tokenów;
- eksportów danych kupujących ani pełnych payloadów produkcyjnych;
- danych logowania do Allegro, PrestaShop, BaseLinkera lub przewoźników;
- zgody na samodzielne publikowanie, kończenie ofert, zmianę cen lub nadawanie przesyłek.
