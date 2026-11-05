# Allegro Ads — analityka rentowności i kontrakt danych

Data weryfikacji źródeł: **2026-11-05**. Status: **RESEARCHED + DESIGNED**, nie CONNECTED/TESTED. Dokument uzupełnia [ads-and-promotion.md](ads-and-promotion.md); nie zastępuje reguł [BUSINESS_RULES](../../BUSINESS_RULES.md). Konta, API i rzeczywiste kampanie STAW EXPERT **nie zostały odczytane**.

## 1. Fakty potwierdzone przez Allegro
| Fakt | Data / granica | Pierwotne źródło |
| --- | --- | --- |
| Eksport statystyk Allegro Ads jako XLSX; wymiary mogą obejmować miejsca emisji | zweryfikowano 2026-11-05 | https://help.allegro.com/pl/sell/a/jakie-statystyki-moge-sprawdzac-w-panelu-reklamowym-allegro-ads-1nPyDZo9qUe |
| Zakup w ciągu 7 dni od kliknięcia może być przypisany reklamie; sprzedaż może obejmować również inny produkt sprzedawcy | zweryfikowano 2026-11-05 | https://help.allegro.com/pl/sell/c/optymalizacja-i-rozwoj-w-allegro-ads |
| Kliknięcia/koszt zwykle szybciej niż sprzedaż, którą panel aktualizuje dziennie; bieżące dni są niepełne | zweryfikowano 2026-11-05 | ten sam dział pomocy |
| Zasoby GET /order/checkout-forms i GET /order/checkout-forms/{id} udostępniają lineItems[].allegroAds.attributed | zmiana z 2026-10-29 | https://developer.allegro.pl/news/zamowienia-dodalismy-informacje-o-atrybucji-allegro-ads-Pg8glADgbT5 |
| Kampania Express dobiera CPC automatycznie; Kampania Pro daje bardziej szczegółowe sterowanie | 2026-10 | https://help.allegro.com/pl/sell/a/teraz-jeszcze-szybciej-utworzysz-kampanie-w-panelu-allegro-ads-ZMnVlevYyH4 |
| Historia zmian kampanii/grup gromadzona od 2026-07-06, przechowywana 12 miesięcy | zweryfikowano 2026-11-05 | https://help.allegro.com/pl/sell/a/jak-dziala-historia-zmian-w-panelu-allegro-ads-LRzDdmKZ7I0 |
| Planer kampanii: frazy, konkurencja, stawki, sezonowość; limit 2000 wyszukań/mies. | zweryfikowano 2026-11-05 | https://help.allegro.com/pl/sell/a/jak-korzystac-z-planera-kampanii-b2lqkB577TE |
| UI przełącza stawki i koszt Ads netto/brutto, **nie zmienia jednak wartości sprzedaży** | zmiana komunikowana 2026-08-18 | https://help.allegro.com/pl/sell/a/wprowadzilismy-zmiany-dla-sprzedajacych-zapowiedziane-na-18-sierpnia-E7n3d4Alecb |

### Uprawnienia i ograniczenia API
Regulamin Allegro Ads (pkt 2.3 b) ogranicza dostęp do usługi Ads przez REST API do **Partnerów Technicznych i producentów/właścicieli marek**; nie oznacza automatycznego przyznania uprawnień każdemu sprzedawcy. Również regulamin programu partnerskiego od 2026-10-08 zawiera ograniczenia i warunki dostępu do API; nie zakładaj, że obecny program gwarantuje nowy dostęp agencyjny. Źródła:
- https://allegro.pl/regulaminy/regulamin-allegro-ads-a1EnOgMxWfa
- https://allegro.pl/regulaminy/regulamin-programu-partnerskiego-allegro-ads-MREKExrWqIb
- https://help.allegro.com/pl/sell/c/allegro-ads-partner

**KRYTYCZNE:** Scope `allegro:api:campaigns` opisany w publicznym tutorialu dotyczy m.in. programów/akcji Allegro i Allegro Ceny, **nie jest dowodem prawa do kampanii Ads**: https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR . Nie próbuj obchodzić dostępu przez niedokumentowane endpointy, scraping sesji czy automatyczne sterowanie interfejsem. Najpierw ustal oficjalny kontrakt i rzeczywistą autoryzację.

Pole `attributed:true` to dowód atrybucji danej pozycji, **nie** koszt kliknięcia, źródłowy campaignId, koszt pozyskania, zakres 7-dniowy ani dowód wzrostu inkrementalnego. Dla pola nieobecnego/nieznanego nie dopowiadaj `false`. Warstwa domenowa musi przechowywać status `true/false/unknown` wraz z datą odczytu oraz wersją schematu.

