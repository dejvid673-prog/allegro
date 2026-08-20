# Reguły ofert: tytuł, opis, zdjęcia, GPSR, AI i duplikaty

Zweryfikowano: **2026-08-20**. Reguły mają poziom `BLOCKING`, `WARNING` albo `INFO`. Tylko oficjalne wymagania lub zatwierdzone twarde reguły firmy mogą blokować publikację.

## Tytuł

Aktualne ograniczenia Allegro:

- minimum 12 znaków;
- minimum 3 słowa;
- maksimum 75 znaków;
- bez powtarzania słów kluczowych;
- bez informacji o cenie, dostawie, fakturze, lokalizacji, loginie lub numerze magazynowym;
- bez pustych haseł promocyjnych typu „hit”, „okazja”, „promocja”, „gratis”, „najlepszy”;
- bez ozdobnych znaków i marek niezwiązanych z produktem.

Standard firmowy tytułu:

```text
<rodzaj produktu> <marka/linia> <zastosowanie lub gatunek> <wariant/masa/pojemność>
```

Przykład neutralny: `Karma dla karpi koi HelpFish granulat 3 mm 5 kg`.

Reguły automatyczne:

| ID | Warunek | Poziom |
|---|---|---|
| TITLE-001 | mniej niż 12 lub więcej niż 75 znaków | BLOCKING |
| TITLE-002 | mniej niż 3 tokeny słowne | BLOCKING |
| TITLE-003 | niezgodność wariantu/ilości z SKU | BLOCKING |
| TITLE-004 | podejrzane hasło promocyjne / dekoracyjne | WARNING lub BLOCKING wg listy |
| TITLE-005 | marka obca względem produktu | BLOCKING |
| TITLE-006 | nienaturalne powtarzanie słów | WARNING |

## Opis

Opis ma:

- dotyczyć wyłącznie oferowanego produktu i wariantu;
- być spójny z tytułem, kategorią, parametrami, zdjęciami i opakowaniem;
- zawierać faktyczne zastosowanie, zawartość zestawu, sposób użycia i ograniczenia;
- przenosić dane do dedykowanych pól, jeśli Allegro je udostępnia;
- nie zawierać danych kontaktowych, linków do zakupów poza Allegro ani instrukcji płatności;
- nie zawierać keyword stuffing i pustych deklaracji marketingowych;
- nie promować innych wariantów lub produktów tak, jakby były częścią tej oferty;
- nie składać twierdzeń medycznych, biobójczych, środowiskowych lub wydajnościowych bez dokumentu.

Zalecany układ:

1. jednoznaczna nazwa i przeznaczenie;
2. najważniejsze cechy potwierdzone parametrami;
3. zawartość i wariant;
4. instrukcja użycia/dawkowanie;
5. przechowywanie i bezpieczeństwo;
6. informacje prawne profilu produktu;
7. zawartość opakowania.

## Zdjęcia

Aktualne zasady techniczne/pomocowe:

- konto firmowe: do 16 zdjęć w galerii; ogłoszenia: do 40;
- oficjalne strony pomocy podają niespójne minima 400 lub 500 px; standard firmowy przyjmuje konserwatywnie dłuższy bok co najmniej 500 px, a limit runtime trzeba zweryfikować przy uploadzie;
- Allegro wyświetla maksymalnie 2560 × 2560 px;
- plik do 26 megapikseli;
- JPG/JPEG/PNG; API obsługuje również WebP zgodnie z dokumentacją;
- przestrzeń kolorów sRGB;
- tło może być dowolne — białe tło jest standardem firmowym dla głównego packshotu, a nie obowiązkiem Allegro;
- bez dodanego tekstu/logo sklepu; rzeczywiste napisy z produktu, opakowania i logo marki są dozwolone;
- infografiki nie są swobodnie dozwolone; korzystanie z rozszerzonych elementów wymaga zasad/zgody BrandHub.

Kontrole firmowe:

