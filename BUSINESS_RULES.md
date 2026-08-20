# Reguły biznesowe RaFish dla Allegro

Stan: obowiązuje od **2026-08-20**. Zmiana tej listy wymaga jawnej decyzji właściciela procesu.

## Priorytety

1. **Jakość sprzedaży jest priorytetem.** Terminowość, zgodność towaru, szybka odpowiedź, poprawny zwrot i brak nierozwiązanych przesyłek są ważniejsze niż krótkotrwały wzrost liczby ofert.
2. **Każda oferta i każda decyzja cenowa ma kompletny rachunek kosztów.** Brak kosztu nie oznacza zera; oznacza `UNKNOWN` i blokuje automatyczną publikację lub zmianę ceny.
3. **Jedno źródło nadrzędne dla zapasu i ceny.** Przed integracją wybieramy system master dla każdego pola. Agent nie może rozstrzygać konfliktu PrestaShop–BaseLinker–Allegro przez „ostatni zapis wygrywa”.
4. **Dostawa wynika z zapakowanego SKU.** Masa, wymiary, podatność na wyciek, ADR/CLP, żywy organizm i wartość są danymi kartoteki, nie domysłem modelu.
5. **Ofertę klonujemy jako propozycję.** GTIN, produkt katalogowy, parametry, zdjęcia AI, bezpieczeństwo, cena, zapas i dostawa przechodzą ponowną walidację.

## Obowiązkowe koszty

Każdy wariant SKU × kanał × metoda dostawy musi zawierać co najmniej:

- koszt zakupu lub wytworzenia netto;
- transport przychodzący i koszt przyjęcia;
- opakowanie, wypełnienie, etykietę i pracę magazynu;
- prowizję podstawową Allegro i opłaty stałe;
- dopłatę Smart sprzedawcy oraz dopłaty przewoźnika za wagę, gabaryt, strefę, podjazd lub drugą paczkę;
- koszt płatności/pobrania, jeśli występuje;
- koszt promocji i przypisany koszt Allegro Ads;
- rezerwę na zwroty, szkody, braki i niesprzedawalny zwrot;
- VAT oraz informację, czy dane pole jest netto czy brutto;
- cenę minimalną, marżę kwotową i procentową po wszystkich kosztach.

Nie wolno zastępować kosztu wartością `0`, jeżeli koszt jest tylko nieznany. Schemat danych znajduje się w `templates/cost-model.schema.json`.

## Bramy publikacji

Publikacja jest zablokowana, jeżeli zachodzi przynajmniej jeden warunek:

- niespójny EAN/GTIN, SKU, produkt lub kategoria;
- brak parametru wymaganego albo planowanego jako wymagany;
- brak dowodów GPSR/CLP/paszowych lub niezweryfikowany status produktu żywego;
- nieznane pochodzenie zdjęcia AI;
- ryzyko trzeciej zduplikowanej oferty na powiązanych kontach;
- niezweryfikowana zapakowana masa/wymiary lub metoda nie przyjmuje towaru;
- niekompletny kosztorys albo marża poniżej zatwierdzonego minimum;
- niespójna polityka zwrotów, cennik dostaw, czas wysyłki lub adres nadania/zwrotu;
- produkt jest potencjalnie zakazany, reglamentowany lub przewoźnik nie potwierdził przyjęcia.

## Cele operacyjne

- zamówienie nie może zostać nadane dwa razy;
- etykieta nie oznacza nadania — wymagany jest pierwszy skan przewoźnika;
- każde zamówienie `READY_FOR_PROCESSING` ma właściciela, termin i stan realizacji;
- każdy zwrot ma termin decyzji i zwrotu środków, a każde zatrzymanie biegu terminu ma powód i dowód;
- każda oferta nieaktywna lub z błędem trafia do dziennego raportu wyjątków;
- automatyzacja nie obniża deklarowanego czasu wysyłki poniżej wyniku osiąganego w praktyce.