## 2. Źródła danych i poziomy szczegółowości
| Źródło | Granularność | Klucz / kontrola | Uwaga |
| --- | --- | --- | --- |
| XLSX Ads | okres × konto × marketplace × kampania/grupa/oferta/miejsce według eksportu | identyfikator importu, czas eksportu i wymiary | Raporty różnych wymiarów są ALTERNATYWNYMI przekrojami; nie sumuj ich razem |
| API zamówień | checkoutForm × lineItem | id zamówienia, id pozycji, id oferty i data zakupu | Atrybucja na pozycji, zamówienie może obejmować różne SKU |
| System kosztów | SKU × data obowiązywania × konto/metoda dostawy | źródło i status każdej składowej | Marża ma się opierać na faktycznej paczce/pozycji |
| Rozliczenia Allegro | księgowanie × typ opłaty × oferta lub zamówienie (jeśli znany) | dokument rozliczeniowy i kwota | Uzgodnienie wydatków Ads z opłatami, bez podwójnego odejmowania |
| Historia zmian Ads | kampania/grupa × timestamp × osoba/system | konfiguracja przed/po | Nie jest dowodem przyczynowości, a jedynie kontekstem |

### Kontrakt importu — obligatoryjne pola manifestu
- `import_id`, `source_type` (XLSX_ADS, ORDER_API, COST_LEDGER, ALLEGRO_BILLING, CHANGE_HISTORY), `source_url_or_filename`, `retrieved_at`, `period_start`, `period_end`, `account_id`, `marketplace_id`, `currency`, `time_zone`, `monetary_basis` (GROSS/NET), `raw_sha256`, `grain`, `attribution_window_status`.
- Pól brakujących nie udawaj zerem; każdy wskaźnik wprowadź w sposób jawny jako number/null wraz z jednostką/źródłem; przy eksporcie z różnymi wymiarami zachowaj oddzielny `import_id`.
- `revenue_scope` określa czy to przychód przypisany kampanii, całkowita sprzedaż konta, sprzedaż produktu czy zwrot po korekcie. Niedozwolone automatyczne mieszanie tych mianowników.
- `sku_costs` muszą mieć `status` KNOWN / ZERO_CONFIRMED / NOT_APPLICABLE / UNKNOWN, datę, dowód; kwoty brutto/netto i odliczalność VAT jawne.
- W razie wielu kont identyfikator konta to wymiar pierwszorzędny. Nie sumuj rynków lub walut bez jawnych zasad przeliczenia.

### Obsługa VAT i podatków
- Dla STAW EXPERT według ostatniego przekazanego stanu: firma nie jest czynnym podatnikiem VAT (stan wymaga potwierdzenia na dzień analizowanej transakcji). Koszt brutto zakupów/usług pozostaje kosztem ekonomicznym, jeżeli VAT nie podlega odliczeniu. Nie zmieniaj go automatycznie na netto po kliknięciu przełącznika w Allegro Ads.
- VAT i podatek dochodowy to inne strumienie rozliczeń. Zysk przed podatkiem dochodowym, gotówka po opłatach oraz marża kontrybucyjna są różnymi wynikami. Nie odejmuj arbitralnie ryczałtu od zysku.
- Prowizje, koszt dostawy, Smart, dopłaty, opakowanie, materiał, robocizna, straty i zwroty muszą mieć źródło; `UNKNOWN` blokuje stwierdzenie „rentowne”.

## 3. Metryki i wzory (spójna waluta, okres i podstawa)
| KPI | Wzór | Warunek |
| --- | --- | --- |
| CTR | clicks / impressions | impressions > 0 |
| CPC średnie | spend / clicks | clicks > 0 |
| ROAS | attributed_revenue / spend | spend > 0; wartość może być BRUTTO lub NETTO, oznacz |
| ACoS | spend / attributed_revenue | attributed_revenue > 0 |
| CVR Ads | attributed_orders / clicks | tylko zgodne okno atrybucji i licznik zamówień |
| CPA | spend / attributed_orders | attributed_orders > 0 |
| TACoS | spend / total_account_revenue | to samo konto/okres/waluta, bez podwójnych sum |
| Nadwyżka przypisana przed Ads | attributed_revenue - zwroty/rabaty - koszty zmienne sprzedanych pozycji | per item/order, kompletne koszty |
| Nadwyżka przypisana po Ads | contribution_before_ads - ad_spend | spend odjęty dokładnie RAZ |
| Break-even ACoS | contribution_before_ads / attributed_revenue | porównywalna podstawa sprzedaży |
| Break-even średnie CPC | expected_contribution_per_paid_order × conversion_rate_click_to_order | prognoza, nie limit pojedynczego kliknięcia |

Nie nazywaj `attributed contribution` rzeczywistym zyskiem inkrementalnym. Współczynnik CVR obliczony z jednego tygodnia nie musi reprezentować kolejnego tygodnia, zwłaszcza w sezonowym asortymencie.

### Przykład kontrolny — fikcyjne dane
Przypisana sprzedaż 1000 zł, 100 zł kosztu Ads, 820 zł zweryfikowanych kosztów zmiennych bez Ads:
- nadwyżka przed Ads = 180 zł;
- nadwyżka po Ads = 80 zł;
- ROAS = 10,0; ACoS = 10%; break-even ACoS = 18%.
Wynik **nie** dowodzi, że reklama wygenerowała 80 zł dodatkowego zysku względem braku reklamy.

