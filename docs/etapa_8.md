# Briefing para o agente — etapa 8

**Status: não feita.** Não avançar daqui para figuras (`make figures`), demo ou Zenodo.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 8 deste repositório. Siga docs/etapa_8.md até o critério de pronto.
Não avance para etapa 9 (figuras / make figures), demo ou Zenodo.
Não altere docs/grain.md.
Não reescreva os ADRs 0001–0005.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–7 feitas**. Esta tarefa é **só a etapa 8** (SARIMAX / `marts_ml`). Grain em [`docs/grain.md`](grain.md) — **não alterar**. Arquitetura: [`docs/architecture.md`](architecture.md). Métricas: [`docs/data_dictionary.md`](data_dictionary.md). Briefing da etapa 7 (já executado): [`docs/etapa_7.md`](etapa_7.md).

O contrafactual deve confirmar **ausência de anomalia agregada**. Isso é resultado, não falha. Ato 1 fecha com o realizado dentro do intervalo de confiança.

Stack: Python 3.12 (`requires-python = ">=3.12,<3.13"`), `uv`, Typer, Parquet, DVC → R2, pandera, dbt-duckdb, Dagster. Warehouse em `warehouse/betscerveja.duckdb` (gitignored). ML: **statsmodels SARIMAX** — coeficiente, IC e p-valor. Precisamos poder dizer "efeito indistinguível de zero" via banda do contrafactual + p-valores das exógenas permitidas, **não** via dummy de tratamento de bets.

Numeração antiga vs canônica: docs antigos dizem “Fase 6 = SARIMAX”. Ignorar. **SARIMAX / `marts_ml` é etapa 8.** Figuras matplotlib são etapa 9 ([ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md)). Não instalar Prophet, sklearn como substituto do SARIMAX, nem Airflow. Não instalar Power BI.

## Estado atual do código

| Camada | Status |
| --- | --- |
| Lake DVC (`00_landing`, `01_raw`) | pronto |
| Extract API + PDF/HTML | pronto |
| `transform/` dbt-duckdb | **pronto (etapas 5–6)** — staging → intermediate → `marts_core` + `marts_analytics` |
| `fct_serie_mensal` | histórico longo da SIDRA 8885 11.1, 8888, IPCA cerveja, rendimento real — **não cortar em 2023** |
| `agg_panorama_mensal` | janela 2023–2026 (Ato 1). PIM geral entra **aqui**, não no SARIMAX |
| Dagster + CI + Pages | **pronto (etapa 7)** — `make ci` = lint → test → dvc-pull → dbt-build |
| [`src/betscerveja/models/`](../src/betscerveja/models/__init__.py) | stub (“Fase 6”) |
| Schema dbt `marts_ml` | **não existe** |
| `statsmodels` | **não está** no extra `dev` |
| CLI `forecast` / `make sarimax` | **não existem** |
| Figuras / Power BI | fora de escopo desta etapa |

Path do DuckDB: [`transform/profiles.yml`](../transform/profiles.yml) (`warehouse/betscerveja.duckdb`, override `BETSCERVEJA_DUCKDB_PATH`).

`spa_panorama_apostas_2025` está `fora_de_escopo`. **Não** criar `fct_apostas_oficial`. **Não** materializar `ggr` nem `destinacoes_legais` como linhas de fato.

## Critério de pronto

`fct_cerveja_previsao` materializado no DuckDB (schema `marts_ml`), com `realizado`, `previsto`, IC 95% e `dentro_do_intervalo`. As quatro tabelas de grain de ML existem. `make test` e `make lint` continuam verdes. `make ci` inclui o forecast depois do `dbt-build`.

Pronto quando:

1. `make dbt-build` materializa `ml_dataset_cerveja_mensal` (schema `marts_ml`, unique em `data_inicio`)
2. `make sarimax` (depois do `dbt-build`) escreve `fct_cerveja_previsao`, `ml_metricas` e `ml_coeficientes` no mesmo DuckDB, schema `marts_ml`
3. Treino: `data_inicio < 2023-01-01`. Forecast condicional 2023–2026 com exógenas **observadas**
4. Alvo = `producao_bebidas_alcoolicas_indice`. Exógenas = `ipca_cerveja` e `rendimento_real`. Sem PIM geral, clima, GLP-1 ou dummy de apostas
5. IC 95%. `dentro_do_intervalo` = realizado entre `ic_inf` e `ic_sup`. Mês sem realizado: `realizado` nulo e a flag nula
6. Ordem `(p,d,q)(P,D,Q,12)` escolhida por AIC num grid pequeno e **persistida** em `ml_metricas` (uma execução, não um sweep)
7. `ml_coeficientes` tem coeficiente, erro-padrão, p-valor e IC por regressor da execução
8. `statsmodels` no extra `dev`; comando CLI `betscerveja forecast` (ou equivalente) chama a mesma função que o Make e o asset Dagster
9. Job Dagster `build_forecast` separado de `build_warehouse` / ingest / extract
10. CI **não** chama SIDRA/BCB. CI **não** publica DuckDB, Parquet do lake nem `.env`

