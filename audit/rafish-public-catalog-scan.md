# Publiczny skan asortymentu RaFish

Data skanu: **2026-08-20**. Źródła: [mapa strony](https://skleprafish.pl/Mapa%20strony), [strona kategorii głównej](https://skleprafish.pl/2-strona-glowna) i wybrane strony kategorii/produktów. Sklep jest dynamiczny, więc liczby i dostępność są migawką. To nie zastępuje eksportu wszystkich SKU z PrestaShop.

## Drzewo oferty — klastry

| Klaster | Kategorie widoczne publicznie | Profil operacyjny |
|---|---|---|
| ciężkie stawowe | Kreda i Wapno; KREDA; WAPNO TLENKOWE/PALONE | `H20/H25/H31/PALLET`, CLP dla wapna/reactive |
| żywe | Żywe RYBY; Tołpygi i wiosłonosy; zestawy rybne | `LIVE`, ogłoszenie, dokumenty/gatunek/pogoda |
| przynęty miękkie | kulki haczykowe/pop-up/zanętowe, larwy, ślimaki, dumbellsy, waftersy, ciasta/pasty | `XS/S`, spożywczo-paszowe/etykietowe zależnie od klasyfikacji |
| mieszanki i karmy | zanęty Premium/Economy/klasyczne/ready, pellety/granulaty, Method Mix, mixy PVA, karmy dla ryb/wylęgów | `S/M/H20`, wilgoć, partia, etykieta paszowa |
| płyny/aromaty | dipy, aromaty, smoke, zalewy, boostery, żele | `LIQUID`, test szczelności i warunki składu |
| chemia/preparaty | antyglon, preparaty, suplementy, bakterie, HelpFish | `LIQUID/CLP`, kwalifikacja biobójcza/weterynaryjna i przewoźnik |
| staw techniczny | torf, rośliny, siatki ochronne, pompy natleniające i akcesoria | `S/M/SPECIAL`, sezon/kruchość/ryzyko prawne narzędzi połowowych |
| feeder/karp | przypony, haki, pudełka, koszyczki, igły, stopery, spomb, ciężarki, markery, podpórki | `XS/S`, bezpieczne opakowanie ostrzy |
| spinning/żywiec | przynęty na drapieżniki, obrotówki, twistery, akcesoria żywcowe/spławikowe | `XS/S`, ostrza/haki i ryzyko wybranych narzędzi połowowych |
| długie/duże | wędki spinningowe/karpiowe/feederowe/sumowe, pokrowce | `LONG`, tuba, dokładny bok i niestandard |
| sprzęt | kołowrotki, sprzęt feederowy/karpiowy, akcesoria Carphorse | `S/M/HIGH_VALUE` zależnie od SKU |
| elektronika | kamery 4G/Wi‑Fi/solarne, powerbanki, sygnalizatory | `HIGH_VALUE/BATTERY`, ubezpieczenie, numer seryjny, bateria |
| moda/gadżety | bluzy, koszulki i gadżety | `S`, tabela rozmiarów i rezerwa zwrotów |
| usługi/niematerialne | vouchery, rezerwacja łowiska | odrębny format/kategoria; nie udawać przesyłki Smart |
| zestawy | zestawy wędkarskie, HelpFish, Tołpygi/Wiosłonosy, „Zestawy” | prawdziwy skład `productSet`, łączna masa i koszt |

## Wielkość wybranych kategorii widoczna w sklepie

| Kategoria | Liczba widoczna podczas skanu | Znaczenie |
|---|---:|---|
| Kreda i Wapno | ok. 50 | wiele mas i form; nie jeden profil paczki |
| Żywe ryby | ok. 8 | proces specjalny, sezonowy |
| Zanęty wędkarskie | 30 | niska cena jednostkowa, potencjał prawdziwych wielopaków do Smart |
| HelpFish | 37 | duża grupa wymagająca audytu deklaracji i klasyfikacji |
| Preparaty/suplementy/bakterie | 40 | kategoria miesza m.in. ciężką kredę i preparaty — nazwa kategorii nie wystarcza do profilu |
| Kamery | 3 | wysoka wartość i elektronika/baterie |
| Nowe produkty | 7 | między innymi kanistry 5 l i 20 l |

Liczba strony sklepu może obejmować produkt niedostępny albo produkt obecny w więcej niż jednej kategorii. Operator deduplikuje po wewnętrznym ID/SKU/EAN, nie po nazwie i nie sumuje liczb kategorii.

## Krytyczne ryzyka treści wykryte publicznie

1. Część nazw/opisów HelpFish używa twierdzeń o zwalczaniu chorób, pasożytów, pleśniawki/ospa rybia lub określeń „leczniczy”. Może to zmieniać kwalifikację na produkt leczniczy weterynaryjny, biobójczy, dodatek paszowy albo produkt zakazany/warunkowy. **Nie kopiować tych twierdzeń do Allegro bez formalnej klasyfikacji i dokumentu.**
2. `ANTY GLON`, preparaty na organizmy i środki do wody wymagają sprawdzenia składu, etykiety, SDS, UFI/CLP i statusu biobójczego; sama nazwa „naturalny” nie jest dowodem bezpieczeństwa.
3. Wapno tlenkowe/palone jest innym ryzykiem niż kreda węglanowa. Nie mogą dzielić automatycznie profilu zgodności ani dostawy.
4. `Sieci, pułapki, żaki` wymagają ręcznego porównania z listą zakazanych narzędzi połowowych Allegro i prawem.
5. Żywe ryby wymagają weryfikacji gatunku (chroniony/inwazyjny), trybu ogłoszenia, dobrostanu i spójnego numeru dokumentu weterynaryjnego.
6. Kamery/powerbanki mogą zawierać akumulatory litowe; profil przesyłki musi znać typ i pojemność baterii.
7. Publiczne promocje i przekreślone ceny sklepu nie są automatycznie legalną ceną referencyjną promocji Allegro.

## Nietypowe warianty logistyczne zaobserwowane w nazwach

- worki/wiadra 10, 20, 24 i 25 kg oraz oferty wieloworkowe/paletowe;
- kanistry 5 l i 20 l;
- zanęty 1/3/5 kg, drobne opakowania 25–200 ml i wielopaki;
- pokrowce 150 cm oraz wędki wymagające tuby;
- zestawy łączące różne smaki/średnice i wiele opakowań;
- elektronika od kilkuset złotych.

Każda z tych cech wpływa jednocześnie na produkt katalogowy, parametry, zdjęcie, koszt, liczbę sztuk w paczce, Smart i zwroty.

## Co musi pochodzić z eksportu, nie z publicznego skanu

Pełna lista SKU i statusów, EAN, warianty, masa brutto po pakowaniu, trzy wymiary, skład/SDS, VAT, koszt zakupu/wytworzenia, zapas, numer partii/termin, bateria, licencje zdjęć, sprzedaż historyczna i rzeczywiste zwroty. Dopóki tych danych nie ma, macierz logistyczna jest rekomendacją rodziny, a nie automatyczną decyzją dla oferty.
