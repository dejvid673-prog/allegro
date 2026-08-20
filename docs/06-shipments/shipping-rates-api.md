# Cenniki i metody dostawy w API

Weryfikacja kontraktu: **2026-08-20**.

## Endpointy

| Cel | Endpoint | Scope |
|---|---|---|
| dostępne metody i ograniczenia | `GET /sale/delivery-methods` | token aplikacji lub użytkownika |
| lista cenników sprzedawcy | `GET /sale/shipping-rates` | `allegro:api:sale:settings:read` |
| szczegóły cennika | `GET /sale/shipping-rates/{id}` | `allegro:api:sale:settings:read` |
| utworzenie cennika | `POST /sale/shipping-rates` | `allegro:api:sale:settings:write` |
| modyfikacja cennika | `PUT /sale/shipping-rates/{id}` | `allegro:api:sale:settings:write` |
| ustawienia dostawy konta | `GET/PUT /sale/delivery-settings` | odpowiednio settings read/write |

## Metoda dostawy jest dynamicznym słownikiem

Nazwy metod nie są unikalne — kluczem jest `deliveryMethod.id`. Dla każdej metody API zwraca marketplace, politykę płatności, kraj nadania/docelowy, oznaczenie Allegro oraz `shippingRatesConstraints`:

- czy metodę można dodać;
- maksymalną liczbę sztuk w paczce;
- czy i w jakim zakresie można ustawić masę paczki;
- minimalną/maksymalną cenę pierwszej i kolejnej sztuki;
- domyślny oraz edytowalny czas dostawy.

Nie utrzymuj własnej stałej listy metod. Synchronizuj ją co najmniej codziennie i przed edycją cennika. Metoda wycofana może nadal występować w historii, ale mieć `allowed=false`.

## Model wpisu cennika

Każdy `rate` zawiera co najmniej `deliveryMethod.id`, `maxQuantityPerPackage`, opcjonalną wspieraną `maxPackageWeight`, `firstItemRate`, `nextItemRate` i `shippingTime`. Kwoty oraz masa w API są tekstami dziesiętnymi, aby uniknąć błędów zaokrąglenia; parsuj je do `Decimal`, nie float.

Od **2026-07-22** nowe cenniki wymagają:

- `type`: `PHYSICAL` lub `ELECTRONIC`;
- `dispatchCountry`: wymagane dla `PHYSICAL`, np. `PL`.

Przy `PUT` wartości typu/kraju muszą pasować do odczytanego cennika. Cennik z `features.managedByAllegro=true` nie jest edytowalny przez API. Cenniki One Fulfillment mają osobne ograniczenia.

## Bezpieczna modyfikacja

1. Pobierz metody i bieżący cennik.
2. Waliduj każdy rate względem aktualnych constraints i profilu paczki.
3. Oblicz wpływ na wszystkie przypięte oferty, Smart, marżę i rynki.
4. Zbuduj pełny, jawny model `PUT`; nie wysyłaj nieprzefiltrowanej odpowiedzi GET.
5. Pokaż diff oraz oferty tracące Smart/metodę.
6. Po zatwierdzeniu wykonaj PUT i ponownie GET.
7. Uzgodnij widoczność na ofertach i zapisz wersję cennika.

`POST` nie jest bezpieczny do ślepego retry. Po timeout sprawdź listę cenników i identyfikuj wynik po zapisanym fingerprintcie treści/nazwy/czasu, zanim utworzysz następny.

## Reguły nazw i liczby cenników

Nazwa ma kodować przeznaczenie, nie cenę, np. `PL-SMART-S-M-v2026-08` lub `PL-DPD-H31-v2026-08`. API może zwrócić `422`, gdy konto osiągnie limit cenników. Zamiast tworzyć cennik per SKU, używaj niewielkiej liczby zatwierdzonych profili paczek.
