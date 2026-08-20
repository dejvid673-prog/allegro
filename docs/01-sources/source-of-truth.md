# Źródło prawdy

Zweryfikowano: **2026-08-20**.

## Hierarchia

| Priorytet | Źródło | Do czego służy |
|---:|---|---|
| 1 | Oficjalny Swagger/OpenAPI | dokładny kontrakt HTTP: ścieżki, operacje, schematy, scope, deprecations |
| 2 | Aktualna odpowiedź API | stan danego konta, marketplace, kategorii, produktu, oferty i zamówienia |
| 3 | Changelog, Aktualności i Regulamin API | terminy zmian, migracje, zasady techniczne i sankcje |
| 4 | Poradniki Developer Portal | intencja procesu, kolejność wywołań, przykłady i pułapki |
| 5 | Pomoc dla Sprzedających i Regulamin Allegro | reguły oferty, zdjęć, tytułów, duplikatów i asortymentu |
| 6 | Oficjalne źródła prawa / organów | CLP, GPSR, prawo paszowe i obowiązki sektorowe |
| 7 | Zatwierdzone reguły firmy | standard marki, marża, pakowanie, dopuszczone przewoźniki, zatwierdzenia |
| 8 | Stara oferta, PrestaShop, BaseLinker | materiał wejściowy i dane pomocnicze; nigdy samodzielna podstawa zgodności |

## Dlaczego Swagger nie wystarcza

Swagger opisuje kształt API, ale nie gwarantuje aktualności danych biznesowych. Kategorie, parametry wymagane, wartości słownikowe, produkty, cenniki i ustawienia konta trzeba pobierać w czasie działania. Poradnik może opisywać proces lepiej niż schema, ale nie może nadpisać aktualnego kontraktu endpointu.

## Rozstrzyganie konfliktu

1. Zapisz oba twierdzenia i daty ich pozyskania.
2. Sprawdź, czy dotyczą tego samego marketplace, typu konta, kategorii i wersji media type.
3. Sprawdź aktualny Swagger i changelog.
4. Wykonaj odczyt na Sandboxie lub bezpieczny odczyt produkcyjny.
5. Jeśli konflikt dotyczy prawa lub możliwej utraty sprzedaży, zatrzymaj zapis i eskaluj.
6. Udokumentuj decyzję w audycie wraz z URL-em, datą i `Trace-Id`, jeśli użyto API.

## Dane zmienne, których nie wolno utrwalać jako stałe

- lista kategorii i informacja `leaf`;
- parametry kategorii, obowiązkowość i wartości słownikowe;
- produkt powiązany z ofertą i propozycje produktów;
- metody dostawy, cenniki, ograniczenia paczki, ubezpieczenie i pobranie;
- prowizje, opłaty, promocje i programy;
- status oraz reason zakończenia oferty;
- status zamówienia, anulowanie, rewizja i fulfillment;
- scope/token metadata i dostęp aplikacji;
- limity konkretnego zasobu;
- lista endpointów deprecated i terminy ich wyłączenia.

## Rejestr źródeł

Maszynowym rejestrem jest [`sources/registry.json`](../../sources/registry.json). Każdy rekord zawiera właściciela, poziom autorytetu, obszar zastosowania, datę ostatniej kontroli i częstotliwość przeglądu.

Minimalne zasady utrzymania:

- Swagger: kontrola codzienna i porównanie hash/schematów;
- news/changelog/status: kontrola codzienna;
- poradniki i help: co najmniej raz w miesiącu oraz po komunikacie o zmianie;
- prawo/regulaminy: kwartalnie i przy każdej zapowiedzianej zmianie;
- dokumenty firmy: przy zmianie produktu, dostawcy, opakowania lub etykiety.

## Stan na datę audytu

- oficjalny Swagger ma 201 ścieżek, 267 operacji i 967 schematów;
- produkcja: `https://api.allegro.pl`;
- Sandbox: `https://api.allegro.pl.allegrosandbox.pl`;
- sześć operacji jest obecnie oznaczonych `deprecated` w specyfikacji;
- liczby są snapshotem z 2026-08-20 i mają być odświeżane generatorem, nie ręcznie.

## Materiały nieoficjalne

Blogi, fora, przykłady Stack Overflow i kod innych integratorów mogą pomóc zrozumieć problem, ale nie są podstawą kontraktu ani zgodności. Każde ważne twierdzenie musi wskazywać źródło oficjalne lub być oznaczone jako hipoteza do testu.
