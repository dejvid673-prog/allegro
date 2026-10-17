# Allegro MCP — fundament techniczny (2026-10-17)

Status: **OFFLINE READ-ONLY / PROTOTYPE**. Kanoniczne repo wiedzy: `dejvid673-prog/allegro`. Nie jest to podłączone konto sprzedawcy ani usługa produkcyjna.

## Zakres pierwszego uruchamialnego etapu

- `allegro_catalog_status`: metadane migawki OpenAPI, zakres i wiek dokumentacji.
- `allegro_find_read_endpoints`: wyszukiwanie operacji `GET` w zapisanym katalogu.
- `allegro_get_read_endpoint`: szczegóły jednej operacji `GET` z katalogu.

Wszystkie trzy narzędzia czytają wyłącznie lokalne pliki JSON z tego repo. Nie odczytują ani nie wysyłają tokenów, nie mają funkcji HTTP ani zapisu, nie przetwarzają zamówień i nie wykonują działań na ofertach. Katalog jest migawką z **2026-08-20**, a nie gwarancją aktualnego API.

SDK: oficjalny [MCP Python SDK v2](https://py.sdk.modelcontextprotocol.io/) (wersja przypięta w `requirements-mcp.txt`); protokół: [MCP 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28). Uruchamianie lokalne przez **stdio**, bez portu. Serwer nie jest wystawiany przez HTTP i nie ma uwierzytelnienia dla zdalnych użytkowników.

### Ścieżka uruchomienia po uzyskaniu komputera

```bash
python -m pip install -r requirements-mcp.txt
python -m allegro_mcp.server
```

MCP Inspector/klient otwiera proces jako stdio. Sam proces pozostaje uruchomiony i oczekuje na klienta; nie służy do ręcznego wpisywania poleceń w konsoli. Testy offline: `python -m unittest discover -s tests -v`. Smoke MCP: `python scripts/smoke_mcp.py`. GitHub Actions sprawdza oba.

### Granice bezpieczeństwa kolejnego etapu

1. Przed odczytami konta: zarejestrowana aplikacja Allegro, własny stabilny `User-Agent`, autoryzacja sprzedawcy przez OAuth, poprawna tożsamość konta i minimalne scope. **Żadnych** sekretów w GitHub.
2. Dwa oddzielne uwierzytelnienia: *klient MCP → serwer* oraz *serwer → Allegro*. Sam token Allegro nie daje uprawnienia nieznanym klientom MCP. Zdalny Streamable HTTP jest **BLOCKED**, dopóki oba modele nie zostaną zaimplementowane, przetestowane i zatwierdzone.
3. Odczyt danych zamówień i wiadomości obejmuje PII: potrzebne ograniczenia pól, powiązanie tożsamości użytkownika z kontem, kontrola dostępu, retencja oraz polityka eksportu do modelu AI. W pierwszym etapie brak takich narzędzi.
4. Używaj wyłącznie jawnych typowanych narzędzi i allowlisty operacji/hostów; nie dodawaj narzędzia dowolnego `GET URL`, raw `POST` czy uploadu. `GET` nie oznacza braku danych wrażliwych.
5. Zapis do Allegro pozostaje zablokowany. Wymaga pełnych kosztów, modeli master-data, dowodu zgodności produktów, jawnego zatwierdzenia, trwałych identyfikatorów operacji i weryfikacji skutku. W szczególności nie ma automatycznego powielania ofert między kontami.
6. Katalog API: pobranie nowego Swaggera → niezależna kontrola różnic → PR z nową migawką → testy regresji → dopiero po zatwierdzeniu. Nie przyjmuj automatycznie obcego kontraktu, nie ukrywaj różnicy hash.

## Próby i bramy wdrożeniowe

| Etap | Dowód | Stan 2026-10-17 |
|---|---|---|
| Repo i dokumentacja biznesowa | dotychczasowe pliki | PASS (istnienie), wymagają okresowej weryfikacji |
| MCP offline knowledge tools | kod + testy SDK/CI | do zweryfikowania na PR |
| Aktualna migawka OpenAPI | regeneracja + diff od 2026-08-20 | HOLD |
| OAuth i sesja sprzedawcy | sandbox + scoped token + rotacja | NOT IMPLEMENTED |
| Realne operacje GET | test sandbox, mocki, ograniczenia PII | NOT IMPLEMENTED |
| MCP zdalny / produkcyjny | inbound auth, approval, deployment tests | BLOCKED |
| Zapisy i obsługa zleceń | osobny projekt i akceptacja | BLOCKED |

Repo `7dejv-agent-os` dostarcza polityki ogólne. Repo `7dejv-mcp` to odrębne materiały architektoniczne, a `mcp` ma osobny serwer i implementację ERLI. Nie przenosimy kodu/sekretów bez audytu kontraktów i jednoznacznej decyzji o odpowiedzialności. Źródłem prawdy domeny Allegro pozostaje to repo.

## Źródła

- https://developer.allegro.pl/swagger.yaml
- https://developer.allegro.pl/documentation
- https://developer.allegro.pl/tutorials/informacje-podstawowe-b21569boAI1
- https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR
- https://modelcontextprotocol.io/specification/2026-07-28
- https://py.sdk.modelcontextprotocol.io/
