# Kategorie, produkty i parametry

## Kategorie

1. Szukaj kategorii przez `/sale/matching-categories` na podstawie nazwy produktu.
2. Zweryfikuj ścieżkę drzewa przez `/sale/categories` i `/sale/categories/{categoryId}`.
3. Wystawiaj tylko w kategorii z `leaf: true`.
4. Pobierz bieżące parametry przez `/sale/categories/{categoryId}/parameters`.
5. Zapisz snapshot wymagań i datę, ale przed publikacją wykonaj ponowny preflight.

Kategoria ze starej oferty nie jest gwarancją poprawności — drzewo może zostać uproszczone, przeniesione lub zastąpione parametrem.

## Parametry

Każdy parametr normalizuj do:

```json
{
  "parameter_id": "string",
  "name": "Nazwa tylko do UI",
  "value_ids": ["string"],
  "values": ["tekst tylko gdy API na to pozwala"],
  "range": null,
  "unit": null,
  "source": "catalog|sku|user|legacy_offer",
  "verified_at": "2026-08-20T00:00:00Z"
}
```

Nie mapuj wartości po samej nazwie. Nazwy i etykiety mogą się zmienić; kluczem jest `parameter_id` i — jeśli istnieje — `value_id`.

## Obowiązkowość

Rozróżnij:

- wymagane przy tworzeniu produktu;
- wymagane przy tworzeniu/publikacji oferty;
- wymagania warunkowe;
- parametry opisowe/rekomendowane;
- wymagania planowane.

`GET /sale/offers/unfilled-parameters` zwraca braki dla aktywnych ofert, w tym typy `REQUIRED` i `REQUIREMENT_PLANNED`. Agent ma codziennie monitorować wymagania planowane, aby nie czekać do dnia blokady.

## Produkty i GTIN

Kolejność dopasowania:

1. wiarygodny GTIN/EAN z kartoteki/etykiety producenta;
2. znany `product.id` wcześniej zatwierdzony dla SKU;
3. wyszukiwanie produktu po parametrach i kategoriach;
4. propozycja nowego produktu dopiero po udokumentowaniu braku właściwego produktu.

Warunki automatycznego dopasowania powinny wymagać zgodności co najmniej marki, modelu/wariantu, pojemności/masy i kluczowych parametrów. Tytuł jest tylko wskazówką.

## Zmiany kategorii

Monitoruj:

- `/sale/category-events`;
- wymagania z `/sale/offers/unfilled-parameters`;
- changelog i Aktualności;
- rozbieżność snapshotu parametrów względem bieżącego API.

Po zdarzeniu kategorii oznacz powiązane szablony jako `REVALIDATION_REQUIRED`. Nie aktualizuj automatycznie wartości, gdy stary i nowy parametr nie mają jednoznacznego mapowania.

## Cache

| Dane | Sugerowany TTL | Unieważnienie |
|---|---:|---|
| drzewo kategorii | 24 h | category event / breaking news |
| parametry kategorii | 6 h | category event / błąd 422 |
| wynik dopasowania produktu | 24 h | zmiana GTIN/SKU / odrzucenie człowieka |
| pojedynczy produkt | 6 h | event/zmiana oferty / ręczny refresh |
| słowniki globalne | 24 h | hash/spec change |

Cache musi zawierać `fetched_at`, marketplace i etag/hash, jeśli dostępny. Brak API nie uprawnia do publikacji z przeterminowanego cache w obszarze obowiązkowych parametrów.
