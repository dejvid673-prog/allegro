# Macierz pól i spójności oferty Allegro

To lista kontrolna dla szablonu, preflightu i audytu. Dokładną obowiązkowość pól rozstrzyga aktualny Swagger oraz runtime kategorii/produktu/konta.

| Obszar / pole | Źródło nadrzędne | Musi być spójne z | Blokada |
|---|---|---|---|
| konto i marketplace | OAuth/profil Allegro | waluta, język, VAT, cennik, publikacja | pomieszane konto/rynek |
| `external.id` / SKU | kartoteka firmy | zapas, koszt, wariant, zamówienie | brak stabilnego SKU lub kolizja |
| GTIN/EAN | producent/GS1 + katalog | zdjęcie etykiety, wariant, produkt | zgadywany albo inny wariant |
| `productSet` | katalog Allegro/runtime | GTIN, liczba sztuk, parametry | zły produkt lub sztuczny zestaw |
| `category.id` | kategorie API, `leaf=true` | typ produktu i format oferty | kategoria nieliściowa/błędna |
| parametry produktu | katalog/producent | tytuł, opis, etykieta | wymagany brak/konflikt |
| parametry oferty | kategoria API | filtry, stan, wariant | `REQUIRED` brak; `REQUIREMENT_PLANNED` kolejka naprawy |
| tytuł `name` | szablon + dowody produktu | marka, model, masa, liczba, EAN | rozbieżny wariant/zakazane treści |
| opis | zatwierdzony content | parametry, zdjęcia, zawartość, bezpieczeństwo | twierdzenie bez dowodu/inna zawartość |
| zdjęcie główne | asset registry | dokładny wariant i liczba sztuk | inny produkt/zestaw lub brak praw |
| zdjęcia dodatkowe | asset registry | etykieta, wymiary, opis | wprowadzają w błąd |
| AI `aiCoCreatedContent` | historia assetu | pierwszy upload i hash pliku | pochodzenie `UNKNOWN` |
| stan produktu | fizyczny stan SKU | parametry i opis | `NEW` dla produktu niespełniającego definicji |
| format sprzedaży | reguła kategorii | żywe ryby/ogłoszenie, promowanie, Smart | format niedozwolony |
| cena i waluta | polityka cenowa + koszt | marketplace, VAT, prowizja, Smart, Ads | niekompletny koszt lub marża poniżej minimum |
| stock i jednostka | jeden system magazynowy | SKU, zestaw, liczba sztuk | brak/overselling/inna jednostka |
| lokalizacja | miejsce towaru/nadania | `dispatchCountry`, przewidywana dostawa | fałszywy kraj/miejsce |
| cennik `shippingRates.id` | konto Allegro | profil paczki, Smart, rynek | metoda nie przyjmuje produktu |
| czas wysyłki | pomiar magazynu + cutoff | przewidywany pierwszy skan | nierealny lub niespójny z procesem |
| masa/wymiary paczki | pomiar zapakowanego SKU | limity przewoźnika i dopłaty | nieznane lub ponad limit |
| płatność/pobranie | cennik/metoda | Smart, opłata, carrier service | niedozwolona kombinacja |
| warunki zwrotu | zatwierdzona polityka konta | rynek, adres zwrotu, kategoria | brak wymaganej polityki/adresu |
| reklamacja i gwarancja | polityka firmy/producenta | opis, prawo, after-sales ID | sprzeczny termin/zakres |
| faktura i `tax` | księgowość | cena brutto/netto, stawka VAT, rynek | zła stawka/niezgodna deklaracja |
| producent GPSR | dokument producenta | marka, etykieta, katalog | brak lub niezgodna tożsamość |
| osoba odpowiedzialna UE | dokument GPSR | producent/kraj | wymagana i nieudokumentowana |
| informacje bezpieczeństwa | dokument/etykieta | opis, zdjęcia, język rynku | brak/zmieniona treść |
| CLP/UFI | SDS i etykieta | piktogramy, H/P, ilość, przewoźnik | niezweryfikowana chemia |
| pasza | etykieta/dokument paszowy | gatunek, skład, dodatki, partia, termin | brak danych sprzedaży na odległość |
| żywa ryba | dokumenty i identyfikacja gatunku | ogłoszenie, transport, sezon/pogoda | niezgodny gatunek/dokument/transport |
| promowanie/Ads | zatwierdzony eksperyment | koszt, zapas, jakość oferty | brak budżetu/marży lub produkt zablokowany |

## Spójność ilości i wariantu

Najczęstszy błąd klonowania to zmiana tylko tytułu. Dla każdego wariantu porównaj jednocześnie:

- SKU i `external.id`;
- EAN/GTIN i `productSet.product.id`;
- masa/pojemność/liczba w tytule;
- parametry katalogowe i ofertowe;
- zdjęcie frontu/etykiety;
- zawartość opisu i zestawu;
- stock w jednostce sprzedaży;
- profil paczki, koszt, cena i prowizja.

Zmiana któregokolwiek z tych pól unieważnia wcześniejszy kosztorys i zgodę na publikację.

## Preflight obowiązkowy

1. `GET` aktualnego produktu, kategorii i parametrów.
2. Kontrola `GET /sale/offers/unfilled-parameters` dla aktywnych ofert oraz równoważna walidacja draftu.
3. Odczyt cennika i metod wraz z constraints.
4. Wyszukanie duplikatów na wszystkich powiązanych kontach.
5. Walidacja schematu szablonu, pełnych kosztów i profilu compliance.
6. Diff od starej oferty i od źródeł firmy.
7. Ponowny preflight tuż przed wykonaniem, jeśli minął czas ważności propozycji.
