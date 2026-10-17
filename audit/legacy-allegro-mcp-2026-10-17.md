# Audyt starego Allegro MCP i istniejących repozytoriów — 2026-10-17

**Status: AUDIT / VERIFIED FACTS + OPEN GAPS, nie certyfikat produkcyjny.** Zakres: odzyskanie założeń starego Allegro MCP, analiza bieżących repozytoriów i identyfikacja elementów potrzebnych do prawdziwej obsługi handlu. Nie testowano połączeń z prywatnymi kontami ani operacji produkcyjnych. Audyt źródłowy dotyczy stanu publicznych i dostępnych dla właściciela repozytoriów w dniu 2026-10-17.

## 1. Co faktycznie przeanalizowano

| Materiał | Dostępność | Fakty i ograniczenia |
|---|---|---|
| Wcześniejszy dokument **Allegro MCP 1.0 / README(6).md** z Library ChatGPT | READ / tekst | TypeScript, stdio, Device Flow, odczyt orders/offers/products/shipments, write disabled by default; instrukcja `npm run auth` i testowania Inspector. README to deklaracja, nie dowód uruchomienia. |
| **QA_STATUS.md** starego kandydata v0.10 | READ / tekst | Udokumentowana naprawa błędu startu `serveStdio()`, zamysł atomic token file, single refresh, expected-state, dry-run/confirmation i brak retry write. QA jednoznacznie: **PRE-LOGIN/PRE-SANDBOX** i `npm ci && npm run check` **NIE POTWIERDZONE PASS**. |
| Pełne stare ZIP-y Allegro MCP | **NOT LOCATED IN THIS AUDIT** | Nie audytowano historycznych plików `src/`, lockfile, działania OAuth i bezpieczeństwa starych archiwów. Nie twierdzić, że stary kod jest naprawiony czy gotowy do bezpośredniego importu. |
| `dejvid673-prog/mcp` gałąź `main` | READ / repo | Node 24.20, TypeScript, MCP v2, lokalny HTTP loopback, Docker, testy fundamentu. README deklaruje **brak biznesowych tools i autoryzacji**; to nie jest stary integrator Allegro. |
| `dejvid673-prog/mcp` gałąź `feature/erli-write-mvp` | READ / repo i wcześniejsze CI | ERLI client, domain, transport, policy; CI poprzednio wykazał 59 jednostkowych testów i Docker PASS. Oddzielna implementacja ERLI, **nie** Allegro; nie łączyć nieaudytowanych gałęzi. W logu zależności npm wcześniejszego builda zidentyfikowano 1 HIGH + 1 MODERATE — potrzeba precyzyjnego `npm audit`; nie nadpisywać deklaracji o Docker Scout. |
| `dejvid673-prog/7dejv-mcp` `main` | READ / repo | Kanoniczne założenia architektury integracyjnej i `SHIPPING_RULES.md` o statusie **DESIGNED**, nie VERIFIED; w `SOURCES.md` jest preferencja niezależnych typed clients i domain services oraz ADR o ERLI. |
| `dejvid673-prog/allegro` `main` | READ + GitHub Actions | Repo domenowe Allegro, generator OpenAPI, reguły ofert/transportu/kosztów i nowy MCP tylko do odczytu lokalnej dokumentacji. PR #2 scalony 2026-10-17, 10 testów jednostkowych + in-memory MCP smoke PASS. Brak realnego adaptera API Allegro. |
| `dejvid673-prog/7dejv-staw-expert` `main` | struktura repo | Research produktów/kosztów/konkurencji. Nie jest magazynem transakcyjnym ani dowodem aktualnego stocku. |

Źródła GitHub: https://github.com/dejvid673-prog/allegro ; https://github.com/dejvid673-prog/7dejv-mcp ; https://github.com/dejvid673-prog/mcp ; https://github.com/dejvid673-prog/7dejv-staw-expert .

