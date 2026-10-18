# Roadmapa operatora Allegro

## Etap 0 — wiedza i kontrakty (to repo)

- [x] hierarchia źródeł prawdy;
- [x] generowany katalog OpenAPI;
- [x] reguły ofert i profile ryzyka;
- [x] model danych oraz procedury;
- [x] specyfikacja szablonu oferty;
- [x] Smart, cenniki, macierz wysyłek RaFish i procedury wyjątków;
- [x] obowiązkowy model kosztów, Ads/Top oferta i KPI jakości;
- [ ] zatwierdzenie dokumentacji przez właściciela firmy.

## Etap 0.5 — MCP Allegro offline (GitHub-only)

- [x] architektura bezpiecznego MCP, źródła zmian z października 2026 i rozdział autoryzacji;
- [x] pierwsze trzy narzędzia MCP tylko do odczytu lokalnej dokumentacji;
- [x] testy jednostkowe i smoke MCP w CI — ostateczny wynik potwierdzać po PR;
- [ ] wygenerować nowy katalog OpenAPI z oficjalnego Swaggera i zaakceptować diff (poprzednia migawka: 2026-08-20);
- [ ] zaakceptować role/scope OAuth oraz bezpieczny model utrzymania sekretów poza Git;
- [ ] dopiero później: prawdziwy adapter GET Allegro i testy sandbox/read-only.

Stan: **MCP offline, nie połączony z Allegro, nie produkcyjny**.

### Audyt historycznego MCP i plan rozwoju — 2026-10-17

- [x] weryfikacja deklaracji starego Allegro MCP 1.0, raportu QA oraz repozytoriów `mcp`, `7dejv-mcp` i `allegro`;
- [x] sformalizowane wymagania: nadawanie paczek, audyt przesyłek, koszty, asortyment, draft ofert, ceny i konkurencja;
- [x] propozycja rozdzielenia MCP od typed client i domain services, status **PROPOSED / do przeglądu**;
- [x] matryca ryzyk i scenariusze akceptacyjne dla pierwszych etapów;
- [ ] review projektu, wybór runtime i źródła nadrzędnego produktu/stocku;
- [ ] implementacja offline `shipment_preflight` i `cost_audit` oraz testy, po zatwierdzeniu projektowych bramek.

Patrz: [audyt](audit/legacy-allegro-mcp-2026-10-17.md), [projekt](docs/07-architecture/mcp-allegro-business-operator-proposal-2026-10-17.md), [plan](docs/07-architecture/mcp-allegro-implementation-plan-2026-10-17.md).

## Etap 1 — klient tylko do odczytu

- OAuth i rotacja tokenów w sejfie sekretów;
- odczyt tożsamości konta i marketplace;
- pełna synchronizacja ofert oraz zdarzeń z ostatnich 24 godzin;
- odczyt brakujących parametrów i kategorii ze zmianami;
- panel: aktywne / nieaktywne / zakończone / błędne / brakujące dane;
- dziennik `Trace-Id`, opóźnienia, kody HTTP i limity.

**Bramka:** 14 dni poprawnej pracy bez zapisu do Allegro.

## Etap 2 — audyt i propozycje

- reguły tytułów, opisów, zdjęć, GPSR, CLP, pasz i AI;
- wykrywanie duplikatów na wszystkich kontrolowanych kontach;
- porównanie ceny/zapasu z systemem nadrzędnym;
- tworzenie `OfferTemplate` ze starej oferty;
- raport różnic i kolejka zatwierdzeń.

**Bramka:** minimum 100 ręcznie ocenionych raportów i znany poziom fałszywych alarmów.

## Etap 3 — kontrolowany zapis ofert

- tworzenie draftów;
- pojedyncza edycja/publikacja po zatwierdzeniu;
- śledzenie statusu operacji asynchronicznej;
- automatyczny rollback poprzez jawny plan kompensacyjny, nie przez „cofnięcie GET-em”;
- masowe operacje nadal wyłączone.

**Bramka:** dwie osoby potwierdzają zgodność 30 kolejnych publikacji.

## Etap 4 — zamówienia i nadawanie paczek

- konsument zdarzeń zamówień z deduplikacją;
- proces wyłącznie dla `READY_FOR_PROCESSING`;
- kontrola anulowań i zmian rewizji;
- propozycje dostawy, weryfikacja paczki, utworzenie przesyłki, etykieta;
- retry bez podwójnego nadania;
- dashboard wyjątków do ręcznej obsługi.
- monitoring pierwszego skanu, podjazdów, zwrotów i terminów refundacji.

**Bramka:** testy Sandbox, testy przerw sieciowych i ręczna kontrola pierwszych 50 przesyłek.

## Etap 5 — bezpieczne automatyzacje

- automatyczne wznawianie tylko ofert z allowlisty i jednoznaczną przyczyną zakończenia;
- automatyczne aktualizacje ceny/zapasu w ustalonych granicach;
- alerty o wyłączonych ofertach, wygasłych tokenach, błędach i zmianach API;
- okresowa kontrola changelogu i odświeżanie Swaggera.
- rekomendacje Ads i promocji wyłącznie na podstawie marży po wszystkich kosztach.

## Poza zakresem automatyzacji bez osobnego projektu

- decyzje prawne o dopuszczeniu produktu;
- automatyczne deklaracje AI dla zdjęć bez pochodzenia;
- zmiana producenta/osoby odpowiedzialnej GPSR bez dokumentów;
- wysyłka żywych ryb zwykłą ścieżką kurierską;
- swobodne kopiowanie ofert pomiędzy kontami powiązanymi;
- zwroty środków i zakończenie dużej liczby ofert.


### Implementacja offline preflight — 2026-10-18

- [x] Deterministyczny audyt planu pakowania i przesyłek bez API, tokenów i etykiet.
- [x] Audyt kompletności kosztów netto i marży z dokładną arytmetyką Decimal, blokada UNKNOWN.
- [x] Dwa read-only MCP tools i testy jednostkowe oraz in-memory protocol smoke w CI.
- [ ] Zweryfikowany odczyt rzeczywistych zamówień i carrier tracking; decyzja o OAuth/connectionId.
- [ ] Trwały ledger i zatwierdzenia przed jakimkolwiek nadaniem lub edycją cen.

[Kontrakt wejścia i ograniczenia](docs/07-architecture/offline-business-preflight-2026-10-18.md).


### Adapter Allegro GET — 18.10.2026

- [x] Biblioteczny klient GET-only: oferty, szczegóły ofert, zamówienia, zdarzenia i propozycje dostawy.
- [x] Rejestr połączeń dla różnych kont i środowisk; uprawnienia oraz scoped GET, bez tokenów w narzędziach MCP.
- [x] Testy fake transport + rozdzielenie kont + błędy HTTP 401/403/429/5xx i brak automatycznych retry.
- [ ] OAuth Device Flow/Authorization Code, bezpieczne tokeny, weryfikacja tożsamości konta i zakresów.
- [ ] Prawdziwe bezpieczne testy GET Sandbox z upoważnionym sprzedawcą.
- [ ] Privacy-safe projection dla danych zamówień przed publikacją do MCP.

[Kontrakt i ograniczenia klienta READ](docs/07-architecture/allegro-read-client-2026-10-18.md).
