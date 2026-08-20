# Tworzenie oferty ze starej oferty i szablonu

## Zasada

Nie klonujemy payloadu Allegro. Tworzymy neutralny `OfferTemplate`, walidujemy go wobec aktualnego API, a następnie generujemy nowy request. Dzięki temu nie kopiujemy pól tylko do odczytu, starych wymagań ani ukrytych błędów.

## Dane wejściowe

- konto docelowe i marketplace;
- ID starej oferty lub SKU;
- docelowy wariant/pojemność/liczba sztuk;
- aktualna cena, zapas, waga i wymiary paczki;
- dokumenty produktu: etykieta, GTIN, GPSR, CLP/UFI lub dane paszy;
- źródło i status każdego zdjęcia;
- zatwierdzone cenniki dostaw i warunki posprzedażowe.

## Pipeline

### 1. Snapshot źródła

Pobierz ofertę przez `GET /sale/product-offers/{offerId}` i ogólny stan przez `GET /sale/offers/{offerId}`. Zapisz czas, konto, `Trace-Id` i hash zredagowanego snapshotu. Jeśli oferta jest archiwalna i API jej nie zwraca, korzystaj z własnego archiwum — nie rekonstruuj prawdy ze zrzutu ekranu.

### 2. Ekstrakcja

Do neutralnego szablonu kopiuj wyłącznie wartości o znanym znaczeniu. Oznacz pochodzenie każdego pola:

- `verified_current` — potwierdzone w kartotece/aktualnym API;
- `legacy_candidate` — tylko ze starej oferty;
- `derived` — obliczone regułą;
- `missing` — wymaga uzupełnienia.

### 3. Czyszczenie

Zawsze usuń lub odtwórz:

- `id`, timestamps, publication status i pola serwerowe;
- liczniki sprzedaży, statystyki, walidacje i operacje;
- produkt/kategorię/parametry bez aktualnej weryfikacji;
- cenę, stock, cennik, handling time, location;
- `external.id`, jeśli docelowy wariant ma inne SKU;
- zdjęcia bez informacji o prawach i AI;
- manufacturer/responsible person/safety info bez dokumentu;
- podatki i marketplace settings zależne od konta;
- promocje, badge, automatyczne ceny i kampanie.

### 4. Aktualne dane API

Pobierz i potwierdź:

1. kategorię liściową;
2. parametry kategorii;
3. produkt lub wynik propozycji produktu;
4. cennik i after-sales services konta docelowego;
5. dane osoby odpowiedzialnej/producenta, jeśli są potrzebne;
6. marketplace i publication settings.

### 5. Reguły firmy i compliance

Uruchom wspólny zestaw reguł oraz dokładnie jeden profil główny:

- `pond_chemical`;
- `fish_feed`;
- `live_fish_classified`;
- `general_goods`.

Profil może dodać blokady, obowiązkowe zdjęcia etykiety i pola szablonu.

### 6. Duplikaty

Zbuduj fingerprint produktu na podstawie:

- product ID/GTIN;
- kategorii;
- condition;
- kluczowych parametrów;
- podobieństwa miniatury;
- wszystkich powiązanych kont.

Przed publikacją odczytaj aktywne oferty na wszystkich kontrolowanych kontach. Dla tego samego nowego produktu w tej samej podkategorii nie przekraczaj dwóch ofert łącznie.

### 7. Preflight i diff

Raport dla człowieka pokazuje:

| Sekcja | Stara wartość | Nowa wartość | Źródło | Ryzyko |
|---|---|---|---|---|
| produkt/kategoria | … | … | Allegro API | blocking/warning/info |
| tytuł/opis | … | … | template | … |
| cena/zapas | … | … | source system | … |
| dostawa | … | … | shipping profile | … |
| GPSR/CLP/pasze | … | … | document | … |
| zdjęcia/AI | … | … | asset registry | … |

Blokada, jeśli występuje błąd `BLOCKING`, nieznane pochodzenie zdjęcia, niezweryfikowany GTIN, brak parametru obowiązkowego lub brak profilu zgodności.

### 8. Publikacja

- utwórz trwały `operation_key` przed requestem;
- prześlij minimalny, jawnie zbudowany payload;
- przy `201` zapisz offer ID;
- przy `202` odpytuj `/sale/product-offers/{id}/operations/{operationId}` zgodnie z `Retry-After`;
- nie uznawaj sukcesu na podstawie samego odczytu oferty — błędy walidacji mogą być wyłącznie w wyniku operacji;
- po sukcesie ponownie odczytaj ofertę i porównaj pola krytyczne.

## Edycja istniejącej oferty

`PATCH /sale/product-offers/{id}` używa Merge Patch. Adapter ma allowlistę pól do zapisu. Nie wykonuj `GET → zmiana jednego pola → odesłanie całego JSON`, ponieważ odpowiedź zawiera pola nieobsługiwane w requestach i może zakończyć się `UnknownJSONProperty`.

## Wznowienie zakończonej oferty

Automatyczne wznowienie jest możliwe dopiero po ustaleniu:

- kto/co zakończyło ofertę;
- czy produkt jest nadal dostępny i legalny;
- czy brakujące parametry nie spowodowały zakończenia;
- czy nie powstanie duplikat;
- czy cena, zapas, zdjęcia, dostawa i compliance są aktualne;
- czy oferta nie została zarchiwizowana i nadal jest dostępna po ID.

W innym przypadku utwórz nowy draft z szablonu i poproś o zatwierdzenie.
