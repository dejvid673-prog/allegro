# Macierz wysyłek dla asortymentu RaFish

Weryfikacja sklepu: **2026-08-20** na [skleprafish.pl](https://skleprafish.pl/) i [stronie dostaw](https://skleprafish.pl/content/1-dostawy-i-platnosc). To kwalifikacja rodzin produktowych, nie gotowy cennik dla konkretnego SKU. Wdrożenie wymaga eksportu kartoteki z wagą i wymiarami po zapakowaniu.

## Profile opakowań

| Profil | Kryterium | Preferowana dostawa | Blokady/kontrole |
|---|---|---|---|
| `XS` | ≤0,5 kg, do 32,5 × 23 × 2 cm | MiniPrzesyłka lub automat | tylko produkt niepodatny na zgniecenie/wyciek |
| `S` | do 5 kg, mieści się w automacie | pełny Allegro Delivery + InPost | uszczelnienie cieczy, ochrona elektroniki |
| `M` | 5–15 kg, mieści się w automacie | Allegro Delivery/ InPost + kurier | One punkt/automat ma obecnie 15 kg w tabeli WzA; nie zakładaj 20 kg dla każdej metody |
| `H20` | 15–20 kg | DPD punkt/automat, wybrane AD, InPost, kurier | konkretne limity metody i wymiarów; dowód wagi |
| `H25` | >20–25 kg | kurier; InPost tylko przy bezpiecznym buforze i gabarycie | rzeczywista masa z opakowaniem ≤25 kg |
| `H31` | >25–31,5 kg | DPD kurier / zweryfikowana metoda | bez punktów/automatów; koszt dopłat w marży |
| `LONG` | bok >120 cm | kurier odpowiedniej usługi | dokładny limit długości; możliwy kurierski wyjątek Smart |
| `PALLET` | >31,5 kg lub wiele ciężkich worków | paleta/półpaleta | nie dziel automatycznie bez kalkulacji wielu paczek |
| `LIQUID` | płyn/żel/dip | automat lub kurier zależnie od masy | szczelna zakrętka, worek, absorbent, pion, test wycieku |
| `CLP` | substancja/mieszanina klasyfikowana | metoda zatwierdzona na podstawie SDS | zakaz automatycznego nadania bez klasyfikacji transportowej |
| `LIVE` | żywa ryba | specjalna umowa i opakowanie dobrostanowe | pogoda, pon.–śr., tlen, czas, odbiór; brak zwykłego Smart |
| `HIGH_VALUE` | kamera/elektronika o wysokiej wartości | kurier/punkt z trackingiem i ubezpieczeniem | plomba, numer seryjny, dowód pakowania |

## Rodziny produktów

| Asortyment widoczny w sklepie | Profil domyślny | Rekomendacja | Szczególne ryzyko |
|---|---|---|---|
| kulki, dumbellsy, waftersy, pellety, method mix, zanęty | `XS/S`, większe zestawy `M` | pełny AD + InPost; prawdziwe wielopaki pomagają osiągnąć próg Smart | alergeny/skład, termin, zapach; nie twórz sztucznego mieszanego zestawu dla pozycjonowania |
| karma dla ryb i wylęgów | `S/M/H20` | automat/punkt do limitu, kurier dla worków | oznakowanie paszy, partia, termin, wilgoć i szkodniki |
| preparaty, bakterie i suplementy HelpFish | `S/LIQUID`, kanistry `H20/H25` | małe pojemności automat/kurier; duże kurier | wyciek, temperatura, legalne twierdzenia i instrukcja dawkowania |
| antyglon i chemia stawowa | `LIQUID/CLP` | dopiero po SDS/CLP i akceptacji przewoźnika | towar zakazany/warunkowy, UFI, piktogramy, niezgodny transport |
| kreda 10 kg | `M/H20` | automat tylko po pomiarze; kurier jako stabilna opcja | pylenie, uszkodzenie worka, masa gabarytowa |
| kreda 24 kg | `H25` | domyślnie DPD kurier | opakowanie może zbliżyć paczkę do limitu InPost 25 kg |
| kreda/wapno 25 kg | `H31` | DPD kurier; paleta przy wielu sztukach | masa netto + opakowanie przekracza 25 kg; wapno palone wymaga odrębnej oceny reaktywności/CLP |
| rośliny do stawu | `S`, sezonowo `SPECIAL` | kurier/automat tylko po testach czasu i temperatury | przesuszenie, mróz/upał, roślina chroniona/inwazyjna |
| siatki, pułapki, żaki | `S/M/LONG` | manualna kwalifikacja prawna przed logistyką | część narzędzi połowowych może być zakazana na Allegro |
| pompy, napowietrzanie | `S/M/HIGH_VALUE` | AD + InPost, cięższe kurier | kruche króćce, gwarancja, numer seryjny, elementy mokre/elektryczne |
| kamery 4G/Wi‑Fi/solar, powerbanki | `S/HIGH_VALUE` | tracking, ubezpieczenie; punkt lub kurier | akumulator litowy, numer seryjny, stan plomby i cyberbezpieczeństwo produktu |
| wędki | `LONG` | DPD lub usługa dopuszczająca długość tuby | długość po zapakowaniu, zgniecenie, dopłata niestandardowa |
| kołowrotki, przynęty i drobne akcesoria | `XS/S` | pełny AD + InPost | ochrona haczyków/ostrzy, autentyczność marki |
| odzież | `S` | pełny AD + InPost | tabela rozmiarów i wysoki udział zwrotów |
| żywe ryby ozdobne | `LIVE` | ogłoszenie, odbiór lub zatwierdzona wysyłka żywych zwierząt | dobrostan, gatunek, pogoda, dokumentacja weterynaryjna, brak Smart |
| bony/vouchery | zależnie od reguły kategorii | kanał elektroniczny, jeśli regulamin kategorii go dopuszcza | ważność, sposób realizacji; nie udawaj fizycznej paczki Smart |

## Krytyczne niespójności wykryte na stronie RaFish

Publiczna strona kategorii żywych ryb i strona dostaw pokazują **dwa różne numery weterynaryjnego zatwierdzenia transportu**. Publikacja ofert żywych ryb i automatyczne kopiowanie tej informacji są zablokowane do czasu potwierdzenia prawidłowego numeru w dokumencie źródłowym i ujednolicenia wszystkich kanałów.

Strona sklepu podaje standardowo 2–4 dni robocze, a w szczycie 5–7. Dla żywych ryb podaje odrębny, sezonowy proces. Nie wolno przenieść ogólnego czasu sklepu do Allegro bez pomiaru cutoffu i pierwszego skanu przewoźnika.

## Cennik sklepu jako punkt porównawczy, nie cennik Allegro

Strona RaFish wyświetlała 2026-08-20 następujące stawki kanału własnego:

| Dostawa sklepu | Przedpłata | Pobranie |
|---|---:|---:|
| InPost automat | 16,00 zł | — |
| kurier standard | 17,00 zł | 19,00 zł |
| żywe ryby | 70,00 zł | według procesu sklepu |
| Geodis półpaleta 100–300 kg | 210,61 zł | 242,61 zł |
| Geodis paleta 301–700 kg | 279,23 zł | 299,34 zł |
| Geodis paleta 701–1000 kg | 322,90 zł | 343,35 zł |

Przed użyciem trzeba potwierdzić, czy kwoty są brutto/netto i aktualne. Na Allegro maksymalna stawka kupującego dla metod Smart jest niższa, a część kosztu ponosi sprzedawca. Dla palet i żywych ryb należy stworzyć osobny profil oraz sprawdzić, czy dana metoda może być udostępniona w kategorii i na warunkach umowy — nie kopiować `70 zł` ani stawki Geodis do cennika Allegro bez tej weryfikacji.

## Dane brakujące do kwalifikacji SKU

Eksport z PrestaShop/BaseLinkera powinien dostarczyć: SKU, EAN, nazwę, rodzinę, stan fizyczny, masa netto, masa zapakowana, trzy wymiary, typ opakowania, maksymalna liczba sztuk/paczkę, kruchość, płyn, akumulator, SDS/CLP, wartość ubezpieczenia, temperatura minimalna/maksymalna, czas kompletacji i koszt pełny. Bez tych pól profil pozostaje `UNQUALIFIED`.
