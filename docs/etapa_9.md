# Briefing para o agente — etapa 9

**Status: feita** (critério de pronto fechado). Não avançar daqui para `make demo` ou Zenodo.

Cole o bloco abaixo num chat novo (Agent mode) e anexe este arquivo se quiser. O agente deve **executar** o briefing, não reescrever o plano.

```
Implemente a etapa 9 deste repositório. Siga docs/etapa_9.md até o critério de pronto.
Não avance para etapa 10 (make demo / Zenodo).
Não altere docs/grain.md.
Não reescreva os ADRs 0001–0005.
Não instale Power BI, Streamlit, Plotly nem Vega.
```

---

## Contexto do projeto

`bets-cerveja` é um **pipeline de pesquisa**, não um app de apostas. Pergunta: de onde saiu o dinheiro das bets no Brasil (2023–2026), em especial o canal on-premise (bares/restaurantes/delivery). Cerveja agregada não caiu; a ponte empírica é o survey Locomotiva (48% C/D/E dizem ter tirado dinheiro de bares/restaurantes/delivery).

Ordem fixa em [`docs/etapas.md`](etapas.md). Etapas **1–8 feitas**. Esta tarefa é **só a etapa 9** (figuras matplotlib). Grain em [`docs/grain.md`](grain.md) — **não alterar**. Arquitetura: [`docs/architecture.md`](architecture.md). Decisão: [ADR 0005](adr/0005-figuras-em-vez-de-power-bi.md). Briefing da etapa 8 (já executado): [`docs/etapa_8.md`](etapa_8.md).

Há poucos pontos apresentáveis: série mensal SIDRA, 3–4 anuais MAPA (2024 em dois vintages), survey de um corte, duas linhas de emprego. Mix sem álcool e V de puro malte **não entram no gráfico** ([`docs/fontes_lacunas.md`](fontes_lacunas.md)).

Stack: Python 3.12 (`requires-python = ">=3.12,<3.13"`), `uv`, Typer, Parquet, DVC → R2, pandera, dbt-duckdb, Dagster, statsmodels. Warehouse em `warehouse/betscerveja.duckdb` (gitignored). Apresentação: **matplotlib** — PNG + HTML em [`exports/figures/`](../exports/figures/). Sem `.pbix`, sem Power BI Desktop, sem Streamlit, sem Plotly, sem Vega. Pages continua sendo o catálogo dbt; o HTML das figuras entra no `make demo` da etapa 10.

Se `fct_cerveja_previsao` ainda não existir, **parar** e executar a etapa 8 primeiro. Ato 1 fecha com a banda do contrafactual.

## Estado atual do código

| Camada | Status |
| --- | --- |
| Lake DVC (`00_landing`, `01_raw`) | pronto |
| `transform/` dbt-duckdb | **pronto (etapas 5–6)** — `marts_core` + `marts_analytics` |
| SARIMAX / `marts_ml` | **pronto (etapa 8)** — `fct_cerveja_previsao`, `ml_metricas`, `ml_coeficientes` |
| Dagster + CI + Pages | **pronto (etapa 7)** — `make ci` = lint → test → dvc-pull → dbt-build → sarimax |
| [`exports/figures/`](../exports/figures/) | só README |
| `matplotlib` | **não está** no extra `dev` |
| CLI `figures` / `make figures` | **não existem** |
| Power BI / Streamlit / Plotly | fora de escopo |

Path do DuckDB: [`transform/profiles.yml`](../transform/profiles.yml) (`warehouse/betscerveja.duckdb`, override `BETSCERVEJA_DUCKDB_PATH`).

`spa_panorama_apostas_2025` está `fora_de_escopo`. **Não** criar `fct_apostas_oficial`. **Não** plotar `agg_mix_produto`. **Não** recompute o SARIMAX — só ler as tabelas já materializadas.

## Critério de pronto

`make figures` (depois do warehouse + forecast já existentes) grava os PNG e o HTML em `exports/figures/`. `make test` e `make lint` continuam verdes. CI **não** passa a publicar figuras nem DuckDB.

Pronto quando:

1. `matplotlib` no extra `dev` de [`pyproject.toml`](../pyproject.toml); `uv sync --extra dev`
2. Função importável lê o DuckDB e escreve os artefatos; CLI e Make **chamam essa função** — não duplicar o plot
3. Existem, no mínimo:
   - `ato1_panorama.png` — `agg_panorama_mensal` (8885 11.1; PIM geral / IPCA só como contexto, sem eixo enganoso que misture índice e preço)
   - `ato1_producao_anual.png` — `fct_mercado_cerveja_anual`, **dois pontos de 2024** (vintages distintos visíveis)
   - `ato1_sarimax.png` — `fct_cerveja_previsao` (realizado, previsto, IC 95%)
   - `ato2_substituicao.png` — `agg_de_onde_saiu_o_dinheiro` (Locomotiva p. 19, inclusive 48% bares/restaurantes/delivery)
   - `ato3_emprego.png` — `agg_estrutura_setorial` e/ou `qa_divergencias` (IEPS vs IBJR: dois números rotulados, não uma série falsa)
   - `index.html` — os PNG + tabela de proveniência (`agg_indicadores_declarados`) + `qa_divergencias`