## 2. Audyt starego MCP 1.0 — co odzyskać, co poprawić

| Obszar | Obserwacja | Ocena / wymagane działanie |
|---|---|---|
| Narzędzia READ | Zamówienia, oferty, produkty, kategorie, zdarzenia, przewoźnicy i przesyłki były w dokumentacji README. | **REUSE AS REQUIREMENTS**. Odtworzyć API klienta z aktualnego Swaggera, nie kopiować niesprawdzonego kodu. |
| Logowanie OAuth | Device Flow, odświeżanie i lokalny `.tokens.json`. | **HOLD**. Wymagane testy sandbox, atomowy store w sejfie, odnowienie i brak tokenów w logach, wielokontowość bez pomylenia sellerId. |
| `ALLEGRO_ENABLE_WRITES` | Globalny przełącznik zapisu z wersji 1.0. | **REJECT AS SOLE GATE**. Serwerowy per-actor/per-connection/per-operation allowlist + expected state + jawne zatwierdzenie konkretnej propozycji + identyfikator operacji. |
| `allegro_patch_offer` / `allegro_create_product_offer` z dowolnym JSON | README zachęcało do przekazania pełnego payloadu Allegro. | **REJECT FOR AI TOOLS**. Typed business commands, allowlisted fields, osobne operacje ceny, stocku i draftu; nie wystawiać surowego HTTP/path/host/sekretu jako argumentu. |
| Reconciliation | Raport QA wspomina o UUID i potwierdzaniu wyników oraz zakazie retry POST/PATCH/DELETE. | **KEEP / REINFORCE**. Persistent ledger/outbox oraz odczyt finalnego statusu zewnętrznego, bez „zadziałało, bo HTTP=202”. |
| Transport stdio | Stary bootstrap miał udokumentowany błąd `serveStdio`. | **HOLD** bez pełnego artefaktu. Nowy Python MCP ma in-memory test, ale nie dowodzi interoperacyjności z klientem desktop na Windows. |
| Składanie paczek | Stary projekt zakładał tools zamówienia/przesyłki, ale nie widzę w materiałach dowodu end-to-end WzA. | **NOT IMPLEMENTED/VERIFIED**. To osobny proces biznesowy, nie tylko POST endpointu. |
| Finanse i konkurencja | W starym README brak potwierdzonego modelu kosztów oraz legalnej ścieżki importu rynku. | **NEW DOMAIN SERVICES**. Bez nich nie da się bezpiecznie sterować cenami. |

Nieznane: kompletność poprzedniego `package-lock.json`, realny OAuth, stan danych zapisanych na starym komputerze, integralność ZIP oraz współpraca z klientem ChatGPT/Inspector. **Nie raportować PASS tam, gdzie jest UNKNOWN**.

## 3. Luka obecnego MCP Allegro

Obecny `allegro_mcp/server.py` eksponuje dokładnie:
- `allegro_catalog_status`
- `allegro_find_read_endpoints`
- `allegro_get_read_endpoint`

Te narzędzia czytają `sources/generated/*.json`, nie posiadają tokenów, nie wywołują `https://api.allegro.pl`. Obecny katalog to **2026-08-20**; oficjalny Swagger pobrany 2026-10-17 zawiera 270 operacji, a przeglądowy diff stwierdził 3 nowe/0 usuniętych/13 zmienionych w indeksowanych polach. **Schema compatibility NOT VERIFIED**: https://github.com/dejvid673-prog/allegro/blob/main/audit/openapi-drift-2026-10-17.md .

**Krytyczny błąd kategorii:** 10 PASS w CI dowodzi jedynie poprawności lokalnych funkcji/protokołu testowanego w pamięci. Nie dowodzi OAuth, wydrukowania etykiety, działania stdio na Windows, synchronizacji kont ani marż.

## 4. Luki funkcjonalne i priorytety

