# Model produktu, oferty i publikacji

## Produkt ≠ oferta

| Produkt w Katalogu Allegro | Oferta sprzedawcy |
|---|---|
| identyfikuje towar niezależnie od sprzedawcy | definiuje warunki konkretnej sprzedaży |
| GTIN/EAN, marka, model, parametry katalogowe | tytuł, opis, cena, liczba sztuk, dostawa |
| wspólny i może być aktualizowany przez Allegro | należy do konta sprzedającego |
| może mieć wielu sprzedawców | wskazuje jeden lub więcej elementów `productSet` |

Nową ofertę tworzymy przez `POST /sale/product-offers`. Jeśli produkt istnieje, wskazujemy jego `id`; jeśli go nie ma, proces może zawierać dane propozycji produktu. Nie twórz nowego produktu tylko dlatego, że wyszukiwanie po błędnym tytule nic nie zwróciło.

## Główne elementy oferty

Dokładny payload zawsze rozstrzyga bieżący Swagger. Operator ma jednak znać co najmniej:

- `productSet` — produkty i ich parametry/ilości w ofercie;
- `name` — tytuł;
- `category.id` — kategoria liściowa;
- `parameters` — parametry oferty;
- `description.sections` — strukturalny opis tekst/zdjęcia;
- `images` — galeria;
- `sellingMode` — format i cena;
- `stock` — liczba i jednostka;
- `delivery` — cennik, czas wysyłki, ewentualne dane dodatkowe;
- `payments`, `afterSalesServices` — płatność, zwroty, reklamacje, gwarancje;
- `location` — lokalizacja przedmiotu;
- `publication` — stan i plan publikacji;
- `external.id` — stabilne powiązanie z SKU/systemem firmy;
- `tax`, faktura i ustawienia marketplace;
- `responsibleProducer`, `responsiblePerson`, `safetyInformation` — dane bezpieczeństwa zależnie od produktu;
- `aiCoCreatedContent.images` — deklaracje obrazów AI zgodnie z aktualnym kontraktem.

## Statusy i własny model

Nie opieraj logiki tylko na jednym polu `publication.status`. Lokalny rekord powinien przechowywać:

```text
seller_account_id
offer_id
external_id / sku
product_ids[]
category_id
publication_status
publication_ended_by
validation_status
last_offer_event_at
last_full_read_at
snapshot_version
source_hash
archived_at
```

## Media, opis i prawa do treści

Opis jest zbiorem sekcji, a nie dowolnym HTML-em. Generator szablonu ma przechowywać semantyczne bloki (`heading`, `paragraph`, `image`, `bullets`) i dopiero adapter Allegro tłumaczy je na dozwoloną strukturę `sections.items`.

Zdjęcie ma własną tożsamość i pochodzenie:

- oryginalny plik/URL i hash;
- właściciel/licencja;
- źródło: fotografia własna, producent, Allegro Catalog, generatywne AI, edycja AI;
- decyzja `ai_declaration_required` wraz z dowodem;
- URL zwrócony przez `POST /sale/images`;
- kolejność i rola (`main`, `gallery`, `description`, `label`, `hazard`).

Oznaczenie AI ustala się przy pierwszym uploadzie pliku. Gdy obraz już istnieje w bazie Allegro, ponowne przesłanie deklaracji w ofercie może zostać zignorowane na rzecz pierwotnego oznaczenia.

## External ID

`external.id` powinno być deterministyczne i stabilne. Rekomendacja:

```text
<brand-or-company>:<sku>:<pack-variant>:v<template-major>
```

Nie umieszczaj danych osobowych, ceny, zapasu ani daty. Dla kilku kont dopuszczalny jest prefiks konta, jeśli ta sama kartoteka może mieć różne oferty.

## Marketplace

Oferta może być publikowana na rynkach zagranicznych tylko wtedy, gdy:

- produkt i kategoria są dostępne na danym rynku;
- tłumaczenia, cena, VAT i waluta są poprawne;
- dostawa działa z właściwego `dispatchCountry`;
- etykieta i wymagane informacje bezpieczeństwa są w języku rynku;
- asortyment nie jest objęty ograniczeniem transgranicznym.

Domyślnie nowy szablon jest ograniczony do `allegro-pl`, dopóki profil compliance nie dopuści kolejnych rynków.
