# Briefing para o agente — etapa 7

**Status: feita** (critério de pronto fechado). Não avançar daqui para SARIMAX, Power BI, demo ou Zenodo.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 7 deste repositório. Siga docs/etapa_7.md até o critério de pronto.
Não avance para etapa 8 (SARIMAX / marts_ml), Power BI, demo ou Zenodo.
Não altere docs/grain.md.
Não reescreva o ADR 0001.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–6 feitas**. Esta tarefa é **só a etapa 7** (Dagster, GitHub Actions, Pages). Grain em [`docs/grain.md`](grain.md) — **não alterar**. Arquitetura: [`docs/architecture.md`](architecture.md). Orquestração: [ADR 0001](adr/0001-orquestracao-dagster-em-vez-de-airflow.md). Briefing da etapa 6 (já executado): [`docs/etapa_6.md`](etapa_6.md).

Stack: Python 3.12 (`requires-python = ">=3.12,<3.13"`), `uv`, Typer, Parquet, DVC → R2, pandera, dbt-duckdb. Warehouse em `warehouse/betscerveja.duckdb` (gitignored).

Numeração antiga vs canônica: docs antigos dizem “Fase 5 = Dagster” e “Fase 7 = Power BI”. Ignorar. **Dagster / CI / Pages é etapa 7.** Power BI é etapa 9. SARIMAX é etapa 8. Não instalar Airflow. Não usar Dagster Cloud.

## Estado atual do código

| Camada | Status |
| --- | --- |
| Lake DVC (`00_landing`, `01_raw`) | pronto — `data/00_landing.dvc`, `data/01_raw.dvc` |
| Extract API + PDF/HTML | pronto |
| `transform/` dbt-duckdb | **pronto (etapas 5–6)** — staging → intermediate → `marts_core` + `marts_analytics` |
| Testes `unique` / `relationships` / FK composta | prontos |
| Makefile | `test`, `lint`, `dvc-pull`, `dbt-build` existem; **sem** `ci` / `dagster-dev` |
| [`orchestration/`](../orchestration/) | só README (“Fase 5”) |
| `.github/` | **não existe** |
| GitHub Pages | **não existe** |
| SARIMAX, Power BI | fora de escopo desta etapa |

dbt lê estes Parquets em [`transform/models/staging/_sources.yml`](../transform/models/staging/_sources.yml):

- APIs: `sidra_8885_pim_bebidas`, `sidra_8888_pim_geral`, `sidra_7060_ipca`, `bcb_sgs_rendimento_real`
- Anuários: `anuario_cerveja_ref2023_pub2024`, `anuario_cerveja_ref2024_pub2025`, `anuario_cerveja_ref2025_pub2026`

Funções já existentes (não reimplementar adapters): `ingest_source` em [`src/betscerveja/ingest/runner.py`](../src/betscerveja/ingest/runner.py), `extract_source` em [`src/betscerveja/extract/runner.py`](../src/betscerveja/extract/runner.py).

Remote DVC: [`.dvc/config`](../.dvc/config) (`s3://bets-cerveja-landing`, endpoint R2). Segredos **não** estão no git; local usa `.env` via [`scripts/dvc_run.py`](../scripts/dvc_run.py). boto3 ≥ 1.36 precisa dos flags de checksum em [`.env.example`](../.env.example) (`when_required`), senão o R2 responde AccessDenied.

`spa_panorama_apostas_2025` está `fora_de_escopo`. **Não** criar `fct_apostas_oficial`. **Não** materializar `ggr` nem `destinacoes_legais` como linhas de fato.

## Critério de pronto

CI no GitHub Actions roda **lint**, **dvc pull** e **dbt build**. Dagster materializa os models dbt como assets. Pages publica o catálogo `dbt docs generate`. `make test` e `make lint` continuam verdes.

Pronto quando:

1. `make ci` (local, com R2 no `.env`) encadeia lint → test → dvc-pull → dbt-build sem erro
2. Existe [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) que no `push`/`pull_request` faz o mesmo (Ubuntu, Python 3.12, `uv`)
3. `dagster` + `dagster-webserver` + `dagster-dbt` estão no extra `dev`; `make dagster-dev` sobe a UI local
4. Cada model dbt é um asset (`@dbt_assets` + `dbt build`), não um retângulo único em volta do Makefile
5. Assets Python finos envolvem ingest/extract das 4 APIs e dos 3 Anuários listados acima; job `build_warehouse` = dbt; ingest/extract são jobs à parte
6. As `Definitions` carregam (teste `validate_loadable` ou equivalente)
7. No `main`, depois do `dbt build`, o workflow gera `dbt docs` e publica o catálogo estático no GitHub Pages (`manifest` / `catalog` / `index.html`)
8. CI **não** chama SIDRA/BCB (`ingest` / `extract`). CI **não** publica DuckDB, Parquet do lake nem `.env`