- zdjęcie główne pokazuje dokładnie oferowany wariant i ilość;
- dla chemii obowiązkowe czytelne zdjęcie etykiety i oznaczeń;
- dla karmy obowiązkowe zdjęcie etykiety/składu/masy;
- nie pokazuj większego zestawu niż sprzedawany;
- sprawdź rozdzielczość, format, profil barwny, perceptual hash i podobieństwo do ofert duplikujących;
- zachowaj dowód praw/licencji.

## Obrazy AI

Od 2026-08-02 trzeba informować o obrazach wygenerowanych lub istotnie zmodyfikowanych przez AI, jeśli spełniają ustawową definicję deepfake. Dotyczy to m.in. w pełni syntetycznych zdjęć produktu, wirtualnych modeli i generowanych tła, gdy zmiana jest istotna.

Zasady techniczne Allegro od 2026-07-29:

- używaj `aiCoCreatedContent.images` w obsługiwanych endpointach;
- decyzję przekazuje się przy pierwszym uploadzie obrazu;
- oznaczenia zapisanego dla pliku nie można później zmienić;
- przy obrazie już obecnym w bazie liczy się pierwotna deklaracja;
- brak pola oznacza brak żądania oznaczenia, dlatego agent nie może zgadywać „false” przy nieznanym pochodzeniu.

Macierz:

| Pochodzenie | Działanie |
|---|---|
| fotografia własna bez istotnej edycji AI | zapisz dowód, brak deklaracji AI |
| retusz techniczny bez istotnej zmiany treści | ręczna klasyfikacja według aktualnego FAQ |
| generowane tło / element produktu | oznacz zgodnie z zasadami i zachowaj prompt/workflow |
| obraz w pełni wygenerowany | oznacz, zweryfikuj brak wprowadzania w błąd |
| pochodzenie nieznane | BLOCKING — nie uploaduj |

## GPSR

Od 2024-12-13 dla objętych produktów wymagane mogą być:

- dane producenta;
- dane osoby odpowiedzialnej w UE, gdy producent jest spoza UE;
- informacje dotyczące bezpieczeństwa;
- spójność danych z etykietą/opakowaniem i dokumentami.

Allegro udostępnia zasoby producentów odpowiedzialnych, osób odpowiedzialnych i pól bezpieczeństwa. Agent może pomóc mapować zatwierdzony dokument, ale nie może wymyślać danych ani automatycznie akceptować sugestii wygenerowanej przez platformę.

## Duplikaty

Allegro dopuszcza maksymalnie dwie oferty tego samego produktu w stanie Nowy w tej samej podkategorii, licząc łącznie wszystkie konta sprzedającego/powiązane. Przy ocenie może porównywać produkt, parametry (w tym EAN) i miniaturę. Zestawy są oceniane odmiennie, ale „zestaw” musi być faktycznym zestawem, nie obejściem reguły.

Reguła `DUPLICATE-001`:

1. zbierz oferty z całej grupy kont;
2. dopasuj po product ID/GTIN i kategorii;
3. rozszerz wykrywanie o kluczowe parametry i podobieństwo obrazu;
4. policz aktywne oferty w condition `NEW`;
5. przy liczbie `>=2` zablokuj kolejną publikację i pokaż oferty kolidujące.

## Spójność oferty

Blokuj, gdy dowolne z poniższych się nie zgadza:

- masa/pojemność: tytuł ↔ parametry ↔ opis ↔ zdjęcie etykiety ↔ SKU;
- gatunek/przeznaczenie: tytuł ↔ kategoria ↔ pasza/produkt;
- ilość sztuk: zdjęcie ↔ `productSet` ↔ opis ↔ stock unit;
- producent/marka: katalog ↔ GPSR ↔ etykieta;
- deklaracje bezpieczeństwa: opis ↔ CLP/UFI ↔ zdjęcie;
- AI: asset registry ↔ upload ↔ `aiCoCreatedContent`;
- wysyłka: metoda ↔ profil produktu ↔ rzeczywista paczka.
