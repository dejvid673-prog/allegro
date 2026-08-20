# Kontrakt narzędzi MCP dla Codex

Narzędzia powinny być małe, jawne i rozdzielać odczyt, propozycję oraz wykonanie. Model nie otrzymuje surowego tokena Allegro.

## Odczyt

| Narzędzie | Wynik |
|---|---|
| `allegro.accounts.list` | konta, marketplace, scopes i poziom jakości |
| `allegro.offers.search` | paginowana lista z filtrami, stanem i czasem odczytu |
| `allegro.offers.get_normalized` | znormalizowana oferta + dane źródłowe |
| `allegro.offers.audit` | findings: inactive, missing, stale, duplicate, cost, compliance |
| `allegro.catalog.resolve` | kandydaci produktu/kategorii z confidence i dowodami |
| `allegro.orders.list_ready` | bieżące READY, terminy i wyjątki |
| `allegro.shipments.get_proposals` | usługi Allegro dla konkretnego zamówienia |
| `allegro.shipments.list_exceptions` | brak skanu, opóźnienie, zwrot, dopłata |
| `allegro.returns.list_due` | zwroty z deadline i kwotą |
| `allegro.quality.snapshot` | KPI platformy i wewnętrzne |
| `allegro.costs.calculate` | pełny rachunek i scenariusze rentowności |

## Propozycje

| Narzędzie | Wymagane wejście | Wynik |
|---|---|---|
| `allegro.offers.clone_proposal` | konto, oferta źródłowa, docelowy SKU/rynek | neutralny szablon, diff, findings |
| `allegro.offers.create_proposal` | SKU/template | payload, preflight, koszt, ryzyko duplikatu |
| `allegro.offers.update_proposal` | offer id + intent | minimalny Merge Patch i wpływ |
| `allegro.shipments.create_proposal` | order id + packed profile | paczki, usługa, koszt, ostrzeżenia |
| `allegro.returns.refund_proposal` | return id | rozbicie kwoty i termin |
| `allegro.ads.recommend` | zakres, budżet, próg marży | lista ofert/testów, bez wykonania w panelu |

## Wykonanie

Każde narzędzie zapisu przyjmuje `proposalId`, `approvalToken`, `expectedRevision` i `dryRun=false`. Nie przyjmuje dowolnego surowego JSON-u od modelu.

| Narzędzie | Poziom domyślny |
|---|---|
| `allegro.offers.publish_approved` | APPROVE |
| `allegro.offers.patch_approved` | APPROVE |
| `allegro.shipments.create_approved` | APPROVE, potem możliwość ograniczonej automatyzacji |
| `allegro.shipments.cancel_approved` | RESTRICTED |
| `allegro.returns.refund_approved` | RESTRICTED |
| `allegro.offers.end_approved` | RESTRICTED |

## Odpowiedź narzędzia

Każda odpowiedź zawiera: `operationId`, `mode`, `accountId`, `resourceIds`, `observedAt`, `sourceVersions`, `warnings`, `blockingFindings`, `approvalRequired`, `traceIds`, `resultState` i `reconciliationState`. Dane klienta są domyślnie redagowane.