Não é critério desta etapa: o workflow verde no GitHub (depende de secrets e de Pages no Settings — ação **sua**, ver Tarefa 2 e 3). O código e o YAML têm que estar prontos para isso.

Não é critério desta etapa: SARIMAX, `marts_ml`, Power BI, `make export`, `make demo`, Zenodo, partições mensais, sensores de API, Dagster Cloud.

## Tarefa 1 — Dagster + dagster-dbt

1. Adicionar `dagster`, `dagster-webserver` e `dagster-dbt` no extra `dev` de [`pyproject.toml`](../pyproject.toml). Pin compatível com `dbt-core>=1.9,<1.11` e Python 3.12. `uv sync --extra dev`. Não instalar Airflow.
2. Código em [`orchestration/`](../orchestration/) (já gitignored: `orchestration/.dagster/`). Tornar o pacote importável a partir da raiz (`pythonpath` do pytest deve incluir `.` além de `src`, ou equivalente). Incluir `orchestration` no `src` do Ruff e no `make lint` (hoje só `src` e `tests`).
3. `DbtProject` apontando para [`transform/`](../transform/) e [`transform/profiles.yml`](../transform/profiles.yml) (path do DuckDB: `warehouse/betscerveja.duckdb`). Um `@dbt_assets` com `dbt.cli(["build"], ...)` para **cada model virar asset** (consequência do [ADR 0001](adr/0001-orquestracao-dagster-em-vez-de-airflow.md)).
4. Assets Python finos que chamam `ingest_source` / `extract_source` — não shell do CLI. Cobrir só o que o dbt lê:
   - APIs: `sidra_8885_pim_bebidas`, `sidra_8888_pim_geral`, `sidra_7060_ipca`, `bcb_sgs_rendimento_real`
   - Anuários: `anuario_cerveja_ref2023_pub2024`, `anuario_cerveja_ref2024_pub2025`, `anuario_cerveja_ref2025_pub2026`
5. Jobs: `build_warehouse` materializa os assets dbt. Ingest e extract ficam em jobs separados. Não colocar ingest no job que a CI usa.
6. Makefile: alvo `dagster-dev` no espírito de `uv run dagster dev -m orchestration.definitions` (ajuste o módulo se a árvore for outra). Incluir no `.PHONY`.
7. Teste barato em `tests/`: as `Definitions` carregam (`Definitions.validate_loadable()` ou equivalente da versão pinada). Sem subir a UI no pytest.

Fora desta tarefa: partições mensais, sensores de API, `dagster dev` no CI, Dagster Cloud.

## Tarefa 2 — GitHub Actions

Novo [`.github/workflows/ci.yml`](../.github/workflows/ci.yml):

- `on: push` e `pull_request`; `ubuntu-latest`; Python 3.12; `astral-sh/setup-uv`.
- Passos: `uv sync --extra dev` → `make lint` → `make test` → `make dvc-pull` → `make dbt-build`.
- Env do job (valores, não nomes inventados):
  - `AWS_ACCESS_KEY_ID`: `${{ secrets.AWS_ACCESS_KEY_ID }}`
  - `AWS_SECRET_ACCESS_KEY`: `${{ secrets.AWS_SECRET_ACCESS_KEY }}`
  - `AWS_REQUEST_CHECKSUM_CALCULATION`: `when_required`
  - `AWS_RESPONSE_CHECKSUM_VALIDATION`: `when_required`
- Endpoint R2 **já está** em [`.dvc/config`](../.dvc/config). Não hardcodar chaves. Não commitar `.env`.
- Alvo `make ci` no [`Makefile`](../Makefile) que encadeia lint → test → dvc-pull → dbt-build, para o YAML não divergir do local. Incluir no `.PHONY`.
- Sem `--no-verify`. Sem `ingest` / `extract`. Sem publicar `warehouse/*.duckdb` nem bytes de `data/00_landing` / `data/01_raw`.

Ação **sua** (externa, não é código): criar no repositório os secrets `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` (mesmo par do `.env` local / R2). O agente documenta isso em `docs/implementacao.md`; não pede as chaves no chat.

Se o `dvc pull` falhar em fork sem secrets, falhar o job de build com a mensagem do DVC — não inventar sample commitado para mascarar. PRs do mesmo repositório usam os secrets.

