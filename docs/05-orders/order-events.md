# Zamówienia i zdarzenia

Weryfikacja: **2026-08-20**. Źródło techniczne: `developer-orders` w rejestrze źródeł i aktualny Swagger.

## Kiedy rozpocząć realizację

Realizuj dopiero formularz zakupowy ze statusem `READY_FOR_PROCESSING`. Nie opieraj realizacji wyłącznie na zdarzeniu płatności ani wiadomości od kupującego. Przed utworzeniem przesyłki pobierz aktualny formularz i sprawdź:

- `checkoutForm.id` oraz `revision`;
- dane dostawy, metodę, punkt odbioru i zamaskowany e-mail;
- pozycje identyfikowane przez `lineItem.id`, SKU, ilość i cenę;
- płatność, fakturę, dopłatę i stan anulowania;
- czy kilka formularzy nie zostało połączonych w nowe zamówienie.

Po połączeniu zamówień powstaje nowy `checkoutForm.id`. Integracja śledzi pozycje także po `lineItem.id`; nie może uznać starego identyfikatora formularza za nadal realizowany.

## Konsumpcja zdarzeń

Zdarzenia mogą się powtarzać i dotrzeć poza kolejnością. Strumień służy do szybkiego wykrywania zmian, a pełny odczyt zasobu do rozstrzygnięcia stanu.

1. Zapisz `event.id` przed przetwarzaniem.
2. Jeżeli identyfikator już istnieje, zakończ jako duplikat.
3. Pobierz bieżący formularz zakupowy.
4. Porównaj `revision` i stan lokalny.
5. Wykonaj deterministyczną zmianę.
6. Zapisz wynik oraz kursor dopiero po powodzeniu.
7. Okresowo wykonuj pełne uzgodnienie, bo historia zdarzeń nie jest archiwum bezterminowym.

Retencja zdarzeń zamówień wynosi 60 dni. Lokalny dziennik audytowy musi zachować dane wymagane przez księgowość i obsługę reklamacji, z ograniczeniem danych osobowych i zgodnie z polityką retencji firmy.

## Minimalna maszyna stanów

| Stan lokalny | Warunek wejścia | Dozwolone następne stany |
|---|---|---|
| `DISCOVERED` | zdarzenie lub odczyt nowego formularza | `WAITING_PAYMENT`, `READY`, `CANCELLED` |
| `WAITING_PAYMENT` | brak `READY_FOR_PROCESSING` | `READY`, `CANCELLED` |
| `READY` | aktualny status `READY_FOR_PROCESSING` | `ALLOCATED`, `CANCELLED`, `BLOCKED` |
| `ALLOCATED` | zapas zarezerwowany | `PACKED`, `BLOCKED`, `CANCELLED` |
| `PACKED` | potwierdzona paczka, masa i wymiary | `LABEL_CREATED`, `BLOCKED` |
| `LABEL_CREATED` | utworzenie przesyłki zakończone powodzeniem | `HANDED_OVER`, `LABEL_CANCELLED`, `EXCEPTION` |
| `HANDED_OVER` | pierwszy skan przewoźnika | `IN_TRANSIT`, `EXCEPTION` |
| `IN_TRANSIT` | ruch w sieci przewoźnika | `DELIVERED`, `RETURNING`, `EXCEPTION` |
| `DELIVERED` | dowód doręczenia | `CLOSED`, `RETURN_REQUESTED` |
| `CANCELLED` | aktualne anulowanie i brak nieodwracalnej wysyłki | stan końcowy |

## Idempotencja

Klucz zadania nadania powinien być unikalny dla `accountId + checkoutForm.id + parcelSequence + carrierService`. Zapisz UUID polecenia **przed** `POST`. Po timeout nie twórz kolejnego polecenia, dopóki nie sprawdzisz statusu pierwszego i istniejących przesyłek.

## Anulowania i race conditions

Zdarzenie anulowania może dotrzeć przed innym zdarzeniem albo po rozpoczęciu pakowania. Przed zakupem etykiety i przed wydaniem paczki wykonaj odczyt aktualnego zamówienia. Po pierwszym skanie przewoźnika nie anuluj automatycznie; uruchom procedurę przechwycenia/zwrotu i obsługę klienta.
