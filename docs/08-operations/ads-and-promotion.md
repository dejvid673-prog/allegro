# Allegro Ads, wyróżnienia i promocje

Weryfikacja: **2026-08-20**. Główne źródła: [Allegro Ads](https://help.allegro.com/pl/sell/c/podstawowe-informacje-o-allegro-ads) i [wyróżnienia](https://help.allegro.com/pl/sell/a/czym-sa-wyroznienia-czyli-opcje-promowania-nnkeyKZLlUY).

## Granica integracji

Publiczny Swagger Allegro REST API nie zawiera obecnie ogólnego API do zarządzania kampaniami Allegro Ads. REST API ma zasoby promocji ofert, programów rabatowych i kampanii, ale nie należy utożsamiać ich z pełnym panelem Ads. Dlatego pierwszy operator:

- pobiera/ingestuje raporty Ads lub dane z zatwierdzonego źródła;
- oblicza rekomendacje budżetu i listę ofert;
- zmiany w panelu Ads pozostawia jako `APPROVE`, a automatyzację przeglądarkową rozważa dopiero po testach i zgodzie.

## Oferty sponsorowane

Model rozliczenia to CPC — koszt kliknięcia. Konfiguracja obejmuje grupę reklam, dobór ofert, miejsca emisji, budżet dzienny, stawkę CPC i typ licytacji. Dynamiczne CPC może podwyższać/obniżać stawkę w zależności od prognozy sprzedaży, więc limit budżetu i ekonomia SKU pozostają obowiązkowe.

W Dynamicznym CPC maksymalna stawka pojedynczego kliknięcia może sięgnąć **2 × ustawionego celu średniego CPC**, a system dąży do średniej równej celowi. Cel Dynamicznego CPC musi być co najmniej 25% wyższy od najwyższego minimalnego CPC w grupie. Mieszanie kategorii z różnymi minimami podnosi minimum całej grupy — rodziny RaFish należy rozdzielać.

### Minimalne CPC allegro.pl — wybrane działy RaFish

| Dział | Wyniki wyszukiwania | Inne miejsca |
|---|---:|---:|
| Supermarket | 0,75 zł | 0,65 zł |
| Dom i ogród | 0,75 zł | 0,65 zł |
| Elektronika | 0,75 zł | 0,65 zł |
| Sport i turystyka | 0,70 zł | 0,60 zł |

Dokładną kategorię oferty i minimum sprawdź w [bieżącym cenniku Ads](https://help.allegro.com/pl/sell/a/ile-kosztuje-i-jak-jest-rozliczana-reklama-w-allegro-ads-v875Pq01Ruo). Minimalny budżet dzienny Ofert sponsorowanych na allegro.pl wynosi obecnie 3 zł dla emisji tylko w Allegro oraz 10 zł, gdy obejmuje Google; nie oznacza to sensownego budżetu testu.

Od 2026-07-29 Allegro co minutę kontroluje tempo wydatków i może automatycznie obniżać CPC, aby kampania nie wyczerpała budżetu zbyt wcześnie. Po 22:00 mechanizm się wyłącza. Analiza godzinowa musi uwzględniać tę zmianę; spadek CPC nie musi być ręczną edycją.

Minimalny zestaw raportowy dziennie:

| Metryka | Wzór / interpretacja |
|---|---|
| CTR | kliknięcia / wyświetlenia |
| CPC | koszt / kliknięcia |
| CVR Ads | zamówienia przypisane / kliknięcia |
| CPA | koszt / zamówienia przypisane |
| ROAS | przychód przypisany / koszt Ads |
| marża po Ads | przychód netto − wszystkie koszty produktu/logistyki/Allegro − Ads |
| break-even CPC | marża przed Ads × spodziewana konwersja kliknięcia |
| udział nowej sprzedaży | sprzedaż inkrementalna, a nie tylko przypisana |

Panel atrybuuje m.in. zainteresowanie, sztuki i wartość sprzedaży przez 7 dni po kliknięciu. Dlatego wynik dzisiejszej kampanii nie jest kompletny dzisiaj, a sprzedaż przypisana nie jest automatycznie sprzedażą wywołaną reklamą.

ROAS może wyglądać dobrze przy nierentownym produkcie. Decyzją nadrzędną jest dodatnia marża po Ads oraz brak pogorszenia jakości sprzedaży.

## Eksperyment startowy

1. Wybierz 5–10 aktywnych ofert z kompletnym kosztorysem, dobrym zdjęciem, parametrami, Smart i zapasem na minimum 14 dni.
2. Rozdziel kampanie według rodziny i marży; nie mieszaj tanich zanęt z drogimi kamerami.
3. Ustal dzienny limit straty oraz maksymalny CPA z marży.
4. Nie zmieniaj jednocześnie ceny, miniatury i CPC.
5. Zbieraj dane minimum kilka dni i przez pełny rytm tygodnia; niskowolumenowe SKU oceniaj dłużej.
6. Zatrzymaj ofertę po przekroczeniu limitu kliknięć bez sprzedaży, ale uwzględnij opóźnienie atrybucji.
7. Skaluj budżet stopniowo tylko przy dodatniej marży po Ads.

## Wyróżnienia — bieżące stawki brutto allegro.pl

| Opcja | Opłata cykliczna | Dodatkowa prowizja |
|---|---:|---:|
| Wyróżnienie Elastyczne | 2,90 zł / 1 dzień | 0,75 × prowizja podstawowa kategorii |
| Wyróżnienie | zwykle 19,90 zł / 10 dni; wybrane kategorie 2,90 lub 5,90 | 0,75 × prowizja podstawowa kategorii |
| Promowanie na stronie działu | 29,90 zł / 10 dni | brak |

Opłatę pobiera się z góry za cykl i może odnawiać automatycznie. Przed zakończeniem/wznowieniem oferty sprawdź, czy promowanie również się wznowi i naliczy opłatę. Koszt stały oraz dodatkowa prowizja muszą trafić do `costs.promotion*`.

## Warunki i selekcja

Promowanie wymaga konta firmowego i odpowiedniej jakości; jeżeli jakość spadnie poniżej `Neutralny`, opcje mogą zostać wyłączone po okresie ochronnym. Oferta musi spełniać warunki formatu/kategorii i nie każdy typ zestawu jest dopuszczony. Sprawdź bieżącą kwalifikację w panelu przed uruchomieniem.

Wyróżnienie warto testować, gdy oferta jest już konkurencyjna i dobrze konwertuje. Promowanie słabej karty produktu kupuje ruch do problemu, zamiast go naprawiać.

## Programy cenowe

Allegro Ceny, AlleObniżka i akcje sezonowe mają odrębne zasady wyrównania, ceny referencyjnej, dodatkowej prowizji i oznaczenia najniższej ceny. Każda akcja wymaga oddzielnej symulacji:

`wynik = przychód po obniżce + potwierdzone wyrównanie − pełne koszty − opłaty akcji − wzrost zwrotów`.

Nie zakładaj, że wyrównanie jest gotówką ani że zadziała dla całej liczby sztuk. Zapisz limit, okres i sposób rozliczenia z regulaminu konkretnej kampanii.