| Obszar użytkownika | Najważniejsze źródło/operacja | Bieżący status | Priorytet |
|---|---|---|---|
| Audyt zamówień i przesyłek | `GET /order/checkout-forms`; `GET /order/events`; WzA `GET /shipment-management/delivery-proposals/{orderId}`; status paczek i zdarzenia | **DESIGNED** w docs, brak live adaptera | P0 |
| Nadawanie paczek / etykiety | `POST /shipment-management/shipments/create-commands` → odczyt statusu → etykieta → pierwszy skan | **NOT IMPLEMENTED**. WRITE wymaga autoryzacji, approval i ledger | P0 po odczycie |
| Reguły pakowania | `7dejv-mcp/SHIPPING_RULES.md` + lokalny `shipping-profile.schema.json` | **DESIGNED / UNVERIFIED** (braki limitów usług i wag) | P0 |
| Koszt jednostkowy i marża | `templates/cost-model.schema.json`, billing, cenniki, invoice/import | Schemat **DESIGNED**, brak uzgodnionego źródła wszystkich kwot | P0 |
| Asortyment i stock | `GET /sale/offers`, `GET /sale/product-offers/{offerId}`, Product Master | Read-only tylko dokumentacja, stock master **UNASSIGNED** | P0/P1 |
| Nowe produkty / oferty | `GET /sale/products`, kategorie i parametry; `POST /sale/product-offers` (szkic) | Szablon **DESIGNED**; compliance/duplicates gate | P1 |
| Sterowanie cenami | ceny/stock odczyt, `PATCH /sale/product-offers/{offerId}` lub command po approval | Brak runtime; globalny przełącznik write nie jest wystarczający | P1 |
| Skany konkurencji | publiczne źródło danych z ofert i kosztów dostawy, EAN/GTIN | **BLOCKED by source**: ogólny `GET /offers/listing` nie jest już dostępny w Allegro REST API | P1 research + legalne źródła |
| Ads i akcje | raport Ads, `GET /billing/billing-entries`, odpowiednie zasoby promocji | Brak uniwersalnego API Ads w obecnym Swaggerze — wymagany import raportu | P2 |
| Kontrola wielu kont | mapping `connectionId`, sellerId, accounts / source SKU | Brak rejestru uprawnień; ryzyko pomylenia kont | P0 bezpieczeństwo |

**Oficjalny kontekst:** https://developer.allegro.pl/tutorials/jak-zarzadzac-przesylkami-przez-wysylam-z-allegro-LRVjK7K21sY ;
https://developer.allegro.pl/tutorials/jak-zarzadzac-ofertami-7GzB2L37ase ;
https://developer.allegro.pl/tutorials/jak-jednym-requestem-wystawic-oferte-powiazana-z-produktem-D7Kj9gw4xFA ;
https://developer.allegro.pl/tutorials/lista-metod-rest-api-allegro-yPyaj0wG3C4 (uwaga na niedostępne `GET /offers/listing`).

## 5. Reguły pakowania znalezione w poprzednim projekcie

Z `dejvid673-prog/7dejv-mcp/SHIPPING_RULES.md` — **DESIGNED, not VERIFICATION**:

- `PACK-ALG-001`: 1 worek kredy = 1 paczka; nie łącz worków automatycznie.
- `PACK-ALG-002`: nie łącz kredy z bańkami 5 L.
- `PACK-ALG-003`: do 3 baniek w paczce; 4 bańki = 2+2; dla **>4 baniek** dokładny algorytm niezatwierdzony → `HUMAN_REQUIRED`. Nie dobierać metod kurierskich przed potwierdzeniem wagi/brutto i wymiarów.
- `PALLET-003`: paleta pobraniowa bez usługi COD = `CRITICAL/BLOCK`.
- Nie tworzyć etykiety, gdy brakuje statusu `READY_FOR_PROCESSING`, bezpiecznego planu pakowania lub danych dostawy; w razie `UNKNOWN` → `HUMAN_REQUIRED`.
- `LABEL_CREATED` to nie `HANDED_OVER`. Wysyłkę uznać za przekazaną dopiero po zdarzeniu pierwszego skanu/protokołu zgodnie z usługą.