Não é critério desta etapa: figuras, `make figures`, `make demo`, Zenodo, segundo modelo de cerveja zero, partições mensais, sensores, Dagster Cloud.

## Tarefa 1 — `ml_dataset_cerveja_mensal` (dbt)

1. Schema `marts_ml` em [`transform/dbt_project.yml`](../transform/dbt_project.yml) para `models/marts/ml/` (materialized table).
2. Model `ml_dataset_cerveja_mensal`: pivot/join de [`fct_serie_mensal`](../transform/models/marts/core/fct_serie_mensal.sql). Grain: **um mês**. Inner join dos meses em que existem **alvo e as duas exógenas**. Geografia Brasil.
   - `data_inicio`
   - `producao_bebidas_alcoolicas_indice` (alvo; SIDRA 8885 11.1 — já filtrado no fato)
   - `ipca_cerveja`
   - `rendimento_real`
3. **Não** incluir `producao_industrial_geral_indice` neste dataset. PIM geral continua só em `agg_panorama_mensal`.
4. **Não** filtrar em 2023. O SARIMAX treina no histórico longo; a janela 2023–2026 é o horizonte de previsão, não o corte do dataset.
5. Contrato dbt + teste `unique` em `data_inicio`. `not_null` nas quatro colunas. Relationship de `data_inicio` → `dim_data`.
6. [`transform/README.md`](../transform/README.md): schema `marts_ml`; o dataset é dbt; as três saídas do Python **não** são models dbt (o forecast não cabe em SQL).

## Tarefa 2 — SARIMAX (Python)

1. Adicionar `statsmodels` no extra `dev` de [`pyproject.toml`](../pyproject.toml). Python 3.12. `uv sync --extra dev`. Não instalar Prophet nem sklearn no lugar do SARIMAX.
2. Código em [`src/betscerveja/models/`](../src/betscerveja/models/) (hoje só o stub “Fase 6”). Função importável: lê o DuckDB, treina, escreve as três tabelas. O CLI e o Dagster **chamam essa função** — não duplicar o fit.
3. Especificação (não negociar no chat):
   - statsmodels `SARIMAX`
   - endógeno: `producao_bebidas_alcoolicas_indice`
   - exógenas: `ipca_cerveja`, `rendimento_real`
   - `s=12`
   - treino: `data_inicio < 2023-01-01`
   - forecast: 2023-01-01 até 2026-12-01 (ou o último mês em que as exógenas existam no dataset), **condicional** às exógenas observadas
   - IC 95%
   - grid pequeno de `(p,d,q)(P,D,Q,12)` por AIC; persistir a ordem escolhida em `ml_metricas`; **uma** execução (não várias linhas de forecast por candidato)
4. Sem dummy de apostas, sem GLP-1, sem série climática, sem segundo modelo de cerveja zero, sem PIM geral como regressor.
5. Escrever no mesmo arquivo `warehouse/betscerveja.duckdb`, schema `marts_ml` (criar o schema se o dbt ainda não o tiver criado):
   - `fct_cerveja_previsao` — um mês: `data_inicio`, `realizado`, `previsto`, `ic_inf`, `ic_sup`, `dentro_do_intervalo`. `dentro_do_intervalo` = realizado entre os limites do IC; nulo se `realizado` for nulo
   - `ml_metricas` — uma execução: `execucao_id`, timestamp, ordem, ordem sazonal, AIC, BIC, `n_train`, `n_forecast`, alvo, lista de exógenas
   - `ml_coeficientes` — um regressor por execução: `execucao_id`, nome do regressor, coeficiente, erro-padrão, p-valor, IC inf/sup
6. Pandera (irmão de [`src/betscerveja/schemas/raw.py`](../src/betscerveja/schemas/raw.py)) nas três saídas. Pytest de grain: unique de `fct_cerveja_previsao` em `data_inicio`; unique de `ml_metricas` em `execucao_id`; unique de `ml_coeficientes` em `(execucao_id, regressor)`. Sem subir a UI do Dagster. Sem rede.
7. CLI: comando `betscerveja forecast` (nome equivalente ok) em [`src/betscerveja/cli.py`](../src/betscerveja/cli.py). Makefile: alvo `sarimax` no espírito de `uv run betscerveja forecast`, **depois** de um warehouse já buildado. Incluir no `.PHONY`. Encadear em `make ci` **depois** de `dbt-build` (lint → test → dvc-pull → dbt-build → sarimax). O YAML do GitHub já chama `make ci`; não precisa de passo extra se o Makefile encadear. O job de Pages **não** precisa rodar o forecast (catálogo dbt não depende dele). CI continua sem `ingest` / `extract` e sem publicar DuckDB.

