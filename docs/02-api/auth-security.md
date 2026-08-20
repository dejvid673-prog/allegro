# Uwierzytelnianie, autoryzacja i sekrety

Zweryfikowano: **2026-08-20**.

## Wybór przepływu OAuth

| Przypadek | Zalecany flow | Uwagi |
|---|---|---|
| aplikacja webowa z callbackiem | Authorization Code + PKCE | użytkownik loguje się na Allegro; serwer nie widzi hasła |
| urządzenie/CLI bez wygodnego callbacku | Device Flow | użytkownik autoryzuje kod na innym urządzeniu |
| zadania w tle na koncie sprzedawcy | odświeżanie tokenu uzyskanego w user flow | operacje sprzedażowe wymagają kontekstu użytkownika |

Nie proś użytkownika o własny Client ID/Secret. Integracja działa na swoim zarejestrowanym kluczu i otrzymuje dostęp do kont przez OAuth.

## Czas życia i rotacja

- access token: około `43199` sekund, czyli niemal 12 godzin;
- refresh token: maksymalnie około 3 miesięcy;
- refresh token rotuje — po odświeżeniu należy atomowo zapisać nową parę;
- poprzedni token może jeszcze działać przez około 60 sekund, co nie oznacza, że wolno go zachować jako aktywny;
- tokeny mogą zostać unieważnione wcześniej, między innymi po wylogowaniu ze wszystkich urządzeń, zmianie hasła/e-maila, blokadzie sprzedaży, odpięciu aplikacji lub przekroczeniu liczby aktywnych sesji.

## Scope

Żądaj najmniejszego zestawu niezbędnego do aktualnego modułu. Scope dostępne w bieżącym OpenAPI obejmują m.in.:

- `allegro:api:sale:offers:read`, `allegro:api:sale:offers:write`;
- `allegro:api:sale:settings:read`, `allegro:api:sale:settings:write`;
- `allegro:api:orders:read`, `allegro:api:orders:write`;
- `allegro:api:shipments:read`, `allegro:api:shipments:write`;
- `allegro:api:profile:read`, `allegro:api:profile:write`;
- messaging, disputes, ratings, payments, billing, fulfillment, bids, campaigns i affiliate.

Moduł audytowy ofert nie potrzebuje zapisu do przesyłek. Rozdzielaj klientów/role logiczne, nawet jeśli korzystają z tego samego klucza aplikacji.

## Przechowywanie sekretów

Wymagania:

1. tokeny w zarządzanym sejfie sekretów, szyfrowane w spoczynku;
2. dostęp tylko dla serwisu wykonawczego, nie dla frontendu i analityki;
3. logi zawierają `token_ref`, nigdy wartość tokenu;
4. rotacja refresh tokenu w transakcji z blokadą na konto;
5. alarm przy kolejnych błędach `invalid_grant` i zakaz nieskończonego retry;
6. możliwość natychmiastowego odłączenia konta i unieważnienia lokalnych danych dostępowych;
7. osobne sekrety produkcji i Sandboxa.

## Nagłówki obowiązkowe

```http
Authorization: Bearer <access-token>
Accept: application/vnd.allegro.public.v1+json
Content-Type: application/vnd.allegro.public.v1+json
User-Agent: NazwaAplikacji/Wersja (+https://adres-kontaktowy.example)
Accept-Language: pl-PL
```

Media type może być public lub beta zależnie od endpointu. Sprawdź bieżący Swagger. Własny, stabilny `User-Agent` jest obowiązkowy od końca czerwca 2026; zmieniaj w nim numer wersji aplikacji, a nie losowy identyfikator każdego requestu.

## Zmiana regulaminu od 2026-09-01

Dla nowych kluczy rejestrowanych od tej daty przygotuj kontrolę:

- użycie klucza w ciągu 30 dni od rejestracji;
- alarm przed 90 dniami braku użycia autoryzacji aplikacji;
- założenie jednego standardowego klucza; dodatkowy wymaga wniosku;
- naruszenie regulaminu może skutkować punktami ujemnymi w jakości sprzedaży.

## Threat model

| Zagrożenie | Ochrona |
|---|---|
| wyciek refresh tokenu | sejf, redakcja logów, minimalny dostęp, rotacja i revoke |
| pomylenie konta | po OAuth odczytaj user identity i pokaż seller ID przed zatwierdzeniem |
| zapis na złym środowisku | oddzielne hosty, sekrety i wyraźny znacznik `environment` |
| nadmierne scope | manifest scope per moduł i przegląd przy każdym rozszerzeniu |
| replay / podwójny POST | operation key/UUID, outbox i sprawdzenie stanu przed retry |
| zależność od jednej osoby | procedura odzyskania dostępu i dwóch właścicieli technicznych bez współdzielenia haseł |