## 6. Najważniejsze ryzyka systemowe

- **CRITICAL / AUTH:** `client → MCP` i `MCP → Allegro` to dwie oddzielne granice; połączenie przez stdio chroni lokalne uruchomienie, ale nie zabezpiecza zdalnego endpointu. Nie wprowadzać remote Streamable HTTP bez inbound auth.
- **CRITICAL / IDENTITY:** wiele kont = server-side `connectionId` i mapowanie actor→accounts; każda operacja musi rewalidować konto i uprawnienia.
- **CRITICAL / IDENTITY OF PRODUCT:** nie zakładać niezależności „różnych” kont dla limitów duplikatów i zgodności regulaminowej. Kontrolować wszystkie powiązane konta.
- **HIGH / SHIPMENT:** command idempotency i status command to dwa różne etapy. Nie powtarzać ślepo POST w razie timeoutu. Reconciliation przed ponowieniem.
- **HIGH / PRICING:** używać `Decimal`, jawnej podstawy NET/GROSS, źródła VAT i stawek oraz kompletności kosztów. `UNKNOWN` nie jest zerem; marża nie może być deklarowana przy brakujących opłatach Smart/Ads/wysyłce.
- **HIGH / INVENTORY:** jeden system master dla stocku/zakupu/ceny; dashboard i MCP nie mogą zastępować magazynu.
- **HIGH / MARKET:** zwykły token Allegro Seller OAuth nie przywraca wyłączonego listing search dla konkurencji; nie obiecywać automatycznego skanowania rynku bez potwierdzonego zgodnego źródła.
- **HIGH / OPERATIONS:** wszystkie działania AI uruchamiane ręcznie na żądanie operatora; nowe procesy handlowe nie dostają autonomicznego schedulera bez nowej jawnej decyzji.
- **MEDIUM / GOVERNANCE:** w `allegro/agents/AGENTS_allegro_logistics.md` i `AGENTS_allegro_shipping_auditor.md` pozostały stare wskaźniki do `7dejv-skills-prompts`. Zasady globalne obecnie w `7dejv-agent-os`; profil specjalistyczny wymaga sprawdzenia lokalizacji i migracji, a nie zgadywania ścieżki.
- **MEDIUM / TEST COVERAGE:** brak smoke realnego Windows/Inspector, token lifecycle, 401/429, 202+Retry-After, awarii sieci i podwójnych kliknięć/nadań, różnic Sandbox–production.

## 7. Wnioski audytowe

**DECISION PROPOSAL:** zachować repo `allegro` jako źródło implementacji domeny Allegro i bieżącego Python MCP offline; na potrzeby długofalowe warstwy biznesowe muszą być transport/SDK-neutral. `7dejv-mcp` pozostaje referencją architektury integracyjnej; `mcp` dostarcza oddzielny runtime TypeScript i ERLI. **Nie łączyć bezpośrednio repozytoriów ani kodu TypeScript/Python bez decyzji o runtime, licencji i granicach danych.**

Nie odtwarzamy starego globalnego `ALLEGRO_ENABLE_WRITES` i `raw PATCH` jako narzędzi AI. Idziemy po kolei: audyt zamówień i pakowania → koszty → read-only klient Allegro → drafty i kontrolowane operacje → transakcje po approval.

Przed nadaniem statusu VERIFIED potrzebny jest kod, CI na wskazanym SHA, testy Sandbox i kontrolowany test użyteczności z człowiekiem. Szczegóły: [projekt](../docs/07-architecture/mcp-allegro-business-operator-proposal-2026-10-17.md) i [plan](../docs/07-architecture/mcp-allegro-implementation-plan-2026-10-17.md).
