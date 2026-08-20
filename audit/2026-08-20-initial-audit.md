# Audyt początkowy Allegro / RaFish

Data: **2026-08-20**. Zakres: publiczne źródła Allegro, Swagger, publiczny sklep RaFish. Bez dostępu do konta Allegro, eksportu SKU, PrestaShop ani BaseLinkera nie można potwierdzić stanu konkretnych ofert i marż.

## Wynik

| Obszar | Status | Najważniejsze ustalenie |
|---|---|---|
| źródło prawdy API | OK | oficjalny Swagger: 201 paths, 267 operations, 967 schemas; katalog wygenerowany z SHA-256 |
| tworzenie/klonowanie | SPEC READY | neutralny szablon, aktualne produkty/parametry, diff i zatwierdzenie |
| duplikaty wielokontowe | HIGH | limit dwóch ofert tego samego nowego produktu w podkategorii obejmuje powiązane konta |
| obrazy AI | HIGH | pochodzenie trzeba deklarować przy pierwszym uploadzie; nieznane blokuje publikację |
| koszty | BLOCKED UNTIL DATA | brak eksportu zakupów/prowizji/pakowania/Ads; obowiązkowy kompletny kosztorys |
| Smart | SPEC READY | kryteria, metody i tabela wkładu udokumentowane; wymaga ustawień/konta runtime |
| ciężkie worki | HIGH | 24 kg ma mały bufor do 25 kg InPost; 25 kg netto wymaga kuriera/palety po pomiarze |
| żywe ryby | BLOCKED | ogłoszenie, specjalny transport i niespójne publiczne dane weterynaryjne |
| chemia/wapno palone | BLOCKED PER SKU | SDS/CLP i kwalifikacja przewoźnika przed ofertą/nadaniem |
| sieci/żaki/pułapki | MANUAL REVIEW | możliwe kategorie przedmiotów zakazanych/warunkowych |
| zwroty | CHANGE DUE | automatyczne refundacje Allegro zapowiedziane od 2026-09-01 |
| jakość | CHANGE DUE | zapowiedziane nowe progi od 2026-08-26; cel firmy ustawiony wyżej |
| Ads | MANUAL/REPORT | brak pełnego publicznego Ads API w Swaggerze; import raportów i rekomendacje |

## Asortyment rozpoznany publicznie

Kreda i wapno (w tym worki 10/24/25 kg), żywe ryby, przynęty i zanęty, pasze, preparaty/suplementy/bakterie, antyglon/chemia, rośliny, sieci/pułapki/żaki, pompy/napowietrzanie, odzież/powerbanki, kamery, wędki, kołowrotki, przynęty i akcesoria. Macierz: `docs/06-shipments/rafish-shipping-matrix.md`.

Pełniejsze drzewo kategorii i ryzyka publicznych opisów: `audit/rafish-public-catalog-scan.md`. Wykryto m.in. twierdzenia dotyczące chorób/pasożytów i „leczenia”, które wymagają formalnej kwalifikacji produktu przed użyciem na Allegro.

## Krytyczna niespójność do wyjaśnienia

Publiczna strona żywych ryb i strona dostaw RaFish podają dwa różne numery weterynaryjnego zatwierdzenia transportu. Nie kopiować żadnego do Allegro. Właściciel procesu musi porównać oba wpisy z ważnym dokumentem i ujednolicić sklep, Allegro, szablony oraz instrukcje magazynowe.

## Dane wymagane od firmy

1. Eksport ofert Allegro wszystkich powiązanych kont.
2. Eksport SKU z PrestaShop/BaseLinkera: EAN, zapas, masa netto/zapakowana, wymiary i koszt.
3. Cenniki Allegro oraz umowy i dopłaty przewoźników.
4. Dokumenty GPSR, SDS/CLP/UFI, etykiety pasz, dokumenty weterynaryjne i gatunki.
5. Rzeczywiste czasy: płatność→pakowanie→etykieta→pierwszy skan.
6. Rozliczenia Allegro: prowizje, Smart, Ads, wyróżnienia, zwroty i dopłaty.
7. Lista kont oraz dozwolony zakres automatyzacji per konto.

## Kolejność działań

1. Ujednolicić dane prawne i wybrać system master dla zapasu/ceny.
2. Zbudować kartotekę opakowań i zważyć SKU graniczne.
3. Zaimportować koszty i ustalić minimalną marżę rodzin.
4. Uruchomić read-only audyt ofert/duplikatów/braków.
5. Wdrożyć monitoring zamówień, skanów, zwrotów i jakości.
6. Testować tworzenie propozycji w Sandbox.
7. Dopiero potem ograniczone nadawanie i publikacja po zatwierdzeniu.
