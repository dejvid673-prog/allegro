# Codex — bootstrap analityki Allegro Ads STAW EXPERT

Wersja instrukcji: 2026-11-05. Właściciel: STAW EXPERT / 7DEJV OS. Status: instrukcja wykonania, a nie dowód instalacji. Działać na Windows / PowerShell.

## Cel
Zweryfikować najnowszy stan GitHub, pobrać zatwierdzone artefakty, zainstalować w Codex sprawdzone skille (bez nadpisywania istniejących), przetestować istniejący offline stack Allegro, przygotować operatora do importu XLSX Allegro Ads, przeprowadzić walidację i raportować dowody.

## Repozytoria (kanoniczne, NIE duplikować)
- `dejvid673-prog/7dejv-agent-os` — wspólne skille i workflow. Gałąź robocza `research/allegro-ads-profit-2026-11-05` zawiera kandydatów PR.
- `dejvid673-prog/allegro` — produktowa dokumentacja Ads, model importu, koszty, istniejące offline MCP.
- `dejvid673-prog/7dejv-skills-prompts` — router dla Codex; nie publikować treści repo prywatnego.
- `dejvid673-prog/7dejv-mcp` — osobna warstwa integracji; NIE modyfikować bez oddzielnego planu.

## Sekwencja
1. Sprawdź `git --version`, `gh --version`, `python --version`, `codex --version`, `git status --short`, `git remote -v`, dostęp SSH/HTTPS, uprawnienia do repo. Nigdy nie wklejaj tokenu do czatu/logu. Jeśli narzędzia nie istnieją, przedstaw bezpieczny plan instalacji z oficjalnego dostawcy; nie uruchamiaj nieznanych skryptów.
2. W istniejących klonach sprawdź `AGENTS.md`, gałąź, `git status --porcelain` i pliki lokalne. Nie nadpisuj zmian. Wykonaj `git fetch --prune`. Jeśli lokalny `main` jest czysty, `git pull --ff-only`; jeżeli nie, STOP dla tej gałęzi i użyj osobnego worktree/klonu. Gałąź PR otwieraj osobno; nie force-pushuj.
3. Sprawdź różnice `main...origin/research/allegro-ads-profit-2026-11-05` i PR. Dopiero po walidacji i zatwierdzeniu scal. Nie uznawaj samego zapisu na gałęzi za aktywację.
4. Odczytaj i porównaj istniejące skille w `$HOME/.agents/skills`, `$HOME/.codex/skills`, lokalnym `.agents/skills` i konfiguracji Codex. Preferuj aktualną oficjalną ścieżkę `$HOME/.agents/skills` dla globalnego użytku; jeśli runtime wymaga starszej, potwierdź i udokumentuj. Nie instaluj tego samego skilla dwa razy.
5. Po kontroli frontmatter, zawartości i SHA, zainstaluj SKILL.md z `7dejv-agent-os/skills/7dejv-allegro-ads-profit-analyst/` do odpowiedniego katalogu skilli. Jeżeli istnieje — wykonaj diff i kopię, bez automatycznego overwrite. Router `codex-workflow-router` instaluj z `7dejv-skills-prompts/codex-router/codex-workflow-router/` tylko jeśli brak lub jawna aktualizacja. Zachowaj informację o URL repo, commicie źródłowym i katalogu docelowym.
6. NIE klonuj/instaluj przypadkowych clickerów, scraperów Ads, niezweryfikowanych rozszerzeń Chrome ani backendów agencyjnych. Projekty omnihero1 i retrievershop traktuj jako kod do krytycznej oceny; REST Ads wymaga osobnych praw. Scope `allegro:api:campaigns` NIE jest pełnym Ads API.
7. Utwórz izolowane środowisko Python 3.11+ dla istniejącego repo `allegro`; przed `pip install -r ...` przeczytaj przypięte zależności. Następnie uruchom `python scripts/validate_repository.py`, `python -m unittest discover -s tests -v` i `python -m scripts.smoke_mcp`. Wynik LIVE/CONNECTED można ogłosić wyłącznie po oddzielnym teście autoryzowanego API. Nie uruchamiaj serwera bez oceny.
8. Waliduj `templates/ads-audit-import.schema.json` oraz `templates/ads-audit-import.synthetic.example.json` biblioteką `jsonschema` wyłącznie po akceptacji jej instalacji lub dostępnym walidatorem. Sprawdź ręcznie: CTR 2%, CPC 0,50 PLN, CVR 5%, ROAS 10x, ACoS 10%, contribution before Ads 180 PLN, after Ads 80 PLN. To syntetyczne dane, nie raport sprzedaży.
9. Jeśli rozszerzasz offline kalkulator, zacznij od diagnostyki istniejących skryptów i `allegro_cost_preflight_offline`, nie twórz drugiego source-of-truth; wymagaj danych rzeczywistych i testów: zero-denominator, unknown cost, refund, duplicate aggregates, attribution lag, multiple accounts.
10. Gdy dostarczony jest XLSX Ads i zamówienia, stwórz read-only import + reconciliation i raport; bez danych produkcyjnych nie symuluj wyniku biznesowego. Wszelkie propozycje CPC/budżetów pozostaw jako PROPOSE z zatwierdzeniem, limitem i rollbackiem.
11. Odśwież generowany Swagger istniejącym `scripts/build_api_catalog.py` po pobraniu aktualnej specyfikacji, wykonaj diff kontraktów, uruchom walidacje. Zmiany poza zakresem Ads umieść w oddzielnym PR, jeśli są istotne lub niepowiązane.
12. Raport końcowy: repo + URL PR + commit, lista plików, hash i install path skilli, wersje narzędzi, zrealizowane komendy, logi/testy PASS/FAIL/NOT RUN, różnice API, stwierdzone braki i granice uprawnień. Nie pisz „zainstalowane” bez wykrycia w Codex po restarcie / ponownym odczycie.

## Oficjalna dokumentacja aktywacji i narzędzi
- https://developers.openai.com/api/reference/cli — oficjalna lokalizacja `.agents/skills` w Codex.
- https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-installer/SKILL.md — starszy `$CODEX_HOME/skills` i import z GitHub.
- https://developers.openai.com/learn/docs-mcp — opcjonalny MCP do dokumentacji OpenAI; to nie jest API Allegro Ads.
- https://developer.allegro.pl/tutorials/uwierzytelnianie-i-autoryzacja-zlq9e75GdIR — rozróżnienie scope'ów.
