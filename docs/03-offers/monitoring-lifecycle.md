# Monitoring i cykl życia ofert

## Dwa tryby synchronizacji

1. **Zdarzenia** — `GET /sale/offer-events`, ciągły kursor i małe opóźnienie.
2. **Pełna rekonsyliacja** — stronicowane `GET /sale/offers`, które wykrywa utracone zdarzenia i rozbieżności.

Zdarzenia ofert są dostępne za ostatnie 24 godziny. Awaria dłuższa niż okno retencji wymaga pełnego backfillu. Pojedyncza strona listy obejmuje maksymalnie 1000 ofert, więc zawsze implementuj paginację.

## Typy zdarzeń, które należy obsłużyć

Co najmniej:

- aktywacja i zakończenie;
- zmiana oferty;
- zmiana ceny;
- zmiana stocku;
- archiwizacja;
- wszystkie nowe typy zwrócone przez aktualny Swagger/API jako `UNKNOWN_EVENT`, zapisane do analizy zamiast odrzucone.

## Klasyfikacja stanu biznesowego

| Stan operatora | Znaczenie | Akcja |
|---|---|---|
| `ACTIVE_OK` | aktywna i zgodna | monitoruj |
| `ACTIVE_DRIFT` | aktywna, ale cena/zapas/dane różnią się od źródła | propozycja korekty |
| `ACTIVE_MISSING_REQUIRED` | braki obecne lub planowane | pilny raport / naprawa |
| `INACTIVE_EXPECTED` | wyłączona zgodnie z planem | bez alarmu |
| `INACTIVE_UNEXPECTED` | oczekiwano aktywnej | alarm i analiza przyczyny |
| `ENDED_REVIEW` | zakończona, przyczyna wymaga decyzji | kolejka zatwierdzeń |
| `ARCHIVED` | usunięta z bieżącej listy | korzystaj z własnego archiwum |
| `UNKNOWN` | niepełne dane lub błąd synchronizacji | nie wykonuj automatycznego zapisu |

## Expected state

Operator nie może alarmować o każdej nieaktywnej ofercie. Dla każdej oferty przechowuj zamiar:

```text
desired_publication_state = ACTIVE | INACTIVE | SCHEDULED | SEASONAL | RETIRED
desired_from / desired_until
reason
approved_by
```

Alert powstaje, gdy stan rzeczywisty różni się od zamierzonego dłużej niż próg tolerancji.

## Codzienne kontrole

- brak ofert oczekiwanych jako aktywne;
- oferty zakończone w ostatnich 24 h i powód;
- braki `REQUIRED` i `REQUIREMENT_PLANNED`;
- stock `0` przy dodatnim magazynie i dodatni stock przy braku magazynu;
- cena poza min/max lub różnica od źródła;
- niezgodne category/product IDs;
- duplikaty w grupie kont;
- zbliżający się koniec ogłoszeń żywych zwierząt;
- nieprawidłowy User-Agent, 401/403/429 i starzenie tokenu;
- asynchroniczne operacje bez terminalnego wyniku.

## Archiwum

Oferty zakończone są po pewnym czasie archiwizowane i mogą przestać być dostępne standardowo po ID (poradnik wskazuje około 60 dni). Drafty także mogą być usuwane po okresie bez zmian; oficjalne materiały zawierają niespójne wzmianki o 60 i 120 dniach. Dlatego:

- nie polegaj na Allegro jako archiwum treści;
- zapisuj wersjonowany, zredagowany snapshot każdej oferty i zmianę;
- przechowuj obrazy/dokumenty zgodnie z prawem i polityką retencji;
- drafty ważne biznesowo eksportuj do `OfferTemplate` natychmiast;
- nie koduj jednego terminu usunięcia jako gwarancji SLA.

## SLO

| Kontrola | Cel |
|---|---:|
| opóźnienie zdarzeń ofert | < 5 min |
| wykrycie nieoczekiwanej dezaktywacji | < 10 min |
| pełna rekonsyliacja | co 24 h |
| braki planowanych parametrów | raport co 24 h |
| zgodność ceny/zapasu | zależnie od systemu nadrzędnego, zalecane < 15 min |
| brak kursora zdarzeń | alarm po 15 min |