## Tarefa 3 — Dagster

Asset Python fino em [`orchestration/`](../orchestration/) que chama a **mesma** função do CLI (não shell). Job `build_forecast` separado de `build_warehouse`, `ingest_sources` e `extract_sources`. Dependência: o warehouse dbt (pelo menos `ml_dataset_cerveja_mensal`) já materializado — não disparar ingest de rede.

Atualizar o teste de `Definitions.validate_loadable()`. `make lint` já cobre `orchestration`.

Fora desta tarefa: partições mensais, sensores de API, `dagster dev` no CI, Dagster Cloud, colocar o forecast dentro de `build_warehouse`.

## Tarefa 4 — docs (obrigatório)

Quando o critério de pronto fechar:

- [`docs/etapas.md`](etapas.md) — etapa atual **9**. Manter o link para este briefing
- [`docs/implementacao.md`](implementacao.md) — SARIMAX / `marts_ml` no “Feito”; `make sarimax` nos comandos
- [`transform/README.md`](../transform/README.md) — schema `marts_ml` (dataset dbt; saídas Python)
- [`orchestration/README.md`](../orchestration/README.md) — job `build_forecast`
- [`src/betscerveja/models/__init__.py`](../src/betscerveja/models/__init__.py) — etapa 8, não “Fase 6”
- [`docs/architecture.md`](architecture.md) — se ainda disser “Fase 6” no texto do SARIMAX, uma linha “SARIMAX na etapa 8”. Não reverter o nó de figuras (ADR 0005) para Power BI. Não reescrever ADRs 0001–0005
- Este arquivo: no topo, marcar **feita** (não apagar o briefing)
- A linha na tabela de docs do [`README.md`](../README.md) apontando este briefing já existe; não expandir o README além disso

**Não** alterar `docs/grain.md`.

## Fora de escopo

- Etapa 9: figuras, `make figures`, `exports/figures/` (ver [etapa_9.md](etapa_9.md); [ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md))
- Etapa 10: `make demo`, Zenodo
- Segundo modelo SARIMAX de cerveja zero ([`docs/trabalho_futuro.md`](trabalho_futuro.md))
- Mix sem álcool 4,9%→1,27% e V de puro malte 29,2→24,7→29,2 como tendência (quebra metodológica / três vintages — [`docs/fontes_lacunas.md`](fontes_lacunas.md) “Verificações etapa 4”)
- Clima, SPA GGR, shift-share, GLP-1 como regressor, dummy de tratamento de bets (ADRs 0002–0004)
- Notebooks em `analysis/` como fonte da verdade
- Prophet / sklearn no lugar do statsmodels; Airflow; Dagster Cloud
- Commit/push só se o usuário pedir

## Verificação

```powershell
uv sync --extra dev
make dvc-pull
make dbt-build
make sarimax
make test
make lint
make ci
```

Conferir no DuckDB (ou pandas via duckdb):

- `ml_dataset_cerveja_mensal` tem meses **antes** de 2023 (treino) e não tem `producao_industrial_geral_indice`
- `fct_cerveja_previsao` tem a janela 2023–2026 (ou o recorte em que as exógenas existem), colunas `realizado` / `previsto` / `ic_inf` / `ic_sup` / `dentro_do_intervalo`
- `ml_metricas` tem uma linha com a ordem escolhida e AIC
- `ml_coeficientes` tem pelo menos as duas exógenas (e os termos AR/MA que o statsmodels reportar), com p-valor
- nenhum fato/agg/ml com `metrica_id` `ggr` ou `destinacoes_legais`

Conferir no YAML / no código:

- `make ci` inclui `sarimax` depois de `dbt-build` e **não** chama `ingest` / `extract`
- job de Pages continua só com `dbt-build` + `dbt docs generate` (sem DuckDB no artefato)
- `orchestration/` passa no Ruff; `build_forecast` existe e não dispara ingest
- teste das `Definitions` e dos grains ML está em `make test`

## Arquivos esperados (orientação)

Tocar no mínimo:

- `pyproject.toml` / `uv.lock`
- `Makefile` (`sarimax` no `.PHONY` e em `ci`)
- `src/betscerveja/models/`
- `src/betscerveja/schemas/` (pandera das saídas)
- `src/betscerveja/cli.py`
- `transform/dbt_project.yml`
- `transform/models/marts/ml/` (`ml_dataset_cerveja_mensal` + yml)
- `transform/README.md`
- `orchestration/` (asset + job `build_forecast` + README)
- `tests/`
- `docs/etapa_8.md` (status)
- `docs/etapas.md`
- `docs/implementacao.md`
- `docs/architecture.md` (não reverter figuras → Power BI)

Não tocar: `docs/grain.md`, ADRs 0001–0005, `analysis/`, `exports/figures/`, código de ingest/extract salvo bug que impeça o dataset de ler `fct_serie_mensal`.
