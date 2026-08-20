# Rejestr źródeł

`registry.json` jest listą źródeł wykorzystywanych przez dokumentację i przyszły Change Watcher.

## Pola

- `id` — stabilny identyfikator;
- `title` — nazwa czytelna dla człowieka;
- `url` — bezpośredni adres oficjalnej strony/pliku;
- `owner` — organizacja odpowiedzialna za treść;
- `kind` — typ materiału;
- `authority` — poziom rozstrzygający od 1 (najwyższy) do 8;
- `areas` — obszary systemu;
- `review_cadence` — częstotliwość ponownej kontroli;
- `last_verified` — data ręcznej lub automatycznej kontroli;
- `status` — `active`, `planned`, `deprecated`, `archived` albo `context-only` dla materiału nieoficjalnego;
- `notes` — ograniczenia interpretacji.

Nie przechowujemy tutaj kopii stron ani dokumentacji chronionej prawem autorskim. Generator zachowuje tylko metadane i własny indeks operacji na podstawie oficjalnego Swaggera.