4. **Não** há figura de `agg_mix_produto` nem sparkline 4,9%→1,27% / V de puro malte
5. HTML só embute imagens e tabelas. Sem JS de charting. Sem segundo site no GitHub Pages
6. Makefile: alvo `figures` no espírito de `uv run betscerveja figures`. Incluir no `.PHONY`. **Não** encadear em `make ci`
7. Pytest barato: os arquivos listados acima existem depois de uma chamada da função (tmp path, sem rede). Sem subir Dagster

Não é critério desta etapa: `make demo`, Zenodo, Dagster job de figuras, Pages das figuras, `.pbix`, `make export` para Parquet.

## Tarefa 1 — matplotlib + módulo

1. Adicionar `matplotlib` no extra `dev`. Python 3.12. Não instalar seaborn/plotly/streamlit/altair “por via das dúvidas”.
2. Código em [`src/betscerveja/figures/`](../src/betscerveja/figures/) (criar). Função importável: abre o DuckDB, gera PNG + HTML no diretório de saída (default `exports/figures/`). O CLI chama essa função.
3. Não reler Parquet do lake. Não chamar SIDRA/BCB. Não chamar o fit do SARIMAX.
4. Dois vintages de 2024 na produção anual **não** podem virar um único ponto. Emprego IEPS e IBJR **não** podem virar uma média.

## Tarefa 2 — CLI e Make

1. Comando `betscerveja figures` em [`src/betscerveja/cli.py`](../src/betscerveja/cli.py) (nome equivalente ok).
2. [`Makefile`](../Makefile): alvo `figures`. Não colocar `figures` na receita de `ci`.
3. [`exports/figures/README.md`](../exports/figures/README.md): como gerar; listar os PNG; lembrar que mix fica de fora.

## Tarefa 3 — docs (obrigatório)

Quando o critério de pronto fechar:

- [`docs/etapas.md`](etapas.md) — etapa atual **10**. Manter o link para este briefing
- [`docs/implementacao.md`](implementacao.md) — figuras no “Feito”; `make figures` nos comandos (sair da seção “Ainda não”)
- [`exports/figures/README.md`](../exports/figures/README.md) — deixar de dizer que `make figures` não existe
- Este arquivo: no topo, marcar **feita** (não apagar o briefing)
- A linha na tabela de docs do [`README.md`](../README.md) apontando este briefing já existe; não expandir o README além disso

**Não** alterar `docs/grain.md`. **Não** reescrever ADRs 0001–0005. **Não** reabrir Power BI.

## Fora de escopo

- Etapa 10: `make demo`, Zenodo
- Power BI, `.pbix`, `exports/powerbi/`, `make export` para Parquet
- Streamlit, Dash, Plotly, Vega, segundo workflow de Pages
- Plotar `agg_mix_produto`; mix sem álcool 4,9%→1,27% e V de puro malte como tendência
- Recomputar SARIMAX; segundo modelo de cerveja zero
- Clima, SPA GGR, shift-share, GLP-1 como regressor (ADRs 0002–0004)
- Encadear `figures` em `make ci`; publicar DuckDB ou lake no Pages
- Commit/push só se o usuário pedir

## Verificação

```powershell
uv sync --extra dev
make dbt-build
make sarimax
make figures
make test
make lint
```

Conferir em `exports/figures/`:

- os cinco PNG e o `index.html` existem
- `ato1_producao_anual.png` mostra os dois vintages de 2024
- `ato1_sarimax.png` tem banda de IC
- `index.html` tem proveniência e `qa_divergencias`
- nenhum arquivo de mix / sparkline de teor alcoólico ou puro malte

Conferir no Makefile / CI:

- `figures` está no `.PHONY` e **não** está na receita de `ci`
- job de Pages continua só com `dbt docs` (sem PNG, sem DuckDB)

## Arquivos esperados (orientação)

Tocar no mínimo:

- `pyproject.toml` / `uv.lock`
- `Makefile` (`figures` no `.PHONY`; **não** em `ci`)
- `src/betscerveja/figures/`
- `src/betscerveja/cli.py`
- `exports/figures/` (README + PNG + HTML gerados)
- `tests/`
- `docs/etapa_9.md` (status)
- `docs/etapas.md`
- `docs/implementacao.md`

Não tocar: `docs/grain.md`, ADRs 0001–0005, `analysis/` como fonte da verdade, models dbt, código de ingest/extract, o fit SARIMAX (salvo se o path do DuckDB estiver errado).
