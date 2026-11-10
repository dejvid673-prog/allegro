# Allegro READ -> bezpieczna projekcja danych dla agenta (2026-11-10)

**Status: IMPLEMENTED + MOCK TESTED. Produkcyjny runtime i tożsamość kont NIEZWERYFIKOWANE.**

## Cel
Agent 7DEJV analizuje oferty i zamówienia bez przesyłania do modelu surowych checkout forms, danych kupujących, adresów, telefonów, e-maili, faktur i wiadomości. Zasada: AI dostaje tylko pola potrzebne do zadania; pełne dane pozostają w autoryzowanej domenie backendu.

## Wykorzystane istniejące komponenty
- `allegro_api/read_client.py`: typowany klient GET z allowlistą endpointów, scope, limitami i sanitacją błędów.
- `allegro_api/device_oauth.py`: wyłącznie pojedyncze kroki Device OAuth i refresh; bez przechowywania tokenów.
- `allegro_mcp/server.py`: nadal tylko offline; nie modyfikowano jego ekspozycji narzędzi.

## Nowe komponenty
- `allegro_api/agent_projection.py`: czyste funkcje `project_offer`, `project_offers_page`, `project_order`, `project_orders_page`.
- `allegro_api/safe_read_service.py`: `SafeAllegroReadService`, cienka warstwa `client -> ACL -> verified seller binding -> allowlisted projection`. Domyślnie BRAK zweryfikowanych kont, więc odmawia dostępu przed odczytem tokenu. Akceptuje tylko tożsamość uwierzytelnioną przez zaufany backend; **nie wyprowadzać `authenticated_actor` ani `verified_sellers` z argumentów LLM/MCP**.

## Zakres projekcji
- Oferta: ID, tytuł, sygnatura/SKU, kategoria, status publikacji, cena brutto, dostępny i sprzedany zapas. Brak ceny pozostaje `null`.
- Zamówienie: ID, status, status realizacji, data aktualizacji, typ płatności, jawna kwota dostawy i do zapłaty, pozycje (ID, oferta, SKU, ilość, cena wyjściowa).
- Zawsze wykluczone: `buyer`, `invoice`, `messageToSeller`, adresy/telefony, dostawca płatności, szczegóły dostawy i dowolne pozostałe pola surowego API.
- Maksymalnie 100 rekordów strony i 100 pozycji zamówienia. Zduplikowane identyfikatory blokują projekcję; walidacja pól odrzuca nieprawidłowe wartości i nigdy nie wypisuje wartości z odpowiedzi w błędzie.
- `data_complete` oznacza kompletność pól tej **uproszczonej projekcji**, NIE kompletną rentowność, księgowość ani potwierdzenie płatności. Rzeczywiste prowizje, koszty transportu, rabaty, zwroty i faktury wymagają osobnych źródeł.

## Krytyczne bramki przed MCP/live
1. Zweryfikować identyfikator i uprawnienia sprzedawcy w każdym połączeniu; aktualne `seller_id` w `ConnectionRegistry` to deklaracja lokalna, nie dowód.
2. Wdrożyć chroniony token broker z trwałym, atomowym zapisem rotowanego refresh tokenu w magazynie sekretów. Bez `access_token`/`refresh_token` w modelu, parametrach tooli i logach.
3. Pozyskać osobną autoryzację klienta MCP -> serwer 7DEJV, niezależną od OAuth Allegro -> serwer.
4. Uwierzytelniony backend podaje `authenticated_actor` i `verified_sellers`; użytkownik ani model nie mogą ich deklarować.
5. Przeprowadzić autoryzowany test w Sandbox i oddzielny kontrolowany odczyt produkcyjny, z walidacją scope i identyfikatora konta.
6. Dopiero po pozytywnych testach udostępnić ograniczone projekcje jako narzędzia MCP; **nigdy** bezpośrednio surowe odpowiedzi klientów.
7. Bez dopuszczonych uprawnień do zapisu; żadnych automatycznych zmian cen i ofert w tym etapie.

## Testy
`python -m unittest discover -s tests -v` — testy projekcji, duplikatów, niekompletnych kosztów, braków, niesanitowanych danych, izolacji kont oraz istniejących operacji offline.

`python -m scripts.smoke_mcp` — nadal **dokładnie dziewięć narzędzi offline**, bez dodatkowej ekspozycji danych kont.

## Źródła weryfikowane 2026-11-10
- [OAuth / Device flow, scope, token refresh](https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR)
- [Allegro API — offers GET](https://developer.allegro.pl/tutorials/jak-zarzadzac-ofertami-7GzB2L37ase)
- [Allegro REST API / checkoutForms](https://developer.allegro.pl/documentation/)
