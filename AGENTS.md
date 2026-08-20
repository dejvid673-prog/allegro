# Instrukcja obowiązkowa dla Codex i agentów AI

Niniejszy plik obowiązuje w całym repozytorium.

## Misja

Pomagaj obsługiwać Allegro bez utraty ofert, sprzedaży, zgodności prawnej, danych kupujących ani kontroli nad kontem. Preferuj dowód i aktualny odczyt z API zamiast pamięci modelu lub starego payloadu.

## Źródło prawdy

Przed implementacją lub decyzją przeczytaj `docs/01-sources/source-of-truth.md`. W razie konfliktu stosuj kolejność:

1. aktualny oficjalny Swagger/OpenAPI;
2. aktualna odpowiedź API dla danego konta, marketplace, kategorii i produktu;
3. oficjalny changelog/aktualności oraz regulamin;
4. oficjalne poradniki Allegro i Pomoc dla Sprzedających;
5. zatwierdzone reguły firmy;
6. stara oferta, BaseLinker i PrestaShop jako źródła pomocnicze.

Przeczytaj też `BUSINESS_RULES.md`. Jakość sprzedaży jest priorytetem, a komplet kosztów jest obowiązkowy.

## Zasady bezwzględne

- Nie zapisuj sekretów, tokenów, danych kupujących ani etykiet wysyłkowych w Git.
- Wszystkie identyfikatory API przechowuj jako tekst, nawet jeśli wyglądają jak liczby.
- Nie powtarzaj `POST`, jeśli nie znasz wyniku pierwszej próby. Najpierw ustal stan po identyfikatorze/idempotency key.
- Do poleceń asynchronicznych używaj UUID, zapisuj go przed wywołaniem i odpytuj status operacji.
- Nie wysyłaj surowej odpowiedzi `GET` jako payload `PATCH/PUT`; zbuduj request z jawnie dozwolonych pól.
- Obsługuj `429` i `Retry-After`; nie uruchamiaj agresywnych pętli odpytywania.
- Zapisuj `Trace-Id`, kod HTTP, endpoint, typ operacji i zanonimizowany wynik.
- Nie publikuj oferty, jeśli brakuje danych obowiązkowych kategorii, GPSR lub właściwego profilu produktu.
- Nie kopiuj GTIN/EAN, kategorii, parametrów bezpieczeństwa, ceny, zapasu, dostawy ani informacji AI bez ponownej weryfikacji.
- Nie traktuj masy lub wymiarów sugerowanych przez AI/Allegro jako dowodu; źródłem ma być zweryfikowana kartoteka SKU.
- Nie automatyzuj żywych zwierząt jak zwykłej sprzedaży towarowej — jest to proces ogłoszeniowy.
- Nie twórz trzeciej oferty tego samego nowego produktu w tej samej podkategorii, także na innym powiązanym koncie.
- Nie publikuj ani nie proponuj ceny jako rentownej, dopóki wszystkie wymagane koszty nie mają stanu `KNOWN`, `ZERO_CONFIRMED` albo `NOT_APPLICABLE` z dowodem.
- Nie używaj wartości `0` jako zamiennika nieznanego kosztu.
- Nie uznawaj etykiety za nadanie; wymagaj pierwszego skanu/protokołu i monitoruj paczki bez ruchu.
- Nie optymalizuj Ads, czasu wysyłki ani liczby ofert kosztem jakości sprzedaży.

## Poziomy decyzji

| Poziom | Agent może | Przykłady |
|---|---|---|
| READ | wykonywać automatycznie | odczyt ofert, zdarzeń, brakujących parametrów, zamówień, statusów przesyłek |
| PROPOSE | przygotować bez wykonania | tytuł, opis, mapowanie kategorii, zmiana ceny, wznowienie oferty |
| APPROVE | czekać na zatwierdzenie | publikacja nowej oferty, masowa edycja, wznowienie zakończonej oferty |
| RESTRICTED | wymaga osobnego uprawnienia i dodatkowej kontroli | zakończenie/usunięcie ofert, zwroty pieniędzy, anulowanie przesyłek, działania na wielu kontach |

Domyślny poziom dla operacji zapisu to `APPROVE`.

## Tworzenie oferty ze starej

Stara oferta jest inspiracją, nie szablonem do skopiowania 1:1. Procedura:

1. odczytaj pełny stan źródłowej oferty i oznacz jego czas;
2. pobierz aktualny produkt, kategorię, parametry i ograniczenia;
3. wyodrębnij pola do neutralnego `OfferTemplate`;
4. odrzuć pola serwerowe, identyfikatory i wartości zmienne;
5. nadpisz cenę, zapas, logistykę i compliance z właściwych źródeł;
6. wykonaj walidację statyczną oraz preflight API;
7. pokaż różnice i ryzyka użytkownikowi;
8. po zatwierdzeniu opublikuj i zweryfikuj status operacji.

## Modyfikowanie dokumentacji

- Każde nowe źródło dodaj do `sources/registry.json`.
- Każdy fakt czasowo zmienny oznacz datą weryfikacji.
- Nie przepisuj pełnego Swaggera; odśwież generowany katalog skryptem.
- Zmianę niekompatybilną dodaj do `docs/09-change-management/2026-changes.md` i do testów regresji.
- Fakty prawne oznacz jako wymagające kontroli specjalisty; ta dokumentacja nie jest poradą prawną.

## Kryterium ukończenia operacji

Sukces odpowiedzi HTTP nie wystarcza. Operacja jest ukończona dopiero po:

1. sprawdzeniu końcowego statusu lub operacji Command;
2. weryfikacji oczekiwanego stanu zasobu;
3. zapisaniu wyniku i `Trace-Id`;
4. zasygnalizowaniu błędów częściowych;
5. bezpiecznym oznaczeniu zadania jako wykonane, aby retry nie utworzył duplikatu.
6. przeliczeniu i zapisaniu rzeczywistego kosztu, jeśli operacja generuje opłatę.
