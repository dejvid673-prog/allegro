# HTTP, limity, błędy i odporność

## Środowiska

| Środowisko | Base URL |
|---|---|
| produkcja | `https://api.allegro.pl` |
| Sandbox | `https://api.allegro.pl.allegrosandbox.pl` |

Sandbox może być okresowo resetowany, w tym wraz z ofertami. Nie traktuj go jako trwałego archiwum testów.

## Reguły protokołu

- identyfikatory zapisuj jako string;
- czas zapisuj w UTC ISO 8601, a do interfejsu przeliczaj jawnie na `Europe/Warsaw`;
- zachowuj `Trace-Id` z każdej odpowiedzi;
- `PATCH` ofert używa JSON Merge Patch — wysyłaj wyłącznie zmieniane, obsługiwane pola;
- `PUT` jest z natury powtarzalny dla tego samego URI/payloadu, ale skutki biznesowe nadal trzeba potwierdzić;
- `POST` nie jest bezpieczny do ślepego retry: ponowne `POST /sale/product-offers` może utworzyć duplikat;
- przy `202 Accepted` odpytuj wskazany status operacji, nie zakładaj sukcesu na podstawie samej odpowiedzi;
- respektuj `Location` i `Retry-After`.

## Limity

Główny limit jest opisany jako 9000 requestów/minutę na Client ID, ale konkretne zasoby mogą mieć niższe limity. Allegro stosuje mechanizm zbliżony do Leaky Bucket i może zwracać `429` także przy zbyt dużej współbieżności jednego użytkownika.

Budżet ruchu dziel na kolejki:

1. zamówienia i anulowania — najwyższy priorytet;
2. status operacji Command i przesyłek;
3. zdarzenia ofert;
4. odczyty pojedynczych zasobów;
5. pełne audyty i raporty historyczne.

## Polityka retry

| Sytuacja | Działanie |
|---|---|
| `429` | czekaj zgodnie z `Retry-After`, zmniejsz współbieżność, dodaj jitter |
| `502/503/504` przy GET | exponential backoff z limitem prób |
| timeout przy GET | bezpieczny retry z tym samym correlation ID |
| timeout przy POST | najpierw sprawdź stan po command UUID / kluczu operacji; nie powtarzaj w ciemno |
| `401` | pojedyncza zsynchronizowana próba odświeżenia; potem reautoryzacja |
| `403` | sprawdź scope, właściciela zasobu i stan konta; retry zwykle nie pomoże |
| `404` | rozróżnij brak, archiwizację i usunięty endpoint |
| `409` | pobierz bieżący stan/revision i wykonaj ponowną ocenę biznesową |
| `422` | pokaż wszystkie validation errors; nie usuwaj pól losowo |

## Model błędu

Normalizuj błąd do:

```json
{
  "occurred_at": "2026-08-20T10:00:00Z",
  "operation": "create_product_offer",
  "method": "POST",
  "path_template": "/sale/product-offers",
  "status": 422,
  "trace_id": "redacted-example",
  "command_id": null,
  "retryable": false,
  "category": "VALIDATION",
  "errors": [],
  "account_id": "seller-ref",
  "payload_fingerprint": "sha256:..."
}
```

Nie loguj pełnego payloadu, jeśli zawiera dane kupującego. Dla ofert zachowuj zredagowany snapshot i hash.

## Idempotencja aplikacyjna

Każda operacja zapisu otrzymuje `operation_key`, np.:

`account_id + operation_type + business_object_id + desired_state_version`

Tabela operacji ma unikalny indeks na `operation_key`, zapisany request fingerprint, command UUID, stan `PLANNED/SENT/ACCEPTED/SUCCEEDED/FAILED/UNKNOWN` i końcową weryfikację. Stan `UNKNOWN` blokuje automatyczny retry do czasu rekonsyliacji.

## Monitoring techniczny

- success/error/429 rate per endpoint i konto;
- p50/p95/p99 latency;
- wiek tokenu i ostatni udany refresh;
- liczba operacji `UNKNOWN` oraz Command bez terminalnego statusu;
- opóźnienie kursora zdarzeń ofert i zamówień;
- różnica pełnego backfillu względem modelu eventowego;
- hash Swaggera i liczba zmian endpointów/schematów;
- status `https://api.allegrostatus.pl/`.