## Tarefa 3 — Pages = catálogo dbt

Depois do `dbt build` bem-sucedido no `main`:

1. `uv run dbt docs generate --project-dir transform --profiles-dir transform`
2. Publicar o catálogo estático (`index.html`, `manifest.json`, `catalog.json` — o necessário para o site do dbt docs abrir) via `actions/upload-pages-artifact` + `actions/deploy-pages`
3. Só `main` (não PRs). Job separado com `permissions: pages: write` e `id-token: write`, `needs` do job de CI
4. Não enviar DuckDB, Parquet, `.env`, `00_landing` nem `01_raw`

Ação **sua** (externa): Settings → Pages → Source = GitHub Actions.

Pages **não** é o demo da etapa 10 nem o `.pbix` da etapa 9. É linhagem Anuário → mart.

## Tarefa 4 — docs (obrigatório)

Quando o critério de pronto fechar:

- [`docs/etapas.md`](etapas.md) — etapa atual **8**. Manter o link para este briefing
- [`docs/implementacao.md`](implementacao.md) — Dagster / CI / Pages no “Feito”; `make ci` e `make dagster-dev` nos comandos; nas “Ações suas”: secrets R2 no GitHub + Pages Source = GitHub Actions (Zenodo continua etapa 10)
- [`orchestration/README.md`](../orchestration/README.md) — etapa 7, como rodar `make dagster-dev`; não “Fase 5”
- [`docs/architecture.md`](architecture.md) — uma linha na tabela: “Dagster na etapa 7” (no lugar de “Fase 5”). Não reescrever o ADR 0001
- Este arquivo: no topo, marcar **feita** (não apagar o briefing)
- Uma linha na tabela de docs do [`README.md`](../README.md) apontando este briefing. Não expandir o README além disso

**Não** alterar `docs/grain.md`.

## Fora de escopo

- Etapa 8: SARIMAX, `fct_cerveja_previsao`, `marts_ml`
- Etapa 9: Power BI, `make export`, `.pbix`
- Etapa 10: `make demo`, Zenodo
- Airflow, Dagster Cloud, ingest/extract na CI, site MkDocs paralelo, publicar dados brutos no Pages
- Partições mensais e sensores de API (o ADR cita isso como motivo do Dagster; não é critério desta etapa)
- Mix sem álcool 4,9%→1,27% e V de puro malte 29,2→24,7→29,2 como tendência (quebra metodológica / três vintages — [`docs/fontes_lacunas.md`](fontes_lacunas.md) “Verificações etapa 4”)
- Clima, SPA GGR, shift-share, GLP-1 como regressor (ADRs 0002–0004 e [`docs/trabalho_futuro.md`](trabalho_futuro.md))
- Commit/push só se o usuário pedir

## Verificação

```powershell
uv sync --extra dev
make dvc-pull
make test
make lint
make ci
```

`make dagster-dev` sobe a UI; conferir que os models dbt aparecem como assets e que `build_warehouse` não dispara ingest de rede.

Conferir no YAML / no código:

- `.github/workflows/ci.yml` chama `make lint`, `make dvc-pull` e `make dbt-build` (via `make ci` ou os alvos equivalentes) e **não** chama `ingest` / `extract`
- env do workflow tem os dois secrets AWS e os dois flags `when_required`
- job de Pages só no `main`, depois do build, e o artefato não contém DuckDB nem lake
- `orchestration/` passa no Ruff (`make lint`)
- teste das `Definitions` está em `make test`

O agente **não** precisa ver o workflow verde no GitHub se os secrets ainda não existirem. Precisa deixar o YAML e os docs prontos para o usuário colar os secrets e ligar o Pages.

## Arquivos esperados (orientação)

Tocar no mínimo:

- `pyproject.toml` / `uv.lock`
- `Makefile` (`ci`, `dagster-dev`; lint cobrindo `orchestration`)
- `orchestration/` (definitions, assets dbt, assets ingest/extract, README)
- `.github/workflows/ci.yml`
- `tests/` (load das Definitions)
- `docs/etapa_7.md` (status)
- `docs/etapas.md`
- `docs/implementacao.md`
- `docs/architecture.md` (uma linha)
- `README.md` (uma linha na tabela de docs)

Não tocar: `docs/grain.md`, `docs/adr/0001-orquestracao-dagster-em-vez-de-airflow.md` (além de não reescrever), `analysis/`, `exports/powerbi/`, models dbt salvo se um path de source estiver errado para o `dbt build` no CI, código de ingest/extract salvo bug que impeça o asset de chamar a função já existente.
