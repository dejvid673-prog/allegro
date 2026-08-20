# Profile produktów RaFish / HelpFish / StawExpert

Ten dokument jest checklistą integracyjną, nie poradą prawną. Jeśli klasyfikacja produktu jest niejasna, publikację blokuje się do czasu sprawdzenia przez osobę kompetentną i zapisania dokumentu źródłowego.

## Wybór profilu

| Profil | Przykłady | Tryb Allegro | Główne ryzyko |
|---|---|---|---|
| `pond_chemical` | preparaty do wody, środki stawowe, mieszaniny | oferta produktowa, o ile dozwolona | CLP/UFI, zakazy substancji, transport |
| `fish_feed` | karma dla koi, karpi, ryb ozdobnych | oferta produktowa | prawo paszowe, skład, dawkowanie, podmiot odpowiedzialny |
| `live_fish_classified` | żywe ryby ozdobne | wyłącznie ogłoszenie | dobrostan, transport, gatunki chronione/inwazyjne |
| `general_goods` | akcesoria nieobjęte specjalnym profilem | oferta produktowa | GPSR, parametry i prawa do treści |

Jeśli produkt pasuje do kilku profili, stosuj sumę wymagań i najbardziej restrykcyjny tryb.

## Chemia stawowa (`pond_chemical`)

### Twarde blokady

- produkt należy do kategorii chemii, której Allegro zakazuje;
- zawiera fosforek glinu jako substancję czynną;
- brak klasyfikacji: czy produkt jest substancją/mieszaniną stwarzającą zagrożenie;
- niezgodność etykiety z opisem lub językiem rynku;
- brak wymaganych danych CLP widocznych na etykiecie lub w opisie;
- brak możliwości legalnego i bezpiecznego transportu wybraną metodą;
- twierdzenia biobójcze/ochrony roślin bez właściwej podstawy i dopuszczenia.

### Dane do zebrania z etykiety/dokumentów

- nazwa, adres i telefon dostawcy/producenta/dystrybutora;
- nominalna ilość;
- identyfikator produktu;
- piktogramy zagrożenia;
- hasło ostrzegawcze;
- zwroty H i P;
- informacje uzupełniające z art. 25 CLP;
- UFI, jeśli wymagany;
- karta charakterystyki i wersja/data jako dokument wewnętrzny;
- ograniczenia magazynowania, temperatury, przewozu i marketplace;
- podstawa do każdego twierdzenia o działaniu produktu.

### Zdjęcia

- przód realnego opakowania;
- czytelna etykieta z wariantem/pojemnością;
- piktogramy i UFI, jeśli wymagane;
- nie zastępuj realnej etykiety wygenerowaną makietą AI.

### Reguła językowa

Produkt powinien mieć etykietę w języku kraju docelowego. Sama automatyczna translacja oferty nie tłumaczy fizycznej etykiety.

## Karma dla ryb (`fish_feed`)

Oficjalne źródła kontroli sprzedaży na odległość wskazują, że oferta/materiały towarzyszące muszą zawierać wymagane dane paszy, nie tylko zdjęcie opakowania.

### Minimalne dane

- rodzaj: materiał paszowy / pasza pełnoporcjowa / uzupełniająca itp.;
- gatunek/kategoria zwierzęcia i, jeśli dotyczy, etap życia;
- instrukcja prawidłowego stosowania i dawkowanie;
- warunki przechowywania przed i po otwarciu;
- minimalny okres trwałości na opakowaniu i obsługa partii w magazynie;
- skład/materialy paszowe w odpowiedniej kolejności;
- dodatki paszowe z właściwą kategorią/grupą;
- składniki analityczne wymagane dla danego typu paszy;
- dane podmiotu odpowiedzialnego za etykietowanie;
- kanał do uzyskania informacji dodatkowych;
- identyfikacja partii oraz numer zatwierdzenia/rejestracji zakładu, jeśli dotyczy;
- masa netto i wariant granulacji spójne we wszystkich polach.

### Twarde blokady

- brak rodzaju paszy, przeznaczenia, dawkowania lub składu;
- SKU/tytuł mówi o innej masie lub granulacji niż etykieta;
- deklarowany surowiec/korzyść nie ma potwierdzenia w etykiecie lub specyfikacji;
- data/partia nie może być kontrolowana przez magazyn;
- produkt faktycznie jest weterynaryjnym produktem leczniczym, a nie zwykłą paszą — wymaga innej ścieżki i uprawnień.

### Logistyka

Karmy i ciężkie worki łatwo powodują dopłaty. Waga wysyłkowa obejmuje opakowanie i wypełnienie, a nie tylko masę netto. Profile paczek powinny rozdzielać opakowania jednostkowe i wielosztuki.

## Żywe ryby (`live_fish_classified`)

### Tryb

Oferty w kategorii Żywe zwierzęta mają wyłącznie charakter ogłoszeniowy. Nie kieruj ich do standardowego pipeline `READY_FOR_PROCESSING → przesyłka`.

### Twarde blokady

- próba utworzenia zwykłej oferty produktowej zamiast ogłoszenia;
- brak potwierdzenia gatunku (nazwa zwyczajowa i naukowa w kartotece);
- gatunek chroniony lub inwazyjny albo brak sprawdzenia list;
- brak humanitarnego sposobu transportu;
- brak możliwości obejrzenia hodowli i odbioru;
- automatyczny wybór zwykłego kuriera bez zatwierdzonej usługi do żywych zwierząt;
- nieprawdziwe zdjęcie wygenerowane przez AI przedstawiające konkretną sztukę jako realną.

### Dane ogłoszenia

- gatunek, odmiana, przybliżony rozmiar/wiek i liczba;
- realne zdjęcia oferowanych zwierząt lub jasno opisanej partii;
- warunki utrzymania i zdrowotne, jeśli są istotne i potwierdzone;
- zasady obejrzenia hodowli i odbioru;
- dokładny plan humanitarnego transportu, terminy i ograniczenia pogodowe;
- wymagane dokumenty i metryka, jeśli dotyczą gatunku;
- sezonowość i ręczne okno aktywności ogłoszenia.

### Operacje

- monitoruj datę końca płatnego pakietu ogłoszenia;
- wznowienie zawsze wymaga potwierdzenia bieżącej dostępności zwierząt;
- kontakt i finalizacja muszą pozostać zgodne z aktualnymi zasadami Allegro;
- nie przesyłaj danych kupującego do systemów, które nie są niezbędne do obsługi kontaktu/transportu.

## General goods

Nawet gdy produkt nie jest chemią, paszą ani żywym zwierzęciem, wymagaj:

- poprawnego produktu/kategorii/GTIN;
- GPSR i instrukcji bezpieczeństwa, jeśli dotyczą;
- realnych danych opakowania i logistyki;
- praw do zdjęć i opisów;
- braku przedmiotu na liście zakazanej;
- zgodności z rynkiem docelowym.

## Evidence pack

Każdy produkt powinien wskazywać wersjonowany zestaw dowodów:

```text
product_compliance_profile
document_id / source_url
document_type
issuer / owner
valid_from / valid_until
applies_to_sku_or_batch
verified_by / verified_at
extracted_fields + confidence
file_hash
```

Agent może ekstrahować pola, ale osoba zatwierdzająca potwierdza ich zgodność z oryginałem.