## 4. Przypadki STAW EXPERT / segmentacja
Nie grupuj w jednej analizie:
- kredy sypkiej/granulowanej oraz wysyłek ciężkich 20–31,5 kg (często paczka na worek);
- baniek 1/5/20 l (limity wspólnego pakowania i ryzyko wycieku);
- preparatów bakteryjnych, utleniających, chemicznych;
- palet/BigBagów i przesyłek specjalnych;
- ofert sezonowych (wiosna/lato) oraz pozasezonowych.

Segmentację buduj na rzeczywistym `SKU`, wadze/opakowaniu, sposobie dostawy, koncie i kategorii, nie tylko na nazwie oferty. Próg sensownego CPC różni się dla produktu i zestawu produktów. Osobno badaj miejsca emisji, nową i organiczną sprzedaż, trend planera, dostępność magazynu i jakość karty.

## 5. SOP audytu / odpowiedzialność
1. HUMAN eksportuje oficjalny XLSX z Ads (Statystyki → dobór okresu/wymiarów → Pobierz → Moje pliki), przekazuje kosztową kartotekę SKU i okres zamówień z opóźnieniem.
2. CODE zachowuje oryginały poza repo jeśli zawierają dane transakcyjne; generuje manifest z hash, sprawdza sumy/duble/daty i statusy braków. Wyklucza przypadki nakładających się raportów.
3. CODE łączy zamówienia tylko po faktycznych kluczach. Dzieli logistykę zgodnie z rzeczywistą alokacją paczek, nie proporcją wartości gdy nieuzasadniona.
4. AI porównuje kampanie Pro/Express, miejsca, CPC, CTR, CVR, ACoS i jednostkowe progi z marginesem niepewności.
5. HUMAN akceptuje zmiany oddzielnie. Nie uruchamiać zmian budżetów, automatycznego wyłączania kampanii, nietestowanych API Ads ani narzędzi strony trzeciej.
6. CODE/AI po 7 dniach lub odpowiednio dłuższym oknie ocenia kohortę, historię zmian i opóźnione zwroty; zachowuje poprzedni raport i opisuje korekty.

Statusy w raporcie: `PASS` (kompletny i spójny), `PROVISIONAL` (atrybucja jeszcze dojrzewa), `HOLD_DATA` (brak kosztu/rozbieżności), `BLOCKED` (dostęp/zgodność). Zapis w repo to stan projektu, nie dowód podłączenia konta.

## 6. Lista kontroli i testy akceptacyjne
- Zero impressions/clicks/spend => wskaźniki o mianowniku 0 to `null`, nie 0 lub ∞.
- Zero konwersji w pierwszym dniu => `PROVISIONAL`, nie automatyczne pauzowanie.
- UNKNOWN materiał/wysyłka/Smart => brak ostatecznego progu rentowności.
- 2 alternatywne eksporty grup i ofert => ten sam spend nie sumuje się dwa razy.
- Zamówienie z dwiema pozycjami, jedną attributed:true => przypisuj flagę per item, nie do całego koszyka.
- Zwrot zamówienia i opłata stała => jawna korekta nadwyżki; policz ponownie.
- Zmiana widoku Ads NET/GROSS => wartości sprzedaży nie przeliczaj automatycznie.
- Sezonowość i mała próba => nie ogłaszaj zwycięzcy bez danych porównawczych.
- Raporty z różnych kont i walut => oddziel lub przelicz wg jawnego kursu.
- Każde źródło ma datę oraz URL; brak danych produkcyjnych = test NOT RUN.

## 7. Przegląd otwartych projektów GitHub (materiał porównawczy, nie gotowy pakiet)
- https://github.com/omnihero1/Allegro-Ads-Zarzadzanie — opisuje panel TS/React i API agencyjne; **nie gwarantuje** zwykłemu sprzedawcy uprawnień; nie instalować bez audytu licencji, zależności i endpointów.
- https://github.com/suchokrates1/retrievershop-suite — przykłady modelu analityki/profit; ocenić pochodzenie danych panelu i metodę alokacji kosztów; nie kopiować tokenów/cookie.
- https://github.com/em411/allegro-php-api — klient generowany z modelu OpenAPI; sprawdzić wersję kontraktu i jakość przed użyciem.
- https://github.com/allegro/allegro-api — oficjalne forum developerskie; nie jest SDK sterowania Ads.

**Rekomendacja:** wykorzystać oficjalne XLSX, zgodne z prawem odczyty zamówień i offline calculator. Nie instalować automatycznego „clickera” reklam ani sesyjnego scrapera.

## 8. Otwarte braki (do uzupełnienia danymi, nie domysłami)
- rzeczywiste eksporty Ads, opłaty, zamówienia i koszty STAW EXPERT;
- uprawnienia każdego konta i aktualny status VAT na daty transakcji;
- zweryfikowany offset opóźnienia raportów, definicje pól w konkretnym XLSX;
- potwierdzenie opłat za emisję i dane rabatów/zwrotów;
- testy porównawcze z panelu i rzeczywiste `7DEJV OMS`.

Kolejny etap: import i walidacja pierwszego XLSX; dopiero potem rekomendacje stawek i budżetu.
